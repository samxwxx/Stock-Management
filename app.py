import tkinter as tk
from tkinter import font, ttk
import json
import os
import re
from datetime import datetime

# Import des classes backend
from BEpython.client import Client, GestionClients
from BEpython.client import Produit, GestionProduits
from BEpython.client import Achat, GestionAchats
from BEpython.client import Vente, GestionVentes
from BEpython.client import GestionStock

# Import des vues
from UItkinter.produits_view import ProduitsView
from UItkinter.clients_view import ClientsView
from UItkinter.achats_view import AchatsView
from UItkinter.ventes_view import VentesView
from UItkinter.stock_view import StockView

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GDS")
        self.geometry("1200x700")
        self.configure(bg="#e9e9e9")
        
        self.colors = {
            "primary": "#8B1A10",
            "dark": "#222222",
            "light": "#e9e9e9",
            "white": "#ffffff",
            "text_light": "#ffffff",
            "text_dark": "#222222",
            "button": "#222222",
        }
        
        # Initialisation des gestionnaires
        self.gestion_clients = GestionClients()
        self.gestion_produits = GestionProduits()
        self.gestion_achats = GestionAchats(self.gestion_produits)
        self.gestion_ventes = GestionVentes(self.gestion_produits)
        self.gestion_stock = GestionStock(self.gestion_produits)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Création du header
        header = tk.Frame(self, bg=self.colors["primary"], height=80)
        header.pack(fill=tk.X)
        
        title_font = font.Font(family="Helvetica", size=24, weight="bold")
        title = tk.Label(header, text="GDS", font=title_font, 
                         bg=self.colors["primary"], fg=self.colors["text_light"])
        title.pack(side=tk.LEFT, padx=30, pady=20)
        
        # Création du menu latéral
        sidebar = tk.Frame(self, bg=self.colors["dark"], width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        
        # Assurer que le sidebar garde sa largeur
        sidebar.pack_propagate(False)
        
        # Conteneur principal pour les différentes vues
        self.main_container = tk.Frame(self, bg=self.colors["light"])
        self.main_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Boutons du menu
        menu_items = [
            ("Clients", self.show_clients_view),
            ("Produits", self.show_products_view),
            ("Achats", self.show_achats_view),
            ("Ventes", self.show_ventes_view),
            ("Stock", self.show_stock_view)
        ]
        
        menu_button_font = font.Font(family="Helvetica", size=12, weight="bold")
        
        for text, command in menu_items:
            btn = tk.Button(sidebar, text=text, font=menu_button_font,
                           bg=self.colors["dark"], fg=self.colors["text_light"],
                           bd=0, padx=20, pady=15, anchor="w", width=15,
                           activebackground=self.colors["primary"],
                           activeforeground=self.colors["text_light"],
                           command=command)
            btn.pack(fill=tk.X, pady=1)
        
        # Afficher la vue des produits par défaut
        self.show_products_view()
    
    def clear_main_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
    
    def show_clients_view(self):
        self.clear_main_container()
        clients_view = ClientsView(self.main_container)
        clients_view.pack(fill=tk.BOTH, expand=True)
    
    def show_products_view(self):
        self.clear_main_container()
        products_view = ProduitsView(self.main_container)
        products_view.pack(fill=tk.BOTH, expand=True)
    
    def show_achats_view(self):
        self.clear_main_container()
        achats_view = AchatsView(self.main_container)
        achats_view.pack(fill=tk.BOTH, expand=True)
    
    def show_ventes_view(self):
        self.clear_main_container()
        ventes_view = VentesView(self.main_container)
        ventes_view.pack(fill=tk.BOTH, expand=True)
    
    def show_stock_view(self):
        self.clear_main_container()
        stock_view = StockView(self.main_container)
        stock_view.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop() 