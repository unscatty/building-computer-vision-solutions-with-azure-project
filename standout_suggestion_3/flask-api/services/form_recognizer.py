from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import FormRecognizerClient

from utils.form_recognizer import recognized_form_to_dict
from env import ENV
from .schemas import IDENTITY_SCHEMA, BOARDING_PASS_SCHEMA


class KioskFormRecognizer:
    def __init__(self, endpoint, key, custom_boarding_pass_model_id):
        self.form_recognizer_client = FormRecognizerClient(
            endpoint, AzureKeyCredential(key))
        self.boarding_pass_model_id = custom_boarding_pass_model_id

    def extract_from_identity(self, identity_url: str, schema=IDENTITY_SCHEMA) -> list:
        # Extract al information from the document url
        id_content_from_url = self.form_recognizer_client.begin_recognize_identity_documents_from_url(
            identity_url)

        id_content = id_content_from_url.result()

        # Transform it into a dict
        return [recognized_form_to_dict(result.fields, schema) for result in id_content]

    def extract_from_identity_file(self, indentity_file, schema=IDENTITY_SCHEMA) -> list:
        # Extract al information from the document file
        id_content_from_file = self.form_recognizer_client.begin_recognize_identity_documents(
            indentity_file)

        id_content = id_content_from_file.result()

        # Transform it into a dict
        return [recognized_form_to_dict(result.fields, schema) for result in id_content]

    def extract_from_boarding_pass(self, boarding_pass_url: str, schema=BOARDING_PASS_SCHEMA) -> list:
        # Extract information from the boarding pass url document using the custom model already trained
        # The model id is loaded from an environment variable
        extraction_process = self.form_recognizer_client.begin_recognize_custom_forms_from_url(
            model_id=self.boarding_pass_model_id, form_url=boarding_pass_url)
        result_content = extraction_process.result()

        # Transform the result into a dict
        return [recognized_form_to_dict(result.fields, schema) for result in result_content]

    def extract_from_boarding_pass_file(self, boarding_pass_file, schema=BOARDING_PASS_SCHEMA) -> list:
        # Extract information from the boarding pass document using the custom model already trained
        # The model id is loaded from an environment variable
        extraction_process = self.form_recognizer_client.begin_recognize_custom_forms(
            model_id=self.boarding_pass_model_id, form=boarding_pass_file)
        result_content = extraction_process.result()

        # Transform the result into a dict
        return [recognized_form_to_dict(result.fields, schema) for result in result_content]


__form_recognizer_config = ENV.azure.form_recognizer

__endpoint = __form_recognizer_config.endpoint
__key = __form_recognizer_config.key
__custom_model_id = __form_recognizer_config.training.model_id

kiosk_form_recognizer = KioskFormRecognizer(
    __endpoint, __key, __custom_model_id)
