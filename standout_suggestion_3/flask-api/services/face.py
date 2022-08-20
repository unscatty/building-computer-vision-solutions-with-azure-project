from io import BufferedIOBase, BufferedReader
from uuid import uuid4
from time import sleep
from azure.cognitiveservices.vision.face import FaceClient
from azure.cognitiveservices.vision.face.models import TrainingStatusType
from azure.cognitiveservices.vision.face.models._models_py3 import APIErrorException
from msrest.authentication import CognitiveServicesCredentials

from env import ENV
from video_indexer import VideoIndexer
from . import video_indexer as video_indexer_service

__face_api_config = ENV.azure.face_api

face_client = FaceClient(__face_api_config.endpoint,
                         CognitiveServicesCredentials(__face_api_config.key))


def build_person_group_from_streams(
        stream_images,
        person_group_id,
        person_group_name=None,
        person_group_person_name=None,
        client: FaceClient = face_client):

    if not person_group_name:
        person_group_name = person_group_id + '-person-group'

    if not person_group_person_name:
        person_group_person_name = person_group_name + str(uuid4())

    # Create new person group
    try:
        client.person_group.create(person_group_id, person_group_name)
    except APIErrorException as api_exception:
        # Return if person group is already created
        if api_exception.error.error.code == 'PersonGroupExists':
            return person_group_id
        else:
            raise api_exception

    face_person = client.person_group_person.create(
        person_group_id, person_group_person_name)

    for stream_image in stream_images:
        client.person_group_person.add_face_from_stream(
            person_group_id, face_person.person_id, stream_image)

    client.person_group.train(person_group_id)

    # Train the person group
    while (True):
        training_status = client.person_group.get_training_status(
            person_group_id)
        print("Training status: {}.".format(training_status.status))

        if (training_status.status is TrainingStatusType.succeeded):
            return person_group_id
        elif (training_status.status is TrainingStatusType.failed):
            client.person_group.delete(person_group_id=person_group_id)
            raise Exception(
                f'Training the person group with id {person_group_id} has failed.')
        sleep(5)


def detect_faces_ids_from_stream(stream_image, face_client: FaceClient = face_client):
    detected_faces = face_client.face.detect_with_stream(stream_image)
    return [detected_face.face_id for detected_face in detected_faces]


def detected_faces_ids_from_url(url: str, face_client: FaceClient = face_client):
    detected_faces = face_client.face.detect_with_url(url)
    return [detected_face.face_id for detected_face in detected_faces]


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


def identify_from_video_group(detected_faces_ids: list,
                              video_id: str,
                              face_client: FaceClient = face_client,
                              vi_client: VideoIndexer = video_indexer_service.video_indexer_client):
    video_analysis = video_indexer_service.get_video_analysis(
        video_id, vi_client)

    # List of thumbnail ids
    thumbnail_ids = video_analysis.get('thumbnails')

    # Get each thumbnail as stream
    thumbnail_image_streams = video_indexer_service.get_video_thumbnail_streams(
        video_id, thumbnail_ids, vi_client)

    # Create group person from thumbnails in video
    person_group_id = build_person_group_from_streams(
        thumbnail_image_streams, person_group_id=video_id + '_group_id')

    # Identify based on detected faces
    identification_result = identity_face_from_person_group(
        detected_faces_ids, person_group_id, face_client)

    return identification_result


def identify_from_video_group_using_url(
    image_url: str,
    video_id: str,
    face_client: FaceClient = face_client,
    vi_client: VideoIndexer = video_indexer_service.video_indexer_client
):
    detected_faces_ids = detected_faces_ids_from_url(image_url)

    return identify_from_video_group(detected_faces_ids, video_id, face_client, vi_client)


def identify_from_video_group_using_stream(
    image_stream: BufferedReader,
    video_id: str,
    face_client: FaceClient = face_client,
    vi_client: VideoIndexer = video_indexer_service.video_indexer_client
):
    detected_faces_ids = detect_faces_ids_from_stream(image_stream)

    return identify_from_video_group(detected_faces_ids, video_id, face_client, vi_client)
