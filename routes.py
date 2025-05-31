from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, jsonify
from models import User, Evenement, Participant, Attestation, ModeleAttestation
from __init__ import db 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import pandas as pd
import os
from sqlalchemy import or_ 
from flask_sqlalchemy import SQLAlchemy
from pdf2image import convert_from_path
import io
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from datetime import datetime
import zipfile

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

    total_evenement = Evenement.query.filter_by(user_id=current_user.id).count()

    participant_evenement = db.session.query(
        Evenement,
        db.func.count(Participant.id).label('participant_count')
        ).outerjoin(Participant, Participant.evenement_id == Evenement.id).filter(
            Evenement.user_id==current_user.id).group_by(
                Evenement.id
            ).all()
    
    total_participants = db.session.query(Participant).join(
        Evenement,
        Participant.evenement_id == Evenement.id
    ).filter(
        Evenement.user_id == current_user.id
    ).count()
        

    total_attestations = Attestation.query.filter_by(user_id=current_user.id).count()

    return render_template("dashboard.html",
                        user=current_user, 
                        total_evenement=total_evenement, 
                        total_participants=total_participants, 
                        total_attestations=total_attestations,
                        participant_evenement=participant_evenement)


   


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
    participant_count = Participant.query.filter_by(evenement_id=id).count()
    
    evenement.verified = True
    db.session.commit()
    
    return render_template("events.html",user=current_user,evenement=evenement,participants=participants, participant_count=participant_count)

    

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



@routes.route('/certificate/<int:id>', methods = ['GET', 'POST'])
@login_required
def certificate(id):
    evenement = Evenement.query.get_or_404(id)

    certificate = Attestation.query.filter_by(evenement_id=id).all()

    return render_template("certificate.html", evenement=evenement, certificate=certificate)





# Importer les participants

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@routes.route('/upload_participants/<int:event_id>', methods=['POST'])
@login_required
def upload_participants(event_id):
    event = Evenement.query.get_or_404(event_id)
    

    if 'file' not in request.files:
        flash('Aucun fichier sélectionné', 'error')
        return redirect(url_for('routes.events', id=event_id))

    file = request.files['file']
    
    if file.filename == '':
        flash('Aucun fichier sélectionné', 'error')
        return redirect(url_for('routes.events', id=event_id))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        try:

            # Lecture du fichier
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:  # ficchier .xlsc
                df = pd.read_excel(filepath)

            # Vérification des colonnes requises
            required_columns = {'nom', 'email', 'titre_article'}
            if not required_columns.issubset(df.columns):
                flash("Le fichier doit contenir les colonnes: 'nom', 'email', 'titre_article'", 'error')
                return redirect(url_for('routes.events', id=event_id))

            # Ajout des participants
            count = 0
            for _, row in df.iterrows():
                participant = Participant(
                    nom=row['nom'],
                    email=row['email'],
                    titre_article=row['titre_article'],
                    evenement_id=event_id
                )
                db.session.add(participant)
                count += 1

            db.session.commit()
            flash(f'{count} participants ajoutés avec succès!', 'success')
        
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'import: {str(e)}", 'error')
        
        finally:
            # Nettoyage du fichier temporaire
            if os.path.exists(filepath):
                os.remove(filepath)
        
        return redirect(url_for('routes.events', id=event_id))

    flash('Type de fichier non autorisé. Utilisez CSV ou Excel', 'error')
    return redirect(url_for('routes.events', id=event_id))





# Recherche de participants par Nom et ID 





#             GENERATE CERTIFICAT


#ajouter des models à la base sde donnee
@routes.route('/admin/modele_attestation', methods=['GET', 'POST'])
@login_required
def admin_modele_attestation():
    if request.method == 'POST':
        file = request.files.get('template_file')
        if not file:
            flash("Veuillez télécharger un fichier modèle PDF.", "danger")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        path = os.path.join('static', 'templates', filename)
        file.save(path)

        modele = ModeleAttestation(
            template_path=path,
            fontname_nom=request.form.get('fontname_nom'),
            fontsize_nom=int(request.form.get('fontsize_nom')),
            fontcolor_nom=request.form.get('fontcolor_nom'),
            pos_nom_x=float(request.form.get('pos_nom_x')),
            pos_nom_y=float(request.form.get('pos_nom_y')),
            fontname_titre=request.form.get('fontname_titre'),
            fontsize_titre=int(request.form.get('fontsize_titre')),
            fontcolor_titre=request.form.get('fontcolor_titre'),
            pos_titre_x=float(request.form.get('pos_titre_x')),
            pos_titre_y=float(request.form.get('pos_titre_y')),
            fontname_date=request.form.get('fontname_date'),
            fontsize_date=int(request.form.get('fontsize_date')),
            fontcolor_date=request.form.get('fontcolor_date'),
            pos_date_x=float(request.form.get('pos_date_x')),
            pos_date_y=float(request.form.get('pos_date_y')),
            pos_logo_x=float(request.form.get('pos_logo_x')),
            pos_logo_y=float(request.form.get('pos_logo_y')),
            pos_signature_x=float(request.form.get('pos_signature_x')),
            pos_signature_y=float(request.form.get('pos_signature_y'))
        )
        db.session.add(modele)
        db.session.commit()
        flash("Modèle ajouté avec succès.", category="success")
        return redirect(url_for('routes.admin_modele_attestation'))

    return render_template('admin_modele.html')




