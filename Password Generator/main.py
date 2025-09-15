import random
import string
import time
import sys
import pyperclip
from colorama import init, Fore
from time import sleep
import os

# Initialize colorama
init(autoreset=True)

# کاراکترها
LOWERCASE = string.ascii_lowercase
UPPERCASE = string.ascii_uppercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?/"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def animate_text(text, delay=0.03, border=False):
    if border:
        line = "+" + "-" * (len(text) + 2) + "+"
        print(Fore.MAGENTA + line)
        sys.stdout.write(Fore.MAGENTA + "| ")
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    if border:
        print(Fore.MAGENTA + " |")
        print(Fore.MAGENTA + line)
    else:
        print()

def generate_password(length=12, use_upper=True, use_digits=True, use_symbols=True):
    char_pool = LOWERCASE
    password = []

    # همیشه با یک کاراکتر شروع شود
    start_char_pool = LOWERCASE
    if use_upper: start_char_pool += UPPERCASE
    if use_digits: start_char_pool += DIGITS
    if use_symbols: start_char_pool += SYMBOLS
    password.append(random.choice(start_char_pool))
    
    if use_upper: char_pool += UPPERCASE
    if use_digits: char_pool += DIGITS
    if use_symbols: char_pool += SYMBOLS

    while len(password) < length:
        password.append(random.choice(char_pool))
    random.shuffle(password[1:])  # بقیه کاراکترها مخلوط شوند
    return ''.join(password)

def password_strength(password):
    score = 0
    if any(c.islower() for c in password): score += 1
    if any(c.isupper() for c in password): score += 1
    if any(c.isdigit() for c in password): score += 1
    if any(c in SYMBOLS for c in password): score += 1
    if len(password) >= 12: score += 1

    bar_length = 20
    filled = int(bar_length * score / 5)
    bar = Fore.GREEN + '|' * filled + Fore.RED + '|' * (bar_length - filled)

    if score <= 2: level = Fore.RED + "Weak"
    elif score == 3: level = Fore.YELLOW + "Medium"
    else: level = Fore.GREEN + "Strong"
    
    return f"|{bar}| {level}"

def generating_animation():
    print("\nGenerating passwords", end="")
    for _ in range(6):
        sys.stdout.write(Fore.CYAN + ".")
        sys.stdout.flush()
        time.sleep(0.3)
    print("\n")

def main():
    clear_screen()
    # ولکام جذاب با border
    animate_text("WELCOME TO THE ULTIMATE PASSWORD GENERATOR", delay=0.02, border=True)

    try:
        length = int(input("[ $ ] Enter password length (8-64 recommended) : "))
        use_upper = input("[ $ ] Include uppercase letters? (y/n) : ").lower() == 'y'
        use_digits = input("[ $ ] Include digits? (y/n) : ").lower() == 'y'
        use_symbols = input("[ $ ] Include symbols? (y/n) : ").lower() == 'y'
        count = int(input("[ $ ] How many passwords to generate? : "))
        save_file = input("[ $ ] Save passwords to file? (y/n) : ").lower() == 'y'
        if save_file:
            filename = input("[ $ ] Enter filename (default: passwords.txt) : ")
            if not filename:
                filename = "passwords.txt"
    except ValueError:
        print(Fore.RED + "Invalid input! Please enter numbers correctly.")
        sleep(1.5)
        main()


    generating_animation()

    passwords = []

    for i in range(count):
        pwd = generate_password(length, use_upper, use_digits, use_symbols)
        passwords.append(pwd)
        print(f"[{i+1}] Password: {pwd}")
        print("Strength:", password_strength(pwd))
        time.sleep(0.1)

        if i == 0:
            pyperclip.copy(pwd)
            print(Fore.MAGENTA + "-> First password copied to clipboard!")

    if save_file:
        with open(filename, 'w') as f:
            for pwd in passwords:
                f.write(pwd + '\n')
        print(Fore.GREEN + f"\nPasswords saved to {filename}!")

    animate_text("All passwords generated successfully!", 0.02, border=True)
    again = input(Fore.YELLOW + "\nDo you want to generate more passwords? (y/n) : ").strip().lower()
    if again in ['n', 'no', 'exit', 'quit']:
        animate_text("Thanks for using the Ultimate Password Generator! Stay secure! 🔐", delay=0.02, border=True)
        sys.exit(0)
    main()

if __name__ == "__main__":
    main()
