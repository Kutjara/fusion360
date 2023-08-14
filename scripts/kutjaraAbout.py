from .. import config

from ..includes import kutjaraFunctions as functions
from ..data import kutjaraAboutData as data

CMD_NAME = config.os.path.splitext(config.os.path.basename(__file__))[0]

class CommandCreatedHandler(functions.adsk.core.CommandCreatedEventHandler):    
    def __init__(self):
        super().__init__()        
    def notify(self, args):
        try:
            cmd = args.command
            cmd.isRepeatable = False

            texte = f'Name : {config.ADDIN_NAME}\nVersion : {config.ADDIN_VERSION}\nDate : {config.ADDIN_DATE}\nDescription : {config.ADDIN_DESC}'
            texte += '\n\n'
            for cle in config.AddInList.keys():
                texte += '{}\t{}\n'.format(cle, config.AddInList[cle])
            functions.ui.messageBox(texte, config.ADDIN_NAME)

        except:
            if functions.ui:
                functions.ui.messageBox('Failed:\n{}'.format(functions.traceback.format_exc()), data.CMD_NAME)
