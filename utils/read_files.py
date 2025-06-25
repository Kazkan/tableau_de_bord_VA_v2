###############################################
# Gabriel NAVENNEC - 06/05/2025               #
# SYMBHI - FRANCE DIGUE - IUGA                #
#                                             #
# Version 1.0                                 #
###############################################

import pandas as pd
import os
import datetime
import numpy as np
import json
import streamlit as st

# fonction de récupération des répertoires internes de l'applications
def rep_int(type : str) -> str :
    # récupération du répertoire de l'application
    output = os.path.dirname(os.path.abspath(__file__))
    # renvoie du répertoire de l'application
    if type == "application" :
        return ""
    # renvoie du répertoire des données propres à l'application
    if type == "data" :
        return "data"
    # renvoie du répertoire des pages
    if type == "pages" :
        return "pages"  
    # renvoie du répertoire du fichier de reference des systemes propres à l'application  : OBSOLETE
    #if type == "systeme" :
    #    return "tableau_de_bord/data/ref_system.json")
    # renvoie du répertoire du fichier de reference des systemes propres à l'application  : V2
    if type == "systeme" :
        return str(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/ref_systeme.json")
    # renvoie du répertoire du fichier des utilisateurs
    if type == "utilisateurs" :
        return "data/utilisateurs.json"
        # renvoie du répertoire du fichier des utilisateurs
    if type == "rep_utilisateurs" :
        return "data/rep_utilisateurs.json"
    # renvoie du répertoire des fichiers des thématiques : OBSOLETE
    # if type == "thematique" :
    #    return str(output[:-6]+"\data/thematique")
    # renvoie du fichier des fichiers des thematiques : V2
    if type == "desordres" :
        return str(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/desordres.json")
    if type == "prestations" :
        return str(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/prestations.json")
    if type == "reseaux" :
        return str(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/reseaux.json")
    #tableau de bord
    if type == "tableau" :
        return str(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+"/tableau_de_bord.json")
    # renvoie du répertoire du fichier des catégorie de désordre
    if type == "cat_desordre" :
        return "data/categorie_desordre.json"
    # renvoie du répertoire du fichier des suite de désordre
    if type == "suite_desordre" :
        return "data/suite_desordre.json"
    # renvoie du répertoire du fichier des codes desordres
    if type == "code_urgence" :
        return "data/desordre_urgence.json"
    # renvoie du repertoire des images
    if type == "images" :
        return "data/img"
    # renvoie du répertoire du fchier toml
    if type == "toml" :
        return ".streamlit/pages.toml"
    
# fonction pour obtenir la date de création d'un fichier
def date_fichier(chemin : str) -> str :
     return datetime.datetime.fromtimestamp(os.stat(chemin)[8]).strftime("%Y-%m-%d %H:%M:%S")

# récupération des noms de champs dans une liste
def csv_list_nom_champs(chemin : str, separateur : str) -> list :
    return pd.read_csv(chemin, sep=separateur).columns.tolist()

# fonction de création d'un dataframe pandas pour les fichiers de références
def ref_to_df(chemin_source : str, separateur : str, systeme : str, digue : str, troncon : str) -> pd.DataFrame:
    # import du tableau avec uniquement les colonnes renseigné dans la fonction
    df = pd.read_csv(chemin_source, sep=separateur)[[systeme, digue, troncon ]]
    # renommage des colonnes de manière standard
    df = df.rename(columns={systeme: 'Système', digue: 'Digue', troncon : 'Tronçon'})
    # remettre la lecture fichier à zéro après la visualisation
    chemin_source.seek(0)
    # renvoie du dataframe d'un extrait créé
    return df

# fonction pour transformer un objet pour etre enregistrable en fichier json pour être réutilisé
def nettoyer_objet_json(obj):
    if isinstance(obj, pd.DataFrame):
        return obj.astype(str).to_dict(orient="records")
    # Gestion des Series
    if isinstance(obj, pd.Series):
        return obj.astype(str).tolist()
    # Gestion des Numpy arrays et objets Numpy
    if isinstance(obj, (np.ndarray, np.generic)):
        return obj.tolist()
    # Gestion des objets datetime
    if isinstance(obj, (pd.Timestamp, datetime.datetime)):
        return obj.isoformat()
    # Gestion des dictionnaires
    if isinstance(obj, dict):
        return {str(k): nettoyer_objet_json(v) for k, v in obj.items()}
    # Gestion des listes, tuples et ensembles
    if isinstance(obj, (list, tuple, set)):
        return [nettoyer_objet_json(item) for item in obj]
    # Gestion des objets JSON-compatibles
    try:
        json.dumps(obj)
        return obj
    except (TypeError, OverflowError):
        return str(obj)

# fonction pour enregistrer un élément en particulier du session state en json
def enregistrer_element_session_state(nom_variable: str, chemin_fichier: str):
    try:
        # nettoyage de l'élément à enregistrer via la fonction adéquat
        element_pretraite = nettoyer_objet_json(st.session_state[nom_variable])
        # enregistrement du fichier en json
        with open(chemin_fichier, "w", encoding="utf-8") as f:
            json.dump(element_pretraite, f, ensure_ascii=False, indent=2)
        # message si ça a fonctionné
        #st.success(f"Élément '{nom_variable}' enregistré dans '{chemin_fichier}'.")
    # message d'erreur
    except Exception as erreur:
        st.error(f"Erreur lors de l'enregistrement : {erreur}")

# fonction de récupération des données thématiques selon un élément d'endiguement séléctionné
def import_tables_theme(chemin_theme : list) -> pd.DataFrame :
    # création d'un tableau vide de stockage des données
    df_stockage = pd.DataFrame()
    # boucle sur les fichiers uploadés
    for file in chemin_theme :
        # création du dataframe à partir du fichier examiné
        df_themes = pd.read_csv(file, sep = ',')
            # ajout de la table analysé à la table de stockage
        df_stockage = pd.concat([df_stockage, df_themes])
    df_stockage.sort_values('Date de début', ascending=True, inplace=True)
    return df_stockage

########## gestion des dataframes ###########

# fonction pour filtre la table de référence selon
def filtre_table_ref(table : st.session_state, element : str, entites : list) -> pd.DataFrame :
    table_stockage = pd.DataFrame() 
    for entite in entites :
        table_stockage = pd.concat([table_stockage, pd.DataFrame(table)[pd.DataFrame(table)[element] == entite]])
    return table_stockage
    
# fonction qui renvoie la liste des éléments d'endiguements choisies
def list_dig(table : st.session_state, element : str) -> list :
    # création d'une liste avec tout les elements uniques détecté en colonne 0
    return pd.unique(pd.DataFrame(table)[element]).tolist()

# fonction de récupération des données thématiques selon un élément d'endiguement séléctionné
def extract_data_them(table_systeme : st.session_state, table_theme : st.session_state) :
    # filtre de la table thématique selon les élément choisi
    df_theme_filtre = pd.merge(pd.DataFrame(table_theme), pd.DataFrame(table_systeme), left_on = ['Tronçon'], right_on = ['Tronçon'])
    df_theme_filtre.sort_values('Date de début', ascending=True, inplace=True)
    return df_theme_filtre

##############################################################
##############################################################



# fonction d'écriture du fichier interne de référencement des tronçons selon systeme
def write_dig(chemin_source : str, chemin_cible : str, separateur : str, systeme : str, digue : str, troncon : str) :
    # import du tableau avec uniquement les colonnes renseigné dans la fonction
    df = pd.read_csv(chemin_source, sep=separateur)[[systeme, digue, troncon ]]
    # renommage des colonnes de manière standard
    df = df.rename(columns={systeme: 'systeme', digue: 'digue', troncon : 'troncon'})
    # écriture du nouveau fichier 
    df.to_csv(chemin_cible, index=False, encoding='utf-8-sig')
    

