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
                 uploaded_at REAL,
                 current_version INTEGER DEFAULT 1,
                 created_by TEXT
                 )''')
    c.execute('''CREATE TABLE IF NOT EXISTS asset_versions (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 asset_id INTEGER,
                 version_number INTEGER,
                 path TEXT,
                 operation TEXT,
                 operation_params TEXT,
                 created_at REAL,
                 created_by TEXT,
                 FOREIGN KEY (asset_id) REFERENCES assets (id)
                 )''')
    c.execute('''CREATE TABLE IF NOT EXISTS asset_comments (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 asset_id INTEGER,
                 version_id INTEGER,
                 comment TEXT,
                 created_at REAL,
                 created_by TEXT,
                 FOREIGN KEY (asset_id) REFERENCES assets (id),
                 FOREIGN KEY (version_id) REFERENCES asset_versions (id)
                 )''')
    conn.commit()
    conn.close()

def save_asset(db_path, filepath, label, created_by=None):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    current_time = time.time()
    c.execute('INSERT INTO assets (label, path, uploaded_at, created_by) VALUES (?, ?, ?, ?)',
              (label, filepath, current_time, created_by))
    asset_id = c.lastrowid

    # Create initial version
    c.execute('INSERT INTO asset_versions (asset_id, version_number, path, operation, created_at, created_by) VALUES (?, ?, ?, ?, ?, ?)',
              (asset_id, 1, filepath, 'upload', current_time, created_by))

    conn.commit()
    conn.close()
    return asset_id

def list_assets(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    rows = c.execute('SELECT id, label, path, uploaded_at FROM assets ORDER BY uploaded_at DESC').fetchall()
    conn.close()
    return [{'id': r[0], 'label': r[1], 'path': r[2], 'uploaded_at': r[3]} for r in rows]

def get_asset_path(db_path, asset_id, version=None):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    if version is None:
        # Get current version
        row = c.execute('SELECT path FROM assets WHERE id=?', (asset_id,)).fetchone()
    else:
        # Get specific version
        row = c.execute('SELECT path FROM asset_versions WHERE asset_id=? AND version_number=?', (asset_id, version)).fetchone()
    conn.close()
    return row[0] if row else None

def save_asset_version(db_path, asset_id, new_path, operation, operation_params=None, created_by=None):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Get current version number
    row = c.execute('SELECT current_version FROM assets WHERE id=?', (asset_id,)).fetchone()
    if not row:
        conn.close()
        return None

    new_version = row[0] + 1
    current_time = time.time()

    # Insert new version
    c.execute('''INSERT INTO asset_versions (asset_id, version_number, path, operation, operation_params, created_at, created_by)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (asset_id, new_version, new_path, operation, operation_params, current_time, created_by))

    # Update asset current version and path
    c.execute('UPDATE assets SET current_version=?, path=? WHERE id=?', (new_version, new_path, asset_id))

    conn.commit()
    conn.close()
    return new_version

def get_asset_versions(db_path, asset_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    rows = c.execute('''SELECT version_number, operation, operation_params, created_at, created_by
                        FROM asset_versions WHERE asset_id=? ORDER BY version_number DESC''', (asset_id,)).fetchall()
    conn.close()
    return [{'version': r[0], 'operation': r[1], 'params': r[2], 'created_at': r[3], 'created_by': r[4]} for r in rows]

def add_asset_comment(db_path, asset_id, comment, version_id=None, created_by=None):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('INSERT INTO asset_comments (asset_id, version_id, comment, created_at, created_by) VALUES (?, ?, ?, ?, ?)',
              (asset_id, version_id, comment, time.time(), created_by))
    comment_id = c.lastrowid
    conn.commit()
    conn.close()
    return comment_id

def get_asset_comments(db_path, asset_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    rows = c.execute('''SELECT c.comment, c.created_at, c.created_by, v.version_number
                        FROM asset_comments c
                        LEFT JOIN asset_versions v ON c.version_id = v.id
                        WHERE c.asset_id=? ORDER BY c.created_at DESC''', (asset_id,)).fetchall()
    conn.close()
    return [{'comment': r[0], 'created_at': r[1], 'created_by': r[2], 'version': r[3]} for r in rows]
