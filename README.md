# PDI20 — Cyclabilité OSM
## Qualifier la cyclabilité des itinéraires OpenStreetMap

## Description

Ce modèle QGIS permet, à partir des données OpenStreetMap, d'assigner à chaque intersection la signalisation qui lui correspond sur le terrain pour les routes et chemins accessibles aux cyclistes.

Ce projet de développement informatique a été réalisé dans le cadre d'un enseignement de Master 1 à l'école Géodata-Paris par **Yasmine Moutchou**, **Victor Oberti**, **Safira Said** et **Romain Bernasconi**.

Son objectif est d'intégrer la qualification de la signalisation au niveau de l'intersection à un indicateur de cyclabilité global, réalisé par **Raphaël Bres**, Post-Doctorant à Université Grenoble Alpes et commanditaire du projet.

Ce dépôt est composé d'un fichier Python du script de notre modèle réalisé dans le modeleur QGIS (version **3.40.7** recommandée).

---

## Mode d'emploi de l'outil

---

### 1 — Téléchargement des données OpenStreetMap via Overpass Turbo

- Accéder à l'API : [https://overpass-turbo.eu/](https://overpass-turbo.eu/)
- Remplacer la requête d'exemple par l'une des requêtes ci-dessous
- Cliquer sur "exporter" pour récupérer le résultat, sélectionner le format "GeoJSON"

#### Éléments OSM à récupérer

| Élément | Tag OSM |
|---|---|
| Tronçons de route | `highway = *` + `bicycle != no` + `bicycle_road != no` |
| Rond-point / giratoire | `highway = *` + `junction = roundabout` |
| Petit rond-point | `highway = mini_roundabout` |
| Panneau stop | `highway = stop` |
| Panneau cédez-le-passage | `highway = give_way` |
| Feu tricolore | `highway = traffic_signals` |

#### Requêtes Overpass

**Sélection des signalisations** (exemple pour Champs-sur-Marne) :

```overpassql
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
// (Résultat : ~10 000 données recensées dans le monde, concentrées majoritairement dans les grandes villes françaises)
[out:json][timeout:60];
{{geocodeArea:Champs-sur-marne}}->.searchArea;
relation["type"="restriction"]
        ["restriction:bicycle"~"(stop|give_way)"]
        (area.searchArea);
out body;
>;
out skel qt;
```
**Note** : *La requête ci-dessus ne fonctionne pas pour toutes les villes car certaines données ne sont pas mappées sur OSM. Compte tenu des résultats obtenus, nous avons décidé de ne pas retenir cette requête dans le cadre de ce travail. Une mise en perspective a été apportée sur la recherche des cédez-le-passage cycliste pour la poursuite de ce travail.* 

**Sélection des routes autorisées aux cyclistes** :

```overpassql
[out:json][timeout:120];
{{geocodeArea:Champs-sur-marne}}->.searchArea;
way ["highway"~"primary|secondary|tertiary|residential|cycleway|path|living_street|unclassified|primary_link|secondary_link|tertiary_link"]
    ["bicycle" != "no"]
    ["bicycle_road" != "no"](area.searchArea);
out body;
>;
out skel qt;
```

---

### 2 Mise en place de l'outil : 
- Télécharger les fichier de script vous intéressant : 
   - modeleurV6 : utilisable pour identifier les intersections au début et à la fin de chaque tronçon 
   - modeleurV7 : idem v6 mais permettant le calcul de l'indice de cyclabilité global 


### 3 — Benchmark des performances
Performances du modeleurV6 sur la zone de Champs-sur-Marne (7.32 km², urbain en banlieue parisienne) : 
- PC Windows 11, 12th Gen Intel i3-12100f, 16Go RAM : 25 secondes
- Laptop Windows 11, AMD Ryzen 5 4600H, 16Go RAM : 33 secondes
- PC Dell Windows 11, Intel Xeon W-2223, 32Go RAM, NVIDIA RTX &-2000 : 45 secondes
