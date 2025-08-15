_Namespace = 'EPICS'
_Columns = {1: {'justify': 'right', 'color': [220, 220, 220]}, 2: {'width': 90}, 3: {'width': 80, 'justify': 'right'}, 4: {'width': 60}, 5: {'width': 50, 'justify': 'right'}, 6: {'width': 60}}
_Rows = [
[{'localhost;9701:dev1:run': {'desc': 'Start/Stop/Exit', 'initial': ['Started'], 'features': 'RWE', 'widget': 'combo'}}, {'localhost;9701:server:debug': {'desc': 'Debugging level', 'initial': [0], 'features': 'RWE', 'widget': 'spinbox'}}],
[{'localhost;9701:dev1:frequency': {'desc': 'Update frequency of all counters', 'initial': [1.0], 'features': 'RWE', 'widget': 'spinbox'}}, {'localhost;9701:dev1:nPoints': {'desc': 'Number of points in the waveform', 'initial': [1000], 'features': 'RWE', 'widget': 'spinbox'}}],
[{'localhost;9701:dev1:cycle': {'desc': 'Cycle number', 'features': 'R'}}, {'localhost;9701:dev1:cycle': {'desc': 'Cycle number', 'features': 'R'}}],
[{'localhost;9701:dev1:clear': {'desc': 'Clear cerain parameters', 'initial': [None], 'features': 'WE', 'widget': 'button'}}, {'localhost;9701:dev1:clear': {'desc': 'Clear cerain parameters', 'initial': [None], 'features': 'WE', 'widget': 'button'}}],
]
