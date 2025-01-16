from flask import Flask, render_template, url_for, redirect, flash, session
from flask_wtf import FlaskForm
from wtforms.validators import ValidationError
from forms import Loginform, Registrationform, ServiceProviderRegistrationForm, ServiceProviderloginform,Admin
import hashlib
from flask_mysqldb import MySQL
from MySQLdb import IntegrityError
import bcrypt

app = Flask(__name__)

app.secret_key = 'gjhsdafuhaiwjerb'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Jaydip.m.p@2204'
app.config['MYSQL_DB'] = 'register'
mysql = MySQL(app)


@app.route('/')
@app.route('/users')
def user():
    return render_template("users.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = Loginform()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM client WHERE Email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            print(f"User found: {user}", flush=True)
            if bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
                session['user_id'] = user[0]
                return redirect(url_for('home'))
            else:
                flash("Invalid email or password", "danger")
                print("Invalid password", flush=True)
        else:
            flash("No user found with this email", "danger")
            print(f"No user found for email: {email}", flush=True)

        return redirect(url_for('login'))

    else:
        print("Form validation failed:", form.errors, flush=True)

    return render_template("login.html", form=form)



@app.route('/register', methods=["POST", "GET"])
def register():
    form = Registrationform()
    try:
        if form.validate_on_submit():
            name = form.name.data
            email = form.email.data.lower()
            mobile = form.Mobile.data
            password = form.password.data
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor = mysql.connection.cursor()

            cursor.execute("INSERT INTO client(Username, Password, Email, Mobile_no) VALUES(%s,%s,%s,%s)", (name, hashed_password, email, mobile,))
            mysql.connection.commit()
            cursor.close()
            flash('you registred successfully', 'success')
            return redirect(url_for('login'))

    except IntegrityError as e:
        flash('Email already taken .', 'danger')
        return redirect(url_for('register'))

    return render_template("register.html", form=form)


@app.route('/home')
def home():
    if 'user_id' in session:
        user_id = session['user_id']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT *FROM client WHERE id=%s", (user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return render_template('home.html', user=user)

    return redirect(url_for('login'))

@app.route('/shome')
def shome():
    if 'user_id' in session:
        user_id = session['user_id']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT *FROM service_provider WHERE S_id=%s", (user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return render_template('shome.html', user=user)

    return redirect(url_for('slogin'))


@app.route('/slogin', methods=["POST", "GET"])
def slogin():
    form = ServiceProviderloginform()
    if form.validate_on_submit():
        email = form.S_Email.data.lower()
        password = form.S_Pass.data
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM service_provider WHERE S_Email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        # print(user[2])
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
                session['user_id'] = user[0]
                return redirect(url_for('shome'))
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for('slogin'))

    return render_template("slogin.html", form=form)


@app.route('/sregister', methods=["POST", "GET"])
def sregister():
    form = ServiceProviderRegistrationForm()
    try:
        if form.validate_on_submit():
            S_Name = form.S_Name.data
            S_Email = form.S_Email.data.lower()
            S_Pass = form.S_Pass.data
            S_Mobile = form.S_Mobile.data
            S_Skill = form.S_Skills.data
            S_City = form.S_City.data
            hash_password = bcrypt.hashpw(S_Pass.encode('utf-8'), bcrypt.gensalt())
            cursor = mysql.connection.cursor()

            cursor.execute("INSERT INTO service_provider(S_Name, S_Email, S_Pass, S_Skills, S_Mobile, S_City) VALUES(%s, %s, %s, %s, %s, %s)",(S_Name, S_Email, hash_password, S_Skill, S_Mobile, S_City))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('slogin'))

    except IntegrityError as e:
        flash('Email already taken.', 'danger')
        return redirect(url_for('sregister'))

    return render_template("sregister.html", form=form)


@app.route("/AdMin", methods=["POST", "GET"])
def admin():
    form = Admin()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Admin WHERE Email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['user_id'] = user[0]
            return redirect(url_for('admin_dashbord',user=user))
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for('admin'))

    return render_template("admin.html", form=form)

@app.route('/dashbord')
def admin_dashbord():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM client")
    client_table = cursor.fetchall()
    cursor.execute("SELECT * FROM service_provider")
    service_provider = cursor.fetchall()
    cursor.close()
    if 'user_id' in session:
        user_id = session['user_id']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT *FROM service_provider WHERE S_id=%s", (user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return render_template('dashbord.html', client_table=client_table, service_provider=service_provider)
    


    
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
