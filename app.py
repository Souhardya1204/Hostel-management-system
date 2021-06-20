from enum import unique
import os
import razorpay
from flask import Flask, render_template, request, redirect, flash, url_for, make_response
from flask.globals import session
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model
from sqlalchemy import func
from sqlalchemy.sql.expression import false, null
from sqlalchemy.sql.functions import user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = 'static/profile_pics/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__, static_url_path='', static_folder='static/',)

app.secret_key = os.urandom(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hosteldata.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
db = SQLAlchemy(app)


class HostelInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    totalstudents = db.Column(db.Integer, nullable=False)

    def __init__(self,):
        return 'HostelInfo' + str(self.id)

class Student(db.Model):
    roll = db.Column(db.String(30), primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    room = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    dept = db.Column(db.String(30), nullable=False)
    contact = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(30), unique=True,nullable=False)

    def __repr__(self):
        return 'Student'


class Applicants(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    s_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(30), nullable=False)
    g_name = db.Column(db.String(30), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    distance = db.Column(db.Integer, nullable=False)
    state = db.Column(db.String(30), nullable=False)
    roll = db.Column(db.String(30), unique=True)
    dept = db.Column(db.String(10), nullable=False)
    income = db.Column(db.Integer, nullable=False)
    year = db.Column(db.String(10), nullable=False)
    contact = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    fees_status = db.Column(db.String(10), nullable=False)
    image_file = db.Column(db.String(20), nullable=False)
    

    def __init__(self, s_name, email, password, g_name, address, distance, state, roll, dept, income, year, contact):
        self.s_name = s_name
        self.email = email
        self.password = password
        self.g_name = g_name
        self.address = address
        self.distance = distance
        self.state = state
        self.roll = roll
        self.dept = dept
        self.income = income
        self.year = year
        self.contact = contact
        self.status = "waiting"
        self.fees_status = "Not Paid"
        self.image_file = "unnamed.png"
        


class Admin(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(30), nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password = password

# adding an admin


def init_admin():
    admin = Admin(
        "admin@123", generate_password_hash("admin", method='sha256'))
    db.session.add(admin)
    db.session.commit()


@app.route('/')
def index():
    return render_template("home.html", students=db.session.query(func.count(Student.roll)).scalar(), warden="Partha Haldar", no_of_rooms=20, hostel_fees=1000, mess_fees=2000)


@app.route('/admin')
def admin():
    if 'admin' in session:
        info = HostelInfo.query.get(1)
        return render_template("dashboard.html", students=db.session.query(func.count(Student.roll)).scalar(),
                               students_1st=db.session.query(Student).filter(
                                   Student.year == "1st").count(),
                               students_2nd=db.session.query(Student).filter(
                                   Student.year == "2nd").count(),
                               students_3rd=db.session.query(Student).filter(
                                   Student.year == "3rd").count(),
                               students_4th=db.session.query(Student).filter(Student.year == "4th").count(),students_CSE=db.session.query(Student).filter(
                                   Student.dept == "CSE").count(),students_IT=db.session.query(Student).filter(
                                   Student.dept == "IT").count(),students_CT=db.session.query(Student).filter(
                                   Student.dept == "CT").count())
    
    else:
        flash("You are not logged in", "error")
        return render_template("login.html")


@app.route('/students')
def hostel():
    if 'admin' in session:
        students = Student.query.all()
        return render_template('students.html', students=students)
    else:

        flash("You are not logged in", "error")
        return render_template("login.html")

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')


@app.route('/show_applicants')
def show_applicants():
    if 'admin' in session:
        students = db.session.query(Applicants).filter(
            Applicants.status == 'waiting').all()
        return render_template('show_applicants.html', students=students)
    else:
        flash("You are not logged in", "error")
        return render_template("login.html")


@app.route('/students/delete/<roll>', methods=['GET', 'POST'])
def delete(roll):
    if 'admin' in session:
        student = Student.query.get_or_404(roll)
        db.session.delete(student)
        db.session.commit()
        return redirect('/students')
    else:
        flash("You are not logged in", "error")
        return render_template("login.html")


@app.route('/applicant/delete/<id>', methods=['GET', 'POST'])
def delete_applicant(id):
    if 'admin' in session:
        student = Applicants.query.get_or_404(id)
        student.status = "rejected"
        db.session.commit()
        return redirect('/show_applicants')
    else:
        flash("You are not logged in", "error")
        return render_template("login.html")



@app.route('/add-student/<id>', methods=['GET', 'POST'])
def addstudent(id):
    if 'admin' in session:
        student = Applicants.query.get_or_404(id)
        if student:
            if request.method == 'POST':
                #if not request.form['name'] or not request.form['roll'] or not request.form['room'] or not request.form['year'] or not request.form['dept']:
                    #flash('Please enter all the fields', 'error')
                if not request.form['room']:
                    flash('Please provide a room no.')
                else:
                    '''name = request.form.get('name').upper()
                    roll = request.form['roll']
                    dept = request.form.get('dept')
                    year = request.form.get('year')
                    email = student.email'''
                    name=student.s_name.upper()
                    roll=student.roll
                    dept=student.dept
                    year=student.year
                    email=student.email
                    contact=student.contact
                    room = request.form['room']
                    # adding the student in the residents table
                    new_student = Student(
                        roll=roll, name=name, room=room, year=year, dept=dept,contact=contact, email=email)
                    db.session.add(new_student)
                    db.session.commit()
                    # deleting the student from appplicants table
                    student = Applicants.query.get_or_404(id)
                    student.status = "alloted"
                    db.session.commit()
                    # db.session.delete(student)
                    # db.session.commit()
                    return redirect('/admin')
            return render_template('addstudent.html', student=student)
        else:
            return redirect(url_for('show_applicants'))
    else:
        flash("You are not logged in", "error")
        return render_template("login.html")


@app.route('/students/edit/<roll>', methods=['GET', 'POST'])
def update(roll):
    if 'admin' in session:
        student = Student.query.get_or_404(roll)
        if request.method == 'POST':
            #if not request.form['name'] or not request.form['roll'] or not request.form['room'] or not request.form['year'] or not request.form['dept']:
                #flash('Please enter all the fields', 'error')
            if not request.form['room']:
                flash("Please provide a room no.")
            else:
                #student.name = request.form['name']
                #student.roll = request.form['roll']
                student.room = request.form['room']
                #student.dept = request.form['dept']
                #student.year = request.form['year']
                db.session.commit()
                return redirect('/students')

        return render_template('edit-student.html', student=student)
    else:
        flash("You are not logged in")
        return render_template("login.html")


@app.route('/search_student', methods=['GET', 'POST'])
def search_student():
    if 'admin' in session:
        if(request.method == 'POST'):
            print('post')
            name = request.form.get('search_name')
            if name:
                student = db.session.query(Student).filter(
                    Student.name == name.upper()).all()
                if len(student) == 0:
                    flash('Student does not exist', 'error')
                else:
                    return render_template('students.html', students=student)
            else:
                return redirect('/students')
        return redirect('/students')
    else:
        flash("You are not logged in", "error")
        return render_template("login.html")



@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'POST':
        s_name = request.form.get('s_fname')+' '+request.form.get('s_lname')
        password = request.form.get('password')
        email = request.form.get('email')
        g_name = request.form.get('g_fname')+' '+request.form.get('g_lname')
        address = request.form.get('address')
        distance = request.form.get('distance')
        state = request.form.get('state')
        roll = request.form.get('roll')
        dept = request.form.get('dept')
        income = request.form.get('income')
        year = request.form.get('year')
        contact = request.form.get('contact')
        if password and s_name and email and g_name and address and distance and state and roll and dept and income and year and contact:
            distance = int(distance)
            income = int(income)
            applicant = Applicants.query.filter_by(email=email).first()
            if applicant:  # if a user is found, we want to redirect back to signup page so user can try again
                flash("User already exits")
                return render_template('apply.html')

            new_user = Applicants(s_name, email, generate_password_hash(
                password, method='sha256'), g_name, address, distance, state, roll, dept, income, year, contact)

        # add the new user to the database
            db.session.add(new_user)
            db.session.commit()
            flash("Successfully Applied", "success")
            return redirect(url_for('login'))
        else:
            flash("Please fill up all the fields")
            return render_template('apply.html')
    else:
        return render_template('apply.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if(request.method == 'POST'):
        email = request.form.get('email')
        password = request.form.get('password')
        type = request.form.get('type')
        if email and password and (type=='Admin' or type=='Student'):
            if type == 'Student':
                user = Applicants.query.filter_by(email=email).first()

            # check if the user actually exists
            # take the user-supplied password, hash it, and compare it to the hashed password in the database
                if not user or not check_password_hash(user.password, password):
                    flash('Please check your login details and try again.', "error")
                    # if the user doesn't exist or password is wrong, reload the page
                    return render_template("login.html")
                else:
                    session['email'] = user.email
                    msg = 'Logged in successfully !'
                    return redirect(url_for('student_dashboard'))
            elif type == 'Admin':
                user = Admin.query.filter_by(email=email).first()

            # check if the user actually exists
            # take the user-supplied password, hash it, and compare it to the hashed password in the database
                if not user or not check_password_hash(user.password, password):
                    flash('Please check your login details and try again.', "error")
                    # if the user doesn't exist or password is wrong, reload the page
                    return redirect(url_for('login'))
                else:
                    session['admin'] = user.email
                    msg = 'Logged in successfully !'
                    return redirect(url_for('admin'))
        else:
            flash("Please fill up all fields ", "error")
            return render_template('login.html')
    else:
       
        return render_template('login.html')


    

@app.route('/student_dashboard')
def student_dashboard():
    if 'email' in session:
        email = session['email']
        user = Applicants.query.filter_by(email=email).first()
        return render_template('student_dashboard.html', user=user)
    else:
        flash("You are not logged in", "error")
        return render_template("login.html")


@app.route('/student_profile')
def student_profile():
    if 'email' in session:
        email = session['email']
        user = Applicants.query.filter_by(email=email).first()
        return render_template('student_profile.html', user=user)
    else:
        flash("You are not logged in", "error")
        return render_template("login.html")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route("/student/update_profile",methods=['GET','POST'])
def update_profile():
    if 'email' in session:
        email = session['email']
        user = Applicants.query.filter_by(email=email).first()
        if request.method=='POST':
            if not request.form['name'] or not request.form['roll']  or not request.form['year'] or not request.form['dept'] or not request.form['contact']:
                flash('Please enter all the fields', 'error')
                return render_template('update_profile.html',student=user)
          
            else:
                user.s_name = request.form['name']
                user.roll = request.form['roll']
                user.dept = request.form['dept']
                user.year = request.form['year']
                user.contact=request.form['contact']
                db.session.commit()
                student=Student.query.filter_by(email=email).first()
                if student:
                    student.name = request.form['name']
                    student.roll = request.form['roll']
                    student.dept = request.form['dept']
                    student.year = request.form['year']
                    student.contact=request.form['contact']
                    db.session.commit()
                flash('Profile successfully updated')
                return redirect(url_for('student_profile'))

        else:
            return render_template('update_profile.html', student=user)
    else:
        flash("You are not logged in", "error")
        return render_template("login.html")




@app.route('/student_upload_image', methods=['GET', 'POST'])
def upload_file():
    if 'email' in session:
        email = session['email']
        user = Applicants.query.filter_by(email=email).first()
        if request.method == 'POST':
            
            if 'file' not in request.files:
                flash('No file part','error')
                return redirect(url_for('student_dashboard'))
            file = request.files['file']
            
            if file.filename == '':
                return redirect(url_for('student_dashboard'))
                
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user.image_file = filename
                db.session.commit()
                flash('File uploaded successfully!!','success')
                return redirect(url_for('student_dashboard'))  
        return  render_template("student_upload_image.html",user=user) 


    else:
        flash("Please log in as student to upload photo", "error")
        return render_template("login.html")

#/student_fees_payment
@app.route('/student_fees_payment', methods=['GET', 'POST'])
def pay_fees():
    if 'email' in session:
        email = session['email']
        user = Applicants.query.filter_by(email=email).first()
        client = razorpay.Client(auth=("rzp_test_A4VvhETPM5RfxC", "MYpcmIHLh4o7kc9CZb6rGYDp"))
        payment = client.order.create({'amount' : int(300000) , 'currency': 'INR', 'payment_capture' : '1'})
        return render_template("payment_page.html", user=user , payment=payment)
    else:
        flash("You are not logged in", "error")
        return render_template("login.html")


@app.route('/check_stat/<email>')
def check_stat(email):
    if 'email' in session and email == session['email']:
        student = Applicants.query.filter_by(email=email).first()
        if (student.status == "waiting"):
            flash("Your application is waiting for decision", "info")
        elif(student.status == "alloted"):
            flash(
                "Your application has been approved. Contact the superintendent for further details.", "success")
        else:
            flash("Your application has been rejected.", "error")
        return redirect(url_for('student_dashboard'))
    else:
        flash("You are not logged in", "error")
        return render_template("login.html")


@app.route('/check_fees_stat/<email>')
def check_fees_stat(email):
    if 'email' in session and email == session['email']:
        student = Applicants.query.filter_by(email=email).first()
        if (student.fees_status == "Not Paid"):
            flash("You have not paid your fees. ", "error")
            
        else:
            flash("Your fees have been paid", "success")
       
        return redirect(url_for('student_dashboard'))
    else:
        flash("You are not logged in", "error")
        return render_template("login.html")


@app.route('/payment_successful/<email>', methods=['GET', 'POST'])
def payment_successful(email):
    if 'email' in session and email == session['email']:
        student = Applicants.query.filter_by(email=email).first()
        student.fees_status = "Paid" 
        db.session.commit()
        return render_template("payment_successful.html" )


@app.route('/payment_unsuccessful', methods=['GET', 'POST'])
def payment_unsuccessful():
    return render_template('payment_unsuccessful.html')


@app.route('/logout')
def logout():
    if 'email' in session:
        session.pop("email", None)
    elif 'admin' in session:
        session.pop("admin", None)
    flash("You have successfully logged out", "success")
    return render_template("login.html")


if __name__ == "__main__":
    db.create_all()
    Admin.query.delete()
    init_admin()
    app.run(debug=True)    
