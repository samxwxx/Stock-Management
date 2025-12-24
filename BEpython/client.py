import json
import os
from datetime import datetime
import re

class Client:
    def __init__(self, id_client, nom, prenom, adresse, telephone, email):
        self.id_client = id_client
        self.nom = nom
        self.prenom = prenom
        self.adresse = adresse
        self.telephone = telephone
        self.email = email

    def to_dict(self):
        return {
            "id_client": self.id_client,
            "nom": self.nom,
            "prenom": self.prenom,
            "adresse": self.adresse,
            "telephone": self.telephone,
            "email": self.email
        }

class GestionClients:
    def __init__(self, fichier_clients="clients.json"):
        self.fichier_clients = fichier_clients
        self.clients = self.charger_clients()

    def charger_clients(self):
        if os.path.exists(self.fichier_clients):
            with open(self.fichier_clients, "r", encoding="utf-8") as f:
                donnees = json.load(f)
                return [Client(**client) for client in donnees]
        return []

    def sauvegarder_clients(self):
        with open(self.fichier_clients, "w", encoding="utf-8") as f:
            json.dump([client.to_dict() for client in self.clients], f, indent=4)

    def ajouter_client(self, nom, prenom, adresse, telephone, email):
        # Nettoyer le numéro de téléphone (supprimer les espaces, caractères spéciaux, et gérer le code pays)
        telephone = re.sub(r'[^0-9]', '', telephone)  # Enlever tout sauf les chiffres
        
        # Vérifier si le numéro contient 10 chiffres
        if len(telephone) != 10:
            print("❌ Erreur : Le numéro de téléphone doit contenir exactement 10 chiffres.")
            return
        
        # Vérifier le format de l'email avec une regex simple
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            print("❌ Erreur : L'adresse e-mail n'est pas valide. Elle doit être du type exemple@domaine.com")
            return

        # Vérifier si le client existe déjà par le numéro de téléphone
        for client in self.clients:
            if client.telephone == telephone:
                raise ValueError("Ce client existe déjà.")

        id_client = self.generer_nouvel_id()
        nouveau_client = Client(id_client, nom, prenom, adresse, telephone, email)
        self.clients.append(nouveau_client)
        self.sauvegarder_clients()
        print(f"✅ Client {nom} {prenom} ajouté avec succès.")

    def modifier_client(self, id_client, nom, prenom, adresse, telephone, email):
        for client in self.clients:
            if client.id_client == id_client:
                client.nom = nom
                client.prenom = prenom
                client.adresse = adresse
                client.telephone = telephone
                client.email = email
                self.sauvegarder_clients()
                print(f"Client ID {id_client} modifié avec succès.")
                return
        print(f"Client ID {id_client} non trouvé.")

    def supprimer_client(self, id_client):
        for client in self.clients:
            if client.id_client == id_client:
                self.clients.remove(client)
                self.sauvegarder_clients()
                print(f"Client ID {id_client} supprimé avec succès.")
                return
        print(f"Client ID {id_client} non trouvé.")

    def lister_clients(self):
        if not self.clients:
            print("Aucun client enregistré.")
        for client in self.clients:
            print(f"ID: {client.id_client} | Nom: {client.nom} | Prénom: {client.prenom} | Email: {client.email}")

    def generer_nouvel_id(self):
        if not self.clients:
            return 1
        return max(client.id_client for client in self.clients) + 1
    
    def consulter_historique_achats(self, id_client, gestion_ventes):
     ventes_client = [vente for vente in gestion_ventes.ventes if vente.id_client == id_client]

     if ventes_client:
        print(f"\nHistorique des achats pour le client ID {id_client} :")
        for vente in ventes_client:
            print(f"- Produit ID : {vente.id_produit}, Quantité : {vente.quantite}, "
                  f"Date : {vente.date_vente}, Total : {vente.total:.2f} €")
     else:
        print(f"\nAucun achat trouvé pour le client ID {id_client}.")

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
        if not description:
            raise ValueError("La description du produit est obligatoire.")
        if not categorie:
            raise ValueError("La catégorie du produit est obligatoire.")
        id_produit = self.generer_nouvel_id()
        nouveau_produit = Produit(id_produit, nom, description, prix, categorie, quantite)
        self.produits.append(nouveau_produit)
        self.sauvegarder_produits()
        return nouveau_produit

    def trouver_produit(self, id_produit):
        for produit in self.produits:
            if produit.id_produit == id_produit:
                return produit
        return None

    def modifier_produit(self, id_produit, nom, description, prix, categorie):
        for produit in self.produits:
            if produit.id_produit == id_produit:
                produit.nom = nom
                produit.description = description
                produit.prix = prix
                produit.categorie = categorie
                self.sauvegarder_produits()
                print(f"Produit ID {id_produit} modifié avec succès.")
                return
        print(f"Produit ID {id_produit} non trouvé.")

    def supprimer_produit(self, id_produit):
        for produit in self.produits:
            if produit.id_produit == id_produit:
                self.produits.remove(produit)
                self.sauvegarder_produits()
                print(f"Produit ID {id_produit} supprimé avec succès.")
                return
        print(f"Produit ID {id_produit} non trouvé.")

    def lister_produits(self):
        if not self.produits:
            print("Aucun produit enregistré.")
            return
        for produit in self.produits:
            print(f"ID: {produit.id_produit} | Nom: {produit.nom} | Prix: {produit.prix} DA | Catégorie: {produit.categorie}")

    def lister_produits_par_categorie(self, categorie_recherchee):
        produits_trouves = [p for p in self.produits if p.categorie.lower() == categorie_recherchee.lower()]
        if not produits_trouves:
            print(f"Aucun produit trouvé dans la catégorie '{categorie_recherchee}'.")
            return
        for produit in produits_trouves:
             print(f"ID: {produit.id_produit} | Nom: {produit.nom} | Prix: {produit.prix} DA")

    def rechercher_produit(self, critere, valeur):
        resultat = []
        for produit in self.produits:
            if critere == "nom":
                # Recherche insensible à la casse et partielle
                if valeur.lower() in produit.nom.lower():
                    resultat.append(produit)
            elif critere == "categorie":
                # Recherche insensible à la casse et partielle
                if valeur.lower() in produit.categorie.lower():
                    resultat.append(produit)
            elif critere == "stock":
                try:
                    seuil = int(valeur)
                    if produit.quantite_stock <= seuil:
                        resultat.append(produit)
                except ValueError:
                    # Si la valeur n'est pas un nombre, on ignore
                    pass

        return resultat

