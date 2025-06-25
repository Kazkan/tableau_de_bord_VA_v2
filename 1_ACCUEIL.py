###############################################
# Gabriel NAVENNEC - 06/05/2025               #
# SYMBHI - FRANCE DIGUE - IUGA                #
#                                             #
# Version 1.0                                 #
###############################################

# import de streamlit
import streamlit as st
import os
import utils.read_files as rf
import utils.st_widget as sw
import pandas as pd
import json
import utils.sidebar as sb

########## initialisation des session states ###########

# vérification de l'existence d'un fichier utilisateur dans les données internes
if os.path.exists(rf.rep_int("utilisateurs")) :
    # s'il existe, on le charge
    with open(rf.rep_int("utilisateurs") , "r", encoding="utf-8") as file:
        st.session_state["utilisateurs"] = json.load(file)

# vérification de l'existence d'un fichier utilisateur dans les données internes
if os.path.exists(rf.rep_int("rep_utilisateurs")) :
    # s'il existe, on le charge
    with open(rf.rep_int("rep_utilisateurs") , "r", encoding="utf-8") as file:
        st.session_state["rep_utilisateurs"] = json.load(file)

# vérification de l'existence de données sur les désordres
if os.path.exists(rf.rep_int("cat_desordre")) :
    # s'il existe, on le charge
    st.session_state["categorie_desordre"] = pd.read_json(rf.rep_int("cat_desordre"))
    # affichage de la date

# vérification de l'existence de données sur les désordres
if os.path.exists(rf.rep_int("suite_desordre")) :
# s'il existe, on le charge
    st.session_state["suite_desordre"] = table_suite = pd.read_json(rf.rep_int("suite_desordre"))

if os.path.exists(rf.rep_int("code_urgence")) :
    # s'il existe, on le charge
    st.session_state["desordre_urgence"] = pd.read_json(rf.rep_int("code_urgence"))

########## chargement du paramétrage de d'utilisateur courant et vue courante ##########

# fonction de la barre latéral
sb.sidebar_content()

cola, colb, colc = st.columns([3,1,1])
with cola :
    st.title ("Tableau de bord des données SIRS Digues")
    st.text("Bienvenue dans le tableau de bord des données SIRS !")
    st.text("Utilisez le pour explorer vos données thématiques et réer votre tableau de bord personnalisé")
with colb:
    # affichage de l'image SYMBHI
    st.image(rf.rep_int("images")+"/logo_France_Digues.jfif",width=250)
with colc:
    # affichage de l'image SYMBHI
    st.image(rf.rep_int("images")+"/Logo_SYMBHI.png",width=180)
st.divider()
subheader = st.subheader("Comment utiliser l'application ?")
st.write("1 - Vous pouvez utiliser le menu latéral pour sélectionner votre compte utilisateur.")
st.write("2 - Vous pouvez également vous servir du menu latéral pour choisir/créer une ""vue"" pour sauvegarder à l'intérieur les fichier de données, les paramètres associées et votre tableau de bord personnalisé.")
st.write("3 - Pour chaque nouvelle ""vue"" créée, veillez à bien importer les données de référence nécessaires au bon fonctionnement de l'application. Vous pouvez le faire dans la section \"Chargement/mise à jour des données de référence\" un peu plus bas. Par défaut, les fichiers de tronçon et de thématiques les plus récents de votre dossier utilisateur seront chargés")
st.write("4 - Il est possible de consulter les données thématiques des systèmes d'endiquements relatives aux désordres, aux prestations et aux réseaux dans les pages correspondantes. Les figures générés peuvent alors être ajoutées au tableau de bord de votre vue avec les boutons :star:.")
st.write("5 - Vous pouvez gérer la présence et la position des figure de votre tableau de bord dans l'onglet :gear: de la page tableau de bord.")
st.write("6 - La page des paramètres généraux est accesible uniquement pour les profils utilisateurs disposants des droits d'administrateurs. Elle permet de gérer les utilisateurs et leurs données de référence de façon global.")

# fin de la section            
st.divider()

st.subheader("Chargement/mise à jour des données de référence")

########## V2 : charger le fichier de référence des sytemes d'endiguement ##########

# controle du repertoire de l'utilisateur courant
if st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0] == "" or st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0] == "aucun" :
    st.warning("Aucun répertoire utilisateur n'est défini. Veuillez en créer un dans la page des paramètres généraux.")

