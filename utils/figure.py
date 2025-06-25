import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

########### figure de visualisation des désordres sous forme linéaire 1D ##########
def figure_lin(table: pd.DataFrame, table_cat: pd.DataFrame, table_suite : pd.DataFrame, etiquettes : st.session_state, infos : st.session_state, discretisation : st.session_state, troncon : st.session_state):
    # Filtrer la table par tronçon
    table = table[table['Tronçon'] == troncon]
    # Fonction pour appliquer les règles de filtrage
    def filtrer_pr(groupe):
        pr_unique = groupe['PR_borne'].unique()
        # Règle 1 : Si au moins deux valeurs de PR sont identiques, on garde cette valeur
        if len(pr_unique) < len(groupe):
            return pr_unique[0]
        # Règle 2 : Si la différence entre au moins deux PR est inférieure à 5 m, on garde la moyenne des PR
        if any(abs(pr_unique[i] - pr_unique[j]) < 5 for i in range(len(pr_unique)) for j in range(i + 1, len(pr_unique))):
            return np.mean(groupe['PR_borne'])
        # Règle 3 : S'il n'y a qu'une seule valeur de PR pour cette borne, on garde cette valeur unique
        return pr_unique[0]
    
    if discretisation == "type":
        discretisation = "code_desordre"
    elif discretisation == "categorie":
        discretisation = "code_categorie"
    elif discretisation == "suite":
        discretisation = "code_suite"

    mapping_urgence = {
        'Faible urgence': 'Code 0',
        'Pas de grande urgence': 'Code 1',
        'Désordre devant être traité à court ou moyen terme': 'Code 2',
        'Désordre devant être traité de façon urgente': 'Code 3'
    }
    table['code_urgence'] = table.iloc[:, 79].map(mapping_urgence)

    mapping_categorie = dict(zip(table_cat['libelle_x'], table_cat['abrege_y']))
    mapping_codedes = dict(zip(table_cat['libelle_x'], table_cat['abrege_x']))
    mapping_suite = dict(zip(table_suite['libelle'], table_suite['abrege']))

    table['code_categorie'] = table.iloc[:, 35].map(mapping_categorie)
    table['code_desordre'] = table.iloc[:, 35].map(mapping_codedes)
    table['code_suite'] = table.iloc[:, 78].map(mapping_suite)

    table["PR de début"] = pd.to_numeric(table["PR de début"])
    table["Distance (borne début)"] = pd.to_numeric(table["Distance (borne début)"])

    table['PR_borne'] = [i - j if k == 'Aval' else i + j for i, j, k in zip(table.iloc[:, 7], table.iloc[:, 5], table.iloc[:, 4])]
    df_bornes = pd.DataFrame({'Borne': table.iloc[:, 3], 'PR_borne': table['PR_borne']})
    df_bornes = df_bornes.sort_values(by=['Borne', 'PR_borne']).reset_index(drop=True)

    df_bornes_filtered = df_bornes.groupby('Borne', as_index=False).apply(lambda grp: pd.Series({'PR_borne': filtrer_pr(grp)}))
    df_bornes_filtered = df_bornes_filtered.sort_values(by=['Borne', 'PR_borne']).reset_index(drop=True)
    df_bornes_filtered.rename(columns={'PR_borne': 'PR_filtered'}, inplace=True)

    table2 = table.merge(df_bornes_filtered, left_on=table.iloc[:, 3].name, right_on='Borne', how='left')
    table2['PR_borne'] = table2['PR_filtered']
    table2.drop(columns=['PR_filtered', 'Borne'], inplace=True)

    xlim = []

    if xlim:
        table2 = table2[(table2.iloc[:, 7] >= xlim[0]) & (table2.iloc[:, 13] <= xlim[1])]

    unique_codes_desordre = table2[discretisation].unique() 
    couleurs_plotly = px.colors.qualitative.Plotly
    couleurs = {code: couleurs_plotly[i % len(couleurs_plotly)] for i, code in enumerate(unique_codes_desordre)}

    vpos = {'Code 0': 0.05, 'Code 1': 0.15, 'Code 2': 0.25, 'Code 3': 0.35}
    fig = go.Figure()

    for _, row in table2.iterrows():
        amont = row.iloc[7]
        aval = float(row.iloc[13])
        code_urgence = row['code_urgence']
        code_desordre = row[discretisation]
        designation = row.iloc[18]
        couleur = couleurs[code_desordre]
        y = vpos.get(code_urgence, 0.05)
        # créer les etiquettes pour la fonction text
        text_etiquettes =""
        for etiquette in etiquettes:
            text_etiquettes = text_etiquettes+"<br>"+str(row[etiquette])
        # créer les infobulles 
        text_infos = ""
        for info in infos:
            text_infos = text_infos+"<br>"+str(row[info])

        if abs(amont - aval) < 20:
            fig.add_trace(go.Scatter(
                x=[(amont + aval) / 2],
                y=[y],
                mode='markers',
                marker=dict(color=couleur, size=8),
                hovertext=text_infos,
                hoverinfo='text',
                name=code_desordre,
                legendgroup=code_desordre,
                showlegend=True if not fig.data or code_desordre not in [trace.name for trace in fig.data] else False
            ))
            fig.add_annotation(
                x=(amont + aval) / 2,
                y=y,
                text=text_etiquettes,
                textangle=270, 
                showarrow=False,
                font=dict(size=12),
                xanchor="center",
                yanchor="bottom"
            )

        else:
            fig.add_trace(go.Scatter(
                x=[amont, aval],
                y=[y, y],
                mode='lines',
                line=dict(color=couleur, width=3),
                hovertext=text_infos,
                hoverinfo='text',
                name=code_desordre,
                legendgroup=code_desordre,
                showlegend=True if not fig.data or code_desordre not in [trace.name for trace in fig.data] else False
            ))
            fig.add_annotation(
                x=(amont + aval) / 2,
                y=y,
                text=text_etiquettes,
                textangle=270,  
                showarrow=False,
                font=dict(size=12),
                xanchor="center",
                yanchor="bottom"
            )

    for _, row in df_bornes_filtered.iterrows():
        fig.add_vline(x=row['PR_filtered'], line=dict(color='black', width=0.5, dash='dash'))
        fig.add_annotation(x=row['PR_filtered'], y=0.02, text=row['Borne'], showarrow=False, textangle=0, align="center", bgcolor="rgba(255,255,255,0.8)", borderpad=4)

    fig.update_layout(
        height=500,
        width=1200,
        xaxis_title="Position le long de l'axe PR (m)",
        yaxis=dict(
            tickvals=list(vpos.values()),
            ticktext=list(vpos.keys()),
            title="Code urgence",
            range=[-0.05, 0.45]
        ),
        showlegend=True
    )

    return fig

