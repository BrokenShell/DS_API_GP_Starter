import os

from dotenv import load_dotenv
from boto3.session import Session


class S3:
    load_dotenv()
    bucket = os.getenv("S3_BUCKET")
    access_key = os.getenv("AWS_ACCESS_KEY")
    secret_key = os.getenv("AWS_SECRET_KEY")
    directory = "saved_model"
    if not os.path.exists(directory):
        os.mkdir(directory)

    def session(self):
        return Session(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        ).client('s3')

    def upload(self, filename):
        filepath = os.path.join(self.directory, filename)
        with open(filepath, "rb") as file:
            self.session().upload_fileobj(
                Fileobj=file,
                Bucket=self.bucket,
                Key=filename,
            )

    def download(self, filename: str):
        self.session().download_file(
            Bucket=self.bucket,
            Key=filename,
            Filename=f"{self.directory}/{filename}",
        )

    def delete(self, filename: str):
        self.session().delete_object(
            Bucket=self.bucket,
            Key=filename,
        )
