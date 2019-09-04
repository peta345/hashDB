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


    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
