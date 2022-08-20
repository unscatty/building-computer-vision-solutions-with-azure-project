from azure.ai.formrecognizer import RecognizedForm
from .dict import partial_dict
from .common import to_camel_case

def recognized_form_to_dict(recognized_form: RecognizedForm, schema) -> dict:
  recognized_form_dict = partial_dict(recognized_form, schema)

  # Transform dict keys to camel case for a more consistent response
  return {to_camel_case(key): value for key, value in recognized_form_dict.items()}