import os
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def init_db():
    db_exists = os.path.exists('database.db')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS authors (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS zanri (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            title TEXT NOT NULL, 
            gads INTEGER,
            image TEXT DEFAULT 'default.jpg',
            author_id INTEGER, 
            zanrs_id INTEGER,
            FOREIGN KEY(author_id) REFERENCES authors(id), 
            FOREIGN KEY(zanrs_id) REFERENCES zanri(id)
        );
        CREATE TABLE IF NOT EXISTS borrowers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, book_id INTEGER);
    ''')
    
    if not db_exists:
        cursor.executescript('''
            INSERT INTO zanri (name) VALUES ('Romāns'), ('Dzeja'), ('Luga'), ('Detektīvs'), 
                                           ('Fantāzija'), ('Zinātne'), ('Biogrāfija');
        ''')
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row 
    return conn

@app.route('/') 
def index():
    return render_template('index.html')

@app.route('/gramatas') 
def gramatas():
    conn = get_db()
    query = '''
        SELECT books.*, authors.name as author, zanri.name as zanrs 
        FROM books 
        JOIN authors ON books.author_id = authors.id 
        JOIN zanri ON books.zanrs_id = zanri.id
    '''
    books = conn.execute(query).fetchall()
    conn.close()
    return render_template('gramatas.html', books=books)

@app.route('/par-mums')
def about():
    return render_template('par_mums.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/pievienot', methods=('GET', 'POST')) 
def pievienot():
    conn = get_db()
    if request.method == 'POST':
        title = request.form['title']
        gads = request.form['gads']
        author_name = request.form['author']
        zanrs_id = request.form['zanrs_id']
        image = request.form['image'] if request.form['image'] else 'default.jpg'
        
        author = conn.execute('SELECT id FROM authors WHERE name = ?', (author_name,)).fetchone()
        if author:
            author_id = author['id']
        else:
            cur = conn.execute('INSERT INTO authors (name) VALUES (?)', (author_name,))
            author_id = cur.lastrowid
            
        conn.execute('INSERT INTO books (title, gads, image, author_id, zanrs_id) VALUES (?, ?, ?, ?, ?)', 
                     (title, gads, image, author_id, zanrs_id))
        conn.commit()
        return redirect(url_for('gramatas')) 
    
    zanri = conn.execute('SELECT * FROM zanri').fetchall()
    return render_template('pievienot.html', zanri=zanri)

@app.route('/rediget/<int:id>', methods=('GET', 'POST')) 
def rediget(id):
    conn = get_db()
    if request.method == 'POST':
        conn.execute('UPDATE books SET title=?, gads=?, zanrs_id=?, image=? WHERE id=?', 
                     (request.form['title'], request.form['gads'], request.form['zanrs_id'], request.form['image'], id))
        conn.commit()
        return redirect(url_for('gramatas'))
    
    book = conn.execute('SELECT books.*, authors.name as author FROM books JOIN authors ON books.author_id = authors.id WHERE books.id=?', (id,)).fetchone()
    zanri = conn.execute('SELECT * FROM zanri').fetchall()
    return render_template('rediget.html', book=book, zanri=zanri)

@app.route('/dzest/<int:id>', methods=('POST',)) 
def dzest(id):
    conn = get_db()
    conn.execute('DELETE FROM books WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('gramatas'))

if __name__ == '__main__':
    app.run(debug=True)