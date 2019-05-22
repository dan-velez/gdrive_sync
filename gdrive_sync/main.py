#!/usr/bin/python3
"""
main.py - A daemon that keeps the designated folder always 
synced to google drive. The drive is specified in a config file.
"""

import sys
import time
import os
import pprint
import gdrive_crud as gdrive
from princ import princ
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

# The interval at which the drive will sync with the shared folder,
# in secods.
SYNC_INTERVAL=10

# A structure that holds the drive modifications that have occured
# after the last sync interval.
drive_mods = []

# The folder on the drive that is to be synced with this one.
ROOT_DIR = ""

# Verbose logging
DEBUG = True

# Use this for a watchdog bug of multiple event generation.
last_read = time.time()
last_file = ""
las_event = ""

class FmonHandler(LoggingEventHandler):
    "Event handler for watchdog."
    def dispatch(self, event):
        global last_read
        global last_file
        global last_event
        global drive_mods
        # Don't sync vim's swp files
        if (not ("swp" in event.src_path) and not (event.src_path == '.') and
        not("swx" in event.src_path)):
            # Clean path
            fname = clean_path(event.src_path)
            dest_path = ""
            if event.event_type == "moved": dest_path = clean_path(event.dest_path)
            # Don't process modified directory events
            if event.event_type == "modified" and (os.path.isdir(fname) or
            (not os.path.isdir(fname) and not os.path.isfile(fname))):
                return
            # Fix bug in watchdog
            read_time = time.time()
            if ((read_time - last_read < 1) and (last_file == fname) and 
            (last_event == 'created')):
                last_event = event.event_type
                last_read = read_time
                last_file = fname
                return
            last_file = fname
            last_read = read_time
            last_event = event.event_type
            # Add the modification to drive_mods
            princ("[%s] : [%s]" % (event.event_type, fname), "cyan")
            if not mod_exists(fname): drive_mods.append({
                    "type": event.event_type,
                    "path": fname,
                    "dest_path": dest_path
                })

def clean_path(fname):
    if fname.startswith("./"): fname = fname[2:]
    return fname

def fix_drive_mods():
    "Reorder 'move dir' events so that the files are moved first."
    global drive_mods
    print("[*] fixing drive mods...")
    d_mods = drive_mods.copy()
    # Holds the mods of the 'move dir' event.
    event_group = []
    # Where to splice the array
    event_group_idx = 0
    i = 0
    while i < len(d_mods):
        print("[*] scanning d_mods [%s]" % (str(i)))
        mod = d_mods[i]
        # Find the mods
        if ((mod['type'] == 'moved' or mod['type'] == 'deleted') 
        and os.path.isdir(mod['dest_path'])):
            print("\n[*] found start of 'move dir' event group [%s]\n" %(mod))
            # Collect the mods that are in the event group
            moved_dir = mod['path'].split(os.path.sep)[0]
            event_group_idx = i
            j = 0
            for submod in d_mods[i:]:
                if ((submod['type'] == mod['type']) and 
                (submod['path'].split(os.path.sep)[0] == moved_dir)):
                    event_group.append(submod)
                    j = j+1
                else:
                    break
            # Reverse array
            # event_group.reverse()
            # print("\n[*] reversed event group")
            # if DEBUG: pprint.PrettyPrinter(indent=4).pprint(event_group)
            # print("\n")
            # Splice the bad mods out using d_mods[i] to d_mods[j+1]
            d_mods = d_mods[0:i+1]+d_mods[i+j:]
            # Splice the fixed mods into d_mods[i]
            # d_mods = d_mods[0:i]+event_group+d_mods[i:]
            # Set drive_mods to the fixed copy
            print("[*] fixed drive mods")
            if DEBUG: pprint.PrettyPrinter(indent=4).pprint(d_mods)
            print("\n")
            drive_mods = d_mods
            i += j-1
        i += 1

