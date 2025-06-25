import streamlit as st
import pandas as pd
import geopandas as gpd
import os
from datetime import datetime
import numpy as np

#  import des fonctions de cartographie
import folium
from folium.plugins import MarkerCluster
from folium.plugins import Fullscreen
from streamlit_folium import st_folium
from shapely.wkt import loads
from shapely.geometry import Point, LineString


def map_desordres(table : pd.DataFrame, etiquettes : st.session_state, popup : st.session_state, discretisation : st.session_state, cle : int) :

    # Transformer les LineString avec deux points identiques en Point
    def corriger_linestrings(geometrie):
        if isinstance(geometrie, LineString):
            coords = list(geometrie.coords)
            if len(coords) == 2 and coords[0] == coords[1]:
                return Point(coords[0])
        return geometrie
    
    # transformation des données en geodataframe
    gdf = gpd.GeoDataFrame(table,geometry=table['Géométrie'].apply(loads),crs="EPSG:2154").to_crs(epsg=4326)

    # conversion des champs date en str
    gdf['Date de début'] = gdf['Date de début'].astype(str)
    gdf['Date de fin'] = gdf['Date de fin'].astype(str)

    # corriger géométries dégénérées
    gdf['geometry'] = gdf.geometry.apply(corriger_linestrings)

    # Séparer les points et les autres géométries
    gdf_point = gdf[gdf.geometry.geom_type == "Point"]
    gdf_ligne = gdf[gdf.geometry.geom_type != "Point"]

    # afficher les données sur la carte
    m = folium.Map(control_scale=True)

    ########## définitions des entités ##########
    # ajouter les points à la carte
    if not gdf_point.empty:
        points_group = folium.FeatureGroup(name="Désordres ponctuels", show=True)
        for _, row in gdf_point.iterrows():
            # définition de la couleur des entités
            color = "blue" # couleur par défaut
            ###### condition de l'activation de la vue par urgence
            if discretisation == "urgence" :
                if row["Observation Urgence"] == "Faible urgence":
                    color = "LawnGreen"
                elif row["Observation Urgence"] == "Pas de grande urgence":
                    color = "GoldenRod"
                elif row["Observation Urgence"] == "Désordre devant être traité à court ou moyen terme":
                    color = "DarkOrange"
                elif row["Observation Urgence"] == "Désordre devant être traité de façon urgente":
                    color = "Crimson"
                elif row["Observation Urgence"] == "Indéfini":
                    color = "DarkGrey"
                else :
                    color = "Black"
            ###### condition de l'activation de la vue par categorie
            elif discretisation == "categorie" :
                if row["Catégorie de désordre"] == "Érosion externe":
                    color = "chocolate"
                elif row["Catégorie de désordre"] == "Érosion interne":
                    color = "blue"
                elif row["Catégorie de désordre"] == "Désordre affectant la structure":
                    color = "DarkOrange"
                elif row["Catégorie de désordre"] == "Brèche":
                    color = "Crimson"
                elif row["Catégorie de désordre"] == "Conditions d'entretien de la digue, détérioration des équipements, activités illégales, gêne à la gestion":
                    color = "GoldenRod"
                elif row["Catégorie de désordre"] == "Défaut sur dispositif de protection":
                    color = "purple"
                elif row["Catégorie de désordre"] == "Autre":
                    color = "DarkGrey"
                else :
                    color = "Black"
            ###### condition de l'activation de la vue par suite à donner
            elif discretisation == "suite" :
                if row["Observation Suite à apporter"] == "Aucune":
                    color = "DarkGrey"
                elif row["Observation Suite à apporter"] == "Surveillance":
                    color = "green"
                elif row["Observation Suite à apporter"] == "Entretien":
                    color = "DarkOrange"
                elif row["Observation Suite à apporter"] == "Etudes":
                    color = "Blue"
                elif row["Observation Suite à apporter"] == "Travaux":
                    color = "chocolate"
                elif row["Observation Suite à apporter"] == "Archivé":
                    color = "GoldenRod"
                elif row["Observation Suite à apporter"] == "Prioritaire":
                    color = "Crimson"
                elif row["Observation Suite à apporter"] == "Constat":
                    color = "purple"
                else :
                    color = "Black"
            # création de la géométrie du symbole
            folium.Marker(
                location=[row.geometry.y, row.geometry.x],
                icon=folium.DivIcon(html=f"""
                                    <div>
                                    <svg width="10" height="10" viewBox="0 0 40 40">
                                        <polygon points="25,0 00,60 60,60" fill="white" />
                                        <polygon points="25,10 10,50 50,50" fill="{color}"/>
                                    </svg>
                                    </div>"""),
                opacity=0.8,
                tooltip = folium.Tooltip("<br>".join(f"{col}: {row[col]}" for col in popup)),
            ).add_to(points_group)
            # création du contenu des etiquettes
            html_label = f"""<div style="font-size: 12px; color: {color}; white-space: nowrap;text-shadow:-1px -1px 0 white,1px -1px 0 white,-1px 1px 0 white,1px 1px 0 white;">"""
            for etiquette in etiquettes :
                if str(row[etiquette]) != "nan" :
                    html_label = html_label+"<BR>"+str(row[etiquette])
            html_label = html_label+"</div>"
            # ajout des etiquettes
            folium.Marker(
                location=[row.geometry.y, row.geometry.x],
                tooltip = folium.Tooltip("<br>".join(f"{col}: {row[col]}" for col in popup)),
                icon=folium.DivIcon(
                    html=html_label
                    )
                    ).add_to(points_group)
        points_group.add_to(m)

    # ajouter les lignes à la carte
    if not gdf_ligne.empty:
        lignes_group = folium.FeatureGroup(name="Désordres linéaires", show=True)
        for _, row in gdf_ligne.iterrows():
            # définition de la couleur des entités
            color = "blue" # couleur par défaut
            # condition de l'activation de la vue par urgence
            if discretisation == "urgence" :
                if row["Observation Urgence"] == "Faible urgence":
                    color = "LawnGreen"
                elif row["Observation Urgence"] == "Pas de grande urgence":
                    color = "GoldenRod"
                elif row["Observation Urgence"] == "Désordre devant être traité à court ou moyen terme":
                    color = "DarkOrange"
                elif row["Observation Urgence"] == "Désordre devant être traité de façon urgente":
                    color = "Crimson"
                elif row["Observation Urgence"] == "Indéfini":
                    color = "DarkGrey"
                else :
                    color = "Black"
            ###### condition de l'activation de la vue par categorie
            elif discretisation == "categorie":
                if row["Catégorie de désordre"] == "Érosion externe":
                    color = "chocolate"
                elif row["Catégorie de désordre"] == "Érosion interne":
                    color = "blue"
                elif row["Catégorie de désordre"] == "Désordre affectant la structure":
                    color = "DarkOrange"
                elif row["Catégorie de désordre"] == "Brèche":
                    color = "Crimson"
                elif row["Catégorie de désordre"] == "Conditions d'entretien de la digue, détérioration des équipements, activités illégales, gêne à la gestion":
                    color = "GoldenRod"
                elif row["Catégorie de désordre"] == "Défaut sur dispositif de protection":
                    color = "purple"
                elif row["Catégorie de désordre"] == "Autre":
                    color = "DarkGrey"
                else :
                    color = "Black"
            ###### condition de l'activation de la vue par suite à donner
            elif discretisation == "suite" :
                if row["Observation Suite à apporter"] == "Aucune":
                    color = "DarkGrey"
                elif row["Observation Suite à apporter"] == "Surveillance":
                    color = "green"
                elif row["Observation Suite à apporter"] == "Entretien":
                    color = "DarkOrange"
                elif row["Observation Suite à apporter"] == "Etudes":
                    color = "Blue"
                elif row["Observation Suite à apporter"] == "Travaux":
                    color = "chocolate"
                elif row["Observation Suite à apporter"] == "Archivé":
                    color = "GoldenRod"
                elif row["Observation Suite à apporter"] == "Prioritaire":
                    color = "Crimson"
                elif row["Observation Suite à apporter"] == "Constat":
                    color = "purple"
                else :
                    color = "Black"
            # ligne halo blanche plus épaisse dessous
            folium.GeoJson(
                row.geometry,
                style_function=lambda x: {
                    'color': "white",
                    'weight': 10,  # plus large que la ligne principale
                    'opacity': 0.8
                },
            ).add_to(lignes_group)
            folium.GeoJson(
                row.geometry,
                style_function=lambda x, color=color: {
                    'color': color,
                    'weight': 6,
                    'opacity': 0.8
                },
                tooltip=folium.Tooltip("<br>".join(f"{col}: {row[col]}" for col in popup)),
            ).add_to(lignes_group)
            # ajoute les étiquettes sur les lignes
            coords = list(row.geometry.coords)
            # ne s'active que si des géométries sont présentes
            if coords:
                # prend le point médian de la géométrie
                midpoint = coords[len(coords) // 2]
                # création du contenu des etiquettes
                html_label = f"""<div style="font-size: 12px; color: {color}; white-space: nowrap;text-shadow:-1px -1px 0 white,1px -1px 0 white,-1px 1px 0 white,1px 1px 0 white;">"""
                for etiquette in etiquettes :
                    if str(row[etiquette]) != "nan" :  # vérifie si l'étiquette n'est pas None
                        html_label = html_label+str(row[etiquette])+"<BR>"
                html_label = html_label+"</div>"
                # création de l'étiquettes
                folium.Marker(
                    location=[midpoint[1], midpoint[0]],
                    tooltip=folium.Tooltip("<br>".join(f"{col}: {row[col]}" for col in popup)),
                    icon=folium.DivIcon(
                        html=html_label
                    )
                ).add_to(lignes_group)
        # ajout des lignes à la carte
        lignes_group.add_to(m)

    # emprise de l'affichage
    bounds = gdf.total_bounds[[1, 0, 3, 2]].reshape(2, 2).tolist()
    m.fit_bounds(bounds)
    # Contrôle de couches
    folium.LayerControl(collapsed=True).add_to(m)
    if discretisation == "urgence" :
        legend_html =  '''
        <div style="position: fixed; 
            bottom: 75px; left: 5px; width: 160px; height: 165px; 
            background-color: white; z-index:9999; font-size:14px;
            border:2px solid grey; padding: 10px;">
        <b>Niveaux d'urgence</b><br>
        <i style="color:LawnGreen;">▲ ▬</i> 0<br>
        <i style="color:GoldenRod;">▲ ▬</i> 1<br>
        <i style="color:DarkOrange;">▲ ▬</i> 2<br>
        <i style="color:Crimson;">▲ ▬</i> 3<br>
        <i style="color:DarkGrey;">▲ ▬</i> Indéfini<br>
        <i style="color:Black;">▲ ▬</i> Non renseigné<br>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
    elif discretisation == "categorie" :
        legend_html = '''
        <div style="position: fixed; 
            bottom: 75px; left: 5px; width: 185px; height: 200px; 
            background-color: white; z-index:9999; font-size:14px;
            border:2px solid grey; padding: 10px;">
        <b>Catégories de désordre</b><br>
        <i style="color:chocolate;">▲ ▬</i> ERX<br>
        <i style="color:blue;">▲ ▬</i> ERI<br>
        <i style="color:DarkOrange;">▲ ▬</i> DAF<br>
        <i style="color:Crimson;">▲ ▬</i> BRE<br>
        <i style="color:GoldenRod;">▲ ▬</i> ENT<br>
        <i style="color:purple;">▲ ▬</i> DDP<br>
        <i style="color:DarkGrey;">▲ ▬</i> AUT<br>
        <i style="color:Black;">▲ ▬</i> Non renseigné<br>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
    elif discretisation == "suite" :
        legend_html = '''
        <div style="position: fixed; 
            bottom: 75px; left: 5px; width: 160px; height: 220px; 
            background-color: white; z-index:9999; font-size:14px;
            border:2px solid grey; padding: 10px;">
        <b>Suites à apporter</b><br>
        <i style="color:darkgrey;">▲ ▬</i> AUC<br>
        <i style="color:green;">▲ ▬</i> SUR<br>
        <i style="color:DarkOrange;">▲ ▬</i> ENT<br>
        <i style="color:blue;">▲ ▬</i> ETU<br>
        <i style="color:chocolate;">▲ ▬</i> TRA<br>
        <i style="color:goldenrod;">▲ ▬</i> ARH<br>
        <i style="color:crimson;">▲ ▬</i> PRI<br>
        <i style="color:purple;">▲ ▬</i> CST<br>
        <i style="color:Black;">▲ ▬</i> Non renseigné<br>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))

    # add full screen button to map
    Fullscreen(position='topleft').add_to(m)
    # taille de la carte
    st_folium(m, width=750, height=500, key=cle)
    # afficher la carte
    return m

