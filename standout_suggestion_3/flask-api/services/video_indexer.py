from typing import List
from video_indexer import VideoIndexer
from env import ENV
from io import BytesIO

from utils import video_indexer as video_indexer_utils

# Monkey patch the Video Indexer class
VideoIndexer.upload_stream_to_video_indexer = video_indexer_utils.upload_stream_to_video_indexer

__vi_config = ENV.azure.video_indexer

video_indexer_client = VideoIndexer(vi_subscription_key=__vi_config.subscription_key,
                                    vi_location=__vi_config.location, vi_account_id=__vi_config.account_id)


def get_video_thumbnails(video_info_response) -> List[str]:
    return [thumbnail['id'] for thumbnail in video_info_response['videos'][0]['insights']['faces'][0]['thumbnails']]

def get_video_analysis(video_id: str, vi_client : VideoIndexer = video_indexer_client):
  info = vi_client.get_video_info(video_id)

  thumbnails_ids = get_video_thumbnails(info)
  sentiments = info['summarizedInsights']['sentiments']
  emotions = info['summarizedInsights']['emotions']

  return {'thumbnails': thumbnails_ids, 'sentiments': sentiments, 'emotions': emotions}


def get_video_thumbnail_streams(video_id: str, thumbnail_ids: List[str], vi_client: VideoIndexer = video_indexer_client):
  # Get every thumbnail in id list and convert it to a stream
  image_streams =  [BytesIO(vi_client.get_thumbnail_from_video_indexer(video_id, thumbnail_id)) for thumbnail_id in thumbnail_ids]

  return image_streams
