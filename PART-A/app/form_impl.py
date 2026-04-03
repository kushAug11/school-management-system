from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, EmailField
from wtforms.validators import DataRequired, Length, NumberRange, Regexp

class RegistrationForm(FlaskForm):
    # Depending on your app config, CSRF can be enabled.
    # Usually handled by configuring SECRET_KEY in Flask app.
    
    email = EmailField('Email', validators=[
        DataRequired(message="Email is required"), 
        Length(max=50, message="Email must be at most 50 characters")
    ])
    
    name = StringField('Name', validators=[
        DataRequired(message="Name is required"), 
        Length(max=100, message="Name must be at most 100 characters")
    ])
    
    dob = DateField('Date of Birth', format='%Y-%m-%d', validators=[
        DataRequired(message="Date of Birth is required")
    ])
    
    guardian_name = StringField('Guardian Name', validators=[
        DataRequired(message="Guardian Name is required"), 
        Length(max=100, message="Guardian Name must be at most 100 characters")
    ])
    
    guardian_contact = StringField('Guardian Contact', validators=[
        DataRequired(message="Guardian Contact is required"),
        Regexp(r'^[6-9]\d{9}$', message="Must be a 10 digit number starting with 6, 7, 8, or 9")
    ])
    
    language1 = IntegerField('Language 1', validators=[
        DataRequired(message="Language 1 score is required"), 
        NumberRange(min=70, max=100, message="Language 1 must be between 70 and 100")
    ])
    
    language2 = IntegerField('Language 2', validators=[
        DataRequired(message="Language 2 score is required"), 
        NumberRange(min=70, max=100, message="Language 2 must be between 70 and 100")
    ])
    
    math = IntegerField('Math', validators=[
        DataRequired(message="Math score is required"), 
        NumberRange(min=65, max=100, message="Math score must be between 65 and 100")
    ])
    
    science = IntegerField('Science', validators=[
        DataRequired(message="Science score is required"), 
        NumberRange(min=65, max=100, message="Science score must be between 65 and 100")
    ])
    
    history = IntegerField('History', validators=[
        DataRequired(message="History score is required"), 
        NumberRange(min=50, max=100, message="History score must be between 50 and 100")
    ])
    
    geography = IntegerField('Geography', validators=[
        DataRequired(message="Geography score is required"), 
        NumberRange(min=50, max=100, message="Geography score must be between 50 and 100")
    ])