else :

    # avertissement de l'existence et de la date du dernier fichier de mise à jour
    # vérification de l'existence d'un fichier de systemes d'endiguement dans les données internes
    if os.path.exists(rf.rep_int("systeme")) :
        # affichage de la date
        st.caption("Fichier de référence : Mis à jour la dernière fois le "+rf.date_fichier(rf.rep_int("systeme")))
    else :
        st.caption("Fichier de référence : Aucun fichier")

    # section sous forme d'onglet
    with st.expander("1 - fichier des systèmes d'endiguements"):

        st.text("Le fichier des systèmes d'endiguements est une table contenant les correspondances entre les systèmes d'endiguement, les digues et les tronçons. Il est nécessaire pour le bon fonctionnement de l'application.")
        st.markdown("*Il est possible d'enregistrer le fichier uniquement pour la ""vue"", ou pour l'ensemble des ""vues"" enregistrées dans votre compte utilisateurs.*")
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
            # bouton pour déclencher le chargement du fichier de référence
            charg_ref = st.toggle("Charger dans le tableau de bord", value=False,key="but_charg_ref")
            if charg_ref :
                # prévisualisation des données
                st.write("Prévisualisation :")
                st.dataframe(rf.ref_to_df(uploaded_file, separateur, systeme, digue, troncon))
                #  si chargement, prévisualisation et bouton pour déclencher la sauvegarde du fichier de référence
                cola,colb = st.columns(2)
                with cola :
                    # bouton de sauvegarde
                        # bouton pour déclencher la sauvegarde du fichier de référence
                    sauv_ref = st.button('Sauvegarder dans la vue',key="but_sauv_ref")
                    if sauv_ref :
                        # enregistrement des références
                        st.session_state["ref_systeme"] = rf.ref_to_df(uploaded_file, separateur, systeme, digue, troncon)
                        rf.enregistrer_element_session_state("ref_systeme",rf.rep_int("systeme"))
                        # suppression de la sessions state pour éviter les doublons avec le json
                        del st.session_state["ref_systeme"]
                        st.rerun()
                with colb : 
                    # bouton de sauvegarde
                        # bouton pour déclencher la sauvegarde du fichier de référence
                    sauv_ref = st.button("Sauvegarder pour l'utilisateur",key="but_sauv_ref_user")
                    if sauv_ref :
                        # enregistrement des références
                        st.session_state["ref_systeme"] = rf.ref_to_df(uploaded_file, separateur, systeme, digue, troncon)
                        for vue in os.listdir(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]) :
                            rf.enregistrer_element_session_state("ref_systeme",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+vue+"/ref_systeme.json")
                        # suppression de la sessions state pour éviter les doublons avec le json
                        del st.session_state["ref_systeme"]
                        st.rerun()


    ########## charger le fichier des thématiques des sytemes d'endiguement ##########
    ###### V2 - chargement dans le répertoire utilisateurs
    # vérification de l'existence des fichiers des thématiques dans les données internes
    st.caption("Fichiers thématiques chargées :")
    if os.path.exists(rf.rep_int("desordres")) :
        st.caption("Desordres" + " : "+rf.date_fichier(rf.rep_int("desordres")))
    elif os.path.exists(rf.rep_int("prestations")) :
        st.caption("Prestations :" + " : "+rf.date_fichier(rf.rep_int("prestations")))
    elif os.path.exists(rf.rep_int("reseaux")) :
        st.caption("Reseaux :" + " : "+rf.date_fichier(rf.rep_int("reseaux")))
    else :
        st.caption("Aucun fichier")

    # section sous forme d'onglet
    with st.expander('2 - fichiers des thématiques'):

        # indications sur la méthode pour générer les tables thématiques
        st.text('Les tables thématiques sont issues des extractions du plugin QGIS "couchDB importer" enregistré en .csv')
        st.text("pour chaque thématique, il est possible d'importer à la fois les données ponctuels et les données linéaires.")
        st.markdown("*Il est possible d'enregistrer les fichier uniquement pour la ""vue"", ou pour l'ensemble des ""vues"" enregistrées dans votre compte utilisateurs.*")

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
                    # bouton de sauvegarde et liste des vue pour l'enregistrement
                    vues = st.multiselect("Vues ciblés :",os.listdir(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]),default=[st.session_state["vue_courante"]], key="but_vues_desordre_select_save")
                    sauv_desordre = st.button('Sauvegarder',key="but_sauv_desordre")
                    # enregistrement des références
                    st.session_state["them_desordre"] = df_desordre_total
                    if sauv_desordre :
                        for vue in vues :
                            rf.enregistrer_element_session_state("them_desordre",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+vue+"/desordres.json")
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
                    # bouton de sauvegarde et liste des vue pour l'enregistrement
                    vues = st.multiselect("Vues ciblés :",os.listdir(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]),default=[st.session_state["vue_courante"]], key="but_vues_prestation_select_save")
                    sauv_prestation = st.button('Sauvegarder',key="but_sauv_prestation")
                    # enregistrement des références
                    st.session_state["them_prestation"] = df_prestation_total
                    if sauv_prestation :
                        for vue in vues :
                            rf.enregistrer_element_session_state("them_prestation",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+vue+"/prestations.json")
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
                    # bouton de sauvegarde et liste des vue pour l'enregistrement
                    vues = st.multiselect("Vues ciblés :",os.listdir(st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]),default=[st.session_state["vue_courante"]], key="but_vues_reseau_select_save")
                    sauv_reseau = st.button('Sauvegarder',key="but_sauv_reseau")
                    # enregistrement des références
                    st.session_state["them_reseau"] = df_reseau_total
                    if sauv_reseau :
                        for vue in vues :
                            rf.enregistrer_element_session_state("them_reseau",st.session_state["utilisateurs"][st.session_state["utilisateur_courant"]][0]+"/"+vue+"/reseaux.json")
                        # suppression de la sessions state pour éviter les doublons avec le json
                        del st.session_state["them_reseau"]
                        st.rerun()

    # fin de la section
    st.divider()







