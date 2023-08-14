from .. import config
import json

from ..includes import kutjaraFunctions as functions
from ..data import kutjaraWasherData as data

CMD_NAME = config.os.path.splitext(config.os.path.basename(__file__))[0]

class CommandCreatedHandler(functions.adsk.core.CommandCreatedEventHandler):    
    def __init__(self):
        super().__init__()        
    def notify(self, args):
        try:
            # Read the cached values, if they exist.
            settings = None
            settingAttribute = functions.app.activeProduct.attributes.itemByName(CMD_NAME, 'settings')
            if settingAttribute is not None:
                jsonSettings = settingAttribute.value
                settings = json.loads(jsonSettings)              
                settingType = settings['_settingType']
                settingInner = settings['_settingInner']
            else:
                settingType = data.defaultWasherType
                settingInner = data.defaultWasherInner

            cmd = args.command
            cmd.isRepeatable = False

            onInputChanged   = CommandInputChangedHandler()
            onExecutePreview = CommandExecuteHandler()
            onExecute        = CommandExecuteHandler()

            cmd.inputChanged.add(onInputChanged)
            cmd.executePreview.add(onExecutePreview)
            cmd.execute.add(onExecute)

            # keep the handler referenced beyond this function
            functions.handlers.append(onInputChanged)
            functions.handlers.append(onExecutePreview)
            functions.handlers.append(onExecute)

            # define the inputs
            inputs = cmd.commandInputs

            global washerImage, washerInnerLib, washerTypeLib, washerInnerTxt, washerOuterTxt, washerThinnerTxt

            washerImage = inputs.addImageCommandInput('_washerImage', '',  "resources/kutjaraWasher/{}.png".format(settingType))
            washerImage.isFullWidth = True

            inputs.addStringValueInput('washerName', 'Nom du composant', data.defaultWasherName)

            washerInnerLib = inputs.addDropDownCommandInput('_washerInner', 'Diametre interne', functions.adsk.core.DropDownStyles.TextListDropDownStyle)
            listItems = washerInnerLib.listItems
            for cle in data.standardWasherSizes.keys():
                listItems.add(cle, cle==settingInner, '') 

            washerTypeLib = inputs.addDropDownCommandInput('_washerType', 'Type', functions.adsk.core.DropDownStyles.TextListDropDownStyle)
            listItems = washerTypeLib.listItems
            for cle in data.standardWasherSizes[data.defaultWasherInner].keys():
                if cle!="diametre":
                    listItems.add(cle, cle==settingType, '') 

            washerInnerTxt   = inputs.addTextBoxCommandInput('_washerInnerTxt', 'Diametre interieur', "{} mm".format(data.standardWasherSizes[data.defaultWasherInner]["diametre"]*10), 1, True)
            washerOuterTxt   = inputs.addTextBoxCommandInput('_washerOuterTxt', 'Diametre exterieur', "{} mm".format(data.standardWasherSizes[data.defaultWasherInner][data.defaultWasherType]["externe"]*10), 1, True)
            washerThinnerTxt = inputs.addTextBoxCommandInput('_washerThinnerTxt', 'Epaisseur', "{} mm".format(data.standardWasherSizes[data.defaultWasherInner][data.defaultWasherType]["epaisseur"]*10), 1, True)
        except:
            if functions.ui:
                functions.ui.messageBox('Failed:\n{}'.format(functions.traceback.format_exc()), CMD_NAME)

class CommandInputChangedHandler(functions.adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = functions.adsk.core.InputChangedEventArgs.cast(args)
            changedInput = eventArgs.input
            
            washerInnerTxt.text   = "{} mm".format(data.standardWasherSizes[washerInnerLib.selectedItem.name]["diametre"]*10)
            washerOuterTxt.text   = "{} mm".format(data.standardWasherSizes[washerInnerLib.selectedItem.name][washerTypeLib.selectedItem.name]["externe"]*10)
            washerThinnerTxt.text = "{} mm".format(data.standardWasherSizes[washerInnerLib.selectedItem.name][washerTypeLib.selectedItem.name]["epaisseur"]*10)

            if changedInput.id == '_washerType':
                washerImage.imageFile = "resources/kutjaraWasher/{}.png".format(str(changedInput.selectedItem.name))
                
        except:
            if functions.ui:
                functions.ui.messageBox('Failed:\n{}'.format(functions.traceback.format_exc()), CMD_NAME)

class CommandExecuteHandler(functions.adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            command = args.firingEvent.sender
            inputs = command.commandInputs

            thingToDraw = ThingToDraw()
            for input in inputs:
                if input.id == 'washerName':
                    thingToDraw.washerName = input.value
                elif input.id == '_washerInner':
                    thingToDraw.washerInner = input.selectedItem.name
                elif input.id == '_washerType':
                    thingToDraw.washerType = input.selectedItem.name

            thingToDraw.build()
            args.isValidResult = True

        except:
            if functions.ui:
                functions.ui.messageBox('Failed:\n{}'.format(functions.traceback.format_exc()), CMD_NAME)

class ThingToDraw :
    def __init__(self):
        self._washerName  = data.defaultWasherName
        self._washerInner = data.defaultWasherInner
        self._washerType  = data.defaultWasherType

    #properties
    @property
    def washerName(self):
        return self._washerName
    @washerName.setter
    def washerName(self, value):
        self._washerName = value

    @property
    def washerInner(self):
        return self._washerInner
    @washerInner.setter
    def washerInner(self, value):
        self._washerInner = value

    @property
    def washerType(self):
        return self._washerType
    @washerType.setter
    def washerType(self, value):
        self._washerType = value

    def build(self):

        try:
            global newComp
            newComp = functions.createNewComponent()

            if newComp is None:
                functions.ui.messageBox('New component failed to create', CMD_NAME)
                return

            # Save the current values as attributes.
            settings = {
                            '_settingType': self.washerType,
                            '_settingInner': self.washerInner,
                        }
            jsonSettings = json.dumps(settings)
            des = functions.adsk.fusion.Design.cast(functions.app.activeProduct)
            attribs = des.attributes
            attribs.add(CMD_NAME, 'settings', jsonSettings)

            model = data.standardWasherSizes[self.washerInner]

            newComp.name = "{} ({}-{})".format(self.washerName,self.washerInner ,self.washerType)

            sketches     = newComp.sketches
            xyPlane      = newComp.xYConstructionPlane
            extrudes     = newComp.features.extrudeFeatures

            center = functions.adsk.core.Point3D.create(0, 0, 0)

            sketch = sketches.add(xyPlane)
            sketch.sketchCurves.sketchCircles.addByCenterRadius(center, model["diametre"]/2)
            sketch.sketchCurves.sketchCircles.addByCenterRadius(center, model[self.washerType]["externe"]/2)

            extrusionValue = functions.adsk.core.ValueInput.createByReal(model[self.washerType]["epaisseur"])
            extrusion = extrudes.createInput(sketch.profiles.item(1), functions.adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            extrusion.setDistanceExtent(False, extrusionValue)
            washerBody = extrudes.add(extrusion)

        except:
            if functions.ui:
                functions.ui.messageBox('Failed to compute the washer. This is most likely because the input values define an invalid washer.', CMD_NAME)

