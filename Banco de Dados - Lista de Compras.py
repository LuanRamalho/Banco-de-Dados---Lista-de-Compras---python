import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
import os

JSON_FILE = "shopping_list.json"

# --- MANIPULAÇÃO DE DADOS ---
def load_data():
    if not os.path.exists(JSON_FILE):
        return []
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_data(data):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- CLASSE PARA PLACEHOLDER ---
class PlaceholderEntry(tk.Entry):
    def __init__(self, container, placeholder, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = "grey"
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

        self._add_placeholder()

    def _add_placeholder(self, event=None):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_color)

    def _clear_placeholder(self, event=None):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.default_fg_color)

    def get_value(self):
        """Retorna o valor real, ignorando o placeholder."""
        val = self.get()
        return "" if val == self.placeholder else val

# --- LÓGICA DE INTERFACE ---
def update_total_price():
    data = load_data()
    total = sum(item.get("price", 0) for item in data)
    total_price_label.config(text=f"Total: R$ {total:.2f}")

def render_cards(query=""):
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    
    data = load_data()
    items = sorted(data, key=lambda x: x['name'].lower())
    
    if query:
        items = [i for i in items if query in i['name'].lower() or query in i.get('note', '').lower()]

    for item in items:
        create_card(item)
    
    update_total_price()

def create_card(item):
    card = tk.Frame(scrollable_frame, bg="white", highlightbackground="#d1d9e0", highlightthickness=1, bd=0)
    card.pack(fill="x", padx=15, pady=8)

    header = tk.Frame(card, bg="white")
    header.pack(fill="x", padx=15, pady=(10, 5))

    tk.Label(header, text=item['name'], font=("Arial", 14, "bold"), bg="white", fg="#333").pack(side="left")
    tk.Label(header, text=f"R$ {item['price']:.2f}", font=("Arial", 13), bg="white", fg="#007bff").pack(side="right")

    note_text = item.get("note", "").strip()
    if note_text:
        note_frame = tk.Frame(card, bg="#f8f9fa", bd=0)
        note_frame.pack(fill="x", padx=15, pady=5)
        lbl_note = tk.Label(note_frame, text=note_text, font=("Arial", 10, "italic"), bg="#f8f9fa", fg="#555", justify="left", wraplength=700)
        lbl_note.pack(anchor="w", padx=10, pady=8)

    footer = tk.Frame(card, bg="white")
    footer.pack(fill="x", padx=15, pady=(5, 10))

    tk.Button(footer, text="✏️ Editar", font=("Arial", 9), command=lambda n=item['name']: edit_item(n)).pack(side="left", padx=2)
    tk.Button(footer, text="📝 Nota", font=("Arial", 9), command=lambda n=item['name']: add_note(n)).pack(side="left", padx=2)
    tk.Button(footer, text="🗑️", font=("Arial", 9), bg="#fee2e2", command=lambda n=item['name']: delete_item(n)).pack(side="right", padx=2)

# --- FUNÇÕES DE AÇÃO ---
def add_item():
    name = item_name_entry.get_value().strip()
    price_val = item_price_entry.get_value().replace(",", ".")
    
    try:
        price = float(price_val)
    except ValueError:
        messagebox.showerror("Erro", "Preço inválido.")
        return
    
    if name:
        data = load_data()
        data.append({"name": name, "price": price, "note": ""})
        save_data(data)
        item_name_entry.delete(0, tk.END); item_name_entry._add_placeholder()
        item_price_entry.delete(0, tk.END); item_price_entry._add_placeholder()
        render_cards()

