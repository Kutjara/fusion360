from . import config as config

from .includes import kutjaraFunctions as kutjaraFunctions

from .scripts import kutjaraAbout as kutjaraAbout
from .scripts import kutjaraBearing as kutjaraBearing
from .scripts import kutjaraGear as kutjaraGear
from .scripts import kutjaraBolt as kutjaraBolt
from .scripts import kutjaraBoring as kutjaraBoring
from .scripts import kutjaraCupWasher as kutjaraCupWasher
from .scripts import kutjaraHandles as kutjaraHandles
from .scripts import kutjaraKey as kutjaraKey
from .scripts import kutjaraNut as kutjaraNut
from .scripts import kutjaraSpacer as kutjaraSpacer
from .scripts import kutjaraText as kutjaraText
from .scripts import kutjaraWasher as kutjaraWasher
from .scripts import kutjaraStandoff as kutjaraStandoff

def run(context):
    ui = None
    try:
        app = kutjaraFunctions.adsk.core.Application.get()
        ui  = app.userInterface

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions
        
        # Create a button command definition.
        kutjaraAboutButton = cmdDefs.addButtonDefinition('KutjaraAboutButtonId', 
                                                   'KutjaraAbout', 
                                                   '{}'.format(config.AddInList['About']),
                                                   './Resources/kutjaraAbout')
        
        kutjaraBearingButton = cmdDefs.addButtonDefinition('KutjaraBearingButtonId', 
                                                   'KutjaraBearing', 
                                                   '{}'.format(config.AddInList['Bearing']),
                                                   './Resources/kutjaraBearing')
        
        kutjaraGearButton = cmdDefs.addButtonDefinition('KutjaraGearButtonId', 
                                                   'KutjaraGear', 
                                                   '{}'.format(config.AddInList['Gear']),
                                                   './Resources/kutjaraGear')

        kutjaraNutButton = cmdDefs.addButtonDefinition('kutjaraNutButtonId', 
                                                   'KutjaraNut', 
                                                   '{}'.format(config.AddInList['Nut']),
                                                   './Resources/kutjaraNut')
        
        kutjaraBotlButton = cmdDefs.addButtonDefinition('KutjaraBoltButtonId', 
                                                   'KutjaraBolt', 
                                                   '{}'.format(config.AddInList['Bolt']),
                                                   './Resources/kutjaraBolt')
        
        kutjaraBoringButton = cmdDefs.addButtonDefinition('KutjaraBoringButtonId', 
                                                   'KutjaraBoring', 
                                                   '{}'.format(config.AddInList['Boring']),
                                                   './Resources/kutjaraBoring')
        
        kutjaraHandlesButton = cmdDefs.addButtonDefinition('kutjaraHandlesButtonId', 
                                                   'KutjaraHandles', 
                                                   '{}'.format(config.AddInList['Handles']),
                                                   './Resources/kutjaraHandles')
        
        kutjaraKeyButton = cmdDefs.addButtonDefinition('kutjaraKeyButtonId', 
                                                   'KutjaraKey', 
                                                   '{}'.format(config.AddInList['Key']),
                                                   './Resources/kutjaraKey')
        
        kutjaraSpacerButton = cmdDefs.addButtonDefinition('kutjaraSpacerButtonId', 
                                                   'KutjaraSpacer', 
                                                   '{}'.format(config.AddInList['Spacer']),
                                                   './Resources/kutjaraSpacer')
        
        kutjaraTextButton = cmdDefs.addButtonDefinition('kutjaraTextButtonId', 
                                                   'KutjaraText', 
                                                   '{}'.format(config.AddInList['Text']),
                                                   './Resources/kutjaraText')
        
        kutjaraWasherButton = cmdDefs.addButtonDefinition('kutjaraWasherButtonId', 
                                                   'KutjaraWasher', 
                                                   '{}'.format(config.AddInList['Washer']),
                                                   './Resources/kutjaraWasher')
        
        kutjaraCupWasherButton = cmdDefs.addButtonDefinition('kutjaraCupWasherButtonId', 
                                                   'KutjaraCupWasher', 
                                                   '{}'.format(config.AddInList['CupWasher']),
                                                   './Resources/kutjaraCupWasher')
        
        kutjaraStandoffButton = cmdDefs.addButtonDefinition('kutjaraStandoffButtonId', 
                                                   'kutjaraStandoff', 
                                                   '{}'.format(config.AddInList['Standoff']),
                                                   './Resources/kutjaraStandoff')
        
        # Connect to the command created event.
        aboutCommandCreated = kutjaraAbout.CommandCreatedHandler()
        kutjaraAboutButton.commandCreated.add(aboutCommandCreated)
        kutjaraFunctions.handlers.append(aboutCommandCreated)
        
        bearingCommandCreated = kutjaraBearing.CommandCreatedHandler()
        kutjaraBearingButton.commandCreated.add(bearingCommandCreated)
        kutjaraFunctions.handlers.append(bearingCommandCreated)
        
        gearCommandCreated = kutjaraGear.CommandCreatedHandler()
        kutjaraGearButton.commandCreated.add(gearCommandCreated)
        kutjaraFunctions.handlers.append(gearCommandCreated)
        
        boltCommandCreated = kutjaraBolt.CommandCreatedHandler()
        kutjaraBotlButton.commandCreated.add(boltCommandCreated)
        kutjaraFunctions.handlers.append(boltCommandCreated)
        
        nutCommandCreated = kutjaraNut.CommandCreatedHandler()
        kutjaraNutButton.commandCreated.add(nutCommandCreated)
        kutjaraFunctions.handlers.append(nutCommandCreated)
        
        boringCommandCreated = kutjaraBoring.CommandCreatedHandler()
        kutjaraBoringButton.commandCreated.add(boringCommandCreated)
        kutjaraFunctions.handlers.append(boringCommandCreated)
        
        handlesCommandCreated = kutjaraHandles.CommandCreatedHandler()
        kutjaraHandlesButton.commandCreated.add(handlesCommandCreated)
        kutjaraFunctions.handlers.append(handlesCommandCreated)
        
        keyCommandCreated = kutjaraKey.CommandCreatedHandler()
        kutjaraKeyButton.commandCreated.add(keyCommandCreated)
        kutjaraFunctions.handlers.append(keyCommandCreated)
        
        spacerCommandCreated = kutjaraSpacer.CommandCreatedHandler()
        kutjaraSpacerButton.commandCreated.add(spacerCommandCreated)
        kutjaraFunctions.handlers.append(spacerCommandCreated)
        
        textCommandCreated = kutjaraText.CommandCreatedHandler()
        kutjaraTextButton.commandCreated.add(textCommandCreated)
        kutjaraFunctions.handlers.append(textCommandCreated)
        
        washerCommandCreated = kutjaraWasher.CommandCreatedHandler()
        kutjaraWasherButton.commandCreated.add(washerCommandCreated)
        kutjaraFunctions.handlers.append(washerCommandCreated)
        
        cupWasherCommandCreated = kutjaraCupWasher.CommandCreatedHandler()
        kutjaraCupWasherButton.commandCreated.add(cupWasherCommandCreated)
        kutjaraFunctions.handlers.append(cupWasherCommandCreated)
        
        standoffCommandCreated = kutjaraStandoff.CommandCreatedHandler()
        kutjaraStandoffButton.commandCreated.add(standoffCommandCreated)
        kutjaraFunctions.handlers.append(standoffCommandCreated)
        
        # Get the "DESIGN" workspace. 
        designWS = ui.workspaces.itemById('FusionSolidEnvironment')

        # Get the "TOOLS" toolbartabs
        toolsTab = designWS.toolbarTabs.itemById('SolidTab')

        # Create "KUTJARA" panel
        kutjaraPanel = ui.allToolbarPanels.itemById('KutjaraPanelId')
        if not kutjaraPanel:
            kutjaraPanel = toolsTab.toolbarPanels.add('KutjaraPanelId','Kutjara')
 
        # Add the button to the bottom of the panel.
        kutjaraPanel.controls.addCommand(kutjaraAboutButton)
        kutjaraPanel.controls.addCommand(kutjaraBearingButton)
        kutjaraPanel.controls.addCommand(kutjaraGearButton)
        kutjaraPanel.controls.addCommand(kutjaraNutButton)
        kutjaraPanel.controls.addCommand(kutjaraBotlButton)
        kutjaraPanel.controls.addCommand(kutjaraBoringButton)
        kutjaraPanel.controls.addCommand(kutjaraHandlesButton)
        kutjaraPanel.controls.addCommand(kutjaraKeyButton)
        kutjaraPanel.controls.addCommand(kutjaraSpacerButton)
        kutjaraPanel.controls.addCommand(kutjaraTextButton)
        kutjaraPanel.controls.addCommand(kutjaraWasherButton)
        kutjaraPanel.controls.addCommand(kutjaraCupWasherButton)
        kutjaraPanel.controls.addCommand(kutjaraStandoffButton)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(kutjaraFunctions.traceback.format_exc()))

