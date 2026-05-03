import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_and_clean_data, extract_skills
from openai import OpenAI

st.set_page_config(layout="wide", page_title="Emploi Sénégal IA", page_icon="🇸🇳")

# Chargement
df = load_and_clean_data("data/dataset_concoursn.csv")

# Sidebar
st.sidebar.header("⚙️ Filtres")
villes = st.sidebar.multiselect("Ville", options=df['Ville'].unique(), default=df['Ville'].unique())
df_f = df[df['Ville'].isin(villes)]

st.title("🇸🇳 Dashboard Emploi & Assistant IA")

tab1, tab2 = st.tabs(["📊 Statistiques", "🤖 Assistant IA"])

with tab1:
    c1, c2, c3 = st.columns(3)
    c1.metric("Offres", len(df_f))
    c2.metric("Entreprises", df_f['Entreprise'].nunique())
    c3.metric("Villes", df_f['Ville'].nunique())
    
    # Graphique des recruteurs
    top_recruteurs = df_f['Entreprise'].value_counts().head(10).reset_index()
    top_recruteurs.columns = ['Entreprise', 'Nombre d\'offres']
    fig = px.bar(top_recruteurs, x='Nombre d\'offres', y='Entreprise', orientation='h', title="Top 10 Recruteurs")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Posez vos questions à l'IA")
    key = st.secrets.get("OPENAI_API_KEY")
    if not key:
        st.warning("⚠️ Veuillez configurer votre clé `OPENAI_API_KEY` dans les secrets de Streamlit.")
    else:
        client = OpenAI(api_key=key)
        if "messages" not in st.session_state: st.session_state.messages = []
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        
        if p := st.chat_input("Ex: Quelles sont les compétences pour Dakar ?"):
            st.session_state.messages.append({"role": "user", "content": p})
            with st.chat_message("user"): st.markdown(p)
            
            # Contexte réduit pour l'IA
            context = df_f[['Poste', 'Entreprise', 'Competences']].head(15).to_string()
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": f"Tu es un expert emploi au Sénégal. Voici les données : {context}"},
                          {"role": "user", "content": p}]
            )
            ans = resp.choices[0].message.content
            with st.chat_message("assistant"): st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