class Achat:
    def __init__(self, id_produit, quantite, date_achat):
        self.id_produit = id_produit
        self.quantite = quantite
        self.date_achat = date_achat

    def to_dict(self):
        return {
            "id_produit": self.id_produit,
            "quantite": self.quantite,
            "date_achat": self.date_achat
        }

class GestionAchats:
    def __init__(self, gestion_produits, fichier_achats="achats.json"):
        self.gestion_produits = gestion_produits
        self.fichier_achats = fichier_achats
        self.achats = self.charger_achats()

    def charger_achats(self):
        if os.path.exists(self.fichier_achats):
            with open(self.fichier_achats, "r", encoding="utf-8") as f:
                donnees = json.load(f)
                return [Achat(**achat) for achat in donnees]
        return []

    def sauvegarder_achats(self):
        with open(self.fichier_achats, "w", encoding="utf-8") as f:
            json.dump([achat.to_dict() for achat in self.achats], f, indent=4)

    def ajouter_achat(self, id_produit, quantite):
        produit = self.trouver_produit(id_produit)
        if produit:
            # Mettre à jour la quantité en stock
            produit.quantite_stock += quantite
            self.gestion_produits.sauvegarder_produits()

            # Créer l'achat
            date_achat = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            nouvel_achat = Achat(id_produit, quantite, date_achat)
            self.achats.append(nouvel_achat)
            self.sauvegarder_achats()

            print(f"Achat enregistré : +{quantite} unités pour '{produit.nom}'.")
        else:
            print(f"Produit avec ID {id_produit} non trouvé.")

    def trouver_produit(self, id_produit):
        for produit in self.gestion_produits.produits:
            if produit.id_produit == id_produit:
                return produit
        return None

    def lister_achats(self):
        if not self.achats:
            print("Aucun achat enregistré.")
            return
        for achat in self.achats:
            produit = self.trouver_produit(achat.id_produit)
            produit_nom = produit.nom if produit else "Inconnu"
            print(f"Produit: {produit_nom} | Quantité: {achat.quantite} | Date: {achat.date_achat}")    

class Vente:
    def __init__(self, id_vente, id_client, id_produit, quantite, date_vente, total):
        self.id_vente = id_vente
        self.id_client = id_client
        self.id_produit = id_produit
        self.quantite = quantite
        self.date_vente = date_vente
        self.total = total

    def to_dict(self):
        return {
            "id_vente": self.id_vente,
            "id_client": self.id_client,
            "id_produit": self.id_produit,
            "quantite": self.quantite,
            "date_vente": self.date_vente,
            "total": self.total
        }
       


