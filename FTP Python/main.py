from ftplib import FTP, FTP_TLS, error_perm, all_errors
from functools import wraps
from time import sleep
import platform
import os
import sys
import json
from colorama import init, Fore, Style
from tqdm import tqdm
import logging
from logging.handlers import RotatingFileHandler
import os
import ssl


# تنظیمات پایه لاگ
LOG_FILE = "ftp_client.log"
logging.basicConfig(
    filename=LOG_FILE,
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
# جلوگیری از پر شدن دیسک
handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=5)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)


if platform.system().lower() != "windows":
    try:
        import readline
    except ImportError:
        pass

init(autoreset=True)

COMMANDS = [
    "help",
    "ls",
    "pwd",
    "cd",
    "clear",
    "get",
    "put",
    "delete",
    "mkdir",
    "rmdir",
    "rename",
    "quit",
    "exit",
]
PROFILE_FILE = ".ftp_profiles.json"


def completer(text, state):
    options = [cmd for cmd in COMMANDS if cmd.startswith(text)]
    if state < len(options):
        return options[state]
    return None


try:
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
except Exception:
    pass


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
            print(
                f"Last profile: host={profile['host']} user={profile['username']} TLS={profile['tls']}"
            )
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
            print("\n[!] All fields are required. Please try again.")
            sleep(1)
            return wrapper(*args, **kwargs)

        save_profile(host, username, use_tls)
        data = [username, password, host, use_tls]
        return func(data, *args, **kwargs)

    return wrapper

@get_login_data
def login(data):
    host, username, password = data[2], data[0], data[1]
    print("="*20, "\nConnecting...!", sep="")

    while True:
        ftp = None
        try:
            ftp = FTP(timeout=10)
            ftp.connect(host, 21)
            ftp.login(user=username, passwd=password)
            print("[+] Connected successfully (FTP)")

            print(ftp.getwelcome())
            sleep(1)
            handle_cmds(ftp, host)
            break

        except error_perm as e:
            print(f"[!] Permission error: {e}")
            break
        except (ConnectionRefusedError, TimeoutError) as e:
            print(f"[!] Connection failed: {e}")
            retry = input("Retry? (y/N): ").strip().lower()
            if retry != "y":
                break
        except all_errors as e:
            print(f"[!] FTP error: {e}")
            break
        except Exception as e:
            print(f"[!] Unknown error: {e}")
            break
        finally:
            if ftp is not None:
                try:
                    ftp.quit()
                except Exception:
                    try:
                        ftp.close()
                    except Exception:
                        pass


def handle_cmds(ftp, host):
    """حلقه دستورات اصلی"""
    print("[-] Use -help To See Commands")
    while True:
        try:
            cwd = ftp.pwd()
            prompt = Fore.CYAN + f"ftp@{host}:{cwd}> " + Style.RESET_ALL
            cmd = input(prompt).strip()
            if not cmd:
                continue

            parts = cmd.split()
            command = parts[0].lower()
            args = parts[1:]

            if command in ["quit", "exit"]:
                print("[-] Closing connection...")
                break

            elif command == "help":
                print(
                    """
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
                """
                )

            elif command == "pwd":
                print(Fore.GREEN + ftp.pwd())
            elif command == "ls":
                print(Fore.YELLOW + "[Listing files...]")
                ftp.dir()

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
                        logging.info(f"Downloaded '{remote_file}' -> '{local_file}'")
                        size = ftp.size(remote_file)
                        with open(local_file, "wb") as f, tqdm(
                            total=size, unit="B", unit_scale=True, desc=remote_file
                        ) as bar:

                            def callback(data):
                                f.write(data)
                                bar.update(len(data))

                            ftp.retrbinary(f"RETR {remote_file}", callback)
                        print(
                            Fore.GREEN
                            + f"[+] Downloaded '{remote_file}' -> '{local_file}'"
                        )
                    except all_errors as e:
                        print(Fore.RED + f"[!] FTP error: {e}")
                        logging.error(f"Failed to download '{remote_file}': {e}")

            elif command == "put":
                if len(args) < 1:
                    print("[!] Usage: put <local> [remote]")
                else:
                    local_file = args[0]
                    remote_file = (
                        args[1] if len(args) > 1 else os.path.basename(local_file)
                    )
                    if not os.path.exists(local_file):
                        print(Fore.RED + f"[!] Local file not found: {local_file}")
                    else:
                        try:
                            size = os.path.getsize(local_file)
                            with open(local_file, "rb") as f, tqdm(
                                total=size, unit="B", unit_scale=True, desc=local_file
                            ) as bar:

                                def callback(data):
                                    bar.update(len(data))

                                ftp.storbinary(f"STOR {remote_file}", f, 1024, callback)
                            print(
                                Fore.GREEN
                                + f"[+] Uploaded '{local_file}' -> '{remote_file}'"
                            )
                        except all_errors as e:
                            print(Fore.RED + f"[!] FTP error: {e}")

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
                print(
                    f"[!] Unknown command: {command}. Type 'help' for available commands."
                )

        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n[!] Interrupted. Type 'quit' to exit.")
        except EOFError:
            print(Fore.YELLOW + "\n[-] End of input detected. Exiting...")
            break


if __name__ == "__main__":
    try:
        login()
    except KeyboardInterrupt:
        print("\n[!] The program was stopped.")
        sys.exit(0)
