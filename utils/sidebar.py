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
import utils.st_widget as sw
import st_pages
from st_pages import get_nav_from_toml, add_page_title

# création du contenu de la sidebar dans une fonction appelable
def sidebar_content() :
    with st.sidebar:
    #    st.write(dir(st_pages))
    #    
    #    nav = get_nav_from_toml(rf.rep_int("toml"))
    #    pg = st.navigation(nav)
    #    add_page_title(pg)
    #    pg.run()


##########  choix de l'utilisateur et de la vue ##########

        # récupération de l'index de l'utilisateur en cour s'il existe et si le session state est chargé
        if "utilisateur_courant"  in st.session_state and st.session_state["utilisateur_courant"] in list(dict(sorted(st.session_state["utilisateurs"].items())).keys()):
            index_utilisateur =list(dict(sorted(st.session_state["utilisateurs"].items())).keys()).index(st.session_state["utilisateur_courant"])
        else :
            # sinon index par défaut
            index_utilisateur=0
        
        with st.container(): 
            # choix de l'utilisateur
            st.session_state["utilisateur_courant"] = st.selectbox("Profil utilisateur :",list(dict(sorted(st.session_state["utilisateurs"].items())).keys()),index=index_utilisateur,key="sel_utilisateur_courant",on_change=sw.on_user_change)
            ############# nécessite une double selection pour se mettre à jour : à corriger !!!!!!!!!
            # Vérification de l'indicateur de rechargement
            if st.session_state.get("recharger_vue", False):
                # Réinitialise la vue courante et réinitialise le flag
                st.session_state["vue_courante"] = ""
                st.session_state["recharger_vue"] = False
                st.rerun()
            # récupération de la liste des vues
            if st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0] == "aucun" or st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0] == "" :
                # gestion du coup de figure ou le répertoire n'a pas été défini
                st.caption("aucun répertoire d'enregistrement n'a été défini (voir paramètre utilisateurs)")
            else :
                # selection des vues
                # test si le repertoire est valide
               # sélection des vues
                if os.listdir(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]):
                    list_vue = []
                    for object in os.listdir(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]):
                        if os.path.isdir(os.path.join(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0], object)):
                            list_vue.append(object)

                    # récupération de l'index de la vue en cours s'il existe
                    if "vue_courante" in st.session_state and st.session_state["vue_courante"] in list_vue:
                        index_vue = list_vue.index(st.session_state["vue_courante"])
                    else:
                        index_vue = 0
                    # Sélection de la vue
                    nouvelle_vue = st.selectbox(
                        "Vue :",
                        list_vue,
                        index=index_vue,
                        key="sel_vue_courant"
                    )
                    # Si la vue a changé, on déclenche le rechargement
                    if "vue_courante" not in st.session_state or nouvelle_vue != st.session_state["vue_courante"]:
                        st.session_state["vue_courante"] = nouvelle_vue
                        st.session_state["recharger_contenu"] = True
                        st.rerun()
                    # Rechargement du contenu de la vue
                    if st.session_state.get("recharger_contenu", False):
                        st.session_state["recharger_contenu"] = False

                    # Création d'une liste de paramètres chargés
                    st.session_state["parametre_vue"] = []
                    vue_path = os.path.join(
                        st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0],
                        st.session_state["vue_courante"]
                    )
                    # Chargement des JSON de la vue courante
                    if os.path.exists(vue_path):
                        for object in os.listdir(vue_path):
                            json_path = os.path.join(vue_path, object)
                            if os.path.isfile(json_path):
                                with open(json_path, "r", encoding="utf-8") as file:
                                    st.session_state[object] = json.load(file)
                                st.session_state["parametre_vue"].append(object)

                    # Suppression des paramètres résiduels
                    element_supr = []
                    for object in st.session_state:
                        element_supr.append(object)

                    for object in element_supr:
                        if object not in st.session_state["parametre_vue"] and object.endswith(".json"):
                            del st.session_state[object]  
                    # suppression des elements d'affichage
                    if "affichage_graph_lin" in st.session_state: 
                        del st.session_state["affichage_graph_lin"]
                    if "affichage_graph_bar" in st.session_state:
                        del st.session_state["affichage_carte_desordre"]
                    if "tableau_de_bord.json" not in st.session_state :
                        st.session_state["tableau_de_bord.json"]={}

                # gestion du cas de figure ou aucune vue n'est enregistré dans le répertoire
                else :
                    st.caption("Aucune vue enregistrée")

                



        ########## enregistrement/suprresion d'une nouvelle vue ##########

        st.divider()

        with st.container(): 

            st.markdown("### Gestion des vues")

            cola,colb = st.columns(2)

            with cola :
                # déclencher l'enregistrement de la vue
                if st.button("Créer     ", key="but_nouvelle_vue") :
                    sw.menu_crea_vue()
                                    
            with colb :
                # déclencher le renommage de la vue
                if st.button("Renommer  ", key="but_ren_vue") :
                    sw.menu_renom_vue()

            cola,colb = st.columns(2)
            with cola :
                # déclencher la copie de la vue
                if st.button("Copier    ", key="but_cop_vue") :
                    if st.session_state["vue_courante"] in os.listdir(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]):
                        #itération pour compter les éventuelles copies déjà existentes
                        i=0
                        for object in os.listdir(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]) :
                            if object[:-1] == st.session_state["vue_courante"]+" copie " :
                                # on récupère le numéro de la copie
                                num_copie = int(object[-1])
                                # on incrémente le numéro de la copie
                                if num_copie > i :
                                    i = num_copie
                        # copie de la vue
                        shutil.copytree(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"], st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"]+" copie "+str(i+1))
                        st.success("la vue "+st.session_state["vue_courante"]+" a été copiée")
                        st.session_state["vue_courante"] = st.session_state["vue_courante"]+" copie "+str(i+1)
                        st.rerun()
                    else:
                        st.warning("la vue "+st.session_state["vue_courante"]+" n'existe pas")
            with colb :
                # déclencher la suppresion de la vue
                if st.button("Supprimer ", key="but_sup_vue") :
                    if st.session_state["vue_courante"]  in os.listdir(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]):
                        shutil.rmtree(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"])
                        st.success("la vue "+st.session_state["vue_courante"]+" a été supprimée")
                        st.rerun()
                    else:
                        st.warning("la vue "+st.session_state["vue_courante"]+" n'existe pas")
        
            cola,colb = st.columns(2)
            # exporter une vue dans un répertoire
            with cola :
                # bouton de lancement 
                if st.button("Exporter  ", key="but_exporter_vue") :
                    # répertoire d'enregistrement 
                    rep_export = subprocess.run(["python", rf.rep_int("application") + "/utils/tk_widget.py"],capture_output=True, text=True, check=True).stdout.strip()
                    # on vérifie que le répertoire existe
                    if os.path.exists(rep_export) :
                        # on controle que la vue n'existe pas déjà dans le répertoire de copie
                        if os.path.exists(rep_export+"/"+st.session_state["vue_courante"]) :
                            st.warning("la vue existe déjà dans le répertoire de destination")
                        else :
                        # on copie le répertoire de la vue
                            shutil.copytree(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+st.session_state["vue_courante"], rep_export+"/"+st.session_state["vue_courante"])
                    else :
                        st.warning("le répertoire sélectionné n'existe pas")
            # importer une vue dans le répertoire utilisateur
            with colb :
                # bouton de lancement 
                if st.button("Importer  ", key="but_importer_vue") :
                    # répertoire d'enregistrement 
                    rep_import = subprocess.run(["python", rf.rep_int("application") + "/utils/tk_widget.py"],capture_output=True, text=True, check=True).stdout.strip()
                    # on vérifie que le répertoire existe
                    if os.path.exists(rep_import) :
                        # récupération du nom du dossier
                        nom_dossier = os.path.basename(rep_import)
                        # controle la pré existence d'un fichier du même nom
                        if os.path.exists(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+nom_dossier) :
                            st.warning("La vue existe déjà dans le répertoire de l'utilisateur")
                        else :
                            # on copie le répertoire de la vue
                            shutil.copytree(rep_import, st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+nom_dossier)
                            st.rerun()
                    else :
                        st.warning("le répertoire sélectionné n'existe pas")