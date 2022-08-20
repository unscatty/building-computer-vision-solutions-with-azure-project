### Step 5: Validation and Metrics Monitoring

#### :ballot_box_with_check: A list of all the Python libraries used in your project in text format
```
azure-ai-formrecognizer==3.1.2
azure-cognitiveservices-vision-computervision==0.9.0
azure-cognitiveservices-vision-customvision==3.1.0
azure-cognitiveservices-vision-face==0.6.0
azure-common==1.1.28
azure-core==1.24.0
azure-storage-blob==12.12.0
blinker==1.4
brotlipy==0.7.0
bson==0.5.10
certifi==2021.10.8
charset-normalizer==2.0.12
cryptography==37.0.2
docopt==0.6.2
isodate==0.6.1
flask
Flask-Cors==3.0.10
msrest
pipreqs==0.4.11
pymongo==4.1.1
python-dotenv==0.20.0
requests-oauthlib==1.3.1
typing_extensions==4.2.0
video-indexer==0.1.8
yarg==0.1.9
```

#### :ballot_box_with_check: Code snippet or screenshot showing that face matching is completed with X% match between face from the video and face from the ID

This method takes the ids of the faces generated from the id document, and the id of the person group model that was created using the thumbnails generated from the verification video and performs the validation using the Face API. The person group has already been created and trained.

File: `services/face.py` at line `76`

```python
def identity_face_from_person_group(detected_faces_ids, person_group_id, face_client: FaceClient = face_client):
    identification_result = face_client.face.identify(
        detected_faces_ids, person_group_id)

    for result in identification_result:
        if result.candidates:
            for candidate in result.candidates:
                print("The Identity match confidence is {}".format(
                    candidate.confidence))
        else:
            print("Can't verify the identity with the person group")

    return identification_result
```

![](video_match_percentage.png)

#### :ballot_box_with_check: Code snippet or screenshot showing you have generated the validation results from all the data from ID, boarding pass, and face video, and finally stored the validation results to the flight manifest table

Full passenger validation is performed by using 4 methods, each one validates a different aspect of the validation process. Each method modifies the manifest table file with the validation result, the manifest file is stored in an Azure Blob Storage container and is updated using the Azure Blob Storage python package.

The file can be accessed at any time here: https://azureaiblob.blob.core.windows.net/kiosk-validator/flight_manifest.csv?sp=r&st=2022-08-20T02:09:36Z&se=2025-12-20T11:09:36Z&spr=https&sv=2021-06-08&sr=b&sig=xnBqNf5ihEVXr9kLmyjCVTxcb2FkFMYQIGplTSYyMH4%3D to see the validation results.

You can go to https://www.convertcsv.com/csv-viewer-editor.htm and input the above url to see the file without downloading it.

The first method validates the data from the boarding pass document, extracting the information using a Form Recognizer Custom Model, and compares it with that from the manifest file.

This method is the most important because it uses the `BoardingPassID` to select the corresponding row in the flight manifest CSV file, which the other methods use when validating. Otherwise it wouldn't be possible to identify the corresponding row to perform the other validations.

