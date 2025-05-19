import mysql.connector
from mysql.connector import Error
import getpass
import hashlib
from datetime import datetime, timedelta
import sys
from tabulate import tabulate

class LibrarySystem:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.current_user = None
        
    def connect_to_database(self):
        """Establish database connection"""
        try:
            password = getpass.getpass("Enter MySQL password: ")
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password=password,
                autocommit=False
            )
            self.cursor = self.connection.cursor(dictionary=True)
            
            # Create database if not exists
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS library_management")
            self.cursor.execute("USE library_management")
            return True
            
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False

    def initialize_database(self):
        """Create tables and default admin account"""
        try:
            # Create users table
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                password VARCHAR(64) NOT NULL,
                role ENUM('admin', 'librarian', 'member') NOT NULL,
                status ENUM('active', 'suspended') DEFAULT 'active',
                date_joined DATE NOT NULL
            )''')

            # Create books table
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                book_id INT AUTO_INCREMENT PRIMARY KEY,
                isbn VARCHAR(20) UNIQUE,
                title VARCHAR(100) NOT NULL,
                author VARCHAR(100) NOT NULL,
                genre VARCHAR(50),
                total_copies INT NOT NULL,
                available_copies INT NOT NULL,
                date_added DATE NOT NULL
            )''')

            # Create loans table
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS loans (
                loan_id INT AUTO_INCREMENT PRIMARY KEY,
                book_id INT NOT NULL,
                user_id INT NOT NULL,
                checkout_date DATE NOT NULL,
                due_date DATE NOT NULL,
                return_date DATE,
                status ENUM('checked_out', 'returned', 'overdue') DEFAULT 'checked_out',
                FOREIGN KEY (book_id) REFERENCES books(book_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )''')

            # Create default admin if no users exist
            self.cursor.execute("SELECT COUNT(*) FROM users")
            if self.cursor.fetchone()['COUNT(*)'] == 0:
                hashed_pass = hashlib.sha256("admin123".encode()).hexdigest()
                self.cursor.execute('''INSERT INTO users 
                    (username, full_name, password, role, date_joined)
                    VALUES (%s, %s, %s, %s, CURDATE())''',
                    ('admin', 'Administrator', hashed_pass, 'admin'))
                self.connection.commit()
                print("\nDefault admin account created:")
                print("Username: admin")
                print("Password: admin123")
                
            return True
            
        except Error as e:
            print(f"Error initializing database: {e}")
            self.connection.rollback()
            return False

    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self):
        """User login system"""
        print("\n=== Login ===")
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        
        try:
            self.cursor.execute('''SELECT * FROM users 
                               WHERE username = %s''', (username,))
            user = self.cursor.fetchone()
            
            if user and user['password'] == self.hash_password(password):
                if user['status'] == 'active':
                    self.current_user = user
                    print(f"\nWelcome, {user['full_name']}!")
                    return True
                print("Account is suspended!")
            else:
                print("Invalid credentials!")
        except Error as e:
            print(f"Login error: {e}")
            
        return False

    def admin_menu(self):
        """Admin dashboard"""
        while True:
            print("\n=== Admin Dashboard ===")
            print("1. Manage Users")
            print("2. Manage Books")
            print("3. View Reports")
            print("4. Change Password")
            print("0. Logout")
            
            choice = input("Enter choice: ")
            
            if choice == "1":
                self.manage_users()
            elif choice == "2":
                self.manage_books()
            elif choice == "3":
                self.view_reports()
            elif choice == "4":
                self.change_password()
            elif choice == "0":
                self.current_user = None
                break
            else:
                print("Invalid choice!")

    def manage_users(self):
        """User management"""
        while True:
            print("\n=== User Management ===")
            print("1. Add User")
            print("2. View Users")
            print("3. Update User")
            print("4. Suspend User")
            print("0. Back")
            
            choice = input("Enter choice: ")
            
            if choice == "1":
                self.add_user()
            elif choice == "2":
                self.view_users()
            elif choice == "3":
                self.update_user()
            elif choice == "4":
                self.suspend_user()
            elif choice == "0":
                break
            else:
                print("Invalid choice!")

    def add_user(self):
        """Add new user"""
        print("\n=== Add New User ===")
        username = input("Username: ")
        full_name = input("Full name: ")
        
        while True:
            role = input("Role (admin/librarian/member): ").lower()
            if role in ['admin', 'librarian', 'member']:
                break
            print("Invalid role!")
            
        password = getpass.getpass("Password: ")
        confirm = getpass.getpass("Confirm password: ")
        
        if password != confirm:
            print("Passwords don't match!")
            return
            
        try:
            hashed_pass = self.hash_password(password)
            self.cursor.execute('''INSERT INTO users 
                (username, full_name, password, role, date_joined)
                VALUES (%s, %s, %s, %s, CURDATE())''',
                (username, full_name, hashed_pass, role))
            self.connection.commit()
            print("User added successfully!")
        except Error as e:
            print(f"Error adding user: {e}")
            self.connection.rollback()

    def view_users(self):
        """View all users"""
        try:
            self.cursor.execute("SELECT user_id, username, full_name, role, status FROM users")
            users = self.cursor.fetchall()
            
            if users:
                print("\n=== Users ===")
                print(tabulate(users, headers="keys", tablefmt="grid"))
            else:
                print("No users found!")
        except Error as e:
            print(f"Error fetching users: {e}")

    def update_user(self):
        """Update user information"""
        print("\n=== Update User ===")
        user_id = input("Enter user ID to update: ")
        
        try:
            self.cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            user = self.cursor.fetchone()
            
            if not user:
                print("User not found!")
                return
                
            print("\nCurrent user information:")
            print(tabulate([user], headers="keys", tablefmt="grid"))
            
            print("\nSelect field to update:")
            print("1. Full Name")
            print("2. Role")
            print("3. Status")
            choice = input("Enter choice: ")
            
            if choice == "1":
                new_value = input("Enter new full name: ")
                field = "full_name"
            elif choice == "2":
                new_value = input("Enter new role (admin/librarian/member): ")
                field = "role"
            elif choice == "3":
                new_value = input("Enter new status (active/suspended): ")
                field = "status"
            else:
                print("Invalid choice!")
                return
                
            self.cursor.execute(f"UPDATE users SET {field} = %s WHERE user_id = %s", 
                               (new_value, user_id))
            self.connection.commit()
            print("User updated successfully!")
            
        except Error as e:
            print(f"Error updating user: {e}")
            self.connection.rollback()

    def suspend_user(self):
        """Suspend a user account"""
        print("\n=== Suspend User ===")
        user_id = input("Enter user ID to suspend: ")
        
        try:
            # Check if user exists
            self.cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            user = self.cursor.fetchone()
            
            if not user:
                print("User not found!")
                return
                
            if user['status'] == 'suspended':
                print("User is already suspended!")
                return
                
            # Check for active loans
            self.cursor.execute('''SELECT COUNT(*) FROM loans 
                               WHERE user_id = %s AND status = 'checked_out' ''', 
                               (user_id,))
            active_loans = self.cursor.fetchone()['COUNT(*)']
            
            if active_loans > 0:
                print(f"Cannot suspend user with {active_loans} active loans!")
                return
                
            confirm = input(f"Suspend user {user['username']}? (y/n): ").lower()
            if confirm == 'y':
                self.cursor.execute("UPDATE users SET status = 'suspended' WHERE user_id = %s", 
                                  (user_id,))
                self.connection.commit()
                print("User suspended successfully!")
                
        except Error as e:
            print(f"Error suspending user: {e}")
            self.connection.rollback()

    def manage_books(self):
        """Book management"""
        while True:
            print("\n=== Book Management ===")
            print("1. Add Book")
            print("2. View Books")
            print("3. Update Book")
            print("4. Remove Book")
            print("0. Back")
            
            choice = input("Enter choice: ")
            
            if choice == "1":
                self.add_book()
            elif choice == "2":
                self.view_books()
            elif choice == "3":
                self.update_book()
            elif choice == "4":
                self.remove_book()
            elif choice == "0":
                break
            else:
                print("Invalid choice!")

    def add_book(self):
        """Add new book"""
        print("\n=== Add New Book ===")
        title = input("Title: ")
        author = input("Author: ")
        isbn = input("ISBN (optional): ") or None
        genre = input("Genre (optional): ") or None
        
        try:
            copies = int(input("Number of copies: "))
            if copies < 1:
                print("Must have at least 1 copy")
                return
                
            self.cursor.execute('''INSERT INTO books 
                (title, author, isbn, genre, total_copies, available_copies, date_added)
                VALUES (%s, %s, %s, %s, %s, %s, CURDATE())''',
                (title, author, isbn, genre, copies, copies))
            self.connection.commit()
            print("Book added successfully!")
        except ValueError:
            print("Invalid number of copies!")
        except Error as e:
            print(f"Error adding book: {e}")
            self.connection.rollback()

    def view_books(self):
        """View all books"""
        try:
            self.cursor.execute('''SELECT book_id, title, author, genre, 
                               available_copies as available, total_copies as total
                               FROM books''')
            books = self.cursor.fetchall()
            
            if books:
                print("\n=== Books ===")
                print(tabulate(books, headers="keys", tablefmt="grid"))
            else:
                print("No books found!")
        except Error as e:
            print(f"Error fetching books: {e}")

    def update_book(self):
        """Update book information"""
        print("\n=== Update Book ===")
        book_id = input("Enter book ID to update: ")
        
        try:
            self.cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
            book = self.cursor.fetchone()
            
            if not book:
                print("Book not found!")
                return
                
            print("\nCurrent book information:")
            print(tabulate([book], headers="keys", tablefmt="grid"))
            
            print("\nSelect field to update:")
            print("1. Title")
            print("2. Author")
            print("3. Genre")
            print("4. Total Copies")
            choice = input("Enter choice: ")
            
            if choice == "1":
                new_value = input("Enter new title: ")
                field = "title"
            elif choice == "2":
                new_value = input("Enter new author: ")
                field = "author"
            elif choice == "3":
                new_value = input("Enter new genre: ")
                field = "genre"
            elif choice == "4":
                try:
                    new_value = int(input("Enter new total copies: "))
                    field = "total_copies"
                    
                    # Calculate difference to update available copies
                    diff = new_value - book['total_copies']
                    self.cursor.execute('''UPDATE books 
                                       SET available_copies = available_copies + %s 
                                       WHERE book_id = %s''', 
                                       (diff, book_id))
                except ValueError:
                    print("Invalid number!")
                    return
            else:
                print("Invalid choice!")
                return
                
            self.cursor.execute(f"UPDATE books SET {field} = %s WHERE book_id = %s", 
                              (new_value, book_id))
            self.connection.commit()
            print("Book updated successfully!")
            
        except Error as e:
            print(f"Error updating book: {e}")
            self.connection.rollback()

    def remove_book(self):
        """Remove a book"""
        print("\n=== Remove Book ===")
        book_id = input("Enter book ID to remove: ")
        
        try:
            # Check if book exists
            self.cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
            book = self.cursor.fetchone()
            
            if not book:
                print("Book not found!")
                return
                
            # Check if all copies are available
            if book['available_copies'] < book['total_copies']:
                print("Cannot remove book with checked out copies!")
                return
                
            confirm = input(f"Remove book '{book['title']}'? (y/n): ").lower()
            if confirm == 'y':
                self.cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
                self.connection.commit()
                print("Book removed successfully!")
                
        except Error as e:
            print(f"Error removing book: {e}")
            self.connection.rollback()

    def view_reports(self):
        """View system reports"""
        try:
            print("\n=== Reports ===")
            
            # Books report
            self.cursor.execute('''SELECT genre, COUNT(*) as titles, 
                               SUM(total_copies) as total, SUM(available_copies) as available
                               FROM books GROUP BY genre''')
            genre_report = self.cursor.fetchall()
            
            if genre_report:
                print("\nBooks by Genre:")
                print(tabulate(genre_report, headers="keys", tablefmt="grid"))
            
            # Users report
            self.cursor.execute('''SELECT role, COUNT(*) as count FROM users GROUP BY role''')
            users_report = self.cursor.fetchall()
            
            if users_report:
                print("\nUsers by Role:")
                print(tabulate(users_report, headers="keys", tablefmt="grid"))
            
            # Loans report
            self.cursor.execute('''SELECT status, COUNT(*) as count FROM loans GROUP BY status''')
            loans_report = self.cursor.fetchall()
            
            if loans_report:
                print("\nLoans by Status:")
                print(tabulate(loans_report, headers="keys", tablefmt="grid"))
                
        except Error as e:
            print(f"Error generating reports: {e}")

    def change_password(self):
        """Change password for current user"""
        print("\n=== Change Password ===")
        current = getpass.getpass("Current password: ")
        new_pass = getpass.getpass("New password: ")
        confirm = getpass.getpass("Confirm new password: ")
        
        if new_pass != confirm:
            print("Passwords don't match!")
            return
            
        # Verify current password
        if self.current_user['password'] != self.hash_password(current):
            print("Current password is incorrect!")
            return
            
        try:
            new_hash = self.hash_password(new_pass)
            self.cursor.execute('''UPDATE users SET password = %s 
                               WHERE user_id = %s''',
                               (new_hash, self.current_user['user_id']))
            self.connection.commit()
            print("Password changed successfully!")
        except Error as e:
            print(f"Error changing password: {e}")
            self.connection.rollback()

    def librarian_menu(self):
        """Librarian dashboard"""
        while True:
            print("\n=== Librarian Dashboard ===")
            print("1. Check Out Book")
            print("2. Process Return")
            print("3. View Active Loans")
            print("4. View Overdue Books")
            print("5. Change Password")
            print("0. Logout")
            
            choice = input("Enter choice: ")
            
            if choice == "1":
                self.checkout_book()
            elif choice == "2":
                self.process_return()
            elif choice == "3":
                self.view_active_loans()
            elif choice == "4":
                self.view_overdue_books()
            elif choice == "5":
                self.change_password()
            elif choice == "0":
                self.current_user = None
                break
            else:
                print("Invalid choice!")

    def checkout_book(self):
        """Check out a book to a member"""
        print("\n=== Check Out Book ===")
        book_id = input("Enter book ID: ")
        user_id = input("Enter member ID: ")
        
        try:
            # Check book availability
            self.cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
            book = self.cursor.fetchone()
            
            if not book:
                print("Book not found!")
                return
                
            if book['available_copies'] < 1:
                print("No available copies of this book!")
                return
                
            # Check member status
            self.cursor.execute('''SELECT * FROM users 
                               WHERE user_id = %s AND role = 'member' AND status = 'active' ''',
                               (user_id,))
            member = self.cursor.fetchone()
            
            if not member:
                print("Active member not found!")
                return
                
            # Check if member has reached limit
            self.cursor.execute('''SELECT COUNT(*) FROM loans 
                               WHERE user_id = %s AND status = 'checked_out' ''',
                               (user_id,))
            active_loans = self.cursor.fetchone()['COUNT(*)']
            
            if active_loans >= 5:
                print("Member has reached maximum checked out books (5)!")
                return
                
            # Create loan record
            checkout_date = datetime.now().date()
            due_date = checkout_date + timedelta(days=14)
            
            self.cursor.execute('''INSERT INTO loans 
                (book_id, user_id, checkout_date, due_date, status)
                VALUES (%s, %s, %s, %s, 'checked_out')''',
                (book_id, user_id, checkout_date, due_date))
                
            # Update book availability
            self.cursor.execute('''UPDATE books SET available_copies = available_copies - 1 
                               WHERE book_id = %s''', (book_id,))
                               
            self.connection.commit()
            print(f"Book '{book['title']}' checked out to {member['full_name']}")
            print(f"Due date: {due_date}")
            
        except Error as e:
            print(f"Error checking out book: {e}")
            self.connection.rollback()

    def process_return(self):
        """Process a book return"""
        print("\n=== Process Return ===")
        book_id = input("Enter book ID: ")
        user_id = input("Enter member ID: ")
        
        try:
            # Find active loan
            self.cursor.execute('''SELECT * FROM loans 
                               WHERE book_id = %s AND user_id = %s AND status = 'checked_out' ''',
                               (book_id, user_id))
            loan = self.cursor.fetchone()
            
            if not loan:
                print("No active loan found for this book and member!")
                return
                
            # Update loan status
            return_date = datetime.now().date()
            status = 'returned' if return_date <= loan['due_date'] else 'overdue'
            
            self.cursor.execute('''UPDATE loans 
                               SET return_date = %s, status = %s 
                               WHERE loan_id = %s''',
                               (return_date, status, loan['loan_id']))
                               
            # Update book availability
            self.cursor.execute('''UPDATE books SET available_copies = available_copies + 1 
                               WHERE book_id = %s''', (book_id,))
                               
            self.connection.commit()
            
            # Get book and member details
            self.cursor.execute("SELECT title FROM books WHERE book_id = %s", (book_id,))
            book_title = self.cursor.fetchone()['title']
            
            self.cursor.execute("SELECT full_name FROM users WHERE user_id = %s", (user_id,))
            member_name = self.cursor.fetchone()['full_name']
            
            print(f"Book '{book_title}' returned by {member_name}")
            if status == 'overdue':
                print("This book was returned overdue!")
                
        except Error as e:
            print(f"Error processing return: {e}")
            self.connection.rollback()

    def view_active_loans(self):
        """View all active loans"""
        try:
            self.cursor.execute('''SELECT l.loan_id, b.title, u.full_name, l.checkout_date, l.due_date
                               FROM loans l
                               JOIN books b ON l.book_id = b.book_id
                               JOIN users u ON l.user_id = u.user_id
                               WHERE l.status = 'checked_out'
                               ORDER BY l.due_date''')
            loans = self.cursor.fetchall()
            
            if loans:
                print("\n=== Active Loans ===")
                print(tabulate(loans, headers="keys", tablefmt="grid"))
            else:
                print("No active loans found!")
        except Error as e:
            print(f"Error fetching active loans: {e}")

    def view_overdue_books(self):
        """View all overdue books"""
        try:
            today = datetime.now().date()
            self.cursor.execute('''SELECT b.title, u.full_name, l.due_date, 
                               DATEDIFF(%s, l.due_date) as days_overdue
                               FROM loans l
                               JOIN books b ON l.book_id = b.book_id
                               JOIN users u ON l.user_id = u.user_id
                               WHERE l.status = 'checked_out' AND l.due_date < %s
                               ORDER BY days_overdue DESC''',
                               (today, today))
            overdue_books = self.cursor.fetchall()
            
            if overdue_books:
                print("\n=== Overdue Books ===")
                print(tabulate(overdue_books, headers="keys", tablefmt="grid"))
            else:
                print("No overdue books found!")
        except Error as e:
            print(f"Error fetching overdue books: {e}")

    def member_menu(self):
        """Member dashboard"""
        while True:
            print("\n=== Member Dashboard ===")
            print("1. View My Books")
            print("2. Search Books")
            print("3. Change Password")
            print("0. Logout")
            
            choice = input("Enter choice: ")
            
            if choice == "1":
                self.view_member_books()
            elif choice == "2":
                self.search_books()
            elif choice == "3":
                self.change_password()
            elif choice == "0":
                self.current_user = None
                break
            else:
                print("Invalid choice!")

    def view_member_books(self):
        """View books checked out by member"""
        try:
            self.cursor.execute('''SELECT b.title, l.checkout_date, l.due_date, 
                               DATEDIFF(l.due_date, CURDATE()) as days_remaining
                               FROM loans l
                               JOIN books b ON l.book_id = b.book_id
                               WHERE l.user_id = %s AND l.status = 'checked_out'
                               ORDER BY l.due_date''',
                               (self.current_user['user_id'],))
            books = self.cursor.fetchall()
            
            if books:
                print("\n=== My Checked Out Books ===")
                print(tabulate(books, headers="keys", tablefmt="grid"))
            else:
                print("You have no books currently checked out!")
        except Error as e:
            print(f"Error fetching your books: {e}")

    def search_books(self):
        """Search for books"""
        print("\n=== Search Books ===")
        search_term = input("Enter search term (title/author/genre): ")
        
        try:
            self.cursor.execute('''SELECT book_id, title, author, genre, available_copies
                               FROM books
                               WHERE title LIKE %s OR author LIKE %s OR genre LIKE %s''',
                               (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            books = self.cursor.fetchall()
            
            if books:
                print("\n=== Search Results ===")
                print(tabulate(books, headers="keys", tablefmt="grid"))
            else:
                print("No books found matching your search!")
        except Error as e:
            print(f"Error searching books: {e}")

    def run(self):
        """Main program loop"""
        if not self.connect_to_database():
            sys.exit(1)
            
        if not self.initialize_database():
            sys.exit(1)
            
        try:
            while True:
                print("\n=== Library Management System ===")
                print("1. Login")
                print("2. Exit")
                
                choice = input("Enter choice: ")
                
                if choice == "1":
                    if self.login():
                        if self.current_user['role'] == 'admin':
                            self.admin_menu()
                        elif self.current_user['role'] == 'librarian':
                            self.librarian_menu()
                        elif self.current_user['role'] == 'member':
                            self.member_menu()
                elif choice == "2":
                    print("Goodbye!")
                    break
                else:
                    print("Invalid choice!")
                    
        finally:
            if self.connection:
                self.cursor.close()
                self.connection.close()

if __name__ == "__main__":
    system = LibrarySystem()
    system.run()