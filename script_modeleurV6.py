"""
Model exported as python.
Name : identifier_les_types_d_intersections_v6
Group : 
With QGIS : 34014
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFile
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsCoordinateReferenceSystem
import processing


class Identifier_les_types_d_intersections_v6(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('couche_route', 'Couche route', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('couche_signalisation', 'couche signalisation', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('fichier_de_style', 'Fichier de Style', behavior=QgsProcessingParameterFile.File, fileFilter='Tous les fichiers (*.*)', defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('AjoutDeLaSignalisationAuxIntersections', 'ajout de la signalisation aux intersections', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Tronons_Avec_intersections', 'tronçons_ avec_intersections', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(25, model_feedback)
        results = {}
        outputs = {}

        # reprojection de la couche signalisation
        # De manière à pouvoir faire des calculs, nous passons la couche en format projeté en Lambert 93
        alg_params = {
            'CONVERT_CURVED_GEOMETRIES': False,
            'INPUT': parameters['couche_signalisation'],
            'OPERATION': None,
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:2154'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojectionDeLaCoucheSignalisation'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Filtre par type de géométrie
        # on filtRe la couche des routes pour ne garder que les lignes, cela permet d'éviter les problèmes de géométrie qui peuvent survenir avec les points ou les polygones 
        # dans la mesure où la requete d'overpass peut renvoyer un fichier avec des points, des lignes et des polygones

        alg_params = {
            'INPUT': parameters['couche_route'],
            'LINES': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FiltreParTypeDeGomtrie'] = processing.run('native:filterbygeometry', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Reprojection de la couche route
        # De manière à pouvoir faire des calculs, nous passons la couche en format projeté en Lambert 93
        alg_params = {
            'CONVERT_CURVED_GEOMETRIES': False,
            'INPUT': outputs['FiltreParTypeDeGomtrie']['LINES'],
            'OPERATION': None,
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:2154'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojectionDeLaCoucheRoute'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Créer un index spatial pour la couche des routes pour accélérer les traitements
        alg_params = {
            'INPUT': outputs['ReprojectionDeLaCoucheRoute']['OUTPUT']
        }
        outputs['CrerUnIndexSpatialPourLaCoucheDesRoutes'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # On commence ici le bloc de traitement pour la séparation des segments par les intersections 
        # Avec l'outil "intersections de ligne" nous créons une couche de points qui représente les intersections entre les segments de la couche des routes
        alg_params = {
            'INPUT': outputs['CrerUnIndexSpatialPourLaCoucheDesRoutes']['OUTPUT'],
            'INPUT_FIELDS': [''],
            'INTERSECT': outputs['CrerUnIndexSpatialPourLaCoucheDesRoutes']['OUTPUT'],
            'INTERSECT_FIELDS': [''],
            'INTERSECT_FIELDS_PREFIX': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CrationDesIntersections'] = processing.run('native:lineintersections', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Création de lignes depuis les intersections 
        alg_params = {
            'CLOSE_PATH': False,
            'GROUP_EXPRESSION': None,
            'INPUT': outputs['CrationDesIntersections']['OUTPUT'],
            'NATURAL_SORT': False,
            'ORDER_EXPRESSION': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CrationDeLignesDepuisLesIntersections'] = processing.run('native:pointstopath', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # utilisation de l'outil transect pour créer le croisement de ligne au point 
        alg_params = {
            'ANGLE': 90,
            'INPUT': outputs['CrationDeLignesDepuisLesIntersections']['OUTPUT'],
            'LENGTH': 5,
            'SIDE': 2,  # Tous les deux
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CroisementDeLigneAuPoint'] = processing.run('native:transect', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # utilisation de l'outil splitwithlines pour créer les 1er tronçons que l'on va utiliser
        alg_params = {
            'INPUT': outputs['CrerUnIndexSpatialPourLaCoucheDesRoutes']['OUTPUT'],
            'LINES': outputs['CroisementDeLigneAuPoint']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CrationTroncons1er'] = processing.run('native:splitwithlines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}
        
        #création de variables pour le calcul du nombre d'intersections par tronçon
        couche_tronçons = outputs['CrationTroncons1er']['OUTPUT']
        expression_nb_intersections = f"""aggregate(layer:= '{couche_tronçons}', aggregate:= 'count', expression := 1, filter:=intersects($geometry, geometry(@parent)))"""

        # extraction des bonnes intersections
        # On extrait les "vraies" intersections, celles qui observent l'intersection de plus de 2 tronçons, et on récupère également les autres
        alg_params = {
            'EXPRESSION': expression_nb_intersections + ">2",
            'INPUT': outputs['CrationDesIntersections']['OUTPUT'],
            'FAIL_OUTPUT': QgsProcessing.TEMPORARY_OUTPUT,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractionDesBonnesIntersections'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Points vers lignes bonnes inter
        alg_params = {
            'CLOSE_PATH': False,
            'GROUP_EXPRESSION': None,
            'INPUT': outputs['ExtractionDesBonnesIntersections']['OUTPUT'],
            'NATURAL_SORT': False,
            'ORDER_EXPRESSION': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PointsVersLignesBonnesInter'] = processing.run('native:pointstopath', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # ajout de la signalisation aux intersections
        # On ajoute aux intersections la signalisation en prenant le panneau de signalisation le plus proche de l'intersection 
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['highway'],
            'INPUT': outputs['ExtractionDesBonnesIntersections']['OUTPUT'],
            'INPUT_2': outputs['ReprojectionDeLaCoucheSignalisation']['OUTPUT'],
            'MAX_DISTANCE': 25,
            'NEIGHBORS': 1,
            'PREFIX': 'j',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AjoutDeLaSignalisationAuxIntersections'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # index spatial tronçons
        alg_params = {
            'INPUT': outputs['CrationTroncons1er']['OUTPUT']
        }
        outputs['IndexSpatialTroncons'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # remplissage du champ "type_intersect" dans la couche des intersections
        # on vérifie d'abord si l'intersection est un rond point(information stockée dans les champs "junction" ou "junction_2"), si oui 
        # le champ "type_intersect" prend la valeur du champ "j2junction", sinon il prend la valeur du champ "jhighway" qui correspond au type 
        # de panneau de signalisation présent à l'intersection, s'il n'y a pas de panneau à l'intersection alors le champ prend la valeur "priorité à droite"
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'type_intersect',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Texte (chaîne de caractères)
            'FORMULA': 'CASE \r\nWHEN "junction_2" IS NOT NULL\r\nTHEN "junction_2"\r\nWHEN "junction" IS NOT NULL\r\nTHEN "junction"\r\nWHEN "jhighway" IS NOT NULL\r\nTHEN "jhighway"\r\nELSE \'priorité à droite\'\r\nEND',
            'INPUT': outputs['AjoutDeLaSignalisationAuxIntersections']['OUTPUT'],
            'OUTPUT': parameters['AjoutDeLaSignalisationAuxIntersections']
        }
        outputs['RemplissageDuChampType_intersect'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['AjoutDeLaSignalisationAuxIntersections'] = outputs['RemplissageDuChampType_intersect']['OUTPUT']

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # index spatial mauvaises intersections
        alg_params = {
            'INPUT': outputs['ExtractionDesBonnesIntersections']['FAIL_OUTPUT']
        }
        outputs['IndexSpatialMauvaisesIntersections'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Appliquer le style
        alg_params = {
            'INPUT': outputs['RemplissageDuChampType_intersect']['OUTPUT'],
            'STYLE': parameters['fichier_de_style']
        }
        outputs['AppliquerLeStyle'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Transect bonnes inters
        alg_params = {
            'ANGLE': 90,
            'INPUT': outputs['PointsVersLignesBonnesInter']['OUTPUT'],
            'LENGTH': 5,
            'SIDE': 2,  # Tous les deux
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['TransectBonnesInters'] = processing.run('native:transect', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # extraction des segments mauvaisement intersectés
        # Ici on extrait les segments qui sont concernés par les fausses intersections en observant quels segments intersectent les fausses intersections,
        #  c'est à dire les intersections qui n'intersectent moins de 3 tronçons que nous avons extrait à la ligne 149
        alg_params = {
            'INPUT': outputs['IndexSpatialTroncons']['OUTPUT'],
            'INTERSECT': outputs['IndexSpatialMauvaisesIntersections']['OUTPUT'],
            'PREDICATE': [0],  # intersecte
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractionDesSegmentsMauvaisementIntersects'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Regroupement des segments 
        # On regroupe les segments concernés de manière à avoir des tronçons continus, l'objectif ici est de rassembler les tronçons qui étaient séparés par 
        # les fausses intersections. Ces tronçons sont par exemple des ponts, qui dans osm sont des tronçons individuel qui mais sont en réalité dans la continuité de la route 
        # on fait attention à maintenir les éléments disjoints séparés pour maintenir l'indépendance des tronçons 

        alg_params = {
            'FIELD': [''],
            'INPUT': outputs['ExtractionDesSegmentsMauvaisementIntersects']['OUTPUT'],
            'SEPARATE_DISJOINT': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RegroupementDesSegments'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # suppression des tronçons mauvais dans la couche des routes
        # On enlève de la couche des routes les tronçons équivalent aux tronçons que l'on a regroupé dans l'étape précédente
        alg_params = {
            'GRID_SIZE': None,
            'INPUT': outputs['CrerUnIndexSpatialPourLaCoucheDesRoutes']['OUTPUT'],
            'OVERLAY': outputs['RegroupementDesSegments']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SuppressionDesTrononsMauvaisDansLaCoucheDesRoutes'] = processing.run('native:difference', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # rajout des bons tronçons dans la couche originelle
        # On rajoute dans la couche des routes les tronçons continus à la place de ceux que l'on vient d'enlever de manière à avoir une couche de route complète
        alg_params = {
            'GRID_SIZE': None,
            'INPUT': outputs['SuppressionDesTrononsMauvaisDansLaCoucheDesRoutes']['OUTPUT'],
            'OVERLAY': outputs['RegroupementDesSegments']['OUTPUT'],
            'OVERLAY_FIELDS_PREFIX': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RajoutDesBonsTrononsDansLaCoucheOriginelle'] = processing.run('native:union', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # On réitère l'étape de séparation des routes par les tronçons dans la mesure où certains tronçon unis à l'étape précédente
        # ne correspondent pas à la réalité du découpage du réseau routier 
        alg_params = {
            'INPUT': outputs['RajoutDesBonsTrononsDansLaCoucheOriginelle']['OUTPUT'],
            'LINES': outputs['TransectBonnesInters']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CouperAvecDesLignes2emeFois'] = processing.run('native:splitwithlines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # création de variables pour le remplissage des champs de priorité

        couches_intersections = outputs['AjoutDeLaSignalisationAuxIntersections']['OUTPUT']
        expression_prio_fin = f"""CASE \r\nWHEN \r\narray_first(aggregate(layer:= '{couches_intersections}', aggregate:=\'array_agg\', expression:=  "junction", filter:=intersects($geometry, end_point(geometry(@parent))))) IS NOT NULL\r\nTHEN array_first(aggregate(layer:=  '{couches_intersections}' , aggregate:=\'array_agg\', expression:=  "junction", filter:=intersects($geometry, end_point(geometry(@parent)))))\r\nWHEN \r\narray_first(aggregate(layer:=  '{couches_intersections}' , aggregate:=\'array_agg\', expression:=  "junction_2", filter:=intersects($geometry, end_point(geometry(@parent))))) IS NOT NULL\r\nTHEN array_first(aggregate(layer:=  '{couches_intersections}' , aggregate:=\'array_agg\', expression:=  "junction_2", filter:=intersects($geometry, end_point(geometry(@parent)))))\r\nWHEN  \r\narray_first(aggregate(layer:=  '{couches_intersections}', aggregate:=\'array_agg\', expression:=  "jhighway", filter:=intersects($geometry, end_point(geometry(@parent))))) IS NOT NULL\r\nTHEN \r\narray_first(aggregate(layer:=  '{couches_intersections}', aggregate:=\'array_agg\', expression:=  "jhighway", filter:=intersects($geometry, end_point(geometry(@parent)))))\r\nELSE \r\n\'priorité à droite\'\r\nEND"""
        expression_prio_debut = f"""CASE \r\nWHEN \r\narray_first(aggregate(layer:=  '{couches_intersections}' , aggregate:=\'array_agg\', expression:=  "junction", filter:=intersects($geometry, start_point(geometry(@parent))))) IS NOT NULL\r\nTHEN array_first(aggregate(layer:=  '{couches_intersections}' , aggregate:=\'array_agg\', expression:=  "junction", filter:=intersects($geometry, start_point(geometry(@parent)))))\r\nWHEN \r\narray_first(aggregate(layer:=  '{couches_intersections}' , aggregate:=\'array_agg\', expression:=  "junction_2", filter:=intersects($geometry, start_point(geometry(@parent))))) IS NOT NULL\r\nTHEN array_first(aggregate(layer:=  '{couches_intersections}' , aggregate:=\'array_agg\', expression:=  "junction_2", filter:=intersects($geometry, start_point(geometry(@parent)))))\r\nWHEN \r\narray_first(aggregate(layer:=  '{couches_intersections}' , aggregate:=\'array_agg\', expression:=  "jhighway", filter:=intersects($geometry, start_point(geometry(@parent))))) IS NOT NULL\r\nTHEN \r\narray_first(aggregate(layer:=  '{couches_intersections}' , aggregate:=\'array_agg\', expression:=  "jhighway", filter:=intersects($geometry, start_point(geometry(@parent)))))\r\n\r\nELSE \r\n\'priorité à droite\'\r\nEND"""

        # remplissage champ prio_fin
        # On remplit ici le champ qui contient le régime de priorité au début du tronçon.
        # Pour cela on compare la position d'un point intersection avec le début ou la fin du tronçon puis on vérifie si l'intersection est un rond point,
        #  si oui le champ prend la valeur du champ "junction" ou "junction_2" dans la couche des intersections, si non il prend la valeur du champ "jhighway"

        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'prio_fin',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Texte (chaîne de caractères)
            'FORMULA': expression_prio_fin,
            'INPUT': outputs['CouperAvecDesLignes2emeFois']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RemplissageChampPrio_fin'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # remplissage du champ "prio_début", idem que précdént mais on compare la position du point d'intersection avec le début du tronçon au lieu de la fin
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'prio_début',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Texte (chaîne de caractères)
            'FORMULA': expression_prio_debut, 
            'INPUT': outputs['RemplissageChampPrio_fin']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RemplissageDuChampPrio_dbut'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(23)
        if feedback.isCanceled():
            return {}
        

        # création des variables pour le calcul du nombre de tronçons intersectés
        couche_tronçons = outputs['RemplissageDuChampPrio_dbut']['OUTPUT']
        epxression_nb_troncons_intersect_debut = f"""aggregate(layer:= '{couche_tronçons}', aggregate:= 'count', expression := 1, filter:=intersects($geometry, start_point(geometry(@parent))))-1"""
        expression_nb_troncons_intersect_fin = f"""aggregate(layer:= '{couche_tronçons}', aggregate:= 'count', expression := 1, filter:=intersects($geometry, end_point(geometry(@parent))))-1"""

        # Calcul du nombre de tronçons intersecté au début, on regarde ici combien de tronçons intersectent le début du tronçon considéré
        # de manière à savoir combien de routes sont concernées par l'intersection.
        # on fait -1 pour ne pas compter le tronçon lui même
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'nb_tronçons_intersect_début',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Entier (32bit)
            'FORMULA': epxression_nb_troncons_intersect_debut,
            'INPUT': outputs['RemplissageDuChampPrio_dbut']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculDuNombreDeTrononsIntersectAuDbut'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(24)
        if feedback.isCanceled():
            return {}

        # calcul du nb de tronçons intersectés à la fin
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'nb_tronçons_inter_fin',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Entier (32bit)
            'FORMULA': expression_nb_troncons_intersect_fin,
            'INPUT': outputs['CalculDuNombreDeTrononsIntersectAuDbut']['OUTPUT'],
            'OUTPUT': parameters['Tronons_Avec_intersections']
        }
        outputs['CalculDuNbDeTrononsIntersects'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Tronons_Avec_intersections'] = outputs['CalculDuNbDeTrononsIntersects']['OUTPUT']
        return results

    def name(self):
        return 'identifier_les_types_d_intersections_v6'

    def displayName(self):
        return 'identifier_les_types_d_intersections_v6'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Identifier_les_types_d_intersections_v6()
