import pandas as pd
import re
import streamlit as st
from collections import Counter

@st.cache_data
def load_and_clean_data(filepath):
    df = pd.read_csv(filepath)
    # Nettoyage des lignes de résumé
    df = df[~df['Intitulé du poste'].str.contains(r"Les \d+ offres d’emploi", na=False)]
    # ID unique
    df.insert(0, 'ID', range(1, len(df) + 1))
    # Nettoyage Entreprise
    def clean_company(row):
        c, t = str(row['Entreprise']).strip(), str(row['Intitulé du poste'])
        if any(p in c.lower() for p in ["postuler", "urgent", "n/a", "nan"]) or c.lower() in ["", "nan"]:
            match = re.search(r'^(.*?) recrute', t)
            return match.group(1).strip() if match else "Société de la place"
        return c
    df['Entreprise'] = df.apply(clean_company, axis=1)
    # Valeurs manquantes
    df['Ville'] = df['Ville'].fillna('Sénégal').replace('N/A', 'Sénégal')
    df['Type de contrat'] = df['Type de contrat'].fillna('Non spécifié')
    df['Date de publication'] = pd.to_datetime(df['Date de publication'], errors='coerce')
    return df.rename(columns={'Intitulé du poste': 'Poste', 'Compétences demandées': 'Competences'})

def extract_skills(text):
    if pd.isna(text): return []
    skills_list = ['Gestion', 'Finance', 'Comptabilité', 'Vente', 'Marketing', 'Informatique', 'Anglais', 'RH', 'Logistique', 'Python', 'Excel', 'Management']
    return [s for s in skills_list if s.lower() in str(text).lower()]
