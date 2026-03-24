# PDI20---cyclabilite-OSM - Qualifier la cyclabilité des itinéraires OpenStreetMap

## Description

Ce modèle Qgis permet à partir des données OpenStreetMap d'assigner à chaque intersection la signalisation qui lui correspond sur le terrain pour les routes et chemins accessibles aux cyclistes.
Ce projet de développement informatique a été réalisé dans le cadre d'un enseignement de Master 1 à l'école Géodata-Paris par Yasmine Moutchou, Victor Oberti, Safira Said et Romain Bernasconi.
Son objectif est d'intégrer la qualification de la signalisation au niveau de l'intersection à un indicateur de cyclabilité global, réalisé par Raphaël Bres, Post-Doctorant à Université Grenoble Alpes et commenditaire du projet.

Ce dépôt est composé d'un fichier python du script de notre modèle réalisé dans le modeleur Qgis (version 3.40.7 recommendée).



## MODE D'EMPLOI DE L'OUTIL :

### 1 - Installer le plugin SplitLinesByPoints dans l'onglet Extensions

  - Plugin nécessaire au bon fonctionnement du modèle.

### 2 - Téléchargement des données OpenStreetMap sur l'api Overpass-turbo : https://overpass-turbo.eu/

  - LISTE DES ÉLÉMENTS OSM À RÉCUPÉRER SUR OVERPASS-TURBO
    Rond point et giratoire : highway = *, junction = roundabout
    petit rond point : highway = mini_roundabout
    Panneau stop : highway = stop
    Panneau cédez le passage : highway = give_way
    feu tricolore : highway = traffic_signals
    cédez le passage au feu : red_turn:(right/straight/left):bicycle = yes ; restriction:bicycle = stop/give_way
  
  - REQUÊTE : 
    // Requête de sélection des signalisations pour Champs-sur-Marne (mettre la zone de son choix dans geocodeArea:)
    [out:json][timeout:120];
    {{geocodeArea:Champs-sur-Marne}}->.searchArea;
    (node ["highway"~"stop|give_way|traffic_signals|mini_roundabout"]
      ["bus"!="yes"](area.searchArea);
    );
    out body;
    >;
    out skel qt;

  
    // Autre façon de récupérer des cédez-le-passage cycliste au feu (couche de tronçon + signalisation)
    [out:json][timeout:60];
    // Ne fonctionne pas pour toutes les villes car certaines données ne sont pas mappées sur OSM (~10 000> données dans le monde)
    {{geocodeArea:Champs-sur-marne}}->.searchArea;
    relation["type"="restriction"]
      ["restriction:bicycle"~"(stop|give_way)"]
      (area.searchArea);
    out body;
    >;
    out skel qt;

  
    // Requête de sélection des routes 
    [out:json][timeout:120];
    {{geocodeArea:Champs-sur-marne}}->.searchArea;
    way ["highway"~"primary|secondary|tertiary|residential|cycleway|path|living_street|unclassified|primary_link|secondary_link|tertiary_link"]
      ["cycleway" != "no"]
      ["bicycle" != "no"]
      ["bicycle_road" != "no"](area.searchArea);
    out body;
    >;
    out skel qt;


### 3 - Utilisation du modèle sur Qgis

  - Télécharger le modèlé du dépôt
  - Ouvrir Qgis (version 3.40.7 recommandée)
  - Ouvrir l'interface modeleur dans l'onglet traitement
  - Une fois l'interface ouverte, importer le fichier du modèle
  - Lancer le script
  - Dans la nouvelle page qui s'ouvre : 
      mettre la couche geojson des routes dans "Couche route"
      mettre la couche geojson des signalisations dans "Couche signalisation"
      enregistrer les nouvelles couches ou les laisser temporaires et exécuter le script
      
