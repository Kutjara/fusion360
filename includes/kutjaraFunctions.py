import adsk.core, adsk.fusion, adsk.cam, math

handlers = []
app = adsk.core.Application.get()
if app:
    ui = app.userInterface

product = app.activeProduct
design = adsk.fusion.Design.cast(product)

newComp = None

def createNewComponent(base = False):
    # Get the active design.
    if base:
        rootComp = design.rootComponent
    else:
        rootComp = design.activeComponent
    allOccs = rootComp.occurrences
    newOcc = allOccs.addNewComponent(adsk.core.Matrix3D.create())
    return newOcc.component

