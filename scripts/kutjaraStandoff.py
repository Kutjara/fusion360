from .. import config
import json

from ..includes import kutjaraFunctions as functions
from ..data import kutjaraStandoffData as data

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
                setting1 = settings['_setting1']        # Type
                setting2 = settings['_setting2']        # Tread
                setting3 = settings['_setting3']        # Body Length
            else:
                setting1 = data.defaultStandoffType
                setting2 = data.defaultStandoffTread
                setting3 = data.defaultStandoffBody

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

            global _standoffImage, _standoffName, _standoffType, _standoffTread, _standoffBodyLength, _standoffStudLength, _standoffHexSize, _standoffHoleDepth

            _standoffImage = inputs.addImageCommandInput('_standoffImage', '',  "resources/kutjaraStandoff/{}.png".format(setting1))
            _standoffImage.isFullWidth = True

            _standoffName = inputs.addStringValueInput('_standoffName', 'Nom du composant', data.defaultStandoffName)

            _standoffType = inputs.addDropDownCommandInput('_standoffType', 'Type', functions.adsk.core.DropDownStyles.TextListDropDownStyle)
            standoffTypeListItems = _standoffType.listItems
            for cle in data.standardStandoffSizes.keys():
                standoffTypeListItems.add(cle, cle==setting1, '') 

            _standoffTread = inputs.addDropDownCommandInput('_standoffTread', 'Diametre', functions.adsk.core.DropDownStyles.TextListDropDownStyle)
            standoffTreadListItems = _standoffTread.listItems
            for cle in data.standardStandoffSizes[setting1].keys():
                standoffTreadListItems.add(cle, cle==setting2, '') 

            _standoffBodyLength = inputs.addDropDownCommandInput('_standoffBodyLength', 'Longueur du corps', functions.adsk.core.DropDownStyles.TextListDropDownStyle)
            _standoffHexSize    = inputs.addTextBoxCommandInput("_standoffHexSize", "Clé", "", 1, True)
            _standoffHoleDepth  = inputs.addTextBoxCommandInput("_standoffHoleDepth", "Profondeur de filetage", "", 1, True)
            _standoffStudLength = inputs.addTextBoxCommandInput("_standoffStudLength", "Longeur de filetage", "", 1, True)
            standoffBodyLengthlistItems = _standoffBodyLength.listItems
            models = data.standardStandoffSizes[setting1][setting2]
            for values in models:
                standoffBodyLengthlistItems.add('{}'.format(values[1]), values[1]==setting3, '') 
                if values[1]==setting3:
                    _standoffStudLength.text = '{} mm'.format(values[2])
                    _standoffHexSize.text = '{} mm'.format(values[3])
                    _standoffHoleDepth.text = '{} mm'.format(values[4])
            _standoffStudLength.isVisible = (_standoffType.selectedItem.name=="Male-Femelle")

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

            if changedInput.id == '_standoffType':
                _standoffImage.imageFile = "resources/kutjaraStandoff/{}.png".format(str(changedInput.selectedItem.name))

                _standoffTread.listItems.clear()
                listItems = _standoffTread.listItems
                firstItem = True            
                for cle in data.standardStandoffSizes[changedInput.selectedItem.name].keys():
                    if firstItem:
                        listItems.add(cle, True, '') 
                        firstTread = cle
                        firstItem = False
                    else:
                        listItems.add(cle, False, '') 
                
                _standoffBodyLength.listItems.clear()
                listItems = _standoffBodyLength.listItems
                firstItem = True            
                for values in data.standardStandoffSizes[changedInput.selectedItem.name][firstTread]:
                    if firstItem:
                        listItems.add('{}'.format(values[1]), True, '') 
                        _standoffStudLength.text = '{}'.format(values[2])
                        _standoffHexSize.text = '{}'.format(values[3])
                        _standoffHoleDepth.text = '{}'.format(values[4])
                        firstItem = False
                    else:
                        listItems.add('{}'.format(values[1]), False, '') 

                _standoffStudLength.isVisible = (changedInput.selectedItem.name=="Male-Femelle")

            elif changedInput.id == '_standoffTread':
                _standoffBodyLength.listItems.clear()
                firstItem = True            
                listItems = _standoffBodyLength.listItems
                for values in data.standardStandoffSizes[_standoffType.selectedItem.name][changedInput.selectedItem.name]:
                    if firstItem:
                        listItems.add('{}'.format(values[1]), True, '') 
                        _standoffStudLength.text = '{} mm'.format(values[2])
                        _standoffHexSize.text = '{} mm'.format(values[3])
                        _standoffHoleDepth.text = '{} mm'.format(values[4])
                        firstItem = False
                    else:
                        listItems.add('{}'.format(values[1]), False, '') 

            elif changedInput.id == '_standoffBodyLength':
                for values in data.standardStandoffSizes[_standoffType.selectedItem.name][_standoffTread.selectedItem.name]:
                    if changedInput.selectedItem.name == '{}'.format(values[1]):
                        _standoffStudLength.text = '{} mm'.format(values[2])
                        _standoffHexSize.text = '{} mm'.format(values[3])
                        _standoffHoleDepth.text = '{} mm'.format(values[4])
                        break

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
                if input.id == '_standoffName':
                    thingToDraw.standoffName = input.value
                elif input.id == '_standoffType':
                    thingToDraw.standoffType = input.selectedItem.name
                elif input.id == '_standoffTread':
                    thingToDraw.standoffTread = input.selectedItem.name
                elif input.id == '_standoffBodyLength':
                    thingToDraw.standoffBodyLength = float(input.selectedItem.name)

            thingToDraw.build()
            args.isValidResult = True

        except:
            if functions.ui:
                functions.ui.messageBox('Failed:\n{}'.format(functions.traceback.format_exc()), CMD_NAME)

