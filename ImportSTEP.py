import adsk.core, adsk.fusion, traceback

# Global variables
app = adsk.core.Application.get()
ui = app.userInterface
commandId = 'ImportStepLocalCommand'
commandName = 'Insert STEP'
commandDescription = 'Insert a STEP file into the current design.'
handlers = []

class ImportStepHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # 1. Open file picker
            fileDlg = ui.createFileDialog()
            fileDlg.isMultiSelectEnabled = False
            fileDlg.title = 'Select STEP File to Import'
            fileDlg.filter = 'STEP Files (*.stp *.step)'
            
            if fileDlg.showOpen() == adsk.core.DialogResults.DialogOK:
                selected_file = fileDlg.filename
                
                # 2. Perform Import
                importMgr = app.importManager
                stpOptions = importMgr.createSTEPImportOptions(selected_file)
                design = adsk.fusion.Design.cast(app.activeProduct)
                root = design.rootComponent
                
                # Keep track of components before import to identify the new one
                existing_count = root.occurrences.count
                importMgr.importToTarget(stpOptions, root)
                
                # 3. Handle Move Command
                if root.occurrences.count > existing_count:
                    new_component = root.occurrences.item(root.occurrences.count - 1)
                    
                    adsk.doEvents()

                    ui.activeSelections.clear()
                    ui.activeSelections.add(new_component)

                    ui.commandDefinitions.itemById('FusionMoveCommand').execute()
                        
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def run(context):
    try:
        cmdDef = ui.commandDefinitions.itemById(commandId)
        if not cmdDef:
            cmdDef = ui.commandDefinitions.addButtonDefinition(commandId, commandName, commandDescription, './resources')
        
        onCommandCreated = ImportStepHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)

        designWS = ui.workspaces.itemById('FusionSolidEnvironment')
        insertPanel = designWS.toolbarTabs.itemById('SolidTab').toolbarPanels.itemById('InsertPanel')
        insertPanel.controls.addCommand(cmdDef)
    except:
        if ui: ui.messageBox('Add-in Start Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    try:
        cmdDef = ui.commandDefinitions.itemById(commandId)
        if cmdDef: cmdDef.deleteMe()
        
        designWS = ui.workspaces.itemById('FusionSolidEnvironment')
        insertPanel = designWS.toolbarTabs.itemById('SolidTab').toolbarPanels.itemById('InsertPanel')
        control = insertPanel.controls.itemById(commandId)
        if control: control.deleteMe()
    except:
        pass
