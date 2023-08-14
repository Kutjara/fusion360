from .. import config
import json
import math

from ..includes import kutjaraFunctions as functions
from ..data import kutjaraGearData as data

CMD_NAME = config.os.path.splitext(config.os.path.basename(__file__))[0]

def getCommandInputValue(commandInput, unitType):
    try:
        valCommandInput = functions.adsk.core.ValueCommandInput.cast(commandInput)
        if not valCommandInput:
            return (False, 0)

        # Verify that the expression is valid.
        des = functions.adsk.fusion.Design.cast(functions.app.activeProduct)
        unitsMgr = des.unitsManager
        
        if unitsMgr.isValidExpression(valCommandInput.expression, unitType):
            value = unitsMgr.evaluateExpression(valCommandInput.expression, unitType)
            return (True, value)
        else:
            return (False, 0)
    except:
        if functions.ui:
            functions.ui.messageBox('Failed:\n{}'.format(functions.traceback.format_exc()), CMD_NAME)

class CommandCreatedHandler(functions.adsk.core.CommandCreatedEventHandler):    
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # functions.ui.messageBox('CommandCreatedHandler', CMD_NAME)
            # Read the cached values, if they exist.
            settings = None
            settingAttribute = functions.app.activeProduct.attributes.itemByName(CMD_NAME, 'settings')
            if settingAttribute is not None:
                jsonSettings = settingAttribute.value
                settings = json.loads(jsonSettings)              
                module        = settings['_module']
                numTeeth      = settings['_teeth']
                pressureAngle = settings['_pressure']
                backlash      = settings['_back']
                rootFilletRad = settings['_root']
                thickness     = settings['_thick']
                holeDiam      = settings['_hole']
            else:
                module        = data.defaultModule
                numTeeth      = data.defaultTeeth
                pressureAngle = data.defaultPressure
                backlash      = data.defaultBack
                rootFilletRad = data.defaultRoot
                thickness     = data.defaultThick
                holeDiam      = data.defaultHole

            cmd = args.command
            cmd.isRepeatable = False
         
            onValidateInputs = CommandValidateInputsHandler()
            onInputChanged   = CommandInputChangedHandler()
            # onExecutePreview = CommandExecuteHandler()
            onExecute        = CommandExecuteHandler()

            cmd.validateInputs.add(onValidateInputs)
            cmd.inputChanged.add(onInputChanged)
            # cmd.executePreview.add(onExecutePreview)
            cmd.execute.add(onExecute)

            functions.handlers.append(onInputChanged)     
            functions.handlers.append(onValidateInputs)
            # functions.handlers.append(onExecutePreview)
            functions.handlers.append(onExecute)

            global _pressureAngle, _diaPitch, _module, _numTeeth, _rootFilletRad, _thickness, _holeDiam, _pitchDiam, _backlash, _errMessage, _imgInput

            inputs = cmd.commandInputs

            diaPitch = 25.4 / module
            pitchDia = module * numTeeth

            # Define the command dialog.
            _imgInput = inputs.addImageCommandInput('gearImage', '', 'resources/kutjaraGear/Metric.png')
            _imgInput.isFullWidth = True

            _module = inputs.addValueInput('module', 'Module', '', functions.adsk.core.ValueInput.createByReal(module))   
                
            _numTeeth = inputs.addValueInput('numTeeth', 'Number of Teeth', '', functions.adsk.core.ValueInput.createByReal(numTeeth))        

            _pressureAngle = inputs.addDropDownCommandInput('pressureAngle', 'Pressure Angle', functions.adsk.core.DropDownStyles.TextListDropDownStyle)
            _pressureAngle.listItems.add('{} deg'.format(14.5), pressureAngle==14.5, '')
            _pressureAngle.listItems.add('{} deg'.format(20)  , pressureAngle==20  , '')
            _pressureAngle.listItems.add('{} deg'.format(25)  , pressureAngle==20  , '')

            _backlash = inputs.addValueInput('backlash', 'Backlash', 'mm', functions.adsk.core.ValueInput.createByReal(backlash))

            _rootFilletRad = inputs.addValueInput('rootFilletRad', 'Root Fillet Radius', 'mm', functions.adsk.core.ValueInput.createByReal(rootFilletRad))

            _thickness = inputs.addValueInput('thickness', 'Gear Thickness', 'mm', functions.adsk.core.ValueInput.createByReal(thickness))

            _holeDiam = inputs.addValueInput('holeDiam', 'Hole Diameter', 'mm', functions.adsk.core.ValueInput.createByReal(holeDiam))

            _diaPitch = inputs.addTextBoxCommandInput('diaPitch', 'Diametral Pitch', '{:.2f}'.format(diaPitch), 1, True) 
            _pitchDiam = inputs.addTextBoxCommandInput('pitchDiam', 'Pitch Diameter', '{:.2f} mm'.format(pitchDia), 1, True)
            _errMessage = inputs.addTextBoxCommandInput('errMessage', '', '', 2, True)
            _errMessage.isFullWidth = True
            
        except:
            if functions.ui:
                functions.ui.messageBox('Failed:\n{}'.format(functions.traceback.format_exc()), CMD_NAME)

