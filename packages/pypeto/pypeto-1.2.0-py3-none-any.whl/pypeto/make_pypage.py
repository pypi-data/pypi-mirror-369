import sys

class PyPage():
    pass
    #title = 'Page?'
    #namespace = 'ADO'
    #rows = [['make_pypage']]
    #columns = {}
    #page = (240,240,240)
    #def __init__(self, title):
        #PyPage.title = title
        #self.page = (240,240,240)
        #self.columns = {}
        #self.rows = [['make_pypage']]

def make_pypage(module):
    print(f'>make_pypage from {module.__name__}')
    pypage = PyPage()
    pypage.title = module.__name__
    pypage.namespace = module._Namespace
    #if pypage.namespace
    #pypage.columns = module._Columns
    pypage.rows = module._Rows
    return pypage

