from flask import Flask, render_template, request, flash, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_session import Session
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FloatField
from wtforms.validators import DataRequired
import base64
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import numpy as np
import joblib


app = Flask(__name__, static_folder='static')

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


app.config['SECRET_KEY'] = '4046bde895cc19ca9cbd373a'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:admin123@localhost/malnutritiondb'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER) 

db = SQLAlchemy(app)
migrate = Migrate(app, db)
Session(app)

# # Example function to train and save the model
# def train_and_save_model(data_path):
#     df = pd.read_csv(data_path)
#     X = df[['weight', 'height', 'age']]  # assuming these columns exist
#     y = df['malnutrition_risk']  # assuming this is the target column
    
#     # Preprocess the data (scaling)
#     scaler = StandardScaler()
#     X_scaled = scaler.fit_transform(X)
    
#     # Train the logistic regression model
#     model = LogisticRegression()
#     model.fit(X_scaled, y)
    
#     # Save the model and scaler
#     joblib.dump(model, 'malnutrition_model.pkl')
#     joblib.dump(scaler, 'scaler.pkl')

# Call this function with the path to your dataset
# train_and_save_model('Dataset1.csv')

def save_profile_picture(file, user_id):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_prefix = f"{user_id}_{int(datetime.now().timestamp())}"
        filename = f"{unique_prefix}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return os.path.join('images', filename)  # This path is stored in the database
    return None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Load the dataset
# def load_data(filepath):
#     return pd.read_csv(filepath)

# # Preprocess the data
# def preprocess_data(df):
#     scaler = StandardScaler()
#     features = ['weight', 'height', 'age']
#     df[features] = scaler.fit_transform(df[features])
#     return df, scaler

# # Train the model
# def train_model(df):
#     X = df[['weight', 'height', 'age']]
#     y = df['malnutrition_risk']  # Assuming there is a 'malnutrition_risk' column in your dataset
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#     model = LogisticRegression()
#     model.fit(X_train, y_train)
#     print(f"Model accuracy on test set: {model.score(X_test, y_test)}")
#     return model

# # Main function to tie it all together
# def main(filepath):
#     df = load_data(filepath)
#     df, scaler = preprocess_data(df)
#     model = train_model(df)
#     # Example prediction
#     print(predict_malnutrition(model, scaler, 10, 90, 24))

# # Prediction function
# def predict_malnutrition(weight, height, age):
#     features = np.array([[weight, height, age]])
#     features_scaled = scaler.transform(features)
#     risk = model.predict(features_scaled)[0]
#     return risk

# User Class
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(255), nullable=False)
    lname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    pbday = db.Column(db.Date)
    pnumber = db.Column(db.String(20), nullable=False, unique=True)  # Changed to String
    edu = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Integer, default=0, nullable=False)
    profile_picture = db.Column(db.Text)  # Large text field for Base64 image data

    def __repr__(self):
        return f'User("{self.id}", "{self.fname}", "{self.lname}", "{self.pbday}", "{self.edu}", "{self.status}")'

# Child Class
class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable = False)
    height = db.Column(db.Float, nullable = False)
    guardian_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Assuming a foreign key from a user table

    def __repr__(self):
        return f'<Child {self.first_name} {self.last_name}>'

class ChildForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    weight = FloatField('Weight', validators=[DataRequired()])
    height = FloatField('Height', validators=[DataRequired()])
    submit = SubmitField('Predict Malnutrition Risk')

# create admin Class
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'Admin("{self.username}","{self.id}")'

# Function to create db tables
def create_db_tables():
    with app.app_context():
        db.create_all()

# Create table
create_db_tables()

# # Initialize and train your model here (or load a pre-trained model)
# model = LogisticRegression()

# insert admin data one time only one time insert this data
# latter will check the condition
# @app.before_request
# def insert_admin():
#     try:
#         if not Admin.query.first():
#             admin = Admin(username='bsisthesis123', password='adminthesis2024')
#             db.session.add(admin)
#             db.session.commit()
#             print("Admin data inserted successfully")
#         else:
#             print("Admin data already exists")
#     except Exception as e:
#         print(f"Error occurred while inserting admin data: {str(e)}")

