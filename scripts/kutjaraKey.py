from .. import config
import json

from ..includes import kutjaraFunctions as functions
from ..data import kutjaraKeyData as data

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
                settingShaft = settings['_settingShaft']
                settingLength = settings['_settingLength']
            else:
                settingType = data.defaultKeyType
                settingShaft = data.defaultKeyShaft
                settingLength = data.defaultKeyLength

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

            global _keyImage, _keyName, _keyType, _keyShaft, _keyLength, _keyWidth, _keyThick, _keyChamfer

            keySize = data.findStandardKey(data.defaultKeyShaft)

            inputs = cmd.commandInputs

            _keyImage = inputs.addImageCommandInput('_keyImage', '',  "resources/kutjaraKey/{}.png".format(settingType))
            _keyImage.isFullWidth = True

            _keyName = inputs.addStringValueInput('_keyName', 'Nom du composant', data.defaultKeyName)

            _keyType = keyTypeLib = inputs.addDropDownCommandInput('_keyType', 'Type', functions.adsk.core.DropDownStyles.TextListDropDownStyle)
            listItems = keyTypeLib.listItems
            for cle in data.standardKeyType:
                listItems.add(cle, cle == settingType, '') 

            initShaft = functions.adsk.core.ValueInput.createByReal(settingShaft)
            _keyShaft = inputs.addValueInput('_keyShaft', "Diametre de l'arbre",'mm',initShaft)

            initLength = functions.adsk.core.ValueInput.createByReal(settingLength)
            _keyLength = inputs.addValueInput('_keyLength', "Longueur",'mm',initLength)

            _keyWidth   = inputs.addTextBoxCommandInput('_keyWidth', 'Largeur', "{:.0f} mm".format(keySize[1]*10), 1, True)
            _keyThick   = inputs.addTextBoxCommandInput('_keyThick', 'Epaisseur', "{:.0f} mm".format(keySize[2]*10), 1, True)
            _keyChamfer = inputs.addTextBoxCommandInput('_keyChamfer', 'Chanfrein', "{:.2f} mm".format(keySize[3]*10), 1, True)

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

            if changedInput.id == '_keyType':
                _keyImage.imageFile = "resources/kutjaraKey/{}.png".format(str(changedInput.selectedItem.name))

            elif changedInput.id == '_keyShaft':
                keySize = data.findStandardKey(changedInput.value)
                _keyShaft.unitType = "mm"
                _keyWidth.text     = "{:.0f} mm".format(keySize[1]*10)
                _keyThick.text     = "{:.0f} mm".format(keySize[2]*10)
                _keyChamfer.text   = "{:.2f} mm".format(keySize[3]*10)

            elif changedInput.id == '_keyLength':
                _keyLength.unitType = "mm"

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
                if input.id == '_keyName':
                    thingToDraw.keyName = input.value
                elif input.id == '_keyType':
                    thingToDraw.keyType = input.selectedItem.name
                elif input.id == '_keyShaft':
                    thingToDraw.keyShaft = input.value
                elif input.id == '_keyLength':
                    thingToDraw.keyLength = input.value

            thingToDraw.build()
            args.isValidResult = True

        except:
            if functions.ui:
                functions.ui.messageBox('Failed:\n{}'.format(functions.traceback.format_exc()), CMD_NAME)

