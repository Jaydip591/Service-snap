from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from com.DAO.client_dao import ClientDAO
from com.DAO.service_provider_dao import ServiceProviderDAO
from com.VO import ClientVO, ServiceProviderVO
from forms import Loginform, Registrationform, ServiceProviderRegistrationForm, ServiceProviderloginform
from base import mysql
import bcrypt
from werkzeug.utils import secure_filename

bp = Blueprint('auth', __name__)
client_dao = ClientDAO()
service_provider_dao = ServiceProviderDAO()

# Configure upload folder for user photos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
@bp.route('/users')
def user():
    return render_template("users.html")

@bp.route('/login', methods=['POST', 'GET'])
def login():
    form = Loginform()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data
        
        user = client_dao.get_by_email(email)
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            session['user_id'] = user.id
            return redirect(url_for('auth.home'))
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for('auth.login'))

    return render_template("login.html", form=form)

@bp.route('/register', methods=["POST", "GET"])
def register():
    form = Registrationform()
    if form.validate_on_submit():
        client = ClientVO(
            username=form.name.data,
            email=form.email.data.lower(),
            mobile_no=form.Mobile.data,
            password=form.password.data
        )
        try:
            client_dao.create(client)
            flash('You registered successfully', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('Email already taken.', 'danger')
            return redirect(url_for('auth.register'))

    return render_template("register.html", form=form)

@bp.route('/home')
def home():
    if 'user_id' in session:
        user = client_dao.get_by_id(session['user_id'])
        if user:
            # Add the user city to the session for filters
            session['user_city'] = user.city
            return render_template('home.html', user=user)
    return redirect(url_for('auth.login'))

@bp.route('/slogin', methods=["POST", "GET"])
def slogin():
    form = ServiceProviderloginform()
    if form.validate_on_submit():
        email = form.S_Email.data.lower()
        password = form.S_Pass.data
        
        provider = service_provider_dao.get_by_email(email)
        if provider and bcrypt.checkpw(password.encode('utf-8'), provider.s_pass.encode('utf-8')):
            session['user_id'] = provider.s_id
            return redirect(url_for('auth.shome'))
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for('auth.slogin'))

    return render_template("slogin.html", form=form)

@bp.route('/sregister', methods=["POST", "GET"])
def sregister():
    form = ServiceProviderRegistrationForm()
    if form.validate_on_submit():
        provider = ServiceProviderVO(
            s_name=form.S_Name.data,
            s_email=form.S_Email.data.lower(),
            s_pass=form.S_Pass.data,
            s_skills=form.S_Skills.data,
            s_mobile=form.S_Mobile.data,
            s_city=form.S_City.data
        )
        try:
            service_provider_dao.create(provider)
            return redirect(url_for('auth.slogin'))
        except Exception as e:
            flash('Email already taken.', 'danger')
            return redirect(url_for('auth.sregister'))

    return render_template("sregister.html", form=form)

@bp.route('/shome')
def shome():
    if 'user_id' in session:
        provider = service_provider_dao.get_by_id(session['user_id'])
        if provider:
            # Get pending appointment requests
            cursor = mysql.connection.cursor()
            cursor.execute("""
                SELECT * FROM appointment 
                WHERE service_provider_id = %s AND status = 'pending'
                ORDER BY appointment_date ASC
            """, (session['user_id'],))
            appointment_requests = cursor.fetchall()
            cursor.close()
            
            return render_template('shome.html', user=provider, appointment=appointment_requests)
    return redirect(url_for('auth.slogin'))

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.user'))

@bp.route('/profile')
def profile():
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor()
    try:
        # Try to get client profile first
        cursor.execute("""
            SELECT ID, Name, Email, Phone, City, photo
            FROM client 
            WHERE ID = %s
        """, (session['user_id'],))
        user = cursor.fetchone()
        
        if user:
            # Convert the result to a dictionary for easier template access
            user_data = {
                'id': user[0],
                'name': user[1],
                'email': user[2],
                'phone': user[3],
                'city': user[4],
                'photo': user[5] if len(user) > 5 else None,
                'user_type': 'client'
            }
            return render_template("profile.html", user=user_data)
        else:
            # If not found in client table, try service_provider table
            cursor.execute("""
                SELECT S_id, S_Name, S_Email, S_Mobile, S_City, photo, S_Skills
                FROM service_provider 
                WHERE S_id = %s
            """, (session['user_id'],))
            provider = cursor.fetchone()
            
            if provider:
                # Convert the result to a dictionary for easier template access
                user_data = {
                    'id': provider[0],
                    'name': provider[1],
                    'email': provider[2],
                    'phone': provider[3],
                    'city': provider[4],
                    'photo': provider[5] if len(provider) > 5 else None,
                    'skills': provider[6] if len(provider) > 6 else None,
                    'user_type': 'provider'
                }
                return render_template("profile.html", user=user_data)
        
        # If no user found
        flash("User not found", "danger")
        session.clear()  # Clear session as the user doesn't exist
        return redirect(url_for('auth.login'))
    except Exception as e:
        print(f"Error fetching profile: {str(e)}")
        flash("An error occurred while fetching your profile", "danger")
        return redirect(url_for('auth.home'))
    finally:
        cursor.close()

@bp.route('/upload_photo', methods=['POST'])
def upload_photo():
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('auth.login'))

    if 'photo' not in request.files:
        flash("No file selected", "danger")
        return redirect(url_for('auth.profile'))

    file = request.files['photo']
    if file.filename == '':
        flash("No file selected", "danger")
        return redirect(url_for('auth.profile'))

    if file and allowed_file(file.filename):
        try:
            # Read the file content
            photo_data = file.read()
            
            cursor = mysql.connection.cursor()
            try:
                # Try to update client table first
                cursor.execute("""
                    UPDATE client 
                    SET photo = %s 
                    WHERE ID = %s
                """, (photo_data, session['user_id']))
                
                if cursor.rowcount == 0:
                    # If not found in client table, try service_provider table
                    cursor.execute("""
                        UPDATE service_provider 
                        SET photo = %s 
                        WHERE S_id = %s
                    """, (photo_data, session['user_id']))
                
                mysql.connection.commit()
                flash("Photo uploaded successfully", "success")
            except Exception as e:
                mysql.connection.rollback()
                print(f"Error updating photo: {str(e)}")
                flash("An error occurred while updating the photo", "danger")
            finally:
                cursor.close()
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            flash("An error occurred while processing the photo", "danger")
    else:
        flash("Invalid file type", "danger")

    return redirect(url_for('auth.profile')) 