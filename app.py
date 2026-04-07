import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# --- CONFIGURATION DE L'APPLICATION ---
app = Flask(__name__)

# Clé secrète pour les sessions
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key')

# Configuration de la Base de Données
# On récupère l'URL depuis les variables d'environnement (Render le fournira)
# En local, c'est celle du fichier .env (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///stock.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de la base de données
db = SQLAlchemy(app)

# --- MODÈLE DE DONNÉES (TA BASE DE DONNÉES) ⭐ ---
class Produit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    reference = db.Column(db.String(50), unique=True, nullable=False)
    quantite = db.Column(db.Integer, default=0)
    prix = db.Column(db.Float, nullable=False)
    categorie = db.Column(db.String(50))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255)) # URL de l'image
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)

    # Méthode pour afficher le nom du produit facilement
    def __repr__(self):
        return f'<Produit {self.nom}>'

# --- ROUTES (PAGES WEB) ---

# 1. Page d'accueil (Voir les marchandises)
@app.route('/')
def index():

    tous_produits = Produit.query.order_by(Produit.date_ajout.desc()).all()

    # Grouper les produits par catégorie
    produits_par_categorie = {
        'Électronique': [],
        'Vêtements': [],
        'Alimentation': [],
        'Autre': []
    }
    
    for produit in tous_produits:
        categorie = produit.categorie if produit.categorie in produits_par_categorie else 'Autre'
        produits_par_categorie[categorie].append(produit)
    
    return render_template('index.html', produits_par_categorie=produits_par_categorie)

# 2. Page d'ajout (Ajouter une marchandise)
@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.form['nom']
        reference = request.form['reference']
        quantite = request.form['quantite']
        prix = request.form['prix']
        categorie = request.form['categorie']
        description = request.form['description']
        image_url = request.form['image_url']

        # Création du nouvel objet
        nouveau_produit = Produit(
            nom=nom, reference=reference, quantite=quantite,
            prix=prix, categorie=categorie, description=description,
            image_url=image_url
        )

        try:
            db.session.add(nouveau_produit)
            db.session.commit()
            flash('✅ Produit ajouté avec succès !', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('❌ Erreur lors de l\'ajout (vérifiez la référence unique).', 'danger')
            return redirect(url_for('ajouter'))

    return render_template('formulaire.html', action="ajouter")

# 3. Suppression (Supprimer une marchandise)
@app.route('/supprimer/<int:id>')
def supprimer(id):
    produit_a_supprimer = Produit.query.get_or_404(id)

    try:
        db.session.delete(produit_a_supprimer)
        db.session.commit()
        flash('🗑️ Produit supprimé avec succès !', 'warning')
        return redirect(url_for('index'))
    except:
        flash('❌ Erreur lors de la suppression.', 'danger')
        return redirect(url_for('index'))

# --- INITIALISATION DE LA BASE DE DONNÉES ---
# Cette partie crée les tables si elles n'existent pas
with app.app_context():
    db.create_all()

# --- LANCEMENT DU SERVEUR ---
if __name__ == '__main__':
    # debug=True permet de voir les erreurs en direct et de recharger automatiquement
    app.run(debug=True)