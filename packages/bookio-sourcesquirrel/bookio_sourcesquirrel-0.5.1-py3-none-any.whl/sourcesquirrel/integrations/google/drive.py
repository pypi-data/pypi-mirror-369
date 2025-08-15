import logging

from oauth2client.service_account import ServiceAccountCredentials
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

SCOPES = ["https://www.googleapis.com/auth/drive"]
DEFAULT_SECRETS_PATH = "/etc/google/secrets.json"

logger = logging.getLogger(__name__)


class GoogleDriveClient:
    def __init__(self, secrets_path: str):
        secrets_path = secrets_path or DEFAULT_SECRETS_PATH

        gauth = GoogleAuth()
        gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            filename=secrets_path,
            scopes=SCOPES,
        )

        self.drive: GoogleDrive = GoogleDrive(gauth)

    @staticmethod
    def from_google_secrets_path(google_secrets_path: str) -> "GoogleDriveClient":
        return GoogleDriveClient(
            secrets_path=google_secrets_path,
        )

    @staticmethod
    def from_google_secrets_json(google_secrets_json: str) -> "GoogleDriveClient":
        google_secrets_path = "/tmp/secrets.json"

        with open(google_secrets_path, "w") as f:
            f.write(google_secrets_json)

        return GoogleDriveClient.from_google_secrets_path(
            google_secrets_path=google_secrets_path,
        )

    def download(self, file_id: str, path: str) -> None:
        file = self.drive.CreateFile({"id": file_id, "fields": "*"})
        file.GetContentFile(path)

        logger.info(f"Downloaded file {file_id} to {path}")
