"""CS 354 Library Manager — Tkinter + MySQL CRUD application."""
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {"host": "localhost", "user": "root", "password": "", "database": "library_db", "connection_timeout": 5}

class LibraryApp:
    def __init__(self, root):
        self.root = root
        root.title("Library Manager | CS 354")
        root.geometry("1050x680")
        root.minsize(850, 580)
        self.style = ttk.Style()
        if "clam" in self.style.theme_names(): self.style.theme_use("clam")
        self.style.configure("Treeview", rowheight=28)
        self.status = tk.StringVar(value="Ready")
        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True, padx=16, pady=12)
        self.build_books()
        self.build_members()
        self.build_loans()
        ttk.Label(root, textvariable=self.status, anchor="w").pack(fill="x", padx=18, pady=(0, 10))
        self.refresh_all()

    def connect(self):
        return mysql.connector.connect(**DB_CONFIG)

    def run_query(self, query, params=(), fetch=False):
        conn = None
        cursor = None
        try:
            conn = self.connect()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            conn.commit()
            return cursor.rowcount
        except Error as exc:
            if conn is not None:
                try: conn.rollback()
                except Error: pass
            messagebox.showerror("Database error", f"Could not complete operation:\n{exc}\n\nCheck MySQL is running and schema.sql was imported.")
            self.status.set("Database operation failed")
            return None
        finally:
            if cursor is not None: cursor.close()
            if conn is not None and conn.is_connected(): conn.close()

    def frame(self, title):
        page = ttk.Frame(self.tabs, padding=14)
        self.tabs.add(page, text=title)
        return page

    def entry(self, parent, label, row, col, var):
        ttk.Label(parent, text=label).grid(row=row, column=col, sticky="w", padx=5, pady=(6, 1))
        field = ttk.Entry(parent, textvariable=var, width=31)
        field.grid(row=row+1, column=col, sticky="ew", padx=5, pady=(0, 6))
        return field

    def tree(self, parent, columns):
        holder = ttk.Frame(parent)
        holder.pack(fill="both", expand=True, pady=(12, 0))
        tree = ttk.Treeview(holder, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            tree.heading(col, text=col.replace('_', ' ').title())
            tree.column(col, width=130, anchor="w")
        scroll = ttk.Scrollbar(holder, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return tree

    def fill(self, tree, rows, columns):
        tree.delete(*tree.get_children())
        if rows is not None:
            for item in rows:
                tree.insert("", "end", values=[item.get(col, "") for col in columns])
            self.status.set(f"Loaded {len(rows)} records")

    def selected(self, tree):
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Select a row", "Please select a record from the table first.")
            return None
        return tree.item(selection[0], "values")

    def build_books(self):
        page = self.frame("Books")
        form = ttk.LabelFrame(page, text="Book details", padding=10)
        form.pack(fill="x")
        self.book_title = tk.StringVar(); self.book_author = tk.StringVar(); self.book_category = tk.StringVar()
        self.entry(form, "Title", 0, 0, self.book_title)
        self.entry(form, "Author", 0, 1, self.book_author)
        self.entry(form, "Category", 0, 2, self.book_category)
        form.columnconfigure(0, weight=1); form.columnconfigure(1, weight=1); form.columnconfigure(2, weight=1)
        actions = ttk.Frame(page); actions.pack(fill="x", pady=10)
        for label, command in [("Add", self.add_book), ("Update selected", self.update_book), ("Delete selected", self.delete_book), ("Clear", self.clear_book), ("Show all", self.refresh_books)]:
            ttk.Button(actions, text=label, command=command).pack(side="left", padx=3)
        ttk.Label(actions, text="Search:").pack(side="left", padx=(20, 4))
        self.book_search = tk.StringVar()
        ttk.Entry(actions, textvariable=self.book_search, width=22).pack(side="left")
        ttk.Button(actions, text="Find", command=self.refresh_books).pack(side="left", padx=4)
        self.book_cols = ("book_id", "title", "author", "category")
        self.book_tree = self.tree(page, self.book_cols)
        self.book_tree.bind("<<TreeviewSelect>>", self.on_book_select)

    def clear_book(self):
        for var in (self.book_title, self.book_author, self.book_category): var.set("")
        self.book_tree.selection_remove(self.book_tree.selection())

    def on_book_select(self, _event=None):
        sel = self.book_tree.selection()
        if sel:
            v = self.book_tree.item(sel[0], "values")
            self.book_title.set(v[1]); self.book_author.set(v[2]); self.book_category.set(v[3])

    def book_values(self):
        vals = (self.book_title.get().strip(), self.book_author.get().strip(), self.book_category.get().strip())
        if not all(vals): messagebox.showwarning("Missing fields", "Enter title, author and category."); return None
        return vals

    def add_book(self):
        vals = self.book_values()
        if vals and self.run_query("INSERT INTO books (title, author, category) VALUES (%s, %s, %s)", vals) is not None:
            self.refresh_books(); self.clear_book(); messagebox.showinfo("Added", "Book added successfully.")

    def update_book(self):
        row = self.selected(self.book_tree); vals = self.book_values() if row else None
        if vals and self.run_query("UPDATE books SET title=%s, author=%s, category=%s WHERE book_id=%s", (*vals, row[0])) is not None:
            self.refresh_books(); messagebox.showinfo("Updated", "Book updated successfully.")

    def delete_book(self):
        row = self.selected(self.book_tree)
        if row and messagebox.askyesno("Confirm delete", f"Permanently delete '{row[1]}'?"):
            if self.run_query("DELETE FROM books WHERE book_id=%s", (row[0],)) is not None:
                self.refresh_books(); self.clear_book(); messagebox.showinfo("Deleted", "Book deleted successfully.")

    def refresh_books(self):
        search = "%" + self.book_search.get().strip() + "%"
        rows = self.run_query("SELECT book_id, title, author, category FROM books WHERE title LIKE %s OR author LIKE %s OR category LIKE %s ORDER BY book_id", (search, search, search), fetch=True)
        self.fill(self.book_tree, rows, self.book_cols)

    def build_members(self):
        page = self.frame("Members")
        form = ttk.LabelFrame(page, text="Member details", padding=10); form.pack(fill="x")
        self.member_name = tk.StringVar(); self.member_email = tk.StringVar()
        self.entry(form, "Full name", 0, 0, self.member_name); self.entry(form, "Email", 0, 1, self.member_email)
        form.columnconfigure(0, weight=1); form.columnconfigure(1, weight=1)
        actions = ttk.Frame(page); actions.pack(fill="x", pady=10)
        for label, fn in [("Add", self.add_member), ("Update selected", self.update_member), ("Delete selected", self.delete_member), ("Clear", self.clear_member), ("Show all", self.refresh_members)]:
            ttk.Button(actions, text=label, command=fn).pack(side="left", padx=3)
        ttk.Label(actions, text="Search:").pack(side="left", padx=(20, 4))
        self.member_search = tk.StringVar()
        ttk.Entry(actions, textvariable=self.member_search, width=20).pack(side="left")
        ttk.Button(actions, text="Find", command=self.refresh_members).pack(side="left", padx=4)
        self.member_cols = ("member_id", "full_name", "email")
        self.member_tree = self.tree(page, self.member_cols)
        self.member_tree.bind("<<TreeviewSelect>>", self.on_member_select)

    def clear_member(self):
        self.member_name.set(""); self.member_email.set("")
        self.member_tree.selection_remove(self.member_tree.selection())

    def on_member_select(self, _event=None):
        sel = self.member_tree.selection()
        if sel:
            v = self.member_tree.item(sel[0], "values")
            self.member_name.set(v[1]); self.member_email.set(v[2])

    def member_values(self):
        vals = (self.member_name.get().strip(), self.member_email.get().strip())
        if not all(vals) or "@" not in vals[1]:
            messagebox.showwarning("Invalid input", "Enter a name and valid-looking email."); return None
        return vals

    def add_member(self):
        vals = self.member_values()
        if vals and self.run_query("INSERT INTO members (full_name, email) VALUES (%s, %s)", vals) is not None:
            self.refresh_members(); self.clear_member(); messagebox.showinfo("Added", "Member added successfully.")

    def update_member(self):
        row = self.selected(self.member_tree); vals = self.member_values() if row else None
        if vals and self.run_query("UPDATE members SET full_name=%s, email=%s WHERE member_id=%s", (*vals, row[0])) is not None:
            self.refresh_members(); messagebox.showinfo("Updated", "Member updated successfully.")

    def delete_member(self):
        row = self.selected(self.member_tree)
        if row and messagebox.askyesno("Confirm delete", f"Permanently delete member '{row[1]}'?"):
            if self.run_query("DELETE FROM members WHERE member_id=%s", (row[0],)) is not None:
                self.refresh_members(); self.clear_member(); messagebox.showinfo("Deleted", "Member deleted successfully.")

    def refresh_members(self):
        term = "%" + self.member_search.get().strip() + "%"
        rows = self.run_query("SELECT member_id, full_name, email FROM members WHERE full_name LIKE %s OR email LIKE %s ORDER BY member_id", (term, term), fetch=True)
        self.fill(self.member_tree, rows, self.member_cols)

    def build_loans(self):
        page = self.frame("Borrowings")
        form = ttk.LabelFrame(page, text="Record a borrowing (use IDs shown in Books and Members)", padding=10); form.pack(fill="x")
        self.loan_book = tk.StringVar(); self.loan_member = tk.StringVar()
        self.entry(form, "Book ID", 0, 0, self.loan_book); self.entry(form, "Member ID", 0, 1, self.loan_member)
        actions = ttk.Frame(page); actions.pack(fill="x", pady=10)
        for label, fn in [("Borrow book", self.add_loan), ("Mark returned", self.return_loan), ("Delete record", self.delete_loan), ("Refresh", self.refresh_loans)]:
            ttk.Button(actions, text=label, command=fn).pack(side="left", padx=4)
        self.loan_cols = ("loan_id", "book_id", "title", "member_id", "full_name", "borrowed_at", "returned_at")
        self.loan_tree = self.tree(page, self.loan_cols)

    def add_loan(self):
        try:
            book_id = int(self.loan_book.get()); member_id = int(self.loan_member.get())
            if book_id <= 0 or member_id <= 0: raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid IDs", "Enter positive numeric Book ID and Member ID."); return
        existing = self.run_query("SELECT loan_id FROM borrowings WHERE book_id=%s AND returned_at IS NULL", (book_id,), fetch=True)
        if existing is None: return
        if existing:
            messagebox.showwarning("Already borrowed", "This book has not been returned yet."); return
        if self.run_query("INSERT INTO borrowings (book_id, member_id) VALUES (%s, %s)", (book_id, member_id)) is not None:
            self.refresh_loans(); messagebox.showinfo("Borrowed", "Borrowing recorded successfully.")

    def return_loan(self):
        row = self.selected(self.loan_tree)
        if row:
            if row[6]: messagebox.showinfo("Already returned", "This borrowing is already returned."); return
            if self.run_query("UPDATE borrowings SET returned_at=CURRENT_TIMESTAMP WHERE loan_id=%s", (row[0],)) is not None:
                self.refresh_loans(); messagebox.showinfo("Returned", "Book marked as returned.")

    def delete_loan(self):
        row = self.selected(self.loan_tree)
        if row and messagebox.askyesno("Confirm delete", f"Delete borrowing record #{row[0]} permanently?"):
            if self.run_query("DELETE FROM borrowings WHERE loan_id=%s", (row[0],)) is not None:
                self.refresh_loans(); messagebox.showinfo("Deleted", "Borrowing record deleted.")

    def refresh_loans(self):
        rows = self.run_query("""SELECT b.loan_id, b.book_id, k.title, b.member_id, m.full_name,
             b.borrowed_at, b.returned_at FROM borrowings b
             JOIN books k ON k.book_id=b.book_id JOIN members m ON m.member_id=b.member_id
             ORDER BY b.loan_id DESC""", fetch=True)
        self.fill(self.loan_tree, rows, self.loan_cols)

    def refresh_all(self):
        self.refresh_books(); self.refresh_members(); self.refresh_loans()

if __name__ == "__main__":
    root = tk.Tk()
    LibraryApp(root)
    root.mainloop()
