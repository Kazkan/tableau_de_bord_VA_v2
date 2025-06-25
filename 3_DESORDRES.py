###############################################
# Gabriel NAVENNEC - 06/05/2025               #
# SYMBHI - FRANCE DIGUE - IUGA                #
#                                             #
# Version 1.0                                 #
###############################################

import streamlit as st
import pandas as pd
import geopandas as gpd
import os
from datetime import datetime
from streamlit_folium import st_folium

#import de fonctions maisons
from utils import read_files as rf
from utils import figure as fi
from utils import st_widget as sw
from utils import folium_widget as fw
import utils.sidebar as sb

sb.sidebar_content()

########## initialisation des paramètres utilisateurs et des donnees en memoires ##########
# ###################### déjà fait à priori²²

# titre de la page
st.title("Désordres")
st.divider()

########## prétraitement des tables ##########

# condition selon existence du fichier de reférence des systèmes
if "desordres.json" not in st.session_state :
    st.warning("Le fichier des désordres n'existe pas. Veuillez le charger dans l'application.")
if "ref_systeme.json" not in st.session_state :
    st.warning("Le fichier de référence des systèmes d'endiguements n'existe pas. Veuillez le charger dans l'application.")

if "desordres.json" in st.session_state and "ref_systeme.json" in st.session_state :
    # création du dataframe de thématique lié aux désordres
    df_desordre_select = rf.extract_data_them(st.session_state["ref_systeme.json"],st.session_state["desordres.json"])

    ########## initialisation des données par défaut si elles sont chargés
    # systeme
    if "param_systeme.json" in st.session_state :
        st.session_state["defaut_systeme"] =  st.session_state["param_systeme.json"]
    else :
        st.session_state["defaut_systeme"] = []
    # digue
    if "param_digue.json" in st.session_state :
        st.session_state["defaut_digue"] =  st.session_state["param_digue.json"]
    else :
        st.session_state["defaut_digue"] = []
    # troncon
    if "param_troncon.json" in st.session_state :
        st.session_state["defaut_troncon"] =  st.session_state["param_troncon.json"]
    else :
        st.session_state["defaut_troncon"] = []

    # date_début
    if "param_desordre_date_debut.json" in st.session_state :
        st.session_state["defaut_date_debut"] =  st.session_state["param_desordre_date_debut.json"]
    else :
        st.session_state["defaut_date_debut"] = False

    # date d'observation nul
    if "param_desordre_obs_date_nul.json" in st.session_state :
        st.session_state["defaut_param_desordre_obs_date_nul"] =  st.session_state["param_desordre_obs_date_nul.json"]
    else :
        st.session_state["defaut_param_desordre_obs_date_nul"] = True

    # dict de référence des urgences
    dict_urgence = {}
    # boucle sur les désordres urgences
    for index,ligne in st.session_state["desordre_urgence"].iterrows() :
        dict_urgence[ligne["libelle"]] = str(ligne["abrege"])+" : "+ligne["libelle"]

    # établir les paramètres par défaut
    st.session_state["param_desordre_urgence_defaut"] = []
    st.session_state["param_desordre_urgence_selec"] = []
    if "param_desordre_urgence" in st.session_state :
        del st.session_state["param_desordre_urgence"]
    # chargement de fichier enregistré pour régler les parametre par défaut
    if "param_desordre_urgence.json" in st.session_state :
        # Charger depuis le fichier JSON
        for elem in st.session_state["param_desordre_urgence.json"] :
            st.session_state["param_desordre_urgence_defaut"].append(dict_urgence[elem]) 

    # réglage des paramètres par défaut
    st.session_state["param_desordre_archive_defaut"] = True
    st.session_state["param_desordre_nonarchive_defaut"] = True
    if "param_desordre_archive.json" in st.session_state :
        st.session_state["param_desordre_archive_defaut"] =  st.session_state["param_desordre_archive.json"]
    if "param_desordre_nonarchive.json" in st.session_state :
        st.session_state["param_desordre_nonarchive_defaut"] =  st.session_state["param_desordre_nonarchive.json"]

    # réglage des paramètres par défaut
    st.session_state["param_desordre_colonne_defaut"] = []
    if "param_desordre_colonne.json" in st.session_state :
        # Charger depuis le fichier JSON
        for elem in st.session_state["param_desordre_colonne.json"] :
            st.session_state["param_desordre_colonne_defaut"].append(elem) 

    # réglage des paramètres par défaut
    st.session_state["param_desordre_auteur_defaut"] = []
    if "param_desordre_auteur.json" in st.session_state :
        # Charger depuis le fichier JSON
        for elem in st.session_state["param_desordre_auteur.json"] :
            st.session_state["param_desordre_auteur_defaut"].append(elem) 

    # réglage des paramètres par défaut
    st.session_state["param_desordre_observateur_defaut"] = []
    if "param_desordre_observateur.json" in st.session_state :
        # Charger depuis le fichier JSON
        for elem in st.session_state["param_desordre_observateur.json"] :
            st.session_state["param_desordre_observateur_defaut"].append(elem) 

    # réglage des paramètres par défaut
    st.session_state["param_desordre_suite_defaut"] = []
    if "param_desordre_suite.json" in st.session_state :
        # Charger depuis le fichier JSON
        for elem in st.session_state["param_desordre_suite.json"] :
            st.session_state["param_desordre_suite_defaut"].append(elem) 

    # réglage des paramètres par défaut
    st.session_state["param_desordre_categorie_defaut"] = []
    if "param_desordre_categorie.json" in st.session_state :
        # Charger depuis le fichier JSON
        for elem in st.session_state["param_desordre_categorie.json"] :
            st.session_state["param_desordre_categorie_defaut"].append(elem) 

    # réglage des paramètres par défaut
    st.session_state["param_desordre_type_defaut"] = []
    if "param_desordre_type.json" in st.session_state :
        # Charger depuis le fichier JSON
        for elem in st.session_state["param_desordre_type.json"] :
            st.session_state["param_desordre_type_defaut"].append(elem) 

    # réglage par défaut
    st.session_state["param_desordre_geom_pt_defaut"] = True
    st.session_state["param_desordre_geom_ligne_defaut"] = True
    if "param_desordre_geom_pt.json" in st.session_state :
        st.session_state["param_desordre_geom_pt_defaut"] =  st.session_state["param_desordre_geom_pt.json"]
    if "param_desordre_geom_ligne.json" in st.session_state :
        st.session_state["param_desordre_geom_ligne_defaut"] =  st.session_state["param_desordre_geom_ligne.json"]

    ########################################################

    # choix du type d'élément à inspecter
    with st.expander("0 - Choix des tronçons : ") :
        with st.container():
            cola,colb,colc = st.columns(3)
            # systeme
            with cola :
                # gestion des systeme par  défaut
                defaut_systeme = [opt for opt in st.session_state["defaut_systeme"] if opt in rf.list_dig(st.session_state["ref_systeme.json"],"Système")]
                # sélection en fonction des systeme détectées
                st.session_state["param_systeme"] = st.multiselect("Système :",rf.list_dig(df_desordre_select,"Système"), default=defaut_systeme, key="param_systeme_desordre_widget", on_change=sw.entite_defaut_vide)
                # filtre des systeme si existant
                if st.session_state["param_systeme"] != [] :
                    df_desordre_select = rf.filtre_table_ref(df_desordre_select,"Système", st.session_state["param_systeme"])
            # digue
            with colb :
            # gestion des digue par  défaut
                defaut_digue = [opt for opt in st.session_state["defaut_digue"] if opt in rf.list_dig(df_desordre_select,"Digue")]
                # sélection en fonction des digue détectées
                st.session_state["param_digue"] = st.multiselect("Digue :",rf.list_dig(df_desordre_select,"Digue"), default=defaut_digue, key="param_digue_desordre_wideget",on_change=sw.entite_defaut_vide)
                # filtre des digue si existant
                if st.session_state["param_digue"] != [] :
                    df_desordre_select = rf.filtre_table_ref(df_desordre_select,"Digue", st.session_state["param_digue"])
            # troncon
            with colc :
                # gestion des troncon par  défaut
                defaut_troncon = [opt for opt in st.session_state["defaut_troncon"] if opt in rf.list_dig(df_desordre_select,"Tronçon")]
                # sélection en fonction des troncon détectées
                st.session_state["param_troncon"] = st.multiselect("Tronçon :",rf.list_dig(df_desordre_select,"Tronçon"), default=defaut_troncon, key="param_troncon_desordre_widget",on_change=sw.entite_defaut_vide)
                # filtre des troncon si existant
                if st.session_state["param_troncon"] != [] :
                    df_desordre_select = rf.filtre_table_ref(df_desordre_select,"Tronçon", st.session_state["param_troncon"])

            ########## enregistrement des sessions state éléments entités dans la vue ##########
            if st.button("Sauvegarder dans la vue",key="but_save_entite_desordre") :
                rf.enregistrer_element_session_state("param_systeme",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/param_systeme.json")
                rf.enregistrer_element_session_state("param_digue",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/param_digue.json")
                rf.enregistrer_element_session_state("param_troncon",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/param_troncon.json")

    # fin de la section            
    st.divider()

    # tableau récapitulatif
    st.write("Table récapitulative des désordres :")
    with st.container():
        ########## affichage de la table des données désordres ##########
        # emplacement de la table à afficher
        table_element_filtre = st.empty()
        # emplacement du comptage à afficher
        cola, colb = st.columns([7,1])
        with cola :
            compte_table = st.empty()
        with colb :
            bouton_favoris = st.empty()
        selection_table = st.empty()


    # fin de la section            
    st.divider()

    ########## filtres généraux ########## 
    # enchainement de filtre. Les parametre (user input) sont récupéré en session state et la table en variable passe de  filtre en filtre

    with st.expander('1 - Filtres'):
        with st.container():
            st.subheader("Généraux")

            ########## DATE ##########
            # Convertir la colonne 'Date de début/fin' en format datetime
            # transformer les dates non correspondantes en nat
            df_desordre_select["Date de début"] = pd.to_datetime(df_desordre_select["Date de début"], errors='coerce').dt.date
            df_desordre_select["Date de fin"] = pd.to_datetime(df_desordre_select["Date de fin"], errors='coerce').dt.date
            df_desordre_select["Observation Date d'observation"] = pd.to_datetime(df_desordre_select["Observation Date d'observation"], errors='coerce').dt.date
            # fonction de réinitialisation des dates
            def date_reinit():
                oldest_date = df_desordre_select["Date de début"].dropna().min()
                st.session_state["param_desordre_periode"] = (oldest_date, datetime.now().date())
                    # fonction de réinitialisation des dates d'observations
            def date_reinit_obs():
                oldest_date = df_desordre_select["Observation Date d'observation"].dropna().min()
                st.session_state["param_desordre_periode_obs"] = (oldest_date, datetime.now().date())

            # vérification de l'existence d'un fichier de paramètre de date
            if "param_desordre_periode.json" in st.session_state:
                # Charger depuis le fichier JSON
                st.session_state["param_desordre_periode"] = st.session_state["param_desordre_periode.json"]
            else:
                # Récupération de la date la plus ancienne
                if not df_desordre_select["Date de début"].dropna().empty:
                    oldest_date = df_desordre_select["Date de début"].dropna().min()
                    st.session_state["param_desordre_periode"] = (oldest_date, datetime.now().date())
                else:
                    st.session_state["param_desordre_periode"] = (datetime.now().date(), datetime.now().date())

            # vérification de l'existence d'un fichier de paramètre de date observés
            if "param_desordre_periode_obs.json" in st.session_state:
                # Charger depuis le fichier JSON
                st.session_state["param_desordre_periode_obs"] = st.session_state["param_desordre_periode_obs.json"]
            else:
                # Récupération de la date la plus ancienne
                if not df_desordre_select["Observation Date d'observation"].dropna().empty:
                    oldest_date_obs = df_desordre_select["Observation Date d'observation"].dropna().min()
                    st.session_state["param_desordre_periode_obs"] = (oldest_date_obs, datetime.now().date())
                else:
                    st.session_state["param_desordre_periode_obs"] = (datetime.now().date(), datetime.now().date())

            cola,colb = st.columns(2)
            with cola :
                # choix du filtre de date pré réglé sur la plus ancienne à aujourd'hui
                st.session_state["param_desordre_periode"] = st.date_input("actif(s) entre :", st.session_state["param_desordre_periode"], key="param_desordre_periode_widget",on_change=date_reinit)
            with colb :
                st.session_state["param_desordre_periode_obs"] = st.date_input("observé(s) entre :", st.session_state["param_desordre_periode_obs"],key="param_desordre_periode_obs_widget",on_change=date_reinit_obs)
            cola,colb,colc,cold = st.columns(4)
            with cola :
                # filtre des dates uniquement sur la date de début
                st.session_state["param_desordre_date_debut"] = st.toggle("créé(s) à cette période uniquement", value=st.session_state["defaut_date_debut"], key="param_desordre_date_debut_widget",)
            with colb :
                # filtre des date d'observations nul
                st.session_state["param_desordre_obs_date_nul"] = st.toggle("sans observation(s)", value=st.session_state["defaut_param_desordre_obs_date_nul"], key="param_desordre_obs_date_nul_widget",)
            ########## ARCHIVAGE ##########
            # choix des filtres des désordre archivés
            with colc :
                st.session_state["param_desordre_archive"] = st.toggle("archivé(s)", value=st.session_state["param_desordre_archive_defaut"],key="param_desordre_archive_widget")
            with cold :
                st.session_state["param_desordre_nonarchive"] = st.toggle("non archivé(s)", value=st.session_state["param_desordre_nonarchive_defaut"],key="param_desordre_nonarchive_widget")

            cola,colb = st.columns(2)
            with cola :
            ########## AUTEUR ##########
             # choix du filtre auteur
                st.session_state["param_desordre_auteur_defaut"] = [elem for elem in st.session_state["param_desordre_auteur_defaut"] if elem in df_desordre_select['Auteur'].unique()]   
                st.session_state["param_desordre_auteur"] = st.multiselect("auteur(e-s) :",list(df_desordre_select['Auteur'].unique()),key="param_desordre_auteur_selec_widget",default=st.session_state["param_desordre_auteur_defaut"])
            with colb :
            ########## OBSERVATEUR ##########
             # choix du filtre auteur
                st.session_state["param_desordre_observateur_defaut"] = [elem for elem in st.session_state["param_desordre_observateur_defaut"] if elem in df_desordre_select['Observation Observateur'].unique()]
                st.session_state["param_desordre_observateur"] = st.multiselect("dernier(e-s) observateur(ice-s) :",list(df_desordre_select['Observation Observateur'].unique()),key="param_desordre_observateur_selec_widget",default=st.session_state["param_desordre_observateur_defaut"])

            st.subheader("Descriptifs")
            cola, colb = st.columns(2)
            with cola :
            ########## CATEGORIE ##########
             # choix du filtre niveau d'suite 
                st.session_state["param_desordre_categorie"] = st.multiselect("catégorie(s) de désordre :",list((st.session_state["categorie_desordre"]["libelle_y"]).unique()),key="param_desordre_categorie_selec_widget",default=st.session_state["param_desordre_categorie_defaut"])
            with colb :
            ########## TYPE ##########
             # choix du filtre niveau d'suite 
                st.session_state["param_desordre_type"] = st.multiselect("type(s) de désordre :",list((st.session_state["categorie_desordre"]["libelle_x"]).unique()),key="param_desordre_type_selec_widget",default=st.session_state["param_desordre_type_defaut"])
            cola, colb = st.columns(2)
            with cola :
                ########## URGENCE ##########
                # choix du filtre niveau d'urgence 
                st.session_state["param_desordre_urgence_selec"] = st.multiselect("niveau(x) d'urgence :",list(dict_urgence.values()),key="param_desordre_urgence_selec_widget",default=st.session_state["param_desordre_urgence_defaut"])
                # allocation des clés sur la session state
                if st.session_state["param_desordre_urgence_selec"] != [] :
                    st.session_state["param_desordre_urgence"] = []
                    # récupération de la clé du dict d'urgence qui doit servir pour le filtre st.session_state["param_desordre_urgence"]
                    for u in st.session_state["param_desordre_urgence_selec"] :
                        for k, val in dict_urgence.items(): 
                            if u == val: 
                                st.session_state["param_desordre_urgence"].append(k)
                else : 
                    st.session_state["param_desordre_urgence"] = []
            with colb :
                ########## SUITE A APPORTER ##########
                # choix du filtre niveau d'suite 
                st.session_state["param_desordre_suite"] = st.multiselect("suite(s) à apporter :",list((st.session_state["suite_desordre"]["libelle"]).unique()),key="param_desordre_suite_selec_widget",default=st.session_state["param_desordre_suite_defaut"])
            cola,colb,colc = st.columns([1,1,2])
            ########## GÉOMÉTRIE ##########
            # choix du type de géométrie
            with cola :
                st.session_state["param_desordre_geom_pt"] = st.toggle("désordre(s) ponctuel(s)", value=st.session_state["param_desordre_geom_pt_defaut"], key="param_desordre_geom_pt_widget")
            with colb :
                st.session_state["param_desordre_geom_ligne"] = st.toggle("désordre(s) linéaire(s)", value=st.session_state["param_desordre_geom_ligne_defaut"], key="param_desordre_geom_ligne_widget")

            st.subheader("Visuels")
            ########## COLONNE ##########
            # choix du filtre colonne 
            st.session_state["param_desordre_colonne"] = st.multiselect("colonne(s) à afficher :",df_desordre_select.columns.values.tolist(),key="param_desordre_colonne_widget", default=st.session_state["param_desordre_colonne_defaut"])

            ########## enchainement des filtres ##########
            # filtrage par date # s'applique systematiquement
            df_desordre_select = sw.filtre_table_date(df_desordre_select, st.session_state["param_desordre_periode"], st.session_state["param_desordre_date_debut"])
            # filtrage par date d'observation
            df_desordre_select = sw.filtre_table_obs_date(df_desordre_select, st.session_state["param_desordre_periode_obs"], st.session_state["param_desordre_obs_date_nul"])
            # filtrage par urgence si filtre selectionné
            if st.session_state["param_desordre_urgence"] != [] :
                df_desordre_select = sw.filtre_valeur_liste(df_desordre_select, "Observation Urgence", st.session_state["param_desordre_urgence"])
            # filtrage par archivage
            df_desordre_select = sw.filtre_table_archive(df_desordre_select, st.session_state["param_desordre_archive"], st.session_state["param_desordre_nonarchive"])
            # filtrage par auteur
            if st.session_state["param_desordre_auteur"] != [] :
                df_desordre_select = sw.filtre_valeur_liste(df_desordre_select, "Auteur",st.session_state["param_desordre_auteur"])
            # filtrage par observateur
            if st.session_state["param_desordre_observateur"] != [] :
                df_desordre_select = sw.filtre_valeur_liste(df_desordre_select, "Observation Observateur",st.session_state["param_desordre_observateur"])
            # filtrage par suite à donner
            if st.session_state["param_desordre_suite"] != [] :
                df_desordre_select = sw.filtre_valeur_liste(df_desordre_select, "Observation Suite à apporter",st.session_state["param_desordre_suite"])
            # filtrage par catégorie
            if st.session_state["param_desordre_categorie"] != [] :
                df_desordre_select = sw.filtre_valeur_liste(df_desordre_select, "Catégorie de désordre",st.session_state["param_desordre_categorie"])
            # filtrage par type
            if st.session_state["param_desordre_type"] != [] :
                df_desordre_select = sw.filtre_valeur_liste(df_desordre_select, "Type de désordre",st.session_state["param_desordre_type"])
            # filtrage par géométrie
            df_desordre_select = sw.filtre_table_geom(df_desordre_select, st.session_state["param_desordre_geom_pt"], st.session_state["param_desordre_geom_ligne"])
            # filtrage par colonne
            if st.session_state["param_desordre_colonne"] != [] :
                df_desordre_visuel = sw.filtre_table_colonne(df_desordre_select, st.session_state["param_desordre_colonne"])
            else :
                df_desordre_visuel = df_desordre_select

            # désordre visuel est le dataframe avec les colonnes personnalisés. desordre selec est le dataframe avec toute les colonnes qui peut etre exploiter pour les opérations à venir

            # mise à jour des emplacements de table et de compte d'entités
            event = table_element_filtre.dataframe(df_desordre_visuel,on_select="rerun",selection_mode=["single-row"])
            compte_table.markdown(str(len(df_desordre_visuel))+" ligne(s) détectée(s)")
            if event.selection and event.selection.rows:
                descript=[]
                descript.append("désordre n° "+str(df_desordre_select.iloc[event.selection.rows[0],]['Désignation'])+" relevé")
                if str(df_desordre_select.iloc[event.selection.rows[0],]['Auteur']) != "NaT" :
                    descript.append(" par "+str(df_desordre_select.iloc[event.selection.rows[0],]['Auteur']))
                descript.append(" le "+str(df_desordre_select.iloc[event.selection.rows[0],]['Date de début']))
                descript.append(" sur le tronçon "+str(df_desordre_select.iloc[event.selection.rows[0],]['Tronçon']))
                descript.append(" au niveau du PR "+str(df_desordre_select.iloc[event.selection.rows[0],]['PR de début']))
                if str(df_desordre_select.iloc[event.selection.rows[0],]['Catégorie de désordre']) != "NaT" :
                    descript.append(', de catégorie "'+str(df_desordre_select.iloc[event.selection.rows[0],]['Catégorie de désordre'])+'"')
                if str(df_desordre_select.iloc[event.selection.rows[0],]['Type de désordre']) != "NaT" :
                    descript.append(', de type "'+str(df_desordre_select.iloc[event.selection.rows[0],]['Type de désordre'])+'"')
                if str(df_desordre_select.iloc[event.selection.rows[0],]['Observation Urgence']) != "NaT" :
                    descript.append(', classé comme "'+str(df_desordre_select.iloc[event.selection.rows[0],]['Observation Urgence'])+'"')
                if str(df_desordre_select.iloc[event.selection.rows[0],]['Observation Suite à apporter']) != "NaT" and str(df_desordre_select.iloc[event.selection.rows[0],]['Observation Suite à apporter']) != "Archivé" :
                    descript.append(', devant être soumis à "'+str(df_desordre_select.iloc[event.selection.rows[0],]['Observation Suite à apporter'])+'"')
                if str(df_desordre_select.iloc[event.selection.rows[0],]['Date de fin']) != "NaT" :
                    descript.append(", cloturé le "+str(df_desordre_select.iloc[event.selection.rows[0],]['Date de fin']))
                if str(df_desordre_select.iloc[event.selection.rows[0],]["Observation Date d'observation"]) != "NaT" :
                    descript.append(", observé la dernière fois le "+str(df_desordre_select.iloc[event.selection.rows[0],]["Observation Date d'observation"]) )
                if str(df_desordre_select.iloc[event.selection.rows[0],]["Observation Observateur"]) != "NaT" :
                    descript.append(", par "+str(df_desordre_select.iloc[event.selection.rows[0],]["Observation Observateur"])      )         
                selection_table.markdown("Selectionnée : "+''.join(descript))
            add_fav=bouton_favoris.button(":star:",key="fav_filtre_des")

            #table_element_filtre.selection

            ########## enregistrement des sessions state filtre dans la vue ##########
            if st.button("Sauvegarder dans la vue",key="but_save_filtre_desordre") :
                rf.enregistrer_element_session_state("param_desordre_periode",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/param_desordre_periode.json")
                rf.enregistrer_element_session_state("param_desordre_periode_obs",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/param_desordre_periode_obs.json")
                rf.enregistrer_element_session_state("param_desordre_obs_date_nul",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/param_desordre_obs_date_nul.json")
                rf.enregistrer_element_session_state("param_desordre_urgence",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/param_desordre_urgence.json")
                rf.enregistrer_element_session_state("param_desordre_auteur",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/param_desordre_auteur.json")
                rf.enregistrer_element_session_state("param_desordre_observateur",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/param_desordre_observateur.json")
                rf.enregistrer_element_session_state("param_desordre_suite",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/param_desordre_suite.json")
                rf.enregistrer_element_session_state("param_desordre_categorie",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/param_desordre_categorie.json")
                rf.enregistrer_element_session_state("param_desordre_type",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/param_desordre_type.json")
                rf.enregistrer_element_session_state("param_desordre_archive",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/param_desordre_archive.json")
                rf.enregistrer_element_session_state("param_desordre_nonarchive",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/param_desordre_nonarchive.json")
                rf.enregistrer_element_session_state("param_desordre_geom_pt",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/param_desordre_geom_pt.json")
                rf.enregistrer_element_session_state("param_desordre_geom_ligne",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/param_desordre_geom_ligne.json")
                rf.enregistrer_element_session_state("param_desordre_colonne",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/param_desordre_colonne.json")
                rf.enregistrer_element_session_state("param_desordre_date_debut",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/param_desordre_date_debut.json")

            ########### création de l'export vers le tableau de bord ##########
            if add_fav:
                sw.favoris_desordres("filtre_colonne="+str(st.session_state["param_desordre_colonne"])+"""
if filtre_colonne != [] :
    desordres=sw.filtre_table_colonne(desordres, """+str(st.session_state["param_desordre_colonne"])+""")
st.dataframe(desordres)
st.caption(str(len(desordres))+" ligne(s) détectée(s)")""")

    ########## Cartographie des désordres ##########

    with st.expander('2 - Cartographie'):
        with st.container():
            cola, colb = st.columns([2,1])

            ########### paramètre de la carte ##########
            with colb :
                # chargement des parametre enregistré
                # etiquette
                if "map_desordre_etiquettes.json" in st.session_state :
                    st.session_state["defaut_map_desordre_etiquettes"] =  st.session_state["map_desordre_etiquettes.json"]
                else :
                    st.session_state["defaut_map_desordre_etiquettes"] = []

                # popup
                if "map_desordre_infobulle.json" in st.session_state :
                    st.session_state["defaut_map_desordre_infobulle"] =  st.session_state["map_desordre_infobulle.json"]
                else :
                    st.session_state["defaut_map_desordre_infobulle"] = []

                # cartographie 
                # liste des cartes disponibles
                type_discretisation=["aucune","urgence","categorie","suite"]
                if "map_desordre_discretisation.json" in st.session_state :
                    st.session_state["defaut_map_desordre_discretisation"] =  type_discretisation.index(st.session_state["map_desordre_discretisation.json"])
                else :
                    st.session_state["defaut_map_desordre_discretisation"] = 0

                st.session_state["map_desordre_etiquettes"] = st.multiselect("étiquettes :",df_desordre_select.columns.values.tolist(),key="map_desordre_etiquettes_widget", default=st.session_state["defaut_map_desordre_etiquettes"])
                st.session_state["map_desordre_infobulle"] = st.multiselect("infos :",df_desordre_select.columns.values.tolist(),key="map_desordre_infobulle_widget", default=st.session_state["defaut_map_desordre_infobulle"])
                st.session_state["map_desordre_discretisation"] = st.selectbox("cartes thématiques :",type_discretisation , key="map_desordre_discretisation_widget",index=st.session_state["defaut_map_desordre_discretisation"])
                
                col1,col2 = st.columns([2,1])
                with col1 :
                    if st.button("Sauvegarder dans la vue",key="but_save_map_desordre") :
                        rf.enregistrer_element_session_state("map_desordre_etiquettes",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/map_desordre_etiquettes.json")
                        rf.enregistrer_element_session_state("map_desordre_infobulle",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/map_desordre_infobulle.json")
                        rf.enregistrer_element_session_state("map_desordre_discretisation",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/map_desordre_discretisation.json")
                with col2 :
                    ########### création de l'export vers le tableau de bord ##########
                    if st.button(":star:",key="fav_carte_des"):
                        sw.favoris_desordres("fw.map_desordres(desordres,"+str(st.session_state["map_desordre_etiquettes"])+","+str(st.session_state["map_desordre_infobulle"])+",'"+str(st.session_state["map_desordre_discretisation"])+"""',iter)
st.empty()""")
                
                # affichage des légendes selon la carte choisie
                if "affichage_carte_desordre" in st.session_state and st.session_state["map_desordre_discretisation"] == "urgence" :
                    st.markdown("**Niveau d'urgence des désordres :**")
                    legend_html = '''
                    <i style="color:LawnGreen;">▲ ▬</i> 0 : Faible urgence<br>
                    <i style="color:GoldenRod;">▲ ▬</i> 1 : Pas de grande urgence<br>
                    <i style="color:DarkOrange;">▲ ▬</i> 2 : Désordre devant être traité à court ou moyen terme<br>
                    <i style="color:Crimson;">▲ ▬</i> 3 : Désordre devant être traité de façon urgente<br>
                    <i style="color:DarkGrey;">▲ ▬</i> Indéfini<br>
                    <i style="color:Black;">▲ ▬</i> Non renseigné<br>
                    </div>
                    '''
                    st.html(legend_html)
                elif "affichage_carte_desordre" in st.session_state and st.session_state["map_desordre_discretisation"] == "categorie" :
                    st.markdown("**Catégorisation des désordres :**")
                    legend_html = '''
                    <i style="color:chocolate;">▲ ▬</i> ERX - Érosion externe<br>
                    <i style="color:blue;">▲ ▬</i> ERI - Érosion interne<br>
                    <i style="color:DarkOrange;">▲ ▬</i> DAF - Désordre affectant la structure<br>
                    <i style="color:Crimson;">▲ ▬</i> BRE - Brèche<br>
                    <i style="color:GoldenRod;">▲ ▬</i> ENT - Conditions d'entretien de la digue, détérioration des équipements, activités illégales, gêne à la gestion<br>
                    <i style="color:purple;">▲ ▬</i> DDP - Défaut sur dispositif de protection<br>
                    <i style="color:DarkGrey;">▲ ▬</i> AUT - Autre<br>
                    <i style="color:Black;">▲ ▬</i> Non renseigné<br>
                    </div>
                    '''
                    st.html(legend_html)
                elif "affichage_carte_desordre" in st.session_state and st.session_state["map_desordre_discretisation"] == "suite" :
                    st.markdown("**Suite à apporter :**")
                    legend_html = '''
                    <i style="color:darkgrey;">▲ ▬</i> AUC - Aucune<br>
                    <i style="color:green;">▲ ▬</i> SUR - Surveillance<br>
                    <i style="color:DarkOrange;">▲ ▬</i> ENT - Entretien<br>
                    <i style="color:blue;">▲ ▬</i> ETU - Etudes<br>
                    <i style="color:chocolate;">▲ ▬</i> TRA - Travaux<br>
                    <i style="color:goldenrod;">▲ ▬</i> ARH - Archivé<br>
                    <i style="color:crimson;">▲ ▬</i> PRI - Prioritaire<br>
                    <i style="color:purple;">▲ ▬</i> CST - Constat<br>
                    <i style="color:Black;">▲ ▬</i> Non renseigné<br>
                    </div>
                    '''
                    st.html(legend_html)
    
            with cola :
                affichage_carte_desordre = st.toggle("Afficher/masquer la carte",key="but_graph_carte_desordre")
                # création de la carte si condition rempli
                if affichage_carte_desordre:
                    # affichage de la carte avec les désordres
                    fw.map_desordres(df_desordre_select,st.session_state["map_desordre_etiquettes"],st.session_state["map_desordre_infobulle"],st.session_state["map_desordre_discretisation"],"1")
                    st.empty()

    ########## graph du linéaire de digues ##########
            
    with st.expander('3 - Visualisation linéaire'):
        with st.container():

            # chargement données par défaut/enregistré :
            # etiquette
            if "graph_lin_desordre_etiquettes.json" in st.session_state :
                st.session_state["defaut_graph_lin_desordre_etiquettes"] =  st.session_state["graph_lin_desordre_etiquettes.json"]
            else :
                st.session_state["defaut_graph_lin_desordre_etiquettes"] = []
            # popup
            if "graph_lin_desordre_infobulle.json" in st.session_state :
                st.session_state["defaut_graph_lin_desordre_infobulle"] =  st.session_state["graph_lin_desordre_infobulle.json"]
            else :
                st.session_state["defaut_graph_lin_desordre_infobulle"] = [] 
            # liste des themes disponibles
            type_discretisation_lin=["type","categorie","suite",]
            if "graph_lin_desordre_discretisation.json" in st.session_state :
                st.session_state["defaut_graph_lin_desordre_discretisation"] =  type_discretisation_lin.index(st.session_state["graph_lin_desordre_discretisation.json"])
            else :
                st.session_state["defaut_graph_lin_desordre_discretisation"] = 0
            # liste des themes tronçons disponibles
            if "graph_lin_desordre_tronc.json" in st.session_state :
                # vérifie si le tronçon par défaut est disponible dans la table des désordres filtré
                if st.session_state["graph_lin_desordre_tronc.json"] in rf.list_dig(df_desordre_select,"Tronçon") :
                    st.session_state["defaut_graph_lin_desordre_tronc"] =  rf.list_dig(df_desordre_select,"Tronçon").index(st.session_state["graph_lin_desordre_tronc.json"])
                else :
                    st.session_state["defaut_graph_lin_desordre_tronc"] = 0
            else :
                st.session_state["defaut_graph_lin_desordre_tronc"] = 0

            # selecteurs de parmatres de graphique linéaire
            cola, colb, colc,cold = st.columns(4)
            with colc :
                st.session_state["graph_lin_desordre_etiquettes"] = st.multiselect("étiquettes :",df_desordre_select.columns.values.tolist(),key="graph_lin_desordre_etiquettes_widget", default=st.session_state["defaut_graph_lin_desordre_etiquettes"])
            with colb :
                st.session_state["graph_lin_desordre_infobulle"] = st.multiselect("infos :",df_desordre_select.columns.values.tolist(),key="graph_lin_desordre_infobulle_widget", default=st.session_state["defaut_graph_lin_desordre_infobulle"])
            with cola :
                st.session_state["graph_lin_desordre_discretisation"] = st.selectbox("thématiques :",type_discretisation_lin , key="graph_lin_desordre_discretisation_widget",index=st.session_state["defaut_graph_lin_desordre_discretisation"])
            with cold :
                st.session_state["graph_lin_desordre_tronc"] = st.selectbox("tronçon  :",rf.list_dig(df_desordre_select,"Tronçon") , key="graph_lin_desordre_tronc_widget",index=st.session_state["defaut_graph_lin_desordre_tronc"])
            cola,cold,cole = st.columns([12,3,1])
            
            with cola : 
                affichage_graph_lin = st.toggle("Afficher/masquer le graphique linéaire des désordres",key="but_graph_lin_desordre")

            with cold :
                if st.button("Sauvegarder dans la vue",key="but_save_graph_lin_desordre") :
                    rf.enregistrer_element_session_state("graph_lin_desordre_etiquettes",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/graph_lin_desordre_etiquettes.json")
                    rf.enregistrer_element_session_state("graph_lin_desordre_infobulle",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/graph_lin_desordre_infobulle.json")
                    rf.enregistrer_element_session_state("graph_lin_desordre_discretisation",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/graph_lin_desordre_discretisation.json")
                    rf.enregistrer_element_session_state("graph_lin_desordre_tronc",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/graph_lin_desordre_tronc.json")
            with cole :
                ########### création de l'export vers le tableau de bord ##########
                if st.button(":star:",key="fav_lin_des"):
                    sw.favoris_desordres("st.plotly_chart(fi.figure_lin(desordres,st.session_state['categorie_desordre'],st.session_state['suite_desordre'],"+str(st.session_state["graph_lin_desordre_etiquettes"])+","+str(st.session_state["graph_lin_desordre_infobulle"])+",'"+str(st.session_state["graph_lin_desordre_discretisation"])+"','"+str(st.session_state["graph_lin_desordre_tronc"])+"'))")
            if affichage_graph_lin :
                st.plotly_chart(fi.figure_lin(df_desordre_select,st.session_state["categorie_desordre"],st.session_state["suite_desordre"],st.session_state["graph_lin_desordre_etiquettes"],st.session_state["graph_lin_desordre_infobulle"],st.session_state["graph_lin_desordre_discretisation"],st.session_state["graph_lin_desordre_tronc"])) 
                # nomenclature
                if st.session_state["graph_lin_desordre_discretisation"] != "aucun" :
                    dict_nom_arc={}
                    if st.toggle("afficher/masquer la nomenclature",key="but_lin_nomenclature_desordre") :
                        if st.session_state["graph_lin_desordre_discretisation"] == "type" :
                            for index,row in st.session_state["categorie_desordre"].sort_values("abrege_x").iterrows(): 
                                dict_nom_arc[row["abrege_x"]] = row["libelle_x"]
                            for key, item in dict_nom_arc.items() :
                                st.markdown("**" + str(key) + "** : " + str(item))
                        elif st.session_state["graph_lin_desordre_discretisation"] == "categorie" :
                            for index,row in st.session_state["categorie_desordre"].sort_values("abrege_y").iterrows(): 
                                dict_nom_arc[row["abrege_y"]] = row["libelle_y"]
                            for key, item in dict_nom_arc.items() :
                                st.markdown("**" + str(key) + "** : " + str(item))
                        elif st.session_state["graph_lin_desordre_discretisation"] == "suite" :
                            for index,row in st.session_state["suite_desordre"].sort_values("abrege").iterrows(): 
                                dict_nom_arc[row["abrege"]] = row["libelle"]
                            for key, item in dict_nom_arc.items() :
                                st.markdown("**" + str(key) + "** : " + str(item))
                        elif st.session_state["graph_lin_desordre_discretisation"] == "urgence" :
                            for index,row in st.session_state["desordre_urgence"].sort_values("abrege").iterrows(): 
                                dict_nom_arc[row["abrege"]] = row["libelle"]
                            for key, item in dict_nom_arc.items() :
                                st.markdown("**" + str(key) + "** : " + str(item))
                    

    with st.expander("4 - Niveau d'archivage"):
        with st.container():
            # chargement données par défaut/enregistré :
            # etiquette
            type_etiquettes_arc = ["aucun","thématique","groupe"]
            if "arc_plot_desordre_etiquettes.json" in st.session_state :
                st.session_state["defaut_arc_plot_desordre_etiquettes"] =  type_etiquettes_arc.index(st.session_state["arc_plot_desordre_etiquettes.json"])
            else :
                st.session_state["defaut_arc_plot_desordre_etiquettes"] = 0
            # liste des themes disponibles
            type_discretisation_arc=["aucun","type","categorie","suite","urgence"]
            if "arc_plot_desordre_discretisation.json" in st.session_state :
                st.session_state["defaut_arc_plot_desordre_discretisation"] =  type_discretisation_arc.index(st.session_state["arc_plot_desordre_discretisation.json"])
            else :
                st.session_state["defaut_arc_plot_desordre_discretisation"] = 0
            # liste des themes disponibles
            type_regroupement_arc=["aucun","Tronçon","Digue","Système"]
            if "arc_plot_desordre_regroupement.json" in st.session_state :
                st.session_state["defaut_arc_plot_desordre_regroupement"] =  type_regroupement_arc.index(st.session_state["arc_plot_desordre_regroupement.json"])
            else :
                st.session_state["defaut_arc_plot_desordre_regroupement"] = 0

            # selecteurs de parametres de graphique archive
            cola, colb, colc = st.columns(3)
            with cola :
                st.session_state["arc_plot_desordre_discretisation"] = st.selectbox("thématiques :",type_discretisation_arc , key="arc_plot_desordre_discretisation_widget",index=st.session_state["defaut_arc_plot_desordre_discretisation"])
            with colb :
                st.session_state["arc_plot_desordre_regroupement"] = st.selectbox("grouper par :",type_regroupement_arc , key="arc_plot_desordre_regroupement_widget",index=st.session_state["defaut_arc_plot_desordre_regroupement"])
            with colc :
                st.session_state["arc_plot_desordre_etiquettes"] = st.selectbox("étiquettes :",["aucun","thématique","groupe"],key="arc_plot_desordre_etiquettes_widget", index=st.session_state["defaut_arc_plot_desordre_etiquettes"])
            cola,cold,cole = st.columns([12,3,1])
            with cola :
                affichage_graph_arc = st.toggle("Afficher/masquer le graphique du niveau d'archivage",key="but_graph_arc_desordre")

            with cold :
                # enregistrement des parametres
                if st.button("Sauvegarder dans la vue",key="but_save_arc_plot_desordre") :
                    rf.enregistrer_element_session_state("arc_plot_desordre_etiquettes",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/arc_plot_desordre_etiquettes.json")
                    rf.enregistrer_element_session_state("arc_plot_desordre_regroupement",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/arc_plot_desordre_regroupement.json")
                    rf.enregistrer_element_session_state("arc_plot_desordre_discretisation",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/arc_plot_desordre_discretisation.json")
            with cole :
    ########### création de l'export vers le tableau de bord ##########
                if st.button(":star:",key="fav_arc_des"):
                    sw.favoris_desordres("st.plotly_chart(fi.plot_archive(desordres, '"+str(st.session_state["arc_plot_desordre_etiquettes"])+"','"+str(st.session_state["arc_plot_desordre_regroupement"])+"','"+str(st.session_state["arc_plot_desordre_discretisation"])+"'))")
            if affichage_graph_arc :
                st.plotly_chart(fi.plot_archive(df_desordre_select, st.session_state["arc_plot_desordre_etiquettes"],st.session_state["arc_plot_desordre_regroupement"],st.session_state["arc_plot_desordre_discretisation"]))
                # nomenclature
                if st.session_state["arc_plot_desordre_discretisation"] != "aucun" :
                    dict_nom_arc={}
                    if st.toggle("afficher/masquer la nomenclature",key="but_arc_nomenclature_desordre") :
                        if st.session_state["arc_plot_desordre_discretisation"] == "type" :
                            for index,row in st.session_state["categorie_desordre"].sort_values("abrege_x").iterrows(): 
                                dict_nom_arc[row["abrege_x"]] = row["libelle_x"]
                            for key, item in dict_nom_arc.items() :
                                st.markdown("**" + str(key) + "** : " + str(item))
                        elif st.session_state["arc_plot_desordre_discretisation"] == "categorie" :
                            for index,row in st.session_state["categorie_desordre"].sort_values("abrege_y").iterrows(): 
                                dict_nom_arc[row["abrege_y"]] = row["libelle_y"]
                            for key, item in dict_nom_arc.items() :
                                st.markdown("**" + str(key) + "** : " + str(item))
                        elif st.session_state["arc_plot_desordre_discretisation"] == "suite" :
                            for index,row in st.session_state["suite_desordre"].sort_values("abrege").iterrows(): 
                                dict_nom_arc[row["abrege"]] = row["libelle"]
                            for key, item in dict_nom_arc.items() :
                                st.markdown("**" + str(key) + "** : " + str(item))
                        elif st.session_state["arc_plot_desordre_discretisation"] == "urgence" :
                            for index,row in st.session_state["desordre_urgence"].sort_values("abrege").iterrows(): 
                                dict_nom_arc[row["abrege"]] = row["libelle"]
                            for key, item in dict_nom_arc.items() :
                                st.markdown("**" + str(key) + "** : " + str(item))

    with st.expander("5 - Résumé périodique"):
        with st.container():
            # chargement données par défaut/enregistré :
            # etiquette
            type_etiquettes_temp = ["aucun","thématique","groupe"]
            if "temp_plot_desordre_etiquettes.json" in st.session_state :
                st.session_state["defaut_temp_plot_desordre_etiquettes"] =  type_etiquettes_temp.index(st.session_state["temp_plot_desordre_etiquettes.json"])
            else :
                st.session_state["defaut_temp_plot_desordre_etiquettes"] = 0
            # liste des themes disponibles
            type_discretisation_temp=["aucun","type","categorie","suite","urgence","archivage"]
            if "temp_plot_desordre_discretisation.json" in st.session_state :
                st.session_state["defaut_temp_plot_desordre_discretisation"] =  type_discretisation_temp.index(st.session_state["temp_plot_desordre_discretisation.json"])
            else :
                st.session_state["defaut_temp_plot_desordre_discretisation"] = 0
            # liste des themes disponibles
            type_regroupement_temp=["aucun","Tronçon","Digue","Système"]
            if "temp_plot_desordre_regroupement.json" in st.session_state :
                st.session_state["defaut_temp_plot_desordre_regroupement"] =  type_regroupement_temp.index(st.session_state["temp_plot_desordre_regroupement.json"])
            else :
                st.session_state["defaut_temp_plot_desordre_regroupement"] = 0
            # liste des themes disponibles
            type_frequence_temp=["annee","mois","jour"]
            if "temp_plot_desordre_frequence.json" in st.session_state :
                st.session_state["defaut_temp_plot_desordre_frequence"] =  type_frequence_temp.index(st.session_state["temp_plot_desordre_frequence.json"])
            else :
                st.session_state["defaut_temp_plot_desordre_frequence"] = 0
            # liste des themes disponibles
            type_date_temp=["Date de début","Date de fin","Observation Date d'observation"]
            if "temp_plot_desordre_date.json" in st.session_state :
                st.session_state["defaut_temp_plot_desordre_date"] =  type_date_temp.index(st.session_state["temp_plot_desordre_date.json"])
            else :
                st.session_state["defaut_temp_plot_desordre_date"] = 0

            # selecteurs de parametres de graphique archive
            cola, colb = st.columns(2)
            with cola :
                st.session_state["temp_plot_desordre_frequence"] = st.selectbox("Périodicité :",type_frequence_temp,key="temp_plot_desordre_frequence_widget", index=st.session_state["defaut_temp_plot_desordre_frequence"])
            with colb :
                st.session_state["temp_plot_desordre_date"] = st.selectbox("Type de date :",type_date_temp,key="temp_plot_desordre_date_widget", index=st.session_state["defaut_temp_plot_desordre_date"])
            cola, colb, colc = st.columns(3)
            with cola :
                st.session_state["temp_plot_desordre_discretisation"] = st.selectbox("thématiques :",type_discretisation_temp , key="temp_plot_desordre_discretisation_widget",index=st.session_state["defaut_temp_plot_desordre_discretisation"])
            with colb :
                st.session_state["temp_plot_desordre_regroupement"] = st.selectbox("grouper par :",type_regroupement_temp , key="temp_plot_desordre_regroupement_widget",index=st.session_state["defaut_temp_plot_desordre_regroupement"])
            with colc :
                st.session_state["temp_plot_desordre_etiquettes"] = st.selectbox("étiquettes :",type_etiquettes_temp,key="temp_plot_desordre_etiquettes_widget", index=st.session_state["defaut_temp_plot_desordre_etiquettes"])
            cola,cold,cole = st.columns([12,3,1])
            with cola :
                affichage_temp_plot = st.toggle("Afficher/masquer le graphique du résumé périodique",key="but_graph_temp_desordre")
            with cold :
                # enregistrement des parametres
                if st.button("Sauvegarder dans la vue",key="but_save_temp_plot_desordre") :
                    rf.enregistrer_element_session_state("temp_plot_desordre_etiquettes",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/temp_plot_desordre_etiquettes.json")
                    rf.enregistrer_element_session_state("temp_plot_desordre_regroupement",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/temp_plot_desordre_regroupement.json")
                    rf.enregistrer_element_session_state("temp_plot_desordre_discretisation",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/temp_plot_desordre_discretisation.json")
                    rf.enregistrer_element_session_state("temp_plot_desordre_frequence",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/temp_plot_desordre_frequence.json")
                    rf.enregistrer_element_session_state("temp_plot_desordre_date",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/temp_plot_desordre_date.json")
            with cole :
    ########### création de l'export vers le tableau de bord ##########
                if st.button(":star:",key="fav_temp_des"):
                    sw.favoris_desordres("st.plotly_chart(fi.plot_temporel(desordres,'"+str(st.session_state["temp_plot_desordre_frequence"])+"',\""+str(st.session_state["temp_plot_desordre_date"])+"\",'"+str(st.session_state["temp_plot_desordre_regroupement"])+"','"+str(st.session_state["temp_plot_desordre_discretisation"])+"','"+str(st.session_state["temp_plot_desordre_etiquettes"])+"'))")
            if affichage_temp_plot :
                st.plotly_chart(fi.plot_temporel(df_desordre_select,st.session_state["temp_plot_desordre_frequence"],st.session_state["temp_plot_desordre_date"],st.session_state["temp_plot_desordre_regroupement"],st.session_state["temp_plot_desordre_discretisation"],st.session_state["temp_plot_desordre_etiquettes"]))
                # nomenclature
                if st.session_state["temp_plot_desordre_discretisation"] != "aucun" and st.session_state["temp_plot_desordre_discretisation"] != "archivage" :
                    dict_nom_arc={}
                    if st.toggle("afficher/masquer la nomenclature",key="but_temp_nomenclature_desordre") :
                        if st.session_state["temp_plot_desordre_discretisation"] == "type" :
                            for index,row in st.session_state["categorie_desordre"].sort_values("abrege_x").iterrows(): 
                                dict_nom_arc[row["abrege_x"]] = row["libelle_x"]
                            for key, item in dict_nom_arc.items() :
                                st.markdown("**" + str(key) + "** : " + str(item))
                        elif st.session_state["temp_plot_desordre_discretisation"] == "categorie" :
                            for index,row in st.session_state["categorie_desordre"].sort_values("abrege_y").iterrows(): 
                                dict_nom_arc[row["abrege_y"]] = row["libelle_y"]
                            for key, item in dict_nom_arc.items() :
                                st.markdown("**" + str(key) + "** : " + str(item))
                        elif st.session_state["temp_plot_desordre_discretisation"] == "suite" :
                            for index,row in st.session_state["suite_desordre"].sort_values("abrege").iterrows(): 
                                dict_nom_arc[row["abrege"]] = row["libelle"]
                            for key, item in dict_nom_arc.items() :
                                st.markdown("**" + str(key) + "** : " + str(item))
                        elif st.session_state["temp_plot_desordre_discretisation"] == "urgence" :
                            for index,row in st.session_state["desordre_urgence"].sort_values("abrege").iterrows(): 
                                dict_nom_arc[row["abrege"]] = row["libelle"]
                            for key, item in dict_nom_arc.items() :
                                st.markdown("**" + str(key) + "** : " + str(item))

    with st.expander("6 - Résumé par catégorie de désordre"):
        with st.container():
            # chargement données par défaut/enregistré :
            # etiquette
            type_etiquettes_cat = ["aucun","thématique","groupe"]
            if "cat_plot_desordre_etiquettes.json" in st.session_state :
                st.session_state["defaut_cat_plot_desordre_etiquettes"] =  type_etiquettes_cat.index(st.session_state["cat_plot_desordre_etiquettes.json"])
            else :
                st.session_state["defaut_cat_plot_desordre_etiquettes"] = 0
            # liste des themes disponibles
            type_discretisation_cat=["aucun","type","suite","urgence","archivage"]
            if "cat_plot_desordre_discretisation.json" in st.session_state :
                st.session_state["defaut_cat_plot_desordre_discretisation"] =  type_discretisation_cat.index(st.session_state["cat_plot_desordre_discretisation.json"])
            else :
                st.session_state["defaut_cat_plot_desordre_discretisation"] = 0
            # liste des themes disponibles
            type_regroupement_cat=["aucun","Tronçon","Digue","Système"]
            if "cat_plot_desordre_regroupement.json" in st.session_state :
                st.session_state["defaut_cat_plot_desordre_regroupement"] =  type_regroupement_cat.index(st.session_state["cat_plot_desordre_regroupement.json"])
            else :
                st.session_state["defaut_cat_plot_desordre_regroupement"] = 0

            # selecteurs de parametres de graphique 
            cola, colb, colc = st.columns(3)
            with cola :
                st.session_state["cat_plot_desordre_discretisation"] = st.selectbox("thématiques :",type_discretisation_cat , key="cat_plot_desordre_discretisation_widget",index=st.session_state["defaut_cat_plot_desordre_discretisation"])
            with colb :
                st.session_state["cat_plot_desordre_regroupement"] = st.selectbox("grouper par :",type_regroupement_cat , key="cat_plot_desordre_regroupement_widget",index=st.session_state["defaut_cat_plot_desordre_regroupement"])
            with colc :
                st.session_state["cat_plot_desordre_etiquettes"] = st.selectbox("étiquettes :",["aucun","thématique","groupe"],key="cat_plot_desordre_etiquettes_widget", index=st.session_state["defaut_cat_plot_desordre_etiquettes"])
            cola,cold,cole = st.columns([12,3,1])
            with cola :
                affichage_cat_plot = st.toggle("Afficher/masquer le graphique des catégories",key="but_graph_cat_desordre")
            with cold :
                # enregistrement des parametres
                if st.button("Sauvegarder dans la vue",key="but_save_cat_plot_desordre") :
                    rf.enregistrer_element_session_state("cat_plot_desordre_etiquettes",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/cat_plot_desordre_etiquettes.json")
                    rf.enregistrer_element_session_state("cat_plot_desordre_regroupement",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/cat_plot_desordre_regroupement.json")
                    rf.enregistrer_element_session_state("cat_plot_desordre_discretisation",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/cat_plot_desordre_discretisation.json")
            with cole :
    ########### création de l'export vers le tableau de bord ##########
                if st.button(":star:",key="fav_cat_des"):
                    sw.favoris_desordres("st.plotly_chart(fi.plot_cat(desordres, '"+str(st.session_state["cat_plot_desordre_etiquettes"])+"','"+str(st.session_state["cat_plot_desordre_regroupement"])+"','"+str(st.session_state["cat_plot_desordre_discretisation"])+"'))")
            if affichage_cat_plot :
                st.plotly_chart(fi.plot_cat(df_desordre_select, st.session_state["cat_plot_desordre_etiquettes"],st.session_state["cat_plot_desordre_regroupement"],st.session_state["cat_plot_desordre_discretisation"]))
                # nomenclature
                if st.session_state["cat_plot_desordre_discretisation"] != "aucun" and st.session_state["cat_plot_desordre_discretisation"] != "archivage" :
                    dict_nom_arc={}
                    if st.toggle("afficher/masquer la nomenclature",key="but_cat_nomenclature_desordre") :
                        if st.session_state["cat_plot_desordre_discretisation"] == "type" :
                            for index,row in st.session_state["categorie_desordre"].sort_values("abrege_x").iterrows(): 
                                dict_nom_arc[row["abrege_x"]] = row["libelle_x"]
                            for key, item in dict_nom_arc.items() :
                                st.markdown("**" + str(key) + "** : " + str(item))
                        elif st.session_state["cat_plot_desordre_discretisation"] == "categorie" :
                            for index,row in st.session_state["categorie_desordre"].sort_values("abrege_y").iterrows(): 
                                dict_nom_arc[row["abrege_y"]] = row["libelle_y"]
                            for key, item in dict_nom_arc.items() :
                                st.markdown("**" + str(key) + "** : " + str(item))
                        elif st.session_state["cat_plot_desordre_discretisation"] == "suite" :
                            for index,row in st.session_state["suite_desordre"].sort_values("abrege").iterrows(): 
                                dict_nom_arc[row["abrege"]] = row["libelle"]
                            for key, item in dict_nom_arc.items() :
                                st.markdown("**" + str(key) + "** : " + str(item))
                        elif st.session_state["cat_plot_desordre_discretisation"] == "urgence" :
                            for index,row in st.session_state["desordre_urgence"].sort_values("abrege").iterrows(): 
                                dict_nom_arc[row["abrege"]] = row["libelle"]
                            for key, item in dict_nom_arc.items() :
                                st.markdown("**" + str(key) + "** : " + str(item))

    with st.expander("7 - Résumé par Type de désordre"):
        with st.container():
            # chargement données par défaut/enregistré :
            # etiquette
            type_etiquettes_type = ["aucun","thématique","groupe"]
            if "type_plot_desordre_etiquettes.json" in st.session_state :
                st.session_state["defaut_type_plot_desordre_etiquettes"] =  type_etiquettes_type.index(st.session_state["type_plot_desordre_etiquettes.json"])
            else :
                st.session_state["defaut_type_plot_desordre_etiquettes"] = 0
            # liste des themes disponibles
            type_discretisation_type=["aucun","categorie","suite","urgence","archivage"]
            if "type_plot_desordre_discretisation.json" in st.session_state :
                st.session_state["defaut_type_plot_desordre_discretisation"] =  type_discretisation_type.index(st.session_state["type_plot_desordre_discretisation.json"])
            else :
                st.session_state["defaut_type_plot_desordre_discretisation"] = 0
            # liste des themes disponibles
            type_regroupement_type=["aucun","Tronçon","Digue","Système"]
            if "type_plot_desordre_regroupement.json" in st.session_state :
                st.session_state["defaut_type_plot_desordre_regroupement"] =  type_regroupement_type.index(st.session_state["type_plot_desordre_regroupement.json"])
            else :
                st.session_state["defaut_type_plot_desordre_regroupement"] = 0

            # selecteurs de parametres de graphique 
            cola, colb, colc = st.columns(3)
            with cola :
                st.session_state["type_plot_desordre_discretisation"] = st.selectbox("thématiques :",type_discretisation_type , key="type_plot_desordre_discretisation_widget",index=st.session_state["defaut_type_plot_desordre_discretisation"])
            with colb :
                st.session_state["type_plot_desordre_regroupement"] = st.selectbox("grouper par :",type_regroupement_type , key="type_plot_desordre_regroupement_widget",index=st.session_state["defaut_type_plot_desordre_regroupement"])
            with colc :
                st.session_state["type_plot_desordre_etiquettes"] = st.selectbox("étiquettes :",["aucun","thématique","groupe"],key="type_plot_desordre_etiquettes_widget", index=st.session_state["defaut_type_plot_desordre_etiquettes"])
            cola,cold,cole = st.columns([12,3,1])
            with cola :
                affichage_type_plot = st.toggle("Afficher/masquer le graphique des types",key="but_graph_type_desordre")
            with cold :
                # enregistrement des parametres
                if st.button("Sauvegarder dans la vue",key="but_save_type_plot_desordre") :
                    rf.enregistrer_element_session_state("type_plot_desordre_etiquettes",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/type_plot_desordre_etiquettes.json")
                    rf.enregistrer_element_session_state("type_plot_desordre_regroupement",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/type_plot_desordre_regroupement.json")
                    rf.enregistrer_element_session_state("type_plot_desordre_discretisation",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/type_plot_desordre_discretisation.json")
            with cole :
    ########### création de l'export vers le tableau de bord ##########
                if st.button(":star:",key="fav_type_des"):
                    sw.favoris_desordres("st.plotly_chart(fi.plot_type(desordres, '"+str(st.session_state["type_plot_desordre_etiquettes"])+"','"+str(st.session_state["type_plot_desordre_regroupement"])+"','"+str(st.session_state["type_plot_desordre_discretisation"])+"'))")
            if affichage_type_plot:
                st.plotly_chart(fi.plot_type(df_desordre_select, st.session_state["type_plot_desordre_etiquettes"],st.session_state["type_plot_desordre_regroupement"],st.session_state["type_plot_desordre_discretisation"]))
                # nomenclature
                if st.session_state["type_plot_desordre_discretisation"] != "aucun" and st.session_state["type_plot_desordre_discretisation"] != "archivage" :
                    dict_nom_arc={}
                    if st.toggle("afficher/masquer la nomenclature",key="but_type_nomenclature_desordre") :
                        if st.session_state["type_plot_desordre_discretisation"] == "type" :
                            for index,row in st.session_state["categorie_desordre"].sort_values("abrege_x").iterrows(): 
                                dict_nom_arc[row["abrege_x"]] = row["libelle_x"]
                            for key, item in dict_nom_arc.items() :
                                st.markdown("**" + str(key) + "** : " + str(item))
                        elif st.session_state["type_plot_desordre_discretisation"] == "categorie" :
                            for index,row in st.session_state["categorie_desordre"].sort_values("abrege_y").iterrows(): 
                                dict_nom_arc[row["abrege_y"]] = row["libelle_y"]
                            for key, item in dict_nom_arc.items() :
                                st.markdown("**" + str(key) + "** : " + str(item))
                        elif st.session_state["type_plot_desordre_discretisation"] == "suite" :
                            for index,row in st.session_state["suite_desordre"].sort_values("abrege").iterrows(): 
                                dict_nom_arc[row["abrege"]] = row["libelle"]
                            for key, item in dict_nom_arc.items() :
                                st.markdown("**" + str(key) + "** : " + str(item))
                        elif st.session_state["type_plot_desordre_discretisation"] == "urgence" :
                            for index,row in st.session_state["desordre_urgence"].sort_values("abrege").iterrows(): 
                                dict_nom_arc[row["abrege"]] = row["libelle"]
                            for key, item in dict_nom_arc.items() :
                                st.markdown("**" + str(key) + "** : " + str(item))