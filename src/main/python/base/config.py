
class Config:

    def __init__(self):

        # Files and folders in the "Flight" directory.
        # E.g. Flight01/.flight/meta.json
        self.flightDataFolder = '.flight/'
        self.flightMetaFile = '.flight/meta.json'
        self.flightDistributionFile = '.flight/distribution.json'

        # Files and folders in each transect directory
        self.markedImageFolder = '.marked/'
        self.markedDataFile = '.marked/data.transect'

        # Supported image types
        self.supportedImageExtensions = ('.JPG', '.jpg', '.JPEG', '.jpeg')

        # Drawing colors
        self.colors = [
            'Blue',
            'DarkGreen',
            'Teal',
            'Red',
            'Orange',
            'Magenta',
            'Black',
            'White',
        ]

        # Drawing widths
        self.drawingWidths = [
            10,
            20,
            30,
            40,
            50,
            60,
            70,
        ]
        self.defaultWidth = 40

        # Searchable animals
        self.searchableAnimals = [
            'Baboon',
            'Donkey',
            'Eland',
            'Elephant',
            'Gemsbok',
            'Giraffe',
            'Hartebeest',
            'Horse',
            'Human',
            'Impala',
            'Jackal',
            'Kudu',
            'Kudu',
            'Ostrich',
            'Oryx',
            'Rhino',
            'Springbok',
            'Steenbok',
            'Warthog',
            'Waterbuck',
            'Zebra',
        ]

config = Config()
