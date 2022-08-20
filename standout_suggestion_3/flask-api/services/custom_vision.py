from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials

from env import ENV

custom_vision_config = ENV.azure.custom_vision

__prediction_credentials = ApiKeyCredentials(
    in_headers={"Prediction-key": custom_vision_config.prediction.key})
predictor = CustomVisionPredictionClient(
    custom_vision_config.prediction.endpoint, __prediction_credentials)

custom_project_config = custom_vision_config.custom_project
prediction_threshold = custom_project_config.prediction_threshold


def detect_with_stream(stream_image, threshold=prediction_threshold, predictor: CustomVisionPredictionClient = predictor):
    # Detect objects using custom trained model
    results = predictor.detect_image(project_id=custom_project_config.project_id,
                                     published_name=custom_project_config.iteration_name, image_data=stream_image)

    return __filter_predictions(results.predictions, threshold)


def detect_with_url(url: str, threshold=prediction_threshold, predictor: CustomVisionPredictionClient = predictor):
    results = predictor.detect_image_url(
        project_id=custom_project_config.project_id, published_name=custom_project_config.iteration_name, image_data=url)

    return __filter_predictions(results.predictions, threshold)


def __filter_predictions(predictions, threshold=0.25):
    return [prediction for prediction in predictions if prediction.probability >= threshold]
