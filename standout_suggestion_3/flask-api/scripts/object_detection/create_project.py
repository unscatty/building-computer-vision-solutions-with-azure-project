from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials

from env import ENV

custom_vision_config = ENV.azure.custom_vision

__training_credentials = ApiKeyCredentials(
    in_headers={"Training-key": custom_vision_config.training.key})
trainer = CustomVisionTrainingClient(
    custom_vision_config.training.endpoint, __training_credentials)

__prediction_credentials = ApiKeyCredentials(
    in_headers={"Prediction-key": custom_vision_config.prediction.key})
predictor = CustomVisionPredictionClient(
    custom_vision_config.prediction.endpoint, __prediction_credentials)

if __name__ == "__main__":
    # Find the object detection domain
    obj_detection_domain = next(domain for domain in trainer.get_domains(
    ) if domain.type == "ObjectDetection" and domain.name == "General")

    # Create a new project
    print("Your Object Detection Training project has been created. Please move on.")
    project_name = custom_vision_config.custom_project.name
    project = trainer.create_project(
        project_name, domain_id=obj_detection_domain.id)

    # Show project info
    print('Project info:')
    print(project.as_dict())
    print(f'\nProject status: {project.status}')

    # Add project tags
    print('\nAdding tags to project')
    project_tags = custom_vision_config.custom_project.tags
    for tag in project_tags:
        print(
            f'Adding tag: "{tag}" to project: {project_name}, id:{project.id}')
        trainer.create_tag(project.id, tag)
