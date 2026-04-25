import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# ── CONFIG PAGE ──────────────────────────────
st.set_page_config(
    page_title="SantéData — Surveillance Épidémiologique",
    page_icon="🏥",
    layout="wide"
)

DB_PATH = "health_data.db"

# ── BASE DE DONNÉES ───────────────────────────
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

def get_df():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM patients", conn)
    conn.close()
    return df

init_db()

# ── STYLE CSS ────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0D1B2A; }
    .stApp { background-color: #0D1B2A; color: #E8F4F8; }
    h1, h2, h3 { color: #00C9A7 !important; }
    .metric-card {
        background: #1A2E40;
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid #00C9A7;
        text-align: center;
    }
    .stButton>button {
        background-color: #00C9A7;
        color: #0D1B2A;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 10px 25px;
    }
    .stButton>button:hover {
        background-color: #4ECDC4;
        color: #0D1B2A;
    }
</style>
""", unsafe_allow_html=True)

# ── NAVIGATION ────────────────────────────────
st.sidebar.image("https://img.icons8.com/emoji/96/hospital-emoji.png", width=80)
st.sidebar.title("🏥 SANTÉDATA")
st.sidebar.markdown("**Surveillance Épidémiologique**")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigation", [
    "🏠 Tableau de Bord",
    "📋 Collecte de Données",
    "📊 Analyse Descriptive"
])

st.sidebar.markdown("---")
st.sidebar.markdown("*TP INF232 EC2*")
st.sidebar.markdown("*Application Santé Publique*")

# ══════════════════════════════════════════════
#  PAGE 1 : TABLEAU DE BORD
# ══════════════════════════════════════════════
if page == "🏠 Tableau de Bord":
    st.title("📊 Tableau de Bord")
    st.markdown("Bienvenue sur **SantéData** — Système de Surveillance Épidémiologique")
    st.markdown("---")

    df = get_df()

    if df.empty:
        st.warning("⚠️ Aucun patient enregistré. Allez dans **Collecte de Données** pour commencer.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👥 Total Patients", len(df))
        with col2:
            st.metric("🦠 Maladies", df['maladie'].nunique())
        with col3:
            st.metric("🏙️ Villes", df['ville'].nunique())
        with col4:
            st.metric("🌡️ Temp. Moy.", f"{df['temperature'].mean():.1f}°C")

        st.markdown("---")
        st.subheader("🗂️ Liste des Patients")
        st.dataframe(
            df[['nom','prenom','age','sexe','ville','maladie','temperature','statut','date_collecte']],
            use_container_width=True,
            hide_index=True
        )

# ══════════════════════════════════════════════
#  PAGE 2 : COLLECTE
# ══════════════════════════════════════════════
elif page == "📋 Collecte de Données":
    st.title("📋 Collecte de Données Patient")
    st.markdown("Remplissez le formulaire pour enregistrer un nouveau patient.")
    st.markdown("---")

    with st.form("form_patient", clear_on_submit=True):
        st.subheader("👤 Identité")
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom *")
            age = st.number_input("Âge *", min_value=0, max_value=120, value=25)
            ville = st.text_input("Ville *")
        with col2:
            prenom = st.text_input("Prénom *")
            sexe = st.selectbox("Sexe *", ["Masculin", "Féminin"])
            profession = st.text_input("Profession")

        st.subheader("🩺 Informations Cliniques")
        col3, col4 = st.columns(2)
        with col3:
            maladie = st.text_input("Maladie diagnostiquée *")
            temperature = st.number_input("Température (°C)", 35.0, 42.0, 37.0, step=0.1)
            tension_sys = st.number_input("Tension systolique", 60, 250, 120)
            poids = st.number_input("Poids (kg)", 0.0, 300.0, 70.0)
        with col4:
            symptomes = st.text_area("Symptômes observés")
            tension_dia = st.number_input("Tension diastolique", 40, 150, 80)
            taille = st.number_input("Taille (cm)", 0.0, 250.0, 170.0)

        st.subheader("📁 Antécédents & Statut")
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            fumeur = st.selectbox("Fumeur", ["Non", "Oui"])
        with col6:
            diabete = st.selectbox("Diabète", ["Non", "Oui"])
        with col7:
            hypertension = st.selectbox("Hypertension", ["Non", "Oui"])
        with col8:
            statut = st.selectbox("Statut", ["En suivi", "Guéri", "Chronique"])

        date_collecte = st.date_input("Date de collecte", datetime.now())

        submitted = st.form_submit_button("💾 Enregistrer le patient")

        if submitted:
            if not nom or not prenom or not maladie or not ville:
                st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
            else:
                data = (
                    nom.upper(), prenom.capitalize(),
                    age, sexe, ville.capitalize(), profession,
                    maladie, symptomes, temperature,
                    tension_sys, tension_dia, poids, taille,
                    fumeur, diabete, hypertension,
                    str(date_collecte), statut
                )
                ajouter_patient(data)
                st.success("✅ Patient enregistré avec succès !")
                st.balloons()

# ══════════════════════════════════════════════
#  PAGE 3 : ANALYSE
# ══════════════════════════════════════════════
elif page == "📊 Analyse Descriptive":
    st.title("📊 Analyse Descriptive des Données")
    st.markdown("Statistiques et visualisations des données collectées.")
    st.markdown("---")

    df = get_df()

    if df.empty:
        st.warning("⚠️ Aucune donnée disponible. Commencez par collecter des données.")
    else:
        # Statistiques
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👥 Total", len(df))
        with col2:
            st.metric("📅 Âge moyen", f"{df['age'].mean():.1f} ans")
        with col3:
            st.metric("🌡️ Temp. moy.", f"{df['temperature'].mean():.1f}°C")
        with col4:
            st.metric("🦠 Maladies", df['maladie'].nunique())

        col5, col6, col7 = st.columns(3)
        with col5:
            st.metric("📉 Âge min", f"{df['age'].min()} ans")
        with col6:
            st.metric("📈 Âge max", f"{df['age'].max()} ans")
        with col7:
            st.metric("🏙️ Villes", df['ville'].nunique())

        st.markdown("---")
        st.subheader("📈 Visualisations")

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            # Graphique 1 : Maladies
            fig1 = px.bar(
                df['maladie'].value_counts().reset_index(),
                x='maladie', y='count',
                title="Répartition par Maladie",
                color='maladie',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig1.update_layout(
                plot_bgcolor='#1A2E40',
                paper_bgcolor='#0D1B2A',
                font_color='white',
                showlegend=False
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col_g2:
            # Graphique 2 : Sexe
            fig2 = px.pie(
                df, names='sexe',
                title="Répartition par Sexe",
                color_discrete_sequence=['#00C9A7','#FF6B6B']
            )
            fig2.update_layout(
                plot_bgcolor='#1A2E40',
                paper_bgcolor='#0D1B2A',
                font_color='white'
            )
            st.plotly_chart(fig2, use_container_width=True)

        col_g3, col_g4 = st.columns(2)

        with col_g3:
            # Graphique 3 : Âges
            fig3 = px.histogram(
                df, x='age', nbins=8,
                title="Distribution des Âges",
                color_discrete_sequence=['#00C9A7']
            )
            fig3.update_layout(
                plot_bgcolor='#1A2E40',
                paper_bgcolor='#0D1B2A',
                font_color='white'
            )
            st.plotly_chart(fig3, use_container_width=True)

        with col_g4:
            # Graphique 4 : Statut
            fig4 = px.bar(
                df['statut'].value_counts().reset_index(),
                x='count', y='statut',
                title="Statut des Patients",
                orientation='h',
                color='statut',
                color_discrete_sequence=['#00C9A7','#FFE66D','#FF6B6B']
            )
            fig4.update_layout(
                plot_bgcolor='#1A2E40',
                paper_bgcolor='#0D1B2A',
                font_color='white',
                showlegend=False
            )
            st.plotly_chart(fig4, use_container_width=True)

        st.markdown("---")
        st.subheader("📋 Tableau Statistique Complet")
        st.dataframe(
            df[['age','temperature','tension_sys','tension_dia','poids','taille']]
            .describe().round(2),
            use_container_width=True
        )
