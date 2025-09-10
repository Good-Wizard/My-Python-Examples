from ftplib import FTP
from functools import wraps
from time import sleep
import platform, os 

def clear_screen():
    os.system("cls") if platform.system().lower() == "windows" else os.system("clear")

def get_login_data():
    clear_screen()
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
def login(data):
    print("=" * 20, "\nConnecting...!", sep="")
    try:
        ftp = FTP(host=data[2], user=data[0], passwd=data[1])
        print("\nConnected Successfully!")
        sleep(1)
    except TimeoutError:
        print("\nConnection Lost! Try Again.")
        sleep(1)
        return
    except ValueError:
        print("\nWe Got error Please Try Again.")
        sleep(1)
        return