class ThingToDraw :
    def __init__(self):
        self._keyName   = data.defaultKeyName
        self._keyType   = data.defaultKeyType
        self._keyShaft  = data.defaultKeyShaft
        self._keyLength = data.defaultKeyLength

    #properties
    @property
    def keyName(self):
        return self._keyName
    @keyName.setter
    def keyName(self, value):
        self._keyName = value

    @property
    def keyType(self):
        return self._keyType
    @keyType.setter
    def keyType(self, value):
        self._keyType = value

    @property
    def keyShaft(self):
        return self._keyShaft
    @keyShaft.setter
    def keyShaft(self, value):
        self._keyShaft = value

    @property
    def keyLength(self):
        return self._keyLength
    @keyLength.setter
    def keyLength(self, value):
        self._keyLength = value

    def build(self):

        def chamfer(face1, face2):
            chamfers = newComp.features.chamferFeatures
            chamferValue = functions.adsk.core.ValueInput.createByReal(keySize[3])
            edgeCollection = functions.adsk.core.ObjectCollection.create()
            for edge in face1.edges:
                edgeCollection.add(edge)
            for edge in face2.edges:
                edgeCollection.add(edge); 
            chamferInput = chamfers.createInput(edgeCollection, True)
            chamferInput.setToEqualDistance(chamferValue)
            chamfers.add(chamferInput)

        def fillet(face):
            fillets  = newComp.features.filletFeatures
            filletValue = functions.adsk.core.ValueInput.createByReal(keySize[1] / 2)
            edgeCollection = functions.adsk.core.ObjectCollection.create()
            edgeCollection.add(face.edges[1])
            edgeCollection.add(face.edges[3])
            filletInput = fillets.createInput()  
            filletInput.addConstantRadiusEdgeSet(edgeCollection, filletValue, True)
            filletInput.isG2 = False
            filletInput.isRollingBallCorner = True
            fillets.add(filletInput)

        try:
            global newComp
            newComp = functions.createNewComponent()

            if newComp is None:
                functions.ui.messageBox('New component failed to create', CMD_NAME)
                return

            # Save the current values as attributes.
            settings = {
                            '_settingType': self.keyType,
                            '_settingShaft': self.keyShaft,
                            '_settingLength': self.keyLength,
                        }
            jsonSettings = json.dumps(settings)
            des = functions.adsk.fusion.Design.cast(functions.app.activeProduct)
            attribs = des.attributes
            attribs.add(CMD_NAME, 'settings', jsonSettings)

            keySize = data.findStandardKey(self.keyShaft)

            xyPlane  = newComp.xYConstructionPlane
            extrudes = newComp.features.extrudeFeatures
            sketches = newComp.sketches
            sketch   = sketches.add(xyPlane)

            newComp.name = "{} {} {:.0f}x{:.0f}".format(self.keyName, self.keyType, keySize[1]*10, self.keyLength*10)

            center = functions.adsk.core.Point3D.create(0, 0, 0)
            vertices = []
            vertices.append(functions.adsk.core.Point3D.create(center.x, center.y))
            vertices.append(functions.adsk.core.Point3D.create(center.x, center.y + keySize[1]))
            vertices.append(functions.adsk.core.Point3D.create(center.x + self.keyLength, center.y + keySize[1]))
            vertices.append(functions.adsk.core.Point3D.create(center.x + self.keyLength, center.y))
            sketch.sketchCurves.sketchLines.addByTwoPoints(vertices[0], vertices[1])
            sketch.sketchCurves.sketchLines.addByTwoPoints(vertices[1], vertices[2])
            sketch.sketchCurves.sketchLines.addByTwoPoints(vertices[2], vertices[3])
            sketch.sketchCurves.sketchLines.addByTwoPoints(vertices[3], vertices[0])

            extrusion = functions.adsk.core.ValueInput.createByReal(keySize[2])
            keyBody = extrudes.createInput(sketch.profiles.item(0), functions.adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            keyBody.setDistanceExtent(False, extrusion)
            body = extrudes.add(keyBody)

            if self.keyType =="KED":
                chamfer(body.bodies.item(0).faces.item(4),body.bodies.item(0).faces.item(5))

            elif self.keyType =="KES":
                fillet(body.bodies.item(0).faces.item(1))
                chamfer(body.bodies.item(0).faces.item(0),body.bodies.item(0).faces.item(2))

            elif self.keyType =="KEG":
                fillet(body.bodies.item(0).faces.item(1))
                fillet(body.bodies.item(0).faces.item(5))
                chamfer(body.bodies.item(0).faces.item(0),body.bodies.item(0).faces.item(3))

        except:
            if functions.ui:
                functions.ui.messageBox('Failed to compute the key. This is most likely because the input values define an invalid key.', CMD_NAME)

