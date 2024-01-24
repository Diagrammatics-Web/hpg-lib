function deactivateAllObjects() {
  svg.selectAll("*").classed("active", false);
}

function activateObjects(selector) {
  svg.selectAll(selector).classed("active", true);
}



var modes = {
  "trip1": {
    activate: activateTrip1,
    deactivate: deactivateTrip1
  },
  "trip2": {
    activate: activateTrip2,
    deactivate: deactivateTrip2
  },
  "trip3": {
    activate: activateTrip3,
    deactivate: deactivateTrip3
  },
  "edge_trips": {
    activate: activateEdgeTrips,
    deactivate: deactivateEdgeTrips
  },
  "cycle_face": {
    activate: activateCycleFace,
    deactivate: deactivateCycleFace,
  },
  "square_move": {
    activate: activateSquareMove,
    deactivate: deactivateSquareMove,
  },
  "separation_labeling": {
    activate: activateSeparationLabeling,
    deactivate: deactivateSeparationLabeling,
  },
};


/*
  *  Maintain state of app with global variables,
  *  one tracking active button, one tracking active mode,
  *  and one tracking a selected element.
  *  Depending on action, update graph interface.
*/
var activeButton = false;
var activeMode = false;
var moveMode = false;
var selectedElement = false;

// remove any vertices from selected class
function deselect() {
  d3.selectAll(selected).classed("selected", false);
  selected = [];
  selectedIds = [];
}


// button clicked, so activate corresponding mode
function activateButton(obj, mode) {

    // if same button clicked, then deselect
    if(activeButton == obj) {
      activeButton.style.borderStyle = '';
      activeButton = false;
      activeMode.deactivate();
      return;
    }

    // update active button only if not a trip button
    if(activeButton) {
      activeButton.style.borderStyle = '';
    }

    activeButton = obj;
    activeButton.style.borderStyle = 'inset';

    // update active mode, and deactive previous mode
    if(activeMode) {
      activeMode.deactivate();
    }
    activeMode = modes[mode];
    activeMode.activate();
}

// toggle labels
function toggleLabels() {
  showLabels = !showLabels;
  update();
}


// create edge path for Trip and update graph
function activateTrip(tripIndex) {
  activateObjects(".vertex"); // FIXME: is this necessary?
  svg.selectAll(".vertex")
    .on("click", async function(e) {
      v = d3.select(this);
      vertexId = v.datum().id;
      //edgePaths = [];
      // edgepath from python
      eel.get_trip(vertexId, tripIndex)((ep) => {
        // reset edgepaths for this trip type
        //edgePaths[tripIndex] = [];
        console.log(ep);
        edgePaths.push(ep);
        update();
        //activateObjects(".vertex");
        //for (var i = 0; i < ep.length; i++) {
          // add edge to edgePaths
      //    edgePaths[tripIndex].push(JSON.stringify(ep[i]));

          // render graph
        //  update();
        //}
      });

    });
}


function activateEdgeTrips(obj) {
  activateObjects(".edge"); // FIXME: is this necessary?
  svg.selectAll(".edge")
    .on("click", async function(e) {
      //edgePaths = [];
      edge = d3.select(this);
      edgeId = edge.datum().id;

      // edgepath from python
      eel.get_edge_trips(edgeId)((eps) => {
        // reset edgepaths for this trip type
        //edgePaths[tripIndex] = [];
        for(i=0; i<eps.length; i++) {
            edgePaths.push(eps[i]);
        }

        update();
        //activateObjects(".edge");
        //for (var i = 0; i < ep.length; i++) {
          // add edge to edgePaths
      //    edgePaths[tripIndex].push(JSON.stringify(ep[i]));

          // render graph
        //  update();
        //}
      });

    });
}

function deactivateEdgeTrips(obj) {
  svg.selectAll(".edge").on("click", null);
  deactivateAllObjects();
  update();

}

// helper functions to activate/deactivate trip types 1, 2, and 3
function activateTrip1(obj) {
  activateTrip(1);
}

function deactivateTrip1(obj) {
  svg.selectAll(".vertex").on("click", null);
  deactivateAllObjects();
  update();
}

function activateTrip2(obj) {;
  activateTrip(2);
}

function deactivateTrip2(obj) {
  svg.selectAll(".vertex").on("click", null);
  deactivateAllObjects();
  update();
}

function activateTrip3(obj) {
  activateTrip(3);
}

function deactivateTrip3(obj) {
  svg.selectAll(".vertex").on("click", null);
  deactivateAllObjects();
  update();
}

function cycleFace(face_id, inverse) {
  // call backend fn and update graph
  console.log("Cycling face");
  console.log(face_id);
  console.log(inverse);
  eel.cycle_face(face_id, inverse)((d) => {
    // check if error
    if (typeof(d) == "string") {
      console.log(d);
      return;
    }

    data = d;
    preprocess_data();
    update();
  });
}

function activateCycleFace(obj) {
  activateObjects(".face");
  svg.selectAll(".face")
    .on("click", (e, d) => {
      cycleFace(d.id, e.shiftKey);
      update();
      ///activateObjects(".face");
  });
}

function deactivateCycleFace(obj) {
  deactivateAllObjects();
  svg.selectAll(".face").on("click", null);
}


function squareMove(face_id) {
  // call backend fn and update graph
  console.log("Square move");
  console.log(face_id);
  eel.square_move(face_id)((d) => {
    // check if error
    if (typeof(d) == "string") {
      console.log(d);
      return;
    }

    data = d;
    preprocess_data();
    update();
    //activateObjects(".face");
  });
}

function activateSquareMove(obj) {
  activateObjects(".face");
  svg.selectAll(".face")
    .on("click", (e, d) => {
      squareMove(d.id);
      update();
      //activateObjects(".face");
  });
}

function deactivateSquareMove(obj) {
  deactivateAllObjects();
  svg.selectAll(".face").on("click", null);
}




function calculateSeparationLabeling(face_id) {
  // call backend fn and update graph
  console.log("separation labeling");
  console.log(face_id);
  eel.separation_labeling(face_id)((d) => {
    // check if error
    if (typeof(d) == "string") {
      console.log(d);
      return;
    }
    showEdgeLabels = true;
    data = d;
    preprocess_data();
    update();
    //activateObjects(".face");
  });
}

function activateSeparationLabeling(obj) {
  activateObjects(".face");
  svg.selectAll(".face")
    .on("click", (e, d) => {
      calculateSeparationLabeling(d.id);
      update();
      //activateObjects(".face");
  });
}

function deactivateSeparationLabeling(obj) {
  deactivateAllObjects();
  svg.selectAll(".face").on("click", null);
}


// helper fn: add value if missing, remove if present
function addOrRemove(array, value) {
  var index = array.indexOf(value);
  if (index === -1) {
      array.push(value);
  } else {
      array.splice(index, 1);
  }
}
