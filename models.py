from __init__ import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    mdp = db.Column(db.String(150))
    events = db.relationship('Evenement')
    attests = db.relationship('Attestation')

class ModeleAttestation(db.Model):
    __tablename__ = 'modele_attestation'
    id = db.Column(db.Integer, primary_key=True)
    nom_modele = db.Column(db.String(150))
    chemin_logo = db.Column(db.String(350), nullable=False)
    chemin_signature = db.Column(db.String(350), nullable=False)
    events = db.relationship('Evenement', backref='modele')


class Evenement(db.Model):
    __tablename__ = 'evenement'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False)
    date_deb = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date)
    modele_id = db.Column(db.Integer, db.ForeignKey('modele_attestation.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Participant(db.Model):
    __tablename__ = 'participant'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(350), nullable=False) 
    email = db.Column(db.String(150), nullable=False) 
    titre_article = db.Column(db.String(350), nullable=False) 
    evenement_id = db.Column(db.Integer, db.ForeignKey('evenement.id'), nullable=False)

class Attestation(db.Model):
    __tablename__ = 'attestation'
    id = db.Column(db.Integer, primary_key=True) 
    chemin_pdf = db.Column(db.String(350), nullable=False)
    chemin_png = db.Column(db.String(350)) 
    date_generation = db.Column(db.Date)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))