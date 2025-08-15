#Saved pypet snapshot.
class PyPage():
    def __init__(self):
        self.namespace = "LITE"
        self.title = "snapshot"
        self.rows = [
[{'run': {}}, {'run': {'desc': 'Start/Stop/Exit', 'initial': ['Started'], 'features': 'RWE', 'widget': 'combo'}}, {'debug:': {}}, {'debug:': {'desc': 'Debugging level', 'initial': [0], 'features': 'RWE', 'widget': 'spinbox'}}],
[{'frequency': {}}, {'frequency': {'desc': 'Update frequency of all counters', 'initial': [1.0], 'features': 'RWE', 'widget': 'spinbox'}}, {'nPoints:': {}}, {'nPoints:': {'desc': 'Number of points in the waveform', 'initial': [1000], 'features': 'RWE', 'widget': 'spinbox'}}],
[{'cycle:': {}}, {'localhost;9701:dev1:cycle': {'desc': 'Cycle number', 'features': 'R'}}, {'cycleLocal:': {}}, {'localhost;9701:dev1:cycle': {'desc': 'Cycle number', 'features': 'R'}}],
[{' ': {}}, {' ': {'desc': 'Clear cerain parameters', 'initial': [None], 'features': 'WE', 'widget': 'button'}}, {' ': {}}, {' ': {'desc': 'Clear cerain parameters', 'initial': [None], 'features': 'WE', 'widget': 'button'}}],
]
