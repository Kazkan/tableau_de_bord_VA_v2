###############################################
# Gabriel NAVENNEC - 06/05/2025               #
# SYMBHI - FRANCE DIGUE - IUGA                #
#                                             #
# Version 1.0                                 #
###############################################

import streamlit as st
from utils import read_files as rf
from datetime import datetime
import pandas as pd
import os
import json
import shutil
import subprocess

def on_user_change():
    # Définir un indicateur de rechargement
    st.session_state["recharger_vue"] = True

def on_view_change():
    # Définir un indicateur de rechargement pour le contenu de la vue
    st.session_state["recharger_contenu"] = True

def entite_defaut_vide() :
    st.session_state["defaut_systeme"] = []
    st.session_state["defaut_digue"] = []
    st.session_state["defaut_troncon"] = []
    #st.write("coucou")
    #st.write(st.session_state["defaut_systeme"])
    #st.write(st.session_state["defaut_digue"])
    #st.write(st.session_state["defaut_troncon"])

def reset_session(vue) :
    if vue != "" :
        # on supprime les parametres de la vue courante
        for object in os.listdir(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+vue) :
            # on supprime le fichier json du session state
            del st.session_state[object]
        # on vide la liste des parametres de la vue courante
        st.session_state["parametre_vue"] = []

# fonction pour filtrer un dataframe selon une date
def filtre_table_date(table : pd.DataFrame, date_interval : st.session_state, date_debut : st.session_state) -> pd.DataFrame : # à changer si jamais table -> session state !!!!!!!!!!!!!!!!!!!!!
    if date_debut :
        return table[((table["Date de début"] >= datetime.strptime(str(date_interval[0]), "%Y-%m-%d").date()) & 
                                              (table["Date de début"] <= datetime.strptime(str(date_interval[1]), "%Y-%m-%d").date()))]
    else :
        return table[((table["Date de début"] <= datetime.strptime(str(date_interval[0]), "%Y-%m-%d").date()) & 
                                              (table["Date de fin"] >= datetime.strptime(str(date_interval[1]), "%Y-%m-%d").date())) | 
                                              ((table["Date de début"] >= datetime.strptime(str(date_interval[0]), "%Y-%m-%d").date()) & 
                                              (table["Date de début"] <= datetime.strptime(str(date_interval[1]), "%Y-%m-%d").date())) |
                                              ((table["Date de fin"] >= datetime.strptime(str(date_interval[0]), "%Y-%m-%d").date()) & 
                                               (table["Date de fin"] <= datetime.strptime(str(date_interval[1]), "%Y-%m-%d").date())) |
                                               ((table["Date de début"] <= datetime.strptime(str(date_interval[1]), "%Y-%m-%d").date()) & 
                                               (table["Date de fin"].isna()))
                                               ]
    
# fonction pour filtrer un dataframe selon une date d'observation
def filtre_table_obs_date(table : pd.DataFrame, date_interval : st.session_state, nul : st.session_state) -> pd.DataFrame :
    if nul :
        return table[((table["Observation Date d'observation"] >= datetime.strptime(str(date_interval[0]), "%Y-%m-%d").date()) & 
                                                (table["Observation Date d'observation"] <= datetime.strptime(str(date_interval[1]), "%Y-%m-%d").date()) | table["Observation Date d'observation"].isna())]  
    else :
        return table[((table["Observation Date d'observation"] >= datetime.strptime(str(date_interval[0]), "%Y-%m-%d").date()) & 
                                        (table["Observation Date d'observation"] <= datetime.strptime(str(date_interval[1]), "%Y-%m-%d").date()))] 

# fonction pour filtrer un dataframe selon les niveaux d'urgences
def filtre_table_urgence(table : pd.DataFrame, urgences : st.session_state) -> pd.DataFrame :
    table_stockage = pd.DataFrame() 
    for urgence in urgences :
        table_stockage = pd.concat([table_stockage, pd.DataFrame(table)[pd.DataFrame(table)["Observation Urgence"] == urgence]])
    return table_stockage

