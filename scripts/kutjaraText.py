from .. import config
import json

from ..includes import kutjaraFunctions as functions
from ..data import kutjaraTextData as data

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
                settingText = settings['settingText']
                settingAngle = settings['_settingAngle']
                settingSize = settings['_settingSize']
                settingProf = settings['_settingProf']
                settingHAlign = settings['_settingHAlign']
                settingVAlign = settings['_settingVAlign']
                settingHFlip = settings['_settingHFlip']
                settingVFlip = settings['_settingVFlip']
                settingBold = settings['_settingBold']
                settingItalic = settings['_settingItalic']
            else:
                settingText = data.defaultTextText
                settingAngle = data.defaultTextAngle
                settingSize = data.defaultTextSize
                settingProf = data.defaultTextProf
                settingHAlign = data.defaultTextHAlign
                settingVAlign = data.defaultTextVAlign
                settingHFlip = data.defaultTextHFlip
                settingVFlip = data.defaultTextVFlip
                settingBold = data.defaultTextBold
                settingItalic = data.defaultTextItalic

            cmd = args.command
            cmd.isRepeatable = False

            onExecutePreview = ExecuteHandler()
            onExecute        = ExecuteHandler()

            cmd.executePreview.add(onExecutePreview)
            cmd.execute.add(onExecute)            

            functions.handlers.append(onExecutePreview)
            functions.handlers.append(onExecute)

            inputs = cmd.commandInputs

            selectionInput = inputs.addSelectionInput('_selection', 'Face', 'Selectionnez une face plane')
            selectionInput.setSelectionLimits(1,1)
            selectionInput.addSelectionFilter(functions.adsk.core.SelectionCommandInput.PlanarFaces)

            inputs.addStringValueInput('_text', 'Texte', settingText)

            initSizeInput = functions.adsk.core.ValueInput.createByReal(settingSize)
            inputs.addValueInput('_size', "Hauteur du texte",'mm',initSizeInput)

            initProfInput = functions.adsk.core.ValueInput.createByReal(settingProf)
            inputs.addValueInput('_prof', "Profondeur du texte",'mm',initProfInput)

            initAngleInput = functions.adsk.core.ValueInput.createByReal(settingAngle)
            inputs.addValueInput('_angle', "Angle",'deg',initAngleInput)

            inputFontStyle = inputs.addButtonRowCommandInput('_fontStyle', 'Style', True)
            listItems = inputFontStyle.listItems
            listItems.add('bold', settingBold != 0, './Resources/kutjaraText/Bold')
            listItems.add('italic', settingItalic != 0, './Resources/kutjaraText/Italic')

            inputHAlign = inputs.addButtonRowCommandInput('_horizontalAlign', 'Alignement Horizontal', False)
            listItems = inputHAlign.listItems
            listItems.add('left', False, './Resources/kutjaraText/Left')
            listItems.add('center', True, './Resources/kutjaraText/Center')
            listItems.add('right', False, './Resources/kutjaraText/Right')          

            inputVAlign = inputs.addButtonRowCommandInput('_verticalAlign', 'Alignement Vertical', False)
            listItems = inputVAlign.listItems
            listItems.add('top', False, './Resources/kutjaraText/Top')
            listItems.add('middle', True, './Resources/kutjaraText/Middle')
            listItems.add('bottom', False, './Resources/kutjaraText/Bottom')

            inputInvert = inputs.addButtonRowCommandInput('_invert', 'Inverser', True)
            listItems = inputInvert.listItems
            listItems.add('horizontal', settingHFlip != 0, './Resources/kutjaraText/Horizontal')
            listItems.add('vertical', settingVFlip != 0, './Resources/kutjaraText/Vertical')

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
                    thingToDraw.face = input.selection(0).entity

                elif input.id == '_text':
                    thingToDraw.text = input.value

                elif input.id == '_size':
                    thingToDraw.size = unitsMgr.evaluateExpression(input.expression, "mm")

                elif input.id == '_prof':
                    thingToDraw.prof = unitsMgr.evaluateExpression(input.expression, "mm")
                    
                elif input.id == '_angle':
                    thingToDraw.angle = unitsMgr.evaluateExpression(input.expression, "deg")

                elif input.id == '_fontStyle':
                    thingToDraw.bold      = 1 if input.listItems.item(0).isSelected else 0
                    thingToDraw.italic    = 2 if input.listItems.item(1).isSelected else 0

                elif input.id == '_horizontalAlign':
                    if input.selectedItem.name == 'left':
                        thingToDraw.hAlign = functions.adsk.core.HorizontalAlignments.LeftHorizontalAlignment
                    elif input.selectedItem.name == 'center':
                        thingToDraw.hAlign = functions.adsk.core.HorizontalAlignments.CenterHorizontalAlignment
                    elif input.selectedItem.name == 'right':
                        thingToDraw.hAlign = functions.adsk.core.HorizontalAlignments.RightHorizontalAlignment

                elif input.id == '_verticalAlign':
                    if input.selectedItem.name == 'top':
                        thingToDraw.vAlign = functions.adsk.core.VerticalAlignments.TopVerticalAlignment
                    elif input.selectedItem.name == 'middle':
                        thingToDraw.vAlign = functions.adsk.core.VerticalAlignments.MiddleVerticalAlignment
                    elif input.selectedItem.name == 'bottom':
                        thingToDraw.vAlign = functions.adsk.core.VerticalAlignments.BottomVerticalAlignment

                elif input.id == '_invert':
                    thingToDraw.hFlip = input.listItems.item(0).isSelected
                    thingToDraw.vFlip = input.listItems.item(1).isSelected

            thingToDraw.build()
            
        except:
            if functions.ui:
                functions.ui.messageBox('Failed:\n{}'.format(functions.traceback.format_exc()), CMD_NAME)

