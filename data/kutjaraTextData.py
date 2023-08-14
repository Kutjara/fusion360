import adsk.core

defaultTextFace      = None
defaultTextText      = 'Kutjara'
defaultTextAngle     = 0.0
defaultTextSize      = 1.0
defaultTextProf      = -0.1
defaultTextHAlign    = adsk.core.HorizontalAlignments.LeftHorizontalAlignment
defaultTextVAlign    = adsk.core.VerticalAlignments.MiddleVerticalAlignment
defaultTextHFlip     = False
defaultTextVFlip     = False
defaultTextBold      = 0
defaultTextItalic    = 0

def findMin(v1 ,v2):
    return v1 if v1<v2 else v2

def findMax(v1 ,v2):
    return v1 if v1>v2 else v2

