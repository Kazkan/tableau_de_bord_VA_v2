###############################################
# Gabriel NAVENNEC - 06/05/2025               #
# SYMBHI - FRANCE DIGUE - IUGA                #
#                                             #
# Version 1.0                                 #
###############################################

import streamlit as st
import pandas as pd
import os
import datetime
import utils.read_files as rf
import utils.st_widget as sw
import subprocess
import json
import shutil
import utils.sidebar as sb

# affichage de la gestion des utilisateurs
sb.sidebar_content()

# titre de la page
st.title("Paramètres")
st.divider()

# avertissement de l'existence et de la date du dernier fichier de mise à jour
# vérification de l'existence d'un fichier de systemes d'endiguement dans les données internes

# administrateur seulement
# administrateur seulement
if st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][1] != "Administrateur" :
    st.warning("Vous n'avez pas les droits pour accéder à cette page. Seul un administrateur peut modifier les paramètres de l'application.")
elif st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][1] == "Administrateur" :

    ########## charger le fichier de référence des sytemes d'endiguement ##########

    # section sous forme d'onglet
    with st.expander("1 - Mise à jour du fichier des systèmes d'endiguements pour plusieurs utilisateurs"):

        st.write("Le fichier des systèmes d'endiguements est une table contenant les correspondances entre les systèmes d'endiguement, les digues et les tronçons. Il est nécessaire pour le bon fonctionnement de l'application.")

        # indications sur la méthode pour générer la table de référence à charger
        st.text("Si besoin, la table peut être obtenu avec SIRS dans le menu \"Recherche\" et dans l'option \" Requête SQL\". Créez la table en insérant le code SQL suivant dans le champ \"Requête\" et enregistrez le résultat en csv :")
        st.code('SELECT S."libelle" AS systeme, D."libelle" AS digue, T."libelle" AS troncon\nFROM "TronconDigue" T\n     JOIN "Digue" D ON (T."digueId" = D."id")\n     JOIN "SystemeEndiguement" S ON (D."systemeEndiguementId" = S."id") \n;', language="sql")

        # import des tables de référence au format csv
        uploaded_file = st.file_uploader("Import du fichier csv", type="csv", accept_multiple_files=False)

        # affichage du paramettrage conditionné au chargement des fichiers
        if uploaded_file :
            # définition du séparateur (par défaut ",")
            separateur = st.text_input("Séparateur :", value=";")
            # création des noms de champs dans une liste pour servir les futurs paramètres
            list_element = rf.csv_list_nom_champs(uploaded_file,separateur)
            # réinitialisation du csv pour les prochaines lectures
            uploaded_file.seek(0)
            # définition du champ contenant les systemes d'endiguement
            systeme = st.selectbox("champ des systemes d'endiguements :",list_element)
            # définition du champ contenant les digues
            digue = st.selectbox("champ des digues :",list_element)
            # définition du champ contenant les tronçons
            troncon = st.selectbox("champ des tronçons :",list_element)
            # traitement du fichier de référence
            cola,colb = st.columns(2)
            with cola :
                # bouton pour déclencher le chargement du fichier de référence
                charg_ref = st.toggle("Charger dans le tableau de bord", value=False,key="but_charg_ref")
            if charg_ref :
                # prévisualisation des données
                st.write("Prévisualisation :")
                st.dataframe(rf.ref_to_df(uploaded_file, separateur, systeme, digue, troncon))
                #  si chargement, prévisualisation et bouton pour déclencher la sauvegarde du fichier de référence
                # bouton de sauvegarde
                with colb :
                    st.session_state["ref_systeme"] = rf.ref_to_df(uploaded_file, separateur, systeme, digue, troncon)
                    # bouton pour déclencher la sauvegarde du fichier de référence
                    utilisateurs_cibles = st.multiselect("Utilisateurs ciblés :",list(dict(sorted(st.session_state["utilisateurs"].items())).keys()), key="but_utilsiateur_ref_select_save")
                    sauv_ref = st.button('Sauvegarder pour tous',key="but_sauv_ref_all_user")
                    # enregistrement des références
                    if sauv_ref :
                        for utilisateur in utilisateurs_cibles :
                            for vue in os.listdir(st.session_state["utilisateurs"][utilisateur][0]):
                                rf.enregistrer_element_session_state("ref_systeme",st.session_state["utilisateurs"][utilisateur][0]+"/"+vue+"/ref_systeme.json")
                        # suppression de la sessions state pour éviter les doublons avec le json
                        del st.session_state["ref_systeme"]
                        st.rerun()

    # fin de la section            
    st.divider()

    ########## charger le fichier des thématiques des sytemes d'endiguement pour tous les utilisateurs ##########

    # section sous forme d'onglet
    with st.expander('2 - Mise à jour des fichiers des thématiques pour plusieurs utilisateurs'):

        # indications sur la méthode pour générer les tables thématiques
        st.text('Les tables thématiques sont issues des extractions du plugin "couchDB importer" enregistré en .csv')

        cola, colb, colc = st.columns(3)
        # import des fichiers de thématiques au format csv
        with cola :
            # sélection des fichiers à importer
            file_desordre = st.file_uploader("csv des désordres", type="csv", accept_multiple_files=True)
            # conditionné selon l'upload du fichier
            if file_desordre :
                # création du dataframe pandas
                df_desordre_total = rf.import_tables_theme(file_desordre)
                charg_desordre = st.toggle("Charger dans le tableau de bord", value=False,key="but_charg_desordre")
                #  si chargement, prévisualisation et bouton pour déclencher la sauvegarde du fichier de référence
                if charg_desordre :
                    # prévisualisation des données
                    st.write("Prévisualisation :")
                    st.dataframe(df_desordre_total)
                    # bouton de sauvegarde
                    st.session_state["them_desordre"] = df_desordre_total
                    # bouton pour déclencher la sauvegarde du fichier de référence
                    utilisateurs_cibles = st.multiselect("Utilisateurs ciblés :",list(dict(sorted(st.session_state["utilisateurs"].items())).keys()), key="but_utilsiateur_desordre_select_save")
                    sauv_desordres = st.button('Sauvegarder pour tous',key="but_sauv_desordres_all_user")
                    # enregistrement des références
                    if sauv_desordres :
                        for utilisateur in utilisateurs_cibles :
                            for vue in os.listdir(st.session_state["utilisateurs"][utilisateur][0]):
                                rf.enregistrer_element_session_state("them_desordre",st.session_state["utilisateurs"][utilisateur][0]+"/"+vue+"/desordres.json")
                        # suppression de la sessions state pour éviter les doublons avec le json
                        del st.session_state["them_desordre"]
                        st.rerun()

        with colb :
            # sélection des fichiers à importer
            file_prestation = st.file_uploader("csv des prestations", type="csv", accept_multiple_files=True)
            # conditionné selon l'upload du fichier
            if file_prestation :
                # création du dataframe pandas
                df_prestation_total = rf.import_tables_theme(file_prestation)
                charg_prestation = st.toggle("Charger dans le tableau de bord", value=False,key="but_charg_prestation")
                #  si chargement, prévisualisation et bouton pour déclencher la sauvegarde du fichier de référence
                if charg_prestation :
                    # prévisualisation des données
                    st.write("Prévisualisation :")
                    st.dataframe(df_prestation_total)
                    # bouton de sauvegarde
                    st.session_state["them_prestation"] = df_prestation_total
                    # bouton pour déclencher la sauvegarde du fichier de référence
                    utilisateurs_cibles = st.multiselect("Utilisateurs ciblés :",list(dict(sorted(st.session_state["utilisateurs"].items())).keys()), key="but_utilsiateur_prestation_select_save")
                    sauv_prestation = st.button('Sauvegarder pour tous',key="but_sauv_prestation_all_user")
                    # enregistrement des références
                    if sauv_prestation :
                        for utilisateur in utilisateurs_cibles :
                            for vue in os.listdir(st.session_state["utilisateurs"][utilisateur][0]):
                                rf.enregistrer_element_session_state("them_prestation",st.session_state["utilisateurs"][utilisateur][0]+"/"+vue+"/prestations.json")
                        # suppression de la sessions state pour éviter les doublons avec le json
                        del st.session_state["them_prestation"]
                        st.rerun()

        with colc :
            # sélection des fichiers à importer
            file_reseau = st.file_uploader("csv des réseaux", type="csv", accept_multiple_files=True)
            # conditionné selon l'upload du fichier
            if file_reseau :
                # création du dataframe pandas
                df_reseau_total = rf.import_tables_theme(file_reseau)
                charg_reseau = st.toggle("Charger dans le tableau de bord", value=False,key="but_charg_reseau")
                #  si chargement, prévisualisation et bouton pour déclencher la sauvegarde du fichier de référence
                if charg_reseau :
                    # prévisualisation des données
                    st.write("Prévisualisation :")
                    st.dataframe(df_reseau_total)
                    # bouton de sauvegarde
                    st.session_state["them_reseau"] = df_reseau_total
                    # bouton pour déclencher la sauvegarde du fichier de référence
                    utilisateurs_cibles = st.multiselect("Utilisateurs ciblés :",list(dict(sorted(st.session_state["utilisateurs"].items())).keys()), key="but_utilsiateur_reseau_select_save")
                    sauv_reseau = st.button('Sauvegarder pour tous',key="but_sauv_reseau_all_user")
                    # enregistrement des références
                    if sauv_reseau :
                        for utilisateur in utilisateurs_cibles :
                            for vue in os.listdir(st.session_state["utilisateurs"][utilisateur][0]):
                                rf.enregistrer_element_session_state("them_reseau",st.session_state["utilisateurs"][utilisateur][0]+"/"+vue+"/reseaux.json")
                        # suppression de la sessions state pour éviter les doublons avec le json
                        del st.session_state["them_reseau"]
                        st.rerun()

    # fin de la section
    st.divider()

    ########## charger le fichier de catégorisation des désordres ##########

    # section sous forme d'onglet
    with st.expander('3 - Fichiers de références'):

        # vérification de l'existence d'un fichier de catégorie de désordre
        if os.path.exists(rf.rep_int("data")+"/url_references.json") :
            # affichage de la date
            st.caption("url des références : Mis à jour la dernière fois le "+rf.date_fichier(rf.rep_int("data")+"/categorie_desordre.json"))
        else :
            st.caption("Fichier de référence : Aucun fichier")
        # vérification de l'existence d'un fichier de catégorie de désordre
        if os.path.exists(rf.rep_int("data")+"/categorie_desordre.json") :
            # affichage de la date
            st.caption("Fichier de catégorie : Mis à jour la dernière fois le "+rf.date_fichier(rf.rep_int("data")+"/categorie_desordre.json"))
        else :
            st.caption("Fichier de catégorie : Aucun fichier")

        # vérification de l'existence de données sur l'url des désordres
        if os.path.exists(rf.rep_int("data")+"/url_references.json") :
            # s'il existe, on le charge
            with open(rf.rep_int("data")+"/url_references.json", "r", encoding="utf-8") as file:
                st.session_state["url_references.json"] = json.load(file)
        # zone de texte pour la mise à jour du session state si besoin
        st.session_state["url_references"] = st.text_input("URL des références du SIRS :", st.session_state["url_references.json"], key="txt_url_references_area")
        cola, colb = st.columns(2)
        with cola:
            # bouton pour mettre à jour l'url
            if st.button("Mettre à jour l'URL", key="but_update_url_references"):
                rf.enregistrer_element_session_state("url_references", rf.rep_int("data") + "/url_references.json")
        with colb:
            # bouton pour télécharger les fichiers de références
            if st.button("Télécharger les fichiers de références", key="but_download_references"):
                # ref désordres
                type_desordre=pd.read_csv(st.session_state["url_references"]+"RefTypeDesordre.csv",encoding = "utf-8")
                type_desordre["champ_joint"] =type_desordre["categorieId"].astype(str).str[-1].astype(int)
                st.session_state["categorie_desordre"] = pd.merge(type_desordre, pd.read_csv(st.session_state["url_references"]+"RefCategorieDesordre.csv",encoding = "utf-8"), left_on = ['champ_joint'], right_on = ['id'])
                rf.enregistrer_element_session_state("categorie_desordre",rf.rep_int("data")+"\\categorie_desordre.json")
                # ref suite à donner
                st.session_state["suite_desordre"] = pd.read_csv(st.session_state["url_references"]+"RefSuiteApporter.csv",encoding = "utf-8")
                rf.enregistrer_element_session_state("suite_desordre",rf.rep_int("data")+"\\suite_desordre.json")
                # ref urgences
                st.session_state["desordre_urgence"] = pd.read_csv(st.session_state["url_references"]+"RefUrgence.csv",encoding = "utf-8")
                rf.enregistrer_element_session_state("desordre_urgence",rf.rep_int("data")+"\\desordre_urgence.json")
                st.rerun()

    # fin de la section            
    st.divider()

    with st.container():

        # section sous forme d'onglet
        with st.expander("4 - Répertoire des utilisateurs") :

            st.write(" Définir le répertoire où seront stocké toutes les données relatives aux utilisateurs")

            # dernier répertoire connue
            if "repertoire_temp" not in st.session_state :
                st.session_state["repertoire_temp"] = st.session_state["rep_utilisateurs"]
            #bouton pour choisir le repertoire
            if st.button("Sélectionner le répertoire", key="but_use_dossier_rep"):
                # Sélection du répertoire via subprocess
                st.session_state["repertoire_temp"] = subprocess.run(["python", rf.rep_int("application") + "/utils/tk_widget.py"],capture_output=True, text=True, check=True).stdout.strip()
            # Zone de texte pour le répertoire d'enregistrement
            repertoire_finale = st.text_area("Répertoire d'enregistrement :",st.session_state["repertoire_temp"],key="txt_rep_util_rep")
            # bouton pour déclencher l'enregistrement du répertoire
            if st.button("Enregistrer le répertoire", key="but_enreg_dossier_rep"):
                # vérification de l'invalidité du répertoire
                if repertoire_finale == "" or not os.path.exists(repertoire_finale):
                    st.error("Répertoire non renseigné ou inexistant")
                else :
                    # enregistrement du répertoire dans le session state
                    st.session_state["rep_utilisateurs"] = repertoire_finale
                    # enregistrement du fichier json mis à jour
                    rf.enregistrer_element_session_state("rep_utilisateurs", rf.rep_int("data") + "/rep_utilisateurs.json")
                    # boucle sur les utilisateurs pour mettre à jour
                    for utilisateur in st.session_state["utilisateurs"] :
                        # mise à jour du session state utilisateurs
                        st.session_state["utilisateurs"][utilisateur][0] = repertoire_finale+"/"+utilisateur
                        # enregistrement du session state utilisateurs
                        rf.enregistrer_element_session_state("utilisateurs", rf.rep_int("data") + "/utilisateurs.json")
                        # création du répertoire utilisateur s'il n'existe pas
                        if not os.path.exists(repertoire_finale + "/" + utilisateur):
                            # création du dossier
                            os.mkdir(repertoire_finale + "/" + utilisateur)
                            st.success("Répertoire créé pour l'utilisateur : " + utilisateur)
                        else:
                            st.warning("Le répertoire existe déjà pour l'utilisateur : " + utilisateur)
                        # création d'une vue par défaut dans le répertoire si elle n'existe pas
                        if not os.path.exists(repertoire_finale + "/" + utilisateur + "/vue_defaut"):
                            os.mkdir(repertoire_finale + "/" + utilisateur + "/vue_defaut")
                    st.rerun()
                            

    # fin de la section            
    st.divider()

    with st.container():

        with st.expander('5 - Créer/supprimer un utilisateur'):
            cola,colc, colb = st.columns([3,1,3])
            # création d'un utilisateur
            with cola :
                # champ pour le nom de l'utilisateur
                nom_utilisateur = st.text_input("Nom :",key="txt_nom_utilisateur")
                type_utilisateur = st.selectbox("Type :",["Normal","Administrateur"],key="sel_type_utilisateur")
                # bouton créer utilisateur
                if st.button("Créer un utilisateur", key="but_creer_utilisateur_rep"):
                    # si le nom est renseigné, on l'ajoute au dictionnaire des utilisateurs
                    # si un repertoire utilisateurs existe on l'utilise, sinon met aucun
                    if nom_utilisateur != "" and nom_utilisateur not in st.session_state["utilisateurs"]:
                        if "rep_utilisateurs" in st.session_state :
                            repertoire_utilisateur = st.session_state["rep_utilisateurs"] + "/" + nom_utilisateur
                        else :
                            repertoire_utilisateur = "aucun"
                        # mise à jour du session state
                        st.session_state["utilisateurs"] = dict({nom_utilisateur : [repertoire_utilisateur,type_utilisateur]},**st.session_state["utilisateurs"])
                        # enregistrement du fichier json mis à jour
                        rf.enregistrer_element_session_state("utilisateurs",rf.rep_int("data")+"/utilisateurs.json")
                        # création du répertoire utilisateur s'il n'existe pas
                        if not os.path.exists(st.session_state["rep_utilisateurs"] + "/" + nom_utilisateur):
                            # création du dossier
                            os.mkdir(st.session_state["rep_utilisateurs"] + "/" + nom_utilisateur)
                            st.success("Répertoire créé pour l'utilisateur : " + nom_utilisateur)
                        else:
                            st.warning("Le répertoire existe déjà pour l'utilisateur : " + nom_utilisateur)
                        # création d'une vue par défaut dans le répertoire si elle n'existe pas
                        if not os.path.exists(st.session_state["rep_utilisateurs"] + "/" + nom_utilisateur + "/vue_defaut"):
                            os.mkdir(st.session_state["rep_utilisateurs"] + "/" + nom_utilisateur + "/vue_defaut")

                            # création de données par défaut en fonction de ce qui existe déjà dans le dossier utilisateurs
                            vue_dict_ref = {}
                            vue_dict_desordres = {}
                            for user in os.listdir(st.session_state["rep_utilisateurs"]):
                                st.write(user)
                                # examine l'élément traité pour voir s'il s'agit d'un dossier
                                if os.path.isdir(os.path.join(st.session_state["rep_utilisateurs"], user)) and user in list(st.session_state["utilisateurs"]):
                                    # examiner si un des dossiers de vues de l'utilisateurs dispose d'un fichier ref_systeme.json
                                    for object in os.listdir(st.session_state["utilisateurs"][user][0]):
                                        st.write(object)
                                        # examiner le fichier de reference des systèmes 
                                        if os.path.isdir(os.path.join(st.session_state["utilisateurs"][user][0], object)) and "ref_systeme.json" in os.listdir(os.path.join(st.session_state["utilisateurs"][user][0], object)):
                                            # on recupere le nom de la vue et la date de creation du fichier ref
                                            vue_dict_ref[object] = rf.date_fichier((st.session_state["utilisateurs"][user][0]+"/"+object+"/ref_systeme.json"))
                                        # examiner les fichier thematique
                                        if os.path.isdir(os.path.join(st.session_state["utilisateurs"][user][0], object)) and "desordres.json" in os.listdir(os.path.join(st.session_state["utilisateurs"][user][0], object)):
                                            # on recupere le nom de la vue et la date de creation du fichier desordres
                                            vue_dict_desordres[object] = rf.date_fichier((st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+object+"/desordres.json"))
                                # création du répertoire de la nouvelle vue
                            if vue_dict_ref != {} :
                                # on récupère la vue la plus récente
                                vue_récente = max(vue_dict_ref, key=vue_dict_ref.get)
                                # création du fichier de référence dans le répertoire de la vue
                                shutil.copyfile(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+vue_récente+"/ref_systeme.json", st.session_state["rep_utilisateurs"]+"/"+nom_utilisateur+"/vue_defaut/ref_systeme.json")                        
                            if vue_dict_desordres != {} :
                                # on récupère la vue la plus récente
                                vue_récente_desordres = max(vue_dict_desordres, key=vue_dict_desordres.get)
                                # création du fichier desordres dans le répertoire de la vue
                                shutil.copyfile(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+vue_récente_desordres+"/desordres.json", st.session_state["rep_utilisateurs"]+"/"+nom_utilisateur+"/vue_defaut/desordres.json")

                        st.success("Utilisateur créé : "+nom_utilisateur)
                    # cas de figure de nom utilisateur incorrect
                    else :
                        st.error("Nom d'utilisateur déjà existant ou non renseigné")
                    st.rerun()
            # suppression d'un utilisateur
            with colb:
                # champ pour le nom de l'utilisateur
                nom_utilisateur_suppr = st.selectbox("Utilisateur à supprimer :", list(st.session_state["utilisateurs"].keys()), key="sel_utilisateur_suppr_rep")
                rep_suppr = st.toggle("Supprimer le répertoire de l'utilisateur", value=True,key="tog_suppr_rep")
                # bouton supprimer utilisateur
                if st.button("Supprimer un utilisateur", key="but_supprimer_utilisateur_rep"):
                    # si le nom est renseigné, on l'ajoute au dictionnaire des utilisateurs
                    if nom_utilisateur_suppr != "" and nom_utilisateur_suppr in st.session_state["utilisateurs"]:
                        # mise à jour du session state
                        del st.session_state["utilisateurs"][nom_utilisateur_suppr]
                        # enregistrement du fichier json mis à jour
                        rf.enregistrer_element_session_state("utilisateurs",rf.rep_int("data")+"/utilisateurs.json")
                        st.success("Utilisateur supprimé : "+nom_utilisateur_suppr)
                    # si le répertoire doit être supprimé
                    if rep_suppr :
                        # suppression du répertoire utilisateur
                        if os.path.exists(st.session_state["rep_utilisateurs"] + "/" + nom_utilisateur_suppr):
                            # suppression du dossier
                            shutil.rmtree(st.session_state["rep_utilisateurs"] + "/" + nom_utilisateur_suppr)
                            st.success("Répertoire supprimé pour l'utilisateur : " + nom_utilisateur_suppr)
                        else:
                            st.warning("Le répertoire n'existe pas pour l'utilisateur : " + nom_utilisateur_suppr)
                    else :
                        st.error("Nom d'utilisateur non existant ou non renseigné")
                    st.rerun()





