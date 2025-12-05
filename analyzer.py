from hourglass2 import HourglassPlabicGraph

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

def analyzer(graph, use_notebook=True):
    global CURR_GRAPH, SERVER_ON
    CURR_GRAPH = graph
    _prepare_server()
    _start_server()
    _analyzer_thread(use_notebook)
    return CURR_GRAPH

def _analyzer_thread(use_notebook):
    """Run Eel thread for lifetime of app, checking for server status"""
    global SERVER_ON

    # print url
    if (use_notebook == False):
        print("App open @ http://localhost:{0}/draw_analyzer.html".format(PORT))

    # attempt to display app until get feedback from JS
    while SERVER_ON == False:
        if (use_notebook == True):
            clear_output(wait=True)
            iframe = IFrame(src="http://localhost:{0}/draw_analyzer.html".format(PORT),width=650,height=800)
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
        print("Analyzer closed.")

    # clear graph editor, wait for closing message
    #clear_output(wait=False)
    print("Analyzer closed.")


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


    def get_graph():
        return CURR_GRAPH.to_dict_analyzer()

    def get_trip(v_id, trip_idx):
        v = CURR_GRAPH._get_vertex(v_id)
        return CURR_GRAPH.get_trip(v, trip_idx, output='ids')

    def get_edge_trips(strand_id):
        for h in CURR_GRAPH._get_edges():
            for s in h.iterate_strands():
                if s.id == strand_id:
                    r = max(h.v_from().total_degree(),h.v_to().total_degree())
                    return [s.get_trip(i, output='ids') for i in range(1,r)]

        return []

    def get_planar_faces():
        """
        Generate all faces, including those created with boundary vertices.

        :return: list of faces, each face is a list of tuples, each of the form (id, x, y),
                and the index of the face in the returned list corresponds to the face's id
        """
        faces = []
        for face_id in sorted(CURR_GRAPH._faces.keys()):
            faces.append([(v.id, v.x, v.y) for v in CURR_GRAPH._faces[face_id].vertices()])
        return faces

    def cycle_face(face_id, inverse):
        print("CYCLING FACE", face_id, inverse)
        CURR_GRAPH.cycle_face(CURR_GRAPH.faces[face_id], inverse)
        return CURR_GRAPH.to_dict_analyzer()

    def square_move(face_id):
        print("Square move", face_id)
        CURR_GRAPH.square_move(CURR_GRAPH.faces[face_id])
        return CURR_GRAPH.to_dict_analyzer()

    def separation_labeling(face_id):
        print("separating labeling", face_id)
        rank = max(v.total_degree() for v in CURR_GRAPH.vertices.values() if v.is_interior_vertex)
        CURR_GRAPH.separation_labeling(CURR_GRAPH.faces[face_id], rank, check=False)
        return CURR_GRAPH.to_dict_analyzer()

    def tutte_layout():
        CURR_GRAPH.tutte_layout()
        return CURR_GRAPH.to_dict_analyzer()

    def lloyd_layout():
        CURR_GRAPH.lloyd_layout()
        return CURR_GRAPH.to_dict_analyzer()

    # return dict of functions
    return {
        'update_server_status': update_server_status,
        'get_graph': get_graph,
        'get_trip': get_trip,
        'get_edge_trips': get_edge_trips,
        'get_planar_faces': get_planar_faces,
        'cycle_face': cycle_face,
        'square_move': square_move,
        'separation_labeling': separation_labeling,
        'tutte_layout': tutte_layout,
        'lloyd_layout': lloyd_layout
    }
