from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)
app.config['SECRET_KEY'] = 'justasecretkey39857238986'


class Base(DeclarativeBase):
    pass

#sqlite
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

#mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Flamboyance%4069@localhost/mysql_users'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


migrate = Migrate(app, db)
#create User db
class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    color: Mapped[str] = mapped_column(String(100))
    date_added: Mapped[str] = mapped_column(String(100), default=datetime.now())
    password_hash: Mapped[str] = mapped_column(String(200))

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)




with app.app_context():
    db.create_all()


#userform
class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password', 'Password should match!'), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    color = StringField('Favorite color')
    submit = SubmitField("Submit")


#nameform class
class NameForm(FlaskForm):
    name = StringField('Your name', validators=[DataRequired()])
    submit = SubmitField('Submit')


class PasswordForm(FlaskForm):
    name = StringField("Name")
    password = PasswordField("Password")
    submit = SubmitField("Check Password")

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.route('/name', methods=['GET', 'POST'])
def name():
    name = ''
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully!")
    return render_template('name.html', form=form, name=name)


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        verify_user = db.session.execute(db.select(User).filter_by(email=form.email.data)).one_or_none()
        if verify_user is None:
            if form.color.data == '':
                form.color.data = 'None'
            #hashing the password
            hashed_password = generate_password_hash(form.password_hash.data, 'scrypt')
            new_user = User(name=form.name.data, email=form.email.data, color=form.color.data, password_hash=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            form.name.data = ''
            form.email.data = ''
            form.color.data = ''
            form.password_hash.data = ''
            flash('User successfully added!')
        else:
            flash('User already exists!')
    users = db.session.execute(db.select(User).order_by(User.id)).scalars()
    return render_template('add_user.html', form=form, users=users)


@app.route('/user/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    user = db.get_or_404(User, id)

    #when the user clicks the submit button
    if form.validate_on_submit():
        if form.color.data == '':
            form.color.data = 'None'
        user.name = form.name.data
        user.email = form.email.data
        user.color = form.color.data
        db.session.commit()
        flash("User successfully updated!")

    return render_template('update.html', form=form, user=user)


@app.route('/user/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    user = db.get_or_404(User, id)
    if request.method == 'POST':
        db.session.delete(user)
        db.session.commit()
        flash("User successfully deleted.")
    return render_template('delete.html', user=user)


@app.route('/check_password', methods=['GET', 'POST'])
def check_password():
    form = PasswordForm()

    return render_template('check_password.html', form=form)


















@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)