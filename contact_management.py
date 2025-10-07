import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# ---------------------- Database Connection ----------------------
def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",        # change this
            password="Sql123@1",    # change this
            database="contact_management"
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return None


# ---------------------- Add Contact Function ----------------------
def add_contact():
    name = entry_name.get().strip()
    contact = entry_contact.get().strip()

    if name == "" or contact == "":
        messagebox.showwarning("Input Error", "Please enter both Name and Contact Number.")
        return

    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO contacts (name, contact_number) VALUES (%s, %s)", (name, contact))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Contact added successfully!")
        entry_name.delete(0, tk.END)
        entry_contact.delete(0, tk.END)


# ---------------------- Show Details Page ----------------------
def show_details_page():
    root.withdraw()  # Hide main window

    details_window = tk.Toplevel(root)
    details_window.title("Contact Details")
    details_window.geometry("700x700")
    details_window.config(bg="white")

    FONT_LABEL = ("Courier", 12)
    FONT_BUTTON = ("Courier", 12, "bold")

    # --- Pagination Setup ---
    current_page = 1
    records_per_page = 10

    # --- Search ---
    search_var = tk.StringVar()

    def load_contacts(page):
        for i in tree.get_children():
            tree.delete(i)
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM contacts")
            total_records = cursor.fetchone()[0]

            start_index = (page - 1) * records_per_page
            cursor.execute("SELECT id, name, contact_number FROM contacts ORDER BY id ASC LIMIT %s OFFSET %s",
                           (records_per_page, start_index))
            rows = cursor.fetchall()

            for row in rows:
                tree.insert("", tk.END, values=row)

            conn.close()

            total_pages = (total_records // records_per_page) + (1 if total_records % records_per_page != 0 else 0)
            lbl_page.config(text=f"Page {page} of {total_pages}")

            prev_btn["state"] = tk.NORMAL if page > 1 else tk.DISABLED
            next_btn["state"] = tk.NORMAL if page < total_pages else tk.DISABLED

    def next_page():
        nonlocal current_page
        current_page += 1
        load_contacts(current_page)

    def prev_page():
        nonlocal current_page
        if current_page > 1:
            current_page -= 1
            load_contacts(current_page)

    def search_contact():
        search_text = search_var.get().strip()
        for i in tree.get_children():
            tree.delete(i)
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            query = "SELECT id, name, contact_number FROM contacts WHERE name LIKE %s OR contact_number LIKE %s"
            cursor.execute(query, (f"%{search_text}%", f"%{search_text}%"))
            rows = cursor.fetchall()
            for row in rows:
                tree.insert("", tk.END, values=row)
            conn.close()
            lbl_page.config(text="Search Results")

    def select_contact(event):
        selected = tree.focus()
        if selected:
            values = tree.item(selected, "values")
            entry_name2.delete(0, tk.END)
            entry_contact2.delete(0, tk.END)
            entry_name2.insert(0, values[1])
            entry_contact2.insert(0, values[2])

    def update_contact():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Selection Error", "Select a contact to update.")
            return
        values = tree.item(selected, "values")
        contact_id = values[0]
        name = entry_name2.get().strip()
        contact = entry_contact2.get().strip()
        if name == "" or contact == "":
            messagebox.showwarning("Input Error", "Please fill both fields.")
            return
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE contacts SET name=%s, contact_number=%s WHERE id=%s", (name, contact, contact_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Updated", "Contact updated successfully!")
            load_contacts(current_page)

    def delete_contact():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Selection Error", "Select a contact to delete.")
            return
        values = tree.item(selected, "values")
        contact_id = values[0]
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this contact?")
        if confirm:
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM contacts WHERE id=%s", (contact_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Deleted", "Contact deleted successfully!")
                load_contacts(current_page)

    def go_back():
        details_window.destroy()
        root.deiconify()  # Show main window again

    # --- Title ---
    tk.Label(details_window, text="📖 CONTACT DETAILS", font=("Courier", 18, "bold"), bg="white", fg="black").pack(pady=10)

    # --- Table ---
    tree_frame = tk.Frame(details_window, bg="white", highlightbackground="black", highlightthickness=1)
    tree_frame.pack(pady=10)
    columns = ("ID", "Name", "Contact Number")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
    style = ttk.Style()
    style.configure("Treeview", font=("Courier", 11), foreground="black", background="white", fieldbackground="white")
    style.configure("Treeview.Heading", font=("Courier", 12, "bold"), foreground="black", background="white")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=200, anchor="center")
    tree.pack()
    tree.bind("<ButtonRelease-1>", select_contact)

    # --- Edit Fields ---
    edit_frame = tk.Frame(details_window, bg="white")
    edit_frame.pack(pady=10)
    tk.Label(edit_frame, text="Name:", font=FONT_LABEL, bg="white").grid(row=0, column=0, padx=5, pady=5)
    entry_name2 = tk.Entry(edit_frame, width=25, font=FONT_LABEL, relief="solid", bd=1)
    entry_name2.grid(row=0, column=1, padx=5, pady=5)
    tk.Label(edit_frame, text="Contact:", font=FONT_LABEL, bg="white").grid(row=1, column=0, padx=5, pady=5)
    entry_contact2 = tk.Entry(edit_frame, width=25, font=FONT_LABEL, relief="solid", bd=1)
    entry_contact2.grid(row=1, column=1, padx=5, pady=5)

    # --- Buttons ---
    btn_frame = tk.Frame(details_window, bg="white")
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="UPDATE", command=update_contact, font=FONT_BUTTON, bg="white", relief="solid").grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="DELETE", command=delete_contact, font=FONT_BUTTON, bg="white", relief="solid").grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="BACK", command=go_back, font=FONT_BUTTON, bg="white", relief="solid").grid(row=0, column=2, padx=5)

    # --- Search ---
    search_frame = tk.Frame(details_window, bg="white")
    search_frame.pack(pady=10)
    tk.Label(search_frame, text="Search:", font=FONT_LABEL, bg="white").grid(row=0, column=0)
    tk.Entry(search_frame, textvariable=search_var, font=FONT_LABEL, width=25, relief="solid", bd=1).grid(row=0, column=1, padx=5)
    tk.Button(search_frame, text="GO", command=search_contact, font=FONT_BUTTON, bg="white", relief="solid").grid(row=0, column=2, padx=5)

    # --- Pagination ---
    pagination_frame = tk.Frame(details_window, bg="white")
    pagination_frame.pack(pady=10)
    prev_btn = tk.Button(pagination_frame, text="⬅ Prev", command=prev_page, font=FONT_BUTTON, bg="white", relief="solid")
    prev_btn.grid(row=0, column=0, padx=5)
    lbl_page = tk.Label(pagination_frame, text="", font=FONT_LABEL, bg="white")
    lbl_page.grid(row=0, column=1, padx=5)
    next_btn = tk.Button(pagination_frame, text="Next ➡", command=next_page, font=FONT_BUTTON, bg="white", relief="solid")
    next_btn.grid(row=0, column=2, padx=5)

    load_contacts(current_page)


