import sqlite3

def populate():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # 1. Pievienojam žanrus, ja tie vēl nav
    zanri = [('Fantāzija',), ('Bērnu literatūra',), ('Piedzīvojumi',)]
    cursor.executemany('INSERT OR IGNORE INTO zanri (name) VALUES (?)', zanri)
    
    # Dabūjam žanru ID
    cursor.execute("SELECT id FROM zanri WHERE name='Fantāzija'")
    f_id = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM zanri WHERE name='Bērnu literatūra'")
    b_id = cursor.fetchone()[0]

    # 2. Pievienojam autorus
    authors = [('J.K. Rowling',), ('Jeff Kinney',)]
    cursor.executemany('INSERT OR IGNORE INTO authors (name) VALUES (?)', authors)
    
    # Dabūjam autoru ID
    cursor.execute("SELECT id FROM authors WHERE name='J.K. Rowling'")
    rowling_id = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM authors WHERE name='Jeff Kinney'")
    kinney_id = cursor.fetchone()[0]

    # 3. Grāmatu saraksts (nosaukums, gads, autora_id, žanra_id, bilde)
    # Bildes atstājam tukšas vai ierakstām failu nosaukumus, kurus tu vēlāk pievienosi static/gramatas mapē
    books = [
        ('Harijs Poters un Filozofu akmens', 1997, rowling_id, f_id, ''),
        ('Harijs Poters un Noslēpumu kambaris', 1998, rowling_id, f_id, ''),
        ('Harijs Poters un Azkabanas gūsteknis', 1999, rowling_id, f_id, ''),
        ('Grega dienasgrāmata 1: Nožēlojamais Gregs', 2007, kinney_id, b_id, ''),
        ('Grega dienasgrāmata 2: Rodriks rullē', 2008, kinney_id, b_id, ''),
        ('Grega dienasgrāmata 3: Pēdējais piliens', 2009, kinney_id, b_id, '')
    ]

    cursor.executemany('''
        INSERT INTO books (title, gads, author_id, zanrs_id, bilde) 
        VALUES (?, ?, ?, ?, ?)
    ''', books)

    conn.commit()
    conn.close()
    print("Dati veiksmīgi pievienoti! Tagad vari apskatīt mājaslapu.")

if __name__ == '__main__':
    populate()