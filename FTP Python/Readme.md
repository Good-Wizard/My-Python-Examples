# FTP Python Client

A functional FTP client written in Python, suitable for connecting to FTP and FTPS servers, uploading and downloading files, and managing folders via a command line interface.

---

## Features

- Connecting to FTP and FTPS servers (with TLS)
- Saving and loading user profiles
- Interactive commands such as `ls`, `cd`, `pwd`, `get`, `put`, `delete`, `mkdir`, `rmdir`, `rename`, `clear`, `quit`
- Support for resuming downloads and uploads using `tqdm`
- Command line interface with command autocompletion
- Color-coded error and status messages

---

## Usage
To install the requirements use `pip install -r requirements.txt`
And to run use `python main.py`
After running the script, you will be prompted to enter your username, password, and FTP server address.
If you want to use FTPS (secure connection), select the corresponding option.
After a successful connection, you can use interactive commands to manage files and folders.

---

## Save Profile
After a successful login, your profile information (without password) will be saved in the ftp_profiles.json file. In the future, you can use the saved profile for faster login.
