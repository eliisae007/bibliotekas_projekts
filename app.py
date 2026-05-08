import os
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Tas automātiski uztaisīs mapi, ja tās vēl nav, lai nerodas kļūdas
os.makedirs('static/gramatas', exist_ok=True)

# Funkcija, lai uztaisītu datubāzi no nulles, ja tās vēl nav
def init_db():
    # Pārbaudam vai fails jau eksistē, lai nedzēstu datus katru reizi
    db_exists = os.path.exists('database.db')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Te mēs sataisām tās 4 tabulas, kas prasītas kritērijos
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS authors (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS zanri (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            title TEXT NOT NULL, 
            gads INTEGER,
            author_id INTEGER, 
            zanrs_id INTEGER,
            bilde TEXT,
            FOREIGN KEY(author_id) REFERENCES authors(id), 
            FOREIGN KEY(zanrs_id) REFERENCES zanri(id)
        );
        CREATE TABLE IF NOT EXISTS borrowers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, book_id INTEGER);
    ''')
    
    # Ja datubāze tikko uztaisīta, ieliekam tos 7 žanrus
    if not db_exists:
        cursor.executescript('''
            INSERT INTO zanri (name) VALUES ('Romāns'), ('Dzeja'), ('Luga'), ('Detektīvs'), 
                                           ('Fantāzija'), ('Zinātne'), ('Biogrāfija');
        ''')
    conn.commit()
    conn.close()

# Palaižam DB iestatīšanu uzreiz pie starta
init_db()

# Vienkārša funkcija, lai katru reizi nav jāraksta pieslēgšanās
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row # Šitas palīdz dabūt datus pēc nosaukumiem
    return conn

@app.route('/') # Galvenā lapa (index)
def index():
    return render_template('index.html')

@app.route('/gramatas') # Grāmatu saraksta skats
def gramatas():
    conn = get_db()
    # Te mēs savienojam tabulas (JOIN), lai redzētu autora vārdu un žanru, nevis tikai ID
    query = '''
        SELECT books.*, authors.name as author, zanri.name as zanrs 
        FROM books 
        JOIN authors ON books.author_id = authors.id 
        JOIN zanri ON books.zanrs_id = zanri.id
    '''
    books = conn.execute(query).fetchall()
    conn.close()
    return render_template('gramatas.html', books=books)

@app.route('/pievienot', methods=('GET', 'POST'))
def pievienot():
    conn = get_db()
    if request.method == 'POST':
        title = request.form['title']
        gads = request.form['gads']
        author_name = request.form['author']
        zanrs_id = request.form['zanrs_id']
        
        # --- BILDES APSTRĀDE (Jaunums) ---
        bilde = request.files.get('bilde') # Dabūjam failu no formas
        bildes_nosaukums = ""
        if bilde and bilde.filename:
            bildes_nosaukums = bilde.filename
            # Saglabājam bildi mapē
            bilde.save(f"static/gramatas/{bildes_nosaukums}")
        # ---------------------------------
        
        author = conn.execute('SELECT id FROM authors WHERE name = ?', (author_name,)).fetchone()
        if author:
            author_id = author['id']
        else:
            cur = conn.execute('INSERT INTO authors (name) VALUES (?)', (author_name,))
            author_id = cur.lastrowid
            
        # Pievienojam arī "bilde" datubāzē
        conn.execute('INSERT INTO books (title, gads, author_id, zanrs_id, bilde) VALUES (?, ?, ?, ?, ?)', 
                     (title, gads, author_id, zanrs_id, bildes_nosaukums))
        conn.commit()
        return redirect(url_for('gramatas'))
    
    zanri = conn.execute('SELECT * FROM zanri').fetchall()
    return render_template('pievienot.html', zanri=zanri)

@app.route('/rediget/<int:id>', methods=('GET', 'POST')) # Datu labošana
def rediget(id):
    conn = get_db()
    if request.method == 'POST':
        # Updeitojam tikai tos datus, ko ļaujam mainīt
        conn.execute('UPDATE books SET title=?, gads=?, zanrs_id=? WHERE id=?', 
                     (request.form['title'], request.form['gads'], request.form['zanrs_id'], id))
        conn.commit()
        return redirect(url_for('gramatas'))
    
    # Atrodam konkrēto grāmatu, ko gribam labot
    book = conn.execute('SELECT books.*, authors.name as author FROM books JOIN authors ON books.author_id = authors.id WHERE books.id=?', (id,)).fetchone()
    zanri = conn.execute('SELECT * FROM zanri').fetchall()
    return render_template('rediget.html', book=book, zanri=zanri)

@app.route('/dzest/<int:id>', methods=('POST',)) # Grāmatas dzēšana
def dzest(id):
    conn = get_db()
    conn.execute('DELETE FROM books WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('gramatas'))



if __name__ == '__main__':
    app.run(debug=True) # debug=True palīdz redzēt kļūdas, ja kaut kas salūzt

