from .. import config
import json

from ..includes import kutjaraFunctions as functions
from ..data import kutjaraBoltData as data

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
                settingThread = settings['_settingThread']
                settingLength = settings['_settingLength']
                settingTotalLength = settings['_settingTotalLength']
            else:
                settingRoot = data.defaultBoltRoot
                settingType = data.defaultBoltHeadType
                settingThread = data.defaultBoltThread
                settingLength = data.defaultBoltLenght
                settingTotalLength = data.defaultBoltTotalLenght

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

            global boltImage, _boltRoot, threadLibInput, headLibInput, totalLenghtValue, boltLenghtValue

            inputs = cmd.commandInputs

            boltImage = inputs.addImageCommandInput('_boltImage', '',  "resources/kutjaraBolt/{}.png".format(settingType))
            boltImage.isFullWidth = True

            _boltRoot = inputs.addBoolValueInput('_boltRoot', 'Root Component', True, '', settingRoot)

            inputs.addStringValueInput('boltName', 'Nom du composant', data.defaultBoltName)

            threadLibInput = inputs.addDropDownCommandInput('_boltThread', 'Filetage', functions.adsk.core.DropDownStyles.TextListDropDownStyle)
            listItems = threadLibInput.listItems
            for cle in data.standardBoltTreads.keys():
                listItems.add(cle, cle == settingThread, '') 

            headLibInput = inputs.addDropDownCommandInput('_boltHeadType', 'Tete', functions.adsk.core.DropDownStyles.TextListDropDownStyle)
            listItems = headLibInput.listItems
            for cle in data.standardBoltTreads[data.defaultBoltThread].keys():
                if cle!="diametre":
                    listItems.add(cle, cle==settingType, '') 

            initLenght = functions.adsk.core.ValueInput.createByReal(settingLength)
            boltLenghtValue = inputs.addValueInput('_boltLenght', "Longueur de filetage",'mm',initLenght)

            initTotalLenght = functions.adsk.core.ValueInput.createByReal(settingTotalLength)
            totalLenghtValue = inputs.addValueInput('_boltTotalLenght', "Longueur",'mm',initTotalLenght)
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
            
            if changedInput.id == '_boltTotalLenght':
                if (totalLenghtValue.value < boltLenghtValue.value) :
                    boltLenghtValue.value = totalLenghtValue.value

            elif changedInput.id == '_boltLenght':
                if (totalLenghtValue.value < boltLenghtValue.value) :
                    boltLenghtValue.value = totalLenghtValue.value

            elif changedInput.id == '_boltHeadType':
                boltImage.imageFile = "resources/kutjaraBolt/{}.png".format(str(changedInput.selectedItem.name))
                
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
                if input.id == '_boltRoot':
                    thingToDraw.boltRoot = input.value

                elif input.id == '_boltName':
                    thingToDraw.boltName = input.value

                elif input.id == '_boltThread':
                    thingToDraw.boltThread = input.selectedItem.name

                elif input.id == '_boltHeadType':
                    thingToDraw.boltHeadType = input.selectedItem.name

                elif input.id == '_boltLenght':
                    thingToDraw.boltLenght = unitsMgr.evaluateExpression(input.expression, "mm")
                    
                elif input.id == '_boltTotalLenght':
                    thingToDraw.boltTotalLenght = unitsMgr.evaluateExpression(input.expression, "mm")

            thingToDraw.build()
            args.isValidResult = True

        except:
            if functions.ui:
                functions.ui.messageBox('Failed:\n{}'.format(functions.traceback.format_exc()), CMD_NAME)

