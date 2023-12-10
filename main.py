from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import UserForm, NameForm, PasswordForm, LoginForm, PostForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os



app = Flask(__name__)
app.config['SECRET_KEY'] = 'justasecretkey39857238986'

ckeditor = CKEditor(app)

class Base(DeclarativeBase):
    pass

#sqlite
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

#mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Flamboyance%4069@localhost/mysql_users'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


migrate = Migrate(app, db)


#FLask login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'







#create User db
class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    username: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    color: Mapped[str] = mapped_column(String(100))
    about_author: Mapped[str] = mapped_column(String(1000))
    date_added: Mapped[str] = mapped_column(String(100), default=datetime.now())
    password_hash: Mapped[str] = mapped_column(String(200))
    profile_pic: Mapped[str] = mapped_column(String(200), nullable=True)
    posts: Mapped["Posts"] = relationship(backref='poster')

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Posts(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(String(1000))
    # author: Mapped[str] = mapped_column(String(200))
    date_posted: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    slug: Mapped[str] = mapped_column(String(200))
    poster_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)








@app.route('/')
@login_required
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
            new_user = User(name=form.name.data, username=form.username.data, email=form.email.data, color=form.color.data, about_author=form.about_author.data, password_hash=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            form.name.data = ''
            form.username.data = ''
            form.email.data = ''
            form.color.data = ''
            form.about_author.data = ''
            form.password_hash.data = ''
            flash('User successfully added!')
        else:
            flash('User already exists!')
    users = db.session.execute(db.select(User).order_by(User.id)).scalars()
    return render_template('add_user.html', form=form, users=users)


@app.route('/user/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    user = db.get_or_404(User, id)
    # users = db.session.execute(db.select(User)).scalars()
    # for a in users:
    #     print(a.username, a.password)
    #when the user clicks the submit button
    if request.method == 'POST':
        if form.color.data == '':
            form.color.data = 'None'

        user.name = request.form['name']
        user.username = request.form['username']
        user.email = request.form['email']
        user.color = request.form['color']
        user.about_author = request.form['about_author']
        user.profile_pic = request.files['profile_pic']
        db.session.commit()
        flash("User successfully updated!")
    form.name.data = user.name
    form.username.data = user.username
    form.email.data = user.email
    form.color.data = user.color
    form.about_author.data = user.about_author
    form.profile_pic.data = user.profile_pic

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
    email = ''
    password = ''
    check_user = ''
    form = PasswordForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        form.email.data = ''
        form.password.data = ''
        check_user = db.session.execute(db.select(User).filter_by(email=email)).first()
        checked_password = check_password_hash(check_user[0].password_hash, password)

    return render_template('check_password.html', form=form, email=email, password=password, check_user=check_user, checked_password=checked_password)


@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        #add post to db
        post = Posts(title=form.title.data, content=form.content.data, poster_id=poster, slug=form.slug.data)
        db.session.add(post)
        db.session.commit()
        flash("Blog post submitted successfully!")

        #clear form
        form.title.data = ''
        form.content.data = ''
        form.slug.data = ''

    blog_posts = db.session.execute(db.select(Posts).order_by(Posts.id)).all()
    return render_template('add_post.html', form=form, blog_posts=blog_posts)


@app.route('/posts', methods=['GET', 'POST'])
@login_required
def posts():
    all_posts = []
    posts = db.session.execute(db.select(Posts).order_by(Posts.id))
    for post in posts:
        all_posts.append(post[0])
    return render_template('posts.html', all_posts=all_posts)


@app.route('/post/<int:id>')
@login_required
def post(id):
    post = db.get_or_404(Posts, id)
    return render_template('post.html', post=post)


@app.route('/post/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    form = PostForm()
    post = db.get_or_404(Posts, id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.slug = form.slug.data
        db.session.commit()
        flash(f"Blog titled '{post.title}' successfully updated!")
        return redirect(url_for('post', id=post.id))
    form.title.data = post.title
    form.content.data = post.content
    form.slug.data = post.slug
    return render_template('edit.html', form=form, post=post)


@app.route('/post/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_blog(id):
    user = db.get_or_404(Posts, id)
    db.session.delete(user)
    db.session.commit()
    flash("Blog successfully deleted!")
    return redirect(url_for('posts'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).filter_by(username=form.username.data)).scalar()
        if user:
            if check_password_hash(user.password_hash, form.password_hash.data):
                login_user(user)
                flash("Login successfully!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong username or password")
        else:
            flash("Wrong username or password")
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have successfully logged out!')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        all_posts = []
        searching = form.search.data
        posts = db.session.execute(db.select(Posts).order_by(Posts.title).where(Posts.content.like("%" + searching + "%"))).scalars()
        for post in posts:
            all_posts.append(post)
        return render_template('search.html', form=form, searching=searching, all_posts=all_posts)


















@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)