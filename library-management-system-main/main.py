import os
import time
from db import get_connection

# ANSI escape sequences for colors
class Colors:
    HEADER = '\033[95m'    # Purple
    OKBLUE = '\033[94m'    # Blue
    OKCYAN = '\033[96m'    # Cyan
    OKGREEN = '\033[92m'   # Green
    WARNING = '\033[93m'   # Yellow
    FAIL = '\033[91m'      # Red
    ENDC = '\033[0m'       # Reset
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# --- User & Role Management ---
def create_admin():
    print(f'{Colors.HEADER}=== Create First Admin User ==={Colors.ENDC}')
    uid = input('Admin User ID: ').strip()
    name = input('Admin Name: ').strip()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (uid, name, role) VALUES (%s, %s, 'admin')", (uid, name))
    conn.commit()
    cursor.close()
    conn.close()
    print(f'{Colors.OKGREEN}Admin created. Please restart.{Colors.ENDC}')
    exit()

def login():
    print(f"\n{Colors.HEADER}📚==========================================")
    print("   Welcome to BUBT Library Management System")
    print("============================================📚" + Colors.ENDC + "\n")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT uid, name, role FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    if not users:
        create_admin()

    attempts = 0
    max_attempts = 5
    while attempts < max_attempts:
        uid = input(f"{Colors.OKBLUE}Enter your User ID to login (or type 'exit' to quit): {Colors.ENDC}").strip()
        if uid.lower() == 'exit':
            print(f"{Colors.WARNING}👋 Exiting login.{Colors.ENDC}")
            exit()

        matched_user = next((u for u in users if u['uid'] == uid), None)
        if matched_user:
            print(f"\n{Colors.OKCYAN}Checking credentials", end='', flush=True)
            for _ in range(3):
                print('.', end='', flush=True)
                time.sleep(0.5)
            print(f"{Colors.ENDC}\n")
            clear_screen()
            print(f"{Colors.OKGREEN}✅ Successfully logged in as: {Colors.BOLD}{matched_user['name']} ({matched_user['role'].capitalize()}){Colors.ENDC}\n")
            return matched_user['uid'], matched_user['role']

        else:
            attempts += 1
            print(f"{Colors.FAIL}❌ User ID not found. Try again. ({max_attempts - attempts} attempts left){Colors.ENDC}\n")

    print(f"{Colors.WARNING}⚠️ Too many failed attempts. Exiting...{Colors.ENDC}")
    exit()

# --- Book Management ---
def add_book():
    print(f"{Colors.HEADER}=== Add New Book ==={Colors.ENDC}")
    isbn = input('ISBN: ').strip()
    title = input('Title: ').strip()
    author = input('Author: ').strip()
    try:
        copies = int(input('Copies: ').strip())
    except ValueError:
        print(f"{Colors.FAIL}Invalid number for copies.{Colors.ENDC}\n")
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (isbn, title, author, copies) VALUES (%s, %s, %s, %s)",
                   (isbn, title, author, copies))
    conn.commit()
    cursor.close()
    conn.close()
    print(f'{Colors.OKGREEN}✅ Book added successfully.{Colors.ENDC}\n')

def list_books():
    print(f"{Colors.HEADER}=== Book List ==={Colors.ENDC}")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    cursor.close()
    conn.close()

    if not books:
        print(f"{Colors.WARNING}No books found.{Colors.ENDC}\n")
        return

    print(f"{Colors.BOLD}{'ISBN':<15}{'Title':<30}{'Author':<25}{'Copies':<6}{Colors.ENDC}")
    print('-'*80)
    for b in books:
        print(f"{b['isbn']:<15}{b['title']:<30}{b['author']:<25}{b['copies']:<6}")
    print()

def search_books():
    kw = input(f'{Colors.OKBLUE}Search ISBN/title/author: {Colors.ENDC}').lower().strip()
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM books WHERE LOWER(isbn) LIKE %s OR LOWER(title) LIKE %s OR LOWER(author) LIKE %s"
    like_kw = f"%{kw}%"
    cursor.execute(query, (like_kw, like_kw, like_kw))
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    if not results:
        print(f'{Colors.WARNING}No matches found.{Colors.ENDC}\n')
    else:
        print(f'{Colors.HEADER}=== Search Results ==={Colors.ENDC}')
        for b in results:
            print(f"{b['isbn']} | {b['title']} | {b['author']} | Copies: {b['copies']}")
        print()

# --- User Management ---
def add_user():
    print(f"{Colors.HEADER}=== Add New User ==={Colors.ENDC}")
    uid = input('User ID: ').strip()
    name = input('Name: ').strip()
    role = input('Role (admin/librarian/member): ').strip().lower()
    if role not in ('admin', 'librarian', 'member'):
        print(f"{Colors.FAIL}Invalid role.{Colors.ENDC}\n")
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (uid, name, role) VALUES (%s, %s, %s)", (uid, name, role))
    conn.commit()
    cursor.close()
    conn.close()
    print(f'{Colors.OKGREEN}✅ User added successfully.{Colors.ENDC}\n')

def list_users():
    print(f"{Colors.HEADER}=== User List ==={Colors.ENDC}")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    if not users:
        print(f"{Colors.WARNING}No users found.{Colors.ENDC}\n")
        return

    print(f"{Colors.BOLD}{'User ID':<15}{'Name':<30}{'Role':<12}{Colors.ENDC}")
    print('-'*60)
    for u in users:
        print(f"{u['uid']:<15}{u['name']:<30}{u['role']:<12}")
    print()

