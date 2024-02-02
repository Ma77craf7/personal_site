import sqlite3 as sq
import hashlib

def init_db(filename: str) -> None:
    conn = sq.connect(filename)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS secrets (id INTEGER PRIMARY KEY, secret TEXT NOT NULL, description TEXT NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, title TEXT NOT NULL, content TEXT NOT NULL, icon NULL)")
    conn.commit()

def encrypt(plaintext, password):
    """Encrypts the plaintext using XOR with the given password."""
    if not plaintext or not password:
        raise ValueError("Both plaintext and password must be non-empty.")

    encrypted = [ord(p) ^ ord(password[i % len(password)]) for i, p in enumerate(plaintext)]
    return bytes(encrypted)

def decrypt(encrypted_bytes, password):
    """Decrypts the XOR-encrypted bytes using the given password."""
    if not encrypted_bytes or not password:
        raise ValueError("Both encrypted_bytes and password must be non-empty.")

    decrypted = [chr(e ^ ord(password[i % len(password)])) for i, e in enumerate(list(encrypted_bytes))]
    return ''.join(decrypted)

def add_secret(secret: str, description: str, filename: str) -> None:
    conn = sq.connect(filename)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO secrets (secret, description) VALUES (?, ?)''', (encrypt(secret), description))
    conn.commit()
    conn.close()

def get_secret(description: str, filename: str) -> str:
    conn = sq.connect(filename)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM secrets WHERE description = ?', (description,))
    risultati = cursor.fetchall()
    conn.close()

    if risultati:
        encrypted_secret = risultati[0][1]
        return decrypt(encrypted_secret)
    else:
        return "Secret not found"

def verify_secret(type,request)-> bool:
    if type==1:
        secret = get_secret('github notes webhook')
    else:
        return False
    
    if 'X-Hub-Signature' not in request.headers:
        return False

    signature = request.headers.get('X-Hub-Signature')[5:]  # Remove 'sha1=' prefix
    data = request.get_data()

    # Create the expected signature
    expected_signature = hashlib.sha1(secret + data).hexdigest()

    return signature == expected_signature


def add_post(post,filename:str)->None:
    conn = sq.connect(filename)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO posts (title, content) VALUES (?, ?)''', (post["title"], post["content"]))
    conn.commit()
    conn.close()

def get_posts(filename:str)->list:
    conn = sq.connect(filename)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts')
    risultati = cursor.fetchall()
    conn.close()

    posts=[]
    for risultato in risultati:
        posts.append({"id":risultato[0],"title":risultato[1],"content":risultato[2],"icon":risultato[3]})
    return posts

def delete_post(post:tuple, filename:str)-> None:
    conn = sq.connect(filename)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM posts WHERE id = ?', (post[0],))
    conn.commit()
    conn.close()
