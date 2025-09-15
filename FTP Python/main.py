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
    """دکوراتور برای گرفتن اطلاعات ورود از کاربر"""
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
        ftp = FTP(timeout=10)
        ftp.connect(host=data[2], port=21)
        ftp.login(user=data[0], passwd=data[1])
        print("\n[+] Connected successfully!")
        print(ftp.getwelcome())
        sleep(1)

        handle_cmds(ftp, data[2])  # رفتن به حلقه دستورات

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


def handle_cmds(ftp, host):
    """حلقه دستورات اصلی"""
    while True:
        try:
            cwd = ftp.pwd()
            cmd = input(f"ftp@{host}:{cwd}> ").strip()

            if not cmd:
                continue

            parts = cmd.split()
            command = parts[0].lower()
            args = parts[1:]

            if command in ["quit", "exit"]:
                print("[-] Closing connection...")
                break

            elif command == "help":
                print("""
Available commands:
  ls              - List files in current directory
  cd <dir>        - Change directory
  pwd             - Show current directory
  clear           - Clear the screen
  help            - Show this help message
  quit / exit     - Disconnect and quit
                """)

            elif command == "ls":
                ftp.dir()

            elif command == "pwd":
                print(ftp.pwd())

            elif command == "cd":
                if len(args) != 1:
                    print("[!] Usage: cd <directory>")
                else:
                    try:
                        ftp.cwd(args[0])
                    except error_perm as e:
                        print(f"[!] Permission error: {e}")
                    except all_errors as e:
                        print(f"[!] FTP error: {e}")

            elif command == "clear":
                clear_screen()

            else:
                print(f"[!] Unknown command: {command}. Type 'help' for available commands.")

        except KeyboardInterrupt:
            print("\n[!] Interrupted. Type 'quit' to exit.")
        except EOFError:
            print("\n[-] End of input detected. Exiting...")
            break


if __name__ == "__main__":
    try:
        login()
    except KeyboardInterrupt:
        print("\n[!] برنامه متوقف شد.")
        sys.exit(0)
