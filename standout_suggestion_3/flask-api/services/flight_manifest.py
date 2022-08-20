from azure.storage.blob import BlobServiceClient
import csv
import io
from env import ENV

__blob_storage_config = ENV.azure.blob_storage

class FlightManifest:
    def __init__(self, blob_service_client: BlobServiceClient, container_name: str, file_name: str, file_delimiter: str):
        self.blob_service_client = blob_service_client
        self.file_name = file_name
        self.container_name = container_name
        self.file_delimiter = file_delimiter

        self.blob_client = self.blob_service_client.get_blob_client(
            container=container_name, blob=file_name)
        self.values: csv.DictReader = csv.DictReader(
            io.StringIO(self.blob_client.download_blob().content_as_text()), delimiter=file_delimiter)

        self.__as_list = list(self.values)

    def as_list(self):
        return self.__as_list
    
    def find(self, key, value):
        return next((row for row in self.as_list() if row.get(key) == value))

    def upload(self, file_name=None, overwrite=True):
        data = self.as_list()

        if not file_name:
            file_name = self.file_name

        csv_stream = io.StringIO()
        fieldnames = data[0].keys()

        writer = csv.DictWriter(
            csv_stream, delimiter=self.file_delimiter, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

        self.blob_client.upload_blob(csv_stream.getvalue(), overwrite=overwrite)


blob_service_client = BlobServiceClient(account_url=__blob_storage_config.account_url,
                                        credential=__blob_storage_config.sas_token)

flight_manifest = FlightManifest(
    blob_service_client, container_name=__blob_storage_config.container_name, file_name=ENV.flight_manifest.file_name, file_delimiter=ENV.flight_manifest.delimiter)

if __name__ == '__main__':
    rows = flight_manifest.as_list()

    for row in rows:
        print(row)