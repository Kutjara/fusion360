from .. import config
import json

from ..includes import kutjaraFunctions as functions
from ..data import kutjaraBearingData as data

CMD_NAME = config.os.path.splitext(config.os.path.basename(__file__))[0]

class CommandCreatedHandler(functions.adsk.core.CommandCreatedEventHandler):    
    def __init__(self):
        super().__init__()        
    def notify(self, args):
        try:
            #define the inputs
            global _bearingImage, _bearingRoot, _bearingComponent, _bearingInnerSize, _bearingOuterSize, _bearingThickSize, _bearingReference, _bearingInnerRing, _bearingOuterRing, _bearingFilletRadius

            # Read the cached values, if they exist.
            settings = None
            settingAttribute = functions.app.activeProduct.attributes.itemByName(CMD_NAME, 'settings')
            if settingAttribute is not None:
                jsonSettings = settingAttribute.value
                settings = json.loads(jsonSettings)              
                defaultReference = settings['_defaultReference']
                defaultRoot      = settings['_defaultRoot']
            else:
                defaultReference = data.defaultBearingRef
                defaultRoot      = data.defaultBearingRoot

            cmd = args.command
            cmd.isRepeatable = False
         
            onInputChanged   = CommandInputChangedHandler()
            onExecutePreview = CommandExecuteHandler()
            onExecute        = CommandExecuteHandler()

            cmd.inputChanged.add(onInputChanged)
            cmd.executePreview.add(onExecutePreview)
            cmd.execute.add(onExecute)

            functions.handlers.append(onExecute)
            functions.handlers.append(onInputChanged)     
            functions.handlers.append(onExecutePreview)

            inputs = cmd.commandInputs

            _bearingImage = inputs.addImageCommandInput('_bearingImage', '',  "resources/kutjaraBearing/model.png")
            _bearingImage.isFullWidth = True

            _bearingRoot         = inputs.addBoolValueInput('_bearingRoot', 'Root Component', True, '', defaultRoot)

            _bearingComponent    = inputs.addStringValueInput('_bearingComponent', 'Nom du composant', data.defaultBearingName)

            _bearingInnerSize    = inputs.addDropDownCommandInput("_bearingInnerSize", "d : Diamètre d'alésage (mm)", functions.adsk.core.DropDownStyles.TextListDropDownStyle)
            _bearingReference    = inputs.addDropDownCommandInput('_bearingReference', "Reference", functions.adsk.core.DropDownStyles.TextListDropDownStyle)

            _bearingOuterSize    = inputs.addTextBoxCommandInput("_bearingOuterSize", "D : Diamètre extérieur (mm)", "", 1, True)
            _bearingThickSize    = inputs.addTextBoxCommandInput("_bearingThickSize", "H : Epaisseur (mm)", "", 1, True)
            _bearingInnerRing    = inputs.addTextBoxCommandInput('_bearingInnerRing', "d1 : Diamètre d'épaulement (mm)", "", 1, True)
            _bearingOuterRing    = inputs.addTextBoxCommandInput('_bearingOuterRing', "D1 : Diamètre d'embrèvement (mm)", "", 1, True)
            _bearingFilletRadius = inputs.addTextBoxCommandInput('_bearingFilletRadius', "r : Dimension d'arrondi (mm)", "", 1, True)

            _bearingInnerSizeList = _bearingInnerSize.listItems
            _bearingReferenceList = _bearingReference.listItems

            # Inner List
            standardBearingInnerSize = []
            for item in data.standardBearingsSize.items():
                if item[1][0] not in standardBearingInnerSize:
                    standardBearingInnerSize.append(item[1][0])
                    _bearingInnerSizeList.add(str(item[1][0]), item[1][0]==data.standardBearingsSize[defaultReference][0], '') 

            # Reference List
            for item in data.standardBearingsSize.items():
                if str(item[1][0]) == _bearingInnerSize.selectedItem.name:
                    _bearingReferenceList.add(item[0], item[0]==defaultReference, '') 

            # More
            _bearingOuterSize.text = str(data.standardBearingsSize[_bearingReference.selectedItem.name][1])
            _bearingThickSize.text = str(data.standardBearingsSize[_bearingReference.selectedItem.name][2])
            _bearingInnerRing.text = str(data.standardBearingsSize[_bearingReference.selectedItem.name][3])
            _bearingOuterRing.text = str(data.standardBearingsSize[_bearingReference.selectedItem.name][4])
            _bearingFilletRadius.text = str(data.standardBearingsSize[_bearingReference.selectedItem.name][5])

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
            
            if changedInput.id == '_bearingInnerSize':
                _bearingReference.listItems.clear()
                _bearingReferenceList = _bearingReference.listItems

                # Reference List
                for item in data.standardBearingsSize.items():
                    if str(item[1][0]) == _bearingInnerSize.selectedItem.name:
                        _bearingReferenceList.add(item[0], False, '') 
                _bearingReferenceList.item(0).isSelected = True

                # More
                _bearingOuterSize.text = str(data.standardBearingsSize[_bearingReference.selectedItem.name][1])
                _bearingThickSize.text = str(data.standardBearingsSize[_bearingReference.selectedItem.name][2])
                _bearingInnerRing.text = str(data.standardBearingsSize[_bearingReference.selectedItem.name][3])
                _bearingOuterRing.text = str(data.standardBearingsSize[_bearingReference.selectedItem.name][4])
                _bearingFilletRadius.text = str(data.standardBearingsSize[_bearingReference.selectedItem.name][5])

            elif changedInput.id == '_bearingReference':
                # More
                _bearingOuterSize.text = str(data.standardBearingsSize[_bearingReference.selectedItem.name][1])
                _bearingThickSize.text = str(data.standardBearingsSize[_bearingReference.selectedItem.name][2])
                _bearingInnerRing.text = str(data.standardBearingsSize[_bearingReference.selectedItem.name][3])
                _bearingOuterRing.text = str(data.standardBearingsSize[_bearingReference.selectedItem.name][4])
                _bearingFilletRadius.text = str(data.standardBearingsSize[_bearingReference.selectedItem.name][5])

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
                if input.id == '_bearingRoot':
                    thingToDraw.bearingRoot = input.value
                elif input.id == '_bearingComponent':
                    thingToDraw.bearingName = input.value
                elif input.id == '_bearingReference':
                    thingToDraw.bearingRef = input.selectedItem.name

            thingToDraw.build()
            args.isValidResult = True

        except:
            if functions.ui:
                functions.ui.messageBox('Failed:\n{}'.format(functions.traceback.format_exc()), CMD_NAME)

