from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, base64
from database import init_db, ajouter_patient, get_all_patients, get_db_path

app = Flask(__name__)
app.secret_key = "TP_INF232_SecretKey"

# ── PAGE ACCUEIL ──────────────────────────────
@app.route('/')
def index():
    patients = get_all_patients()
    total = len(patients)
    return render_template('index.html', patients=patients, total=total)

# ── FORMULAIRE DE COLLECTE ────────────────────
@app.route('/collecte', methods=['GET', 'POST'])
def collecte():
    if request.method == 'POST':
        f = request.form
        data = (
            f['nom'].upper(),
            f['prenom'].capitalize(),
            int(f['age']),
            f['sexe'],
            f['ville'].capitalize(),
            f.get('profession', ''),
            f['maladie'],
            f.get('symptomes', ''),
            float(f.get('temperature', 37.0)),
            int(f.get('tension_sys', 120)),
            int(f.get('tension_dia', 80)),
            float(f.get('poids', 0)),
            float(f.get('taille', 0)),
            f.get('fumeur', 'Non'),
            f.get('diabete', 'Non'),
            f.get('hypertension', 'Non'),
            f['date_collecte'],
            f.get('statut', 'En suivi')
        )
        ajouter_patient(data)
        flash("✅ Patient enregistré avec succès !")
        return redirect(url_for('index'))
    return render_template('collecte.html')

# ── ANALYSE DESCRIPTIVE ───────────────────────
@app.route('/analyse')
def analyse():
    conn = sqlite3.connect(get_db_path())
    df = pd.read_sql_query("SELECT * FROM patients", conn)
    conn.close()

    if df.empty:
        return render_template('analyse.html', message="Aucune donnée disponible.")

    stats = {
        'total'    : len(df),
        'age_moy'  : round(df['age'].mean(), 1),
        'age_min'  : int(df['age'].min()),
        'age_max'  : int(df['age'].max()),
        'temp_moy' : round(df['temperature'].mean(), 1),
        'maladies' : df['maladie'].nunique(),
        'villes'   : df['ville'].nunique(),
    }

    graphiques = []

    # Graphique 1 : Répartition par maladie
    fig, ax = plt.subplots(figsize=(6, 4), facecolor='#0D1B2A')
    ax.set_facecolor('#1A2E40')
    maladies = df['maladie'].value_counts()
    bars = ax.bar(maladies.index, maladies.values,
                  color=['#00C9A7','#FF6B6B','#FFE66D','#4ECDC4','#A8DADC'])
    ax.set_title('Répartition par Maladie', color='white', fontsize=13, pad=12)
    ax.tick_params(colors='white', labelsize=8)
    ax.set_ylabel('Nombre de cas', color='white')
    plt.xticks(rotation=30, ha='right')
    for spine in ax.spines.values():
        spine.set_edgecolor('#2A4A6A')
    plt.tight_layout()
    graphiques.append(fig_to_b64(fig))

    # Graphique 2 : Répartition par sexe (camembert)
    fig, ax = plt.subplots(figsize=(5, 4), facecolor='#0D1B2A')
    sexes = df['sexe'].value_counts()
    ax.pie(sexes.values, labels=sexes.index, autopct='%1.1f%%',
           colors=['#4ECDC4','#FF6B6B'], textprops={'color':'white'})
    ax.set_title('Répartition par Sexe', color='white', fontsize=13, pad=12)
    plt.tight_layout()
    graphiques.append(fig_to_b64(fig))

    # Graphique 3 : Distribution des âges
    fig, ax = plt.subplots(figsize=(6, 4), facecolor='#0D1B2A')
    ax.set_facecolor('#1A2E40')
    ax.hist(df['age'], bins=8, color='#00C9A7', edgecolor='#0D1B2A')
    ax.set_title('Distribution des Âges', color='white', fontsize=13, pad=12)
    ax.set_xlabel('Âge', color='white')
    ax.set_ylabel('Fréquence', color='white')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_edgecolor('#2A4A6A')
    plt.tight_layout()
    graphiques.append(fig_to_b64(fig))

    # Graphique 4 : Statut des patients
    fig, ax = plt.subplots(figsize=(5, 4), facecolor='#0D1B2A')
    ax.set_facecolor('#1A2E40')
    statuts = df['statut'].value_counts()
    ax.barh(statuts.index, statuts.values,
            color=['#00C9A7','#FFE66D','#FF6B6B'])
    ax.set_title('Statut des Patients', color='white', fontsize=13, pad=12)
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_edgecolor('#2A4A6A')
    plt.tight_layout()
    graphiques.append(fig_to_b64(fig))

    return render_template('analyse.html', stats=stats, graphiques=graphiques)

# ── UTILITAIRE ────────────────────────────────
def fig_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    img = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img

# ── LANCEMENT ─────────────────────────────────
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
