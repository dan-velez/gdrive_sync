#!/usr/bin/python3
"""
gdrive.py - Contains the functions for CRUD on your gdrive.
"""

import pickle
import os
import mimetypes
import pprint
from princ import princ
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors
from apiclient.http import MediaFileUpload

DEBUG = True

def upload_file(local_path, drive_path):
    """Create a new file on the drive. If the file already exists,
    the old one will be overwritten."""
    # Prepare the upload objects
    print("[*] uploading [%s]" % (local_path))
    service = create_service()
    mime_type = mimetypes.MimeTypes().guess_type(local_path)[0]
    print("[*] mimetype of [%s] is [%s]" % (local_path, mime_type))
    media_body = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
    ids = parent_id(drive_path)
    meta_data= {
                'name': drive_path.split(os.path.sep)[-1:][0],
                'parents': [ids['parent_id']]
            }
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
            pass
        if not f is None: princ("[*] uploaded %s" % (local_path), "green")
    except Exception as e:
        princ("[*] could not create file [%s]: [%s]" % (drive_path, e), "red")

def move_file(drive_src_path, drive_dest_path):
    "Move a file on the drive."
    service = create_service()
    # Get IDs for bot paths
    ids_src = parent_id(drive_src_path)
    ids_dest = parent_id(drive_dest_path)
    # Retrieve the existing parents to remove
    f = service.files().get(fileId=ids_src['file_id'],
			    fields='parents').execute()
    previous_parents = ",".join(f.get('parents'))
    f = service.files().update(
        fileId=ids_src['file_id'],
        addParents=ids_dest['parent_id'],
        removeParents=previous_parents, # ids_src['parent_id'],
        fields=('id, parents')).execute()
    princ("[*] moved [%s] to [%s]. ID: [%s]" %
            (drive_src_path, drive_dest_path, f.get('id')), "green")
    return f.get('id')

def move_dir(drive_src_path, drive_dest_path):
    "Move a directory on the drive"
    service = create_service()
    ids_src = parent_id(drive_src_path)
    ids_dest = parent_id(drive_dest_path)
    # Get IDs for both paths

def create_dir(drive_path):
    "Create a directory on the Google Drive."
    res = parent_id(drive_path+"/TMP.txt")['parent_id']
    princ("[*] created dir [%s]" % (drive_path), "green")
    return res

def delete_file(drive_path):
    "Delete a file on the drive."
    service = create_service()
    print("[*] deleting [%s]" % (drive_path))
    ids = parent_id(drive_path)
    file_id = ids['file_id']
    if not file_id is None:
        resp = service.files().delete(fileId=file_id).execute()
    princ("[*] deleted [%s]" % (drive_path), "green")
    return

def check_exists(parent_id, fname):
    "Check for fname in the folder designated by parent_id."
    service = create_service()
    if len(parent_id) == 0: query = ("name='%s'" % (fname))
    else: query = ("name='%s' and '%s' in parents" % (fname, parent_id))
    resp = service.files().list(
            q=query,
            fields="files(id, name)",
            pageToken=None).execute()
    files = resp.get('files', [])
    if len(files) > 0: return files[0].get('id')
    else: return None

def parent_id(drive_path):
    """Return the parent ID for a path. 
    If a folder does not exist, create it."""
    service = create_service()
    current_parent = ""
    dirs = drive_path.split(os.path.sep)[0:-1]
    fname = drive_path.split(os.path.sep)[-1:][0]
    # Find each ID and descend into it
    for dirp in dirs:
        if DEBUG: print("[*] search for [%s]" % (dirp))
        # Build search query
        if len(current_parent) == 0: query = ("name='%s'" % (dirp))
        else: query = ("name='%s' and '%s' in parents" % (dirp, current_parent))
        # Request search
        resp = service.files().list(
                q=query,
                fields="files(id, name)",
                pageToken=None).execute()
        files = resp.get('files', [])
        # Test if file found
        if len(files) > 0:
            current_parent = files[0].get('id')
            if DEBUG: print("[*] directory ID [%s]" % current_parent)
        else:
            # Create a dir if it does not exist.
            if DEBUG: print("[*] could not find dir [%s]; create it" % (dirp))
            if len(current_parent) == 0:
                file_metadata = {
                    'name': dirp,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
            else:
                file_metadata = {
                    'name': dirp,
                    'parents': [current_parent],
                    'mimeType': 'application/vnd.google-apps.folder'
                }
            file = service.files().create(
                body=file_metadata,
                fields='id').execute()
            current_parent = file.get('id')
            if DEBUG: print("[*] created folder, new parent [%s]" % (current_parent))
    # Print results
    res = {
            'parent_id': current_parent,
            'file_id': check_exists(current_parent, fname)
        }
    if DEBUG: pprint.PrettyPrinter(indent=4).pprint(res)
    return res

def create_service():
    "Creates the service object for further use."
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/drive']
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    creds = None
    try:
        # Create auth credentials.
        if os.path.exists('data/token.pickle'):
            with open('data/token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'data/credentials.json', SCOPES)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('data/token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        service = build('drive', 'v3', credentials=creds)
        if DEBUG: print("[*] drive service created")
        return service
    except Exception as e:
        princ("[*] could not create auth credentials [%s]" %(e), "red")
        exit()

## DEBUG ##
if __name__ == "__main__":
    try:
        upload_file("main.py", "chromeos/local/main/pydrive.py")
        # delete_file("chromeos/local/main/pydrive.py")
        # create_dir("project2/module/submodule")
        # create_dir("chromeos/project2/module/submodule")
        # create_dir("project3/module/submodule")
        #########################
        # Find a file or directory
        service = create_service()
        pass
    except Exception as e:
       #  print("[*] could not execute [%s]" % (e))
       pass