# ---------------------- Main Window ----------------------
root = tk.Tk()
root.title("Contact Management (Main Page)")
root.geometry("600x400")
root.config(bg="white")

FONT_LABEL = ("Courier", 12)
FONT_BUTTON = ("Courier", 12, "bold")

tk.Label(root, text="📇 CONTACT MANAGEMENT SYSTEM", font=("Courier", 18, "bold"), bg="white", fg="black").pack(pady=20)

frame = tk.Frame(root, bg="white")
frame.pack(pady=10)

tk.Label(frame, text="Name:", font=FONT_LABEL, bg="white").grid(row=0, column=0, padx=10, pady=5)
entry_name = tk.Entry(frame, width=30, font=FONT_LABEL, relief="solid", bd=1)
entry_name.grid(row=0, column=1, pady=5)

tk.Label(frame, text="Contact Number:", font=FONT_LABEL, bg="white").grid(row=1, column=0, padx=10, pady=5)
entry_contact = tk.Entry(frame, width=30, font=FONT_LABEL, relief="solid", bd=1)
entry_contact.grid(row=1, column=1, pady=5)

tk.Button(root, text="ADD CONTACT", command=add_contact, font=FONT_BUTTON, bg="white", relief="solid").pack(pady=10)
tk.Button(root, text="SHOW DETAILS", command=show_details_page, font=FONT_BUTTON, bg="white", relief="solid").pack(pady=5)

root.mainloop()
