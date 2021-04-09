import logging
import boto3
import json
import os

from dotenv import load_dotenv
load_dotenv()
BUCKET = os.getenv('BUCKET')
KEY = os.getenv('AWS_KEY')
SECRET = os.getenv('AWS_SECRET')
MONGO_USER = os.getenv('MONGO_USER')
MONGO_PASS = os.getenv('MONGO_PASS')
credentials = ''

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Library:
    def __init__(self, live=True):
        self.live = live

    def write(self, path, content):
        c = json.dumps(content)
        self._write_s3(path, c)

    def read(self, path, default=None):
        try:
            content = self._read_s3(path)
        except Exception as e:
            logger.exception(f'Could not read content fron {path}')
            if default is not None:
                return default
            raise e
        return json.loads(content)

    @property
    def s3(self):
        s3 = boto3.client('s3', aws_access_key_id=KEY,
                          aws_secret_access_key=SECRET)
        return s3

    def _read_s3(self, path):
        return self.s3.get_object(Bucket=BUCKET, Key=path)['Body'].read()

    def _write_s3(self, path, content):
        self.s3.put_object(Bucket=BUCKET, Key=path, Body=content)
