import boto3
import pathlib

credentials = ''

class Library:
    def __init__(self, live=False):
        self.live = live
        if live:
            self.auth_s3(credentials)
        
        self.root_path = pathlib.Path('./_cache')
        self.root_path.mkdir(exist_ok=True)
        if live:
            self.root_path = self.s3_root_path()

    def write(self, path, content):
        if self.live:
            self.write_s3(path, content)
        else:
            self.write_local(path, content)

    def read(self, path):
        if self.live:
            self.read_s3(path)
        else:
            self.read_local(path)

    def write_local(self, path, content):
        print(self.root_path)
        p = self.root_path.joinpath(path)
        with open(p, 'w') as f:
            f.write(content)

    def read_local(self, path):
        p = self.root_path.joinpath(path)
        with open(p, 'r') as f:
            return f.read()
