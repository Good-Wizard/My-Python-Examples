from ftplib import FTP, error_perm, all_errors
from functools import wraps
from time import sleep
import platform
import os
import sys


def clear_screen():
    """پاک کردن صفحه ترمینال"""
    os.system("cls") if platform.system().lower() == "windows" else os.system("clear")


def get_login_data(func):
    """
    دکوراتور برای گرفتن اطلاعات ورود از کاربر
    (username, password, host)
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        clear_screen()
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        host = input("Host: ").strip()

        if not username or not password or not host:
            print("\n[!] همه فیلدها الزامی هستند. دوباره تلاش کنید.")
            sleep(1)
            return wrapper(*args, **kwargs)

        data = [username, password, host]
        return func(data, *args, **kwargs)
    return wrapper


@get_login_data
def login(data):
    """اتصال به FTP سرور"""
    print("=" * 20, "\nConnecting...!", sep="")
    ftp = None
    try:
        ftp = FTP(timeout=10)  # تایم‌اوت اضافه شد
        ftp.connect(host=data[2], port=21)
        ftp.login(user=data[0], passwd=data[1])
        print("\n[+] Connected successfully!")
        print(ftp.getwelcome())
        sleep(1)
        # در فاز بعد اینجا می‌ره به handle_cmds
        # handle_cmds(ftp)

    except error_perm as e:
        print(f"\n[!] Permission error (username/password اشتباه؟): {e}")
    except (ConnectionRefusedError, TimeoutError) as e:
        print(f"\n[!] اتصال برقرار نشد: {e}")
    except all_errors as e:
        print(f"\n[!] خطای عمومی FTP: {e}")
    except Exception as e:
        print(f"\n[!] خطای ناشناخته: {e}")
    finally:
        if ftp is not None:
            try:
                ftp.quit()
                print("\n[-] Connection closed.")
            except Exception:
                ftp.close()


if __name__ == "__main__":
    try:
        login()
    except KeyboardInterrupt:
        print("\n[!] برنامه متوقف شد.")
        sys.exit(0)
