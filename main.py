import flask
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Login Manager Class
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


# Line below only required once, when creating DB.
# db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        hash_password = generate_password_hash(request.form.get("password"),
                                               method="pbkdf2:sha256",
                                               salt_length=8)
        new_user = User(
            email=request.form.get("email"),
            password=hash_password,
            name=request.form.get("name")
        )
        db.session.add(new_user)
        db.session.commit()

        # Login and authenticate user after logging in to the database
        login_user(new_user)

        return render_template("secrets.html", name=new_user.name)

    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        # Find user by email entered.
        user = User.query.filter_by(email=email).first()
        print(user)

        # Check stored password has against entered password hashed.
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("secrets"))  # redirect(url_for("secrets"))

    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    print(current_user.name)
    return render_template("secrets.html", name=current_user.name)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download/<path:filename>')
def download(filename):
    return send_from_directory(directory="static/files", path=filename, as_attachment=False)


if __name__ == "__main__":
    app.run(debug=True)