# Main index page
@app.route('/')
def index():
    return render_template('index.html')

#-------------------------Admin Area---------------------------------------

# Admin login
@app.route('/admin/', methods=["POST", "GET"])
def adminIndex():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('Please fill all the field', 'danger')
            return redirect('/admin/')
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.password == password:
            session['admin_id'] = admin.id
            session['admin_name'] = admin.username
            flash('Login Successfully', 'success')
            return redirect('/admin/dashboard')
        else:
            flash('Invalid Username and Password', 'danger')
            return redirect('/admin/')
    return render_template('admin/index.html', title = "Admin Login")

# Admin Dashboard
@app.route('/admin/dashboard')
def adminDashboard():
    if not session.get('admin_id'):
        return redirect('/admin/')
    
    users = User.query.all()  # Fetch all users
    totalUser = len(users)
    totalApprove = sum(1 for user in users if user.status == 1)
    NotTotalApprove = totalUser - totalApprove
    for user in users:
        print(user.profile_picture)  # Debug output
    
    return render_template('admin/dashboard.html', totalUser=totalUser, totalApprove=totalApprove, NotTotalApprove=NotTotalApprove, users=users)


# Admin get all user 
@app.route('/admin/get-all-user', methods=["POST","GET"])
def adminGetAllUser():
    if not session.get('admin_id'):
        return redirect('/admin/')
    if request.method== "POST":
        search=request.form.get('search')
        users=User.query.filter(User.username.like('%'+search+'%')).all()
        users=User.query.filter(User.email.like('%'+search+'%')).all()
        users=User.query.filter(User.edu.like('%'+search+'%')).all()
        users=User.query.filter(User.fname.like('%'+search+'%')).all()
        users=User.query.filter(User.lname.like('%'+search+'%')).all()
        return render_template('admin/all-user.html',title='Approve User',users=users)
    else:
        users=User.query.all()
        return render_template('admin/all-user.html',title='Approve User',users=users)

# Admin User Approval
@app.route('/admin/approve-user/<int:id>')
def adminApprove(id):
    if not session.get('admin_id'):
        return redirect('/admin/')
    User().query.filter_by(id=id).update(dict(status=1))
    db.session.commit()
    flash('User account creation approved.','success')
    return redirect('/admin/get-all-user')

# Admin Change Password
@app.route('/admin/change-admin-password', methods=["POST", "GET"])
def adminChangePassword():
    admin = Admin.query.get(1)  # Ensure you are fetching the correct admin based on your application logic
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == "" or password == "":
            flash('Please fill the field', 'danger')
            return redirect('/admin/change-admin-password')
        else:
            # Update the admin password as plain text
            Admin.query.filter_by(username=username).update(dict(password=password))
            db.session.commit()
            flash('Admin Password update successfully', 'success')
            return redirect('/admin/change-admin-password')
    else:
        return render_template('admin/admin-change-password.html', title='Admin Change Password', admin=admin)


# admin logout
@app.route('/admin/logout')
def adminLogout():
    if not session.get('admin_id'):
        return redirect('/admin/')
    if session.get('admin_id'):
        session['admin_id']=None
        session['admin_name']=None
        return redirect('/')

#--------------------------------user content--------------------------------

# User login
@app.route('/user/', methods=['POST', 'GET'])
def userIndex():
    if  session.get('user_id'):
        return redirect('/user/dashboard')
    if request.method=="POST":
        # get name of the field
        email = request.form.get('email')
        password = request.form.get('password')
        
        # checks if user exists in this email or not
        users = User().query.filter_by(email = email).first()
        if users and users.password == password:
            # check the admin approval
            is_approve = User.query.filter_by(id=users.id).first()
            if is_approve.status == 0:
                flash('Account not yet approved by Admin.', 'warning')
                return redirect ('/user/')
            else:
                session['user_id'] = users.id
                session['username'] = users.username
                flash('Logged in successfully.', 'success')
                return redirect ('/user/dashboard')
        else:
            flash('Invalid Email or Password.', 'danger')
            return redirect ('/user/')
    else:
        return render_template('user/index.html', title="User Login")

