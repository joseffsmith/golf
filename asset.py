import logging
import boto3
import pathlib
import json
import os

from dotenv import load_dotenv
load_dotenv()
BUCKET = os.getenv('BUCKET')
KEY = os.getenv('AWS_KEY')
SECRET = os.getenv('AWS_SECRET')

credentials = ''

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Library:
    def __init__(self, live=False):
        self.live = live
        self.local_root = pathlib.Path('./_cache')
        self.local_root.mkdir(exist_ok=True)

    def write(self, path, content):
        c = json.dumps(content)
        if self.live:
            self._write_s3(path, c)
        else:
            self._write_local(path, c)

    def read(self, path, default=None):
        try:
            if self.live:
                content = self._read_s3(path)
            else:
                content = self._read_local(path)
        except Exception as e:
            logger.exception(f'Could not read content fron {path}')
            if default is not None:
                return default
            raise e
        return json.loads(content)

    def _write_local(self, path, content):
        p = self.local_root.joinpath(path)
        with open(p, 'w') as f:
            f.write(content)

    def _read_local(self, path):
        p = self.local_root.joinpath(path)
        with open(p, 'r') as f:
            return f.read()

    @property
    def s3(self):
        s3 = boto3.client('s3', aws_access_key_id=KEY,
                          aws_secret_access_key=SECRET)
        return s3

    def _read_s3(self, path):
        return self.s3.get_object(Bucket=BUCKET, Key=path)['Body'].read()

    def _write_s3(self, path, content):
        self.s3.put_object(Bucket=BUCKET, Key=path, Body=content)
