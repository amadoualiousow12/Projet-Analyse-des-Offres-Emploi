
import pandas as pd
import re
import streamlit as st
from collections import Counter

@st.cache_data
def load_and_clean_data(filepath):
    df_raw = pd.read_csv(filepath)
    df = df_raw.copy()

    # A. Supprimer les lignes de résumé (ex: "Les 27 offres d’emploi...")
    df = df[~df['Intitulé du poste'].str.contains(r"Les \d+ offres d’emploi", na=False)]

    # B. Ajouter un identifiant unique (ID)
    df.insert(0, 'ID', range(1, len(df) + 1))

    # C. Nettoyage de la colonne 'Entreprise'
    def clean_company(row):
        company = str(row['Entreprise']).strip()
        title = str(row['Intitulé du poste'])

        parasites = ["postuler", "URGENT", "N/A", "nan", "postuler à cette offre"]

        if any(p.lower() in company.lower() for p in parasites) or company.lower() in ["", "nan"]:
            # Extraction depuis le titre
            match = re.search(r'^(.*?) recrute', title)
            if match:
                return match.group(1).strip()
            return "Société de la place"

        # Corrections spécifiques
        if company == "Espagne" and "Médecins du Monde" in title: return "Médecins du Monde"
        if company == "Conseils" and "Analysis & Conseils" in title: return "Analysis & Conseils"

        return company

    df['Entreprise'] = df.apply(clean_company, axis=1)

    # D. Gestion des valeurs manquantes
    df['Ville'] = df['Ville'].fillna('Sénégal (Multi-sites)').replace('N/A', 'Sénégal (Multi-sites)')
    df['Type de contrat'] = df['Type de contrat'].fillna('Non spécifié').replace('N/A', 'Non spécifié')
    df['Compétences demandées'] = df['Compétences demandées'].fillna('Non spécifié')

    # E. Conversion de la date
    df['Date de publication'] = pd.to_datetime(df['Date de publication'], errors='coerce')

    # F. Amélioration des noms de colonnes (bonus)
    df = df.rename(columns={
        'Intitulé du poste': 'Intitule_du_poste',
        'Entreprise': 'Entreprise',
        'Ville': 'Ville',
        'Type de contrat': 'Type_de_contrat',
        'Date de publication': 'Date_de_publication',
        'Compétences demandées': 'Competences_demandees'
    })

    return df

def extract_skills(text):
    if pd.isna(text): return []
    # Liste de compétences plus exhaustive et adaptée au contexte des offres d'emploi
    common_skills = [
        'Gestion', 'Finance', 'Comptabilité', 'Vente', 'Marketing', 'Informatique', 'Anglais', 'Management', 
        'Communication', 'Audit', 'RH', 'Logistique', 'Commerce', 'Développement', 'Projet', 'Digital', 
        'Technique', 'Analyse', 'Conseil', 'Juridique', 'Ressources Humaines', 'Achats', 'Production', 
        'Qualité', 'Sécurité', 'Environnement', 'Maintenance', 'Opérations', 'Stratégie', 'Client', 
        'Relationnel', 'Rédaction', 'Formation', 'Recrutement', 'Reporting', 'Budgétisation', 'Fiscalité',
        'Data', 'Python', 'Excel', 'Word', 'PowerPoint', 'SQL', 'BI', 'Power BI', 'Tableau', 'SAP', 'Oracle',
        'JavaScript', 'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'PHP', 'Java', 'C++', 'C#',
        'Cloud', 'AWS', 'Azure', 'GCP', 'Cybersécurité', 'Réseaux', 'Systèmes', 'Base de données', 'ERP',
        'CRM', 'E-commerce', 'Social Media', 'SEO', 'SEA', 'Content Marketing', 'Graphisme', 'Design',
        'UX/UI', 'Agile', 'Scrum', 'Kanban', 'Leadership', 'Négociation', 'Résolution de problèmes',
        'Esprit d\'équipe', 'Autonomie', 'Rigueur', 'Créativité', 'Adaptabilité', 'Sens de l\'organisation'
    ]
    
    # Convertir le texte en minuscules pour une correspondance insensible à la casse
    text_lower = text.lower()
    
    found_skills = []
    for skill in common_skills:
        # Utiliser des expressions régulières pour correspondre à des mots entiers ou des phrases
        # Cela évite de matcher 'gestion' dans 'suggestion' par exemple
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
            
    return found_skills

