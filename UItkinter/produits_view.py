# === BACKEND ===

import tkinter as tk
from tkinter import font, messagebox
import json
import os
from BEpython.client import Produit, GestionProduits

class Produit:
    def __init__(self, id_produit, nom, description, prix, categorie, quantite_stock=0):
        self.id_produit = id_produit
        self.nom = nom
        self.description = description
        self.prix = prix
        self.categorie = categorie
        self.quantite_stock = quantite_stock

    def to_dict(self):
        return {
            "id_produit": self.id_produit,
            "nom": self.nom,
            "description": self.description,
            "prix": self.prix,
            "categorie": self.categorie,
            "quantite_stock": self.quantite_stock
        }

class GestionProduits:
    def __init__(self, fichier_produits="produits.json"):
        self.fichier_produits = fichier_produits
        self.produits = self.charger_produits()

    def charger_produits(self):
        if os.path.exists(self.fichier_produits):
            with open(self.fichier_produits, "r", encoding="utf-8") as f:
                donnees = json.load(f)
                return [Produit(**produit) for produit in donnees]
        return []

    def sauvegarder_produits(self):
        with open(self.fichier_produits, "w", encoding="utf-8") as f:
            json.dump([produit.to_dict() for produit in self.produits], f, indent=4)

    def generer_nouvel_id(self):
        if not self.produits:
            return 1
        return max(produit.id_produit for produit in self.produits) + 1

    def ajouter_produit(self, nom, description, prix, categorie, quantite):
        id_produit = self.generer_nouvel_id()
        nouveau_produit = Produit(id_produit, nom, description, prix, categorie, quantite)
        self.produits.append(nouveau_produit)
        self.sauvegarder_produits()
        return nouveau_produit

    def modifier_produit(self, id_produit, nom, description, prix, categorie, quantite):
        for produit in self.produits:
            if produit.id_produit == id_produit:
                produit.nom = nom
                produit.description = description
                produit.prix = prix
                produit.categorie = categorie
                produit.quantite_stock = quantite
                self.sauvegarder_produits()
                return

    def supprimer_produit(self, id_produit):
        self.produits = [p for p in self.produits if p.id_produit != id_produit]
        self.sauvegarder_produits()

# === FRONTEND ===

