from .. import config
import json

from ..includes import kutjaraFunctions as functions
from ..data import kutjaraBoringData as data

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
                defaultLibItem = settings['_defaultLibItem']
            else:
                defaultLibItem = data.defaultBoringType

            global  boringImage, selectionInput, typeLib, holeInput, chamferInput, diamInput, profInput, toleranceInput, _message

            cmd = args.command
            cmd.isRepeatable = False

            onInputChanged   = CommandInputChangedHandler()
            onExecutePreview = ExecuteHandler()
            onExecute        = ExecuteHandler()

            cmd.inputChanged.add(onInputChanged)
            cmd.executePreview.add(onExecutePreview)
            cmd.execute.add(onExecute)            

            functions.handlers.append(onInputChanged)
            functions.handlers.append(onExecutePreview)
            functions.handlers.append(onExecute)

            inputs = cmd.commandInputs

            boringImage = inputs.addImageCommandInput('_boringImage', '',  "resources/kutjaraBoring/{}.png".format(data.defaultBoringType))
            boringImage.isFullWidth = True

            selectionInput = inputs.addSelectionInput('_selection', 'Arete', 'Selectionnez une arete circulaire')
            selectionInput.setSelectionLimits(1,1)
            selectionInput.addSelectionFilter(functions.adsk.core.SelectionCommandInput.CircularEdges)

            typeLib = inputs.addDropDownCommandInput('_type', 'Type', functions.adsk.core.DropDownStyles.TextListDropDownStyle)
            listItems = typeLib.listItems
            for cle in data.standardBoringTypes:
                listItems.add(cle, cle == defaultLibItem, '') 

            initToleranceInput = functions.adsk.core.ValueInput.createByReal(data.defaultBoringTol)
            toleranceInput = inputs.addValueInput('_tolerance', "Tolerance",'mm',initToleranceInput)

            holeInput = inputs.addStringValueInput('_hole', 'Diametre', data.defaultBoringSize)
            holeInput.isVisible = True

            _message = inputs.addTextBoxCommandInput('_message', 'Info', "Nothing is selected", 3, True)

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

            if changedInput.id == '_selection': 
                if changedInput.selectionCount>0:
                    _entity = changedInput.selection(0).entity
                    if type(_entity) is functions.adsk.fusion.BRepEdge :
                        if (_entity.geometry.curveType == functions.adsk.core.Curve3DTypes.Circle3DCurveType) : 
                            diameter = _entity.length / functions.math.pi
                            for d in data.standardBoringDiameters:
                                if diameter >= data.standardBoringDiameters[d]["diametre"]:
                                    holeInput.value = d
                                    _message.text = 'Hole diam : {:.2f} mm ({})\n'.format(diameter*10, holeInput.value)
                        else:
                            _message.text = 'This is NOT a circle'
                    else:
                        _message.text = 'This is NOT an edge'
                else:
                    _message.text = 'Nothing is selected'

            elif changedInput.id == '_type':
                boringImage.imageFile = "resources/kutjaraBoring/{}.png".format(str(changedInput.selectedItem.name))

        except:
            if functions.ui:
                functions.ui.messageBox('Failed:\n{}'.format(functions.traceback.format_exc()), CMD_NAME)

