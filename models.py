from __init__ import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    mdp = db.Column(db.String(150))
    evenements = db.relationship('Evenement', backref='user', lazy=True)
    attestations = db.relationship('Attestation')


class Evenement(db.Model):
    __tablename__ = 'evenement'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False)
    date_deb = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date)
    modele_id = db.Column(db.Integer, db.ForeignKey('modele_attestation.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    participants = db.relationship("Participant", backref="evenement", cascade="all, delete-orphan")

class Participant(db.Model):

    __tablename__ = 'participant'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(350), nullable=False, index=True) 
    email = db.Column(db.String(150), nullable=False, index=True) 
    titre_article = db.Column(db.String(350), nullable=False) 
    evenement_id = db.Column(db.Integer, db.ForeignKey('evenement.id'), nullable=False)
    attestations = db.relationship("Attestation", backref="participant", cascade="all, delete-orphan")


class Attestation(db.Model):

    __tablename__ = 'attestation'
    id = db.Column(db.Integer, primary_key=True) 
    chemin_pdf = db.Column(db.String(350))
    chemin_png = db.Column(db.String(350))
    date_generation = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id', ondelete='CASCADE'))
    evenement_id = db.Column(db.Integer, db.ForeignKey('evenement.id', ondelete='CASCADE'))





#Table Pour Admin
class ModeleAttestation(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    template_path = db.Column(db.String, nullable=False)
    template_png = db.Column(db.String, nullable=False)

    # Pour nom
    fontname_nom = db.Column(db.String, default='Helvetica')
    fontsize_nom = db.Column(db.Integer, default=12)
    fontcolor_nom = db.Column(db.String, default='#000000')
    pos_nom_x = db.Column(db.Float, nullable=False)
    pos_nom_y = db.Column(db.Float, nullable=False)
    
    # Pour titre_article
    
    fontname_titre = db.Column(db.String, default='Helvetica')
    fontsize_titre = db.Column(db.Integer, default=12)
    fontcolor_titre = db.Column(db.String, default='#000000')
    pos_titre_x = db.Column(db.Float, nullable=False)
    pos_titre_y = db.Column(db.Float, nullable=False)
   
    # Pour date
    fontname_date = db.Column(db.String, default='Helvetica')
    fontsize_date = db.Column(db.Integer, default=12)
    fontcolor_date = db.Column(db.String, default='#000000')
    pos_date_x = db.Column(db.Float, nullable=False)
    pos_date_y = db.Column(db.Float, nullable=False)
   
    # Positions logo et signature
    pos_logo_x = db.Column(db.Float, nullable=False)
    pos_logo_y = db.Column(db.Float, nullable=False)
    pos_signature_x = db.Column(db.Float, nullable=False)
    pos_signature_y = db.Column(db.Float, nullable=False)