File: `services/validation.py` at line `31`
```python
def validate_boarding_pass(boarding_pass_file,
                           flight_manifest_service: FlightManifest = flight_manifest_service,
                           validation_schema=boarding_pass_validation_schema,
                           find_by_property='BoardingPassID',
                           validation_column='BoardingPassValidation'):
    extracted_data = form_recognizer_service.extract_from_boarding_pass_file(
        boarding_pass_file)

    if len(extracted_data) != 1:
        # More than one documents
        return False, 'Service detected more than one boarding pass documents', None

    boarding_pass_data = extracted_data[0]

    # Get corresponding row from fligt manifest
    try:
        flight_manifest_row = flight_manifest_service.find(
            key=find_by_property, value=boarding_pass_data.get(validation_schema[find_by_property]).get('value'))
    except StopIteration:
        return False, 'Could not find your boarding pass information in flight manifest', None

    # Validate each field with its corresponding column in flight manifest
    for flight_manifest_key, boarding_pass_key in validation_schema.items():
        # Compare values from extracted data with values from flight manifest
        # In extracted data actual text value is in "value" key
        boarding_pass_value = boarding_pass_data[boarding_pass_key]['value']
        flight_manifest_value = flight_manifest_row[flight_manifest_key]

        # Transform 'Economy' to 'E', and 'Business' to 'B'
        if flight_manifest_key == 'Class':
            flight_manifest_value = flight_manifest_value[0].upper()

        print(
            f'Flight manifest[{flight_manifest_key}:{flight_manifest_value}] - Boarding pass[{boarding_pass_key}:{boarding_pass_value}]')

        # Values are not the same
        if flight_manifest_value.strip() != boarding_pass_value.strip():
            # Change flight manifest
            flight_manifest_row[validation_column] = str(False).upper()

            # Update flight manifest
            flight_manifest_service.upload()

            return False, (f'Field "{flight_manifest_key}" with value "{flight_manifest_value}"'
                           ' from flight manifest did not match '
                           f'"{boarding_pass_key}" with value "{boarding_pass_value}" from boarding pass'), None

    # Change flight manifest
    flight_manifest_row[validation_column] = str(True).upper()

    # Update flight manifest
    flight_manifest_service.upload()

    return True, boarding_pass_data, flight_manifest_row
```

The second method validates the identify of the person using the data extracted from the identification document. More specifically it performs the `NameValidation` and `DoBValidation`.

File: `services/validation.py` at line `87`
```python
def validate_identity_document(identity_doc_file,
                               flight_manifest_row,
                               flight_manifest_service: FlightManifest = flight_manifest_service,
                               date_format=__flight_manifest_config.date_format):
    extracted_data = form_recognizer_service.extract_from_identity_file(
        identity_doc_file)

    id_document_data = extracted_data[0]

    # Print to the terminal for debugging purposes
    print('\n\n')
    print('------------------------------------ Flight Manifest Data ------------------------------------')
    print(flight_manifest_row)
    print('----------------------------------------------------------------------------------------------')
    print('-------------------------------------- ID document data --------------------------------------')
    print(id_document_data)
    print('----------------------------------------------------------------------------------------------')

    # Full name from identity document
    id_document_name = id_document_data['firstname']['value'] + \
        ' ' + id_document_data['lastname']['value']
    id_date_of_birth = id_document_data['dateofbirth']['value']

    # Validate name and date of birth
    name_validation: Boolean = flight_manifest_row['PassengerName'] == id_document_name

    # Transform to datetime.date for comparison
    flight_manifest_date_of_birth = datetime.strptime(
        flight_manifest_row['DateOfBirth'], date_format).date()

    date_of_birth_validation: Boolean = id_date_of_birth == flight_manifest_date_of_birth

    # Change manifest validation values
    flight_manifest_row['NameValidation'] = str(name_validation).upper()
    flight_manifest_row['DoBValidation'] = str(
        date_of_birth_validation).upper()

    # Update flight manifest with validation info
    flight_manifest_service.upload()

    if name_validation and date_of_birth_validation:
        # Valid id document
        return True, id_document_data, flight_manifest_row

    # Couldn't get info from flight manifest
    return False, 'Your identification data could not be found in flight manifest', None
```

The third method validates the carry-on luggage, using an image of the items and the custom vision object detection model.

File: `services/validation.py` at line `135`
```python
def validate_luggage(luggage_image_file, flight_manifest_row, flight_manifest_service: FlightManifest = flight_manifest_service):
    predictions = custom_vision_service.detect_with_stream(luggage_image_file)

    if len(predictions) > 0:
        # Lighter has been detected
        # Update flight manifest
        flight_manifest_row['LuggageValidation'] = str(False).upper()
        flight_manifest_service.upload()

        return False, 'A lighter has been detected', None

    # Update flight manifest
    flight_manifest_row['LuggageValidation'] = str(True).upper()
    flight_manifest_service.upload()

    return True, {}, flight_manifest_row
```