# User registration
@app.route('/user/signup', methods=['POST', 'GET'])
def userSignup():
    if 'user_id' in session:
        return redirect(url_for('userDashboard'))  # Redirect if already logged in

    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        pbday_str = request.form.get('pbday')
        pnumber = request.form.get('pnumber')
        edu = request.form.get('edu')
        username = request.form.get('username')
        password = request.form.get('password')
        file = request.files['profile_picture']

        if not all([fname, lname, email, pbday_str, pnumber, edu, username, password, file]):
            flash('All fields including the profile picture are required.', 'danger')
            return render_template('user/signup.html')

        if User.query.filter_by(email=email).first():
            flash('Email already in use.', 'danger')
            return render_template('user/signup.html')

        if file and allowed_file(file.filename):
            image_data = file.read()
            encoded_string = base64.b64encode(image_data).decode('utf-8')
        else:
            flash('Invalid file format.', 'danger')
            return render_template('user/signup.html')

        pbday = datetime.strptime(pbday_str, '%Y-%m-%d')
        legal_age = 18
        eighteen_years_ago = datetime.now() - timedelta(days=365 * legal_age)
        if pbday >= eighteen_years_ago:
            flash('You must be at least 18 years old to sign up.', 'danger')
            return render_template('user/signup.html')

        new_user = User(
            fname=fname,
            lname=lname,
            email=email,
            pbday=pbday,
            pnumber=pnumber,
            edu=edu,
            username=username,
            password=password,
            profile_picture=encoded_string 
        )
        db.session.add(new_user)
        db.session.commit()
        flash('User account pending approval by Admin.', 'success')
        return redirect(url_for('userDashboard'))

    return render_template('user/signup.html', title="User Signup")



# User dashboard
@app.route('/user/dashboard')
def userDashboard():
    if not session.get('user_id'):
        return redirect('/user/')
    if session.get('user_id'):
        id = session.get('user_id')
    users = User().query.filter_by(id=id).first()
    return render_template('user/dashboard.html', title="User Dashboard", users = users)

# User Logout
@app.route('/user/logout')
def userLogout():
    if not session.get('user_id'):
        return redirect('/user/')
    if session.get('user_id'):
        session['user_id'] = None
        session['username'] = None
        return redirect('/user/')
    
    
# Child Information Router    
@app.route('/user/add_child', methods=['GET', 'POST'])
def add_child():
    form = ChildForm()
    if form.validate_on_submit():  # This will only be True if the form was submitted and the data was valid
        # Store data in the database
        new_child = Child(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            age=form.age.data,
            weight=form.weight.data,
            height=form.height.data
        )
        db.session.add(new_child)
        db.session.commit()
        
        # Prediction (make sure to implement or adjust the predict_malnutrition function accordingly)
        # risk = predict_malnutrition(form.weight.data, form.height.data, form.age.data)
        # flash(f'Predicted Malnutrition Risk: {risk}', 'info')
        return redirect(url_for('add_child'))
    
    return render_template('user/add_child.html', form=form)

# User Change Password
@app.route('/user/change-password', methods=['POST', 'GET'])
def userChangePassword():
    if not session.get('user_id'):
        return redirect('/user/')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email == "" or password == "":
            flash('Please fill the field.', 'warning')
            return redirect('/user/change-password')
        else:
            # Find user by email
            users = User.query.filter_by(email=email).first()
            if users:
                # Update password as plain text
                users.password = password
                db.session.commit()
                flash('Password changed successfully.', 'success')
                return redirect('/user/change-password')
            else:
                flash('Invalid email', 'danger')
                return redirect('/user/change-password')
    else:
        return render_template('user/change-password.html', title="Change Password")


if __name__ == '__main__':
    app.run(debug=True)
#     main('Dataset1.csv')
#     # Load the model and scaler
# model = joblib.load('malnutrition_model.pkl')
# scaler = joblib.load('scaler.pkl')
    
