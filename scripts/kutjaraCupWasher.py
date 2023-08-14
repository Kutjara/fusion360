from .. import config
import json

from ..includes import kutjaraFunctions as functions
from ..data import kutjaraCupWasherData as data

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
                settingRoot = settings['_settingRoot']
                settingType = settings['_settingType']
                settingInner = settings['_settingInner']
            else:
                settingRoot = data.defaultCupWasherRoot
                settingType = data.defaultCupWasherType
                settingInner = data.defaultCupWasherSize

            cmd = args.command
            cmd.isRepeatable = False

            onInputChanged   = CommandInputChangedHandler()
            onExecutePreview = CommandExecuteHandler()
            onExecute        = CommandExecuteHandler()

            cmd.inputChanged.add(onInputChanged)
            cmd.executePreview.add(onExecutePreview)
            cmd.execute.add(onExecute)

            functions.handlers.append(onInputChanged)
            functions.handlers.append(onExecutePreview)
            functions.handlers.append(onExecute)

            inputs = cmd.commandInputs

            global _cupWasherImage, _cupWasherName, _cupWasherSizeLib, _cupWasherTypeLib, _cupWasherInfoInner, _cupWasherInfoOuter, _cupWasherInfoChamfer, _cupWasherInfoHeight, _cupWasherInfoThick, _cupWasherInfo

            _cupWasherImage = inputs.addImageCommandInput('_cupWasherImage', '',  "resources/kutjaraCupWasher/{}.png".format(settingType))
            _cupWasherImage.isFullWidth = True

            _cupWasherRoot = inputs.addBoolValueInput('_cupWasherRoot', 'Root Component', True, '', settingRoot)

            _cupWasherName = inputs.addStringValueInput('_cupWasherName', 'Nom du composant', data.defaultCupWasherName)

            _cupWasherSizeLib = inputs.addDropDownCommandInput('_cupWasherSize', 'Diametre nominal', functions.adsk.core.DropDownStyles.TextListDropDownStyle)
            listItems = _cupWasherSizeLib.listItems
            for cle in data.standardCupWasherSizes.keys():
                listItems.add(cle, cle==settingInner, '') 

            _cupWasherTypeLib = inputs.addDropDownCommandInput('_cupWasherType', 'Type', functions.adsk.core.DropDownStyles.TextListDropDownStyle)
            listItems = _cupWasherTypeLib.listItems
            listItems.add("Usinée", settingType == 'Usinée', '') 
            listItems.add("Emboutie", settingType == 'Emboutie', '') 

            _cupWasherInfoInner = inputs.addTextBoxCommandInput('_cupWasherInfoInner', 'Interieur', "", 1, True)
            _cupWasherInfoInner.text = "{:.2f} mm".format(data.standardCupWasherSizes[_cupWasherSizeLib.selectedItem.name]["inner"]*10)

            _cupWasherInfoOuter = inputs.addTextBoxCommandInput('_cupWasherInfoOuter', 'Exterieur', "", 1, True)
            _cupWasherInfoOuter.text = "{:.2f} mm".format(data.standardCupWasherSizes[_cupWasherSizeLib.selectedItem.name]["outer"]*10)

            _cupWasherInfoChamfer = inputs.addTextBoxCommandInput('_cupWasherInfoChamfer', 'Chanfrein', "", 1, True)
            _cupWasherInfoChamfer.text = "{:.2f} mm".format(data.standardCupWasherSizes[_cupWasherSizeLib.selectedItem.name]["chamfer"]*10)

            _cupWasherInfoHeight = inputs.addTextBoxCommandInput('_cupWasherInfoHeight', 'Hauteur', "", 1, True)
            _cupWasherInfoHeight.text = "{:.2f} mm".format(data.standardCupWasherSizes[_cupWasherSizeLib.selectedItem.name]["height"]*10)

            _cupWasherInfoThick = inputs.addTextBoxCommandInput('_cupWasherInfoThick', 'Epaisseur', "", 1, True)
            _cupWasherInfoThick.text = "{:.2f} mm".format(data.standardCupWasherSizes[_cupWasherSizeLib.selectedItem.name]["thick"]*10)
            _cupWasherInfoThick.isVisible = (_cupWasherTypeLib.selectedItem.name == "Emboutie")


        except:
            if functions.ui:
                functions.ui.messageBox('Failed to create:\n{}'.format(functions.traceback.format_exc()), CMD_NAME)

