from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import User #, Contact
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


@routes.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.home'))

@routes.route('/events')
def events():
    return render_template("events.html")

@routes.route('/eventsDetails')
def eventsDetails():
    return render_template("eventsDetails.html")

@routes.route('/certificate')
def certificate():
    return render_template("certificate.html")

@routes.route('/event')
def event():
    return render_template("events.html")