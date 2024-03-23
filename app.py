from flask import Flask, render_template, url_for, redirect,request,flash,abort,session,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user,current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,validators
from wtforms.validators import InputRequired, Length, ValidationError,EqualTo,Regexp,Email,DataRequired
from flask_bcrypt import Bcrypt,generate_password_hash,check_password_hash
from sqlalchemy import inspect,ForeignKey
import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField, FileRequired
from sqlalchemy import or_
from sqlalchemy.orm import relationship
from functools import wraps
from datetime import timedelta,datetime
import secrets
from flask_mail import Mail
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from itsdangerous import URLSafeTimedSerializer as Serializer
from itsdangerous import URLSafeTimedSerializer
from fuzzywuzzy import process,fuzz

app = Flask(__name__)

bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'bibekrai655@gmail.com'
app.config['MAIL_PASSWORD'] = 'piux zeri dtsy dyxj'
app.config['MAIL_DEFAULT_SENDER'] = 'bibekrai655@gmail.com'

mail = Mail(app)


db = SQLAlchemy(app)
app.app_context().push()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

saved_events = db.Table('saved_events',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True)
)
posted_events = db.Table('user_posted_events',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    saved_events = db.relationship('Event', secondary=saved_events, backref='saved_by')
    posted_events = db.relationship('Event', secondary=posted_events, backref='posted_by')

class SavedEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

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
    image_path = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User',backref=db.backref('events', lazy=True))

    @staticmethod
    def get_similar_events(event_title, limit=3):
        
        all_events = Event.query.filter(Event.eventname != event_title).all()

        
        event_titles = [e.eventname for e in all_events]

        # Use FuzzyWuzzy to find similar event titles
        title_matches = process.extract(event_title, event_titles, limit=limit)

        # Retrieve similar events based on matched titles
        similar_events = [event for (title, score) in title_matches for event in all_events if event.eventname == title]

        return similar_events


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

class UpdatePasswordForm(FlaskForm):
    email = StringField('Email', validators=[validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', validators=[validators.DataRequired(), validators.Length(min=8)])


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


class EventForm(FlaskForm):
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
    image = FileField(validators=[FileRequired()])
 

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
    
        
    

@app.route('/')

def home():
    app.permanent_session_lifetime = timedelta(seconds=600)
    events=Event.query.all()

    #for datetime

    all_events = Event.query.all()
    today=datetime.today().date()

    for event in all_events:
        event.date = datetime.strptime(event.date, '%Y-%m-%d').date()

    today_events = [event for event in all_events if event.date == today]
    past_events = [event for event in all_events if event.date < today]
    upcoming_events = [event for event in all_events if event.date > today]

    return render_template('home.html',events=events,today_events=today_events,past_events=past_events,upcoming_events=upcoming_events)


@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

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

@app.route('/save_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def save_event(event_id):
    event = Event.query.get_or_404(event_id)
    user = current_user

    
    if event in user.saved_events:
        flash('Event already saved.', 'warning')
    else:
        user.saved_events.append(event)
        db.session.commit()
        flash('Event saved successfully!', 'success')

    return redirect(url_for('dashboard', event_id=event.id,saved=True))

@app.route('/posted_events')
@login_required
def posted_events():
    
    posted_events = current_user.posted_events
    return render_template('profile.html', posted_events=posted_events)



@app.route('/remove_saved_event/<int:event_id>', methods=['POST'])
@login_required
def remove_saved_event(event_id):
    event = Event.query.get_or_404(event_id)
    user = current_user

    if event in user.saved_events:
        user.saved_events.remove(event)
        db.session.commit()
        flash('Event removed from saved events successfully!', 'success')
    else:
        flash('Event not found in saved events.', 'warning')

    return redirect(url_for('profile', user_id=user.id))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():  
    events = Event.query.all()

    #for datetime

    all_events = Event.query.all()
    today=datetime.today().date()

    for event in all_events:
        event.date = datetime.strptime(event.date, '%Y-%m-%d').date()
        
    today_events = [event for event in all_events if event.date == today]
    past_events = [event for event in all_events if event.date < today]
    upcoming_events = [event for event in all_events if event.date > today]

    return render_template('dashboard.html', events=events,today_events=today_events,past_events=past_events,upcoming_events=upcoming_events)


@app.route('/profile/<int:user_id>',methods=['GET','POST'])
@login_required
def profile(user_id):
    if current_user.id != user_id:
        abort(403)  
    
    user = User.query.get_or_404(user_id)
    posted_events = user.posted_events
    saved_events = user.saved_events
    return render_template('profile.html', user=user, saved_events=saved_events,posted_events=posted_events)


@app.route('/event_details/<int:event_id>')
def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    saved_message = None

    similar_events = Event.get_similar_events(event.eventname)

    if current_user.is_authenticated:
        if request.method == 'POST':
            if event in current_user.saved_events:
                saved_message = 'Event already saved.'
            else:
                current_user.saved_events.append(event)
                db.session.commit()
                saved_message = 'Event saved successfully!'

    return render_template('event_details.html', event=event, saved_message=saved_message,similar_events=similar_events)

@app.route('/filter', methods=['GET', 'POST'])
def filter_events():
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
       
        filtered_events = Event.query.filter(Event.date.between(start_date, end_date)).all()
        
        return render_template('filter_results.html', events=filtered_events)
    
    return render_template('filter.html')


@app.route('/event/delete/<int:event_id>', methods=['POST', 'DELETE'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user.id!=event.user_id:
        abort(403)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    error_message = None
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
            token = s.dumps(email, salt='forgot-password')
            reset_link = url_for('update_password', token=token, _external=True)

            send_reset_email(email, reset_link)
            flash('Password reset email sent. Please check your inbox.', 'info')
            return redirect(url_for('login'))
        else:
            error_message = 'Email address not found. Please provide a registered email address.'
    
    return render_template('forgot_password.html',error_message=error_message)

@app.route('/update_password/<token>', methods=['GET', 'POST'])
def update_password(token):
    form = UpdatePasswordForm()
    if request.method == 'POST':
        new_password = request.form.get('new-password')
        confirm_password = request.form.get('confirm-password')

       
        if new_password != confirm_password:
            flash('New password and confirm password do not match.', 'error')
            return redirect(url_for('update_password', token=token))

        if len(new_password) < 8:
            flash('New password must be at least 8 characters long.', 'error')
            return redirect(url_for('update_password', token=token))

        s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        try:
            email = s.loads(token, salt='forgot-password', max_age=1800)  
        except:
            flash('Invalid or expired token.', 'error')
            return redirect(url_for('forgot_password'))

        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(new_password)
            db.session.commit()
            flash('Password updated successfully.', 'success')
            return redirect(url_for('login'))
        else:
            flash('User not found.', 'error')
            return redirect(url_for('forgot_password'))

    return render_template('update_password.html', token=token)


def send_reset_email(email, reset_link):
    
    from flask_mail import Mail, Message
    mail = Mail(app)
    msg = Message('Password Reset', recipients=[email])
    msg.body = f'Click the following link to reset your password: {reset_link}'
    mail.send(msg)

@app.route('/update_event/<int:event_id>', methods=['GET','POST'])
@login_required
def update_event_page(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user.id!=event.user_id:
        abort(403)
    if request.method == 'POST':
        
        event.eventname = request.form['eventname']
        event.duration = request.form['duration']
        event.date = request.form['date']
        event.location = request.form['location']
        event.time = request.form['time']
        event.organizer = request.form['organizer']
        event.contactorganizer = request.form['contactorganizer']
        event.description = request.form['description']

        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename != '':
                
                filename = secure_filename(image_file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image_file.save(image_path)
                event.image_path = filename

        db.session.commit()
        return redirect(url_for('event_details', event_id=event.id))
    return render_template('update_event.html', event=event)

    


@app.route('/search', methods=['POST'])
def search():
    search_query = request.form['search_query'].lower()  
    events = Event.query.filter(Event.eventname.ilike(f"%{search_query}%")).all()
    
    return render_template('search_results.html', search_query=search_query, events=events)


    
@app.route('/post_event', methods=['GET', 'POST'])
@login_required
def post_event():
    form = EventForm()
    if form.validate_on_submit():
        image_file = form.image.data
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(image_path)
        user_id = current_user.id
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
            
            image_path=filename,
            user_id=user_id
                       
        )
        
        db.session.add(event)
        current_user.posted_events.append(event)
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