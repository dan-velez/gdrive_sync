#!/usr/bin/python3
"""
main.py - A daemon that keeps the designated folder always 
synced to google drive. The drive is specified in a config file.
"""

import sys
import time
import gdrive
import os
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

# The interval at which the drive will sync with the shared folder,
# in secods.
SYNC_INTERVAL=30

# A structure that holds the drive modifications that have occured
# after the last sync interval.
drive_mods = []

# The folder on the drive that is to be synced with this one.
ROOT_DIR = ""

# Use this for a watchdog bug of multiple event generation.
last_read = time.time()
last_file = ""
las_event = ""

class FmonHandler(LoggingEventHandler):
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
            print("[%s] : [%s]" % (event.event_type, fname))
            if not mod_exists(fname): drive_mods.append({
                    "type": event.event_type,
                    "path": fname
                })

def clean_path(fname):
    while (fname[0] == ".") or (fname[0] == "/"):
        fname = fname[1:]
    return fname

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
    print("\n[*] syncing drive folder...")
    for mod in drive_mods:
        # Perform sync action.
        print(ROOT_DIR+"/"+mod['path'])
        if mod['type'] is "created":
            if os.path.isdir(mod['path']):
                print("[*] creating dir [%s]" % (mod['path']))
                gdrive.create_dir(ROOT_DIR+"/"+mod['path'])
            else:
                print("[*] creating file [%s]" % (mod['path']))
                gdrive.upload_file(mod['path'], ROOT_DIR + '/' + mod['path'])

        elif mod['type'] is "modified":
            gdrive.upload_file(mod['path'], ROOT_DIR + '/' + mod['path'])
            print("[*] updating file [%s]" % (mod['path']))

        elif mod['type'] is "deleted":
            gdrive.delete_file(ROOT_DIR + '/' + mod['path'])
            print("[*] deleting file [%s]" % (mod['path']))
    print("[*] sync complete, resetting drive_mods\n")
    drive_mods = []

def usage():
    print("""Usage: gdrive_sync <local_dir> <drive_dir>""")
    exit()

def main():
    if len(sys.argv) < 3:
        usage()
    path = sys.argv[1]
    ROOT_DIR = sys.argv[2]
    print("[*] gdrive_sync daemon started")
    print("[*] local path: [%s]" % (os.path.abspath(path)))
    print("[*] drive path: [%s]" % (ROOT_DIR))
    event_handler = FmonHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print("[*] running watchdog")
    # register_schedule()
    try:
        while True:
            time.sleep(SYNC_INTERVAL)
            sync_shared_folder()
    except KeyboardInterrupt:
        observer.stop()
    except Exception as e:
        print("[*] execution error [%s]" % (e))
    observer.join()

if __name__ == "__main__":
    main()
