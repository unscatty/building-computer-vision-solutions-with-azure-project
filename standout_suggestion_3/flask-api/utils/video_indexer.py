from io import BufferedReader
import requests
import time

from video_indexer import VideoIndexer

def upload_stream_to_video_indexer(
    self, stream: bytes, video_name='',
    video_language='English', streaming_preset='Default', indexing_preset='Default'
):
    self.check_access_token()

    print('Uploading video to video indexer...')
    params = {
        'streamingPreset': streaming_preset,
        'indexingPreset': indexing_preset,
        'language': video_language,
        'name': video_name,
        'accessToken': self.access_token
    }

    files = {
        'file': stream
    }

    retry_count = 5

    while True:
        if retry_count < 1:
            raise Exception('Retry count exceeded.')

        upload_video_req = requests.post(
            'https://api.videoindexer.ai/{loc}/Accounts/{acc_id}/Videos'.format(
                loc=self.vi_location,
                acc_id=self.vi_account_id
            ),
            params=params,
            files=files
        )

        if upload_video_req.status_code == 200:
            break

        if upload_video_req.status_code == 429:  # hit throttling limit, sleep and retry
            error_resp = upload_video_req.json()
            print('Throttling limit hit. Error message: {}'.format(
                error_resp.get('message')))
            retry_after = VideoIndexer.get_retry_after_from_message(
                error_resp.get('message'))
            time.sleep(retry_after + 1)
            retry_count -= 1
            continue

        print('Error uploading video to video indexer: {}'.format(
            upload_video_req.json()))
        raise Exception('Error uploading video to video indexer')

    response = upload_video_req.json()
    return response['id']
