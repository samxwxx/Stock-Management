import tkinter as tk
from tkinter import font, messagebox, ttk
import json
import os
from datetime import datetime
from BEpython.client import Achat, GestionAchats, GestionProduits

class AchatsView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#e9e9e9")
        self.gestion_produits = GestionProduits()
        self.gestion = GestionAchats(self.gestion_produits)
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
        self.refresh_achats()

    def create_widgets(self):
        title_font = font.Font(family="Helvetica", size=22, weight="bold")
        title = tk.Label(self, text="GDS - Gestion des Achats", font=title_font, bg=self.colors["light"], anchor="w")
        title.pack(fill=tk.X, padx=30, pady=20)

        content_frame = tk.Frame(self, bg=self.colors["light"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        self.create_new_achat_form(content_frame)
        self.create_achats_list(content_frame)

    def create_new_achat_form(self, parent):
        form_frame = tk.Frame(parent, bg=self.colors["primary"], padx=30, pady=30)
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(form_frame, text="Nouvel achat", font=("Helvetica", 18, "bold"),
                 bg=self.colors["primary"], fg=self.colors["text_light"]).pack(anchor="w", pady=(0, 20))

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
            form_frame, text="Ajouter", bg=self.colors["button"], fg=self.colors["text_light"],
            font=("Helvetica", 12, "bold"), command=self.add_achat
        )
        self.submit_button.pack(fill=tk.X, pady=(20, 0))

    def create_achats_list(self, parent):
        self.list_frame = tk.Frame(parent, bg=self.colors["white"])
        self.list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

    def update_produits_combobox(self):
        produits = [(f"{p.id_produit} - {p.nom}") for p in self.gestion_produits.produits]
        self.produit_combobox['values'] = produits
        if produits:
            self.produit_combobox.current(0)

    def refresh_achats(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        header = tk.Frame(self.list_frame, bg=self.colors["white"])
        header.pack(fill=tk.X, padx=20, pady=10)

        columns = ["Produit", "Quantité", "Date d'achat"]
        for col in columns:
            label = tk.Label(header, text=col, font=("Helvetica", 12, "bold"), bg=self.colors["white"])
            label.pack(side=tk.LEFT, expand=True)

        for achat in self.gestion.achats:
            row = tk.Frame(self.list_frame, bg=self.colors["white"])
            row.pack(fill=tk.X, padx=20, pady=5)

            produit = self.gestion.trouver_produit(achat.id_produit)
            produit_nom = produit.nom if produit else "Inconnu"
            
            tk.Label(row, text=produit_nom, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=achat.quantite, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=achat.date_achat, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)

    def add_achat(self):
        if not self.produit_var.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un produit.")
            return
            
        try:
            quantite = int(self.quantite_entry.get())
            if quantite <= 0:
                raise ValueError("La quantité doit être positive")
        except ValueError:
            messagebox.showerror("Erreur", "La quantité doit être un nombre entier positif.")
            return
            
        # Extraire l'ID du produit de la chaîne sélectionnée
        id_produit = int(self.produit_var.get().split(' - ')[0])
        
        self.gestion.ajouter_achat(id_produit, quantite)
        self.quantite_entry.delete(0, tk.END)
        self.refresh_achats()