def plot_archive(table : pd.DataFrame, etiquettes : st.session_state, groupement : st.session_state, discretisation : st.session_state) :
    # création d'un champ archivage qui se rempli en fonction de la présence d'une donné dans le champ date de fin
    table['archivage'] = np.select([(table['Date de fin'].isnull())], ["non archivé"], default="archivé" )

    # groupement des entités par statut d'archivage et par urgence (pour avoir la somme dans plotly), il s'agit d'un format spécial à plotly)
    # changement figure selon parametre 
    crit_group = ["archivage"]
    hov=[]
    col="archivage"
    if discretisation == "urgence" :
        # joiture avec la table des abréviations
        table = table.merge(st.session_state["desordre_urgence"], left_on="Observation Urgence", right_on="libelle", how="left")
        # remplacer les valeurs manquantes par "non renseigné"
        table['abrege'] = table['abrege'].fillna("non renseigné")
        crit_group.append("abrege")
        crit_group.append("Observation Urgence")
        hov.append("Observation Urgence")
        col="abrege"
    elif discretisation == "categorie" :
        # joiture avec la table des abréviations
        table = table.merge(st.session_state["categorie_desordre"], left_on="Type de désordre", right_on="libelle_x", how="left")
        # remplacer les valeurs manquantes par "non renseigné"
        table['abrege_y'] = table['abrege_y'].fillna("non renseigné")
        crit_group.append("abrege_y")
        crit_group.append("Catégorie de désordre")
        hov.append("Catégorie de désordre")
        col="abrege_y"
    elif discretisation == "type" :
        # joiture avec la table des abréviations
        table = table.merge(st.session_state["categorie_desordre"], left_on="Type de désordre", right_on="libelle_x", how="left")
        # remplacer les valeurs manquantes par "non renseigné"
        table['abrege_x'] = table['abrege_x'].fillna("non renseigné")
        crit_group.append("abrege_x")
        crit_group.append("Type de désordre")
        hov.append("Type de désordre")
        col="abrege_x"
    elif discretisation == "suite" :
        # joiture avec la table des abréviations
        table = table.merge(st.session_state["suite_desordre"], left_on="Observation Suite à apporter", right_on="libelle", how="left")
        # remplacer les valeurs manquantes par "non renseigné"
        table['abrege'] = table['abrege'].fillna("non renseigné")
        crit_group.append("abrege")
        crit_group.append("Observation Suite à apporter")
        hov.append("Observation Suite à apporter")
        col="abrege"
    else :
        hov.append("archivage")
    if groupement != "aucun" :
        crit_group.append(groupement)
        hov.append(groupement)
    table = table.groupby(crit_group)["Observation Nb désordres"].count().reset_index()
    # gestion des etiquettes
    if etiquettes == "thématique" and discretisation != "aucun" :
        etiquettes = col
    elif etiquettes == 'groupe' and groupement != "aucun" :
        etiquettes = groupement
    else :
        etiquettes = None
    # création du graph permettant de visualiser les desordres archiver selon le code durgence
    fig = px.bar(table, x="archivage", y="Observation Nb désordres",hover_data=hov,text=etiquettes, color=col, labels={col: hov[0]})
    return fig

