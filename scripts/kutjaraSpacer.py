from .. import config
import json

from ..includes import kutjaraFunctions as functions
from ..data import kutjaraSpacerData as data

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
                settingInner = settings['_settingInner']
                settingOuter = settings['_settingOuter']
                settingHeight = settings['_settingHeight']
            else:
                settingInner = data.defaultSpacerInner
                settingOuter = data.defaultSpacerOuter
                settingHeight = data.defaultSpacerHeight

            cmd = args.command
            cmd.isRepeatable = False

            onExecute = CommandExecuteHandler()
            onExecutePreview = CommandExecuteHandler()

            cmd.execute.add(onExecute)
            cmd.executePreview.add(onExecutePreview)

            functions.handlers.append(onExecute)
            functions.handlers.append(onExecutePreview)

            inputs = cmd.commandInputs
            inputs.addStringValueInput('_spacerName', 'Nom du composant', data.defaultSpacerName)

            initInner = functions.adsk.core.ValueInput.createByReal(settingInner)
            inputs.addValueInput('_spacerInner', "Diametre intérieur",'mm',initInner)

            initOuter = functions.adsk.core.ValueInput.createByReal(settingOuter)
            inputs.addValueInput('_spacerOuter', "Diametre extérieur",'mm',initOuter)

            initHeight = functions.adsk.core.ValueInput.createByReal(settingHeight)
            inputs.addValueInput('_spacerHeight', "Hauteur",'mm',initHeight)

        except:
            if functions.ui:
                functions.ui.messageBox('Failed:\n{}'.format(functions.traceback.format_exc()), CMD_NAME)

class CommandExecuteHandler(functions.adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            unitsMgr = functions.app.activeProduct.unitsManager
            command = args.firingEvent.sender
            inputs = command.commandInputs

            thingToDraw = ThingToDraw()
            for input in inputs:
                if input.id == '_spacerName':
                    thingToDraw.spacerName = input.value
                elif input.id == '_spacerInner':
                    thingToDraw.spacerInner = input.value
                elif input.id == '_spacerOuter':
                    thingToDraw.spacerOuter = input.value
                elif input.id == '_spacerHeight':
                    thingToDraw.spacerHeight = input.value

            thingToDraw.build()
            args.isValidResult = True

        except:
            if functions.ui:
                functions.ui.messageBox('Failed:\n{}'.format(functions.traceback.format_exc()), CMD_NAME)

class ThingToDraw :
    def __init__(self):
        self._spacerName   = data.defaultSpacerName
        self._spacerInner  = data.defaultSpacerInner
        self._spacerOuter  = data.defaultSpacerOuter
        self._spacerHeight = data.defaultSpacerHeight

    #properties
    @property
    def spacerName(self):
        return self._spacerName
    @spacerName.setter
    def spacerName(self, value):
        self._spacerName = value

    @property
    def spacerInner(self):
        return self._spacerInner
    @spacerInner.setter
    def spacerInner(self, value):
        self._spacerInner = value

    @property
    def spacerOuter(self):
        return self._spacerOuter
    @spacerOuter.setter
    def spacerOuter(self, value):
        self._spacerOuter = value

    @property
    def spacerHeight(self):
        return self._spacerHeight
    @spacerHeight.setter
    def spacerHeight(self, value):
        self._spacerHeight = value

    def build(self):

        try:
            global newComp
            newComp = functions.createNewComponent()

            if newComp is None:
                functions.ui.messageBox('New component failed to create', CMD_NAME)
                return

            # Save the current values as attributes.
            settings = {
                            '_settingInner': self.spacerInner,
                            '_settingOuter': self.spacerOuter,
                            '_settingHeight': self.spacerHeight,
                        }
            jsonSettings = json.dumps(settings)
            des = functions.adsk.fusion.Design.cast(functions.app.activeProduct)
            attribs = des.attributes
            attribs.add(CMD_NAME, 'settings', jsonSettings)

            newComp.name = "{} {:.0f}x{:.0f}x{:.0f}".format(self.spacerName ,self.spacerInner*10 ,self.spacerOuter*10, self.spacerHeight*10)

            sketches     = newComp.sketches
            xyPlane      = newComp.xYConstructionPlane
            extrudes     = newComp.features.extrudeFeatures

            center = functions.adsk.core.Point3D.create(0, 0, 0)

            # Création de la rondelle
            sketch = sketches.add(xyPlane)
            sketch.sketchCurves.sketchCircles.addByCenterRadius(center, self.spacerInner/2)
            sketch.sketchCurves.sketchCircles.addByCenterRadius(center, self.spacerOuter/2)

            extrusion = functions.adsk.core.ValueInput.createByReal(self.spacerHeight)
            washerBody = extrudes.createInput(sketch.profiles.item(1), functions.adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            washerBody.setDistanceExtent(False, extrusion)
            extrudes.add(washerBody)

        except:
            if functions.ui:
                functions.ui.messageBox('Failed to compute the spacer. This is most likely because the input values define an invalid spacer.', CMD_NAME)

