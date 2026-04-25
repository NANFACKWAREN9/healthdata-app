import sqlite3
from datetime import datetime

DB_PATH = "health_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            nom           TEXT NOT NULL,
            prenom        TEXT NOT NULL,
            age           INTEGER NOT NULL,
            sexe          TEXT NOT NULL,
            ville         TEXT NOT NULL,
            profession    TEXT,
            maladie       TEXT NOT NULL,
            symptomes     TEXT,
            temperature   REAL,
            tension_sys   INTEGER,
            tension_dia   INTEGER,
            poids         REAL,
            taille        REAL,
            fumeur        TEXT DEFAULT 'Non',
            diabete       TEXT DEFAULT 'Non',
            hypertension  TEXT DEFAULT 'Non',
            date_collecte TEXT NOT NULL,
            statut        TEXT DEFAULT 'En suivi'
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Base de données créée avec succès !")

def ajouter_patient(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO patients
        (nom,prenom,age,sexe,ville,profession,maladie,symptomes,
         temperature,tension_sys,tension_dia,poids,taille,
         fumeur,diabete,hypertension,date_collecte,statut)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, data)
    conn.commit()
    conn.close()

def get_all_patients():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM patients ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_db_path():
    return DB_PATH

if __name__ == "__main__":
    init_db()

