from HourglassClasses.hourglassplabicgraph import HourglassPlabicGraph

import eel
import importlib
from IPython.display import IFrame, display, clear_output

import datetime

PORT = 8000
EXPOSED_FNS = set()
SERVER_INIT = False
SERVER_STARTED = False # only ever updated by frontend
SERVER_ON = False
APP_DIR = 'src'
CURR_GRAPH = None

def editor(graph, use_notebook=True):
    global CURR_GRAPH, SERVER_ON
    CURR_GRAPH = graph
    _prepare_server()
    _start_server()
    _editor_thread(use_notebook)
    return CURR_GRAPH

def _editor_thread(use_notebook):
    """Run Eel thread for lifetime of app, checking for server status"""
    global SERVER_ON

    # print url
    if (use_notebook == False):
        print("App open @ http://localhost:{0}/draw_editor.html".format(PORT))

    # attempt to display app until get feedback from JS
    while SERVER_ON == False:
        if (use_notebook == True):
            clear_output(wait=True)
            iframe = IFrame(src="http://localhost:{0}/draw_editor.html".format(PORT),width=650,height=800)
            display(iframe)

        eel.sleep(0.5)

    # watch for server to end
    try:
        while SERVER_ON == True:
            eel.sleep(0.5)
    except (SystemExit, MemoryError, KeyboardInterrupt):
        print("** Always click \'Save/Finish\' to close app. **")
        SERVER_ON = False
        #clear_output(wait=False)
        print("Editor closed.")

    # clear graph editor, wait for closing message
    #clear_output(wait=False)
    print("Editor closed.")


##
## Server / Eel maintenance functions
##
def _prepare_server():
    """Initialize Eel server"""
    global SERVER_INIT
    global COMMENT

    if not SERVER_INIT:
        eel.init(APP_DIR)
        _expose_eel_fns()
        SERVER_INIT = True


def _start_server():
    """Start up or view Eel server"""
    global SERVER_INIT, SERVER_STARTED

    if not SERVER_STARTED:
        SERVER_STARTED = True
        eel.start('draw_editor.html', mode=None, port=PORT, block=False)
    else:
        eel.show()


def _expose_eel_fns():
    """expose functions for frontend calls"""
    eel_fns = _get_eel_fns()
    for name, fn in eel_fns.items():
        if name not in EXPOSED_FNS:
            eel.expose(fn)
            EXPOSED_FNS.add(name)


def _get_eel_fns():
    """Return dict of functions to be exposed to JS"""

    def update_server_status(state):
        global SERVER_ON
        SERVER_ON = state

    def print_from_js(data):
        print(data)

    def get_graph():
        return CURR_GRAPH.to_dict()

    def update_graph_from_editor(g):
        global CURR_GRAPH
        #print(g)
        #print("we close now! go home")
        #return [1,2,3,4]
        CURR_GRAPH = HourglassPlabicGraph.from_dict(g);
        #return CURR_GRAPH.to_dict()
        #CURR_GRAPH.prev_data = CURR_GRAPH._export_data()
        #CURR_GRAPH.data = data
        #CURR_GRAPH.boundary_vertices = []
        #CURR_GRAPH._prepare_data()

        # send updated copy of graph
        #return CURR_GRAPH._export_data()

    # return dict of functions
    return {
        'update_server_status': update_server_status,
        'print_from_js': print_from_js,
        'get_graph': get_graph,
        'update_graph_from_editor': update_graph_from_editor,
    }
