from logging import exception
from flask import Flask,render_template,request, redirect, url_for
import sqlite3
from form import SignupForm,PostForm,LoginForm
from flask_login import LoginManager,current_user,login_user,logout_user
from models import users, get_user,User
from werkzeug.urls import url_parse

#creador de BD
def creabd():
    conn=sqlite3.connect("producto.db")
    try:    
        conn.commit()
        print('la dase de datos fue creada')
    except sqlite3.OperationalError:
        print("ya existe la base de datos")
    conn.close()

#iniciar app
app = Flask(__name__)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
login_manager = LoginManager(app)
#rutas del navegador
posts = []

#ruta a home
@app.route('/')
def index():
    return render_template('home.html', posts=posts)

#ruta a top
@app.route('/top')
def post_view():
    return render_template('top.html',posts=posts )

#ruta a registro de usuario
@app.route("/signup_form", methods=["GET", "POST"])
def show_signup_form():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignupForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        # Creamos el usuario y lo guardamos
        user = User(len(users) + 1, name, email, password)
        users.append(user)
        # Dejamos al usuario logueado
        login_user(user, remember=True)
        next_page = request.args.get('next', None)
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template("signup_form.html", form=form)

#vista entrada como admin
@app.route("/admin/post/", methods=['GET', 'POST'], defaults={'post_id': None})
@app.route("/admin/post/<int:post_id>/", methods=['GET', 'POST'])
def post_form(post_id):
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        title_slug = form.title_slug.data
        content = form.content.data
        post = {'title': title, 'title_slug': title_slug, 'content': content}
        posts.append(post)
        return redirect(url_for('index'))
    return render_template("admin/post_form.html", form=form)

#vista usuario
@login_manager.user_loader
def load_user(user_id):
    for user in users:
        if user.id == int(user_id):
            return user
    return None

#vista iniciar sesion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user(form.email.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
    return render_template('login_form.html', form=form)

#cerrar sesion
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


#start
if __name__ == '__main__':
    app.run(debug=True)
    creabd()
    