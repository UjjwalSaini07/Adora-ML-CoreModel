import sqlite3, os, time
from pathlib import Path

def init_db(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS assets (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 label TEXT,
                 path TEXT,
                 uploaded_at REAL
                 )''')
    conn.commit()
    conn.close()

def save_asset(db_path, filepath, label):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('INSERT INTO assets (label, path, uploaded_at) VALUES (?, ?, ?)', (label, filepath, time.time()))
    asset_id = c.lastrowid
    conn.commit()
    conn.close()
    return asset_id

def list_assets(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    rows = c.execute('SELECT id, label, path, uploaded_at FROM assets ORDER BY uploaded_at DESC').fetchall()
    conn.close()
    return [{'id': r[0], 'label': r[1], 'path': r[2], 'uploaded_at': r[3]} for r in rows]

def get_asset_path(db_path, asset_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    row = c.execute('SELECT path FROM assets WHERE id=?', (asset_id,)).fetchone()
    conn.close()
    return row[0] if row else None