Finally, the fourth method validates the person identity using the thumbnails extracted from the video, and compares them with the face data extracted from the id document using the Face API.

File: `services/validation.py` at line `153`
```python
def validate_identity_from_video(identity_doc_file, video_id, flight_manifest_row, flight_manifest_service: FlightManifest = flight_manifest_service):
    if not video_id:
        # Update flight manifest
        flight_manifest_row['PersonValidation'] = str(False).upper()
        flight_manifest_service.upload()

        return False, 'Identity could not be verified', None

    identification_result = face_service.identify_from_video_group_using_stream(
        identity_doc_file, video_id)

    result = partial_dict(to_dict(identification_result), ['candidates'])[0]

    # Identity could not be verified
    if len(result['candidates']) < 1:
        # Update flight manifest
        flight_manifest_row['PersonValidation'] = str(False).upper()
        flight_manifest_service.upload()

        return False, 'Identity could not be verified', None

    # Show validation results
    for result in result['candidates']:
        print(result)

    if flight_manifest_row:
        # Update flight manifest
        flight_manifest_row['PersonValidation'] = str(True).upper()
        flight_manifest_service.upload()

    return True, result, flight_manifest_row
```

These four methods are used by another method that performs the full passenger validation and creates a JSON response with the validation information

File: `services/validation.py` at line `191`
```python
def __create_response(valid: bool, response, *_):
    return {'valid': valid, 'response': response}


# Perform full validation with all documents
def validate_boarding(boarding_pass_file,
                      identity_doc_file,
                      luggage_image_file,
                      video_id,
                      flight_manifest_service: FlightManifest = flight_manifest_service):
    # Server response
    validation_response = {}

    # Perform boarding pass validation
    bpass_valid, bpass_response, manifest_row = validate_boarding_pass(
        boarding_pass_file=boarding_pass_file, flight_manifest_service=flight_manifest_service)

    validation_response['boardingPass'] = __create_response(
        bpass_valid, bpass_response)

    if not bpass_valid:
        # Validation cannot continue
        # Must pass boarding pass validation in order to continue
        # because boarding pass id is used to identify CSV row in flight manifest
        return validation_response

    # Validate id document
    validation_response['idDocument'] = __create_response(*validate_identity_document(
        identity_doc_file=identity_doc_file, flight_manifest_row=manifest_row, flight_manifest_service=flight_manifest_service))

    # Validate luggage
    if luggage_image_file:
        validation_response['luggage'] = __create_response(*validate_luggage(
            luggage_image_file=luggage_image_file, flight_manifest_row=manifest_row, flight_manifest_service=flight_manifest_service))

    # Reset id document image steram
    identity_doc_file.seek(0)

    # Validate identity from video
    if video_id:
        validation_response['identity'] = __create_response(*validate_identity_from_video(
            identity_doc_file=identity_doc_file, video_id=video_id, flight_manifest_row=manifest_row, flight_manifest_service=flight_manifest_service))

    return validation_response
```
which then is used in a Flask route that takes the three documents as files (video id, generated by Azure Video Indexer, is passed as a route param) and performs the validation process.

File: `app.py` at line `135`
```python
# Performs full validation process taking ID card, video id (from previously uploaded video), boarding pass file and luggage image file
@app.route('/validate', methods=['POST'])
def validate_boarding():
    boarding_pass_file = request.files.get('boarding_pass')
    identity_doc_file = request.files.get('id_document')
    luggage_image_file = request.files.get('luggage')

    video_id = request.args.get('video_id')

    if not (boarding_pass_file and identity_doc_file):
        return {'error': 'You are missing required files'}, 400

    return validation_service.validate_boarding(boarding_pass_file=boarding_pass_file.stream,
                                                identity_doc_file=identity_doc_file.stream,
                                                luggage_image_file=luggage_image_file.stream if luggage_image_file else None,
                                                video_id=video_id, flight_manifest_service=flight_manifest_service)
```