def mod_exists(fname):
    "Search the drive_mods for an existing modification."
    global drive_mods
    exists = False
    for mod in drive_mods:
        if mod['path'] == fname:
            exists = True
            break
    return exists

def sync_shared_folder():
    """Execute any changes in the drive_mods struct,
    relative to the ROOT_DIR.
    """
    global drive_mods
    fix_drive_mods()
    d_mods = drive_mods.copy()
    drive_mods = []
    print("\n[*] syncing drive folder...")
    print("*"*64)
    for mod in d_mods:
        # Perform sync action.
        try:
            if mod['type'] is "created":
                # Create directory
                if os.path.isdir(mod['path']):
                    princ("[*] creating dir [%s]" % (mod['path']), "blue")
                    gdrive.create_dir(ROOT_DIR+"/"+mod['path'])
                else:
                # Create file
                    princ("[*] creating file [%s]" % (mod['path']), "blue")
                    gdrive.upload_file(mod['path'], ROOT_DIR + '/' + mod['path'])

            elif mod['type'] is "modified":
                # Update file
                princ("[*] updating file [%s]" % (mod['path']), "blue")
                gdrive.upload_file(mod['path'], ROOT_DIR + '/' + mod['path'])

            elif mod['type'] is "moved":
                # Move file or folder
                princ("[*] moving file [%s] to [%s]" % (mod['path'], mod['dest_path']), "blue")
                gdrive.move_file(ROOT_DIR+"/"+mod['path'], ROOT_DIR+"/"+mod['dest_path']) 

            elif mod['type'] is "deleted":
                princ("[*] deleting file [%s]" % (mod['path']), "blue")
                gdrive.delete_file(ROOT_DIR + '/' + mod['path'])

        except Exception as e:
            princ("[*] sync_shared_folder failed [%s]" % (e), "red")
        print("-"*64)
    print("[*] sync complete\n")

def usage():
    print("""Usage: gdrive_sync <local_dir> <drive_dir>""")
    exit()

def main():
    global ROOT_DIR
    if len(sys.argv) < 2:
        usage()
    path = '.'
    ROOT_DIR = sys.argv[1] # Folder in Google Drive to sync to.
    print("[*] gdrive_sync daemon started")
    print("[*] local path: [%s]" % (os.path.abspath(path)))
    print("[*] drive path: [%s]" % (ROOT_DIR))
    try:
        # Start file monitor
        event_handler = FmonHandler()
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()
        print("[*] running watchdog")
        # Register scheduler
        while True:
            time.sleep(SYNC_INTERVAL)
            sync_shared_folder()
    except KeyboardInterrupt:
        observer.stop()
    except Exception as e:
        princ("[*] execution error [%s]" % (e), "red")
    observer.join()

def debug_fix_drive_mods():
    princ("[*] Running debug_fix_drive_mods", "green")
    global drive_mods
    drive_mods = [
        {
            "type": "created",
            "path": "chromeos/home_synced/x.py",
            "dest_path": ""
        },
        {
            "type": "created",
            "path": "chromeos/home_synced/y.py",
            "dest_path": ""
        },
        {
            "type": "created",
            "path": "chromeos/home_synced/z.py",
            "dest_path": ""
        },
        {
            "type": "deleted",
            "path": "data",
            "dest_path": "__pycache__"
        },
        {
            "type": "deleted",
            "path": "data",
            "dest_path": "__pycache__/x.py"
        },
        {
            "type": "deleted",
            "path": "data",
            "dest_path": "__pycache__/y.py"
        },
        {
            "type": "deleted",
            "path": "data",
            "dest_path": "__pycache__/z.py"
        },
        {
            "type": "created",
            "path": "chromeos/home_synced/c.py",
            "dest_path": ""
        },
        {
            "type": "created",
            "path": "chromeos/home_synced/b.py",
            "dest_path": ""
        }
    ]
    fix_drive_mods()

if __name__ == "__main__":
    # main()
    debug_fix_drive_mods()
