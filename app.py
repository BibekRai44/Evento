from flask import Flask, render_template, url_for, redirect,request,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user,current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError,EqualTo,Regexp
from flask_bcrypt import Bcrypt
from sqlalchemy import inspect
import os
app = Flask(__name__)

bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eventname = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1024), nullable=False)
    time = db.Column(db.String(100), nullable=False)
    organizer = db.Column(db.String(100), nullable=False)
    contactorganizer = db.Column(db.String(100), nullable=False)
    tags = db.Column(db.String(100), nullable=False)

db.create_all()

inspector = inspect(db.engine)
if 'event' in inspector.get_table_names():
    print("Event table exists in the database.")
else:
    print("Event table does not exist in the database.")
    
class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)])
    email = StringField(validators=[
                        InputRequired(), Length(min=4, max=120)])

    password = PasswordField(validators=[
                             InputRequired()])
    confirm_password = PasswordField(validators=[
                             InputRequired(), EqualTo('password', message='Passwords must match')])

    submit = SubmitField('Register')


    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')
        
    def validate_email(self, email):
        existing_user_email = User.query.filter_by(
            email=email.data).first()
        if existing_user_email:
            raise ValidationError(
                'That email address is already registered.')
        
class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


class eventForm(FlaskForm):
    eventname = StringField(validators=[
                           InputRequired(), Length(min=4, max=255)], render_kw={"placeholder": "Event Name"})

    duration = StringField(validators=[
                           InputRequired(), Length(min=4, max=100)], render_kw={"placeholder": "Duration"})

    date = StringField(validators=[
                           InputRequired(), Length(min=4, max=100)], render_kw={"placeholder": "Date"})

    location = StringField(validators=[
                           InputRequired(), Length(min=4, max=100)], render_kw={"placeholder": "Location"})

    description = StringField(validators=[
                           InputRequired(), Length(min=4, max=1024)], render_kw={"placeholder": "Description"})
    organizer = StringField(validators=[
                           InputRequired(), Length(min=4, max=100)], render_kw={"placeholder": "Organizer"})
    contactorganizer = StringField(validators=[
                           InputRequired(), Length(min=4, max=100)], render_kw={"placeholder": "Contact Organizer"})
    time=StringField(validators=[
                           InputRequired(), Length(min=4, max=100)], render_kw={"placeholder": "Time"})
    tags=StringField(validators=[
                           InputRequired(), Length(min=4, max=100)], render_kw={"placeholder": "Tags"})
 

    submit = SubmitField('Post Event')

    def validate_eventname(self, eventname):
        existing_eventname = Event.query.filter_by(
            eventname=eventname.data).first()
        
    def validate_duration(self, duration):
        existing_duration = Event.query.filter_by(
            duration=duration.data).first()
        
    
    def validate_time(self, time):
        existing_time = Event.query.filter_by(
            time=time.data).first()
        

    def validate_date(self, date):
        existing_date = Event.query.filter_by(
            date=date.data).first()
        

    def validate_location(self, location):
        existing_location = Event.query.filter_by(
            location=location.data).first()
        
    
    def validate_organizer(self, organizer):
        existing_organizer = Event.query.filter_by(
            organizer=organizer.data).first()
    
    def validate_contactorganizer(self, contactorganizer):
        existing_contactorganizer = Event.query.filter_by(
            contactorganizer=contactorganizer.data).first()
        

    def validate_description(self, description):
        existing_description = Event.query.filter_by(
            description=description.data).first()
    
    def validate_tags(self, tags):
        existing_tags = Event.query.filter_by(
            tags=tags.data).first()
        
        
    

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/postevent')
def postevent():
    return render_template('login.html')


@app.route('/service')
def service():
    return render_template('service.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html', form=form)


@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():  
    events = Event.query.all()
    return render_template('dashboard.html', events=events)

#@app.route('/update_event_submit',methods=['GET','POST'])
#@login_required
#def update_event_submit():
    #return render_template('update_event.html')

@app.route('/event_details/<int:event_id>')
def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('event_details.html', event=event)

@app.route('/filter', methods=['GET', 'POST'])
def filter_events():
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        # Query the database to filter events based on the date range
        filtered_events = Event.query.filter(Event.date.between(start_date, end_date)).all()
        
        return render_template('filter_results.html', events=filtered_events)
    
    return render_template('filter.html')


@app.route('/event/delete/<int:event_id>', methods=['POST', 'DELETE'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/update_event/<int:event_id>', methods=['GET','POST'])
def update_event_page(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        # Handle the form submission
        event.eventname = request.form['eventname']
        event.duration = request.form['duration']
        event.date = request.form['date']
        event.location = request.form['location']
        event.time = request.form['time']
        event.organizer = request.form['organizer']
        event.contactorganizer = request.form['contactorganizer']
        event.tags = request.form['tags']
        event.description = request.form['description']
        db.session.commit()
        return redirect(url_for('event_details', event_id=event.id))
    return render_template('update_event.html', event=event)

    


@app.route('/search', methods=['POST'])
def search():
    search_query = request.form['search_query']
    events = Event.query.filter(Event.tags.contains(search_query)).all()
    return render_template('search_results.html', events=events, search_query=search_query)


@app.route('/post_event', methods=['GET', 'POST'])
@login_required
def post_event():
    form = eventForm()
    
    if form.validate_on_submit():
        print("Form data:", request.form)
        event = Event(
            eventname=form.eventname.data,
            duration=form.duration.data,
            date=form.date.data,
            location=form.location.data,
            description=form.description.data,
            time=form.time.data,
            organizer=form.organizer.data,
            contactorganizer=form.contactorganizer.data,
            tags=form.tags.data
            
        )
        db.session.add(event)
        db.session.commit()
        flash('Event posted successfully!', 'success')
        return redirect(url_for('dashboard'))
    else:
        print("Form validation failed. Errors:", form.errors)
    return render_template('post_event.html', form=form)

@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password,email=form.email.data)
        db.session.add(new_user)
        db.session.commit()
        flash('User registration successful. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

if __name__ == "__main__":
    app.run(debug=True)