class ThingToDraw :
    def __init__(self):
        self._face   = data.defaultTextFace
        self._text   = data.defaultTextText
        self._angle  = data.defaultTextAngle
        self._size   = data.defaultTextSize
        self._prof   = data.defaultTextProf
        self._hAlign = data.defaultTextHAlign
        self._vAlign = data.defaultTextVAlign
        self._hFlip  = data.defaultTextHFlip
        self._vFlip  = data.defaultTextVFlip
        self._bold   = data.defaultTextBold
        self._italic = data.defaultTextItalic

    #properties
    @property
    def face(self):
        return self._face
    @face.setter
    def face(self, value):
        self._face = value

    @property
    def text(self):
        return self._text
    @text.setter
    def text(self, value):
        self._text = value

    @property
    def angle(self):
        return self._angle
    @angle.setter
    def angle(self, value):
        self._angle = value

    @property
    def size(self):
        return self._size
    @size.setter
    def size(self, value):
        self._size = value

    @property
    def prof(self):
        return self._prof
    @prof.setter
    def prof(self, value):
        self._prof = value

    @property
    def bold(self):
        return self._bold
    @bold.setter
    def bold(self, value):
        self._bold = value

    @property
    def italic(self):
        return self._italic
    @italic.setter
    def italic(self, value):
        self._italic = value

    @property
    def hAlign(self):
        return self._hAlign
    @hAlign.setter
    def hAlign(self, value):
        self._hAlign = value

    @property
    def vAlign(self):
        return self._vAlign
    @vAlign.setter
    def vAlign(self, value):
        self._vAlign = value

    @property
    def hFlip(self):
        return self._hFlip
    @hFlip.setter
    def hFlip(self, value):
        self._hFlip = value

    @property
    def vFlip(self):
        return self._vFlip
    @vFlip.setter
    def vFlip(self, value):
        self._vFlip = value

    def build(self):
        try:
            body      = self.face.body
            baseComp  = body.parentComponent
            sketches  = baseComp.sketches
            sketch    = sketches.add(self.face)
            txtSketch = sketch.sketchTexts

            # Save the current values as attributes.
            settings = {
                            'settingText': self.text,
                            '_settingAngle': self.angle,
                            '_settingSize': self.size,
                            '_settingProf': self.prof,
                            '_settingHAlign': self.hAlign,
                            '_settingVAlign': self.vAlign,
                            '_settingHFlip': self.hFlip,
                            '_settingVFlip': self.vFlip,
                            '_settingBold': self.bold,
                            '_settingItalic': self.italic,
                        }
            jsonSettings = json.dumps(settings)
            des = functions.adsk.fusion.Design.cast(functions.app.activeProduct)
            attribs = des.attributes
            attribs.add(CMD_NAME, 'settings', jsonSettings)

            # Projection de la face sur l'esquisse
            edges = functions.adsk.core.ObjectCollection.create()
            for edge in self.face.edges:
                edges.add(edge)
            projectedEntities = sketch.project(edges)

            # Recherche des points min et max
            minX = projectedEntities[0].boundingBox.minPoint.x
            minY = projectedEntities[0].boundingBox.minPoint.y
            maxX = projectedEntities[0].boundingBox.maxPoint.x
            maxY = projectedEntities[0].boundingBox.maxPoint.y
            for entitie in projectedEntities:
                minX = data.findMin(minX ,entitie.boundingBox.minPoint.x)
                minY = data.findMin(minY ,entitie.boundingBox.minPoint.y)
                maxX = data.findMax(maxX ,entitie.boundingBox.maxPoint.x)
                maxY = data.findMax(maxY ,entitie.boundingBox.maxPoint.y)

            # Création du texte dans l'esquisse
            cornerPoint = functions.adsk.core.Point3D.create(minX , minY, 0)
            diagonalPoint = functions.adsk.core.Point3D.create(maxX , maxY, 0)
            input = txtSketch.createInput2(self.text, self.size)
            input.textStyle = self.bold + self.italic
            input.angle = self.angle
            input.isHorizontalFlip = self.hFlip
            input.isVerticalFlip = self.vFlip
            input.setAsMultiLine(cornerPoint, diagonalPoint, self.hAlign, self.vAlign, 0)
            txt = txtSketch.add(input)

            # Extrusion du texte sur le corps
            extrude = baseComp.features.extrudeFeatures
            if self.prof<0:
                extrudeMode = functions.adsk.fusion.FeatureOperations.CutFeatureOperation
            else:
                extrudeMode = functions.adsk.fusion.FeatureOperations.JoinFeatureOperation
            txtExtrusion = extrude.createInput(txt, extrudeMode)
            txtExtrusion.setDistanceExtent(False, functions.adsk.core.ValueInput.createByReal(self.prof))
            txtExtrusion.participantBodies = [body]
            extrude.add(txtExtrusion)

        except:
            if functions.ui:
                functions.ui.messageBox('Failed to compute the text. This is most likely because the input values are invalid.', CMD_NAME)

