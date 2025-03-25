from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app, send_file
from com.DAO.service_provider_dao import ServiceProviderDAO
from com.DAO.client_dao import ClientDAO
from com.VO import AppointmentVO
from base import mysql
import bcrypt
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from io import BytesIO

bp = Blueprint('service', __name__)
service_provider_dao = ServiceProviderDAO()
client_dao = ClientDAO()

# Configure upload folder for user photos
UPLOAD_FOLDER = 'base/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/service_providers')
def service_providers():
    # Check if user is logged in
    if 'user_id' not in session:
        flash("Please login to view service providers", "warning")
        return redirect(url_for('auth.login'))
        
    providers = service_provider_dao.get_all()
    return render_template("service_providers.html", providers=providers)

@bp.route('/services', methods=['GET', 'POST'])
def services():
    # Check if user is logged in
    if 'user_id' not in session:
        flash("Please login to access services", "warning")
        return redirect(url_for('auth.login'))
        
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT DISTINCT S_City FROM service_provider")
    cities = [row[0] for row in cursor.fetchall()]
    cursor.close()

    if request.method == "POST":
        selected_city = request.form.get("city")
    elif 'user_id' in session:
        user = client_dao.get_by_id(session['user_id'])
        selected_city = user.city if user else None
    else:
        selected_city = None

    service_providers = []
    if selected_city:
        service_providers = service_provider_dao.get_by_city(selected_city)
    else:
        service_providers = service_provider_dao.get_all()

    # Debug print
    print("Selected City:", selected_city)
    print("Number of providers:", len(service_providers))
    for provider in service_providers:
        print(f"Provider: id={provider.s_id}, name={provider.s_name}, city={provider.s_city}")
        print(f"Provider attributes: {dir(provider)}")

    return render_template("service_listing.html", 
                         cities=cities, 
                         selected_city=selected_city, 
                         providers=service_providers,
                         client_id=session.get('user_id'),
                         now=datetime.now())

@bp.route('/submit_appointment', methods=['POST'])
def submit_appointment():
    if 'user_id' not in session:
        flash("Please login first to request a service", "warning")
        return redirect(url_for('auth.login'))

    service_provider_id = request.form.get('service_provider_id')
    service_date = request.form.get('appointment_date')
    service_time = request.form.get('appointment_time')
    email = request.form.get('email')
    address = request.form.get('address')
    description = request.form.get('description', '')  # New field for service description

    # Debug print
    print(f"Received data: provider_id={service_provider_id}, date={service_date}, time={service_time}, email={email}, address={address}")

    # Validate required fields
    if not all([service_provider_id, service_date, service_time, email, address]):
        flash("All fields are required. Please fill in all the information.", "danger")
        return redirect(url_for('service.services'))

    # Validate date is not in the past
    appointment_datetime = datetime.strptime(f"{service_date} {service_time}", "%Y-%m-%d %H:%M")
    if appointment_datetime < datetime.now():
        flash("Appointment date and time cannot be in the past.", "danger")
        return redirect(url_for('service.services'))

    cursor = mysql.connection.cursor()
    try:
        # Check if the service provider exists
        cursor.execute("SELECT S_id FROM service_provider WHERE S_id = %s", (service_provider_id,))
        if not cursor.fetchone():
            flash("Invalid service provider selected.", "danger")
            return redirect(url_for('service.services'))

        # Check if the client exists and get their ID
        cursor.execute("SELECT ID FROM client WHERE ID = %s", (session['user_id'],))
        client = cursor.fetchone()
        if not client:
            flash("Invalid client ID. Please login again.", "danger")
            session.clear()
            return redirect(url_for('auth.login'))

        client_id = int(client[0])  # Ensure client_id is an integer

        # Check for existing appointments at the same time
        cursor.execute("""
            SELECT COUNT(*) FROM appointment 
            WHERE service_provider_id = %s 
            AND appointment_date = %s 
            AND appointment_time = %s
            AND status != 'rejected'
        """, (service_provider_id, service_date, service_time))
        if cursor.fetchone()[0] > 0:
            flash("This time slot is already booked. Please select a different date/time.", "warning")
            return redirect(url_for('service.services'))

        # Insert the appointment with status 'pending'
        cursor.execute("""
            INSERT INTO appointment (client_id, service_provider_id, appointment_date, appointment_time, 
                                   email, address, description, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')
        """, (client_id, service_provider_id, service_date, service_time, email, address, description))
        
        mysql.connection.commit()
        flash("Service request submitted successfully! The service provider will review your request.", "success")
    except Exception as e:
        mysql.connection.rollback()
        print(f"Detailed error: {str(e)}")
        print(f"Error type: {type(e)}")
        flash(f"An error occurred: {str(e)}", "danger")
    finally:
        cursor.close()

    return redirect(url_for('service.services'))