# fonction pour filtrer un dataframe selon si les données sont archivés
def filtre_table_archive(table : pd.DataFrame, arch : st.session_state, nonarch : st.session_state) -> pd.DataFrame :
    # applique le filtre archivé s'il existe
    if not arch :
        table = table[table["Date de fin"].isna()]
    # applique le filtre archivé s'il existe
    if not nonarch :
        table = table[table["Date de fin"].notna()]
    return table

# fonction pour filtrer un dataframe la géométrie :
def filtre_table_geom(table : pd.DataFrame, pt : st.session_state, ligne : st.session_state) -> pd.DataFrame :
    if not pt :
        table = table[table["PR de début"] != table["PR de fin"]]
    if not ligne :
        table = table[table["PR de début"] == table["PR de fin"]]
    return table

# fonction pour filtrer un dataframe sur ses colonnes
def filtre_table_colonne(table : pd.DataFrame, col_filtre : st.session_state) -> pd.DataFrame :
    table = table.filter(items=col_filtre)
    return table

def filtre_valeur_liste(table : pd.DataFrame, champ : str, valeurs : st.session_state) :
    table = table[table[champ].isin(valeurs)]
    return table

# fonction d'enregistrement des favoris dans le tableau de bord
@st.dialog("Favoris")
def favoris_desordres(item) :
    # récupération de la liste des index
    index=0
    list_index=[]
    for cle,valeur in st.session_state["tableau_de_bord.json"].items() :
        list_index.append(valeur["index"])
    if list_index != [] :
        list_index.sort()
        index = list_index[-1]
    # nom de l'objet
    title = st.text_input("nom :","Figure "+str(index+1),key="tdb_nom_widget")
    # index, ordre d'affichage
    number = st.number_input("position :",min_value=0, value=index+1, key="tdb_index_widget")
    if st.button("Charger dans le tableau de bord :",key="butt_desordre_tdb") :
        # controle que le nom ne soit pas déjà utilisé comme clé.
        if title in list(st.session_state["tableau_de_bord.json"].keys()) : 
            st.warning("le nom de l'enregistrement est déjà utilisé, veuillez en choisir un nouveau différent de : "+str(list(st.session_state["tableau_de_bord.json"].keys())))
        # controle que l'index soit disponible
        elif number in list_index :
            st.warning("l'index de la position est déjà utilisé, veuillez en choisir un nouveau différent de : "+str(list_index))
        else :
        # création du dictionnaire de code filtre
            st.session_state["tableau_de_bord.json"][title] = {"index":number,
                                                                "filtre":f"""filtre1={st.session_state["param_systeme"]}
desordres=desordres_init
if filtre1 != [] :
    desordres = rf.filtre_table_ref(desordres,"Système", filtre1)
filtre2={st.session_state["param_digue"]}
if filtre2 != [] :
    desordres = rf.filtre_table_ref(desordres,"Digue", filtre2)
filtre3={st.session_state["param_troncon"]}
if filtre3 != [] :
    desordres = rf.filtre_table_ref(desordres,"Tronçon", filtre3)
desordres = sw.filtre_table_date(desordres, {st.session_state["param_desordre_periode"]}, {st.session_state["param_desordre_date_debut"]})
desordres = sw.filtre_table_obs_date(desordres, {st.session_state["param_desordre_periode_obs"]}, {st.session_state["param_desordre_obs_date_nul"]})
filtre4={st.session_state["param_desordre_urgence"]}
if filtre4 != [] :
    desordres = sw.filtre_table_urgence(desordres, filtre4)
desordres = sw.filtre_table_archive(desordres, {st.session_state["param_desordre_archive"]}, {st.session_state["param_desordre_nonarchive"]})
filtre5={st.session_state["param_desordre_auteur"]}
if filtre5 != [] :
    desordres = sw.filtre_valeur_liste(desordres, "Auteur",filtre5)
filtre6={st.session_state["param_desordre_observateur"]}
if filtre6 != [] :
    desordres = sw.filtre_valeur_liste(desordres, "Observation Observateur",filtre6)
filtre7={st.session_state["param_desordre_suite"]}
if filtre7 != [] :
    desordres = sw.filtre_valeur_liste(desordres, "Observation Suite à apporter",filtre7)
filtre8={st.session_state["param_desordre_categorie"]}
if filtre8 != [] :
    desordres = sw.filtre_valeur_liste(desordres, "Catégorie de désordre",filtre8)
filtre9={st.session_state["param_desordre_type"]}
if filtre9 != [] :
    desordres = sw.filtre_valeur_liste(desordres, "Type de désordre",filtre9)
desordres = sw.filtre_table_geom(desordres, {st.session_state["param_desordre_geom_pt"]}, {st.session_state["param_desordre_geom_ligne"]})
""",
                                                                         "code":item}
            rf.enregistrer_element_session_state("tableau_de_bord.json",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/tableau_de_bord.json")
            st.rerun()
    
# fonction de création de vue
@st.dialog("Création d'une vue")
def menu_crea_vue() :
    # décompte des vues existente pour le répertoire de l'utilisateurs courant
    index = len(os.listdir(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]))
    # nom de la vue à créer
    nom = st.text_input("nom :","nouvelle vue "+str(index+1),key="tdb_crea_vue_widget")
    # bouton de création de la vue
    if st.button("Enregistrer", key="but_creer_vue") :
        # processus de création de vue
        if nom not in os.listdir(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]):
            # on créé un dictionnaire pour accueillir les informations de la vue
            vue_dict_ref = {}
            vue_dict_desordres = {}
            # examiner si un des dossiers de vues de l'utilisateurs dispose d'un fichier ref_systeme.json
            for object in os.listdir(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]):
                # examiner le fichier de reference des systèmes 
                if os.path.isdir(os.path.join(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0], object)) and "ref_systeme.json" in os.listdir(os.path.join(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0], object)):
                    # on recupere le nom de la vue et la date de creation du fichier ref
                    vue_dict_ref[object] = rf.date_fichier((st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+object+"/ref_systeme.json"))
                # examiner les fichier thematique
                if os.path.isdir(os.path.join(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0], object)) and "desordres.json" in os.listdir(os.path.join(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0], object)):
                    # on recupere le nom de la vue et la date de creation du fichier desordres
                    vue_dict_desordres[object] = rf.date_fichier((st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+object+"/desordres.json"))
            # création du répertoire de la nouvelle vue
            os.mkdir(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+nom)
            if vue_dict_ref != {} :
                # on récupère la vue la plus récente
                vue_récente = max(vue_dict_ref, key=vue_dict_ref.get)
                # création du fichier de référence dans le répertoire de la vue
                shutil.copyfile(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+vue_récente+"/ref_systeme.json", st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+nom+"/ref_systeme.json")                        
            if vue_dict_desordres != {} :
                # on récupère la vue la plus récente
                vue_récente_desordres = max(vue_dict_desordres, key=vue_dict_desordres.get)
                # création du fichier desordres dans le répertoire de la vue
                shutil.copyfile(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+vue_récente_desordres+"/desordres.json", st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+nom+"/desordres.json")
            st.success("la vue "+nom+" a été créée")
            st.session_state["vue_courante"] = nom
            st.rerun()
        else:
            st.warning("la vue "+nom+" existe déjà")

# fonction de renommage des vues
@st.dialog("Renommer une vue")
def menu_renom_vue() :
    st.write('Vue courante :')
    st.markdown(":blue[**"+st.session_state["vue_courante"]+"**]")
    # nouveau nom de la vue
    nom = st.text_input("nouveau nom :", st.session_state["vue_courante"], key="tdb_renom_vue_widget")
    # déclencher le renommage de la vue
    if st.button("Enregistrer", key="but_ren_save_vue") :
        if nom not in os.listdir(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]) and st.session_state["vue_courante"] in os.listdir(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]):
            # on renomme la vue
            os.rename(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"], st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+nom)
            st.success("la vue "+nom+" a été renommée")
            st.session_state["vue_courante"] = nom
            st.rerun()
        else:
            st.warning("la vue "+st.session_state["vue_courante"]+" n'existe pas ou le nom de la nouvelle vue existe déjà")
    


