# -*- coding: utf-8 -*-
import random, processing, json, os
from time import sleep
import operator

from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,Qgis, QgsSpatialIndex,QgsField,QgsFeatureRequest,QgsVectorFileWriter, QgsVectorLayer
    )
from qgis.PyQt.QtCore import QVariant
from .utils import logger, group_key_val

MESSAGE_CATEGORY = 'CadastralSuperimposeTask'

class CadastralSuperimposeTask(QgsTask):
    """This shows how to subclass QgsTask"""

    def __init__(self, description, formData, qgsProject =None):
        super().__init__(description, QgsTask.CanCancel)
        self.iterations = 0
        self.duration = 20
        self.formData = formData
        self.exception = None
        self.qgsProject = qgsProject

    def run(self):
        """Here you implement your heavy lifting.
        Should periodically test for isCanceled() to gracefully
        abort.
        This method MUST return True or False.
        Raising exceptions will crash QGIS, so we handle them
        internally and raise them in self.finished
        """
        QgsMessageLog.logMessage('Started task "{}"'.format(
                                     self.description()),
                                 MESSAGE_CATEGORY, Qgis.Info)
        
        #logger("Inside task")
        try:   
            vLayer_parcel = self.formData.vLayer_parcel
            #logger(str(vLayer_parcel))
            vLayer_plu = self.formData.vLayer_plu
            vLayer_luz = self.formData.vLayer_luz

            plu_field = self.formData.plu_field
            luz_field = self.formData.luz_field

            attr_plu = self.formData.attr_plu
            attr_luz = self.formData.attr_luz
            
            attr_plu_all = self.formData.attr_plu_all
            attr_luz_all = self.formData.attr_luz_all
            
            attr_plu_max_arp = self.formData.attr_plu_max_arp
            attr_luz_max_arp = self.formData.attr_luz_max_arp

            outfile = self.formData.outfile
            if self.formData.use_plu:
                sindex_plu = QgsSpatialIndex()
                sindex_plu = QgsSpatialIndex(vLayer_plu.getFeatures())
            if self.formData.use_luz:
                sindex_luz = QgsSpatialIndex()
                sindex_luz = QgsSpatialIndex(vLayer_luz.getFeatures())

            #https://gis.stackexchange.com/questions/156096/creating-new-empty-memory-layer-with-fields-scheme-from-other-layer-in-qgis
            # Get its list of fields
            parcelFields = vLayer_parcel.dataProvider().fields()
            # Convert its geometry type enum to a string we can pass to
            # QgsVectorLayer's constructor
            parcelLayerGeometryType = ['Point','Line','Polygon'][vLayer_parcel.geometryType()]
            # Convert its CRS to a string we can pass to QgsVectorLayer's constructor
            parcelLayerCRS = vLayer_parcel.crs().authid()
            # Make the output layer
            vLayer_parcel.selectAll()
            mem_layer = processing.run("native:saveselectedfeatures", {'INPUT': vLayer_parcel, 'OUTPUT': 'memory:',})['OUTPUT']
            mem_layer.setName(vLayer_parcel.name()+u'_copy')
            vLayer_parcel.removeSelection()


            # Add attribute Fields
            if self.formData.use_plu:
                if self.formData.default_fields:
                    if mem_layer.dataProvider().fieldNameIndex(attr_plu) == -1: #https://gis.stackexchange.com/questions/308235/writing-pyqgis-script-to-modify-layer-add-field-and-fill-it-inside-qgis
                        mem_layer.dataProvider().addAttributes([QgsField(attr_plu, QVariant.String)]) 
                        mem_layer.updateFields()
                if self.formData.add_fields:
                    if mem_layer.dataProvider().fieldNameIndex(attr_plu_all) == -1: #https://gis.stackexchange.com/questions/308235/writing-pyqgis-script-to-modify-layer-add-field-and-fill-it-inside-qgis
                        mem_layer.dataProvider().addAttributes([QgsField(attr_plu_all, QVariant.String)]) 
                        mem_layer.updateFields()
                    if mem_layer.dataProvider().fieldNameIndex(attr_plu_max_arp) == -1: #https://gis.stackexchange.com/questions/308235/writing-pyqgis-script-to-modify-layer-add-field-and-fill-it-inside-qgis
                        mem_layer.dataProvider().addAttributes([QgsField(attr_plu_max_arp, QVariant.String)]) 
                        mem_layer.updateFields()
            if self.formData.use_luz:
                if self.formData.default_fields:
                    if mem_layer.dataProvider().fieldNameIndex(attr_luz) == -1: #https://gis.stackexchange.com/questions/308235/writing-pyqgis-script-to-modify-layer-add-field-and-fill-it-inside-qgis
                        mem_layer.dataProvider().addAttributes([QgsField(attr_luz, QVariant.String)]) 
                        mem_layer.updateFields()
                if self.formData.add_fields:
                    if mem_layer.dataProvider().fieldNameIndex(attr_luz_all) == -1: #https://gis.stackexchange.com/questions/308235/writing-pyqgis-script-to-modify-layer-add-field-and-fill-it-inside-qgis
                        mem_layer.dataProvider().addAttributes([QgsField(attr_luz_all, QVariant.String)]) 
                        mem_layer.updateFields()                
                    if mem_layer.dataProvider().fieldNameIndex(attr_luz_max_arp) == -1: #https://gis.stackexchange.com/questions/308235/writing-pyqgis-script-to-modify-layer-add-field-and-fill-it-inside-qgis
                        mem_layer.dataProvider().addAttributes([QgsField(attr_luz_max_arp, QVariant.String)]) 
                        mem_layer.updateFields()
            
            attr_plu_colID= mem_layer.dataProvider().fieldNameIndex(attr_plu)
            attr_luz_colID = mem_layer.dataProvider().fieldNameIndex(attr_luz)
            attr_plu_all_colID = mem_layer.dataProvider().fieldNameIndex(attr_plu_all)
            attr_luz_all_colID = mem_layer.dataProvider().fieldNameIndex(attr_luz_all)
            attr_plu_max_arp_colID = mem_layer.dataProvider().fieldNameIndex(attr_plu_max_arp)
            attr_luz_max_arp_colID= mem_layer.dataProvider().fieldNameIndex(attr_luz_max_arp)

            #logger('attr_luz_all_colID: {} '.format(attr_luz_all_colID))
            self.total = mem_layer.featureCount()
            #logger("total = {}".format(self.total))
            
            
         
            if vLayer_parcel !="":
                for parcel in mem_layer.getFeatures():
                    parcel_geom = parcel.geometry()
                    candidateIDs_plu = sindex_plu.intersects(parcel_geom.boundingBox())
                    candidateIDs_luz = sindex_luz.intersects(parcel_geom.boundingBox())
                    if self.formData.use_plu:
                        plu_types = []
                        for candidateID_plu in candidateIDs_plu:
                            candFeatureIterator_plu = vLayer_plu.getFeatures(QgsFeatureRequest(candidateID_plu))
                            for plu in candFeatureIterator_plu:
                                plu_geom = plu.geometry()
                                if (parcel_geom.intersects(plu_geom)):
                                    intersectGeom_plu = parcel_geom.intersection(plu_geom)
                                    area_percent = round((intersectGeom_plu.area() / parcel_geom.area()) * 100, 2)
                                    plu_type = plu[plu_field]
                                    if(area_percent>0):
                                        plu_types.append({plu_type:area_percent})
                                else:
                                    pass
                        if(len(plu_types)>0):        
                            grouped_plu_types = group_key_val(plu_types)
                            if(attr_plu_all_colID != -1):
                                attr_plu_all_val= {attr_plu_all_colID: json.dumps(grouped_plu_types)}
                                mem_layer.dataProvider().changeAttributeValues({parcel.id(): attr_plu_all_val})

                            if (attr_plu_colID != -1):
                                attr_plu_val= {attr_plu_colID: max(grouped_plu_types, key=grouped_plu_types.get)}
                                mem_layer.dataProvider().changeAttributeValues({parcel.id(): attr_plu_val})
                    
                            if (attr_plu_max_arp_colID != -1):
                                attr_plu_max_arp_val = {attr_plu_max_arp_colID: max(grouped_plu_types.values())}
                                mem_layer.dataProvider().changeAttributeValues({parcel.id(): attr_plu_max_arp_val})
                            
                        
                        

                    if self.formData.use_luz:
                        luz_types = []
                        for candidateID_luz in candidateIDs_luz:
                            candFeatureIterator_luz = vLayer_luz.getFeatures(QgsFeatureRequest(candidateID_luz))
                            for luz in candFeatureIterator_luz:
                                luz_geom = luz.geometry()
                                if (parcel_geom.intersects(luz_geom)):
                                    intersectGeom_luz = parcel_geom.intersection(luz_geom)
                                    area_percent = round((intersectGeom_luz.area() / parcel_geom.area()) * 100, 2)
                                    luz_type = luz[luz_field]
                                    if(area_percent>0):
                                        luz_types.append({luz_type:area_percent})
                                else:
                                    pass
                        if(len(luz_types)>0):
                            grouped_luz_types = group_key_val(luz_types)
                            if(attr_luz_all_colID != -1):
                                attr_luz_all_val = {attr_luz_all_colID: json.dumps(grouped_luz_types)}
                                mem_layer.dataProvider().changeAttributeValues({parcel.id():attr_luz_all_val})   

                            if (attr_luz_colID != -1):
                                attr_luz_val= {attr_luz_colID: max(grouped_luz_types, key=grouped_luz_types.get)}
                                mem_layer.dataProvider().changeAttributeValues({parcel.id(): attr_luz_val})
                    
                            if (attr_luz_max_arp_colID != -1):
                                attr_luz_max_arp_val = {attr_luz_max_arp_colID: max(grouped_luz_types.values())}
                                mem_layer.dataProvider().changeAttributeValues({parcel.id(): attr_luz_max_arp_val})
                            
                    self.iterations += 1
                    # use setProgress to report progress
                    self.setProgress(self.iterations / self.total*100)
                    
                    # check isCanceled() to handle cancellation
                    if self.isCanceled():
                        return False
                    """
                    # simulate exceptions to show how to abort task
                    if arandominteger == 42:
                        # DO NOT raise Exception('bad value!')
                        # this would crash QGIS
                        self.exception = Exception('bad value!')
                        return False
                    """
                QgsVectorFileWriter.writeAsVectorFormat(mem_layer, outfile, 'UTF-8', mem_layer.crs(), 'ESRI Shapefile')  # Alternative# QgsVectorFileWriter.writeAsVectorFormat(mem_layer, self.outfile, "UTF-8", parcelLayerCRS , "ESRI Shapefile")
                layer_name = os.path.splitext(os.path.basename(outfile))[0]
                layer = QgsVectorLayer(outfile, layer_name, "ogr")
                if layer.isValid():
                    self.qgsProject.instance().addMapLayers([layer])
            
            else:
                self.exception = Exception('Parcel not selected')
                return False
            

        except Exception as e:
            #logger("{e}".format(e=e))
            self.exception = e
            raise e
        return True

    def finished(self, result):
        """
        This function is automatically called when the task has
        completed (successfully or not).
        You implement finished() to do whatever follow-up stuff
        should happen after the task is complete.
        finished is always called from the main thread, so it's safe
        to do GUI operations and raise Python exceptions here.
        result is the return value from self.run.
        """
        if result:
            #logger("Finished")
            QgsMessageLog.logMessage(
                'RandomTask "{name}" completed\n'.format(
                  name=self.description(),
                  ),
              MESSAGE_CATEGORY, Qgis.Success)
              
        else:
            if self.exception is None:
                QgsMessageLog.logMessage(
                    'RandomTask "{name}" not successful but without '\
                    'exception (probably the task was manually '\
                    'canceled by the user)'.format(
                        name=self.description()),
                    MESSAGE_CATEGORY, Qgis.Warning)
            else:
                QgsMessageLog.logMessage(
                'RandomTask {name} Exception: {exception}'.format(
                name = self.description(),
                exception = self.exception),
                MESSAGE_CATEGORY, Qgis.Critical)
                raise self.exception
    def cancel(self):
        QgsMessageLog.logMessage(
            'RandomTask "{name}" was canceled'.format(
                name=self.description()),
            MESSAGE_CATEGORY, Qgis.Info)
        super().cancel()

