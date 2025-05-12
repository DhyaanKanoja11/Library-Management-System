import mysql.connector
import tabulate
# Connect to the database
passwd=input('Enter MySQL Password: ')
mydb=mysql.connector.connect(host='localhost', user='root', password=passwd)
mycursor=mydb.cursor()

# Create database if not exists
mycursor.execute("CREATE DATABASE IF NOT EXISTS library_management")
mycursor.execute("USE library_management")

#create table(passwords) if not exist
mycursor.execute('''CREATE TABLE IF NOT EXISTS passwords(
    acc_type char(20) PRIMARY KEY,
    name char(20),
    pass varchar(20))''')

# Insert initial passwords if table is empty
mycursor.execute("SELECT COUNT(*) FROM passwords")
if mycursor.fetchone()[0]==0:
    mycursor.execute("INSERT INTO passwords (acc_type, name, pass) VALUES ('admin', 'Administrator', 'adminpass')")
    mycursor.execute("INSERT INTO passwords (acc_type, name, pass) VALUES ('librarian', 'Librarian', 'librarianpass')")
    mydb.commit()

#Create table(members) if not exist
mycursor.execute('''CREATE TABLE IF NOT EXISTS members(
mem_id int auto_increment primary key,
mem_name char(50),
date_joined date,
contact_no varchar(20),
password varchar(20))''')

#create table(books) if not exists
mycursor.execute('''CREATE TABLE IF NOT EXISTS books(
book_id int auto_increment primary key,
ISBN varchar(20),
book_name varchar(50),
author char(50),
quantity int(20))''')

#Create table(books issued) if not exist
mycursor.execute('''CREATE TABLE IF NOT EXISTS issued_books(
                book_id int(100),
                mem_id int(100), 
                issue_date date)''')

# Function to change password
def change_password(user_type):
    current_password=input("Enter your current password: ")

    # Fetch the current password from the database
    mycursor.execute(f"SELECT pass FROM passwords WHERE acc_type='{user_type}'")
    result=mycursor.fetchone()

    if result and current_password==result[0]:
        new_password=input("Enter your new password: ")
        mycursor.execute(f"UPDATE passwords SET pass='{new_password}' WHERE acc_type='{user_type}'")
        mydb.commit()
        print(f"\n{user_type.capitalize()}'s password changed successfully.")
    else:
        print("Current password is incorrect!")

# Admin Functions

#Add Member
def add_member(mem_name, date_joined, contact_no,password):
    if date_joined=="0":
        sql=(f"INSERT INTO members (mem_name, date_joined, contact_no, password) VALUES ('{mem_name}', CURDATE(), '{contact_no}', '{password}')")
    else:
        sql=(f"INSERT INTO members (mem_name, date_joined, contact_no, password) VALUES ('{mem_name}', '{date_joined}', '{contact_no}', '{password}')")
    mycursor.execute(sql)
    mydb.commit()
    print(f"\nMember '{mem_name}' added successfully.")
    member_id=mycursor.lastrowid
    print(f"Member ID number is '{member_id}'")

#View Members
def view_members():
    sql=("SELECT * FROM members")
    mycursor.execute(sql)
    result = mycursor.fetchall()

    headers = ["ID", "Name", "Date Joined", "Contact No", "Password"]

    print("\nMembers List:")
    print(tabulate.tabulate(result, headers=headers, tablefmt="grid"))

#Remove Member
def remove_member(mem_id):
    sql=(f"DELETE FROM members WHERE mem_id='{mem_id}'")
    mycursor.execute(sql)
    mydb.commit()
    print(f"\nMember with ID {mem_id} removed.")

#Add Book
def add_book(ISBN,book_name, author, quantity):
    sql=(f"INSERT INTO books (ISBN, book_name, author, quantity) VALUES ('{ISBN}', '{book_name}', '{author}', {quantity})")
    mycursor.execute(sql)
    mydb.commit()
    book_id=mycursor.lastrowid
    print(f"\nBook '{book_name}'  added successfully.")
    print(f"Book ID '{book_id}' assigned to '{book_name}'")