#### :ballot_box_with_check: Screenshot for all successful validations

Because validation video is required for the whole validation process to succeed, the validation can only be successful using documents generated for my data and my validation video

![](successful_validation.png)

#### :ballot_box_with_check: If validation failed, a screenshot of the error message
When id document does not match with data from the flight manifest
![](unsuccessful_validations_1.png)

When boarding pass data does not match with data from the flight manifest
![](unsuccessful_validations_2.png)

When boarding pass, id document and luggage are valid, but video verification couldn't be validated
![](unsuccessful_validations_3.png)

When boarding pass and id document and luggage are valid, but luggage and video validation fail
![](unsuccessful_validations_4.png)

When boarding pass, id document and video  are valid, but luggage validation fails
![](unsuccessful_validations_5.png)

#### :ballot_box_with_check: Your final manifest table, which has all the updated validation results
| PassengerName     | Carrier | FlightNo | Class    | From          | To            | Date         | Baggage | Seat | Gate | BoardingTime | BoardingPassID    | Sex | DateOfBirth       | DoBValidation | PersonValidation | LuggageValidation | NameValidation | BoardingPassValidation |
|-------------------|---------|----------|----------|---------------|---------------|--------------|---------|------|------|--------------|-------------------|-----|-------------------|---------------|------------------|-------------------|----------------|------------------------|
| Bradley Heller    | UA      | 742      | Economy  | Albuquerque   | Pittsburgh    | May 17, 2022 | Yes     | 35B  | G2   | 12:00 AM PST | ETK-711636124038C | M   | May 10,1991       | TRUE          | FALSE            | TRUE              | TRUE           | TRUE                   |
| Lysanne Grady     | UA      | 456      | Economy  | Atlantic City | Amarillo      | May 17, 2022 | Yes     | 12A  | G1   | 01:45 PM PST | ETK-208677567364B | F   | October 8,1984    | TRUE          | FALSE            | TRUE              | TRUE           | TRUE                   |
| Angela Cartwright | WN      | 699      | Business | Austin        | Daytona Beach | May 20, 2022 | No      | 17B  | G1   | 09:15 AM PST | ETK-592745475599A | F   | December 12,1982  | TRUE          | FALSE            | TRUE              | TRUE           | TRUE                   |
| Freddie McGlynn   | UA      | 345      | Economy  | Cleveland     | Dallas        | May 21, 2022 | Yes     | 32B  | G3   | 10:00 AM PST | ETK-849329293727B | M   | October 10,1978   | TRUE          | FALSE            | TRUE              | TRUE           | TRUE                   |
| Huel Moore        | WN      | 125      | Business | Greenville    | Washington    | May 18, 2022 | Yes     | 15A  | G1   | 08:00 PM PST | ETK-491149085713C | M   | August 15,1977    | TRUE          | FALSE            | TRUE              | TRUE           | TRUE                   |
| Adolf Fisher      | UA      | 878      | Economy  | New Haven     | New York      | May 18, 2022 | No      | 8B   | G2   | 06:00 PM PST | ETK-620118364819D | M   | September 22,1957 | TRUE          | FALSE            | TRUE              | TRUE           | TRUE                   |
| Axel Grimes       | UA      | 248      | Economy  | Miami         | Manchester    | May 22, 2022 | Yes     | 14B  | G1   | 08:20 PM PST | ETK-357640257860B | M   | July 13,1993      | TRUE          | FALSE            | TRUE              | TRUE           | TRUE                   |
| Carlos Aguilera   | WN      | 515      | Economy  | Nashville     | Chicago       | May 20, 2022 | Yes     | 13C  | G1   | 06:00 PM PST | ETK-792338457961C | M   | October 2,1995    | TRUE          | TRUE             | TRUE              | TRUE           | TRUE                   |

