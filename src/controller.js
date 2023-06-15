/*
  *  Graph editor operates in several modes, depending on which button is active.
  *  Each mode has an activate and deactivate function, which are called when
  *  the corresponding button is clicked.
*/
var modes = {
  "move": {
    activate: activateMove,
    deactivate: deactivateMove
  },
  "place_filled": {
    activate: activateFilled,
    deactivate: deactivateFilled
  },
  "place_unfilled": {
    activate: activateUnfilled,
    deactivate: deactivateUnfilled
  },
  "toggle_color": {
    activate: activateToggle,
    deactivate: deactivateToggle
  },
  "place_edge": {
    activate: activateEdge,
    deactivate: deactivateEdge
  },
  "place_hourglass": {
    activate: activateHourglass,
    deactivate: deactivateEdge
  },
  "place_khourglass": {
    activate: activatekHourglass,
    deactivate: deactivateEdge
  },
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
};


/*
  *  Maintain state of app with global variables,
  *  one tracking active button, one tracking active mode, 
  *  and one tracking a selected element.
  *  Depending on action, update graph interface.
*/
var activeButton = false;
var activeMode = false;
var selectedElement = false;


// remove any vertices from selected class
function deselect() {
  d3.selectAll(selected).classed("selected", false);
  selected = [];
}


// button clicked, so activate corresponding mode
function activateButton(obj, mode) {
  // update active button
  if(activeButton) {
    activeButton.style.borderStyle = 'outset';
  }
  activeButton = obj;
  activeButton.style.borderStyle = 'inset';

  // update active mode, and deactive previous mode
  if(activeMode) {
    activeMode.deactivate();
  }
  activeMode = modes[mode];

  // call activate function for new mode
  activeMode.activate();
}


// init d3 object for drag events
var draggroup = d3.drag()
  .on("start", e => svg.style('cursor', 'grabbing'))
  .on("drag", function(e) {
    d3.selectAll(selected)
      .attr("cx", function(d) {
        d.x += x.invert(e.dx)-x.invert(0);
        return x(d.x);
      })
      .attr("cy", function(d) {
        d.y += y.invert(e.dy)-y.invert(0);
        return y(d.y);
      });
    update();
  })
  .on("end", e => svg.style('cursor', 'pointer'));

// init d3 object for stopping drag events
var nodrag = d3.drag()
  .on("drag", null);

// deselect on 'space' or 'enter' keypress
body.on("keypress", function(e) {
  if(e.keyCode === 32 || e.keyCode === 13){
    deselect();
  }
});


// move object
function activateMove(obj) {
  svg.style('cursor', 'pointer');
  activateObjects(".vertex");
  svg.selectAll(".vertex")
    .on("mousedown", function(e) {
      d3.select(this).classed("selected", !d3.select(this).classed("selected"));
      addOrRemove(selected, this);
    });
  svg.call(draggroup);
}

// finish moving object
function deactivateMove(obj) {
  svg.style('cursor', 'default');
  deselect();
  svg.selectAll(".vertex").on("mousedown", null);
  svg.call(nodrag);
  svg.on('mousedown.drag', null);
  deactivateAllObjects();
}


// add filled vertex on click
function activateFilled(obj) {
  mode = "place_filled";
  deselect();
  svg.on('click', addFilledVertex);
}

// finish adding filled vertices
function deactivateFilled(obj) {
  svg.on('click', null);
}

// add unfilled vertex on click
function activateUnfilled(obj) {
  mode = "place_unfilled";
  deselect();
  svg.on('click', addUnfilledVertex);
}

// finish adding unfilled vertices
function deactivateUnfilled(obj) {
  svg.on('click', null);
}

// change vertex color on click
function activateToggle(obj) {
  activateObjects(".vertex");
  svg.selectAll(".vertex")
    .on("click", function(e) {
      v = d3.select(this);
      if(v.datum().type == "filled") {
        v.datum().type = "unfilled";
      } else if (v.datum().type == "unfilled") {
        v.datum().type = "filled";
      }
      update();
    });
}

// finish changing vertex color
function deactivateToggle(obj) {
  svg.selectAll(".vertex").on("click", null);
}


// place object in "active" class
function activateObjects(selector) {
  svg.selectAll(selector).classed("active", true);
}

// remove object from "active" class
function deactivateAllObjects() {
  svg.selectAll("*").classed("active", false);
}

