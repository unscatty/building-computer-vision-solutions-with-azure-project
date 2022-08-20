from env import ENV
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import FormTrainingClient

__form_recognizer_config = ENV.azure.form_recognizer

__endpoint = __form_recognizer_config.endpoint
__key = __form_recognizer_config.key

custom_model_name = __form_recognizer_config.training.model_name
custom_model_training_data_url = __form_recognizer_config.training.training_data.url
custom_model_training_data_subfolder = __form_recognizer_config.training.training_data.subfolder

form_training_client = FormTrainingClient(
    endpoint=__endpoint, credential=AzureKeyCredential(__key))

print('Starting model training...')

training_process = form_training_client.begin_training(
    custom_model_training_data_url, use_training_labels=True, prefix=custom_model_training_data_subfolder, model_name=custom_model_name)

custom_model = training_process.result()

print('Training complete')

# Info about custom model
custom_model_info = form_training_client.get_custom_model(
    model_id=custom_model.model_id)
print("Model ID: {}".format(custom_model_info.model_id))
print("Status: {}".format(custom_model_info.status))
print("Training started on: {}".format(custom_model_info.training_started_on))
print("Training completed on: {}".format(
    custom_model_info.training_completed_on))

# List training documents details
for doc in custom_model.training_documents:
    print("Document name: {}".format(doc.name))
    print("Document status: {}".format(doc.status))
    print("Document page count: {}".format(doc.page_count))
    print("Document errors: {}".format(doc.errors))

# Print model recognized labels
for submodel in custom_model.submodels:
    print(
        "The submodel with form type '{}' has recognized the following fields: {}".format(
            submodel.form_type,
            ", ".join(
                [
                    field.label if field.label else name
                    for name, field in submodel.fields.items()
                ]
            ),
        )
    )