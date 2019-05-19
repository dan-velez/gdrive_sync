# gdrive_sync
A daemon that keeps a designated folder synced with one designated in your google drive.

## Installation
```bash
$ pip3 install gdrive_sync
```
## Usage
Edit the file `credentials.tmp.json` and change the 
following lines:
```JSON
"client_id":"YOU_CLIENT_ID"
"client_secret":"YOUR_CLIENT_SECRET"
"project_id":"YOUR_PROJECT_ID"
```
These fields can be found in the drive API [documentation](https://developers.google.com/drive/api/v3/quickstart/python). Click the button "ENABLE THE DRIVE API" and download the file. **Rename this file `credentials.json`**.

To sync the directory completely, the folder needs to be uploaded to the drive first, then run the daemon to track local changes.

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
```python
import gdrive
local_path = "/home/user/project/main.py"
drive_path = "project/main.py"
gdrive.upload_file(local_path, drive_path)
# gdrive.parent_id can help you manipulate nested files.
print(gdrive.parent_id(drive_path))
gdrive.create_dir("project/module/submodule")
```
* **upload_file (local_path, drive_path)**
	> Uploads string `local_path` to string `drive_path`.
	*Returns*: string `file_id` if it is uploaded, `None` otherwise.

* **create_dir (drive_path)**
	> Works like `mkdir -p`.
	*Returns*: a string id of the created directory.

* **parent_id (drive_file)**
	> Finds the id of the parent of `drive_file`.
	*Returns*: an object with the id of the file, and the id of the parent. 
	```python
	{
		'parent_id': "string",
		'file_id': "string"
	}
	```

## Description
When the daemon starts it runs an instance of [watchdog](https://pypi.org/project/watchdog/) on the local_path directory. When a file is changed, it is uploaded to a path that corresponds to the one in the local folder. The file is overwritten if it exists. The synchronization function is ran every 60 seconds, and can be changed in the variable `SYNC_INTERVAL`  in the file `main.py`.
