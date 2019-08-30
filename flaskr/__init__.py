import os

from flask import Flask, flash, g, redirect, render_template, request, url_for, session, Markup
from flaskr.db import get_db

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # fileter
    @app.template_filter('cr')
    def cr(arg):
        return Markup(arg.replace('\r', '<br>'))

    # a simple page that says hello
    @app.route('/')
    def index():
        db = get_db()
        posts = db.execute('SELECT created, username, filename, body, hash FROM post').fetchall()
        return render_template('/home.html', posts=posts)


    @app.route('/admin', methods=('GET', 'POST'))
    def admin():
        if request.method == "POST":
            password = request.form["password1"]
            # password
            if password == "12345678123":
                return redirect(url_for('edit', flg=True))
        return render_template("admin.html")

    @app.route('/edit', methods=('GET', 'POST'))
    def edit():
        if request.method == "POST":
            if bool(request.form.getlist("ids")):
                db = get_db()            
                for l in request.form.getlist("ids"):
                    db.execute('DELETE FROM post WHERE id ={}'.format(l))
                db.commit()
                flash("Delete success")
        flg = request.args['flg']
        if flg:
            db = get_db()
            posts = db.execute(
                'SELECT id, created, username, filename, body, hash FROM post').fetchall()
            return render_template('edit.html', posts=posts)


    @app.route('/q/<hashparam>', methods=('GET', 'POST'))
    def home(hashparam=None):
        db = get_db()
        print(hashparam)
        post = db.execute(
            'SELECT created, username, filename, body, hash FROM post WHERE hash = "{}"'
            .format(hashparam)).fetchone()
        return render_template('/article.html', post=post)


    @app.route('/register', methods=('GET','POST'))
    def register():
        if request.method == "POST":
            username = request.form['username1']
            filename = request.form['filename']
            hashval = request.form['hash']
            body = request.form['body']
            db = get_db()
            error = None

            print("{0}, {1}, {2}, {3}".format(username, filename, hashval, body))

            if not username or not filename or not hashval or not body:
                error = "You need to input all value."
            elif db.execute(
            'SELECT id FROM post WHERE hash = ?', (hashval,)
            ).fetchone() is not None:
                error = 'Hash {} is already registered.'.format(hashval)

            if error is None:
                db.execute(
                    'INSERT INTO post (username, filename, body, hash) VALUES (?, ?, ?, ?)',
                    (username,filename,body,hashval)
                )
                db.commit()
                flash("Register success !")
                return redirect(url_for('register'))

            flash(error)
        return render_template('/register.html')




    from . import db
    db.init_app(app)

    return app
