from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import User, Evenement, Participant, Attestation, ModeleAttestation
from __init__ import db 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

routes = Blueprint('routes', __name__)

@routes.route('/')
def home():
    return render_template('home.html')


@routes.route('/register', methods=["GET","POST"])
def register():
    if request.method == 'POST':
        nom = request.form.get('nom')
        email = request.form.get('email')
        mdp = request.form.get('mdp')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Ce compte existe déjà !', category='error')

        elif not nom and not email and not mdp:
            flash("N'existe pas !", category='error')
        elif len(mdp) < 8:
            flash("Au minimum 8 caracteres !", category='error')
        else:
            new_user = User(nom=nom, email=email, mdp=generate_password_hash(mdp, method='pbkdf2:sha256'))
            flash('Compte créer avec success !', category='success')
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('routes.dashboard'))
    

    return render_template("register.html", user=current_user)




@routes.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        mdp = request.form.get('mdp')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.mdp, mdp):
                flash('Connexion reussi !', category='success')
                login_user(user, remember=True)
                return redirect(url_for('routes.dashboard'))
            else:
                flash('Mot de passe incorrect !', category='error')
        else:
            flash('Non Reconnu !', category='error')

                

    return render_template("login.html", user=current_user)


@routes.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        nom = request.form.get('nom')
        date_deb = request.form.get('date_deb')
        date_fin = request.form.get('date_fin')

        new_event = Evenement(nom=nom, date_deb=date_deb, date_fin=date_fin, user_id=current_user.id)
        db.session.add(new_event)
        db.session.commit()
        flash('Evénement crée avec succès !', category='success')
        return redirect(url_for('routes.dashboard'))

    return render_template("dashboard.html", user=current_user)


   


@routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.home'))



@routes.route('/events/<int:id>', methods=['GET', 'POST'])
@login_required
def events(id):
    evenement = Evenement.query.get_or_404(id)

    if request.method == 'POST':
        
        if 'add_participant' in request.form:
            nom = request.form.get('nom')
            email = request.form.get('email')
            titre_article = request.form.get('titre_article')
            new_participant = Participant(nom=nom, email=email, titre_article=titre_article, evenement_id=id)
            db.session.add(new_participant)
            
            flash('Participant ajouté avec succès!', 'success')
            db.session.commit()
            return redirect(url_for('routes.events', id=id))
        

        elif 'delete_participant' in request.form:
            participant_id = request.form.get('participant_id')
            participant = Participant.query.get(participant_id)
            if participant:
                db.session.delete(participant)
                flash('Participant supprimé avec succès!', 'success')
                db.session.commit()
                return redirect(url_for('routes.events', id=id))

        elif 'delete_evenement' in request.form:
            db.session.delete(evenement)
            db.session.commit()
            flash('Evenement supprimé avec success', category='success')
            return redirect(url_for('routes.dashboard'))
        

    participants = Participant.query.filter_by(evenement_id=id).all()
    
    evenement.verified = True
    db.session.commit()
    
    return render_template("events.html",user=current_user,evenement=evenement,participants=participants)

    

@routes.route('/edit_event/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    event = Evenement.query.get_or_404(id)
    
    if request.method == 'POST':
        event.nom = request.form.get('nom')
        event.date_deb = request.form.get('date_deb')
        event.date_fin = request.form.get('date_fin')
        
        db.session.commit()
        flash('Événement modifié avec succès!', 'success')
        return redirect(url_for('routes.dashboard'))
    
    return render_template('edit_event.html', user=current_user, event=event)




@routes.route('/edit_participant/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_participant(id):
    participant = Participant.query.get_or_404(id)
    evenement = Evenement.query.get(participant.evenement_id)
    
    if request.method == 'POST':
        participant.nom = request.form.get('nom')
        participant.email = request.form.get('email')
        participant.titre_article = request.form.get('titre_article')
        db.session.commit()
        flash('Participant modifié avec succès!', category='success')
        return redirect(url_for('routes.events', id=evenement.id))
    
    return render_template('edit_participant.html', participant=participant, evenement=evenement,user=current_user)

@routes.route('/certificate')
def certificate():
    return render_template("certificate.html")