def stop(context):
    try:
        app = kutjaraFunctions.adsk.core.Application.get()
        ui  = app.userInterface
        
        # Clean up the UI.
        cmdDef = ui.commandDefinitions.itemById('KutjaraAboutButtonId')
        if cmdDef:
            cmdDef.deleteMe()
        cmdDef = ui.commandDefinitions.itemById('KutjaraBoltButtonId')
        if cmdDef:
            cmdDef.deleteMe()
        cmdDef = ui.commandDefinitions.itemById('KutjaraBoringButtonId')
        if cmdDef:
            cmdDef.deleteMe()
        cmdDef = ui.commandDefinitions.itemById('KutjaraBearingButtonId')
        if cmdDef:
            cmdDef.deleteMe()
        cmdDef = ui.commandDefinitions.itemById('KutjaraGearButtonId')
        if cmdDef:
            cmdDef.deleteMe()
        cmdDef = ui.commandDefinitions.itemById('kutjaraCupWasherButtonId')
        if cmdDef:
            cmdDef.deleteMe()
        cmdDef = ui.commandDefinitions.itemById('kutjaraHandlesButtonId')
        if cmdDef:
            cmdDef.deleteMe()
        cmdDef = ui.commandDefinitions.itemById('kutjaraKeyButtonId')
        if cmdDef:
            cmdDef.deleteMe()
        cmdDef = ui.commandDefinitions.itemById('kutjaraNutButtonId')
        if cmdDef:
            cmdDef.deleteMe()
        cmdDef = ui.commandDefinitions.itemById('kutjaraSpacerButtonId')
        if cmdDef:
            cmdDef.deleteMe()
        cmdDef = ui.commandDefinitions.itemById('kutjaraTextButtonId')
        if cmdDef:
            cmdDef.deleteMe()
        cmdDef = ui.commandDefinitions.itemById('kutjaraWasherButtonId')
        if cmdDef:
            cmdDef.deleteMe()
        cmdDef = ui.commandDefinitions.itemById('kutjaraStandoffButtonId')
        if cmdDef:
            cmdDef.deleteMe()

        kutjaraPanel = ui.allToolbarPanels.itemById('KutjaraPanelId')
        cntrl = kutjaraPanel.controls.itemById('KutjaraAboutButtonId')
        if cntrl:
            cntrl.deleteMe()
        cntrl = kutjaraPanel.controls.itemById('KutjaraBoltButtonId')
        if cntrl:
            cntrl.deleteMe()
        cntrl = kutjaraPanel.controls.itemById('KutjaraBoringButtonId')
        if cntrl:
            cntrl.deleteMe()
        cntrl = kutjaraPanel.controls.itemById('KutjaraBearingButtonId')
        if cntrl:
            cntrl.deleteMe()
        cntrl = kutjaraPanel.controls.itemById('KutjaraGearButtonId')
        if cntrl:
            cntrl.deleteMe()
        cntrl = kutjaraPanel.controls.itemById('kutjaraCupWasherButtonId')
        if cntrl:
            cntrl.deleteMe()
        cntrl = kutjaraPanel.controls.itemById('kutjaraHandlesButtonId')
        if cntrl:
            cntrl.deleteMe()
        cntrl = kutjaraPanel.controls.itemById('kutjaraKeyButtonId')
        if cntrl:
            cntrl.deleteMe()
        cntrl = kutjaraPanel.controls.itemById('kutjaraNutButtonId')
        if cntrl:
            cntrl.deleteMe()
        cntrl = kutjaraPanel.controls.itemById('kutjaraSpacerButtonId')
        if cntrl:
            cntrl.deleteMe()
        cntrl = kutjaraPanel.controls.itemById('kutjaraTextButtonId')
        if cntrl:
            cntrl.deleteMe()
        cntrl = kutjaraPanel.controls.itemById('kutjaraWasherButtonId')
        if cntrl:
            cntrl.deleteMe()
        cntrl = kutjaraPanel.controls.itemById('kutjaraStandoffButtonId')
        if cntrl:
            cntrl.deleteMe()

        if kutjaraPanel:
            kutjaraPanel.deleteMe
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(kutjaraFunctions.traceback.format_exc()))	