#View Books
def view_books():
    sql=("SELECT * FROM books")
    mycursor.execute(sql)
    result = mycursor.fetchall()

    headers = ["ID", "ISBN", "Name", "Author", "Quantity"]

    print("\nBooks List:")
    print(tabulate.tabulate(result, headers=headers, tablefmt="grid"))

#Remove Book
def remove_book(book_id):
    sql=(f"DELETE FROM books WHERE book_id='{book_id}'")
    mycursor.execute(sql)
    mydb.commit()
    print(f"\nBook with ID {book_id} removed.")

#update the quantity of a book
def update_book_quantity(book_id):
    # Fetch the current quantity from the database
    mycursor.execute(f"SELECT quantity FROM books WHERE book_id='{book_id}'")
    result=mycursor.fetchone()

    if result:
        current_quantity=result[0]
        print(f"Current quantity of book with ID {book_id}: {current_quantity}")
        new_quantity=int(input("Enter new quantity: "))

        # Update the quantity in the database
        sql=(f"UPDATE books SET quantity={new_quantity} WHERE book_id='{book_id}'")
        mycursor.execute(sql)
        mydb.commit()
        print(f"\nQuantity of book with ID {book_id} updated to {new_quantity}.")
    else:
        print("Book ID not found!")

# view Department passwords
def department_pass():
    sql=("SELECT * FROM passwords")
    mycursor.execute(sql)
    result = mycursor.fetchall()

    headers = ["Acount Type", "Name", "Password"]

    print("\nDepartment Passwords")
    print(tabulate.tabulate(result, headers=headers, tablefmt="grid"))

# Admin Menu
def admin_menu():
    while True:
        print("\nA d m i n    M e n u ")
        print("1. Add Member")
        print("2. View Members")
        print("3. Remove Member")
        print("4. Add Book")
        print("5. View Books")
        print("6. Update Book Quantity")
        print("7. Remove Book")
        print("8. Change Password")
        print("9. View Department Passwords" )
        print("0. Exit")
        choice=input("Enter your choice: ")

        if choice=="1":
            mem_name=input("Enter member name (Enter 0 to Exit): ")
            if mem_name =="0":
                continue
            else:
                date_joined=input("Enter date joined (YYYY-MM-DD) (Enter '0' to use Current date) : ")
                contact_no=str(input("Enter contact number: "))
                password=str(input("Enter the password: "))
                add_member(mem_name, date_joined, contact_no,password)

        elif choice=="2":
            view_members()

        elif choice=="3":
            mem_id=int(input("Enter member ID to remove (Enter 0 to Exit): "))
            if mem_id==0:
                continue
            else:
                remove_member(mem_id)

        elif choice=="4":
            book_name=input("Enter book name (Enter 0 to Exit) : ")
            if book_name=="0":
                continue
            else:
                author=input("Enter author: ")
                quantity=int(input("Enter quantity: "))
                ISBN=input("Enter ISBN number: ")
                add_book(ISBN,book_name, author, quantity)

        elif choice=="5":
            view_books()

        elif choice=="6":
            book_id=int(input("Enter book ID to Update Quantity (Enter 0 to Exit) : "))
            if book_id==0:
                continue
            else:
                update_book_quantity(book_id)

        elif choice=="7":
            book_id=int(input("Enter book ID to remove (Enter 0 to Exit) : "))
            if book_id==0:
                continue
            else:   
                remove_book(book_id)

        elif choice=="8":
            change_password("admin")

        elif choice=="9":
            department_pass()

        elif choice=="0":
            print("\nExiting Admin Menu.")
            break

        else:
            print("Invalid choice! Please try again.")

# Librarian Functions

# 1. Issue Book
def issue_book(book_id, mem_id):
    # Check if the book exists
    mycursor.execute(f"SELECT * FROM books WHERE book_id='{book_id}'")
    book=mycursor.fetchone()

    if book:
        # Check if the book has already been issued to the member
        mycursor.execute(f"SELECT * FROM issued_books WHERE book_id='{book_id}' AND mem_id='{mem_id}'")
        already_issued=mycursor.fetchone()

        if already_issued:
            print("\nThis book has already been issued to this member. \nCannot issue again.")
        else:
            # Proceed to issue the book
            sql=(f"INSERT INTO issued_books (book_id, mem_id, issue_date) VALUES ('{book_id}', '{mem_id}', CURDATE())")
            mycursor.execute(sql)
            mydb.commit()

            # Update book quantity
            sql_update=(f"UPDATE books SET quantity=quantity - 1 WHERE book_id='{book_id}'")
            mycursor.execute(sql_update)
            mydb.commit()
            print(f"\nBook with ID {book_id} issued.")
    else:
        print("\nBook not found!")