class ThingToDraw:
    def __init__(self):
        self._boltRoot        = data.defaultBoltRoot
        self._boltName        = data.defaultBoltName
        self._boltFace        = None
        self._boltEdge        = None
        self._boltThread      = data.defaultBoltThread
        self._boltHeatType    = data.defaultBoltHeadType
        self._boltLenght      = data.defaultBoltLenght
        self._boltTotalLenght = data.defaultBoltTotalLenght

    #properties
    @property
    def boltRoot(self):
        return self._boltRoot
    @boltRoot.setter
    def boltRoot(self, value):
        self._boltRoot = value

    @property
    def boltName(self):
        return self._boltName
    @boltName.setter
    def boltName(self, value):
        self._boltName = value

    @property
    def boltThread(self):
        return self._boltThread
    @boltThread.setter
    def boltThread(self, value):
        self._boltThread = value

    @property
    def boltHeadType(self):
        return self._boltHeadType
    @boltHeadType.setter
    def boltHeadType(self, value):
        self._boltHeadType = value

    @property
    def boltLenght(self):
        return self._boltLenght
    @boltLenght.setter
    def boltLenght(self, value):
        self._boltLenght = value 

    @property
    def boltTotalLenght(self):
        return self._boltTotalLenght
    @boltTotalLenght.setter
    def boltTotalLenght(self, value):
        self._boltTotalLenght = value 

    def build(self):
        try:
            def sketchBody() :
                sketch = sketches.add(xyPlane)
                sketch.sketchCurves.sketchCircles.addByCenterRadius(center, bolt["diametre"]/2)
                return sketch

            def sketchHead() :
                sketch = sketches.add(xyPlane)
                sketch.sketchCurves.sketchCircles.addByCenterRadius(center, bolt[self.boltHeadType]["diamTete"]/2)
                return sketch

            def sketchKey() :
                sketch = sketches.add(xyPlane)
                radius = (bolt[self.boltHeadType]["cle"]/2) / functions.math.cos(functions.math.pi / 6)
                vertices = []
                for i in range(0, 6):
                    vertex = functions.adsk.core.Point3D.create(center.x + radius * functions.math.cos(functions.math.pi * i / 3), center.y + radius * functions.math.sin(functions.math.pi * i / 3))
                    vertices.append(vertex)
                for i in range(0, 6):
                    sketch.sketchCurves.sketchLines.addByTwoPoints(vertices[(i+1) %6], vertices[i])
                return sketch

            # Corps de la vis
            def buildBody() :
                # Corps
                sketch = sketchBody()
                extrusion = functions.adsk.core.ValueInput.createByReal(self.boltTotalLenght + bolt[self.boltHeadType]["hautTete"])
                boltBody = extrudes.createInput(sketch.profiles.item(0), functions.adsk.fusion.FeatureOperations.JoinFeatureOperation)
                boltBody.setDistanceExtent(False, extrusion)
                body = extrudes.add(boltBody)

                # Chanfrain en bout de vis
                radius = functions.adsk.core.ValueInput.createByReal(bolt[self.boltHeadType]["diamTete"]/20)
                edgeCol = functions.adsk.core.ObjectCollection.create()
                bodyEdges = body.bodies.item(0).faces.item(0).edges
                edgeCol.add(bodyEdges[0]);  
                if self.boltHeadType == "SHC" :
                    edgeCol.add(bodyEdges[1]);  
                chamferInput = chamferFeats.createInput(edgeCol, True)
                chamferInput.setToEqualDistance(radius)
                chamferFeats.add(chamferInput)

                # Filetage
                sideFace = body.sideFaces[0]
                threadDataQuery = threads.threadDataQuery
                defaultThreadType = threadDataQuery.defaultMetricThreadType
                recommendData = threadDataQuery.recommendThreadData(bolt["diametre"], False, defaultThreadType)
                if recommendData[0] :
                    threadInfo = threads.createThreadInfo(False, defaultThreadType, recommendData[1], recommendData[2])
                    faces = functions.adsk.core.ObjectCollection.create()
                    faces.add(sideFace)
                    threadInput = threads.createInput(faces, threadInfo)
                    if self.boltLenght >= self.boltTotalLenght :
                        threadInput.isFullLength = True
                    else :
                        threadInput.isFullLength = False
                        threadInput.threadLength = functions.adsk.core.ValueInput.createByReal(self.boltLenght)
                    threads.add(threadInput)

            # Tete de la vis
            def buildHead(valeur) :
                # Tete
                if self.boltHeadType == "H" :
                    sketch = sketchKey()
                else :
                    sketch = sketchHead()
                extrusion = functions.adsk.core.ValueInput.createByReal(valeur)
                boltHead = extrudes.createInput(sketch.profiles.item(0), functions.adsk.fusion.FeatureOperations.JoinFeatureOperation)
                boltHead.setDistanceExtent(False, extrusion)
                head = extrudes.add(boltHead)
                return head

            # Congés tete CHC
            def conges() :
                # Congés tete CHC
                radius = functions.adsk.core.ValueInput.createByReal(bolt[self.boltHeadType]["diamTete"]/20)
                outerEdgeCollection = functions.adsk.core.ObjectCollection.create()
                outerEdges1 = newComp.bRepBodies.item(0).faces.item(0).edges
                for edge in outerEdges1:
                    outerEdgeCollection.add(edge);  
                outerEdges2 = newComp.bRepBodies.item(0).faces.item(1).edges
                for edge in outerEdges2:
                    outerEdgeCollection.add(edge);  
                outerFilletInput = outerFillets.createInput()  
                outerFilletInput.addConstantRadiusEdgeSet(outerEdgeCollection, radius, True)
                outerFilletInput.isG2 = False
                outerFilletInput.isRollingBallCorner = True
                outerFillets.add(outerFilletInput)

            # Chanfrain tete FHC
            def chamfrain() :
                # Chanfrain tete FHC
                chamferValue = functions.adsk.core.ValueInput.createByReal((bolt["FHC"]["diamTete"]-bolt["diametre"])/2)
                edgeCol = functions.adsk.core.ObjectCollection.create()
                bodyEdges = newComp.bRepBodies.item(0).faces.item(0).edges
                edgeCol.add(bodyEdges[0]);  
                chamferInput = chamferFeats.createInput(edgeCol, True)
                chamferInput.setToEqualDistance(chamferValue)
                chamferFeats.add(chamferInput)

            # Empreinte de la cle (CHC, FHC, SHC) 
            def buildKey() :
                sketch = sketchKey()
                extrusion = functions.adsk.core.ValueInput.createByReal(bolt[self.boltHeadType]["cle"])
                boltHead = extrudes.createInput(sketch.profiles.item(0), functions.adsk.fusion.FeatureOperations.CutFeatureOperation)
                boltHead.setDistanceExtent(False, extrusion)
                boltHead.participantBodies = [newComp.bRepBodies.item(0)]
                newComp.features.extrudeFeatures.add(boltHead)

            newComp = functions.createNewComponent(self.boltRoot)
            if newComp is None:
                functions.ui.messageBox('New component failed to create', CMD_NAME)
                return

            # Save the current values as attributes.
            settings = {
                            '_settingRoot': self.boltRoot,
                            '_settingType': self.boltHeadType,
                            '_settingThread': self.boltThread,
                            '_settingLength': self.boltLenght,
                            '_settingTotalLength': self.boltTotalLenght,
                        }
            jsonSettings = json.dumps(settings)
            des = functions.adsk.fusion.Design.cast(functions.app.activeProduct)
            attribs = des.attributes
            attribs.add(CMD_NAME, 'settings', jsonSettings)

            # Nom du composant
            newComp.name = "{} {} {}x{:.0f}".format(self.boltName ,self.boltHeadType ,self.boltThread ,self.boltTotalLenght*10)

            # Caracteristiques de la vis
            bolt = data.standardBoltTreads[self.boltThread]

            # Création de l'esquisse
            xyPlane  = newComp.xYConstructionPlane
            center   = functions.adsk.core.Point3D.create(0, 0, 0)
            sketches = newComp.sketches

            extrudes     = newComp.features.extrudeFeatures
            chamferFeats = newComp.features.chamferFeatures
            threads      = newComp.features.threadFeatures
            outerFillets = newComp.features.filletFeatures

            # Vis tete H
            if self.boltHeadType == "H" :
                buildBody()
                buildHead(bolt[self.boltHeadType]["hautTete"])

            # Vis CHC
            elif self.boltHeadType == "CHC" :
                buildBody()
                buildHead(bolt[self.boltHeadType]["hautTete"])
                conges()
                buildKey()

            # Vis FHC
            elif self.boltHeadType == "FHC" :
                buildBody()
                buildHead((bolt["FHC"]["diamTete"]-bolt["diametre"])/2)
                chamfrain()
                buildKey()
            
            # Vis SHC
            elif self.boltHeadType == "SHC" :
                buildBody()
                buildKey()

        except:
            if functions.ui:
                functions.ui.messageBox('Failed to compute the bolt. This is most likely because the input values define an invalid bolt.', CMD_NAME)