class ThingToDraw :
    def __init__(self):
        self._standoffName        = data.defaultStandoffName
        self._standoffType        = data.defaultStandoffType
        self._standoffTread       = data.defaultStandoffTread
        self._standoffBodyLength  = 0
        self._standoffTreadValue  = 0
        self._standOffStudLength  = 0
        self._standoffHexSize     = 0
        self._standoffHoleDepth   = 0

    #properties
    @property
    def standoffName(self):
        return self._standoffName
    @standoffName.setter
    def standoffName(self, value):
        self._standoffName = value

    @property
    def standoffType(self):
        return self._standoffType
    @standoffType.setter
    def standoffType(self, value):
        self._standoffType = value

    @property
    def standoffTread(self):
        return self._standoffTread
    @standoffTread.setter
    def standoffTread(self, value):
        self._standoffTread = value

    @property
    def standoffBodyLength(self):
        return self._standoffBodyLength
    @standoffBodyLength.setter
    def standoffBodyLength(self, value):
        self._standoffBodyLength = value

    @property
    def standoffTreadValue(self):
        return self._standoffTreadValue
    @standoffTreadValue.setter
    def standoffTreadValue(self, value):
        self._standoffTreadValue = value

    @property
    def standOffStudLength(self):
        return self._standOffStudLength
    @standOffStudLength.setter
    def standOffStudLength(self, value):
        self._standOffStudLength = value

    @property
    def standoffHexSize(self):
        return self._standoffHexSize
    @standoffHexSize.setter
    def standoffHexSize(self, value):
        self._standoffHexSize = value

    @property
    def standoffHoleDepth(self):
        return self._standoffHoleDepth
    @standoffHoleDepth.setter
    def standoffHoleDepth(self, value):
        self._standoffHoleDepth = value

    def build(self):

        def cercle() :
            sketch.sketchCurves.sketchCircles.addByCenterRadius(center, (self._standoffTreadValue/20))

        def hexagone() :
            radius = (self.standoffHexSize /20) / functions.math.cos(functions.math.pi / 6)
            vertices = []
            for i in range(0, 6):
                vertex = functions.adsk.core.Point3D.create(center.x + radius * functions.math.cos(functions.math.pi * i / 3), center.y + radius * functions.math.sin(functions.math.pi * i / 3))
                vertices.append(vertex)
            for i in range(0, 6):
                sketch.sketchCurves.sketchLines.addByTwoPoints(vertices[(i+1) %6], vertices[i])

        def extrusion(val, profil, mode):
            extrusionValue = functions.adsk.core.ValueInput.createByReal(val/10)
            extrusion = extrudes.createInput(profil, mode)
            extrusion.setDistanceExtent(False, extrusionValue)
            return extrudes.add(extrusion)

        def filetage(face, diametre, isInternal):
            threadDataQuery = threads.threadDataQuery
            defaultThreadType = threadDataQuery.defaultMetricThreadType
            recommendData = threadDataQuery.recommendThreadData(diametre/10, isInternal, defaultThreadType)
            if recommendData[0] :
                threadInfo = threads.createThreadInfo(isInternal, defaultThreadType, recommendData[1], recommendData[2])
                faces = functions.adsk.core.ObjectCollection.create()
                faces.add(face)
                threadInput = threads.createInput(faces, threadInfo)
                threads.add(threadInput)

        try:
            global newComp
            newComp = functions.createNewComponent()

            if newComp is None:
                functions.ui.messageBox('New component failed to create', CMD_NAME)
                return

            # Gets the values
            model = data.standardStandoffSizes[self.standoffType][self.standoffTread]
            for value in model:
                if self.standoffBodyLength == value[1]:
                    self.standoffTreadValue = value[0]
                    self.standOffStudLength = value[2]
                    self.standoffHexSize = value[3]
                    self.standoffHoleDepth = value[4]
                    break
            
            # Save the current values as attributes.
            settings = {
                            '_setting1': self.standoffType,
                            '_setting2': self.standoffTread,
                            '_setting3': self.standoffBodyLength,
                        }
            jsonSettings = json.dumps(settings)
            des = functions.adsk.fusion.Design.cast(functions.app.activeProduct)
            attribs = des.attributes
            attribs.add(CMD_NAME, 'settings', jsonSettings)

            newComp.name = "{} ({}-{})".format(self.standoffName,self.standoffType ,self.standoffTread)

            sketches     = newComp.sketches
            xyPlane      = newComp.xYConstructionPlane
            extrudes     = newComp.features.extrudeFeatures
            threads      = newComp.features.threadFeatures

            center = functions.adsk.core.Point3D.create(0, 0, 0)

            sketch = sketches.add(xyPlane)
            
            cercle()
            hexagone()

            if self.standoffType == "Femelle-Femelle":
                standoffBody = extrusion(self.standoffBodyLength, sketch.profiles.item(1), functions.adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                filetage(standoffBody.bodies.item(0).faces.item(0), self.standoffTreadValue, True)

            elif self.standoffType == "Male-Femelle":
                standoffBody = extrusion(self.standoffBodyLength, sketch.profiles.item(1), functions.adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                standoffBody = extrusion(self.standoffBodyLength-self.standoffHoleDepth, sketch.profiles.item(0), functions.adsk.fusion.FeatureOperations.JoinFeatureOperation)
                standoffBody = extrusion(-self.standOffStudLength, sketch.profiles.item(0), functions.adsk.fusion.FeatureOperations.JoinFeatureOperation)
                filetage(standoffBody.bodies.item(0).faces.item(3), self.standoffTreadValue, True)
                filetage(standoffBody.bodies.item(0).faces.item(0), self.standoffTreadValue, False)

        except:
            if functions.ui:
                functions.ui.messageBox('Failed to compute the standoff. This is most likely because the input values define an invalid washer.', CMD_NAME)