def plot_temporel(table : pd.DataFrame,frequence,date,groupe,discretisation,etiquettes) :
    # groupement des entités par année d'enregistrement et par urgence (pour avoir la somme dans plotly), il s'agit d'un format spécial à plotly)
    # changement figure selon parametre 
    # paramétrage de la fréquence pour le champ de regroupement
    if frequence == "annee" :
        table[date] = table[date].astype(str).str[:4]
    elif frequence == "mois" :
        table[date] = table[date].astype(str).str[:7]
    # gestion des discrétisations et regroupement
    crit_group = [date]
    hov=[date]
    col=date
    if discretisation == "urgence" :
        # joiture avec la table des abréviations
        table = table.merge(st.session_state["desordre_urgence"], left_on="Observation Urgence", right_on="libelle", how="left")
        # remplacer les valeurs manquantes par "non renseigné"
        table['abrege'] = table['abrege'].fillna("non renseigné")
        crit_group.append("abrege")
        crit_group.append("Observation Urgence")
        hov.append("Observation Urgence")
        col = "abrege"
    elif discretisation == "categorie" :
        # joiture avec la table des abréviations
        table = table.merge(st.session_state["categorie_desordre"], left_on="Type de désordre", right_on="libelle_x", how="left")
        # remplacer les valeurs manquantes par "non renseigné"
        table['abrege_y'] = table['abrege_y'].fillna("non renseigné")
        crit_group.append("abrege_y")
        crit_group.append("Catégorie de désordre")
        hov.append("Catégorie de désordre")
        col = "abrege_y"
    elif discretisation == "type" :
        # joiture avec la table des abréviations
        table = table.merge(st.session_state["categorie_desordre"], left_on="Type de désordre", right_on="libelle_x", how="left")
        # remplacer les valeurs manquantes par "non renseigné"
        table['abrege_x'] = table['abrege_x'].fillna("non renseigné")
        crit_group.append("abrege_x")
        crit_group.append("Type de désordre")
        hov.append("Type de désordre")
        col = "abrege_x"
    elif discretisation == "suite" :
        # joiture avec la table des abréviations
        table = table.merge(st.session_state["suite_desordre"], left_on="Observation Suite à apporter", right_on="libelle", how="left")
        # remplacer les valeurs manquantes par "non renseigné"
        table['abrege'] = table['abrege'].fillna("non renseigné")
        crit_group.append("abrege")
        crit_group.append("Observation Suite à apporter")
        hov.append("Observation Suite à apporter")
        col = "abrege"
    elif discretisation == "archivage" :  
        # création d'un champ archivage qui se rempli en fonction de la présence d'une donné dans le champ date de fin
        table['archivage'] = np.select([(table['Date de fin'].isnull())], ["non archivé"], default="archivé" )  
        crit_group.append("archivage")
        hov.append("archivage")
        col = "archivage"
    else :
        hov.append(date)
    if groupe != "aucun" :
        crit_group.append(groupe)
        hov.append(groupe)
    table = table.groupby(crit_group)["Observation Nb désordres"].count().reset_index()
        # gestion des etiquettes
    if etiquettes == "thématique" and discretisation != "aucun" :
        etiquettes = col
    elif etiquettes == 'groupe' and groupe != "aucun" :
        etiquettes = groupe
    else :
        etiquettes = None
    # création du graph permettant de visualiser les desordres archiver selon le code durgence
    fig = px.bar(table, x=date, y="Observation Nb désordres",hover_data=hov,text=etiquettes, color=col, labels={col: hov[1]})
    # affichage
    return fig