# Event handler for the validateInputs event.
class CommandValidateInputsHandler(functions.adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = functions.adsk.core.ValidateInputsEventArgs.cast(args)
            
            _errMessage.text = ''

            # Verify that at lesat 4 teath are specified.
            if not _numTeeth.value.isdigit():
                _errMessage.text = 'The number of teeth must be a whole number.'
                eventArgs.areInputsValid = False
                return
            else:    
                numTeeth = int(_numTeeth.value)
            
            if numTeeth < 4:
                _errMessage.text = 'The number of teeth must be 4 or more.'
                eventArgs.areInputsValid = False
                return
                
            result = getCommandInputValue(_module, '')
            if result[0] == False:
                eventArgs.areInputsValid = False
                return
            else:
                diaPitch = 25.4 / result[1]

            diametralPitch = diaPitch / 2.54
            pitchDia = numTeeth / diametralPitch
            
            if (diametralPitch < (20 *(math.pi/180))-0.000001):
                dedendum = 1.157 / diametralPitch
            else:
                circularPitch = math.pi / diametralPitch
                if circularPitch >= 20:
                    dedendum = 1.25 / diametralPitch
                else:
                    dedendum = (1.2 / diametralPitch) + (.002 * 2.54)                

            rootDia = pitchDia - (2 * dedendum)        
                    
            if _pressureAngle.selectedItem.name == '14.5 deg':
                pressureAngle = 14.5 * (math.pi/180)
            elif _pressureAngle.selectedItem.name == '20 deg':
                pressureAngle = 20.0 * (math.pi/180)
            elif _pressureAngle.selectedItem.name == '25 deg':
                pressureAngle = 25.0 * (math.pi/180)
            baseCircleDia = pitchDia * math.cos(pressureAngle)
            baseCircleCircumference = 2 * math.pi * (baseCircleDia / 2) 

            des = functions.adsk.fusion.Design.cast(functions.app.activeProduct)

            result = getCommandInputValue(_holeDiam, 'mm')
            if result[0] == False:
                eventArgs.areInputsValid = False
                return
            else:
                holeDiam = result[1]
                           
            if holeDiam >= (rootDia - 0.01):
                _errMessage.text = 'The center hole diameter is too large.  It must be less than ' + des.unitsManager.formatInternalValue(rootDia - 0.01, 'mm', True)
                eventArgs.areInputsValid = False
                return

            toothThickness = baseCircleCircumference / (numTeeth * 2)
            if _rootFilletRad.value > toothThickness * .4:
                _errMessage.text = 'The root fillet radius is too large.  It must be less than ' + des.unitsManager.formatInternalValue(toothThickness * .4, 'mm', True)
                eventArgs.areInputsValid = False
                return
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
            
            if _module.value >0:
                diaPitch = 25.4 / _module.value
                _diaPitch.text = '{:.2f}'.format(diaPitch)
            else:
                _diaPitch.text = ''       
                _errMessage.text = 'Module must be greather than 0'             

            if _numTeeth.value.isdigit(): 
                numTeeth = int(_numTeeth.value)
                pitchDia = numTeeth * _module.value
                _pitchDiam.text = '{:.2f} mm'.format(pitchDia)
            else:
                _pitchDiam.text = ''       
                _errMessage.text = 'Number of Teeth must be a valid value'             

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
                if input.id == 'module':
                    thingToDraw.module = input.value

                elif input.id == 'numTeeth':
                    thingToDraw.teeth = input.value

                elif input.id == 'pressureAngle':
                    if input.selectedItem.name == '14.5 deg':
                        thingToDraw.pressure = 14.5 * (math.pi/180)
                    elif input.selectedItem.name == '20 deg':
                        thingToDraw.pressure = 20.0 * (math.pi/180)
                    else:
                        thingToDraw.pressure = 25.0 * (math.pi/180)

                elif input.id == 'backlash':
                    thingToDraw.backlash = input.value

                elif input.id == 'rootFilletRad':
                    thingToDraw.root = input.value

                elif input.id == 'thickness':
                    thingToDraw.thick = input.value

                elif input.id == 'holeDiam':
                    thingToDraw.hole = input.value

            thingToDraw.build()
            args.isValidResult = True

        except:
            if functions.ui:
                functions.ui.messageBox('Failed:\n{}'.format(functions.traceback.format_exc()), CMD_NAME)

class ThingToDraw :
    def __init__(self):
        self._module   = data.defaultModule
        self._teeth    = data.defaultTeeth
        self._pressure = data.defaultPressure
        self._backlash = data.defaultBack
        self._root     = data.defaultRoot
        self._thick    = data.defaultThick
        self._hole     = data.defaultHole

    #properties
    @property
    def module(self):
        return self._module
    @module.setter
    def module(self, value):
        self._module = value

    @property
    def teeth(self):
        return self._teeth
    @teeth.setter
    def teeth(self, value):
        self._teeth = value

    @property
    def pressure(self):
        return self._pressure
    @pressure.setter
    def pressure(self, value):
        self._pressure = value

    @property
    def backlash(self):
        return self._backlash
    @backlash.setter
    def backlash(self, value):
        self._backlash = value

    @property
    def root(self):
        return self._root
    @root.setter
    def root(self, value):
        self._root = value

    @property
    def thick(self):
        return self._thick
    @thick.setter
    def thick(self, value):
        self._thick = value

    @property
    def hole(self):
        return self._hole
    @hole.setter
    def hole(self, value):
        self._hole = value

    def build(self):

        def involutePoint(baseCircleRadius, distFromCenterToInvolutePoint):
            try:
                # Calculate the other side of the right-angle triangle defined by the base circle and the current distance radius.
                # This is also the length of the involute chord as it comes off of the base circle.
                triangleSide = math.sqrt(math.pow(distFromCenterToInvolutePoint,2) - math.pow(baseCircleRadius,2)) 
                
                # Calculate the angle of the involute.
                alpha = triangleSide / baseCircleRadius

                # Calculate the angle where the current involute point is.
                theta = alpha - math.acos(baseCircleRadius / distFromCenterToInvolutePoint)

                # Calculate the coordinates of the involute point.    
                x = distFromCenterToInvolutePoint * math.cos(theta)
                y = distFromCenterToInvolutePoint * math.sin(theta)

                # Create a point to return.        
                return functions.adsk.core.Point3D.create(x, y, 0)
            except:
                if functions.ui:
                    functions.ui.messageBox('Failed:\n{}'.format(functions.traceback.format_exc()), CMD_NAME)

        try:
            global newComp
            newComp = functions.createNewComponent()

            if newComp is None:
                functions.ui.messageBox('New component failed to create', CMD_NAME)
                return

            # Save the current values as attributes.
            settings = {
                            '_module'    : self.module,
                            '_teeth'     : self.teeth,
                            '_pressure'  : self.pressure,
                            '_back'      : self.backlash,
                            '_root'      : self.root,
                            '_thick'     : self.thick,
                            '_hole'      : self.hole,

                        }
            jsonSettings = json.dumps(settings)
            des = functions.adsk.fusion.Design.cast(functions.app.activeProduct)
            attribs = des.attributes
            attribs.add(CMD_NAME, 'settings', jsonSettings)
            
            newComp.name = 'Spur Gear (' + str(self.teeth) + ' teeth)'

            # Create a new sketch.
            xyPlane = newComp.xYConstructionPlane
            sketches = newComp.sketches
            sketch = sketches.add(xyPlane)

            diametralPitch = 10 / self.module
            pitchDia = self.teeth / diametralPitch
            
            #addendum = 1.0 / diametralPitch
            if (diametralPitch < (20 *(math.pi/180))-0.000001):
                dedendum = 1.157 / diametralPitch
            else:
                circularPitch = math.pi / diametralPitch
                if circularPitch >= 20:
                    dedendum = 1.25 / diametralPitch
                else:
                    dedendum = (1.2 / diametralPitch) + (.002 * 2.54)                

            rootDia = pitchDia - (2 * dedendum)
            
            baseCircleDia = pitchDia * math.cos(self.pressure)
            outsideDia = (self.teeth + 2) / diametralPitch
                        
            # Draw a circle for the base.
            sketch.sketchCurves.sketchCircles.addByCenterRadius(functions.adsk.core.Point3D.create(0,0,0), rootDia/2.0)
            
            # Draw a circle for the center hole, if the value is greater than 0.
            prof = functions.adsk.fusion.Profile.cast(None)
            if self.hole - (functions.app.pointTolerance * 2) > 0:
                sketch.sketchCurves.sketchCircles.addByCenterRadius(functions.adsk.core.Point3D.create(0,0,0), self.hole/2.0)

                # Find the profile that uses both circles.
                for prof in sketch.profiles:
                    if prof.profileLoops.count == 2:
                        break
            else:
                # Use the single profile.
                prof = sketch.profiles.item(0)
            
            extrudes = newComp.features.extrudeFeatures
            extInput = extrudes.createInput(prof, functions.adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            distance = functions.adsk.core.ValueInput.createByReal(self.thick)
            extInput.setDistanceExtent(False, distance)
            baseExtrude = extrudes.add(extInput)
            
            # Create a second sketch for the tooth.
            toothSketch = sketches.add(xyPlane)

            # Calculate points along the involute curve.
            involutePointCount = 15 
            involuteIntersectionRadius = baseCircleDia / 2.0
            involutePoints = []
            involuteSize = (outsideDia - baseCircleDia) / 2.0
            for i in range(0, involutePointCount):
                involuteIntersectionRadius = (baseCircleDia / 2.0) + ((involuteSize / (involutePointCount - 1)) * i)
                newPoint = involutePoint(baseCircleDia / 2.0, involuteIntersectionRadius)
                involutePoints.append(newPoint)
                
            # Get the point along the tooth that's at the pictch diameter and then
            # calculate the angle to that point.
            pitchInvolutePoint = involutePoint(baseCircleDia / 2.0, pitchDia / 2.0)
            pitchPointAngle = math.atan(pitchInvolutePoint.y / pitchInvolutePoint.x)

            # Determine the angle defined by the tooth thickness as measured at
            # the pitch diameter circle.
            toothThicknessAngle = (2 * math.pi) / (2 * self.teeth)
            
            # Determine the angle needed for the specified backlash.
            backlashAngle = (self.backlash / (pitchDia / 2.0)) * .25
            
            # Determine the angle to rotate the curve.
            rotateAngle = -((toothThicknessAngle/2) + pitchPointAngle - backlashAngle)
            
            # Rotate the involute so the middle of the tooth lies on the x axis.
            cosAngle = math.cos(rotateAngle)
            sinAngle = math.sin(rotateAngle)
            for i in range(0, involutePointCount):
                newX = involutePoints[i].x * cosAngle - involutePoints[i].y * sinAngle
                newY = involutePoints[i].x * sinAngle + involutePoints[i].y * cosAngle
                involutePoints[i] = functions.adsk.core.Point3D.create(newX, newY, 0)

            # Create a new set of points with a negated y.  This effectively mirrors the original
            # points about the X axis.
            involute2Points = []
            for i in range(0, involutePointCount):
                involute2Points.append(functions.adsk.core.Point3D.create(involutePoints[i].x, -involutePoints[i].y, 0))

            curve1Dist = []
            curve1Angle = []
            for i in range(0, involutePointCount):
                curve1Dist.append(math.sqrt(involutePoints[i].x * involutePoints[i].x + involutePoints[i].y * involutePoints[i].y))
                curve1Angle.append(math.atan(involutePoints[i].y / involutePoints[i].x))
            
            curve2Dist = []
            curve2Angle = []
            for i in range(0, involutePointCount):
                curve2Dist.append(math.sqrt(involute2Points[i].x * involute2Points[i].x + involute2Points[i].y * involute2Points[i].y))
                curve2Angle.append(math.atan(involute2Points[i].y / involute2Points[i].x))

            toothSketch.isComputeDeferred = True
            
            # Create and load an object collection with the points.
            pointSet = functions.adsk.core.ObjectCollection.create()
            for i in range(0, involutePointCount):
                pointSet.add(involutePoints[i])

            # Create the first spline.
            spline1 = toothSketch.sketchCurves.sketchFittedSplines.add(pointSet)

            # Add the involute points for the second spline to an ObjectCollection.
            pointSet = functions.adsk.core.ObjectCollection.create()
            for i in range(0, involutePointCount):
                pointSet.add(involute2Points[i])

            # Create the second spline.
            spline2 = toothSketch.sketchCurves.sketchFittedSplines.add(pointSet)

            # Draw the arc for the top of the tooth.
            midPoint = functions.adsk.core.Point3D.create((outsideDia / 2), 0, 0)
            toothSketch.sketchCurves.sketchArcs.addByThreePoints(spline1.endSketchPoint, midPoint, spline2.endSketchPoint)     

            # Check to see if involute goes down to the root or not.  If not, then
            # create lines to connect the involute to the root.
            if( baseCircleDia < rootDia ):
                toothSketch.sketchCurves.sketchLines.addByTwoPoints(spline2.startSketchPoint, spline1.startSketchPoint)
            else:
                rootPoint1 = functions.adsk.core.Point3D.create((rootDia / 2 - 0.001) * math.cos(curve1Angle[0] ), (rootDia / 2) * math.sin(curve1Angle[0]), 0)
                line1 = toothSketch.sketchCurves.sketchLines.addByTwoPoints(rootPoint1, spline1.startSketchPoint)

                rootPoint2 = functions.adsk.core.Point3D.create((rootDia / 2 - 0.001) * math.cos(curve2Angle[0]), (rootDia / 2) * math.sin(curve2Angle[0]), 0)
                line2 = toothSketch.sketchCurves.sketchLines.addByTwoPoints(rootPoint2, spline2.startSketchPoint)

                baseLine = toothSketch.sketchCurves.sketchLines.addByTwoPoints(line1.startSketchPoint, line2.startSketchPoint)

                # Make the lines tangent to the spline so the root fillet will behave correctly.            
                line1.isFixed = True
                line2.isFixed = True
                toothSketch.geometricConstraints.addTangent(spline1, line1)
                toothSketch.geometricConstraints.addTangent(spline2, line2)
        
            toothSketch.isComputeDeferred = False

            ### Extrude the tooth.
            
            # Get the profile defined by the tooth.
            prof = toothSketch.profiles.item(0)

            # Create an extrusion input to be able to define the input needed for an extrusion
            # while specifying the profile and that a new component is to be created
            extInput = extrudes.createInput(prof, functions.adsk.fusion.FeatureOperations.JoinFeatureOperation)

            # Define that the extent is a distance extent of 5 cm.
            distance = functions.adsk.core.ValueInput.createByReal(self.thick)
            extInput.setDistanceExtent(False, distance)

            # Create the extrusion.
            toothExtrude = extrudes.add(extInput)

            baseFillet = None
            if self.root > 0:
                ### Find the edges between the base cylinder and the tooth.
                
                # Get the outer cylindrical face from the base extrusion by checking the number
                # of edges and if it's 2 get the other one.
                cylFace = baseExtrude.sideFaces.item(0)
                if cylFace.edges.count == 2:
                    cylFace = baseExtrude.sideFaces.item(1)
        
                # Get the two linear edges, which are the connection between the cylinder and tooth.
                edges = functions.adsk.core.ObjectCollection.create()
                for edge in cylFace.edges:
                    if isinstance(edge.geometry, functions.adsk.core.Line3D):
                        edges.add(edge)
        
                # Create a fillet input to be able to define the input needed for a fillet.
                fillets = newComp.features.filletFeatures
                filletInput = fillets.createInput()
        
                # Define that the extent is a distance extent of 5 cm.
                radius = functions.adsk.core.ValueInput.createByReal(self.root)
                filletInput.addConstantRadiusEdgeSet(edges, radius, False)
        
                # Create the extrusion.
                baseFillet = fillets.add(filletInput)

            # Create a pattern of the tooth extrude and the base fillet.
            circularPatterns = newComp.features.circularPatternFeatures
            entities = functions.adsk.core.ObjectCollection.create()
            entities.add(toothExtrude)
            if baseFillet:
                entities.add(baseFillet)
            cylFace = baseExtrude.sideFaces.item(0)        
            patternInput = circularPatterns.createInput(entities, cylFace)
            numTeethInput = functions.adsk.core.ValueInput.createByString(str(self.teeth))
            patternInput.quantity = numTeethInput
            patternInput.patternComputeOption = functions.adsk.fusion.PatternComputeOptions.IdenticalPatternCompute        
            pattern = circularPatterns.add(patternInput)        
            
            # Create an extra sketch that contains a circle of the diametral pitch.
            diametralPitchSketch = sketches.add(xyPlane)
            diametralPitchCircle = diametralPitchSketch.sketchCurves.sketchCircles.addByCenterRadius(functions.adsk.core.Point3D.create(0,0,0), pitchDia/2.0)
            diametralPitchCircle.isConstruction = True
            diametralPitchCircle.isFixed = True

        except:
            if functions.ui:
                functions.ui.messageBox('Failed to compute the Gear. This is most likely because the input values define an invalid key.', CMD_NAME)
