import tkinter as tk
from tkinter import font, messagebox, ttk
import json
import os
from datetime import datetime
from BEpython.client import Vente, GestionVentes, GestionProduits, GestionClients
import tempfile
import subprocess

class VentesView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#e9e9e9")
        self.gestion_produits = GestionProduits()
        self.gestion_clients = GestionClients()
        self.gestion = GestionVentes(self.gestion_produits)
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
        self.refresh_ventes()

    def create_widgets(self):
        title_font = font.Font(family="Helvetica", size=22, weight="bold")
        title = tk.Label(self, text="GDS - Gestion des Ventes", font=title_font, bg=self.colors["light"], anchor="w")
        title.pack(fill=tk.X, padx=30, pady=20)

        content_frame = tk.Frame(self, bg=self.colors["light"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        self.create_new_vente_form(content_frame)
        self.create_ventes_list(content_frame)

    def create_new_vente_form(self, parent):
        form_frame = tk.Frame(parent, bg=self.colors["primary"], padx=30, pady=30)
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(form_frame, text="Nouvelle vente", font=("Helvetica", 18, "bold"),
                 bg=self.colors["primary"], fg=self.colors["text_light"]).pack(anchor="w", pady=(0, 20))

        # Liste déroulante des clients
        tk.Label(form_frame, text="Client", font=("Helvetica", 12),
                 bg=self.colors["primary"], fg=self.colors["text_light"]).pack(anchor="w")
        
        self.client_var = tk.StringVar()
        self.client_combobox = ttk.Combobox(form_frame, textvariable=self.client_var, font=("Helvetica", 12))
        self.client_combobox.pack(fill=tk.X, pady=10, ipady=8)
        self.update_clients_combobox()
        
        # Liste déroulante des produits
        tk.Label(form_frame, text="Produit", font=("Helvetica", 12),
                 bg=self.colors["primary"], fg=self.colors["text_light"]).pack(anchor="w")
        
        self.produit_var = tk.StringVar()
        self.produit_combobox = ttk.Combobox(form_frame, textvariable=self.produit_var, font=("Helvetica", 12))
        self.produit_combobox.pack(fill=tk.X, pady=10, ipady=8)
        self.update_produits_combobox()
        
        # Champ quantité
        tk.Label(form_frame, text="Quantité", font=("Helvetica", 12),
                 bg=self.colors["primary"], fg=self.colors["text_light"]).pack(anchor="w", pady=(10, 0))
        
        self.quantite_entry = tk.Entry(form_frame, font=("Helvetica", 12))
        self.quantite_entry.pack(fill=tk.X, pady=10, ipady=8)

        self.submit_button = tk.Button(
            form_frame, text="Enregistrer la vente", bg=self.colors["button"], fg=self.colors["text_light"],
            font=("Helvetica", 12, "bold"), command=self.add_vente
        )
        self.submit_button.pack(fill=tk.X, pady=(20, 0))

    def create_ventes_list(self, parent):
        self.list_frame = tk.Frame(parent, bg=self.colors["white"])
        self.list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

    def update_clients_combobox(self):
        clients = [(f"{c.id_client} - {c.nom} {c.prenom}") for c in self.gestion_clients.clients]
        self.client_combobox['values'] = clients
        if clients:
            self.client_combobox.current(0)

    def update_produits_combobox(self):
        produits = [(f"{p.id_produit} - {p.nom} (Stock: {p.quantite_stock})") for p in self.gestion_produits.produits]
        self.produit_combobox['values'] = produits
        if produits:
            self.produit_combobox.current(0)

    def refresh_ventes(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        header = tk.Frame(self.list_frame, bg=self.colors["white"])
        header.pack(fill=tk.X, padx=20, pady=10)

        columns = ["ID", "Client", "Produit", "Quantité", "Total", "Date", "Action"]
        for col in columns:
            label = tk.Label(header, text=col, font=("Helvetica", 12, "bold"), bg=self.colors["white"])
            label.pack(side=tk.LEFT, expand=True)

        for vente in self.gestion.ventes:
            row = tk.Frame(self.list_frame, bg=self.colors["white"])
            row.pack(fill=tk.X, padx=20, pady=5)

            # Trouver le client et le produit
            client = next((c for c in self.gestion_clients.clients if c.id_client == vente.id_client), None)
            produit = self.gestion_produits.trouver_produit(vente.id_produit)
            
            client_nom = f"{client.nom} {client.prenom}" if client else "Inconnu"
            produit_nom = produit.nom if produit else "Inconnu"
            
            tk.Label(row, text=vente.id_vente, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=client_nom, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=produit_nom, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=vente.quantite, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=f"{vente.total:.2f} DA", bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=vente.date_vente, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            
            # Ajouter le bouton d'impression
            print_button = tk.Button(
                row, 
                text="🖨️ Imprimer", 
                command=lambda v=vente, c=client, p=produit: self.print_ticket(v, c, p),
                bg=self.colors["white"],
                bd=0
            )
            print_button.pack(side=tk.LEFT, padx=5)

    def generate_ticket_content(self, vente, client, produit):
        """Génère le contenu du ticket de vente"""
        ticket = []
        ticket.append("=" * 40)
        ticket.append("GDS - TICKET DE VENTE")
        ticket.append("=" * 40)
        ticket.append(f"Date: {vente.date_vente}")
        ticket.append(f"Ticket N°: {vente.id_vente}")
        ticket.append("-" * 40)
        ticket.append("INFORMATIONS CLIENT")
        ticket.append(f"Nom: {client.nom} {client.prenom}")
        ticket.append(f"Tél: {client.telephone}")
        ticket.append("-" * 40)
        ticket.append("DÉTAILS DE LA VENTE")
        ticket.append(f"Produit: {produit.nom}")
        ticket.append(f"Quantité: {vente.quantite}")
        ticket.append(f"Prix unitaire: {produit.prix:.2f} DA")
        ticket.append(f"Total: {vente.total:.2f} DA")
        ticket.append("=" * 40)
        ticket.append("Merci de votre confiance!")
        ticket.append("=" * 40)
        return "\n".join(ticket)

    def print_ticket(self, vente, client, produit):
        """Génère et imprime le ticket de vente"""
        try:
            # Sauvegarder le ticket dans un fichier
            chemin_fichier = self.gestion.sauvegarder_ticket(vente, client, produit)

            # Ouvrir le fichier avec l'application par défaut (qui lancera l'impression)
            if os.name == 'nt':  # Windows
                os.startfile(chemin_fichier, 'print')
            else:  # Linux/Mac
                subprocess.run(['lpr', chemin_fichier])

            messagebox.showinfo("Impression", "Le ticket a été envoyé à l'imprimante et sauvegardé.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'impression: {str(e)}")

    def add_vente(self):
        if not self.client_var.get() or not self.produit_var.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un client et un produit.")
            return
            
        try:
            quantite = int(self.quantite_entry.get())
            if quantite <= 0:
                raise ValueError("La quantité doit être positive")
        except ValueError:
            messagebox.showerror("Erreur", "La quantité doit être un nombre entier positif.")
            return
            
        # Extraire les IDs
        id_client = int(self.client_var.get().split(' - ')[0])
        id_produit = int(self.produit_var.get().split(' - ')[0])
        
        # Vérifier le stock
        produit = self.gestion_produits.trouver_produit(id_produit)
        if not produit or produit.quantite_stock < quantite:
            messagebox.showerror("Erreur", "Stock insuffisant pour cette vente.")
            return
        
        self.gestion.enregistrer_vente(id_client, id_produit, quantite)
        self.quantite_entry.delete(0, tk.END)
        self.update_produits_combobox()  # Mettre à jour les stocks affichés
        self.refresh_ventes()