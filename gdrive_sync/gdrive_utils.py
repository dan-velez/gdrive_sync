#!/usr/bin/python3
"gdrive_utils.py - Functions to assist Google Drive CRUD functions."
# TODO
# Function find_id: count the depth to get the right file and avoid
# finding another one by accident.## The drive structure is a tree.
# Do a BFS
# find all the children of a parent
# Traverse from there
import pickle
import os
import pprint
from princ import princ
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors

DEBUG = True

def check_exists(parent_id, fname):
    """Check for fname in the folder designated by parent_id.
    Returns None or the fileId."""
    service = create_service()
    if len(parent_id) == 0: query = ("name='%s'" % (fname))
    else: query = ("name='%s' and '%s' in parents and trashed=false" 
                  % (fname, parent_id))
    resp = service.files().list(
        q=query,
        fields="files(id, name)",
        pageToken=None).execute()
    files = resp.get('files', [])
    if DEBUG: princ("[*] retrieving file_id for [%s]::[%s]"
        % (fname, str(len(files))), "cyan")
    if len(files) > 0: return files[0].get('id')
    else: return None

def find_id(drive_path):
    """Return the ID and the parent ID for a path.
    If a folder does not exist, create it."""
    service = create_service()
    current_parent = ""
    dirs = drive_path.split(os.path.sep)[0:-1]
    fname = drive_path.split(os.path.sep)[-1:][0]
    depth = 0
    # Find each ID and descend into it
    for dirp in dirs:
        if DEBUG: print("[*] search for [%s]" % (dirp))
        # Build search query
        if len(current_parent) == 0: query = ("name='%s'" % (dirp))
        else: query = ("name='%s' and '%s' in parents and trashed=false" 
                      % (dirp, current_parent))
        # Request search
        resp = service.files().list(
            q=query,
            fields="files(id, name)",
            pageToken=None).execute()
        files = resp.get('files', [])
        # Test if file found
        if len(files) > 0:
            # Set new directory ID to search
            current_parent = files[0].get('id')
            if DEBUG: print("[*] directory ID [%s]::[%s]"
                    % (current_parent, str(len(files))))
        else:
            # Create a dir if it does not exist.
            if DEBUG: print("[*] could not find dir [%s]; create it" % (dirp))
            current_parent = create_folder(current_parent, dirp)
        depth += 1
    # Print results
    res = { 'parent_id': current_parent,
            'fname': fname,
            'file_id': check_exists(current_parent, fname) }
    if DEBUG: print("[*] Depth: [%s]" % (depth))
    if DEBUG: pprint.PrettyPrinter(indent=4).pprint(res)
    return res

def create_folder(parent_id, dirname):
    """Create a folder if it does not exist. You will need to know
    the parent ID to run this. Supply "" to create in root.
    """
    service = create_service()
    if len(parent_id) == 0:
        # Create it in the root directory of the drive....
        file_metadata = { 'name': dirname,
                          'mimeType': 'application/vnd.google-apps.folder' }
    else:
        # Create it in a parent directory.
        file_metadata = { 'name': dirname,
                          'parents': [parent_id],
                          'mimeType': 'application/vnd.google-apps.folder' }
    file = service.files().create(
        body=file_metadata,
        fields='id').execute()
    if DEBUG: print("[*] created folder [%s]" % (parent_id))
    return file.get('id')

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
        # if DEBUG: print("[*] drive service created")
        return service
    except Exception as e:
        princ("[*] could not create auth credentials [%s]" %(e), "red")
        exit()

def get_fname(file_id):
    "Return the name of a file by ID."
    service = create_service()
    file_metadata = {
        'name': "",
        'parents': "",
        'mimeType': 'application/vnd.google-apps.folder' }
    file = service.files().get(
        fileId=file_id,
        fields='name').execute()
    return file['name']

def file_info(parent_id, fname):
    "Return the fileId, parentId, and parent name."
    service = create_service()
    query = ("name='%s' and '%s' in parents and trashed=false" % (fname, parent_id))
    resp = service.files().list(
        q=query,
        fields="files(id, name, parents)",
        pageToken=None).execute()
    files = resp.get('files', [])
    return resp.get('files', [])[0]

if __name__ == "__main__":
    # DEBUG #
    # TODO verify this call runs
    find_id("chromeos/prog/module1/TMP.txt")
    pass
