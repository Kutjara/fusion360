from .. import config
import json

from ..includes import kutjaraFunctions as functions
from ..data import kutjaraNutData as data

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
                defaultTypeSetting = settings['_defaultTypeSetting']
                defaultThreadSetting = settings['_defaultThreadSetting']
            else:
                defaultTypeSetting = data.defaultNutType
                defaultThreadSetting = data.defaultNutThread

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

            global nutImage
            
            nutImage = inputs.addImageCommandInput('nutImage', '',  "resources/kutjaraNut/{}.png".format(data.defaultNutType))
            nutImage.isFullWidth = True

            inputs.addStringValueInput('nutName', 'Nom du composant', data.defaultNutName)

            headLibInput = inputs.addDropDownCommandInput('nutType', 'Type', functions.adsk.core.DropDownStyles.TextListDropDownStyle)
            listItems = headLibInput.listItems
            for cle in data.standardNutType:
                listItems.add(cle, cle==defaultTypeSetting, '') 

            threadLibInput = inputs.addDropDownCommandInput('nutThread', 'Filetage', functions.adsk.core.DropDownStyles.TextListDropDownStyle)
            listItems = threadLibInput.listItems
            for cle in data.standardNutTreads.keys():
                listItems.add(cle, cle == defaultThreadSetting, '') 

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

            if changedInput.id == 'nutType':
                nutImage.imageFile = "resources/kutjaraNut/{}.png".format(str(changedInput.selectedItem.name))

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
                if input.id == 'nutName':
                    thingToDraw.nutName = input.value
                elif input.id == 'nutThread':
                    thingToDraw.nutThread = input.selectedItem.name
                elif input.id == 'nutType':
                    thingToDraw.nutType = input.selectedItem.name

            thingToDraw.build()
            args.isValidResult = True

        except:
            if functions.ui:
                functions.ui.messageBox('Failed:\n{}'.format(functions.traceback.format_exc()), CMD_NAME)