// init new vertex object
function newVertex(x, y, type) {
  return {x:x, y:y, id: ++maxVertexId, type:type};
}

// add vertex on click and update graph
function addVertex(e) {
  var vertexType = "filled";
  if (e.shiftKey) {
    vertexType = "unfilled"
  }
  data.vertices.push(newVertex(x.invert(e.offsetX), y.invert(e.offsetY), vertexType));
  update();
}

// add unfilled vertex on click and update graph
function addUnfilledVertex(e) {
  vertexType = "unfilled"
  data.vertices.push(newVertex(x.invert(e.offsetX), y.invert(e.offsetY), vertexType));
  update();
}

// add filled vertex on click and update graph
function addFilledVertex(e) {
  vertexType = "filled"
  data.vertices.push(newVertex(x.invert(e.offsetX), y.invert(e.offsetY), vertexType));
  update();
}

// create edge on click and update graph
function activateEdge(obj) {
  deselect();
  svg.selectAll(".vertex")
    .on("mousedown", function(e) {
      console.log("place_edge");
      d3.select(this).classed("selected", !d3.select(this).classed("selected"));
      addOrRemove(selected, this);
      if(selected.length == 2) {
        addEdge(1);
        deselect();
      }
    })
    .classed("active", true);
}

// TODO: may need to change to allow for different trip-types w/ hourglass edges
// create hourglass edges on click and update graph
function activateHourglass(obj) {
  deselect();
  svg.selectAll(".vertex")
    .on("mousedown", function(e) {
      console.log("place_edge");
      d3.select(this).classed("selected", !d3.select(this).classed("selected"));
      addOrRemove(selected, this);
      if(selected.length == 2) {
        addEdge(2);
        deselect();
      }
    })
    .classed("active", true);
}

// TODO: may need to change to allow for different trip-types w/ hourglass edges
// create k-hourglass edges on click and update graph
function activatekHourglass(obj) {
  deselect();
  svg.selectAll(".vertex")
    .on("mousedown", function(e) {
      console.log("place_edge");
      d3.select(this).classed("selected", !d3.select(this).classed("selected"));
      addOrRemove(selected, this);
      if(selected.length == 2) {
        var k = prompt("Enter degree",3);
        addEdge(k);
        deselect();
      }
    })
    .classed("active", true);
}

// finish creating edge
function deactivateEdge(obj) {
  svg.selectAll(".vertex").on("mousedown", null);
}


// ******** (Trip Permuation Functions) ********
function idStr(e) {
  return "("+e.multiEdge.source.id+"/"+e.multiEdge.target.id+")."+e.multiEdge.id+"."+e.heId;
}


// create edge path for Trip and update graph
function activateTrip(tripIndex) {
  activateObjects(".vertex");
  svg.selectAll(".vertex")
    .on("click", function(e) {
      edgePath = [];
      v = d3.select(this);
      var vertex = v.datum();
      var e0 = vertex.multiHalfEdges[0].halfEdges[0];
      var e = e0;
      console.log("start with",idStr(e));
      edgePath.push(JSON.stringify([e.multiEdge.edge.id, e.heId]));
      while(boundaryVertices.indexOf(e.multiEdge.target)==-1)
      {
          e = e.twin;
          console.log("switch to",idStr(e));
          if(e.multiEdge.source.type=="unfilled") {
            for(var i=0; i<tripIndex; i++) {
              console.log("HE ID:", e.heId, "OTHER:", e.multiEdge.halfEdges)
                e = e.prev;
                console.log("unfilled turn to", idStr(e));
            }
          } else {
            for(var i=0; i<tripIndex; i++) {
                e = e.next;
                console.log("filled turn to", idStr(e));
            }
          }
          edgePath.push(JSON.stringify([e.multiEdge.edge.id, e.heId]));
          update();
      }

    });
}

// helper functions to activate/deactivate trip types 1, 2, and 3
function activateTrip1(obj) {
  activateTrip(1);
}

function deactivateTrip1(obj) {
  svg.selectAll(".vertex").on("click", null);
}

function activateTrip2(obj) {
    activateTrip(2);
}

function deactivateTrip2(obj) {
  svg.selectAll(".vertex").on("click", null);
}

function activateTrip3(obj) {
  activateTrip(3);
}

function deactivateTrip3(obj) {
  svg.selectAll(".vertex").on("click", null);
}
