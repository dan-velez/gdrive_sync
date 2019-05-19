#!/usr/bin/python3
"""
gdrive_sync.py - A daemon that keeps the designated folder always 
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
ROOT_DIR = "chromeos_SYNC"

class FmonHandler(LoggingEventHandler):
    global drive_mods
    def dispatch(self, event):
        if not ("swp" in event.src_path) and not (event.src_path == '.'):
            fname = event.src_path
            if event.src_path.startswith("./"):
                fname = event.src_path[2:]
            print("[%s] : [%s]" % (event.event_type, fname))
            # Add the modification to drive_mods
            drive_mods.append({
                    "type": event.event_type,
                    "path": fname
                })

def sync_shared_folder():
    """Execute any changes in the drive_mods struct,
    relative to the ROOT_DIR.
    """
    global drive_mods
    print("\n[*] syncing drive folder...")
    for mod in drive_mods:
        # Perform sync action.
        if mod['type'] is "created":
            # gdrive.upload_file(mod['path'], ROOT_DIR + '/' + mod['path'])
            print("[*] creating file [%s]" % (mod['path']))

        elif mod['type'] is "modified":
            # gdrive.upload_file(mod['path'], ROOT_DIR + '/' + mod['path'])
            print("[*] updating file [%s]" % (mod['path']))

        elif mod['type'] is "deleted":
            # gdrive.delete_file(ROOT_DIR + '/' + mod['path'])
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
    observer.join()

if __name__ == "__main__":
    main()