def add_note(current_name):
    data = load_data()
    item = next((i for i in data if i['name'] == current_name), None)
    current_note = item.get("note", "") if item else ""

    note_window = tk.Toplevel(root)
    note_window.title(f"Nota: {current_name}")
    note_window.geometry("400x750")
    note_window.config(bg="#f0f4f8")
    note_window.transient(root); note_window.grab_set()

    tk.Label(note_window, text=f"Nota para: {current_name}", font=("Arial", 12, "bold"), bg="#f0f4f8").pack(pady=10)
    textarea = tk.Text(note_window, font=("Arial", 11), wrap="word")
    textarea.pack(expand=True, fill="both", padx=20, pady=5)
    textarea.insert("1.0", current_note)

    def save():
        new_note = textarea.get("1.0", "end-1c").strip()
        for i in data:
            if i['name'] == current_name:
                i['note'] = new_note
        save_data(data)
        render_cards()
        note_window.destroy()

    tk.Button(note_window, text="💾 Salvar Nota", bg="#28a745", fg="white", command=save, pady=10, width=20).pack(pady=20)

def edit_item(old_name):
    """Edita o nome e o preço de um item selecionado."""
    data = load_data()
    # Busca o item atual para ter os valores iniciais nos inputs
    item_atual = next((i for i in data if i['name'] == old_name), None)
    if not item_atual:
        return

    # 1. Solicita o Novo Nome
    new_name = simpledialog.askstring("Editar Item", "Novo nome do produto:", initialvalue=item_atual['name'])
    if new_name is None: return # Usuário cancelou

    # 2. Solicita o Novo Preço
    preco_inicial = str(item_atual['price']).replace(".", ",")
    new_price_str = simpledialog.askstring("Editar Preço", f"Novo preço para '{new_name}':", initialvalue=preco_inicial)
    
    if new_price_str is None: return # Usuário cancelou

    try:
        # Trata vírgula e converte para float
        new_price = float(new_price_str.replace(",", "."))
    except ValueError:
        messagebox.showerror("Erro", "Preço inválido. Use o formato 0,00")
        return
    
    # 3. Atualiza os dados no "banco" NoSQL (JSON)
    for item in data:
        if item['name'] == old_name:
            item['name'] = new_name
            item['price'] = new_price
            break
            
    save_data(data)
    render_cards()
    messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")

def delete_item(name):
    if messagebox.askyesno("Confirmar", f"Excluir '{name}'?"):
        data = [i for i in load_data() if i['name'] != name]
        save_data(data)
        render_cards()

def search():
    render_cards(search_entry.get_value().lower())

# --- INTERFACE PRINCIPAL ---
root = tk.Tk()
root.title("Lista de Compras NoSQL - Cards")
root.geometry("850x750")
root.config(bg="#f0f4f8")

tk.Label(root, text="🛒 Minha Lista de Compras", font=("Arial", 22, "bold"), bg="#f0f4f8").pack(pady=15)

form = tk.Frame(root, bg="#f0f4f8")
form.pack(pady=10)

# Inputs com Placeholder
item_name_entry = PlaceholderEntry(form, "Ex: Arroz", font=("Arial", 14), width=20)
item_name_entry.grid(row=0, column=0, padx=5)

item_price_entry = PlaceholderEntry(form, "Ex: 5.50", font=("Arial", 14), width=10)
item_price_entry.grid(row=0, column=1, padx=5)

tk.Button(form, text="Adicionar", bg="#007bff", fg="white", font=("Arial", 11, "bold"), command=add_item).grid(row=0, column=2, padx=5)

search_frame = tk.Frame(root, bg="#f0f4f8")
search_frame.pack(pady=10)
search_entry = PlaceholderEntry(search_frame, "Buscar por nome ou observação...", font=("Arial", 12), width=40)
search_entry.pack(side="left", padx=5)
tk.Button(search_frame, text="🔍", command=search).pack(side="left")

container = tk.Frame(root, bg="#f0f4f8")
container.pack(fill="both", expand=True, padx=20, pady=10)

canvas = tk.Canvas(container, bg="#f0f4f8", highlightthickness=0)
scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#f0f4f8")

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=800)
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

total_price_label = tk.Label(root, text="Total: R$ 0.00", font=("Arial", 18, "bold"), fg="#d9534f", bg="#f0f4f8")
total_price_label.pack(pady=15)

render_cards()
root.mainloop()
