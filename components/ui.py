from .utils import logger
class FormData():
    def __init__(self, plugin):

        self.plugin = plugin
        self.vLayer_parcel =  None
        self.vLayer_plu = None
        self.vLayer_luz = None
        self.plu_field = None
        self.luz_field = None
        
        self.attr_plu = None
        self.attr_luz = None
        self.attr_plu_all = None
        self.attr_luz_all = None
        self.attr_plu_max_arp = None
        self.attr_luz_max_arp = None
        self.outfile = None
        
        self.plu_layers = []
        self.luz_layers = []
        self.parcel_layers = []
        self.plu_fields = []
        self.luz_fields = []


        self.use_plu = None
        self.use_luz = None
        self.override_input = None
        self.default_fields = None
        self.add_fields = None
        
    def validate(self):
        return True

    def update(self):
        
        self.parcel_layers = self.plugin.parcel_layers
        self.plu_layers = self.plugin.plu_layers
        self.luz_layers = self.plugin.luz_layers
        self.plu_fields = self.plugin.plu_fields
        self.luz_fields = self.plugin.luz_fields
        
        self.vLayer_parcel = self.plugin.parcel_layers[self.plugin.dlg.comboBox_parcel.currentIndex()]if len(self.plugin.parcel_layers)>0 else None
        self.vLayer_plu = self.plugin.plu_layers[self.plugin.dlg.comboBox_plu.currentIndex()]if len(self.plugin.plu_layers)>0 else None
        self.vLayer_luz = self.plugin.luz_layers[self.plugin.dlg.comboBox_luz.currentIndex()]if len(self.plugin.luz_layers)>0 else None
        self.plu_field =  self.plugin.plu_fields[self.plugin.dlg.comboBox_plu_field.currentIndex()] if len(self.plugin.plu_fields)>0 else None
        self.luz_field = self.plugin.luz_fields[self.plugin.dlg.comboBox_luz_field.currentIndex()]if len(self.plugin.luz_fields)>0 else None
        
        self.attr_plu = self.plugin.dlg.lineEdit_attr_plu.text()
        self.attr_luz = self.plugin.dlg.lineEdit_attr_luz.text()
        self.attr_plu_all = self.plugin.dlg.lineEdit_attr_plu_all.text()
        self.attr_luz_all = self.plugin.dlg.lineEdit_attr_luz_all.text()
        self.attr_plu_max_arp = self.plugin.dlg.lineEdit_attr_plu_max_arp.text()
        self.attr_luz_max_arp = self.plugin.dlg.lineEdit_attr_luz_max_arp.text()
        self.outfile = self.plugin.dlg.lineEdit_outfile.text()

        self.use_plu = self.plugin.dlg.checkBox_use_plu.checkState()
        self.use_luz = self.plugin.dlg.checkBox_use_luz.checkState()
        
        self.override_input =self.plugin.dlg.checkBox_override_input.checkState() 
        self.default_fields = self.plugin.dlg.checkBox_default_fields.checkState() 
        self.add_fields = self.plugin.dlg.checkBox_add_fields.checkState()

    def getData(self):

        return {
            "attr_plu":self.attr_plu,
            "attr_luz":self.attr_luz,
            "attr_plu_all":self.attr_plu_all,
            "attr_plu_all":self.attr_luz_all,
            "attr_plu_max_arp":self.attr_plu_max_arp ,
            "attr_luz_max_arp":self.attr_luz_max_arp,
            
            "outfile":self.outfile ,
        
            "plu_layers":str(self.plu_layers),
            "luz_layers":str(self.luz_layers),
            "parcel_layers":str(self.parcel_layers),
            "plu_fields":str(self.plu_fields),
            "luz_fields": str(self.luz_fields),
            
            "use_plu": self.use_plu,
            "use_luz":self.use_luz,
        
            "override_input":self.override_input,
            "default_fields":self.default_fields,
            "add_fields":self.add_fields,
            
            
            "vLayer_parcel": str(self.vLayer_parcel),
            "vLayer_plu":str(self.vLayer_plu),
            "vLayer_luz":str(self.vLayer_luz),
            "plu_field":str(self.plu_field),
            "luz_field":str(self.luz_field)
            }
class Context():
    def __init__(self, plugin=None
                 , iface=None
                 , application=None
                 , project=None, ):
        self.plugin =plugin
        self.iface = iface
        self.application = application
        self.project = project
        