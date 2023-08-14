from .. import config
import json

from ..includes import kutjaraFunctions as functions
from ..data import kutjaraHandlesData as data

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
                settingThread = settings['_settingThread']
            else:
                settingType = data.defaultHandleType
                settingThread = data.defaultHandleTread

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

            global _handleImage, _handleName, _handleType, _handleThread
            inputs = cmd.commandInputs

            _handleImage = inputs.addImageCommandInput('_handleImage', '',  "resources/kutjaraHandles/{}.png".format(data.defaultHandleType))
            _handleImage.isFullWidth = True

            _handleName = inputs.addStringValueInput('_handleName', 'Nom du composant', data.defaultHandleName)

            _handleType = inputs.addDropDownCommandInput('_handleType', 'Type', functions.adsk.core.DropDownStyles.TextListDropDownStyle)
            listItems = _handleType.listItems
            listItems.add("Normal", settingType == 'Normal', '') 
            listItems.add("Plat", settingType == 'Plat', '') 
            listItems.add("Long", settingType == 'Long', '') 

            _handleThread = inputs.addDropDownCommandInput('_handleThread', 'Filetage', functions.adsk.core.DropDownStyles.TextListDropDownStyle)
            listItems = _handleThread.listItems
            for cle in data.standardHandlesTreads.keys():
                listItems.add(cle, cle == settingThread, '') 
            # listItems.item(0).isSelected = True

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

            if changedInput.id == '_handleType':
                _handleImage.imageFile = "resources/kutjaraHandles/{}.png".format(str(changedInput.selectedItem.name))

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
                if input.id == '_handleName':
                    thingToDraw.handleName = input.value

                elif input.id ==  '_handleType':
                    thingToDraw.handleType = input.selectedItem.name

                elif input.id ==  '_handleThread':
                    thingToDraw.handleThread = input.selectedItem.name

            thingToDraw.build()
            args.isValidResult = True

        except:
            if functions.ui:
                functions.ui.messageBox('Failed:\n{}'.format(functions.traceback.format_exc()), CMD_NAME)

