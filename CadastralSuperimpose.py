# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CadastralSuperimpose
                                 A QGIS plugin
 This plugin computes cadastral parcel layer superimposition on Present Land Use layer and Land Use Zoning layer.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-06-30
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Ram Shrestha
        email                : sendmail4ram@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog,QMessageBox,QSizePolicy,QGridLayout
from qgis.gui import QgsMessageBar
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .CadastralSuperimpose_dialog import CadastralSuperimposeDialog
import os.path


from qgis.core import QgsProject, QgsVectorLayer, QgsApplication, QgsTask,QgsMessageLog,Qgis
from .components.ui import FormData
import json, traceback

from .components.ui import FormData, Context
from .components.tasks import CadastralSuperimposeTask
from .components.utils import logger
class CadastralSuperimpose:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.plugin = self
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'CadastralSuperimpose_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Cadastral Superimpose')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        
        #self.bar = QgsMessageBar()
        #self.bar.setSizePolicy( QSizePolicy.Minimum, QSizePolicy.Fixed )
        
        self.context = Context(
            plugin = self.plugin,
            iface = self.iface,
            application = QgsApplication,
            project = QgsProject            
            )
        self.errors={}
        self.parcel_layers = []
        self.plu_layers = []
        self.luz_layers = []

        self.plu_fields = []
        self.luz_fields = []

        self.selected_outfile = ""
      
        

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('CadastralSuperimpose', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/CadastralSuperimpose/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'TSLUMD - Cadastral Superimpose '),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Cadastral Superimpose'),
                action)
            self.iface.removeToolBarIcon(action)
    
    def show_form_data(self):
        err = traceback.print_exc()
        if self.formData is not None:
            self.dlg.textBrowser_logs.setText("ERROR: {}\nDEBUG:\n{}".format(err, json.dumps(self.formData.getData())))

    def fetch_plu_fields(self):
        # find the selected plu
        current_plu_index = self.dlg.comboBox_plu.currentIndex()
        if current_plu_index in range(0, len(self.plu_layers)):
            selected_plu = self.plu_layers[current_plu_index]
            self.plu_fields = selected_plu.fields().names()

            self.dlg.comboBox_plu_field.addItems(self.plu_fields)
            self.dlg.comboBox_plu_field.setCurrentIndex(-1)
        else:
            self.plu_fields = []
            self.dlg.comboBox_plu_field.clear()

    def fetch_luz_fields(self):
        # find the selected luz
        current_luz_index = self.dlg.comboBox_luz.currentIndex()
        if current_luz_index in range(0, len(self.luz_layers)):
            selected_luz = self.luz_layers[current_luz_index]
            self.luz_fields = selected_luz.fields().names()
            
            self.dlg.comboBox_luz_field.addItems(self.luz_fields)
            self.dlg.comboBox_luz_field.setCurrentIndex(-1)
        else:
            self.luz_fields = []
            self.dlg.comboBox_luz_field.clear()
    
    def fetch_layers_all(self):
        # Fetch the currently loaded layers
        layers_tree = QgsProject.instance().layerTreeRoot().children()
        
        self.parcel_layers = []
        self.plu_layers = []
        self.luz_layers = []
        for layer_tree_item in layers_tree:
            layer = layer_tree_item.layer()
            if isinstance(layer, (QgsVectorLayer)):
                self.parcel_layers.append(layer)
                self.plu_layers.append(layer)
                self.luz_layers.append(layer)
                #print (layer_tree_item, "is Vector Layer")
            """
            if isinstance(layer, QgsRasterLayer):
                #print (layer_tree_item, "is of type Raster")
                self.raster_layers.append(layer)
            """
        # clear the content of combo box from previous one
        self.dlg.comboBox_parcel.clear()
        self.dlg.comboBox_plu.clear()
        self.dlg.comboBox_luz.clear()
        # clear the cuntent of dependent combo box 
        self.dlg.comboBox_plu_field.clear()
        self.dlg.comboBox_luz_field.clear()
        
        # populate the comboBox with names of all loaded layers
        self.dlg.comboBox_parcel.addItems([layer.name() for layer in self.parcel_layers])
        self.dlg.comboBox_plu.addItems([layer.name() for layer in self.plu_layers])
        self.dlg.comboBox_luz.addItems([layer.name() for layer in self.luz_layers])
        
        # set currentIndex to -1 to deselect at first
        self.dlg.comboBox_parcel.setCurrentIndex(-1)
        self.dlg.comboBox_plu.setCurrentIndex(-1)        
        self.dlg.comboBox_luz.setCurrentIndex(-1)

    def select_output_file(self):
        """
        https://www.programcreek.com/python/example/103045/PyQt5.QtWidgets.QFileDialog.getSaveFileName
        """
        """
        def select_outdir(self):
            self.selected_outdir = QFileDialog.getExistingDirectory(self.dlg, caption='Choose Directory', directory=os.getcwd())
            self.dlg.lineEdit_outdir.setText(self.selected_outdir)
        """
        
        filename = QFileDialog.getSaveFileName(self.dlg,
        'Save output file', '', "ESRI Shape File (*.shp)"
         #,options=QFileDialog.DontUseNativeDialog
         )
        if filename[0] == '':
            return 0
        if filename[1] == 'ESRI Shape File (*.shp)' and filename[0][-4:] != '.shp':
            self.selected_outfile = filename[0] + '.shp'
        else:
            self.selected_outfile = filename[0]

        self.dlg.lineEdit_outfile.setText(self.selected_outfile)

    # Handlers:
    def onChange_comboBox_plu(self):
        self.fetch_plu_fields()
    def onChange_comboBox_luz(self):
        self.fetch_luz_fields()
    def onCheckBox_use_plu_changed(self):
        use_plu = self.dlg.checkBox_use_plu.isChecked()
        default_fields = self.dlg.checkBox_default_fields.isChecked()
        self.dlg.groupBox_plu.setVisible(use_plu)
        self.dlg.lineEdit_attr_plu.setVisible(use_plu and default_fields)
        self.dlg.lineEdit_attr_plu_all.setVisible(use_plu and default_fields)
        self.dlg.lineEdit_attr_plu_max_arp.setVisible(use_plu and default_fields)
        
        self.dlg.checkBox_use_plu.setVisible(True)
    def onCheckBox_use_luz_changed(self):
        use_luz = self.dlg.checkBox_use_luz.isChecked()
        default_fields = self.dlg.checkBox_default_fields.isChecked()
        self.dlg.groupBox_luz.setVisible(use_luz)
        self.dlg.lineEdit_attr_luz.setVisible(use_luz and default_fields)
        self.dlg.lineEdit_attr_luz_all.setVisible(use_luz and default_fields )
        self.dlg.lineEdit_attr_luz_max_arp.setVisible(use_luz and default_fields)
        
        self.dlg.checkBox_use_luz.setVisible(True)
    def onCheckBox_override_input_changed(self):
        override_input = self.dlg.checkBox_override_input.isChecked()
        self.dlg.groupBox_outfile.setVisible(not override_input)
    def onCheckBox_add_fields_changed(self):
        add_fields = self.dlg.checkBox_add_fields.isChecked()
        self.dlg.groupBox_add_fields.setVisible(add_fields)
        self.dlg.checkBox_add_fields.setVisible(True)
    def toggle_default_fields_editable(self):
        self.dlg.lineEdit_attr_plu.setEnabled(not self.dlg.lineEdit_attr_plu.isEnabled())
        self.dlg.lineEdit_attr_luz.setEnabled(not self.dlg.lineEdit_attr_luz.isEnabled())
        #change button stylesheet too
        if self.dlg.lineEdit_attr_plu.isEnabled():
            self.dlg.pushButton_edit_default_fields.setStyleSheet("background-color: rgb(224, 224, 224); ");
        else:
            self.dlg.pushButton_edit_default_fields.setStyleSheet("");
    def toggle_add_fields_editable(self):
        self.dlg.lineEdit_attr_plu_all.setEnabled(not self.dlg.lineEdit_attr_plu_all.isEnabled())
        self.dlg.lineEdit_attr_luz_all.setEnabled(not self.dlg.lineEdit_attr_luz_all.isEnabled())
        self.dlg.lineEdit_attr_plu_max_arp.setEnabled(not self.dlg.lineEdit_attr_plu_max_arp.isEnabled())
        self.dlg.lineEdit_attr_luz_max_arp.setEnabled(not self.dlg.lineEdit_attr_luz_max_arp.isEnabled())
        
        #change button stylesheet too
        if self.dlg.lineEdit_attr_plu_all.isEnabled():
            self.dlg.pushButton_edit_add_fields.setStyleSheet("background-color: rgb(224, 224, 224); ");
        else:
            self.dlg.pushButton_edit_add_fields.setStyleSheet("");

    def inputCheck(self):
        self.errors = {}

        if self.plugin.dlg.comboBox_parcel.currentIndex() == -1:
            self.errors['vLayer_parcel'] = "required"

        if self.plugin.dlg.checkBox_use_plu.checkState():
            if self.plugin.dlg.comboBox_plu.currentIndex() == -1:
                self.errors['vLayer_plu'] = "required"
            elif self.plugin.dlg.comboBox_plu_field.currentIndex() == -1:
                self.errors['plu_field'] = "required"
            elif self.plugin.dlg.checkBox_add_fields.checkState():
                if self.dlg.lineEdit_attr_plu_all.text() == '':
                    self.errors['attr_plu_all'] = "required"
                if self.dlg.lineEdit_attr_plu_max_arp.text() == '':
                    self.errors['attr_plu_max_areap'] = "required"
        
        if self.plugin.dlg.checkBox_use_luz.checkState():
            if self.plugin.dlg.comboBox_luz.currentIndex() == -1:
                self.errors['vLayer_luz'] = "required"
            elif self.plugin.dlg.comboBox_luz_field.currentIndex() == -1:
                self.errors['luz_field'] = "required"

            elif self.plugin.dlg.checkBox_add_fields.checkState():
                if self.dlg.lineEdit_attr_luz_all.text() == '':
                    self.errors['attr_luz_all'] = "required"
                if self.dlg.lineEdit_attr_luz_max_arp.text() == '':
                    self.errors['attr_luz_max_areap'] = "required"

        if not self.dlg.checkBox_override_input.checkState():
            if self.dlg.lineEdit_outfile.text() == '':
                self.errors['outfile'] = "required"

        if len(self.errors.keys())>0:
            #self.bar.pushMessage("Validation Error!", "Please review input", level=Qgis.Info)
            
            #QMessageBox.information(None, "Validation Error!", "Please review input")
            
            return False
        
            
        return True
    
    def hide_errors(self):
        self.dlg.error_vLayer_parcel.setVisible(False)
        self.dlg.error_vLayer_plu.setVisible(False)
        self.dlg.error_vLayer_luz.setVisible(False)
        self.dlg.error_plu_field.setVisible(False)
        self.dlg.error_luz_field.setVisible(False)
        self.dlg.error_attr_plu.setVisible(False)
        self.dlg.error_attr_luz.setVisible(False)
        self.dlg.error_attr_plu_all.setVisible(False)
        self.dlg.error_attr_luz_all.setVisible(False)
        self.dlg.error_attr_plu_max_areap.setVisible(False)
        self.dlg.error_attr_luz_max_areap.setVisible(False)
        self.dlg.error_outfile.setVisible(False)
    def show_errors(self):
        self.hide_errors()
        for key in self.errors:
            getattr(self.dlg, 'error_{}'.format(key)).setVisible(True)
        
    def execute(self):
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            if self.inputCheck():
                formData = FormData(self.plugin)
                ##UsagePattern
                globals()['task1'] = CadastralSuperimposeTask('Task - Duration 20 ms per iter',formData, qgsProject = QgsProject)
                QgsApplication.taskManager().addTask(globals()['task1'])
            else:
                self.show_errors()
                self.dlg.show()
                self.execute()

        
    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = CadastralSuperimposeDialog()
                    
            self.dlg.pushButton_debug.clicked.connect(self.show_form_data)
            self.dlg.pushButton_refreshLayers.clicked.connect(self.fetch_layers_all)
            self.dlg.pushButton_edit_default_fields.clicked.connect(self.toggle_default_fields_editable)
            self.dlg.pushButton_edit_add_fields.clicked.connect(self.toggle_add_fields_editable)
            self.dlg.pushButton_outfile.clicked.connect(self.select_output_file)
            

            self.dlg.comboBox_plu.currentTextChanged.connect(self.onChange_comboBox_plu)
            self.dlg.comboBox_luz.currentTextChanged.connect(self.onChange_comboBox_luz)

            self.dlg.checkBox_use_plu.stateChanged.connect(self.onCheckBox_use_plu_changed)
            self.dlg.checkBox_use_luz.stateChanged.connect(self.onCheckBox_use_luz_changed)

            self.dlg.checkBox_override_input.stateChanged.connect(self.onCheckBox_override_input_changed)
            self.dlg.checkBox_add_fields.stateChanged.connect(self.onCheckBox_add_fields_changed)
            self.hide_errors()

        self.fetch_layers_all()    
        # show the dialog
        self.dlg.show()
        self.execute()
        
        