# 2. Return Book
def return_book(book_id, mem_id):
    # Check if the book exists
    mycursor.execute(f"SELECT * FROM books WHERE book_id='{book_id}'")
    book=mycursor.fetchone()

    if book:
        # Check if the specific member has the book issued
        mycursor.execute(f"SELECT * FROM issued_books WHERE book_id='{book_id}' AND mem_id='{mem_id}'")
        issued_book=mycursor.fetchone()

        if issued_book:
            # Update book quantity in the books table
            mycursor.execute(f"UPDATE books SET quantity=quantity + 1 WHERE book_id='{book_id}'")
            # Delete the specific issued record
            mycursor.execute(f"DELETE FROM issued_books WHERE book_id='{book_id}' AND mem_id='{mem_id}'")
            mydb.commit()
            print("\nBook returned successfully.")
        else:
            print("\nThis book was not issued to the specified member!")
    else:
        print("\nBook not found!")

# 3. View issued books (all mem)
def issued_books_all():
    sql=("SELECT * FROM issued_books")
    mycursor.execute(sql)
    result=mycursor.fetchall()
    if result:
        print("\nIssued Books:")
        headers = ["Book ID", "Member ID", "Issue Data"]
        print(tabulate.tabulate(result, headers=headers, tablefmt="grid"))        
    else:
        print("\nNo Books Issued")

# Librarian Menu
def librarian_menu():
    while True:
        print("\nL i b r a r i a n     M e n u")
        print("1. Add Book")
        print("2. View Books")
        print("3. Update Book Quantity")
        print("4. Issue Book")
        print("5. Return Book")
        print("6. View Books Issued by Members")
        print("7. Change Password")
        print("0. Exit")
        choice=input("Enter your choice: ")

        if choice=="1":
            book_name=input("Enter book name (Enter 0 to Exit) : ")
            if book_name=="0":
                continue
            else:
                author=input("Enter author: ")
                quantity=int(input("Enter quantity: "))
                ISBN=input("Enter ISBN number: ")
                add_book(ISBN,book_name, author, quantity)

        elif choice=="2":
            view_books()

        elif choice=="3":
            book_id=int(input("Enter book ID to Update Quantity (Enter 0 to Exit) : "))
            if book_id==0:
                continue
            else:
                update_book_quantity(book_id)

        elif choice=="4":
            book_id=int(input("Enter book ID to issue (Enter 0 to Exit) : "))
            if book_id==0:
                continue
            else:
                mem_id=int(input("Enter member ID: "))
                issue_book(book_id, mem_id)

        elif choice=="5":
            book_id=int(input("Enter book ID to return (Enter 0 to Exit) : "))
            if book_id==0:
                continue
            else:
                mem_id=int(input("Enter member ID: "))                
                return_book(book_id,mem_id)
        
        elif choice=="6":
            issued_books_all()

        elif choice=="7":
            change_password("librarian")

        elif choice=="0":
            print("\nExiting Librarian Menu.")
            break

        else:
            print("Invalid choice! Please try again.")

# Member Functions

# 1. Register a new member
def register_member(mem_name, contact_no,password):    
    sql=(f"INSERT INTO members (mem_name, contact_no, password, date_joined) VALUES ('{mem_name}', '{contact_no}', '{password}', CURDATE())")
    mycursor.execute(sql)
    mydb.commit()

    member_id=mycursor.lastrowid

    print(f"\nMember '{mem_name}' registered successfully.")
    print(f"Your ID number is '{member_id}'")