class ProduitsView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#e9e9e9")
        self.gestion = GestionProduits()
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
        self.refresh_products()

    def create_widgets(self):
        title_font = font.Font(family="Helvetica", size=22, weight="bold")
        title = tk.Label(self, text="GDS - Gestion des Produits", font=title_font, bg=self.colors["light"], anchor="w")
        title.pack(fill=tk.X, padx=30, pady=20)

        content_frame = tk.Frame(self, bg=self.colors["light"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        self.create_new_product_form(content_frame)
        self.create_products_list(content_frame)

    def create_new_product_form(self, parent):
        form_frame = tk.Frame(parent, bg=self.colors["primary"], padx=20, pady=20)
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(form_frame, text="Nouveau produit", font=("Helvetica", 18, "bold"),
                 bg=self.colors["primary"], fg=self.colors["text_light"]).pack(anchor="w", pady=(0, 20))

        self.fields = {}
        inputs = [
            ("Nom du produit", "name"),
            ("Description", "description"),
            ("Prix", "price"),
            ("Catégorie", "category"),
            ("Quantité", "quantite")
        ]

        self.id_label = tk.Label(form_frame, text="ID Produit : ---", font=("Helvetica", 12, "italic"),
                                 bg=self.colors["primary"], fg=self.colors["text_light"])
        self.id_label.pack(anchor="w", pady=(0, 10))

        for label_text, key in inputs:
            entry = tk.Entry(form_frame, font=("Helvetica", 12))
            entry.pack(fill=tk.X, pady=4, ipady=8)
            entry.insert(0, f"{label_text}...")
            entry.bind("<FocusIn>", lambda e, entry=entry, text=label_text: self.on_entry_focus_in(entry, f"{text}..."))
            entry.bind("<FocusOut>", lambda e, entry=entry, text=label_text: self.on_entry_focus_out(entry, f"{text}..."))
            self.fields[key] = entry

        # Ajouter le filtre par catégorie
        filter_frame = tk.Frame(form_frame, bg=self.colors["primary"])
        filter_frame.pack(fill=tk.X, pady=10)
        
        self.categorie_filter = tk.Entry(filter_frame, font=("Helvetica", 12))
        self.categorie_filter.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        self.categorie_filter.insert(0, "Filtrer par catégorie...")
        self.categorie_filter.bind("<FocusIn>", lambda e: self.on_entry_focus_in(self.categorie_filter, "Filtrer par catégorie..."))
        self.categorie_filter.bind("<FocusOut>", lambda e: self.on_entry_focus_out(self.categorie_filter, "Filtrer par catégorie..."))
        
        filter_button = tk.Button(
            filter_frame, text="Filtrer", bg=self.colors["button"], fg=self.colors["text_light"],
            font=("Helvetica", 12, "bold"), command=self.filter_by_category
        )
        filter_button.pack(side=tk.LEFT, padx=(10, 0))

        self.submit_button = tk.Button(
            form_frame, text="Ajouter", bg=self.colors["button"], fg=self.colors["text_light"],
            font=("Helvetica", 12, "bold"), command=self.add_or_update_product
        )
        self.submit_button.pack(fill=tk.X, pady=(20, 0))

    def create_products_list(self, parent):
        self.list_frame = tk.Frame(parent, bg=self.colors["white"])
        self.list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

    def refresh_products(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        header = tk.Frame(self.list_frame, bg=self.colors["white"])
        header.pack(fill=tk.X, padx=20, pady=4)

        columns = ["ID", "Nom", "Prix", "Catégorie", "Quantité", "Action"]
        for col in columns:
            label = tk.Label(header, text=col, font=("Helvetica", 12, "bold"), bg=self.colors["white"])
            label.pack(side=tk.LEFT, expand=True)

        for produit in self.gestion.produits:
            row = tk.Frame(self.list_frame, bg=self.colors["white"])
            row.pack(fill=tk.X, padx=20, pady=4)

            tk.Label(row, text=produit.id_produit, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=produit.nom, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=produit.prix, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=produit.categorie, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=produit.quantite_stock, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)

            actions = tk.Frame(row, bg=self.colors["white"])
            actions.pack(side=tk.RIGHT)

            tk.Button(actions, text="✏️", command=lambda p=produit: self.load_product(p), bg=self.colors["white"], bd=0).pack(side=tk.LEFT)
            tk.Button(actions, text="🗑", command=lambda p=produit: self.delete_product(p.id_produit), bg=self.colors["white"], bd=0).pack(side=tk.LEFT)

    def add_or_update_product(self):
        name = self.fields["name"].get()
        description = self.fields["description"].get()
        price = self.fields["price"].get()
        category = self.fields["category"].get()
        quantite = self.fields["quantite"].get()

        if not name or name == "Nom du produit...":
            messagebox.showerror("Erreur", "Le nom du produit est requis.")
            return
        if not description or description == "Description...":
            messagebox.showerror("Erreur", "La description du produit est obligatoire.")
            return
        if not category or category == "Catégorie...":
            messagebox.showerror("Erreur", "La catégorie du produit est obligatoire.")
            return

        try:
            price = float(price)
            quantite = int(quantite)
        except ValueError:
            messagebox.showerror("Erreur", "Prix et Quantité doivent être numériques.")
            return

        if self.submit_button["text"] == "Ajouter":
            produit = self.gestion.ajouter_produit(name, description, price, category, quantite)
        else:
            self.gestion.modifier_produit(self.editing_id, name, description, price, category, quantite)
            self.submit_button.config(text="Ajouter")
            self.editing_id = None

        self.clear_form()
        self.refresh_products()

    def load_product(self, produit):
        self.editing_id = produit.id_produit
        self.id_label.config(text=f"ID Produit : {produit.id_produit}")
        self.fields["name"].delete(0, tk.END)
        self.fields["name"].insert(0, produit.nom)
        self.fields["description"].delete(0, tk.END)
        self.fields["description"].insert(0, produit.description)
        self.fields["price"].delete(0, tk.END)
        self.fields["price"].insert(0, produit.prix)
        self.fields["category"].delete(0, tk.END)
        self.fields["category"].insert(0, produit.categorie)
        self.fields["quantite"].delete(0, tk.END)
        self.fields["quantite"].insert(0, produit.quantite_stock)
        self.submit_button.config(text="Modifier")

    def delete_product(self, id_produit):
        confirm = messagebox.askyesno("Confirmation", "Supprimer ce produit ?")
        if confirm:
            self.gestion.supprimer_produit(id_produit)
            self.refresh_products()

    def clear_form(self):
        self.id_label.config(text="ID Produit : ---")
        for field in self.fields.values():
            field.delete(0, tk.END)
            field.event_generate("<FocusOut>")

    def on_entry_focus_in(self, entry, default_text):
        if entry.get() == default_text:
            entry.delete(0, tk.END)

    def on_entry_focus_out(self, entry, default_text):
        if not entry.get():
            entry.insert(0, default_text)

    def filter_by_category(self):
        categorie = self.categorie_filter.get()
        if not categorie or categorie == "Filtrer par catégorie...":
            self.refresh_products()
            return
        """Filtre les produits par catégorie"""
        categorie = self.categorie_filter.get().strip()
        if not categorie:
            self.refresh_products()  # Si le champ est vide, afficher tous les produits
            return

        # Vider la liste actuelle
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        # Créer l'en-tête
        header = tk.Frame(self.list_frame, bg=self.colors["white"])
        header.pack(fill=tk.X, padx=20, pady=4)

        columns = ["ID", "Nom", "Prix", "Catégorie", "Quantité", "Action"]
        for col in columns:
            label = tk.Label(header, text=col, font=("Helvetica", 12, "bold"), bg=self.colors["white"])
            label.pack(side=tk.LEFT, expand=True)

        # Filtrer et afficher les produits
        produits_filtres = [p for p in self.gestion.produits if p.categorie.lower() == categorie.lower()]
        
        if not produits_filtres:
            no_result = tk.Label(self.list_frame, 
                               text=f"Aucun produit trouvé dans la catégorie '{categorie}'",
                               font=("Helvetica", 12, "italic"),
                               bg=self.colors["white"])
            no_result.pack(pady=20)
            return

        for produit in produits_filtres:
            row = tk.Frame(self.list_frame, bg=self.colors["white"])
            row.pack(fill=tk.X, padx=20, pady=4)

            tk.Label(row, text=produit.id_produit, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=produit.nom, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=produit.prix, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=produit.categorie, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=produit.quantite_stock, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)

            actions = tk.Frame(row, bg=self.colors["white"])
            actions.pack(side=tk.RIGHT)

            tk.Button(actions, text="✏️", command=lambda p=produit: self.load_product(p), bg=self.colors["white"], bd=0).pack(side=tk.LEFT)
            tk.Button(actions, text="🗑", command=lambda p=produit: self.delete_product(p.id_produit), bg=self.colors["white"], bd=0).pack(side=tk.LEFT)