Table can also be found at https://azureaiblob.blob.core.windows.net/kiosk-validator/flight_manifest.csv?sp=r&st=2022-08-20T02:09:36Z&se=2025-12-20T11:09:36Z&spr=https&sv=2021-06-08&sr=b&sig=xnBqNf5ihEVXr9kLmyjCVTxcb2FkFMYQIGplTSYyMH4%3D (However, this table may change every time a validation process is performed from the kiosk website)

You can go to https://www.convertcsv.com/csv-viewer-editor.htm and input the above url to see the file without downloading it.

Table file can also be found at `flight_manifest_final.csv` located in this folder

#### :ballot_box_with_check: Screenshots of the Service Consumption Report showing the usage pattern and performance of each Azure cognitive resource
Metrics for the Form Recognizer service
![](metrics_form_recognizer.png)

Metrics for the Custom Vision service
![](metrics_custom_vision.png)

Metrics for the Face API service
![](metrics_face_api.png)

#### :ballot_box_with_check: Your final reflection write-up in PDF or text format
By creating this project I learned about the capabilities offered by AI services, more specifically computer vision. The project was really challenging as it presents a complete validation flow that takes data from different sources to validate a passenger's flight information and identity.

During the development of this project I faced several challenges. First, I wanted to create a web solution that could simulate a real kiosk that could be placed in an airport, for this I used Flask for the first time, to create an API application. Although it took me some time to learn about Flask, I got used to it, finding it similar to other libraries like Express.js or Sinatra. I also created a Vue SPA that consumes this Flask application for a better approximation of a real solution.

Another challenge was to integrate all the functionality into a single solution and try to define the data flow during the validation process as the functionality was spread over multiple independent scripts.

During the process of tagging the boarding pass documents I realized that the Date field could not be extracted from the documents due to the format of the boarding pass template. Fortunately, I had added an additional date field that I could use when performing the data extraction.

While working on the lighter detection process I realized that, when testing with carry-on luggage images, the lighter detection was not as good as I expected, but I think that is due to the overlapping of the objects in the images and the amount of images used during training was fairly small, anyway, the result was quite acceptable and performed quite well

Another thing I wanted to do was to directly manipulate the CSV file of the flight manifest stored in Azure Blob Storage, for which I used the Azure Blob Storage python package. It wasn't that easy because I had never worked with CSV files in python before and the API for this is quite large, with several different methods that can become overwhelming. I ended up using a method that is not that performant, but I think for small CSV files like this one it is quite acceptable. If the flight manifest data were larger, the solution might show performance issues, but, at this point, I think a better storage option would be more appropriate, such as using a database.

It was a really exciting and fun project, which required a lot of work and from which I learned a lot, not only about the use of Cognitive Services, but also about the related tools, such as the Form OCR testing tool used during the tagging of the boarding pass documents and the Custom Vision website to upload, tag and test the custom lighter detection model, as well as the use of the Azure Portal to create resources, manage them, monitor them and integrate them into a project.

It is really impressive how easy it is to extract data from different documents and how much data can be extracted from a single video. That's why I think it's important to take user privacy as a serious issue when developing a solution that uses Computer Vision, and any AI service in general, with sensitive user data.

It has been an amazing and very enriching experience and I am happy with the results.

##### My TODO list for this project
- [ ] Move to a better and more performant way of storing data, like a database
- [ ] CRUD operations for the data, like being able to register your flight information that would be used later during validation, instead of being static
- [ ] Make it possible for users to generate their boarding pass document from the website by submitting their data and be able to download the generated document
- [ ] Create more iterations for the custom lighter detection model adding more lighter images
- [ ] Make it possible for users to record a short video directly from the kiosk website instead of uploading the video file