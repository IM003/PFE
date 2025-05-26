from flask import Flask, render_template, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
import bcrypt
from flask_mysqldb import MySQL 



#APP config

app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mydatabase'
app.secret_key = 'your_secret_key_here'

mysql = MySQL(app)

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Register')



# Les routes

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    
    print(f"mysql = {mysql}")  # pour debug
    print(f"mysql.connection = {mysql.connection}")  # pour debug
    
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) 

        try:
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
            mysql.connection.commit()
            cursor.close()
        except Exception as e:
            print(f"Erreur MySQL : {e}")
            return "Erreur lors de l'enregistrement"

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/modeles')
def modeles():
    return render_template('modeles.html')

@app.route('/modelesDetails')
def modelesDetails():
    return render_template('modelesDetails.html')

@app.route('/events')
def events():
    return render_template('events.html')

@app.route('/eventsDetails')
def eventsDetails():
    return render_template('eventsDetails.html')

@app.route('/certificates')
def certificates():
    return render_template('certificate.html')




if __name__ == '__main__':
    app.run(debug=True)