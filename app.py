
import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import re
from utils import load_and_clean_data, extract_skills

# Configuration de la page Streamlit
st.set_page_config(layout="wide", page_title="Dashboard Offres d'Emploi Sénégal", page_icon="🇸🇳")

# --- Chargement et nettoyage des données ---
DATA_PATH = "data/dataset_concoursn.csv"
df = load_and_clean_data(DATA_PATH)

# --- Sidebar pour les filtres ---
st.sidebar.header("⚙️ Filtres")

# Filtre par secteur (basé sur les intitulés de poste pour l'exemple, à affiner si une colonne 'Secteur' existe)
# Pour l'instant, on va extraire des mots clés des intitulés de poste pour simuler des secteurs
def extract_sectors(title):
    title_lower = title.lower()
    if 'informatique' in title_lower or 'développeur' in title_lower or 'data' in title_lower: return 'IT/Tech'
    if 'finance' in title_lower or 'comptable' in title_lower or 'audit' in title_lower: return 'Finance/Comptabilité'
    if 'marketing' in title_lower or 'commercial' in title_lower or 'vente' in title_lower: return 'Marketing/Vente'
    if 'rh' in title_lower or 'ressources humaines' in title_lower: return 'Ressources Humaines'
    if 'logistique' in title_lower or 'transport' in title_lower: return 'Logistique/Transport'
    if 'santé' in title_lower or 'médecin' in title_lower or 'infirmier' in title_lower: return 'Santé'
    if 'éducation' in title_lower or 'enseignant' in title_lower: return 'Éducation'
    if 'ingénieur' in title_lower or 'technique' in title_lower: return 'Ingénierie/Technique'
    if 'gestion' in title_lower or 'manager' in title_lower: return 'Management/Gestion'
    return 'Autres'

df['Secteur'] = df['Intitule_du_poste'].apply(extract_sectors)

selected_sectors = st.sidebar.multiselect(
    "Secteur",
    options=df['Secteur'].unique().tolist(),
    default=df['Secteur'].unique().tolist()
)

# Filtre par type de contrat
selected_contract_types = st.sidebar.multiselect(
    "Type de contrat",
    options=df['Type_de_contrat'].unique().tolist(),
    default=df['Type_de_contrat'].unique().tolist()
)

# Filtre par localisation (Ville)
selected_cities = st.sidebar.multiselect(
    "Ville",
    options=df['Ville'].unique().tolist(),
    default=df['Ville'].unique().tolist()
)

# Application des filtres
df_filtered = df[
    df['Secteur'].isin(selected_sectors) &
    df['Type_de_contrat'].isin(selected_contract_types) &
    df['Ville'].isin(selected_cities)
]

# --- Corps de l'application ---
st.title("📊 Dashboard des Offres d'Emploi au Sénégal")
st.markdown("--- ")

# 1. Dashboard principal (KPIs)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Offres", value=len(df_filtered))

with col2:
    st.metric(label="Secteurs Uniques", value=df_filtered['Secteur'].nunique())

with col3:
    st.metric(label="Entreprises Uniques", value=df_filtered['Entreprise'].nunique())

with col4:
    # Top métiers les plus demandés (basé sur les intitulés de poste)
    top_jobs = df_filtered['Intitule_du_poste'].value_counts().head(1).index[0] if not df_filtered.empty else "N/A"
    st.metric(label="Top Métier", value=top_jobs)

st.markdown("--- ")

# 2. Visualisations
st.header("📈 Visualisations")

tab1, tab2, tab3 = st.tabs(["Secteurs", "Compétences", "Évolution Temporelle"])

with tab1:
    st.subheader("Répartition des Offres par Secteur")
    if not df_filtered.empty:
        sector_counts = df_filtered['Secteur'].value_counts().reset_index()
        sector_counts.columns = ['Secteur', 'Nombre d\'offres']
        fig_sector = px.bar(sector_counts, x='Nombre d\'offres', y='Secteur', orientation='h', 
                            title='Nombre d\'offres par Secteur', color='Nombre d\'offres',
                            color_continuous_scale=px.colors.sequential.Viridis)
        st.plotly_chart(fig_sector, use_container_width=True)
    else:
        st.info("Aucune donnée pour les filtres sélectionnés.")

with tab2:
    st.subheader("Top Compétences Demandées")
    if not df_filtered.empty:
        all_extracted_skills = []
        # Appliquer extract_skills sur la colonne 'Competences_demandees'
        df_filtered['Competences_demandees'].apply(lambda x: all_extracted_skills.extend(extract_skills(x)))
        
        if all_extracted_skills:
            top_skills_df = pd.DataFrame(Counter(all_extracted_skills).most_common(15), columns=['Compétence', 'Fréquence'])
            fig_skills = px.bar(top_skills_df, x='Fréquence', y='Compétence', orientation='h',
                                title='Top 15 des Compétences les plus recherchées', color='Fréquence',
                                color_continuous_scale=px.colors.sequential.Plasma)
            st.plotly_chart(fig_skills, use_container_width=True)
        else:
            st.info("Aucune compétence trouvée pour les offres filtrées.")
    else:
        st.info("Aucune donnée pour les filtres sélectionnés.")

with tab3:
    st.subheader("Évolution Mensuelle des Offres")
    if not df_filtered.empty and 'Date_de_publication' in df_filtered.columns:
        df_filtered_valid_dates = df_filtered.dropna(subset=['Date_de_publication'])
        if not df_filtered_valid_dates.empty:
            df_filtered_valid_dates['Mois'] = df_filtered_valid_dates['Date_de_publication'].dt.to_period('M')
            evolution = df_filtered_valid_dates.groupby('Mois').size().reset_index(name='Nombre d\'offres')
            evolution['Mois'] = evolution['Mois'].astype(str)
            fig_evolution = px.line(evolution, x='Mois', y='Nombre d\'offres', markers=True,
                                    title='Évolution Mensuelle des Offres', 
                                    labels={'Mois': 'Mois de publication', 'Nombre d\'offres': 'Nombre d\'offres'})
            st.plotly_chart(fig_evolution, use_container_width=True)
        else:
            st.info("Aucune date de publication valide pour l'évolution temporelle.")
    else:
        st.info("Aucune donnée ou colonne 'Date_de_publication' manquante pour les filtres sélectionnés.")

st.markdown("--- ")

# 3. Tableau interactif des offres
st.header("📋 Offres d'Emploi Filtrées")

search_query = st.text_input("Rechercher par mot-clé dans l'intitulé du poste ou l'entreprise", "")

if search_query:
    df_filtered_search = df_filtered[
        df_filtered['Intitule_du_poste'].str.contains(search_query, case=False, na=False) |
        df_filtered['Entreprise'].str.contains(search_query, case=False, na=False)
    ]
else:
    df_filtered_search = df_filtered

st.dataframe(df_filtered_search[['Intitule_du_poste', 'Entreprise', 'Ville', 'Type_de_contrat', 'Date_de_publication', 'Competences_demandees']], use_container_width=True)

# 4. Bouton d'export
st.markdown("--- ")
st.header("⬇️ Export des Données")

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

if not df_filtered_search.empty:
    csv = convert_df_to_csv(df_filtered_search)
    st.download_button(
        label="Télécharger les données filtrées en CSV",
        data=csv,
        file_name='offres_emploi_filtrees.csv',
        mime='text/csv',
    )
else:
    st.info("Aucune donnée à exporter pour les filtres et la recherche actuels.")
    