# 2. View member profile
def view_member(mem_id):
    # Check if the member ID exists in the database
    sql=(f"SELECT * FROM members WHERE mem_id='{mem_id}'")
    mycursor.execute(sql)
    result=mycursor.fetchone()

    if result:
        password=input("Enter your password to view your profile: ")
        sql=(f"SELECT password FROM members WHERE mem_id='{mem_id}'")
        mycursor.execute(sql)
        password_result=mycursor.fetchone()
        # Check if the password matches
        if password_result and password==password_result[0]:
            print("\nMember Profile:")
            headers = ["ID", "Name", "Date Joined","Contact No"]
            result_alt=[[result[0],result[1],result[2],result[3]]]
            print(tabulate.tabulate(result_alt, headers=headers, tablefmt="grid"))
            view_issued_books(mem_id)
        else:
            print("\nInvalid password! Access denied!")
    else:
        print("\nMember ID not found! Please check your ID and try again.")

# 3. View issued books(individual)
def view_issued_books(mem_id):
    sql=(f"SELECT * FROM issued_books WHERE mem_id='{mem_id}'")
    mycursor.execute(sql)
    result=mycursor.fetchall()

    if result:
        print("Issued Books:")
        headers = ["Book ID", "Member ID", "Issue Date"]
        print(tabulate.tabulate(result, headers=headers, tablefmt="grid"))
    else:
        print("\nNo books issued by you.")

# 4. Function to change password for a member
def change_member_password(mem_id):
    current_password=input("Enter your current password: ")
    # Fetch the current password from the database for the member
    mycursor.execute(f"SELECT password FROM members WHERE mem_id='{mem_id}'")
    result=mycursor.fetchone()

    if result and current_password==result[0]:
        new_password=input("Enter your new password: ")
        if new_password==current_password:
            print(f"\nMember ID {mem_id}'s password not changed.")
            print("Same Password Entered!")
        else:
            mycursor.execute(f"UPDATE members SET password='{new_password}' WHERE mem_id='{mem_id}'")
            mydb.commit()
            print(f"\nMember ID {mem_id}'s password changed successfully.")
    else:
        print("\nCurrent password is incorrect!")

# Member Menu
def member_menu():
    while True:
        print("\nM e m b e r     M e n u")
        print("1. Register")
        print("2. View Profile")
        print("3. View Issued Books")
        print("4. Change Password")
        print("0. Exit")
        choice=input("Enter your choice: ")

        if choice=="1":
            mem_name=input("Enter your name (Enter 0 to Exit) : ")
            if mem_name=="0":
                continue
            else:
                contact_no=input("Enter contact number: ")
                password=input("Enter Password: ")
                register_member(mem_name,contact_no,password)

        elif choice=="2":
            mem_id=int(input("Enter your member ID (Enter 0 to Exit) : "))
            if mem_id==0:
                continue
            else:
                view_member(mem_id)

        elif choice=="3":
            mem_id=int(input("Enter your member ID (Enter 0 to Exit) : "))
            if mem_id==0:
                continue
            else:
                print("")
                view_issued_books(mem_id)

        elif choice=="4":
            mem_id=int(input("Enter your member ID: "))
            change_member_password(mem_id)

        elif choice=="0":
            print("\nExiting Member Menu.")
            break

        else:
            print("Invalid choice! Please try again.")

# Main Function to Start the Program
def main():
    while True:
        print("\nWelcome to the Library Management System")
        print("1. Admin Login")
        print("2. Librarian Login")
        print("3. Member Login")
        print("0. Exit")
        choice=input("Enter your choice: ")

        if choice=="1":
            admin_password=input("Enter admin password: ")
            mycursor.execute(f"SELECT pass FROM passwords WHERE acc_type='admin'")
            result=mycursor.fetchone()
            if result and admin_password==result[0]:
                admin_menu()
            else:
                print("Incorrect admin password!")

        elif choice=="2":
            librarian_password=input("Enter librarian password: ")
            mycursor.execute(f"SELECT pass FROM passwords WHERE acc_type='librarian'")
            result=mycursor.fetchone()
            if result and librarian_password==result[0]:
                librarian_menu()
            else:
                print("Incorrect librarian password!")

        elif choice=="3":
            member_menu()

        elif choice=="0":
            print("Exiting Library Management System")
            print("\nProgram by:")
            print("Dhyaan Dharmesh Kanoja")
            break

        else:
            print("Invalid choice! Please try again!")
# Run the program
main()
