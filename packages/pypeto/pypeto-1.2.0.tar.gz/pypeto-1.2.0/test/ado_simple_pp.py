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
[_,f'{dev1}, angle:', dev1+'degM', 'sine(angle):', 
    {dev1+'sinM':{**color('light cyan'), 'desc': 'Sine of the angle', 'attr':'R',
      'format':'%.7f'}}],
[_,f'{dev2}, angle:', dev2+'angleM', 'sine(angle):', 
    {dev2+'sinM':color( 'light cyan')}],
#[_],
[GrayRow,{f'{dev3}, angle:':span(2,1)},_, dev3+'angleM', 'sine(angle):',
    {dev3+'sinM':{**color('cyan'),'desc':'Sine of the angle', 'format':'%.7f'}}],
[{'Updating period:':span(2,1)},'', dev3+'sleepS', {dev3+'sleepS':slider(0.01,5.01)}],
[{'Variable array of integers:':span(2,1)},_, dev3+'variableArrayM',
    ', fixed length:', dev3+'arrayOfDoubleS'],
[{'Slice[2:6] of the Variable array:':span(2,1)},_,dev3+'variableArrayM[2:6]',_,
    {dev3+'incrementC':{'text':'Increment'}}],
[{'Ramper':{**color('light green'),**just(1)}},
    'Ramping is', dev3+'rampS',_,_],
[{dev3+'rampM':{**span(1,2),**just(1),**color('light green'),
  'font':['Open Sans Extrabold',24]}},
  'Ramp to:', dev3+'rampGoalS',{dev3+'rampGoalS':slider(0,10)}],
[_, 'Ramp rate:', dev3+'rampRateS', {dev3+'rampRateS':slider(0.01,1.01)}],
['Check:',{dev3+'diagnosticMessageM':{**span(3,1),**just(0)}},_,_,_],
[GrayRow,'Status:',{dev3+'adoStatus':{**span(4,1)}}],
[{'Click one of these buttons:':span(2,1)},'', {'xterm':{'launch': 'xterm'}},
    {'pypet':{**span(1,2), 'launch':'pypet', **color(250,200,200),
    **font(18)}},
    {'ipython':{'launch':"xterm -e ipython3 -i -c'from cad_io.adoaccess import IORequest'", 
    **color(200,250,200), **span(1,2), **font(18)}}],
[_,_,{'About pypet':
    {'launch':'firefox https://github.com/ASukhanov/pypeto',
    **color(255,255,200)}}],
]
