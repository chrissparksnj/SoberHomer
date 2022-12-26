from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from forms import *
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, Email
from datetime import datetime



app = Flask(__name__)
app.config['SECRET_KEY'] = "SecretKey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/sparql/sober/soberhousing/test.db'
db = SQLAlchemy(app)


# Login Manager Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Database Stuff
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

class House(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    house_name = db.Column(db.String(80), nullable=False)
    house_address = db.Column(db.String(80), nullable=False)
    house_rooms = db.Column(db.Integer, nullable=False)
    house_beds = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return self.house_name

class Tenant(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    house_name = db.Column(db.String(80), nullable=False)
    room_number = db.Column(db.String(80), nullable=False)
    bed_number = db.Column(db.String(80), nullable=False)
    rent_status = db.Column(db.String(80), nullable=False)

class RemovedTenant(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    house_name = db.Column(db.String(80), nullable=False)
    room_number = db.Column(db.String(80), nullable=False)
    bed_number = db.Column(db.String(80), nullable=False)
    


def choice_query():
    return House.query

class TenantForm(FlaskForm):
    name = StringField(label="House Name", validators=[DataRequired()])
    age = StringField(label="House Address", validators=[DataRequired()])
    room_number = StringField(label="Number Of Beds", validators=[DataRequired()])
    bed_number = StringField(label="Number Of Beds", validators=[DataRequired()])
    house_name = QuerySelectField(query_factory=choice_query, allow_blank=False, get_label="house_name")

@app.route("/")
def index():
    return render_template("index.html")

################################################
############### HOUSING STUFF  #################
################################################

@app.route("/dashboard")
@login_required
def dashboard():
    now = datetime.now()
    date_time_str = now.strftime("%m/%d/%y")
    tenants = Tenant.query.filter_by(user_id=current_user.id).all()
    houses = House.query.filter_by(user_id=current_user.id).all()
    return render_template("/user/dashboard.html", houses=houses, tenants=tenants, date=date_time_str)

@app.route("/addhouse", methods=['GET', 'POST'])
@login_required
def addhouse():
    form = AddHouseForm()
    if form.validate_on_submit():
        user = current_user.id
        houseAddress = form.houseAddress.data
        houseBeds = form.houseBeds.data
        houseName = form.houseName.data
        houseRooms = form.houseRooms.data
        house = House(user_id=user, house_address=houseAddress, house_rooms=houseRooms, house_beds=houseBeds, house_name=houseName)
        db.session.add(house)
        db.session.commit()
        flash("House Added")
        return redirect(url_for("dashboard"))
    
    return render_template("/house/addhouse.html", form=form)

@app.route("/addtenant", methods=['GET', 'POST'])
@login_required
def addtenant():
    form = TenantForm()
    if form.validate_on_submit():
        user = current_user.id
        name = form.name.data
        age = form.age.data
        room_number = form.room_number.data
        house_name = form.house_name.data
        bed_number = form.bed_number.data
        tenant = Tenant(
            user_id=str(user), 
            bed_number=bed_number, 
            name=str(name), 
            age=age, 
            room_number=str(room_number), 
            house_name=str(house_name), 
            rent_status="Unpaid"
            )
        db.session.add(tenant)
        db.session.commit()
        flash("tenant added")
        return redirect(url_for("dashboard"))

    return render_template("/house/addtenant.html", form=form)

@app.route("/payrent/<int:tenant_id>")
def payrent(tenant_id):
    tenant = Tenant.query.get(tenant_id)
    tenant.rent_status = "Paid"
    db.session.commit()
    flash(f'Rent status for {tenant.name} updated')
    return redirect(url_for("dashboard"))

@app.route("/reinstate/<int:tenant_id>")
def reinstate(tenant_id):
    tenant = RemovedTenant.query.get(tenant_id)
    reinstatedTenant = Tenant(
        user_id=str(current_user.id),
        bed_number=0,
        name=str(tenant.name),
        age=tenant.age,
        room_number=str(0),
        house_name=str(tenant.house_name),
        rent_status="Unpaid"
    )
    db.session.add(reinstatedTenant)
    db.session.delete(tenant)
    db.session.commit()
    flash (f'Tenant {tenant.name} reinstated')
    return redirect(url_for("dashboard"))


@app.route("/deletetenant/<int:id>", methods=['GET', 'POST'])
@login_required
def deletetenant(id):
    tenant = Tenant.query.get(id)
    removedTenant = RemovedTenant(
        user_id=str(current_user.id), 
        bed_number=tenant.bed_number, 
        name=str(tenant.name), 
        age=tenant.age, 
        room_number=str(tenant.room_number),
        house_name=str(tenant.house_name),
        )
    db.session.add(removedTenant)
    db.session.delete(tenant)
    db.session.commit()
    flash("Tenant removed from housing")
    return redirect(url_for("dashboard"))

@app.route("/edittenant/<int:user_id>", methods=['GET', 'POST'])
def edittenant(user_id):
    tenant = Tenant.query.get(user_id)
    form = TenantForm()
    if form.validate_on_submit():
        tenant.name = form.name.data
        tenant.age = int(form.age.data)
        tenant.room_number = form.room_number.data
        tenant.house_name = str(form.house_name.data)
        tenant.bed_number = form.bed_number.data
        
        db.session.commit()
        flash("Tenant updated")
        return redirect(url_for("dashboard"))
    return render_template("/house/edittenant.html", form=form, tenant=tenant)


@app.route("/removedtenants", methods=['GET'])
def removedtenants():
    removedTenants = RemovedTenant.query.filter_by(user_id=current_user.id).all()
    return render_template("/house/removedtenants.html", tenants=removedTenants)
################################################
############## LOGIN/LOGOUT STUFF ##############
################################################
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user:
            if user.password == password:
                login_user(user)
                return redirect(url_for("dashboard"))
            else:
                flash("Wrong Password - Try Again")
        else:
            flash("That user doesn't exist")       
    return render_template("/user/login.html", form=form)

@app.route("/logout", methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))
        
    return render_template("/user/signup.html", form=form)

################################################
############## HELPER STUFF ####################
################################################
@app.route("/form_to_json", methods=['POST'])
def form_to_json():
    data = request.form.to_dict(flat=False)
    return jsonify(data)