class ThingToDraw:
    def __init__(self):
        self._bearingName   = data.defaultBearingName
        self._bearingRoot   = data.defaultBearingRoot
        self._bearingRef    = data.defaultBearingRef

    #properties
    @property
    def bearingName(self):
        return self._bearingName
    @bearingName.setter
    def bearingName(self, value):
        self._bearingName = value

    @property
    def bearingRoot(self):
        return self._bearingRoot
    @bearingRoot.setter
    def bearingRoot(self, value):
        self._bearingRoot = value

    @property
    def bearingRef(self):
        return self._bearingRef
    @bearingRef.setter
    def bearingRef(self, value):
        self._bearingRef = value

    def build(self):
        try:
            global newComp
            newComp = functions.createNewComponent(self.bearingRoot)
            if newComp is None:
                functions.ui.messageBox('New component failed to create', CMD_NAME)
                return

            # Nom du composant
            newComp.name = '{} - {}'.format(self.bearingName, self.bearingRef)

            innerDiameter = data.standardBearingsSize[self.bearingRef][0]/10
            outerDiameter = data.standardBearingsSize[self.bearingRef][1]/10
            bodyHeigt     = data.standardBearingsSize[self.bearingRef][2]/10
            innerRingDiam = data.standardBearingsSize[self.bearingRef][3]/10
            outerRingDiam = data.standardBearingsSize[self.bearingRef][4]/10
            filletRadius  = data.standardBearingsSize[self.bearingRef][5]/10

            # Save the current values as attributes.
            settings = {
                            '_defaultReference' : self.bearingRef,
                            '_defaultRoot'      : self.bearingRoot
                        }
            jsonSettings = json.dumps(settings)
            des = functions.adsk.fusion.Design.cast(functions.app.activeProduct)
            attribs = des.attributes
            attribs.add(CMD_NAME, 'settings', jsonSettings)

            # Création de l'esquisse
            sketches = newComp.sketches
            xyPlane  = newComp.xYConstructionPlane
            extrudes = newComp.features.extrudeFeatures
            fillets  = newComp.features.filletFeatures

            sketch   = sketches.add(xyPlane)

            center   = functions.adsk.core.Point3D.create(0, 0, 0)

            # Valeur d'extrusion
            extrusion1 = functions.adsk.core.ValueInput.createByReal(bodyHeigt)
            extrusion2 = functions.adsk.core.ValueInput.createByReal(bodyHeigt-filletRadius)
            extrusion3 = functions.adsk.core.ValueInput.createByReal(filletRadius)
            radius     = functions.adsk.core.ValueInput.createByReal(filletRadius/2)

            # Dessin des cercles
            sketch.sketchCurves.sketchCircles.addByCenterRadius(center, innerDiameter/2)
            sketch.sketchCurves.sketchCircles.addByCenterRadius(center, innerRingDiam/2)
            sketch.sketchCurves.sketchCircles.addByCenterRadius(center, outerRingDiam/2)
            sketch.sketchCurves.sketchCircles.addByCenterRadius(center, outerDiameter/2)

            # Bague Exterieur
            outerInput = extrudes.createInput(sketch.profiles.item(3), functions.adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            outerInput.setDistanceExtent(False, extrusion1)
            body = extrudes.add(outerInput)

            # Billes (Dessus)
            upperBallInput = extrudes.createInput(sketch.profiles.item(2), functions.adsk.fusion.FeatureOperations.JoinFeatureOperation)
            upperBallInput.setDistanceExtent(False, extrusion2)
            upperBallInput.participantBodies = [body.bodies.item(0)]
            body = extrudes.add(upperBallInput)

            # Bague Interieur	
            innerInput = extrudes.createInput(sketch.profiles.item(1), functions.adsk.fusion.FeatureOperations.JoinFeatureOperation)
            innerInput.setDistanceExtent(False, extrusion1)
            innerInput.participantBodies = [body.bodies.item(0)]
            body = extrudes.add(innerInput)

            # Billes (Dessous)
            lowerBallInput = extrudes.createInput(sketch.profiles.item(2), functions.adsk.fusion.FeatureOperations.CutFeatureOperation)
            lowerBallInput.setDistanceExtent(False, extrusion3)
            lowerBallInput.participantBodies = [body.bodies.item(0)]
            body = extrudes.add(lowerBallInput)

            # Congés
            edgeCollection = functions.adsk.core.ObjectCollection.create()
            for edge in newComp.bRepBodies.item(0).edges:
                edgeCollection.add(edge)
            filletInput = fillets.createInput()  
            filletInput.addConstantRadiusEdgeSet(edgeCollection, radius, True)
            filletInput.isG2 = False
            filletInput.isRollingBallCorner = True
            fillets.add(filletInput)

        except:
            if functions.ui:
                functions.ui.messageBox('Failed to compute the bearing. This is most likely because the input values define an invalid bearing.', CMD_NAME)

