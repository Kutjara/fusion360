defaultKeyName    = 'Key'
defaultKeyType    = 'KED'
defaultKeyShaft   = 0.6
defaultKeyLength  = 2.0

standardKeyType = {"KED", "KES", "KEG"}

standardKeySize = {
	"2"  : (0.8,0.2,0.2, 0.016),
	"3"  : (1.0,0.3,0.3, 0.016),
    "4"  : (1.2,0.4,0.4, 0.016),
	"5"  : (1.7,0.5,0.5, 0.025),
	"6"  : (2.2,0.6,0.6, 0.025),
	"8"  : (3.0,0.8,0.7, 0.025),
	"10" : (3.8,1.0,0.8, 0.040),
	"12" : (4.4,1.2,0.8, 0.040),
	"14" : (5.0,1.4,0.9, 0.040),
	"16" : (5.8,1.6,1.0, 0.060),
	"18" : (6.5,1.8,1.1, 0.060),
	"20" : (7.5,2.0,1.2, 0.060),
	"22" : (8.5,2.2,1.4, 0.100),
	"25" : (9.5,2.5,1.4, 0.100),
	"28" : (11.0,2.8,1.6, 0.100),
	"32" : (13.0,3.2,1.8, 0.100),
	"36" : (15.0,3.6,2.0, 0.160),
	"40" : (17.0,4.0,2.2, 0.160),
	"45" : (20.0,4.5,2.5, 0.160),
	"50" : (23.0,5.0,2.8, 0.160),
}
	
def findStandardKey(size) :
    keyChoice = "2"
    for cle, valeur in standardKeySize.items() :
        keyChoice = cle
        if size <= valeur[0] :
            break
    return standardKeySize[keyChoice]

