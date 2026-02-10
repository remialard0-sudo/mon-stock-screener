import streamlit as st
import pandas as pd

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Screener Pro", layout="wide")

# 2. SYSTEME DE LOGIN SIMPLE
def check_password():
    """Retourne True si l'utilisateur a le bon mot de passe."""
    def password_entered():
        if st.session_state["password"] == st.secrets["PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # On ne garde pas le mdp en mémoire
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Premier chargement, on demande le mot de passe
        st.text_input(
            "Entrez votre clé d'accès", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Mot de passe incorrect
        st.text_input(
            "Entrez votre clé d'accès", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Clé d'accès incorrecte")
        return False
    else:
        # Mot de passe correct
        return True

if check_password():
    # 3. CHARGEMENT DES DONNÉES
    # Remplacez le lien ci-dessous par VOTRE lien Google Sheet CSV (Phase 1)
    sheet_url = "https://docs.google.com/spreadsheets/d/1kIqwYFKyynXh1YzOwQeReVyE4dTgQmNBh040FIKEvMM/edit?usp=sharing"
    
    @st.cache_data(ttl=600) # Mise en cache pour que ça aille vite (refresh toutes les 10min)
    def load_data():
        data = pd.read_csv(sheet_url)
        return data

    try:
        df = load_data()
        
        # 4. INTERFACE DU SCREENER
        st.title("📈 Stock Screener Premium")
        
        # Barre latérale (Sidebar) pour les filtres
        st.sidebar.header("Filtres de recherche")
        
        # Exemple de filtre : Secteur (S'adapte automatiquement à vos données)
        if 'Secteur' in df.columns:
            sector_list = df['Secteur'].unique().tolist()
            selected_sector = st.sidebar.multiselect('Secteur', sector_list, sector_list)
            if selected_sector:
                df = df[df['Secteur'].isin(selected_sector)]

        # Exemple de filtre : PER (Price Earning Ratio)
        if 'PER' in df.columns:
            min_per, max_per = st.sidebar.slider('PER (Ratio Cours/Bénéfice)', 
                                float(df['PER'].min()), float(df['PER'].max()), (0.0, 50.0))
            df = df[(df['PER'] >= min_per) & (df['PER'] <= max_per)]

        # 5. AFFICHAGE DES RÉSULTATS
        st.write(f"Actions trouvées : {len(df)}")
        st.dataframe(
            df, 
            use_container_width=True, 
            hide_index=True
        )
        
    except Exception as e:
        st.error(f"Erreur de chargement des données. Vérifiez le lien CSV. Erreur : {e}")
