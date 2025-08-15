"""Control page for ADO am_simple.
"""
__version__='v3.0.0 2025-05-09'# 

#```````````````````Definitions```````````````````````````````````````````````
# Python expressions and functions, used in the PyPage.
dev1 = 'simple.test:'
dev2 = 'am_simple.test:'
dev3 = 'am_simple.0:'
_=' '
def span(x,y): return {'span':[x,y]}
def color(*v): return {'color':v[0]} if len(v)==1 else {'color':list(v)}
def slider(minValue,maxValue):
    """Definition of the GUI element: horizontal slider with flexible range"""
    return {'widget':'hslider','opLimits':[minValue,maxValue],'span':[2,1]}
def font(size): return {'font':['Arial',size]}
def just(i): return {'justify':{0:'left',1:'center',2:'right'}[i]}

LargeFont = {'color':'light gray', **font(18), 'fgColor':'dark green'}
# Attributes for gray row, it should be in the first cell:
GrayRow = {'ATTRIBUTES':{'color':'light gray', **font(12)}}

#``````````````````PyPage Object``````````````````````````````````````````````
class PyPage():
    def __init__(self, instance=None, title=None):
        """instance: unique name of the page.
        For single-device page it is commonly device name or host;port.
        title: is used for name of the tab in the GUI. 
        """
        print(f'Instantiating Page {instance,title}')
        hostPort = instance
        dev = f"{hostPort}:dev1:"
        localDev = 'localhost;9701:dev1:'
        print(f'Controlling device {dev}')
        server = f"{hostPort}:server:"
        pvplot = f"python3 -m pvplot -a L:{dev} x,y"

        #``````````Mandatory class members starts here````````````````````````
        self.namespace = 'ADO'
        self.title = f'am_simple' if title is None else title

        #``````````Page attributes, optional`````````````````````````
        #self.page = color(252,252,237)
        self.page = {**color(240,240,240)}
        #self.page['editable'] = False

        #``````````Definition of columns`````````````````````````````
        self.columns = {
            1: {'width': 100, 'justify': 'right'},
            2: {'width': 100, **just(2)}, #same thing using just()
            3: {'width': 100},
            #4: {width: 20},
            5: {'width': 100, **font(12)},
        }

        #``````````Definition of rows````````````````````````````````
        self.rows = [
[{'':{'embed':'xclock -bg cyan',**span(1,5)}},
    {f'Control of {dev1}, {dev2}, {dev3}':{**span(4,3),
    **LargeFont, 'justify':'center'}}],
[],
[],
[],
[],
]
