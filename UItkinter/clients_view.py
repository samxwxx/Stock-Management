import tkinter as tk
from tkinter import font, messagebox, ttk
import json
import os
import re
from BEpython.client import Client, GestionClients, GestionVentes, GestionProduits

class ClientsView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#e9e9e9")
        self.gestion = GestionClients()
        self.gestion_ventes = GestionVentes(GestionProduits())
        self.colors = {
            "primary": "#8B1A10",
            "dark": "#222222",
            "light": "#e9e9e9",
            "white": "#ffffff",
            "text_light": "#ffffff",
            "text_dark": "#222222",
            "button": "#222222",
        }
        self.create_widgets()
        self.refresh_clients()

    def create_widgets(self):
        title_font = font.Font(family="Helvetica", size=22, weight="bold")
        title = tk.Label(self, text="GDS - Gestion des Clients", font=title_font, bg=self.colors["light"], anchor="w")
        title.pack(fill=tk.X, padx=30, pady=20)

        content_frame = tk.Frame(self, bg=self.colors["light"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        self.create_new_client_form(content_frame)
        self.create_clients_list(content_frame)

    def create_new_client_form(self, parent):
        form_frame = tk.Frame(parent, bg=self.colors["primary"], padx=30, pady=30)
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(form_frame, text="Nouveau client", font=("Helvetica", 18, "bold"),
                 bg=self.colors["primary"], fg=self.colors["text_light"]).pack(anchor="w", pady=(0, 20))

        self.fields = {}
        inputs = [
            ("Nom", "nom"),
            ("Prénom", "prenom"),
            ("Adresse", "adresse"),
            ("Téléphone", "telephone"),
            ("Email", "email")
        ]

        self.id_label = tk.Label(form_frame, text="ID Client : ---", font=("Helvetica", 12, "italic"),
                                 bg=self.colors["primary"], fg=self.colors["text_light"])
        self.id_label.pack(anchor="w", pady=(0, 10))

        for label_text, key in inputs:
            entry = tk.Entry(form_frame, font=("Helvetica", 12))
            entry.pack(fill=tk.X, pady=10, ipady=8)
            entry.insert(0, f"{label_text}...")
            entry.bind("<FocusIn>", lambda e, entry=entry, text=label_text: self.on_entry_focus_in(entry, f"{text}..."))
            entry.bind("<FocusOut>", lambda e, entry=entry, text=label_text: self.on_entry_focus_out(entry, f"{text}..."))
            self.fields[key] = entry

        self.submit_button = tk.Button(
            form_frame, text="Ajouter", bg=self.colors["button"], fg=self.colors["text_light"],
            font=("Helvetica", 12, "bold"), command=self.add_or_update_client
        )
        self.submit_button.pack(fill=tk.X, pady=(20, 0))
        
        # Initialiser l'ID d'édition à None
        self.editing_id = None

    def create_clients_list(self, parent):
        self.list_frame = tk.Frame(parent, bg=self.colors["white"])
        self.list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

    def refresh_clients(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        header = tk.Frame(self.list_frame, bg=self.colors["white"])
        header.pack(fill=tk.X, padx=20, pady=10)

        columns = ["ID", "Nom", "Prénom", "Téléphone", "Email", "Action"]
        for col in columns:
            label = tk.Label(header, text=col, font=("Helvetica", 12, "bold"), bg=self.colors["white"])
            label.pack(side=tk.LEFT, expand=True)

        for client in self.gestion.clients:
            row = tk.Frame(self.list_frame, bg=self.colors["white"])
            row.pack(fill=tk.X, padx=20, pady=5)

            tk.Label(row, text=client.id_client, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=client.nom, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=client.prenom, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=client.telephone, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=client.email, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)

            actions = tk.Frame(row, bg=self.colors["white"])
            actions.pack(side=tk.RIGHT)

            tk.Button(actions, text="✏️", command=lambda c=client: self.load_client(c), bg=self.colors["white"], bd=0).pack(side=tk.LEFT)
            tk.Button(actions, text="🗑", command=lambda c=client: self.delete_client(c.id_client), bg=self.colors["white"], bd=0).pack(side=tk.LEFT)
            tk.Button(actions, text="📊", command=lambda c=client: self.show_client_history(c), bg=self.colors["white"], bd=0).pack(side=tk.LEFT)

    def add_or_update_client(self):
        nom = self.fields["nom"].get()
        prenom = self.fields["prenom"].get()
        adresse = self.fields["adresse"].get()
        telephone = self.fields["telephone"].get()
        email = self.fields["email"].get()

        # Nettoyage et validation
        if nom == "Nom..." or prenom == "Prénom...":
            messagebox.showerror("Erreur", "Le nom et le prénom sont requis.")
            return

        # Nettoyage du téléphone
        telephone_clean = re.sub(r'[^0-9]', '', telephone)
        
        # Validation du téléphone
        if len(telephone_clean) != 10 or not telephone_clean.startswith('0'):
            messagebox.showerror("Erreur", "Le numéro de téléphone doit contenir exactement 10 chiffres et commencer par 0.")
            return
            
        # Validation de l'email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Erreur", "L'adresse e-mail n'est pas valide. Elle doit être du type exemple@domaine.com")
            return

        if self.submit_button["text"] == "Ajouter":
            self.gestion.ajouter_client(nom, prenom, adresse, telephone_clean, email)
        else:
            self.gestion.modifier_client(self.editing_id, nom, prenom, adresse, telephone_clean, email)
            self.submit_button.config(text="Ajouter")
            self.editing_id = None


        self.clear_form()
        self.refresh_clients()

    def load_client(self, client):
        self.editing_id = client.id_client
        self.id_label.config(text=f"ID Client : {client.id_client}")
        self.fields["nom"].delete(0, tk.END)
        self.fields["nom"].insert(0, client.nom)
        self.fields["prenom"].delete(0, tk.END)
        self.fields["prenom"].insert(0, client.prenom)
        self.fields["adresse"].delete(0, tk.END)
        self.fields["adresse"].insert(0, client.adresse)
        self.fields["telephone"].delete(0, tk.END)
        self.fields["telephone"].insert(0, client.telephone)
        self.fields["email"].delete(0, tk.END)
        self.fields["email"].insert(0, client.email)
        self.submit_button.config(text="Modifier")

    def delete_client(self, id_client):
        confirm = messagebox.askyesno("Confirmation", "Supprimer ce client ?")
        if confirm:
            self.gestion.supprimer_client(id_client)
            self.refresh_clients()

    def clear_form(self):
        self.id_label.config(text="ID Client : ---")
        for field in self.fields.values():
            field.delete(0, tk.END)
            field.event_generate("<FocusOut>")

    def on_entry_focus_in(self, entry, default_text):
        if entry.get() == default_text:
            entry.delete(0, tk.END)

    def on_entry_focus_out(self, entry, default_text):
        if not entry.get():
            entry.insert(0, default_text)

    def show_client_history(self, client):
        """Affiche l'historique des achats d'un client dans une nouvelle fenêtre"""
        history_window = tk.Toplevel(self)
        history_window.title(f"Historique des achats - {client.nom} {client.prenom}")
        history_window.geometry("800x600")
        history_window.configure(bg=self.colors["light"])

        # Créer un cadre pour le contenu
        content_frame = tk.Frame(history_window, bg=self.colors["light"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # En-tête avec les informations du client
        client_info = tk.Frame(content_frame, bg=self.colors["primary"], padx=20, pady=10)
        client_info.pack(fill=tk.X, pady=(0, 20))

        tk.Label(client_info, 
                text=f"Client : {client.nom} {client.prenom}",
                font=("Helvetica", 14, "bold"),
                bg=self.colors["primary"],
                fg=self.colors["text_light"]).pack(anchor="w")
        tk.Label(client_info,
                text=f"Téléphone : {client.telephone} | Email : {client.email} | Adresse : {client.adresse}",
                font=("Helvetica", 12),
                bg=self.colors["primary"],
                fg=self.colors["text_light"]).pack(anchor="w")

        # En-tête du tableau
        header = tk.Frame(content_frame, bg=self.colors["white"])
        header.pack(fill=tk.X, pady=(0, 10))

        columns = ["ID Vente", "Produit", "Quantité", "Total", "Date"]
        for col in columns:
            label = tk.Label(header, text=col, font=("Helvetica", 12, "bold"), bg=self.colors["white"])
            label.pack(side=tk.LEFT, expand=True)

        # Créer un canvas avec scrollbar
        canvas = tk.Canvas(content_frame, bg=self.colors["light"])
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["light"])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Afficher les ventes du client
        ventes_client = [v for v in self.gestion_ventes.ventes if v.id_client == client.id_client]
        
        if not ventes_client:
            no_data = tk.Label(scrollable_frame,
                             text="Aucun achat enregistré pour ce client",
                             font=("Helvetica", 12, "italic"),
                             bg=self.colors["light"])
            no_data.pack(pady=20)
        else:
            total_achats = 0
            for vente in ventes_client:
                row = tk.Frame(scrollable_frame, bg=self.colors["white"])
                row.pack(fill=tk.X, pady=5)

                produit = self.gestion_ventes.gestion_produits.trouver_produit(vente.id_produit)
                produit_nom = produit.nom if produit else "Inconnu"
                total_achats += vente.total

                tk.Label(row, text=vente.id_vente, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
                tk.Label(row, text=produit_nom, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
                tk.Label(row, text=vente.quantite, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
                tk.Label(row, text=f"{vente.total:.2f} DA", bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
                tk.Label(row, text=vente.date_vente, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)

            # Afficher le total des achats
            total_frame = tk.Frame(scrollable_frame, bg=self.colors["primary"], padx=20, pady=10)
            total_frame.pack(fill=tk.X, pady=(20, 0))
            tk.Label(total_frame,
                    text=f"Total des achats : {total_achats:.2f} DA",
                    font=("Helvetica", 12, "bold"),
                    bg=self.colors["primary"],
                    fg=self.colors["text_light"]).pack(anchor="e")

        # Packer le canvas et la scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")