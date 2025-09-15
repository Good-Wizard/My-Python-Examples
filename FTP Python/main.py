from ftplib import FTP, FTP_TLS, error_perm, all_errors
from functools import wraps
from time import sleep
import platform
import os
import sys
import json


PROFILE_FILE = ".ftp_profiles.json"


def clear_screen():
    """پاک کردن صفحه ترمینال"""
    os.system("cls") if platform.system().lower() == "windows" else os.system("clear")


def save_profile(host, username, use_tls):
    """ذخیره پروفایل در فایل JSON (بدون پسورد)"""
    profile = {"host": host, "username": username, "tls": use_tls}
    try:
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2)
    except Exception:
        pass


def load_profile():
    """خواندن پروفایل ذخیره‌شده"""
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def get_login_data(func):
    """دکوراتور برای گرفتن اطلاعات ورود از کاربر"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        clear_screen()

        profile = load_profile()
        if profile:
            print(f"Last profile: host={profile['host']} user={profile['username']} TLS={profile['tls']}")
            use_last = input("Use last profile? (y/N): ").strip().lower()
            if use_last == "y":
                username = profile["username"]
                host = profile["host"]
                use_tls = profile.get("tls", False)
                password = input("Password: ").strip()
                data = [username, password, host, use_tls]
                return func(data, *args, **kwargs)

        username = input("Username: ").strip()
        password = input("Password: ").strip()
        host = input("Host: ").strip()
        tls_input = input("Use FTPS? (y/N): ").strip().lower()
        use_tls = tls_input == "y"

        if not username or not password or not host:
            print("\n[!] همه فیلدها الزامی هستند. دوباره تلاش کنید.")
            sleep(1)
            return wrapper(*args, **kwargs)

        save_profile(host, username, use_tls)
        data = [username, password, host, use_tls]
        return func(data, *args, **kwargs)
    return wrapper


@get_login_data
def login(data):
    """اتصال به FTP/FTPS سرور"""
    print("=" * 20, "\nConnecting...!", sep="")
    ftp = None
    try:
        use_tls = data[3]
        ftp_class = FTP_TLS if use_tls else FTP

        ftp = ftp_class(timeout=10)
        ftp.connect(host=data[2], port=21)
        ftp.login(user=data[0], passwd=data[1])

        if use_tls:
            ftp.prot_p()  # Protect data channel with TLS
            print("[+] Secure FTPS connection established")

        print("\n[+] Connected successfully!")
        print(ftp.getwelcome())
        sleep(1)

        handle_cmds(ftp, data[2])  # حلقه دستورات

    except error_perm as e:
        print(f"\n[!] Permission error (username/password اشتباه؟): {e}")
    except (ConnectionRefusedError, TimeoutError) as e:
        print(f"\n[!] اتصال برقرار نشد: {e}")
        retry = input("Retry? (y/N): ").strip().lower()
        if retry == "y":
            return login(data)
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
  ls                   - List files in current directory
  cd <dir>             - Change directory
  pwd                  - Show current directory
  clear                - Clear the screen
  get <remote> [local] - Download a file
  put <local> [remote] - Upload a file
  delete <remote>      - Delete a file
  mkdir <dir>          - Create directory
  rmdir <dir>          - Remove directory
  rename <old> <new>   - Rename a file or directory
  help                 - Show this help message
  quit / exit          - Disconnect and quit
                """)

            elif command == "ls":
                ftp.dir()

            elif command == "pwd":
                print(ftp.pwd())

            elif command == "cd":
                if len(args) != 1:
                    print("[!] Usage: cd <directory>")
                else:
                    ftp.cwd(args[0])

            elif command == "clear":
                clear_screen()

            elif command == "get":
                if len(args) < 1:
                    print("[!] Usage: get <remote> [local]")
                else:
                    remote_file = args[0]
                    local_file = args[1] if len(args) > 1 else remote_file
                    try:
                        with open(local_file, "wb") as f:
                            ftp.retrbinary(f"RETR {remote_file}", f.write)
                        print(f"[+] Downloaded '{remote_file}' -> '{local_file}'")
                    except all_errors as e:
                        print(f"[!] FTP error: {e}")

            elif command == "put":
                if len(args) < 1:
                    print("[!] Usage: put <local> [remote]")
                else:
                    local_file = args[0]
                    remote_file = args[1] if len(args) > 1 else os.path.basename(local_file)
                    if not os.path.exists(local_file):
                        print(f"[!] Local file not found: {local_file}")
                    else:
                        try:
                            with open(local_file, "rb") as f:
                                ftp.storbinary(f"STOR {remote_file}", f)
                            print(f"[+] Uploaded '{local_file}' -> '{remote_file}'")
                        except all_errors as e:
                            print(f"[!] FTP error: {e}")

            elif command == "delete":
                if len(args) != 1:
                    print("[!] Usage: delete <remote>")
                else:
                    try:
                        ftp.delete(args[0])
                        print(f"[+] Deleted '{args[0]}'")
                    except all_errors as e:
                        print(f"[!] FTP error: {e}")

            elif command == "mkdir":
                if len(args) != 1:
                    print("[!] Usage: mkdir <dir>")
                else:
                    try:
                        ftp.mkd(args[0])
                        print(f"[+] Directory created: {args[0]}")
                    except all_errors as e:
                        print(f"[!] FTP error: {e}")

            elif command == "rmdir":
                if len(args) != 1:
                    print("[!] Usage: rmdir <dir>")
                else:
                    try:
                        ftp.rmd(args[0])
                        print(f"[+] Directory removed: {args[0]}")
                    except all_errors as e:
                        print(f"[!] FTP error: {e}")

            elif command == "rename":
                if len(args) != 2:
                    print("[!] Usage: rename <old> <new>")
                else:
                    try:
                        ftp.rename(args[0], args[1])
                        print(f"[+] Renamed '{args[0]}' -> '{args[1]}'")
                    except all_errors as e:
                        print(f"[!] FTP error: {e}")

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