class CommandInputChangedHandler(functions.adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = functions.adsk.core.InputChangedEventArgs.cast(args)
            changedInput = eventArgs.input

            if changedInput.id == '_cupWasherType':
                _cupWasherInfoThick.isVisible = (changedInput.selectedItem.name == "Emboutie")
                _cupWasherImage.imageFile = "resources/kutjaraCupWasher/{}.png".format(str(changedInput.selectedItem.name))

            _cupWasherInfoInner.text   = "{:.2f} mm".format(data.standardCupWasherSizes[_cupWasherSizeLib.selectedItem.name]["inner"]*10)
            _cupWasherInfoOuter.text   = "{:.2f} mm".format(data.standardCupWasherSizes[_cupWasherSizeLib.selectedItem.name]["outer"]*10)
            _cupWasherInfoChamfer.text = "{:.2f} mm".format(data.standardCupWasherSizes[_cupWasherSizeLib.selectedItem.name]["chamfer"]*10)
            _cupWasherInfoHeight.text  = "{:.2f} mm".format(data.standardCupWasherSizes[_cupWasherSizeLib.selectedItem.name]["height"]*10)
            _cupWasherInfoThick.text   = "{:.2f} mm".format(data.standardCupWasherSizes[_cupWasherSizeLib.selectedItem.name]["thick"]*10)

        except:
            if functions.ui:
                functions.ui.messageBox('Failed to change :\n{}'.format(functions.traceback.format_exc()), CMD_NAME)

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
                if input.id == '_cupWasherRoot':
                    thingToDraw.cupWasherRoot = input.value
                elif input.id == '_cupWasherName':
                    thingToDraw.cupWasherName = input.value
                elif input.id == '_cupWasherSize':
                    thingToDraw.cupWasherSize = input.selectedItem.name
                elif input.id == '_cupWasherType':
                    thingToDraw.cupWasherType = input.selectedItem.name

            thingToDraw.build()
            args.isValidResult = True

        except:
            if functions.ui:
                functions.ui.messageBox('Failed to execute :\n{}'.format(functions.traceback.format_exc()), CMD_NAME)

class ThingToDraw :
    def __init__(self):
        self._cupWasherRoot = data.defaultCupWasherRoot
        self._cupWasherName = data.defaultCupWasherName
        self._cupWasherSize = data.defaultCupWasherSize
        self._cupWasherType = data.defaultCupWasherType

    #properties
    @property
    def cupWasherRoot(self):
        return self._cupWasherRoot
    @cupWasherRoot.setter
    def cupWasherRoot(self, value):
        self._cupWasherRoot = value

    @property
    def cupWasherName(self):
        return self._cupWasherName
    @cupWasherName.setter
    def cupWasherName(self, value):
        self._cupWasherName = value

    @property
    def cupWasherSize(self):
        return self._cupWasherSize
    @cupWasherSize.setter
    def cupWasherSize(self, value):
        self._cupWasherSize = value

    @property
    def cupWasherType(self):
        return self._cupWasherType
    @cupWasherType.setter
    def cupWasherType(self, value):
        self._cupWasherType = value

    def build(self):

        try:
            global newComp
            newComp = functions.createNewComponent(self.cupWasherRoot)

            if newComp is None:
                functions.ui.messageBox('New component failed to create', CMD_NAME)
                return

            # Save the current values as attributes.
            settings = {
                            '_settingRoot': self.cupWasherRoot,
                            '_settingType': self.cupWasherType,
                            '_settingInner': self.cupWasherSize,
                        }
            jsonSettings = json.dumps(settings)
            des = functions.adsk.fusion.Design.cast(functions.app.activeProduct)
            attribs = des.attributes
            attribs.add(CMD_NAME, 'settings', jsonSettings)

            model = data.standardCupWasherSizes[self.cupWasherSize]

            newComp.name = "{} ({}-{})".format(self.cupWasherName,self.cupWasherSize ,self.cupWasherType)

            sketches = newComp.sketches
            xyPlane  = newComp.xYConstructionPlane
            extrudes = newComp.features.extrudeFeatures
            chamfers = newComp.features.chamferFeatures
            shells   =  newComp.features.shellFeatures

            center = functions.adsk.core.Point3D.create(0, 0, 0)

            sketch = sketches.add(xyPlane)
            sketch.sketchCurves.sketchCircles.addByCenterRadius(center, model["inner"]/2)
            sketch.sketchCurves.sketchCircles.addByCenterRadius(center, model["outer"]/2)

            extrudeValue = functions.adsk.core.ValueInput.createByReal(model["height"])
            extrude = extrudes.createInput(sketch.profiles.item(1), functions.adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            extrude.setDistanceExtent(False, extrudeValue)
            body = extrudes.add(extrude)

            bodyEdges = body.bodies.item(0).faces.item(0).edges
            edgeCol = functions.adsk.core.ObjectCollection.create()
            edgeCol.add(bodyEdges[0]);  
            chamferValue = functions.adsk.core.ValueInput.createByReal((model["chamfer"]-model["inner"])/2)
            chamfer = chamfers.createInput(edgeCol, True)
            chamfer.setToEqualDistance(chamferValue)
            chamfers.add(chamfer)

            bodyEdges = body.bodies.item(0).faces.item(2).edges
            edgeCol = functions.adsk.core.ObjectCollection.create()
            edgeCol.add(bodyEdges[0]);  
            chamfer1 = functions.adsk.core.ValueInput.createByReal((model["outer"]-model["chamfer"])/2)
            chamfer2 = functions.adsk.core.ValueInput.createByReal(model["height"])
            chamfer = chamfers.createInput(edgeCol, True)
            chamfer.setToTwoDistances(chamfer1, chamfer2)
            chamfers.add(chamfer)

            if self.cupWasherType == 'Emboutie':
                bodyFaces = body.bodies.item(0).faces
                faceCol = functions.adsk.core.ObjectCollection.create()
                faceCol.add(bodyFaces.item(3))
                isTangentChain = False
                shell = shells.createInput(faceCol, isTangentChain)
                thickness = functions.adsk.core.ValueInput.createByReal(model["thick"])
                shell.insideThickness = thickness
                shells.add(shell)

        except:
            if functions.ui:
                functions.ui.messageBox('Failed to compute the washer. This is most likely because the input values define an invalid washer.', CMD_NAME)