class GestionVentes:
    def __init__(self, gestion_produits, fichier_ventes="ventes.json"):
        self.gestion_produits = gestion_produits
        self.fichier_ventes = fichier_ventes
        self.ventes = self.charger_ventes()

        # Créer le dossier tickets s'il n'existe pas
        self.tickets_dir = "tickets"
        if not os.path.exists(self.tickets_dir):
            os.makedirs(self.tickets_dir)


    def charger_ventes(self):
        if os.path.exists(self.fichier_ventes):
            with open(self.fichier_ventes, "r", encoding="utf-8") as f:
                donnees = json.load(f)
                return [Vente(**vente) for vente in donnees]
        return []

    def sauvegarder_ventes(self):
        with open(self.fichier_ventes, "w", encoding="utf-8") as f:
            json.dump([vente.to_dict() for vente in self.ventes], f, indent=4)

    def generer_nouvel_id(self):
        if not self.ventes:
            return 1
        return max(vente.id_vente for vente in self.ventes) + 1

    def sauvegarder_ticket(self, vente, client, produit):
        """Sauvegarde le ticket de vente dans un fichier texte"""
        # Créer le nom du fichier avec l'ID de la vente et la date
        nom_fichier = f"ticket_{vente.id_vente}_{vente.date_vente.replace(':', '-')}.txt"
        chemin_fichier = os.path.join(self.tickets_dir, nom_fichier)

        # Générer le contenu du ticket
        ticket_content = []
        ticket_content.append("=" * 40)
        ticket_content.append("GDS - TICKET DE VENTE")
        ticket_content.append("=" * 40)
        ticket_content.append(f"Date: {vente.date_vente}")
        ticket_content.append(f"Ticket N°: {vente.id_vente}")
        ticket_content.append("-" * 40)
        ticket_content.append("INFORMATIONS CLIENT")
        ticket_content.append(f"Nom: {client.nom} {client.prenom}")
        ticket_content.append(f"Tél: {client.telephone}")
        ticket_content.append("-" * 40)
        ticket_content.append("DÉTAILS DE LA VENTE")
        ticket_content.append(f"Produit: {produit.nom}")
        ticket_content.append(f"Quantité: {vente.quantite}")
        ticket_content.append(f"Prix unitaire: {produit.prix:.2f} DA")
        ticket_content.append(f"Total: {vente.total:.2f} DA")
        ticket_content.append("=" * 40)
        ticket_content.append("Merci de votre confiance!")
        ticket_content.append("=" * 40)

        # Écrire le contenu dans le fichier
        with open(chemin_fichier, "w", encoding="utf-8") as f:
            f.write("\n".join(ticket_content))

        return chemin_fichier

    def enregistrer_vente(self, id_client, id_produit, quantite_vendue):
        produit = self.gestion_produits.trouver_produit(id_produit)
        if produit:
            if produit.quantite_stock >= quantite_vendue:
                produit.quantite_stock -= quantite_vendue
                self.gestion_produits.sauvegarder_produits()
                total = produit.prix * quantite_vendue
                date_vente = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                id_vente = self.generer_nouvel_id()
                nouvelle_vente = Vente(id_vente, id_client, id_produit, quantite_vendue, date_vente, total)
                self.ventes.append(nouvelle_vente)
                self.sauvegarder_ventes()
                print(f"Vente enregistrée : {quantite_vendue} x {produit.nom} ({total} DA).")
            else:
                print("Stock insuffisant pour cette vente.")
        else:
            print(f"Produit avec ID {id_produit} non trouvé.")

    def lister_ventes(self):
        if not self.ventes:
            print("Aucune vente enregistrée.")
            return
        for vente in self.ventes:
            produit = self.gestion_produits.trouver_produit(vente.id_produit)
            produit_nom = produit.nom if produit else "Inconnu"
            print(f"ID Vente: {vente.id_vente} | Produit: {produit_nom} | Quantité: {vente.quantite} | Total: {vente.total} € | Date: {vente.date_vente}")

class GestionStock:
    def __init__(self, gestion_produits):
        self.gestion_produits = gestion_produits

    def afficher_etat_stock(self):
        print("\n--- État actuel du stock ---")
        for produit in self.gestion_produits.produits:
            stock = produit.quantite_stock
            alert = "⚠️ STOCK FAIBLE" if stock < 5 else ""
            print(f"Produit: {produit.nom} | Stock: {stock} unités {alert}")

    def rechercher_produit(self, critere, valeur):
        resultat = []
        for produit in self.gestion_produits.produits:
            if critere == "nom":
                # Recherche insensible à la casse et partielle
                if valeur.lower() in produit.nom.lower():
                    resultat.append(produit)
            elif critere == "categorie":
                # Recherche insensible à la casse et partielle
                if valeur.lower() in produit.categorie.lower():
                    resultat.append(produit)
            elif critere == "stock":
                try:
                    seuil = int(valeur)
                    if produit.quantite_stock <= seuil:
                        resultat.append(produit)
                except ValueError:
                    # Si la valeur n'est pas un nombre, on ignore
                    pass

        return resultat




