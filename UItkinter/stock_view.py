import tkinter as tk
from tkinter import font, ttk
import json
import os
from BEpython.client import GestionStock, GestionProduits

class StockView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#e9e9e9")
        self.gestion_produits = GestionProduits()
        self.gestion = GestionStock(self.gestion_produits)
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
        self.refresh_stock()

    def create_widgets(self):
        title_font = font.Font(family="Helvetica", size=22, weight="bold")
        title = tk.Label(self, text="GDS - Gestion du Stock", font=title_font, bg=self.colors["light"], anchor="w")
        title.pack(fill=tk.X, padx=30, pady=20)

        content_frame = tk.Frame(self, bg=self.colors["light"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        self.create_search_form(content_frame)
        self.create_stock_list(content_frame)

    def create_search_form(self, parent):
        form_frame = tk.Frame(parent, bg=self.colors["primary"], padx=30, pady=30)
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(form_frame, text="Recherche de produits", font=("Helvetica", 18, "bold"),
                 bg=self.colors["primary"], fg=self.colors["text_light"]).pack(anchor="w", pady=(0, 20))

        # Critère de recherche
        tk.Label(form_frame, text="Critère de recherche", font=("Helvetica", 12),
                 bg=self.colors["primary"], fg=self.colors["text_light"]).pack(anchor="w")
        
        self.critere_var = tk.StringVar(value="nom")
        criteres = [("Nom", "nom"), ("Catégorie", "categorie"), ("Stock disponible", "stock")]
        
        critere_frame = tk.Frame(form_frame, bg=self.colors["primary"])
        critere_frame.pack(fill=tk.X, pady=10)
        
        for text, value in criteres:
            rb = tk.Radiobutton(critere_frame, text=text, variable=self.critere_var, value=value,
                               bg=self.colors["primary"], fg=self.colors["text_light"],
                               selectcolor=self.colors["dark"], activebackground=self.colors["primary"],
                               activeforeground=self.colors["text_light"])
            rb.pack(side=tk.LEFT, padx=10)
        
        # Valeur de recherche
        tk.Label(form_frame, text="Valeur recherchée", font=("Helvetica", 12),
                 bg=self.colors["primary"], fg=self.colors["text_light"]).pack(anchor="w", pady=(10, 0))
        
        self.valeur_entry = tk.Entry(form_frame, font=("Helvetica", 12))
        self.valeur_entry.pack(fill=tk.X, pady=10, ipady=8)
        
        # Pour le critère "stock", on ajoute une note explicative
        self.stock_note = tk.Label(form_frame, text="Pour le stock, entrez un nombre (produits avec stock ≤ à cette valeur)",
                                  font=("Helvetica", 10), bg=self.colors["primary"], fg=self.colors["text_light"])
        self.stock_note.pack(anchor="w", pady=(0, 10))

        self.search_button = tk.Button(
            form_frame, text="Rechercher", bg=self.colors["button"], fg=self.colors["text_light"],
            font=("Helvetica", 12, "bold"), command=self.search_products
        )
        self.search_button.pack(fill=tk.X, pady=(10, 0))
        
        # Bouton pour afficher tout le stock
        self.show_all_button = tk.Button(
            form_frame, text="Afficher tout le stock", bg=self.colors["dark"], fg=self.colors["text_light"],
            font=("Helvetica", 12), command=self.refresh_stock
        )
        self.show_all_button.pack(fill=tk.X, pady=(10, 0))

    def create_stock_list(self, parent):
        self.list_frame = tk.Frame(parent, bg=self.colors["white"])
        self.list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

    def refresh_stock(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        header = tk.Frame(self.list_frame, bg=self.colors["white"])
        header.pack(fill=tk.X, padx=20, pady=10)

        columns = ["ID", "Produit", "Catégorie", "Prix", "Stock", "Statut"]
        for col in columns:
            label = tk.Label(header, text=col, font=("Helvetica", 12, "bold"), bg=self.colors["white"])
            label.pack(side=tk.LEFT, expand=True)

        for produit in self.gestion_produits.produits:
            row = tk.Frame(self.list_frame, bg=self.colors["white"])
            row.pack(fill=tk.X, padx=20, pady=5)

            # Déterminer le statut du stock
            stock = produit.quantite_stock
            if stock <= 0:
                statut = "ÉPUISÉ"
                statut_color = "#FF0000"  # Rouge
            elif stock < 5:
                statut = "FAIBLE"
                statut_color = "#FFA500"  # Orange
            else:
                statut = "OK"
                statut_color = "#008000"  # Vert
            
            tk.Label(row, text=produit.id_produit, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=produit.nom, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=produit.categorie, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=f"{produit.prix:.2f} DA", bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=stock, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=statut, bg=self.colors["white"], fg=statut_color, font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, expand=True)

    def search_products(self):
        critere = self.critere_var.get()
        valeur = self.valeur_entry.get()
        
        if not valeur and critere != "stock":
            self.refresh_stock()
            return
            
        # Pour le critère stock, on utilise 5 comme valeur par défaut si rien n'est spécifié
        if critere == "stock" and not valeur:
            valeur = "5"
            
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        header = tk.Frame(self.list_frame, bg=self.colors["white"])
        header.pack(fill=tk.X, padx=20, pady=10)

        columns = ["ID", "Produit", "Catégorie", "Prix", "Stock", "Statut"]
        for col in columns:
            label = tk.Label(header, text=col, font=("Helvetica", 12, "bold"), bg=self.colors["white"])
            label.pack(side=tk.LEFT, expand=True)
            
        # Utiliser la méthode rechercher_produit de GestionStock
        resultat = self.gestion.rechercher_produit(critere, valeur)
                    
        if not resultat:
            no_result = tk.Label(self.list_frame, text="Aucun produit correspondant trouvé.", 
                                font=("Helvetica", 12, "italic"), bg=self.colors["white"])
            no_result.pack(pady=20)
            return
            
        for produit in resultat:
            row = tk.Frame(self.list_frame, bg=self.colors["white"])
            row.pack(fill=tk.X, padx=20, pady=5)

            # Déterminer le statut du stock
            stock = produit.quantite_stock
            if stock <= 0:
                statut = "ÉPUISÉ"
                statut_color = "#FF0000"  # Rouge
            elif stock < 5:
                statut = "FAIBLE"
                statut_color = "#FFA500"  # Orange
            else:
                statut = "OK"
                statut_color = "#008000"  # Vert
            
            tk.Label(row, text=produit.id_produit, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=produit.nom, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=produit.categorie, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=f"{produit.prix:.2f} DA", bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=stock, bg=self.colors["white"]).pack(side=tk.LEFT, expand=True)
            tk.Label(row, text=statut, bg=self.colors["white"], fg=statut_color, font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, expand=True)