class ExecuteHandler(functions.adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            unitsMgr = functions.app.activeProduct.unitsManager
            cmd = args.firingEvent.sender
            inputs = cmd.commandInputs

            thingToDraw = ThingToDraw()
            for input in inputs:
                if input.id == '_selection':
                    thingToDraw.edge = input.selection(0).entity

                elif input.id == '_type':
                    thingToDraw.type = input.selectedItem.name

                elif input.id == '_hole':
                    thingToDraw.hole = input.value

                elif input.id == '_tolerance':
                    thingToDraw.tolerance = unitsMgr.evaluateExpression(input.expression, "mm")
                    
            thingToDraw.build()
            
        except:
            if functions.ui:
                functions.ui.messageBox('Failed:\n{}'.format(functions.traceback.format_exc()), CMD_NAME)

class ThingToDraw :
    def __init__(self):
        self._edge      = data.defaultBoringEdge
        self._type      = data.defaultBoringType
        self._hole      = data.defaultBoringSize
        self._tolerance = data.defaultBoringTol

    #properties
    @property
    def edge(self):
        return self._edge
    @edge.setter
    def edge(self, value):
        self._edge = value

    @property
    def type(self):
        return self._type
    @type.setter
    def type(self, value):
        self._type = value

    @property
    def hole(self):
        return self._hole
    @hole.setter
    def hole(self, value):
        self._hole = value

    @property
    def tolerance(self):
        return self._tolerance
    @tolerance.setter
    def tolerance(self, value):
        self._tolerance = value

    def build(self):

        def chanfrein(chanVal) : 
            try:
                chamfers = rootComp.features.chamferFeatures
                chamferValue = functions.adsk.core.ValueInput.createByReal(chanVal)
                edgeCollection = functions.adsk.core.ObjectCollection.create()
                edgeCollection.add(self.edge)
                chamferInput = chamfers.createInput(edgeCollection, True)
                chamferInput.setToEqualDistance(chamferValue)
                chamfers.add(chamferInput)
            except:
                if functions.ui:
                    _message.text = "Chanfrein Impossible"

        def projection() :
            _center = None
            projectedEntities = sketch.project(self.edge)
            for entities in projectedEntities:
                if type(entities) is functions.adsk.fusion.SketchCircle : 
                    _center = entities.centerSketchPoint
            return _center

        def cercle(diametre) :
            sketch.sketchCurves.sketchCircles.addByCenterRadius(_center, ((diametre + self.tolerance)/2))

        def hexagone(diametre) :
            radius = ((diametre + self.tolerance)/2) / functions.math.cos(functions.math.pi / 6)
            vertices = []
            for i in range(0, 6):
                vertex = functions.adsk.core.Point3D.create(_center.geometry.x + radius * functions.math.cos(functions.math.pi * i / 3), _center.geometry.y + radius * functions.math.sin(functions.math.pi * i / 3))
                vertices.append(vertex)
            for i in range(0, 6):
                sketch.sketchCurves.sketchLines.addByTwoPoints(vertices[(i+1) %6], vertices[i])

        def extrusion(profile, val) :
            try:
                extrusion = functions.adsk.core.ValueInput.createByReal(-1*(val+self.tolerance))
                cutBoring = extrude.createInput(profile, functions.adsk.fusion.FeatureOperations.CutFeatureOperation)
                cutBoring.setDistanceExtent(False, extrusion)
                extrude.add(cutBoring)
            except:
                if functions.ui:
                    _message.text = "Extrusion Impossible\n{}".format(sketch.profiles.count)

        try:
            rootComp = self.edge.body.parentComponent

            if type(self.edge) is functions.adsk.fusion.BRepEdge :
                if (self.edge.geometry.curveType == functions.adsk.core.Curve3DTypes.Circle3DCurveType) : 

                    # Save the current values as attributes.
                    settings = {'_defaultLibItem': self.type}
                    jsonSettings = json.dumps(settings)
                    des = functions.adsk.fusion.Design.cast(functions.app.activeProduct)
                    attribs = des.attributes
                    attribs.add(CMD_NAME, 'settings', jsonSettings)

                    if self.type == "Fraisage":
                        chanval = (data.standardBoringDiameters[self.hole]["Fdiam"] - data.standardBoringDiameters[self.hole]["diametre"] + self.tolerance)/2
                        chanfrein(chanval)

                    else:
                        self.face = self.edge.faces.item(0)
                        extrude   = rootComp.features.extrudeFeatures
                        sketches  = rootComp.sketches
                        sketch    = sketches.add(self.face)
                        _center   = projection()                                
                        if self.type == 'Lamage Vis CHC':
                            cercle(data.standardBoringDiameters[self.hole][self.type][0])
                        else:
                            hexagone(data.standardBoringDiameters[self.hole][self.type][0])                             
                        extrusion(sketch.profiles.item(sketch.profiles.count-1), data.standardBoringDiameters[self.hole][self.type][1])

        except:
            if functions.ui:
                functions.ui.messageBox('Failed:\n{}'.format(functions.traceback.format_exc()), CMD_NAME)