class ThingToDraw:
    def __init__(self):
        self._handleName   = data.defaultHandleName
        self._handleType   = data.defaultHandleType
        self._handleThread = data.defaultHandleTread

    #properties
    @property
    def handleName(self):
        return self._handleName
    @handleName.setter
    def handleName(self, value):
        self._handleName = value

    @property
    def handleType(self):
        return self._handleType
    @handleType.setter
    def handleType(self, value):
        self._handleType = value

    @property
    def handleThread(self):
        return self._handleThread
    @handleThread.setter
    def handleThread(self, value):
        self._handleThread = value

    def build(self):
        try:
            global newComp
            newComp = functions.createNewComponent()
            if newComp is None:
                functions.ui.messageBox('New component failed to create', CMD_NAME)
                return

            handle  = data.standardHandlesTreads[self.handleThread]

            # Save the current values as attributes.
            settings = {
                            '_settingType': self.handleType,
                            '_settingThread': self.handleThread,
                        }
            jsonSettings = json.dumps(settings)
            des = functions.adsk.fusion.Design.cast(functions.app.activeProduct)
            attribs = des.attributes
            attribs.add(CMD_NAME, 'settings', jsonSettings)

            # Nom du composant
            newComp.name = self.handleName

            # Création de l'esquisse
            sketches = newComp.sketches
            xyPlane  = newComp.xYConstructionPlane
            extrudes = newComp.features.extrudeFeatures
            fillets  = newComp.features.filletFeatures

            sketch1 = sketches.add(xyPlane)
            center  = functions.adsk.core.Point3D.create(0, 0, 0)

            sketch1.sketchCurves.sketchCircles.addByCenterRadius(center, (handle["Cle"]*2.0)/2)
            sketch1.sketchCurves.sketchCircles.addByCenterRadius(center, (handle["Cle"]*2)/2-0.1)
            sketch1.sketchCurves.sketchCircles.addByCenterRadius(center, (handle["Diametre"]+data.handleTolerance)/2)

            distance1 = functions.adsk.core.ValueInput.createByReal(handle["Epaisseur"]*2)
            if self.handleType == 'Normal' : 
                distance2 = functions.adsk.core.ValueInput.createByReal(handle["Epaisseur"]*2.00)
            elif self.handleType == 'Long' :
                distance2 = functions.adsk.core.ValueInput.createByReal(handle["Epaisseur"]*5.00)
            else:
                distance2 = functions.adsk.core.ValueInput.createByReal(handle["Epaisseur"]*0.5)
            distance3 = functions.adsk.core.ValueInput.createByReal(-1*(handle["Epaisseur"]+data.handleTolerance))

            # Diametre exterieur
            body = extrudes.addSimple(sketch1.profiles.item(0),distance1,functions.adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

            # Epaulement
            shoulderInput = extrudes.createInput(sketch1.profiles.item(1), functions.adsk.fusion.FeatureOperations.JoinFeatureOperation)
            extend1 = functions.adsk.fusion.DistanceExtentDefinition.create(distance1)        
            extend2 = functions.adsk.fusion.DistanceExtentDefinition.create(distance2)        
            shoulderInput.setTwoSidesExtent(extend1,extend2)
            shoulderInput.participantBodies = [body.bodies.item(0)]
            body = extrudes.add(shoulderInput)

            # Empreinte ecrou
            sketch2 = sketches.add(body.bodies.item(0).faces.item(4))
            center = functions.adsk.core.Point3D.create(0, 0, handle["Cle"]*1.05)
            radius = ((handle["Cle"]+data.handleTolerance)/2) / functions.math.cos(functions.math.pi / 6)
            vertices = []
            for i in range(0, 6):
                vertex = functions.adsk.core.Point3D.create(center.x + radius * functions.math.cos(functions.math.pi * i / 3), center.y + radius * functions.math.sin(functions.math.pi * i / 3))
                vertices.append(vertex)
            for i in range(0, 6):
                sketch2.sketchCurves.sketchLines.addByTwoPoints(vertices[(i+1) %6], vertices[i])
            nutInput = extrudes.createInput(sketch2.profiles.item(2), functions.adsk.fusion.FeatureOperations.CutFeatureOperation)
            nutInput.setDistanceExtent(False, distance3)
            nutInput.participantBodies = [body.bodies.item(0)]
            body = extrudes.add(nutInput)

            # Congés
            radius = functions.adsk.core.ValueInput.createByReal(0.10)
            edgeCollection = functions.adsk.core.ObjectCollection.create()
            edgeCollection.add(body.bodies.item(0).edges.item(19))
            edgeCollection.add(body.bodies.item(0).edges.item(22))
            edgeCollection.add(body.bodies.item(0).edges.item(23))
            filletInput = fillets.createInput()  
            filletInput.addConstantRadiusEdgeSet(edgeCollection, radius, True)
            filletInput.isG2 = False
            filletInput.isRollingBallCorner = True
            fillets.add(filletInput)

            # Fingerprint
            sketch3 = sketches.add(xyPlane)
            center  = functions.adsk.core.Point3D.create((handle["Cle"]*2.0)/2, 0, 0)
            sketch3.sketchCurves.sketchCircles.addByCenterRadius(center, 0.10)
            printInput = extrudes.createInput(sketch3.profiles.item(0), functions.adsk.fusion.FeatureOperations.CutFeatureOperation)
            printInput.setDistanceExtent(False, distance1)
            printInput.participantBodies = [body.bodies.item(0)]
            finger = extrudes.add(printInput)

            inputEntites = functions.adsk.core.ObjectCollection.create()
            inputEntites.add(finger)
            zAxis = newComp.zConstructionAxis
            circularFeats = newComp.features.circularPatternFeatures
            circularFeatInput = circularFeats.createInput(inputEntites, zAxis)
            circularFeatInput.quantity = functions.adsk.core.ValueInput.createByReal(functions.math.ceil(handle["Cle"]*2.0*functions.math.pi*2))
            circularFeat = circularFeats.add(circularFeatInput)

        except:
            if functions.ui:
                functions.ui.messageBox('Failed to compute the bearing. This is most likely because the input values define an invalid bearing.', CMD_NAME)

