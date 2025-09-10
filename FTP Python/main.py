from ftplib import FTP
from functools import wraps

def get_login_data():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            username = input("Username: ")
            password = input("Password: ")
            host = input("Host: ")
            data = [username, password, host]
            return func(data, *args, **kwargs)
        return wrapper
    return decorator


@get_login_data()
def login_ftp(data):
    username = data[0]
    password = data[1]
    host = data[2]
    with FTP(host=host, user= username, passwd = password) as ftp:
        ftp.login()

