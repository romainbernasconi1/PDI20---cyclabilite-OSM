# PDI20 — Cyclabilité OSM
## Qualifier la cyclabilité des itinéraires OpenStreetMap

## Description

Ce modèle QGIS permet, à partir des données OpenStreetMap, d'assigner à chaque intersection la signalisation qui lui correspond sur le terrain pour les routes et chemins accessibles aux cyclistes.

Ce projet de développement informatique a été réalisé dans le cadre d'un enseignement de Master 1 à l'école Géodata-Paris par **Yasmine Moutchou**, **Victor Oberti**, **Safira Said** et **Romain Bernasconi**.

Son objectif est d'intégrer la qualification de la signalisation au niveau de l'intersection à un indicateur de cyclabilité global, réalisé par **Raphaël Bres**, Post-Doctorant à Université Grenoble Alpes et commanditaire du projet.

Ce dépôt est composé d'un fichier Python du script de notre modèle réalisé dans le modeleur QGIS (version **3.40.7** recommandée).

---

## Mode d'emploi de l'outil

### 1 — Installer le plugin SplitLinesByPoints

Dans l'onglet **Extensions**, installer le plugin **SplitLinesByPoints**.

> Plugin nécessaire au bon fonctionnement du modèle.

---

### 2 — Téléchargement des données OpenStreetMap via Overpass Turbo

Accéder à l'API : [https://overpass-turbo.eu/](https://overpass-turbo.eu/)

#### Éléments OSM à récupérer

| Élément | Tag OSM |
|---|---|
| Rond-point / giratoire | `highway = *` + `junction = roundabout` |
| Petit rond-point | `highway = mini_roundabout` |
| Panneau stop | `highway = stop` |
| Panneau cédez le passage | `highway = give_way` |
| Feu tricolore | `highway = traffic_signals` |
| Cédez le passage au feu (vélo) | `red_turn:(right/straight/left):bicycle = yes` ou `restriction:bicycle = stop/give_way` |

#### Requêtes Overpass

**Sélection des signalisations** (exemple pour Champs-sur-Marne) :

```overpassql
// Requête de sélection des signalisations
// Remplacer "Champs-sur-Marne" par la zone souhaitée dans geocodeArea:
[out:json][timeout:120];
{{geocodeArea:Champs-sur-Marne}}->.searchArea;
(
  node ["highway"~"stop|give_way|traffic_signals|mini_roundabout"]
       ["bus"!="yes"](area.searchArea);
);
out body;
>;
out skel qt;
```

**Cédez-le-passage cycliste au feu** (couche de tronçon + signalisation) :

```overpassql
// Ne fonctionne pas pour toutes les villes : certaines données
// ne sont pas mappées sur OSM (~10 000 données dans le monde)
[out:json][timeout:60];
{{geocodeArea:Champs-sur-marne}}->.searchArea;
relation["type"="restriction"]
        ["restriction:bicycle"~"(stop|give_way)"]
        (area.searchArea);
out body;
>;
out skel qt;
```

**Sélection des routes** :

```overpassql
[out:json][timeout:120];
{{geocodeArea:Champs-sur-marne}}->.searchArea;
way ["highway"~"primary|secondary|tertiary|residential|cycleway|path|living_street|unclassified|primary_link|secondary_link|tertiary_link"]
    ["cycleway" != "no"]
    ["bicycle" != "no"]
    ["bicycle_road" != "no"](area.searchArea);
out body;
>;
out skel qt;
```

---

### 3 — Utilisation du modèle sur QGIS

1. Télécharger le modèle depuis ce dépôt.
2. Ouvrir **QGIS** (version 3.40.7 recommandée).
3. Ouvrir l'interface **Modeleur** dans l'onglet **Traitement**.
4. Importer le fichier du modèle dans l'interface.
5. Lancer le script.
6. Dans la fenêtre qui s'ouvre :
   - Renseigner la couche GeoJSON des **routes** dans le champ `Couche route`
   - Renseigner la couche GeoJSON des **signalisations** dans le champ `Couche signalisation`
   - Enregistrer les nouvelles couches ou les laisser temporaires
   - Cliquer sur **Exécuter**
