import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3

# Conectar ao banco de dados SQLite (ou cria se não existir)
conn = sqlite3.connect("shopping_list.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS shopping_list (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    note TEXT
)''')
conn.commit()

# Função para atualizar o preço total
def update_total_price():
    cursor.execute("SELECT SUM(price) FROM shopping_list")
    total = cursor.fetchone()[0] or 0
    total_price_label.config(text=f"R$ {total:.2f}")

# Função para renderizar a tabela
def render_table():
    for row in table.get_children():
        table.delete(row)
    
    cursor.execute("SELECT * FROM shopping_list ORDER BY name ASC")
    for row in cursor.fetchall():
        table.insert("", "end", values=(row[1], f"R$ {row[2]:.2f}", row[3]))

    update_total_price()

# Função para adicionar um item
def add_item():
    name = item_name_entry.get().strip()
    try:
        price = float(item_price_entry.get())
    except ValueError:
        messagebox.showerror("Erro", "Por favor, insira um preço válido.")
        return
    
    if name:
        cursor.execute("INSERT INTO shopping_list (name, price, note) VALUES (?, ?, ?)", (name, price, ""))
        conn.commit()
        render_table()
        item_name_entry.delete(0, tk.END)
        item_price_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Erro", "Por favor, insira o nome do item.")

# Função para editar um item
def edit_item():
    selected = table.selection()
    if not selected:
        messagebox.showinfo("Info", "Selecione um item para editar.")
        return
    
    item = table.item(selected[0], "values")
    new_name = simpledialog.askstring("Editar nome", "Novo nome:", initialvalue=item[0])
    try:
        new_price = float(simpledialog.askstring("Editar preço", "Novo preço:", initialvalue=item[1][3:]))
    except ValueError:
        messagebox.showerror("Erro", "Preço inválido.")
        return
    
    if new_name:
        cursor.execute("UPDATE shopping_list SET name=?, price=? WHERE name=?", (new_name, new_price, item[0]))
        conn.commit()
        render_table()

# Função para excluir um item
def delete_item():
    selected = table.selection()
    if not selected:
        messagebox.showinfo("Info", "Selecione um item para excluir.")
        return

    item = table.item(selected[0], "values")
    cursor.execute("DELETE FROM shopping_list WHERE name=?", (item[0],))
    conn.commit()
    render_table()

# Função para buscar itens
def search_items():
    query = search_entry.get().strip().lower()
    cursor.execute("SELECT * FROM shopping_list WHERE LOWER(name) LIKE ? OR price LIKE ?", (f"%{query}%", f"%{query}%"))
    for row in table.get_children():
        table.delete(row)
    
    for row in cursor.fetchall():
        table.insert("", "end", values=(row[1], f"R$ {row[2]:.2f}", row[3]))

# Função para adicionar nota
def add_note():
    selected = table.selection()
    if not selected:
        messagebox.showinfo("Info", "Selecione um item para adicionar uma nota.")
        return

    item = table.item(selected[0], "values")
    note = simpledialog.askstring("Nota", "Digite a nota:", initialvalue=item[2])
    
    cursor.execute("UPDATE shopping_list SET note=? WHERE name=?", (note, item[0]))
    conn.commit()
    render_table()

# Configuração da janela principal
root = tk.Tk()
root.title("Lista de Compras")
root.geometry("800x600")
root.config(bg="#f0f4f8")

# Label principal
title_label = tk.Label(root, text="Lista de Compras", font=("Arial", 24), fg="#333", bg="#f0f4f8")
title_label.pack(pady=10)

# Entrada de itens
form_frame = tk.Frame(root, bg="#f0f4f8")
form_frame.pack(pady=10)

item_name_entry = tk.Entry(form_frame, font=("Arial", 14))
item_name_entry.grid(row=0, column=0, padx=5, pady=5)
item_name_entry.insert(0, "Nome do item")

item_price_entry = tk.Entry(form_frame, font=("Arial", 14))
item_price_entry.grid(row=0, column=1, padx=5, pady=5)
item_price_entry.insert(0, "Preço")

add_button = tk.Button(form_frame, text="Adicionar Item", font=("Arial", 12), bg="#007bff", fg="white", command=add_item)
add_button.grid(row=0, column=2, padx=5, pady=5)

# Barra de busca
search_frame = tk.Frame(root, bg="#f0f4f8")
search_frame.pack(pady=10)

search_entry = tk.Entry(search_frame, font=("Arial", 14), width=40)
search_entry.grid(row=0, column=0, padx=5, pady=5)
search_entry.insert(0, "Buscar por nome ou preço")

search_button = tk.Button(search_frame, text="Buscar", font=("Arial", 12), command=search_items)
search_button.grid(row=0, column=1, padx=5, pady=5)

# Tabela para exibir itens
table_frame = tk.Frame(root)
table_frame.pack(fill="both", expand=True, padx=20, pady=10)

columns = ("Nome do Item", "Preço", "Nota")
table = ttk.Treeview(table_frame, columns=columns, show="headings")
table.heading("Nome do Item", text="Nome do Item")
table.heading("Preço", text="Preço")
table.heading("Nota", text="Nota")
table.pack(fill="both", expand=True)

# Preço total
total_price_label = tk.Label(root, text="R$ 0.00", font=("Arial", 18), fg="#007bff", bg="#f0f4f8")
total_price_label.pack(pady=10)

# Botões de ação
action_frame = tk.Frame(root, bg="#f0f4f8")
action_frame.pack(pady=10)

edit_button = tk.Button(action_frame, text="Editar", font=("Arial", 12), command=edit_item)
edit_button.grid(row=0, column=0, padx=5)

note_button = tk.Button(action_frame, text="Adicionar Nota", font=("Arial", 12), command=add_note)
note_button.grid(row=0, column=1, padx=5)

delete_button = tk.Button(action_frame, text="Excluir", font=("Arial", 12), command=delete_item)
delete_button.grid(row=0, column=2, padx=5)

render_table()
root.mainloop()

# Fechar a conexão com o banco de dados ao encerrar o aplicativo
conn.close()
