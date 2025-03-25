from flask import Blueprint, render_template, redirect, url_for, flash, session, request, jsonify
from com.DAO.admin_dao import AdminDAO
from com.DAO.client_dao import ClientDAO
from com.DAO.service_provider_dao import ServiceProviderDAO
from com.VO import AdminVO
from forms import Admin as AdminLoginForm, AdminRegistrationForm
from base import mysql
import bcrypt
import re

bp = Blueprint('admin', __name__)
admin_dao = AdminDAO()
client_dao = ClientDAO()
service_provider_dao = ServiceProviderDAO()

@bp.route("/AdMin", methods=["POST", "GET"])
def admin():
    form = AdminLoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data
        
        admin = admin_dao.get_by_email(email)
        if admin:
            try:
                # Use our safer verification method
                if admin_dao.verify_password(admin.password, password):
                    session['admin_id'] = admin.id
                    session['admin_email'] = admin.email
                    return redirect(url_for('admin.dashbord'))
                else:
                    flash("Invalid email or password", "danger")
            except Exception as e:
                # Handle any errors
                flash(f"Authentication error: {str(e)}. Please contact support.", "danger")
                print(f"Auth error details - Email: {email}, Password type: {type(admin.password)}, Error: {str(e)}")
        else:
            flash("Invalid email or password", "danger")
        
        return redirect(url_for('admin.admin'))

    return render_template("admin.html", form=form)

@bp.route('/dashbord')
def dashbord():
    if 'admin_id' not in session:
        flash("Please log in as an administrator", "warning")
        return redirect(url_for('admin.admin'))

    admin = admin_dao.get_by_id(session['admin_id'])
    if not admin:
        session.clear()
        flash("Admin not found", "danger")
        return redirect(url_for('admin.admin'))

    # Get statistics
    clients_count = client_dao.get_count()
    providers_count = service_provider_dao.get_count()
    
    # Get actual client and service provider data
    cursor = mysql.connection.cursor()
    
    # Fetch client data
    cursor.execute("SELECT * FROM client ORDER BY id DESC LIMIT 10")
    client_table = cursor.fetchall()
    
    # Fetch service provider data
    cursor.execute("SELECT * FROM service_provider ORDER BY S_id DESC LIMIT 10")
    service_provider = cursor.fetchall()
    
    # Fetch appointment data - fix the column name in ORDER BY clause
    try:
        # Try with ID (uppercase)
        cursor.execute("SELECT * FROM appointment ORDER BY ID DESC LIMIT 10")
        appointment = cursor.fetchall()
    except Exception as e:
        try:
            # Try with appointment_id
            cursor.execute("SELECT * FROM appointment ORDER BY appointment_id DESC LIMIT 10")
            appointment = cursor.fetchall()
        except Exception as e:
            # If both fail, just fetch without ordering
            cursor.execute("SELECT * FROM appointment LIMIT 10")
            appointment = cursor.fetchall()
    
    cursor.close()
    
    appointments = appointment  # For backward compatibility
    
    return render_template("dashbord.html", 
                          admin=admin,
                          clients_count=clients_count,
                          providers_count=providers_count,
                          appointments=appointments,
                          client_table=client_table,
                          service_provider=service_provider,
                          appointment=appointment)

@bp.route('/create_admin', methods=['GET', 'POST'])
def create_admin():
    # Check if admin is logged in
    if 'admin_id' not in session:
        flash("Please log in as an administrator", "warning")
        return redirect(url_for('admin.admin'))
    
    form = AdminRegistrationForm()
    if form.validate_on_submit():
        admin = AdminVO(
            name=form.name.data,
            email=form.email.data.lower(),
            password=form.password.data
        )
        
        try:
            admin_dao.create(admin)
            flash("Admin user created successfully", "success")
            return redirect(url_for('admin.admin_list'))
        except Exception as e:
            flash(f"Error creating admin: {str(e)}", "danger")
    
    return render_template("admin_create.html", form=form)

@bp.route('/admin_list')
def admin_list():
    # Check if admin is logged in
    if 'admin_id' not in session:
        flash("Please log in as an administrator", "warning")
        return redirect(url_for('admin.admin'))
    
    admins = admin_dao.get_all()
    return render_template("admin_list.html", admins=admins)

@bp.route('/update_admin', methods=['POST'])
def update_admin():
    # Check if admin is logged in
    if 'admin_id' not in session:
        return jsonify({"success": False, "message": "Not authorized"}), 401
    
    data = request.get_json()
    
    admin = AdminVO(
        id=session['admin_id'],
        email=data['email'],
        password=None  # Not updating password here
    )
    
    try:
        admin_dao.update(admin)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@bp.route('/change_password/<int:admin_id>', methods=['POST'])