def plot_cat(table : pd.DataFrame,  etiquettes : st.session_state, groupement : st.session_state, discretisation : st.session_state) :
    # jointure avec la table des abréviations
    table = table.merge(st.session_state["categorie_desordre"], left_on="Type de désordre", right_on="libelle_x", how="left")
    # remplacer les valeurs manquantes par "non renseigné"
    table['abrege_y'] = table['abrege_y'].fillna("non renseigné")
    # renomage de la colonne abrege_y
    table.rename(columns={'abrege_y': 'Catégorie'}, inplace=True) 
    crit_group = ["Catégorie"]
    hov=[]
    col="Catégorie"
    if discretisation == "urgence" :
        # joiture avec la table des abréviations
        table = table.merge(st.session_state["desordre_urgence"], left_on="Observation Urgence", right_on="libelle", how="left")
        # remplacer les valeurs manquantes par "non renseigné"
        table['abrege'] = table['abrege'].fillna("non renseigné")
        crit_group.append("abrege")
        crit_group.append("Observation Urgence")
        hov.append("Observation Urgence")
        col="abrege"
    elif discretisation == "type" :
        # remplacer les valeurs manquantes par "non renseigné"
        table['abrege_x'] = table['abrege_x'].fillna("non renseigné")
        crit_group.append("abrege_x")
        crit_group.append("Type de désordre")
        hov.append("Type de désordre")
        col="abrege_x"
    elif discretisation == "suite" :
        # joiture avec la table des abréviations
        table = table.merge(st.session_state["suite_desordre"], left_on="Observation Suite à apporter", right_on="libelle", how="left")
        # remplacer les valeurs manquantes par "non renseigné"
        table['abrege'] = table['abrege'].fillna("non renseigné")
        crit_group.append("abrege")
        crit_group.append("Observation Suite à apporter")
        hov.append("Observation Suite à apporter")
        col="abrege"
    elif discretisation == "archivage" :  
        # création d'un champ archivage qui se rempli en fonction de la présence d'une donné dans le champ date de fin
        table['archivage'] = np.select([(table['Date de fin'].isnull())], ["non archivé"], default="archivé" )  
        crit_group.append("archivage")
        hov.append("archivage")
        col = "archivage"
    else :
        hov.append("Catégorie")
    if groupement != "aucun" :
        crit_group.append(groupement)
        hov.append(groupement)
    table = table.groupby(crit_group)["Observation Nb désordres"].count().reset_index()
    # gestion des etiquettes
    if etiquettes == "thématique" and discretisation != "aucun" :
        etiquettes = col
    elif etiquettes == 'groupe' and groupement != "aucun" :
        etiquettes = groupement
    else :
        etiquettes = None
    # création du graph permettant de visualiser les desordres archiver selon le code durgence
    fig = px.bar(table, x="Catégorie", y="Observation Nb désordres",hover_data=hov,text=etiquettes, color=col, labels={col: hov[0]})
    return fig

