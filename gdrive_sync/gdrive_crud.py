#!/usr/bin/python3
"""
gdrive_crud.py - Contains the functions for CRUD on your gdrive.
"""

import os
import mimetypes
import pprint
from princ import princ
from apiclient.http import MediaFileUpload
from gdrive_utils import create_service
from gdrive_utils import find_id

DEBUG = True

## File Functions ##############################################

def upload_file(local_path, drive_path):
    """Create a new file on the drive. If the file already exists,
    the old one will be overwritten."""
    # Prepare the upload objects
    service = create_service()
    mime_type = mimetypes.MimeTypes().guess_type(local_path)[0]
    media_body = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
    ids = find_id(drive_path)
    meta_data= { 'name': drive_path.split(os.path.sep)[-1:][0],
                 'parents': [ids['find_id']] }
    print("[*] uploading [%s] mimetype [%s]" % (local_path, mimetype))
    # Upload the file
    try:
        if ids['file_id'] is None:
            # Create file
            f = service.files().create(
                body=meta_data,
                media_body=media_body,
                fields='id').execute()
        else:
            # Modify file
            f = service.files().update(
                fileId=ids['file_id'],
                media_body=media_body,
                fields='id').execute()
        if not f is None: princ("[*] uploaded %s" % (local_path), "green")
    except Exception as e:
        princ("[*] could not create file [%s]: [%s]" % (drive_path, e), "red")

def delete_file(drive_path):
    "Delete a file on the drive."
    service = create_service()
    print("[*] deleting [%s]" % (drive_path))
    ids = find_id(drive_path)
    file_id = ids['file_id']
    if not file_id is None:
        resp = service.files().delete(fileId=file_id).execute()
    princ("[*] deleted [%s]" % (drive_path), "green")
    return

def move_file(drive_src_path, drive_dest_path):
    "Move a file or directory on the drive."
    service = create_service()
    # Get IDs for bot paths
    ids_src = find_id(drive_src_path)
    ids_dest = find_id(drive_dest_path)
    # Retrieve the existing parents to remove
    f = service.files().get(fileId=ids_src['file_id'],
			    fields='parents').execute()
    previous_parents = ",".join(f.get('parents'))
    # Update the file by changing its parent ID.
    f = service.files().update(
        fileId=ids_src['file_id'],
        addParents=ids_dest['find_id'],
        removeParents=previous_parents, # ids_src['find_id'],
        fields=('id, parents')).execute()
    princ("[*] moved [%s] to [%s]. ID: [%s]" %
        (drive_src_path, drive_dest_path, f.get('id')), "green")
    return f.get('id')

## Directory Functions #########################################

def create_dir(drive_path):
    "Create a directory on the Google Drive. Works like mkdir -p."
    res = find_id(drive_path+"/TMP.txt")['find_id']
    princ("[*] created dir [%s]" % (drive_path), "green")
    return res

## DEBUG ##
if __name__ == "__main__":
    try:
        upload_file("main.py", "chromeos/local/main/pydrive.py")
        pass
    except Exception as e:
       #  print("[*] could not execute [%s]" % (e))
       pass
