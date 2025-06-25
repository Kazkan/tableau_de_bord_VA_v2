# import de streamlit
import streamlit as st
import os
import utils.read_files as rf
import utils.st_widget as sw
import utils.sidebar as sb
import json
import pandas as pd
import geopandas as gpd
from datetime import datetime
import datetime
from streamlit_folium import st_folium

#import de fonctions maisons
from utils import read_files as rf
from utils import figure as fi
from utils import st_widget as sw
from utils import folium_widget as fw

# nettoyage des session_state inutile
# liste des sessions_state à garder
session_state_keep = ["utilisateurs","utilisateur_courant","recharger_vue","vue_courante","recharger_contenu","parametre_vue","ref_systeme","rep_utilisateurs","them_desordre","cat_desordre",'categorie_desordre','suite_desordre']
# supression des données hors vue et hors liste
for object in st.session_state:
    if object not in session_state_keep and object.endswith(".json"):
        del st.session_state[object]   

# fonction de la barre latéral
sb.sidebar_content()

tab1, tab2 = st.tabs([":star:", ":gear:"])

with tab2:
    with st.container():
        st.title("Paramètres du tableau de bord")
        st.divider()
        # chargement du nombre de colonne si il existe
        if "tableau_de_bord_colonne.json" in st.session_state :
            st.session_state["defaut_tableau_de_bord_colonne"] =  st.session_state["tableau_de_bord_colonne.json"]
        else :
            st.session_state["defaut_tableau_de_bord_colonne"] = 1
        # chargement des tailles de colonne si il existe
        if "taille_des_colonnes.json" in st.session_state :
            st.session_state["defaut_taille_des_colonnes"] =  st.session_state["taille_des_colonnes.json"]
        else :
            st.session_state["defaut_taille_des_colonnes"] = []
            for i in range(st.session_state["defaut_tableau_de_bord_colonne"]):
                st.session_state["defaut_taille_des_colonnes"].append(1)

        st.subheader("Nombre de colonnes du tableau de bord")
        # parametrage
        st.session_state["tableau_de_bord_colonne"] = st.number_input("Nombre de colonnes du tableau de bord :",min_value=1,value=st.session_state["defaut_tableau_de_bord_colonne"], key="tdb_colonne_widget")
        # enregistrement
        if st.button("Sauvegarder dans la vue",key="but_save_tdb_colonne_desordre") :
            rf.enregistrer_element_session_state("tableau_de_bord_colonne",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/tableau_de_bord_colonne.json")
        st.divider()      

        # création de la liste pour l taille des colonnes
        st.subheader("Définir la largeur des colonnes")        
        st.session_state["taille_des_colonnes"] = []
        cols2= st.columns(st.session_state["tableau_de_bord_colonne"])
        for x in range(st.session_state["tableau_de_bord_colonne"]):
            with cols2[x]:
                # ajout d'une valeur par défaut si on ajoute des colonnes par rapport à la valeur par défaut
                if x > len(st.session_state["defaut_taille_des_colonnes"]) - 1:
                    st.session_state["defaut_taille_des_colonnes"].append(1)
                # largeur de la colonne
                st.session_state["taille_des_colonnes"].append(st.number_input("taille de la colonne "+str(x+1)+" :",min_value=1,value=st.session_state["defaut_taille_des_colonnes"][x], key="tdb_colonne_widget"+str(x)))
        # enregistrement des tailles de colonnes
        if st.button("Sauvegarder dans la vue",key="but_save_tdb_colonne_taille_desordre") :
            rf.enregistrer_element_session_state("taille_des_colonnes",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/taille_des_colonnes.json")
        st.divider()

        # réorganisation des figures du tableau de bord
        st.subheader("Réorganiser la position des éléments du tableau de bord")
        if "tableau_de_bord.json" in st.session_state and st.session_state["tableau_de_bord.json"] != {} :
            # organisation des input selon le format actuel du tableau de bord
            cols3 = st.columns(st.session_state["taille_des_colonnes"])
            i_colonne = 0
            for cle, valeur in dict(sorted(st.session_state["tableau_de_bord.json"].items(), key=lambda item: item[1]["index"])).items():
                with cols3[i_colonne] :
                    cola,colb = st.columns([2, 1])
                    with cola:
                        valeur["index"] = st.number_input(str(cle)+" :",min_value=0,value=valeur["index"], key="tdb_index_"+str(cle))
                    with colb:
                        if st.button(":x:",key="tdb_but_suppr_"+str(cle)) :
                            del st.session_state["tableau_de_bord.json"][cle]
                            rf.enregistrer_element_session_state("tableau_de_bord.json",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/tableau_de_bord.json")
                            st.rerun()
                    i_colonne += 1
                if i_colonne >= st.session_state["tableau_de_bord_colonne"]:
                    #cols3 = st.columns(st.session_state["taille_des_colonnes"])  # Nouvelle ligne de colonnes
                    i_colonne = 0
            # enregistrement des tailles de colonnes
            if st.button("Sauvegarder dans la vue",key="but_save_tdb_reorga_desordre") :
                rf.enregistrer_element_session_state("tableau_de_bord.json",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/tableau_de_bord.json")
                st.rerun()
        st.divider()

with tab1:
    with st.container():
        # chargement de données des desordres
        if "desordres.json" in st.session_state and "ref_systeme.json" in st.session_state :
            desordres_init = rf.extract_data_them(st.session_state["ref_systeme.json"],st.session_state["desordres.json"])
            # Convertir la colonne 'Date de début/fin' en format datetime
            # transformer les dates non correspondantes en nat
            desordres_init["Date de début"] = pd.to_datetime(desordres_init["Date de début"], errors='coerce').dt.date
            desordres_init["Date de fin"] = pd.to_datetime(desordres_init["Date de fin"], errors='coerce').dt.date
            desordres_init["Observation Date d'observation"] = pd.to_datetime(desordres_init["Observation Date d'observation"], errors='coerce').dt.date

        # execution des entrés du tableau de bord
        if "tableau_de_bord.json" in st.session_state and st.session_state["tableau_de_bord.json"] != {} :
            # tri des éléments du tableau de bord
            st.session_state["tableau_de_bord.json"] = dict(sorted(st.session_state["tableau_de_bord.json"].items(), key=lambda item: item[1]["index"]))
            # index des entrées et des colonnes
            cols = st.columns(st.session_state["taille_des_colonnes"])
            iter = 1
            i_colonne = 0
            # affichage des entrées du tableau de bord
            for cle, valeur in st.session_state["tableau_de_bord.json"].items():
                # reclassement des valeurs
                valeur["index"] = iter
                # exécution du filtre et du code associé
                with cols[i_colonne]:
                    st.write(f"{iter} - {cle}")
                    exec(valeur["filtre"])
                    exec(valeur["code"])
                #incrémentation de l'itérateur et de la colonne et de l'initialiseur de colonne
                i_colonne += 1
                if i_colonne >= st.session_state["tableau_de_bord_colonne"]:
                    #cols = st.columns(st.session_state["taille_des_colonnes"])  # Nouvelle ligne de colonnes
                    i_colonne = 0
                    cols = st.columns(st.session_state["taille_des_colonnes"])
                iter += 1
        else :
            st.write("Aucune information chargée dans le tableau de bord")
        

