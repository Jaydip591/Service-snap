from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, BooleanField, SubmitField,SelectField,TextAreaField
from wtforms.validators import email,DataRequired,length,EqualTo
from flask_wtf.file import FileField,file_allowed
class Registrationform(FlaskForm):
    name= StringField('name', validators=[DataRequired(), length(min=4 , max=20)])
    email= EmailField('Email', validators=[DataRequired(), email()])
    Mobile = StringField('Mobile', validators=[DataRequired(), length(min=10, max=10)])
    password = PasswordField('Password', validators=[DataRequired() ])
    submit = SubmitField('Register')

class ServiceProviderRegistrationForm(FlaskForm):
    S_Name = StringField('Name', validators=[DataRequired(), length(min=4, max=100)])
    S_Email = EmailField('Email', validators=[DataRequired(), email()])
    S_Pass = PasswordField('Password', validators=[DataRequired()])
    S_Skills = SelectField('Skills', choices=[('Plumbing', 'Plumbing'),('Electrician', 'Electrician'), ('Mechanic', 'Mechanic'), ('Carpentry', 'Carpentry'), ('AC Repair', 'AC Repair'), ('Cleaning', 'Cleaning')], validators=[DataRequired()])
    S_Mobile = StringField('Mobile', validators=[DataRequired(), length(min=10, max=10)])
    S_City = StringField('City', validators=[DataRequired(), length(min=3, max=30)])
    S_submit = SubmitField('Register')
    
class Loginform(FlaskForm):
    email= EmailField('Email', validators=[DataRequired(), email()])
    password = PasswordField('Password', validators=[DataRequired() ])
    Remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
    
class ServiceProviderloginform(FlaskForm):
    S_Email= EmailField('Email', validators=[DataRequired(), email()])
    S_Pass = PasswordField('Password', validators=[DataRequired()])
    Remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class Admin(FlaskForm):
    email= EmailField('Email', validators=[DataRequired(), email()])
    password = PasswordField('Password', validators=[DataRequired() ])
    Remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class AdminRegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), length(min=3, max=100)])
    email = EmailField('Email', validators=[DataRequired(), email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        length(min=8, message="Password must be at least 8 characters long")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Create Admin')
    
class accountupdateform(FlaskForm):
    picture = FileField(label="profile_picture",validators=[file_allowed(['jpg','png'])])
    submit=SubmitField('submit')
    
class RequestForm(FlaskForm):
    provider_id = StringField('Provider ID', validators=[DataRequired()])
    service_description = TextAreaField('Service Description', validators=[DataRequired()])
    submit = SubmitField('Request Service')