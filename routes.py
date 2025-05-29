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

    if evenement.user.id != current_user.id:
        abort(403)

    if request.method == 'POST':
        db.session.delete(evenement)
        db.session.commit()
        flash('Evenement supprimé avec success', category='success')
        return redirect(url_for('routes.dashboard'))
    
    evenement.verified = True
    db.session.commit()
    return render_template("events.html", user=current_user, evenement=evenement)
    

@routes.route('/edit_event/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    event = Evenement.query.get_or_404(id)
    
    if event.user_id != current_user.id:
        abort(403)
    
    if request.method == 'POST':
        event.nom = request.form.get('nom')
        event.date_deb = request.form.get('date_deb')
        event.date_fin = request.form.get('date_fin')
        
        db.session.commit()
        flash('Événement modifié avec succès!', 'success')
        return redirect(url_for('routes.dashboard'))
    
    return render_template('edit_event.html', user=current_user, event=event)




@routes.route('/certificate')
def certificate():
    return render_template("certificate.html")

