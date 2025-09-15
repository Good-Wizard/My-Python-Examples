import random
import string
import time
import sys
import pyperclip
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# کاراکترهای مختلف
LOWERCASE = string.ascii_lowercase
UPPERCASE = string.ascii_uppercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?/"

def animate_text(text, delay=0.03):
    """انیمیشن تایپ متن"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def show_progress_bar(progress, total, length=30):
    """نمایش Progress Bar رنگی"""
    filled_length = int(length * progress // total)
    bar = Fore.GREEN + '█' * filled_length + Fore.RED + '█' * (length - filled_length)
    percent = (progress / total) * 100
    sys.stdout.write(f"\rProgress: |{bar}| {percent:.1f}%")
    sys.stdout.flush()

def password_strength(password):
    """محاسبه و نمایش قدرت پسورد به شکل Progress Bar"""
    score = 0
    if any(c.islower() for c in password): score += 1
    if any(c.isupper() for c in password): score += 1
    if any(c.isdigit() for c in password): score += 1
    if any(c in SYMBOLS for c in password): score += 1
    if len(password) >= 12: score += 1

    # نوار قدرت بصری
    bar_length = 20
    filled = int(bar_length * score / 5)
    bar = Fore.GREEN + '█' * filled + Fore.RED + '█' * (bar_length - filled)
    if score <= 2:
        level = Fore.RED + "Weak"
    elif score == 3:
        level = Fore.YELLOW + "Medium"
    else:
        level = Fore.GREEN + "Strong"
    return f"|{bar}| {level}"

def generate_password_custom(length, min_upper, min_lower, min_digits, min_symbols):
    """تولید پسورد با قوانین سخت‌گیرانه"""
    if length < (min_upper + min_lower + min_digits + min_symbols):
        raise ValueError("طول پسورد کمتر از مجموع حداقل‌های تعیین‌شده است!")

    password = []

    # اضافه کردن حداقل تعداد کاراکترهای هر نوع
    password += random.choices(UPPERCASE, k=min_upper)
    password += random.choices(LOWERCASE, k=min_lower)
    password += random.choices(DIGITS, k=min_digits)
    password += random.choices(SYMBOLS, k=min_symbols)

    # پر کردن باقی طول پسورد
    remaining_length = length - len(password)
    char_pool = ''
    if min_upper > 0: char_pool += UPPERCASE
    if min_lower > 0: char_pool += LOWERCASE
    if min_digits > 0: char_pool += DIGITS
    if min_symbols > 0: char_pool += SYMBOLS
    if not char_pool: char_pool = LOWERCASE + UPPERCASE + DIGITS + SYMBOLS

    password += random.choices(char_pool, k=remaining_length)
    random.shuffle(password)
    return ''.join(password)

def main():
    animate_text("✨ Welcome to the Ultimate Professional Password Generator! ✨\n")

    try:
        length = int(input("Enter password length (8-20 recommended): "))
        min_upper = int(input("Minimum uppercase letters: "))
        min_lower = int(input("Minimum lowercase letters: "))
        min_digits = int(input("Minimum digits: "))
        min_symbols = int(input("Minimum symbols: "))
        count = int(input("How many passwords to generate?: "))
        save_file = input("Save passwords to file? (y/n): ").lower() == 'y'
        if save_file:
            filename = input("Enter filename (default: passwords.txt): ")
            if not filename:
                filename = "passwords.txt"
    except ValueError:
        print(Fore.RED + "Invalid input! Please enter numbers correctly.")
        return

    animate_text("\nGenerating passwords", 0.05)
    for _ in range(5):  # انیمیشن تولید
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(0.3)
    print("\n")

    passwords = []

    for i in range(count):
        pwd = generate_password_custom(length, min_upper, min_lower, min_digits, min_symbols)
        passwords.append(pwd)

        # انیمیشن هر پسورد
        animate_text(f"[{i+1}] Password: {Fore.CYAN}{pwd}", 0.01)
        print(password_strength(pwd))

        # Progress Bar کلی
        show_progress_bar(i+1, count)
        print("\n")

        # کپی خودکار اولین پسورد
        if i == 0:
            pyperclip.copy(pwd)
            print(Fore.MAGENTA + "-> First password copied to clipboard!")

    # ذخیره در فایل
    if save_file:
        with open(filename, 'w') as f:
            for pwd in passwords:
                f.write(pwd + '\n')
        print(Fore.GREEN + f"\n✅ Passwords saved to {filename}!")

    animate_text("\n🎉 All passwords generated successfully!", 0.03)

if __name__ == "__main__":
    main()