def plot_type(table : pd.DataFrame, etiquettes : st.session_state, groupement : st.session_state, discretisation : st.session_state) :
    # jointure avec la table des abréviations
    table = table.merge(st.session_state["categorie_desordre"], left_on="Type de désordre", right_on="libelle_x", how="left")
    # remplacer les valeurs manquantes par "non renseigné"
    table['abrege_x'] = table['abrege_x'].fillna("non renseigné")
    # renomage de la colonne abrege_x
    table.rename(columns={'abrege_x': 'Type'}, inplace=True)
    crit_group = ["Type"]
    hov=[]
    col="Type"
    if discretisation == "urgence" :
        # joiture avec la table des abréviations
        table = table.merge(st.session_state["desordre_urgence"], left_on="Observation Urgence", right_on="libelle", how="left")
        # remplacer les valeurs manquantes par "non renseigné"
        table['abrege'] = table['abrege'].fillna("non renseigné")
        crit_group.append("abrege")
        crit_group.append("Observation Urgence")
        hov.append("Observation Urgence")
        col="abrege"
    elif discretisation == "categorie" :
        # remplacer les valeurs manquantes par "non renseigné"
        table['abrege_y'] = table['abrege_y'].fillna("non renseigné")
        crit_group.append("abrege_y")
        crit_group.append("Catégorie de désordre")
        hov.append("Catégorie de désordre")
        col="abrege_y"
    elif discretisation == "suite" :
        # joiture avec la table des abréviations
        table = table.merge(st.session_state["suite_desordre"], left_on="Observation Suite à apporter", right_on="libelle", how="left")
        # remplacer les valeurs manquantes par "non renseigné"
        table['abrege'] = table['abrege'].fillna("non renseigné")
        crit_group.append("abrege")
        crit_group.append("Observation Suite à apporter")
        hov.append("Observation Suite à apporter")
        col="abrege"
    elif discretisation == "archivage" :  
        # création d'un champ archivage qui se rempli en fonction de la présence d'une donné dans le champ date de fin
        table['archivage'] = np.select([(table['Date de fin'].isnull())], ["non archivé"], default="archivé" )  
        crit_group.append("archivage")
        hov.append("archivage")
        col = "archivage"
    else :
        hov.append("Type")
    if groupement != "aucun" :
        crit_group.append(groupement)
        hov.append(groupement)
    table = table.groupby(crit_group)["Observation Nb désordres"].count().reset_index()
    # gestion des etiquettes
    if etiquettes == "thématique" and discretisation != "aucun" :
        etiquettes = col
    elif etiquettes == 'groupe' and groupement != "aucun" :
        etiquettes = groupement
    else :
        etiquettes = None
    # création du graph permettant de visualiser les desordres archiver selon le code durgence
    fig = px.bar(table, x="Type", y="Observation Nb désordres",hover_data=hov,text=etiquettes, color=col,labels={col: hov[0]})
    return fig