@bp.route('/provider/requests')
def provider_requests():
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor()
    try:
        # Get all pending requests for this service provider
        cursor.execute("""
            SELECT a.*, c.Name as client_name, c.Email as client_email, c.Phone as client_phone
            FROM appointment a
            JOIN client c ON a.client_id = c.ID
            WHERE a.service_provider_id = %s
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """, (session['user_id'],))
        requests = cursor.fetchall()
        
        return render_template("provider_requests.html", requests=requests)
    except Exception as e:
        print(f"Error fetching requests: {str(e)}")
        flash("An error occurred while fetching requests", "danger")
        return redirect(url_for('service.services'))
    finally:
        cursor.close()

@bp.route('/provider/respond_request', methods=['POST'])
def respond_request():
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('auth.login'))

    appointment_id = request.form.get('appointment_id')
    action = request.form.get('action')  # 'accept' or 'reject'
    response_message = request.form.get('response_message', '')

    if not appointment_id or not action:
        flash("Invalid request", "danger")
        return redirect(url_for('service.provider_requests'))

    cursor = mysql.connection.cursor()
    try:
        # Verify the appointment belongs to this service provider
        cursor.execute("""
            SELECT * FROM appointment 
            WHERE appointment_id = %s AND service_provider_id = %s
        """, (appointment_id, session['user_id']))
        
        if not cursor.fetchone():
            flash("Invalid appointment", "danger")
            return redirect(url_for('service.provider_requests'))

        # Update the appointment status
        status = 'accepted' if action == 'accept' else 'rejected'
        cursor.execute("""
            UPDATE appointment 
            SET status = %s, response_message = %s
            WHERE appointment_id = %s
        """, (status, response_message, appointment_id))
        
        mysql.connection.commit()
        flash(f"Request {status} successfully", "success")
    except Exception as e:
        mysql.connection.rollback()
        print(f"Error updating request: {str(e)}")
        flash("An error occurred while updating the request", "danger")
    finally:
        cursor.close()

    return redirect(url_for('service.provider_requests'))

@bp.route('/client/requests')
def client_requests():
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor()
    try:
        # Get all requests for this client
        cursor.execute("""
            SELECT a.*, sp.s_name as provider_name, sp.s_email as provider_email, sp.s_mobile as provider_phone
            FROM appointment a
            JOIN service_provider sp ON a.service_provider_id = sp.s_id
            WHERE a.client_id = %s
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """, (session['user_id'],))
        requests = cursor.fetchall()
        
        return render_template("client_requests.html", requests=requests)
    except Exception as e:
        print(f"Error fetching requests: {str(e)}")
        flash("An error occurred while fetching requests", "danger")
        return redirect(url_for('service.services'))
    finally:
        cursor.close()

@bp.route('/get_photo/<int:user_id>')
def get_photo(user_id):
    cursor = mysql.connection.cursor()
    try:
        # Try to get photo from client table first
        cursor.execute("SELECT photo FROM client WHERE ID = %s", (user_id,))
        result = cursor.fetchone()
        
        if result and result[0]:
            return send_file(
                BytesIO(result[0]),
                mimetype='image/jpeg'
            )
        
        # If not found in client table, try service_provider table
        cursor.execute("SELECT photo FROM service_provider WHERE S_id = %s", (user_id,))
        result = cursor.fetchone()
        
        if result and result[0]:
            return send_file(
                BytesIO(result[0]),
                mimetype='image/jpeg'
            )
        
        # If no photo found, return default image
        return send_file(
            'base/static/images/default-avatar.png',
            mimetype='image/png'
        )
    finally:
        cursor.close()

@bp.route('/upload_photo', methods=['POST'])
def upload_photo():
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('auth.profile'))

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