@routes.route('/generate/<int:event_id>', methods=['GET', 'POST'])
@login_required
def generate(event_id):
    event = Evenement.query.get_or_404(event_id)
    modeles = ModeleAttestation.query.all()

    if request.method == 'POST':
        modele_id = request.form.get('radioDefault')
        modele = ModeleAttestation.query.get(modele_id)

        date_attestation = request.form.get('date')
        logo_file = request.files.get('formFile2')
        signature_file = request.files.get('formFile')

        # Sauvegarde des fichiers logo et signature dans static/temp/
        temp_dir = os.path.join('static', 'temp', f"{datetime.now().strftime('%Y%m%d%H%M%S')}")
        os.makedirs(temp_dir, exist_ok=True)
        logo_path = os.path.join(temp_dir, secure_filename(logo_file.filename))
        signature_path = os.path.join(temp_dir, secure_filename(signature_file.filename))
        logo_file.save(logo_path)
        signature_file.save(signature_path)

        participants = Participant.query.filter_by(evenement_id=event_id).all()
        output_folder = os.path.join('static', 'attestations', f"event_{event_id}")
        os.makedirs(output_folder, exist_ok=True)

        for p in participants:
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)

            # Nom
            pdfmetrics.registerFont(TTFont(modele.fontname_nom, f"static/fonts/{modele.fontname_nom}.ttf"))
            can.setFont(modele.fontname_nom, modele.fontsize_nom)
            can.setFillColor(HexColor(modele.fontcolor_nom))
            can.drawString(modele.pos_nom_x, modele.pos_nom_y, p.nom)

            # Titre article
            pdfmetrics.registerFont(TTFont(modele.fontname_titre, f"static/fonts/{modele.fontname_titre}.ttf"))
            can.setFont(modele.fontname_titre, modele.fontsize_titre)
            can.setFillColor(HexColor(modele.fontcolor_titre))
            can.drawString(modele.pos_titre_x, modele.pos_titre_y, p.titre_article)

            # Date
            pdfmetrics.registerFont(TTFont(modele.fontname_date, f"static/fonts/{modele.fontname_date}.ttf"))
            can.setFont(modele.fontname_date, modele.fontsize_date)
            can.setFillColor(HexColor(modele.fontcolor_date))
            can.drawString(modele.pos_date_x, modele.pos_date_y, date_attestation)

            # Logo et signature
            can.drawImage(logo_path, modele.pos_logo_x, modele.pos_logo_y, width=50, height=50)
            can.drawImage(signature_path, modele.pos_signature_x, modele.pos_signature_y, width=70, height=30)

            can.save()
            packet.seek(0)

            new_pdf = PdfReader(packet)
            existing_pdf = PdfReader(modele.template_path)
            output = PdfWriter()

            page = existing_pdf.pages[0]
            page.merge_page(new_pdf.pages[0])
            output.add_page(page)

        
            cert_filename = f"{p.nom.replace(' ', '_')}.pdf"

           
            relative_path = os.path.join("attestations", f"event_{event_id}", cert_filename)
            relative_path = relative_path.replace("\\", "/")
           
            absolute_path = os.path.join("static", relative_path)

            
          
            with open(absolute_path, 'wb') as f:
                output.write(f)

            png_output_folder = os.path.join(output_folder, "images")
            os.makedirs(png_output_folder, exist_ok=True)

            images = convert_from_path(relative_path, dpi=200)

            image_filename = cert_filename.replace(".pdf", ".png")
            image_path = os.path.join(png_output_folder, image_filename)
            images[0].save(image_path, 'PNG')

            image_path = image_path.replace("\\", "/")

            attestation = Attestation(
                participant_id=p.id,
                evenement_id=event_id,
                chemin_pdf=relative_path, 
                chemin_png=image_path, 
                date_generation=datetime.now()
            )


            db.session.add(attestation)

        db.session.commit()
        flash("Attestations générées et sauvegardées avec succès !", "success")
        return redirect(url_for('routes.events', id=event.id))


    return render_template('generateCertificat.html', modeles=modeles, evenement=event)


@routes.route('/certificate_gallery/<int:event_id>')
@login_required
def certificate_gallery(event_id):

    evenement = Evenement.query.get(event_id)

    attestations = Attestation.query.filter_by(evenement_id=event_id).all()
    return render_template('certificate.html', attestations=attestations, evenement=evenement)

