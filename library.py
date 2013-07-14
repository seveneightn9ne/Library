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

# enable LESS CSS
if app.debug:
    from flaskext.lesscss import lesscss
    lesscss(app)

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

# def get_db():
#     db = getattr(g, '_database', None)
#     if db is None:
#         # db = g._database = connect_to_database()
#         db = g._database = connect_db()
#     return db

@app.before_request
def before_request():
    g.db = connect_db()
    g.db.row_factory = sqlite3.Row

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    """
    Easily query the datbase.

    From: http://flask.pocoo.org/docs/patterns/sqlite3/#sqlite3
    """
    cur = g.db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route('/')
def browse():
    books = query_db('select title, author from books order by id desc')
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
    # Use the following line to run app publicly:
    # app.run(host='0.0.0.0')
