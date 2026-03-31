# Utilisation de l'outil 

## Utilisation du modelbuilder V6 

1. Avoir récupérer les données sur Overpass(procédure décrite dans le readme)
2. Ouvrir **QGIS** (version 3.40.7 recommandée).
3. Ouvrir l'interface **Modeleur** dans l'onglet **Traitement**.
4. Ouvrir le model builder
5. Ajouter les couches issues de Overpass :
   - Renseigner la couche GeoJSON des **routes** dans le champ `Couche route`
   - Renseigner la couche GeoJSON des **signalisations** dans le champ `Couche signalisation`
   - Renseigner le fichier de style inclut dans le repository
   - Enregistrer les nouvelles couches ou les laisser temporaires
6. Lancer le modèle builder 
7. Le modèle fourni en résultat 2 couches :
   - Une couche de ligne présentant les tronçons avec des champs "prio_début" et "prio_fin" présentant le régime de priorité au début et à la fin du tronçon
   - une couche de point avec un style permettant de visualiser le type d'intersection et les panneaux de signalisation français associés

## Utilisation du script python du modeleur V6

2. Ouvrir **QGIS** (version 3.40.7 recommandée).
3. Afficher la **Boîte à outils de traitements**, onglet **Scripts** et **Ouvrir un script existant...**
3. Ajouter les couches nécéssaires
4. Lancer le script

## Utilisation du modelbuilder V7

1. Executer les traitements décrit dans ce dépot git : https://github.com/raphael-bres/cyclabiliteOSM.git
2. Ouvrir **QGIS** (version 3.40.7 recommandée).
3. Ouvrir l'interface **Modeleur** dans l'onglet **Traitement**.
4. Ouvrir le model builder
5. Ajouter les couches 
   - Renseigner des **routes** issues des traitements de l'étape 1 dans le champ `Couche route`
   - Renseigner la couche GeoJSON des **signalisations** dans le champ `Couche signalisation`
   - Renseigner le fichier de style inclut dans le repository
   - Enregistrer les nouvelles couches ou les laisser temporaires
6. Lancer le modèle builder 
7. Le modèle fourni en résultat 2 couches :
   - Une couche de ligne présentant les tronçons avec un champ "score final" présentant le score de cyclabilité du tronçon 
   - une couche de point avec un style permettant de visualiser le type d'intersection et les panneaux de signalisation français associés

# Récupération du resultat : 

1. Le modèle fourni en résultat 2 couches :
   - Une couche de ligne présentant les tronçons avec des champs "prio_début" et "prio_fin" présentant le régime de priorité au début et à la fin du tronçon
   - une couche de point avec un style permettant de visualiser le type d'intersection et les panneaux de signalisation français associés

2. Extraction des couches : l'extraction des couches de résultats est possible, nous conseillons pour l'instant de le faire vers un format geopackage ou geojson, le format Shapefile (et aussi geopackage parfois) pose des problèmes vis à vis du type de certains champs.