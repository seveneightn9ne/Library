import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing


# configuration
DATABASE = 'db/library.db'
DEBUG = True
SECRET_KEY = '\x86\x98\xc1\xe3\xe6e_\xb6u\xaa\x86}\xc3\x9a\xc1"\x98\x16\xd4]\x9e\x81\x97\xc6C$p\x17J\x06\x8c\xbc\x16&6!\x17\xe6_aV*\xdd\xae'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def browse():
    cur = g.db.execute('select title, author from books order by id desc')
    books = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('browse.html', books=books)

@app.route('/add', methods=['POST'])
def add_book():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into books (title, author) values (?, ?)',
                 [request.form['title'], request.form['author']])
    g.db.commit()
    flash('New book was successfully added')
    return redirect(url_for('browse'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('browse'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('browse'))

if __name__ == '__main__':
    app.run()