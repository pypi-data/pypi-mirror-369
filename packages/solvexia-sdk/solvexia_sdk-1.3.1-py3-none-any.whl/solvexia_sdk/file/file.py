import requests
import json
import sys
import math
import os
from filesplit.split import Split
from solvexia_sdk import api

class file:
    def __init__(self, file_id):
        self.file_id = file_id

    def get_file_metadata(self):
        response = api.api_get(f"files/{self.file_id}/metadata")
        api.status_code_check(response, f"Error getting metadata for file with file_id {self.file_id}")
        return response.json()

    def update_file_metadata(self, name):
        payload = {
            'name': name
        }
        response = api.api_post(f"files/{self.file_id}/metadata", payload)
        api.status_code_check(response, f"Error updating metadata for file with file_id {self.file_id}")
        return response.json()

    def upload_file(self, file):
        upload_file_url = api.base_url + f"files/{self.file_id}"
        with open(file, "rb") as open_file:
            response = requests.post(upload_file_url, files={"Filename": open_file}, headers=api.access_token)
        api.status_code_check(response, f"Error uploading file {file}")
        return response.json()

    def download_file(self):
        download_file_url = api.base_url + f"files/{self.file_id}"
        headers = api.access_token
        headers['Content-Type'] = 'application/octet-stream'
        response = requests.get(download_file_url, headers=headers)
        api.status_code_check(response, f"Error downloading file with file_id {self.file_id}")
        return response
    
    # When uploading a large file by chunks, the process is as follows:
    # 1. Starting the uploading session
    # 2. Uploading each chunk
    # 3. Committing the upload
    # The following function does all three in one function whilst the individual functions for each of the above steps
    # are located further below.

    def upload_file_by_chunks(self, file, chunk_size=25000000):
        self.start_upload_session()
        num_of_chunks = self.upload_chunk(file, chunk_size)
        self.commit_upload(file, num_of_chunks)

    def start_upload_session(self):
        response = api.api_post_no_payload(f"files/{self.file_id}/uploadsessions")
        api.status_code_check(response, f"Error starting upload session for file with file_id {self.file_id}")
        self.upload_session_id = response.json()['uploadsessionid']
        self.chunk_id = 1

    def upload_chunk(self, file, chunk_size=25000000):
        file_size = os.stat(file).st_size
        num_of_chunks = math.ceil(file_size/chunk_size)

        output_dir = os.getcwd()  # Use the current working directory as the output directory
        fs = Split(file, output_dir)
        fs.bysize(chunk_size)

        while self.chunk_id <= num_of_chunks:
            upload_chunk_url = api.base_url + f"files/{self.file_id}/uploadsessions/{self.upload_session_id}/chunks/{self.chunk_id}"
            base = os.path.basename(file)
            # The chunk file path is the path to the chunk file that was created by the filesplit library. 
            # And we follow the naming convention of the library which is as follows:
            # chunk_id is zero-padded to 4 digits. eg: <filename>_0001.<extension>
            chunk_file_path = os.path.join(output_dir, os.path.splitext(base)[0] + f"_{self.chunk_id:04d}" + os.path.splitext(base)[1])
            
            with open(chunk_file_path, 'rb') as f:
                response = requests.post(upload_chunk_url, files={"file": f}, headers=api.access_token)

            api.status_code_check(response, f"Error spliting and uploading file with file_id {self.file_id} and chunkId {self.chunk_id}")
            self.chunk_id = self.chunk_id + 1

        return num_of_chunks
        
    def commit_upload(self, file, num_of_chunks):
        response = api.api_post_no_payload(f"files/{self.file_id}/uploadsessions/{self.upload_session_id}/commit")
        base = os.path.basename(file)
        api.status_code_check(response, f"Error committing upload for file with file_id {self.file_id}")
        self.update_file_metadata(base)

        file_index = 1
        
        while file_index <= num_of_chunks:
            os.remove(os.path.splitext(base)[0] + f"_{file_index:04d}{os.path.splitext(base)[1]}")
            file_index = file_index + 1

        return response.json()
