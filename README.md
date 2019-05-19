# gdrive_sync
A daemon that keeps a designated folder synced with one designated in your google drive.

## Installation
```bash
$ pip3 install gdrive_sync
```
## Usage
### CLI
```bash
$ gdrive_sync <local_path> <drive_path>
```
* **local_path** 
	> The path of the folder on the drive to sync.

* **drive_path**
	> The path of the folder on the drive to sync.

### API
The package exposes some API wrapper functions for google drive.
* **upload_file (local_path, drive_path)**
* **parent_id (drive_path)**
* **check_exists (drive_path)**


## Description
When the daemon starts it runs an instance of [watchdog](https://pypi.org/project/watchdog/) on the local_path directory. 
