# gdrive_sync
A daemon that keeps a local folder synced with one in your google drive.

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
$ gdrive_sync <drive_path>
```
* **drive_path**
	> The path of the folder on the drive to sync with.

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
gdrive.move_file("drive_path", "project/module/main.py")
```
* **upload_file (local_path, drive_path)**
	> Uploads string `local_path` to string `drive_path`.
	*Returns*: string `file_id` if it is uploaded, `None` otherwise.

* **move_file (drive_src_path, drive_dest_path)**
	> Move a file on the drive. If any folder in the destination path does not exist, it is created.
	*Returns*: String fileID of the moved file.

* **delete_file (drive_path)**
	> Delete a file or directory on the drive.
	*Returns*: The ID of the deleted file.
	
* **create_dir (drive_path)**
	> Works like `mkdir -p`.
	*Returns*: a string id of the created directory.
	
* **find_id (drive_file)**
	> Finds the id of the of `drive_file` by descending into the parent directories.
	*Returns*: an object with the id of the file, and the id of the parent. 
	```python
	{
		'parent_id': "string",
		'file_id': "string"
	}
	```

## Description
When the daemon starts it runs an instance of [watchdog](https://pypi.org/project/watchdog/) on the local_path directory. When a file is changed, it is uploaded to a path that corresponds to the one in the local folder. The file is overwritten if it exists. The synchronization function is ran every 60 seconds, and can be changed in the variable `SYNC_INTERVAL`  in the file `main.py`. The API calls may take a couple minutes to take effect,