def delete_user(current_uid):
    uid = input('User ID to delete: ').strip()
    if uid == current_uid:
        print(f"{Colors.FAIL}❌ You cannot delete yourself while logged in.{Colors.ENDC}\n")
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE uid = %s", (uid,))
    conn.commit()
    if cursor.rowcount:
        print(f'{Colors.OKGREEN}✅ User deleted successfully.{Colors.ENDC}\n')
    else:
        print(f'{Colors.WARNING}User not found.{Colors.ENDC}\n')
    cursor.close()
    conn.close()

# --- Borrow & Return ---
from datetime import date

def borrow_book():
    print("=== Borrow Book ===")
    uid = input('Your User ID: ').strip()
    isbn = input('Book ISBN: ').strip()
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE uid = %s", (uid,))
    if not cursor.fetchone():
        print('❌ Invalid user.\n')
        cursor.close()
        conn.close()
        return

    cursor.execute("SELECT copies FROM books WHERE isbn = %s", (isbn,))
    row = cursor.fetchone()
    if row and row['copies'] > 0:
        cursor.execute("UPDATE books SET copies = copies - 1 WHERE isbn = %s", (isbn,))
        today = date.today()
        cursor.execute(
            "INSERT INTO transactions (action, uid, isbn, borrow_date) VALUES ('borrow', %s, %s, %s)",
            (uid, isbn, today)
        )
        conn.commit()
        print('✅ Book borrowed.\n')
    elif row:
        print('❌ No copies left.\n')
    else:
        print('❌ ISBN not found.\n')

    cursor.close()
    conn.close()

from datetime import date

def return_book():
    print("=== Return Book ===")
    uid = input('Your User ID: ').strip()
    isbn = input('Book ISBN: ').strip()
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, borrow_date FROM transactions WHERE action = 'borrow' AND uid = %s AND isbn = %s AND return_date IS NULL LIMIT 1",
        (uid, isbn)
    )
    row = cursor.fetchone()
    if row:
        trans_id = row['id']
        borrow_date = row['borrow_date']
        today = date.today()
        days_borrowed = (today - borrow_date).days
        fine = 0
        if days_borrowed > 7:
            fine = (days_borrowed - 7) * 5  # $5 fine per day late

        # Update transaction with return_date and fine
        cursor.execute(
            "UPDATE transactions SET return_date = %s, fine = %s WHERE id = %s",
            (today, fine, trans_id)
        )
        cursor.execute("UPDATE books SET copies = copies + 1 WHERE isbn = %s", (isbn,))
        conn.commit()

        if fine > 0:
            print(f"⚠️ Book returned late! You have a fine of ${fine}.\n")
        else:
            print('✅ Book returned on time. Thank you!\n')
    else:
        print('❌ No matching borrow record found or book already returned.\n')

    cursor.close()
    conn.close()

# --- Main Menu ---
def main():
    clear_screen()
    current_uid, role = login()

    while True:
        print(f"{Colors.HEADER}{'=' * 40}{Colors.ENDC}")
        print(f"{Colors.BOLD}{'Library Management System':^40}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'=' * 40}{Colors.ENDC}")
        print(f"Logged in as: {Colors.OKGREEN}{current_uid}{Colors.ENDC} ({Colors.OKBLUE}{str(role).capitalize()}{Colors.ENDC})\n")
        print("1) 📚 Book Management")
        print("2) 👥 User Management")
        print("3) 🔁 Borrow & Return")
        print("4) ❌ Exit")
        print(f"{Colors.HEADER}{'-' * 40}{Colors.ENDC}")
        choice = input(f"{Colors.OKBLUE}Choose an option (1-4): {Colors.ENDC}").strip()
        clear_screen()

        if choice == '1':
            if role not in ('admin', 'librarian'):
                print(f"{Colors.FAIL}🚫 Access denied.{Colors.ENDC}\n")
                continue
            print(f"a) ➕ Add Book\nb) 📄 List Books\nc) 🔍 Search Books")
            sub = input(f"{Colors.OKBLUE}Choose (a-c): {Colors.ENDC}").strip().lower(); print()
            if sub == 'a': add_book()
            elif sub == 'b': list_books()
            elif sub == 'c': search_books()
            else: print(f"{Colors.WARNING}⚠️ Invalid choice.{Colors.ENDC}\n")

        elif choice == '2':
            if role != 'admin':
                print(f"{Colors.FAIL}🚫 Access denied.{Colors.ENDC}\n")
                continue
            print(f"a) ➕ Add User\nb) 📄 List Users\nc) ❌ Delete User")
            sub = input(f"{Colors.OKBLUE}Choose (a-c): {Colors.ENDC}").strip().lower(); print()
            if sub == 'a': add_user()
            elif sub == 'b': list_users()
            elif sub == 'c': delete_user(current_uid)
            else: print(f"{Colors.WARNING}⚠️ Invalid choice.{Colors.ENDC}\n")

        elif choice == '3':
            print(f"a) 📗 Borrow Book\nb) 📘 Return Book")
            sub = input(f"{Colors.OKBLUE}Choose (a-b): {Colors.ENDC}").strip().lower(); print()
            if sub == 'a': borrow_book()
            elif sub == 'b': return_book()
            else: print(f"{Colors.WARNING}⚠️ Invalid choice.{Colors.ENDC}\n")

        elif choice == '4':
            print(f"{Colors.WARNING}👋 Goodbye!{Colors.ENDC}")
            break

        else:
            print(f"{Colors.WARNING}⚠️ Invalid input. Please choose 1-4.{Colors.ENDC}\n")

if __name__ == '__main__':
    main()
