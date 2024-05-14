from flask import Flask, render_template, request, flash, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
from flask_session import Session

app = Flask(__name__)

app.config['SECRET_KEY'] = '4046bde895cc19ca9cbd373a'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:admin123@localhost/malnutritiondb'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
Session(app)

# User Class
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(255), nullable=False)
    lname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    pbday = db.Column(db.Date)
    pnumber = db.Column(db.Integer, nullable=False, unique=True)
    edu =  db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password =  db.Column(db.String(255), nullable=False)
    status = db.Column(db.Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f'User("{self.id}", "{self.fname}", "{self.lname}", "{self.pbday}", "{self.edu}", "{self.status}")'

# create admin Class
class Admin(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(255), nullable=False)
    password=db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'Admin("{self.username}","{self.id}")'

# Function to create db tables
def create_db_tables():
    with app.app_context():
        db.create_all()

# Create table
create_db_tables()

# insert admin data one time only one time insert this data
# latter will check the condition
# @app.before_request
# def insert_admin():
#     try:
#         if not Admin.query.first():
#             admin = Admin(username='bsisthesis123', password=bcrypt.generate_password_hash('adminthesis2024', 10))
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
@app.route('/admin/',methods=["POST","GET"])
def adminIndex():
    # check the request is post or not
    if request.method == 'POST':
        # get the value of field
        username = request.form.get('username')
        password = request.form.get('password')
        # check the value is not empty
        if not username or not password:
            flash('Please fill all the field', 'danger')
            return redirect('/admin/')
        else:
            # login admin by username 
            admins=Admin().query.filter_by(username=username).first()
            if admins and bcrypt.check_password_hash(admins.password,password):
                session['admin_id']=admins.id
                session['admin_name']=admins.username
                flash('Login Successfully','success')
                return redirect('/admin/dashboard')
            else:
                flash('Invalid Email and Password','danger')
                return redirect('/admin/')
    else:
        return render_template('admin/index.html',title="Admin Login")

# Admin Dashboard
@app.route('/admin/dashboard')
def adminDashboard():
    if not session.get('admin_id'):
        return redirect('/admin/')
    totalUser=User.query.count()
    totalApprove=User.query.filter_by(status=1).count()
    NotTotalApprove=User.query.filter_by(status=0).count()
    return render_template('admin/dashboard.html',title="Admin Dashboard",totalUser=totalUser,totalApprove=totalApprove,NotTotalApprove=NotTotalApprove)

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
@app.route('/admin/change-admin-password',methods=["POST","GET"])
def adminChangePassword():
    admin=Admin.query.get(1)
    if request.method == 'POST':
        username=request.form.get('username')
        password=request.form.get('password')
        if username == "" or password=="":
            flash('Please fill the field','danger')
            return redirect('/admin/change-admin-password')
        else:
            Admin().query.filter_by(username=username).update(dict(password=bcrypt.generate_password_hash(password,10)))
            db.session.commit()
            flash('Admin Password update successfully','success')
            return redirect('/admin/change-admin-password')
    else:
        return render_template('admin/admin-change-password.html',title='Admin Change Password',admin=admin)


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
        if users and bcrypt.check_password_hash(users.password,password):
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
    if  session.get('user_id'):
        return redirect('/user/dashboard')
    if request.method=='POST':
        #get all input field name
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        pbday_str = request.form.get('pbday')
        pnumber = request.form.get('pnumber')
        edu = request.form.get('edu')
        username = request.form.get('username')
        password = request.form.get('password')
        
        #checks if all field are filled or not
        if fname == "" or lname == "" or pbday_str == "" or edu == "" or username == "" or email == "" or password == "":
            flash('Please fill all the field.', 'danger')
            return redirect ('/user/signup')
        else:
            is_email=User().query.filter_by(email=email).first()
            if is_email:
                flash('Email already in use.', 'danger')
                return redirect ('/user/signup')
            else:
                hash_password = bcrypt.generate_password_hash(password,10)
                pbday = datetime.strptime(pbday_str, '%Y-%m-%d')
                legal_age = 18
                eighteen_years_ago = datetime.now() - timedelta(days = 365 * legal_age)
                if pbday >= eighteen_years_ago:
                    flash('You must be at least 18 years old to sign up.', 'danger')
                    return redirect('/user/signup')
                user = User(fname=fname,lname=lname,password=hash_password,edu=edu,pnumber=pnumber,pbday=pbday,email=email,username=username)
                db.session.add(user)
                db.session.commit()
                flash('User account pending approval by Admin.', 'success')
                return redirect ('/user/')
    else:
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
    
    
# User Profile Update
@app.route('/user/update-profile', methods=["POST","GET"])
def userUpdateProfile():
    if not session.get('user_id'):
        return redirect('/user/')
    if session.get('user_id'):
        id=session.get('user_id')
    users=User.query.get(id)
    if request.method == 'POST':
        # get all input field name
        fname=request.form.get('fname')
        lname=request.form.get('lname')
        email=request.form.get('email')
        username=request.form.get('username')
        edu=request.form.get('edu')
        if fname =="" or lname=="" or email=="" or username=="" or edu=="":
            flash('Please fill all the field','danger')
            return redirect('/user/update-profile')
        else:
            session['username'] = None
            User.query.filter_by(id=id).update(dict(fname=fname,lname=lname,email=email,edu=edu,username=username))
            db.session.commit()
            session['username'] = username
            flash('Profile update Successfully','success')
            return redirect('/user/dashboard')
    else:
        return render_template('user/update-profile.html',title="Update Profile",users=users)
    
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
            return redirect ('/user/change-password')
        else:
            users = User.query.filter_by(email=email).first()
            if users:
                hash_password = bcrypt.generate_password_hash(password,10)
                User.query.filter_by(email=email).update(dict(password=hash_password))
                db.session.commit()
                flash('Password changed successfully.', 'success')
                return redirect ('/user/change-password')
            else:
                flash('Invalid email', 'danger')
                return redirect ('/user/change-password')
                
    else:   
        return render_template('user/change-password.html', title="Change Password")

if __name__ == '__main__':
    app.run(debug=True)
    
# https://www.youtube.com/watch?v=0LER-sVDexY&list=PLKbhw6n2iYKieyy9hhLjLMpD9nbOnCVmo&index=6 [0:01]