from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

# a simple page that says hello
@bp.route('/')
@login_required
def index():
	db = get_db()
	posts = db.execute(
        'SELECT p.id, body, created, author_id, username, filename, hash'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchmany(9)
	return render_template('blog/home.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == "POST":
        filename = request.form['filename']
        hashval = request.form['hash']
        body = request.form['body']
        db = get_db()
        error = None

        if not filename or not hashval or not body:
            error = "You need to input all value."
        elif db.execute('SELECT id FROM post WHERE hash = ?', (hashval,)).fetchone() is not None:
            error = 'Hash {} is already registered.'.format(hashval)

        else:
            db.execute(
                'INSERT INTO post (filename, body, hash, author_id) VALUES (?, ?, ?, ?)',
                (filename,body,hashval, g.user['id'])
            )
            db.commit()
            flash("Register success !")
            return redirect(url_for('blog.index'))

        flash(error)
    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, body, created, author_id, username, filename, hash'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
	post = get_post(id)

	if request.method == 'POST':
		body = request.form['body']
		error = None

		if error is not None:
			flash(error)
		else:
			db = get_db()
			db.execute(
        		'UPDATE post SET body = ?'
        		' WHERE id = ?',
        		(body, id)
        		)
			db.commit()
			return redirect(url_for('blog.index'))

	return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
	get_post(id)
	db = get_db()
	db.execute('DELETE FROM post WHERE id = ?', (id,))
	db.commit()
	return redirect(url_for('blog.index'))


@bp.route('/q/<hashparam>', methods=('GET', 'POST'))
@login_required
def home(hashparam=None):
    db = get_db()
    print(hashparam)
    posts = db.execute(
		'SELECT p.id, body, created, author_id, username, filename, hash'
		' FROM post p JOIN user u ON p.author_id = u.id'
		' WHERE hash = "{}"'.format(hashparam)).fetchone()
    return render_template('blog/article.html', post=posts)
