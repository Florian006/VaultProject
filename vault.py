import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import json
import os
import csv
import hashlib
from datetime import datetime

class VaultFinance:
    def __init__(self, root):
        self.root = root
        self.root.title("VaultFinance Titan Overlord v6.0")
        self.root.geometry("500x900")
        
        # Files and Styling
        self.user_file = "system_users.json"
        self.log_file = "system_logs.json"
        self.colors = {"primary": "#2d3436", "bg": "#f0f2f5", "admin_red": "#d63031", "accent": "#0984e3"}
        
        self.initialize_and_force_admin()
        self.current_user = None
        self.balance = 0.0
        self.history = []
        self.subscriptions = []
        
        self.show_login()

    # --- CORE SECURITY ---
    def hash_pin(self, pin):
        return hashlib.sha256(str(pin).encode()).hexdigest()

    def initialize_and_force_admin(self):
        if os.path.exists(self.user_file):
            with open(self.user_file, "r") as f:
                try: self.users = json.load(f)
                except: self.users = {}
        else: self.users = {}
        self.users["Admin"] = self.hash_pin("1234")
        self.save_system_users()

        if os.path.exists(self.log_file):
            with open(self.log_file, "r") as f:
                try: self.logs = json.load(f)
                except: self.logs = {}
        else: self.logs = {}

    def save_system_users(self):
        with open(self.user_file, "w") as f: json.dump(self.users, f)

    def log_activity(self, user):
        if user not in self.logs: self.logs[user] = []
        self.logs[user].append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        with open(self.log_file, "w") as f: json.dump(self.logs, f)

    # --- UI NAVIGATION ---
    def clear_screen(self):
        for widget in self.root.winfo_children(): widget.destroy()

    def show_login(self):
        self.clear_screen()
        self.root.configure(bg=self.colors["bg"])
        f = tk.Frame(self.root, bg=self.colors["bg"])
        f.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(f, text="🔱", font=("Arial", 65), bg=self.colors["bg"]).pack()
        tk.Label(f, text="TITAN OVERLORD", font=("Helvetica", 18, "bold"), bg=self.colors["bg"]).pack(pady=10)
        
        self.user_var = tk.StringVar(value="Admin")
        tk.OptionMenu(f, self.user_var, *self.users.keys()).pack(pady=5)
        
        self.pin_entry = tk.Entry(f, show="*", justify="center", font=("Arial", 18))
        self.pin_entry.pack(pady=10, ipady=8); self.pin_entry.focus_set()
        
        tk.Button(f, text="UNLOCK SYSTEM", bg=self.colors["primary"], fg="white", width=25, 
                  command=self.check_password).pack(ipady=12)
        
        nav_f = tk.Frame(f, bg=self.colors["bg"])
        nav_f.pack(pady=20)
        tk.Button(nav_f, text="New User", bd=0, bg=self.colors["bg"], command=self.show_registration).pack()

    def check_password(self):
        u, p = self.user_var.get(), self.pin_entry.get()
        if self.hash_pin(p) == self.users.get(u):
            self.current_user = u
            self.log_activity(u)
            self.load_user_data(u)
            self.show_main_interface()
        else: messagebox.showerror("Denied", "Incorrect PIN.")

    def show_registration(self):
        self.clear_screen()
        f = tk.Frame(self.root, bg=self.colors["bg"])
        f.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(f, text="REGISTER", font=("Arial", 12, "bold"), bg=self.colors["bg"]).pack(pady=15)
        u_e = tk.Entry(f, justify="center"); u_e.insert(0, "Name"); u_e.pack(pady=5)
        p_e = tk.Entry(f, show="*", justify="center"); p_e.pack(pady=5)
        def save():
            if u_e.get() and len(p_e.get()) == 4:
                self.users[u_e.get()] = self.hash_pin(p_e.get())
                self.save_system_users(); self.show_login()
        tk.Button(f, text="CREATE", bg="#27ae60", fg="white", width=20, command=save).pack(pady=10)
        tk.Button(f, text="← BACK", bd=0, bg=self.colors["bg"], command=self.show_login).pack()

    # --- DASHBOARD ---
    def show_main_interface(self):
        self.clear_screen()
        header = tk.Frame(self.root, bg=self.colors["primary"], height=100)
        header.pack(fill="x")
        tk.Button(header, text="Logout", bg="#c0392b", fg="white", bd=0, command=self.show_login).place(x=10, y=10)
        self.bal_lbl = tk.Label(header, text=f"${self.balance:,.2f}", font=("Arial", 30, "bold"), fg="white", bg=self.colors["primary"])
        self.bal_lbl.pack(pady=25)

        self.tabs = ttk.Notebook(self.root)
        self.tab_vault = tk.Frame(self.tabs); self.tab_subs = tk.Frame(self.tabs)
        self.tab_bank = tk.Frame(self.tabs); self.tab_tools = tk.Frame(self.tabs)
        
        self.tabs.add(self.tab_vault, text=" Vault ")
        self.tabs.add(self.tab_subs, text=" Subs ")
        self.tabs.add(self.tab_bank, text=" Import ")
        self.tabs.add(self.tab_tools, text=" Tools ")
        
        if self.current_user == "Admin":
            self.tab_adm = tk.Frame(self.tabs)
            self.tabs.add(self.tab_adm, text=" 🛡️ ADMIN SETUP ")
            self.setup_admin_panel()

        self.tabs.pack(expand=True, fill="both")
        self.setup_vault_tab(); self.setup_subs_tab(); self.setup_bank_tab(); self.setup_tools_tab()

    # --- ADMIN SETUP TOOLS ---
    def setup_admin_panel(self):
        container = tk.Canvas(self.tab_adm, bg="white")
        scroll_y = tk.Scrollbar(self.tab_adm, orient="vertical", command=container.yview)
        f = tk.Frame(container, bg="white", padx=20)
        
        container.create_window((0,0), window=f, anchor="nw")
        container.configure(yscrollcommand=scroll_y.set)
        
        # TOOL 1: USER MANAGEMENT (Add/Remove/Recover)
        tk.Label(f, text="USER LIFECYCLE", font=("Arial", 10, "bold"), fg="red", bg="white").pack(pady=10)
        self.adm_target = tk.StringVar(value="Select User")
        others = [u for u in self.users if u != "Admin"]
        if others:
            tk.OptionMenu(f, self.adm_target, *others).pack(fill="x")
            
        tk.Button(f, text="RECOVER/RESET PIN (to 0000)", command=self.adm_recover_pin).pack(fill="x", pady=2)
        tk.Button(f, text="REMOVE USER PERMANENTLY", bg="#ff7675", command=self.adm_remove_user).pack(fill="x", pady=2)
        
        # TOOL 2: GLOBAL MONEY INJECTION/EXTRACTION
        tk.Label(f, text="MONETARY CONTROL", font=("Arial", 10, "bold"), bg="white").pack(pady=10)
        self.adm_amt = tk.Entry(f, justify="center"); self.adm_amt.insert(0, "0.00"); self.adm_amt.pack(fill="x")
        
        btn_f = tk.Frame(f, bg="white")
        btn_f.pack(fill="x", pady=5)
        tk.Button(btn_f, text="ADD MONEY", bg="#55efc4", command=lambda: self.adm_modify_money("add")).pack(side="left", expand=True)
        tk.Button(btn_f, text="REMOVE MONEY", bg="#fab1a0", command=lambda: self.adm_modify_money("rem")).pack(side="left", expand=True)

        # TOOL 3: LOGS
        tk.Label(f, text="SYSTEM LOGS", font=("Arial", 10, "bold"), bg="white").pack(pady=10)
        log_box = tk.Text(f, height=10, font=("Courier", 8), bg="#dfe6e9")
        log_box.pack(fill="x")
        for u, t in self.logs.items():
            log_box.insert(tk.END, f"{u}: {len(t)} entries\n")
        log_box.config(state="disabled")

        container.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        f.bind("<Configure>", lambda e: container.configure(scrollregion=container.bbox("all")))

    def adm_recover_pin(self):
        u = self.adm_target.get()
        if u in self.users:
            self.users[u] = self.hash_pin("0000")
            self.save_system_users()
            messagebox.showinfo("Admin", f"PIN for {u} reset to 0000")

    def adm_remove_user(self):
        u = self.adm_target.get()
        if u in self.users and messagebox.askyesno("Confirm", f"Delete {u}?"):
            del self.users[u]
            if os.path.exists(f"vault_{u}.json"): os.remove(f"vault_{u}.json")
            self.save_system_users()
            self.show_main_interface()

    def adm_modify_money(self, mode):
        u = self.adm_target.get()
        try:
            amt = float(self.adm_amt.get())
            # Load target user's data
            fn = f"vault_{u}.json"
            data = {"balance": 0.0, "history": []}
            if os.path.exists(fn):
                with open(fn, "r") as f: data = json.load(f)
            
            if mode == "add": data["balance"] += amt
            else: data["balance"] -= amt
            
            data["history"].insert(0, {"category": "ADMIN ADJ", "amount": amt, "type": "in" if mode=="add" else "out", 
                                      "date": "ADMIN", "display": f"🛡️ ${amt} ADMIN MOD"})
            
            with open(fn, "w") as f: json.dump(data, f)
            messagebox.showinfo("Admin", f"Modified {u}'s balance by {amt}")
        except: messagebox.showerror("Error", "Select user and enter valid amount")

    # --- VAULT LOGIC (Same as Ultimate) ---
    def setup_vault_tab(self):
        f = tk.Frame(self.tab_vault, bg="white", padx=15, pady=15)
        f.pack(fill="x", padx=20, pady=20)
        self.amt_e = tk.Entry(f, font=("Arial", 14), justify="center"); self.amt_e.pack(fill="x")
        self.cat_e = tk.Entry(f, font=("Arial", 10), justify="center"); self.cat_e.pack(fill="x", pady=5)
        btn_f = tk.Frame(f, bg="white"); btn_f.pack(fill="x")
        tk.Button(btn_f, text="+ Income", bg="#27ae60", fg="white", command=lambda: self.add_tx("in")).pack(side="left", expand=True)
        tk.Button(btn_f, text="- Expense", bg="#e74c3c", fg="white", command=lambda: self.add_tx("out")).pack(side="left", expand=True)
        self.lb = tk.Listbox(self.tab_vault, font=("Courier", 10)); self.lb.pack(fill="both", expand=True, padx=20)
        for i in self.history: self.lb.insert(tk.END, i['display'])

    def add_tx(self, mode):
        try:
            v, c = float(self.amt_e.get()), self.cat_e.get() or "General"
            self.history.insert(0, {"category": c, "amount": v, "type": mode, "date": datetime.now().strftime("%Y-%m-%d"),
                                    "display": f"{'⬆' if mode == 'in' else '⬇'} ${v:>9.2f} | {c[:12]}"})
            self.balance = self.balance + v if mode == "in" else self.balance - v
            self.save_user_data(self.current_user); self.show_main_interface()
        except: pass

    # --- REMAINING UTILS (Tools, Subs, Bank) ---
    def setup_subs_tab(self):
        f = tk.Frame(self.tab_subs, bg="white", padx=10); f.pack(fill="x")
        tk.Label(f, text="SUBSCRIPTIONS").pack()
        self.slb = tk.Listbox(self.tab_subs); self.slb.pack(fill="both", expand=True)

    def setup_bank_tab(self):
        tk.Button(self.tab_bank, text="IMPORT CSV", command=self.import_bank).pack(pady=20)

    def import_bank(self):
        p = filedialog.askopenfilename()
        if p: messagebox.showinfo("Import", "CSV Loaded Successfully")

    def setup_tools_tab(self):
        tk.Label(self.tab_tools, text="Currency tools ready").pack(pady=20)

    def load_user_data(self, u):
        fn = f"vault_{u}.json"
        if os.path.exists(fn):
            with open(fn, "r") as f:
                d = json.load(f)
                self.balance, self.history = d.get("balance", 0.0), d.get("history", [])
        else: self.balance, self.history = 0.0, []

    def save_user_data(self, u):
        with open(f"vault_{u}.json", "w") as f:
            json.dump({"balance": self.balance, "history": self.history}, f)

if __name__ == "__main__":
    root = tk.Tk(); app = VaultFinance(root); root.mainloop()
