import os
import sys
import argparse
import fnmatch
from zipfile import ZipFile, ZIP_DEFLATED
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file']


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Compress and upload files to Google Drive")
    parser.add_argument(
        "directory", help="The target directory containing the files")
    parser.add_argument(
        "folder_id", help="Google Drive folder ID for uploading files")
    parser.add_argument("--exclude", nargs="*",
                        help="File patterns to exclude from upload (e.g. *.log)")
    parser.add_argument("--max-zip-gb", type=float, default=3.5,
                        help="Maximum zip file size in GiB (default: 3.5)")
    parser.add_argument("-d", "--delete-after-sending",
                        action="store_true", help="Delete local files after uploading")
    args = parser.parse_args()

    # Convert max-zip-gb to bytes
    max_zip_bytes = args.max_zip_gb * (1024 ** 3)

    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)

    compress_and_upload_files(args.directory, max_zip_bytes,
                              args.folder_id, args.delete_after_sending, args.exclude)

# Authenticate with Google Drive API


def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def should_exclude(file, patterns):
    if patterns is None:
        return False
    for pattern in patterns:
        if fnmatch.fnmatch(file, pattern):
            return True
    return False


def compress_and_upload_files(directory, max_zip_bytes, folder_id, delete_after_sending, exclude_patterns):
    total_size = 0
    zip_file = None
    files_in_zip = []

    for root, _, files in os.walk(directory):
        for file in files:
            if should_exclude(file, exclude_patterns):
                continue

            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)

            if total_size + file_size > max_zip_bytes:
                if zip_file is not None:
                    zip_file.close()
                    upload_and_cleanup(
                        zip_file.filename, folder_id, files_in_zip, delete_after_sending)
                    files_in_zip = []

                zip_name = os.path.join(
                    directory, f"{os.path.basename(root)}_temp.zip")
                zip_file = ZipFile(zip_name, "w", ZIP_DEFLATED)
                total_size = 0

            if zip_file is not None:
                zip_file.write(file_path, os.path.relpath(
                    file_path, directory))
                files_in_zip.append(file_path)
                total_size += file_size

    if zip_file is not None:
        zip_file.close()
        upload_and_cleanup(zip_file.filename, folder_id,
                           files_in_zip, delete_after_sending)


def upload_and_cleanup(zip_path, folder_id, files_in_zip, delete_after_sending):
    file_id = upload_to_drive(zip_path, folder_id)
    if file_id is not None:
        if delete_after_sending:
            delete_local_files(files_in_zip)
            delete_local_file(zip_path)


def upload_to_drive(file_path, folder_id):
    file_metadata = {
        "name": os.path.basename(file_path),
        "mimeType": "application/zip",
        "parents": [folder_id]
    }

    media = MediaFileUpload(
        file_path, mimetype="application/zip", resumable=True)

    try:
        file = service.files().create(body=file_metadata,
                                      media_body=media, fields="id").execute()
        print(f"Uploaded {file.get('id')}")
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

    return file.get("id")


def delete_local_files(file_paths):
    for file_path in file_paths:
        os.remove(file_path)
        print(f"Deleted {file_path}")


def delete_local_file(file_path):
    os.remove(file_path)
    print(f"Deleted {file_path}")


if __name__ == '__main__':
    main()