def change_password(admin_id):
    # Check if admin is logged in
    if 'admin_id' not in session:
        flash("Please log in as an administrator", "warning")
        return redirect(url_for('admin.admin'))
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            flash("All fields are required", "danger")
            return redirect(url_for('admin.admin_list'))
            
        if new_password != confirm_password:
            flash("New passwords do not match", "danger")
            return redirect(url_for('admin.admin_list'))
            
        # Verify current password
        admin = admin_dao.get_by_id(session['admin_id'])
        try:
            # Use our safer verification method
            if admin_dao.verify_password(admin.password, current_password):
                # Update password
                admin_dao.update_password(admin_id, new_password)
                flash("Password updated successfully", "success")
                return redirect(url_for('admin.admin_list'))
            else:
                flash("Current password is incorrect", "danger")
                return redirect(url_for('admin.admin_list'))
        except Exception as e:
            # Log more details about the error
            print(f"Password change error - Admin ID: {admin_id}, Error: {str(e)}")
            flash(f"Authentication error: {str(e)}. Please contact support.", "danger")
            return redirect(url_for('admin.admin_list'))
    
    return render_template("change_password.html")

@bp.route('/logout')
def logout():
    """Logout the admin user"""
    # Clear the admin session
    session.pop('admin_id', None)
    session.pop('admin_email', None)
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('admin.admin'))

@bp.route('/setup_admin', methods=['GET', 'POST'])
def setup_admin():
    """Setup the first admin user - only works if no admin users exist"""
    
    # Check if any admin users exist
    admins = admin_dao.get_all()
    if admins and len(admins) > 0:
        flash("Admin setup is already completed", "warning")
        return redirect(url_for('admin.admin'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not name or not email or not password or not confirm_password:
            flash("All fields are required", "danger")
            return redirect(url_for('admin.setup_admin'))
            
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for('admin.setup_admin'))
        
        # Create admin
        try:
            # Create admin with DAO
            admin = AdminVO(name=name, email=email, password=password)
            admin_dao.create(admin)
            flash("Admin user created successfully! You can now log in.", "success")
            return redirect(url_for('admin.admin'))
        except Exception as e:
            print(f"Error creating admin: {str(e)}")
            flash(f"Error creating admin user: {str(e)}", "danger")
    
    return render_template("admin_setup.html")

@bp.route('/fix_admin_now', methods=['GET'])
def fix_admin_now():
    """Diagnostic route to debug admin authentication issues"""
    if request.args.get('secret') != 'debug123':
        return "Access denied", 403
    
    try:
        # Get all admin users for diagnostics
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Admin")
        admins = cursor.fetchall()
        
        # Check if we need to create a test admin
        if request.args.get('create') == 'yes':
            # Clear all existing admin records
            cursor.execute("DELETE FROM Admin")
            mysql.connection.commit()
            
            # Create fresh admin with known password
            password = "admin123"
            # Generate a proper bcrypt hash and store as string
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            hashed_str = hashed.decode('utf-8')
            
            # Store directly to avoid any issues with the DAO
            cursor.execute("INSERT INTO Admin(Email, Password) VALUES(%s, %s)",
                          ('admin@test.com', hashed_str))
            mysql.connection.commit()
            admin_id = cursor.lastrowid
            
            # Also add the admin with the credentials provided by the user
            user_email = "prajapatijaydip591@gmail.com"  # Fixed email with gmail.com
            user_password = "JAydip.m.p@2204"
            user_hashed = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())
            user_hashed_str = user_hashed.decode('utf-8')
            
            cursor.execute("INSERT INTO Admin(Email, Password) VALUES(%s, %s)",
                          (user_email, user_hashed_str))
            mysql.connection.commit()
            user_admin_id = cursor.lastrowid
            
            # Get updated admin records
            cursor.execute("SELECT * FROM Admin")
            admins = cursor.fetchall()
            
            success_message = f"""
            <h3>Created test admins:</h3>
            <p>Admin 1:</p>
            <p>- Email: admin@test.com</p>
            <p>- Password: admin123</p>
            <p>- ID: {admin_id}</p>
            <p>Admin 2:</p>
            <p>- Email: {user_email}</p>
            <p>- Password: {user_password}</p>
            <p>- ID: {user_admin_id}</p>
            <p><a href="{url_for('admin.admin')}">Go to login page</a></p>
            <hr>
            """
        else:
            success_message = ""
        
        output = "<h3>Admin Records:</h3>"
        for admin in admins:
            password_type = type(admin[2])
            password_length = len(str(admin[2]))
            password_value = str(admin[2])
            is_valid_hash = "No"
            
            # Check if it's a valid bcrypt hash
            if isinstance(admin[2], str) and re.match(r'^\$2[aby]\$\d+\$.{53}$', admin[2]):
                is_valid_hash = "Yes"
            
            output += f"""
            <p>ID: {admin[0]}</p>
            <p>Email: {admin[1]}</p>
            <p>Password type: {password_type}</p>
            <p>Password length: {password_length}</p>
            <p>Valid bcrypt hash: {is_valid_hash}</p>
            <p>Password start: {password_value[:20]}...</p>
            <hr>
            """
        
        cursor.close()
        
        output = success_message + output
        
        output += f"""
        <p><a href="{url_for('admin.fix_admin_now')}?secret=debug123&create=yes">Create fresh test admins</a></p>
        <p><a href="{url_for('admin.admin')}">Go to login page</a></p>
        """
            
        return output
    
    except Exception as e:
        return f"Error: {str(e)}" 