class ThingToDraw :
    def __init__(self):
        self._nutName   = data.defaultNutName
        self._nutThread = data.defaultNutThread
        self._nutType   = data.defaultNutType

    #properties
    @property
    def nutName(self):
        return self._nutName
    @nutName.setter
    def nutName(self, value):
        self._nutName = value

    @property
    def nutThread(self):
        return self._nutThread
    @nutThread.setter
    def nutThread(self, value):
        self._nutThread = value

    @property
    def nutType(self):
        return self._nutType
    @nutType.setter
    def nutType(self, value):
        self._nutType = value

    def build(self):
        def sketchBody() :
            radius = (nut["cle"]/2) / functions.math.cos(functions.math.pi / 6)
            sketch = sketches.add(xyPlane)
            vertices = []
            for i in range(0, 6):
                vertex = functions.adsk.core.Point3D.create(center.x + radius * functions.math.cos(functions.math.pi * i / 3), center.y + radius * functions.math.sin(functions.math.pi * i / 3))
                vertices.append(vertex)
            for i in range(0, 6):
                sketch.sketchCurves.sketchLines.addByTwoPoints(vertices[(i+1) %6], vertices[i])
            return sketch

        def sketchHead() :
            sketch = sketches.add(xyPlane)
            sketch.sketchCurves.sketchCircles.addByCenterRadius(center, nut["cle"]/2)
            return sketch

        def sketchTread() :
            sketch = sketches.add(xyPlane)
            sketch.sketchCurves.sketchCircles.addByCenterRadius(center, nut["diametre"]/2)
            return sketch

        def conges(newBody) :
            radius = functions.adsk.core.ValueInput.createByReal(nut[self.nutType]["hauteurTotal"] - nut[self.nutType]["hauteurCle"])
            outerEdgeCollection = functions.adsk.core.ObjectCollection.create()
            outerEdges2 = newBody.faces.item(1).edges
            for edge in outerEdges2:
                outerEdgeCollection.add(edge);  
            outerFilletInput = outerFillets.createInput()  
            outerFilletInput.addConstantRadiusEdgeSet(outerEdgeCollection, radius, True)
            outerFilletInput.isG2 = False
            outerFilletInput.isRollingBallCorner = True
            body = outerFillets.add(outerFilletInput)
            return body.bodies.item(0)

        def buildHead() :
            newBody = None
            if nut[self.nutType]["hauteurTotal"] > nut[self.nutType]["hauteurCle"] :
                sketch = sketchHead()
                extrusion = functions.adsk.core.ValueInput.createByReal(nut[self.nutType]["hauteurTotal"])
                nutBody = extrudes.createInput(sketch.profiles.item(0), functions.adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                nutBody.setDistanceExtent(False, extrusion)
                body = extrudes.add(nutBody)
                newBody = conges(body.bodies.item(0))
            return newBody

        def buildBody(newBody) :
            sketch = sketchBody()
            extrusion = functions.adsk.core.ValueInput.createByReal(nut[self.nutType]["hauteurCle"])
            if newBody == None:
                nutBody = extrudes.createInput(sketch.profiles.item(0), functions.adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            else:
                nutBody = extrudes.createInput(sketch.profiles.item(0), functions.adsk.fusion.FeatureOperations.JoinFeatureOperation)
            nutBody.setDistanceExtent(False, extrusion)
            body = extrudes.add(nutBody)
            return body.bodies.item(0)

        def buildTread(newBody) :
            sketch = sketchTread()
            extrusion = functions.adsk.core.ValueInput.createByReal(nut[self.nutType]["hauteurFilet"])
            nutBody = extrudes.createInput(sketch.profiles.item(0), functions.adsk.fusion.FeatureOperations.CutFeatureOperation)
            nutBody.setDistanceExtent(False, extrusion)
            nutBody.participantBodies = [newBody]
            body = extrudes.add(nutBody)

            # Filetage
            sideFace = body.sideFaces.item(0)
            threadDataQuery = threads.threadDataQuery
            defaultThreadType = threadDataQuery.defaultMetricThreadType
            recommendData = threadDataQuery.recommendThreadData(nut["diametre"], True, defaultThreadType)
            if recommendData[0] :
                threadInfo = threads.createThreadInfo(True, defaultThreadType, recommendData[1], recommendData[2])
                faces = functions.adsk.core.ObjectCollection.create()
                faces.add(sideFace)
                threadInput = threads.createInput(faces, threadInfo)
                threads.add(threadInput)

            return body.bodies.item(0)

        try:
            global newComp
            newComp = functions.createNewComponent()
            newBody = None

            if newComp is None:
                functions.ui.messageBox('New component failed to create', CMD_NAME)
                return

            # Save the current values as attributes.
            settings = {
                            '_defaultTypeSetting': self.nutType,
                            '_defaultThreadSetting': self.nutThread,
                        }
            jsonSettings = json.dumps(settings)
            des = functions.adsk.fusion.Design.cast(functions.app.activeProduct)
            attribs = des.attributes
            attribs.add(CMD_NAME, 'settings', jsonSettings)

            # Caracteristiques de l'ecrou
            nut = data.standardNutTreads[self.nutThread]

            # Nom du composant
            newComp.name = "{} {} {}".format(self.nutName ,self.nutType ,self.nutThread)

            # Création de l'esquisse
            sketches     = newComp.sketches
            xyPlane      = newComp.xYConstructionPlane
            extrudes     = newComp.features.extrudeFeatures
            outerFillets = newComp.features.filletFeatures
            threads      = newComp.features.threadFeatures

            # Point central 
            center = functions.adsk.core.Point3D.create(0, 0, 0)

            # Création de l'écrou
            newBody = buildHead()
            newBody = buildBody(newBody)
            newBody = buildTread(newBody)

        except:
            if functions.ui:
                functions.ui.messageBox('Failed to compute the nut. This is most likely because the input values define an invalid nut.', CMD_NAME)

