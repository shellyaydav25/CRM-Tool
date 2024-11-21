import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Database setup
conn = sqlite3.connect("crm.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    phone TEXT,
    address TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    note TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
)
""")
conn.commit()

# Application setup
root = tk.Tk()
root.title("CRM Tool")
root.geometry("900x600")

# Functions
def refresh_customers():
    cursor.execute("SELECT * FROM customers")
    rows = cursor.fetchall()
    for item in tree.get_children():
        tree.delete(item)
    for row in rows:
        tree.insert("", "end", values=row)

def add_customer():
    cursor.execute("INSERT INTO customers (name, email, phone, address) VALUES (?, ?, ?, ?)", 
                   (name_var.get(), email_var.get(), phone_var.get(), address_var.get()))
    conn.commit()
    refresh_customers()

def update_customer():
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item[0])
        customer_id = item['values'][0]
        cursor.execute("UPDATE customers SET name=?, email=?, phone=?, address=? WHERE id=?", 
                       (name_var.get(), email_var.get(), phone_var.get(), address_var.get(), customer_id))
        conn.commit()
        refresh_customers()

def delete_customer():
    selected_item = tree.selection()
    if selected_item:
        customer_id = tree.item(selected_item[0])['values'][0]
        cursor.execute("DELETE FROM customers WHERE id=?", (customer_id,))
        conn.commit()
        refresh_customers()

def search_customers():
    query = search_var.get()
    cursor.execute("SELECT * FROM customers WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?", 
                   (f"%{query}%", f"%{query}%", f"%{query}%"))
    rows = cursor.fetchall()
    for item in tree.get_children():
        tree.delete(item)
    for row in rows:
        tree.insert("", "end", values=row)

def add_interaction():
    selected_item = tree.selection()
    if selected_item:
        customer_id = tree.item(selected_item[0])['values'][0]
        cursor.execute("INSERT INTO interactions (customer_id, note) VALUES (?, ?)", 
                       (customer_id, interaction_var.get()))
        conn.commit()

def view_interactions():
    selected_item = tree.selection()
    if selected_item:
        customer_id = tree.item(selected_item[0])['values'][0]
        cursor.execute("SELECT note FROM interactions WHERE customer_id=?", (customer_id,))
        notes = cursor.fetchall()
        interaction_list.delete(0, tk.END)
        for note in notes:
            interaction_list.insert(tk.END, note[0])

def export_data():
    file = filedialog.asksaveasfilename(defaultextension=".csv")
    if file:
        cursor.execute("SELECT * FROM customers")
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["ID", "Name", "Email", "Phone", "Address"])
        df.to_csv(file, index=False)

def import_data():
    file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file:
        df = pd.read_csv(file)
        for _, row in df.iterrows():
            cursor.execute("INSERT INTO customers (name, email, phone, address) VALUES (?, ?, ?, ?)", 
                           (row["Name"], row["Email"], row["Phone"], row["Address"]))
        conn.commit()
        refresh_customers()

def show_dashboard():
    cursor.execute("SELECT COUNT(*) FROM customers")
    total_customers = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM interactions")
    total_interactions = cursor.fetchone()[0]

    fig, ax = plt.subplots(figsize=(5, 4))
    labels = ["Customers", "Interactions"]
    values = [total_customers, total_interactions]
    ax.bar(labels, values)
    ax.set_title("CRM Metrics")

    canvas = FigureCanvasTkAgg(fig, root)
    canvas.get_tk_widget().pack()
    canvas.draw()

# UI Setup
frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

tree = ttk.Treeview(frame, columns=("ID", "Name", "Email", "Phone", "Address"), show="headings")
for col in ("ID", "Name", "Email", "Phone", "Address"):
    tree.heading(col, text=col)
    tree.column(col, width=100)
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

form_frame = tk.Frame(root)
form_frame.pack(fill=tk.X)

name_var = tk.StringVar()
email_var = tk.StringVar()
phone_var = tk.StringVar()
address_var = tk.StringVar()
search_var = tk.StringVar()
interaction_var = tk.StringVar()

tk.Label(form_frame, text="Name").grid(row=0, column=0)
tk.Entry(form_frame, textvariable=name_var).grid(row=0, column=1)
tk.Label(form_frame, text="Email").grid(row=0, column=2)
tk.Entry(form_frame, textvariable=email_var).grid(row=0, column=3)
tk.Label(form_frame, text="Phone").grid(row=1, column=0)
tk.Entry(form_frame, textvariable=phone_var).grid(row=1, column=1)
tk.Label(form_frame, text="Address").grid(row=1, column=2)
tk.Entry(form_frame, textvariable=address_var).grid(row=1, column=3)
tk.Entry(root, textvariable=search_var).pack()
tk.Button(root, text="Search", command=search_customers).pack()

tk.Button(root, text="Add Customer", command=add_customer).pack()
tk.Button(root, text="Update Customer", command=update_customer).pack()
tk.Button(root, text="Delete Customer", command=delete_customer).pack()
tk.Button(root, text="Add Interaction", command=add_interaction).pack()
tk.Button(root, text="View Interactions", command=view_interactions).pack()
tk.Button(root, text="Export Data", command=export_data).pack()
tk.Button(root, text="Import Data", command=import_data).pack()
tk.Button(root, text="Dashboard", command=show_dashboard).pack()

interaction_list = tk.Listbox(root)
interaction_list.pack(fill=tk.BOTH, expand=True)

refresh_customers()
root.mainloop()
