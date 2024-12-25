from flask import Flask, render_template,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,SubmitField
from wtforms.validators import Length,Email,EqualTo,DataRequired,ValidationError
from flask_bcrypt import Bcrypt
from flask_login import LoginManager,login_user,UserMixin
import os
secret_key = os.urandom(24).hex()  

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/marketdb?charset=utf8mb4&connect_timeout=10'
app.config['SECRET_KEY'] = 'secret_key'

bcrypt=Bcrypt(app)
db = SQLAlchemy(app)
login_manager=LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/')
@app.route('/home')
def homepage():
    return render_template('homepage.html')

class Users(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    budget = db.Column(db.Integer, default=1000)
    items = db.relationship('Items', backref='owned_user', lazy=True)

    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self,plain_text_password):
        self.password_hash=bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
    
    def check_password(self,attempted_password):
        return bcrypt.check_password_hash(self.password_hash,attempted_password)
    
class Items(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    barcode = db.Column(db.String(12), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'))

   
@app.route('/assign_owner')
def assign_owner():
    user = Users.query.first() 
    item = Items.query.first()  

    if user and item:  
        item.owner = user.id  
        db.session.commit() 
        return f"Owner assigned: {user.user_name} is now the owner of {item.name}."
    
    return "User or Item not found."

@app.route('/market')
def marketpage():
    items = Items.query.all()  
    return render_template('market.html', item=items)  

class Registerform(FlaskForm):
    def validate_user_name(self,form_user_name):
        valid_user=Users.query.filter_by(user_name=form_user_name.data).first()
        if valid_user:
            raise ValidationError('user name already exits')
        
    def validate_email(self,form_email):
        valid_user=Users.query.filter_by(email=form_email.data).first()
        if valid_user:
            raise ValidationError('Email address already exists')

    user_name=StringField(label='User name',validators=[Length(min=3,max=20),DataRequired()])
    email=StringField(label='email address',validators=[Email(),DataRequired()])
    password1=PasswordField(label='password',validators=[Length(min=3),DataRequired()])
    password2=PasswordField(label='Conform password',validators=[EqualTo('password1'),DataRequired()])
    submit=SubmitField(label='Create account')

@app.route('/register',methods=['GET','POST'])
def registerpage():
    form=Registerform()
    if form.validate_on_submit():
        temp_user=Users(user_name=form.user_name.data,email=form.email.data,password=form.password1.data)
        db.session.add(temp_user)
        db.session.commit()
        return redirect(url_for('marketpage'))
    if form.errors!={}:
        for err_msg in form.errors.values():
            flash(f'Note : {err_msg}',category='danger')
    return render_template('registerpage.html',form=form)

class Loginform(FlaskForm):
    user_name=StringField(label='user name',validators=[DataRequired()])
    password=PasswordField(label='password',validators=[DataRequired()])
    submit=SubmitField(label='login')

@app.route('/login',methods=['GET','POST'])  
def loginpage():
    form=Loginform()
    if form.validate_on_submit():
        temp_user=Users.query.filter_by(user_name=form.user_name.data).first()
        if temp_user and temp_user.check_password(attempted_password=form.password.data):
            login_user(temp_user)
            flash(f'login successfully!, hi {temp_user.user_name}',category='success')
            return redirect (url_for('marketpage'))
        else:
            flash('invaild user_name and password',category='danger')
    return render_template('login.html',form=form)  

if __name__ == '__main__':
    app.run(debug=True)
