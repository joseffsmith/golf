import boto3
import pathlib
import json
import os

from dotenv import load_dotenv
load_dotenv()
BUCKET = os.getenv('BUCKET')

credentials = ''

class Library:
    def __init__(self, live=False):
        self.live = live
        if live:
            self.auth_s3(credentials)
        
        self.local_root = pathlib.Path('./_cache')
        self.local_root.mkdir(exist_ok=True)

    def write(self, path, content):
        c = json.dumps(content)
        if self.live:
            self.write_s3(path, c)
        else:
            self.write_local(path, c)

    def read(self, path):
        if self.live:
            content = self.read_s3(path)
        else:
            content = self.read_local(path)
        return json.loads(content)

    def write_local(self, path, content):
        print(self.local_root)
        p = self.local_root.joinpath(path)
        with open(p, 'w') as f:
            f.write(content)

    def read_local(self, path):
        p = self.local_root.joinpath(path)
        with open(p, 'r') as f:
            return f.read()

    @property
    def s3(self):
        s3 = boto3.resource('s3')
        return s3.Bucket(BUCKET)

    def read_s3(self, path):
        return self.s3.get_object(Key=path)

    def write_s3(self, path, content):
        self.s3.put_object(Key=path, Body=content)