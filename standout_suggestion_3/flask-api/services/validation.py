from xmlrpc.client import Boolean
from services.form_recognizer import kiosk_form_recognizer as form_recognizer_service
from services.flight_manifest import FlightManifest, flight_manifest as flight_manifest_service
from services import custom_vision as custom_vision_service
from services import face as face_service
from datetime import datetime

from env import ENV
from utils.dict import to_dict, partial_dict

__flight_manifest_config = ENV.flight_manifest

# Format: {'Flight manifest column': 'Extracted Boarding Pass Field' }
boarding_pass_validation_schema = {
    'PassengerName': 'passengerName',
    'Carrier': 'carrier',
    'FlightNo': 'flightNumber',
    'Class': 'class',
    'From': 'from',
    'To': 'to',
    # Date extracted from boarding pass is wrong, use alternate field value instead
    'Date': 'dateAlt',
    # 'Baggage': 'baggage',
    'Seat': 'seat',
    'Gate': 'gate',
    'BoardingTime': 'boardingTime',
    'BoardingPassID': 'boardingPassId',
}


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

    # Get corresponding row from flight manifest
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

    # Reset id document image stream
    identity_doc_file.seek(0)

    # Validate identity from video
    if video_id:
        validation_response['identity'] = __create_response(*validate_identity_from_video(
            identity_doc_file=identity_doc_file, video_id=video_id, flight_manifest_row=manifest_row, flight_manifest_service=flight_manifest_service))

    return validation_response
