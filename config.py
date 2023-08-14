import os

DEBUG = True

ADDIN_NAME    = os.path.basename(os.path.dirname(__file__))
ADDIN_VERSION = "1.50.10"
ADDIN_DATE    = "06/08/2023"
ADDIN_DESC    = "Ensemble de scripts pour la création automatique de composants mécaniques"
COMPANY_NAME  = "KUTJARA"

AddInList = {
    "About"     : "A Propos de ...",
    "Bearing"   : "Dessin de roulements standards",
    "Gear"      : "Dessin d'engrenage'",
    "Nut"       : "Dessin d'écrous standard",
    "Bolt"      : "Dessin de vis standard",
    "Boring"    : "Dessin de lamages",
    "Handles"   : "Dessin de poignées",
    "Key"       : "Dessin de clavettes standard",
    "Spacer"    : "Dessin d'entretoises",
    "Text"      : "Dessin de texte en relief",
    "Washer"    : "Dessin de rondelles standard",
    "CupWasher" : "Dessin de rondelles cuvette standard",
    "Standoff"  : "Dessin d'entretoises filetées",
}
