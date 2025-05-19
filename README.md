# Library Management System  
**Version 2.2.0**  

A robust, role-based library management system for tracking books, members, and loans. Built with Python and MySQL, featuring enhanced security, reporting, and usability improvements over previous versions.  

---

## 🚀 **Key Features**  
- **Role-Based Access Control**  
  - **Admin**: Full system control (users, books, reports)  
  - **Librarian**: Daily operations (checkouts, returns, overdue tracking)  
  - **Member**: Self-service portal (view loans, search books)  

- **Enhanced Security**  
  - SHA-256 password hashing  
  - Input validation for emails, ISBNs, and user roles  
  - Session-based authentication  

- **Comprehensive Reporting**  
  - Circulation summaries (active loans, overdue books)  
  - Inventory analytics (books by genre, recent additions)  
  - Member activity tracking (most active users, overdue lists)  

- **Improved Database Management**  
  - Automatic database/table initialization  
  - Foreign key constraints for data integrity  
  - Indexes for faster queries  

- **User Experience**  
  - Clean CLI interface with tabulated data  
  - Intuitive menu navigation  
  - Contextual error messages  

---

## ⚙️ **Version 2.2.0 Changes (Upgrade from 2.1.0)**  

| Feature                | v2.1.0                  | v2.2.0 Improvements                                                                 |  
|------------------------|-------------------------|-------------------------------------------------------------------------------------|  
| **Architecture**       | Procedural code         | **Class-based structure** for better modularity and maintainability                |  
| **Security**           | Plaintext passwords     | **SHA-256 hashing** + improved input validation                                     |  
| **Book Management**    | Basic metadata          | **Genre, location, and publication year** tracking                                  |  
| **Loan System**        | Simple checkouts        | **Overdue tracking** with statuses (`checked_out`, `returned`, `overdue`)           |  
| **Error Handling**     | Limited                 | **Transaction rollbacks** + detailed error logging                                  |  
| **User Interface**     | Basic menus             | **Tabulated displays** + consistent headers + streamlined workflows                 |  
| **Reports**            | None                    | **6+ report types** (circulation, inventory, member activity)                       |  

---

## 🛠️ **Installation**  

### Prerequisites  
- Python 3.10+  
- MySQL Server 8.0+  
- `pip` package manager  

### Steps  
1. **Clone the Repository**  
   ```bash  
   git clone https://github.com/your-repo/library-management.git  
   cd library-management  
   ```  

2. **Install Dependencies**  
   ```bash  
   pip install mysql-connector-python tabulate  
   ```  

3. **Database Setup**  
   - MySQL will auto-create the `library_management` database on first run  
   - Default admin credentials:  
     ```  
     Username: admin  
     Password: admin123  
     ```  

4. **Run the System**  
   ```bash  
   python main.py  
   ```  

---

## 📖 **Usage Guide**  

### For Admins  
1. Manage users (add, suspend, update roles)  
2. Add/remove books, update quantities  
3. Generate reports (circulation, inventory)  

### For Librarians  
1. Check out/return books  
2. View active loans and overdue items  
3. Search books by title/author/genre  

### For Members  
1. View personal loan history  
2. Search available books  
3. Update passwords  

---

## 🛡️ **Reliability & Continuous Operation**  
- **Fault Tolerance**: Automatic transaction rollbacks on errors prevent data corruption.  
- **Persistent Connections**: Stable MySQL connection pooling ensures minimal downtime.  
- **Uninterrupted Service**: Designed for 24/7 operation with no need for frequent restarts.  

---

## 📜 **License**  
MIT License | [Full License Text](LICENSE)  

---

## 📧 **Support**  
For issues or feature requests, contact:  
- **Your Name**  
- **Email**: dhyaandk11@gmail.com 

---
