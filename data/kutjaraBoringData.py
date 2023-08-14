defaultBoringEdge = None
defaultBoringType = 'Fraisage'
defaultBoringSize = "M3"
defaultBoringTol  = 0.02

standardBoringTypes = (
    'Fraisage',
    'Lamage Vis CHC', 
    'Lamage Vis H',
    'Lamage Ecrou H Normal',
    'Lamage Ecrou H Bas',
    'Lamage Ecrou H Frein',
    'Lamage Ecrou H Borgne',
)

standardBoringDiameters = {
    "M3" : {
        "diametre"              : 0.30,
        "Fdiam"                 : 0.55,
        'Lamage Vis CHC'        : (0.55, 0.30),
        'Lamage Vis H'          : (0.55, 0.20),
        'Lamage Ecrou H Normal' : (0.55, 0.20),
        'Lamage Ecrou H Bas'    : (0.55, 0.20),
        'Lamage Ecrou H Frein'  : (0.55, 0.20),
        'Lamage Ecrou H Borgne' : (0.55, 0.20),
    },
    "M4" : {
        "diametre" : 0.40,
        "Fdiam"    : 0.75,
        'Lamage Vis CHC'        : (0.70, 0.40),
        'Lamage Vis H'          : (0.70, 0.28),
        'Lamage Ecrou H Normal' : (0.70, 0.28),
        'Lamage Ecrou H Bas'    : (0.70, 0.28),
        'Lamage Ecrou H Frein'  : (0.70, 0.28),
        'Lamage Ecrou H Borgne' : (0.70, 0.28),
    },
    "M5" : {
        "diametre" : 0.50,
        "Fdiam"    : 0.93,
        'Lamage Vis CHC'        : (0.85, 0.50),
        'Lamage Vis H'          : (0.80, 0.35),
        'Lamage Ecrou H Normal' : (0.80, 0.35),
        'Lamage Ecrou H Bas'    : (0.80, 0.35),
        'Lamage Ecrou H Frein'  : (0.80, 0.35),
        'Lamage Ecrou H Borgne' : (0.80, 0.35),
    },
    "M6" : {
        "diametre" : 0.60,
        "Fdiam"    : 1.13,
        'Lamage Vis CHC'        : (1.00, 0.60),
        'Lamage Vis H'          : (1.00, 0.40),
        'Lamage Ecrou H Normal' : (1.00, 0.40),
        'Lamage Ecrou H Bas'    : (1.00, 0.40),
        'Lamage Ecrou H Frein'  : (1.00, 0.40),
        'Lamage Ecrou H Borgne' : (1.00, 0.40),
    },
    "M8" : {
        "diametre" : 0.80,
        "Fdiam"    : 1.53,
        'Lamage Vis CHC'        : (1.30, 0.80),
        'Lamage Vis H'          : (1.30, 0.53),
        'Lamage Ecrou H Normal' : (1.30, 0.53),
        'Lamage Ecrou H Bas'    : (1.30, 0.53),
        'Lamage Ecrou H Frein'  : (1.30, 0.53),
        'Lamage Ecrou H Borgne' : (1.30, 0.53),
    },
    "M10" : {
        "diametre" : 1.00,
        "Fdiam"    : 1.90,
        'Lamage Vis CHC'        : (1.60, 1.00),
        'Lamage Vis H'          : (1.70, 0.64),
        'Lamage Ecrou H Normal' : (1.70, 0.64),
        'Lamage Ecrou H Bas'    : (1.70, 0.64),
        'Lamage Ecrou H Frein'  : (1.70, 0.64),
        'Lamage Ecrou H Borgne' : (1.70, 0.64),
    },
    "M12" : {
        "diametre" : 1.20,
        "Fdiam"    : 2.30,
        'Lamage Vis CHC'        : (1.80, 1.20),
        'Lamage Vis H'          : (1.90, 0.75),
        'Lamage Ecrou H Normal' : (1.90, 0.75),
        'Lamage Ecrou H Bas'    : (1.90, 0.75),
        'Lamage Ecrou H Frein'  : (1.90, 0.75),
        'Lamage Ecrou H Borgne' : (1.90, 0.75),
    },
}

