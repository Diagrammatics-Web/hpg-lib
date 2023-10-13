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
  "remove_edge": {
    activate: activateRemoveEdge,
    deactivate: deactivateRemoveEdge
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
  // if trip button
  if (mode.includes("trip")) {
    // if mode in trips, then remove
    if(trips.includes(mode)) {
      trips.splice(trips.indexOf(mode), 1);
      obj.style.borderStyle = '';
      modes[mode].deactivate();
    }
    // else add to trips
    else {
      trips.push(mode);
      obj.style.borderStyle = 'inset';
      modes[mode].activate();
    }
  }

  // if other type of button
  else {
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
}


// init d3 object for drag events
var draggroup = d3.drag()
  .on("start", (e) => {
    svg.style('cursor', 'grabbing');
  })
  .on("drag", function(e, d) {
    // select current vertex if not already selected
    let temporaryDrag = false;
    if (!d3.select(this).classed("selected")) {
      d3.select(this).classed("selected", true);
      addOrRemove(selected, this);
      addOrRemove(selectedIds, d.id);
      temporaryDrag = true;
    }

    // update position of selected vertices
    d3.selectAll(selected)
      .attr("cx", function(d) {
        d.x += x.invert(e.dx)-x.invert(0);
        return x(d.x);
      })
      .attr("cy", function(d) {
        d.y += y.invert(e.dy)-y.invert(0);
        return y(d.y);
      });

      // rerender
      update();
  })
  .on("end", e => {
    console.log(this);
    svg.style('cursor', 'pointer');
    d3.selectAll(selected)
      .attr("cx", function(d) {
        const snap_dist = 1;
        let dist = Math.sqrt(Math.pow(d.x,2) + Math.pow(d.y,2));

        // if withing epsilon of radius, snap to radius
        if (Math.abs(dist - radius) < snap_dist) {
          var angle = Math.atan2(d.y, d.x);
          d.x = radius * Math.cos(angle);
          d.y = radius * Math.sin(angle);
        }

        return x(d.x);
      })
      .attr("cy", function(d) {
        return y(d.y);
      });

      // save to backend and rerender
      /*eel.import_data(data_compressed())((d) => {
        data = d;
        preprocess_data();
        update();
      });*/
      update();
  });

// init d3 object for stopping drag events
var nodrag = d3.drag()
  .on("start", null)
  .on("drag", null)
  .on("end", null);

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
    .call(draggroup)
    .on("click", function(e, d) {
      d3.select(this).classed("selected", !d3.select(this).classed("selected"));
      addOrRemove(selected, this);
      addOrRemove(selectedIds, d.id);
    });
}

// finish moving object
function deactivateMove(obj) {
  svg.style('cursor', 'default');
  deactivateAllObjects();
  svg.selectAll(".vertex")
    .call(nodrag)
    .on("click", null)
    .on("mousedown.drag", null);

  deselect();
  console.log("deactivate move");
}

// toggle labels
function toggleLabels() {
  showLabels = !showLabels;
  update();
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
  activateObjects(".vertex"); // FIXME: is this necessary?
  svg.selectAll(".vertex")
    .on("click", function(e) {
      v = d3.select(this);
      /*if(v.datum().type == "filled") {
        v.datum().type = "unfilled";
      } else if (v.datum().type == "unfilled") {
        v.datum().type = "filled";
      }*/
      v.datum().filled = !v.datum().filled;
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
function newVertex(x, y, filled, boundary) {
  console.log("New vertex: " + x + ", " + y + ", " + (maxVertexId + 1));
  return {x:x, y:y, id: ++maxVertexId, filled:filled, boundary:boundary};
}

// add vertex on click and update graph
function addVertex(e) {
  var filled = true;
  if (e.shiftKey) {
    filled = false
  }
  data.vertices.push(newVertex(x.invert(e.offsetX), y.invert(e.offsetY), filled, false));

  // TODO: do only at end
  // save to backend
  /*eel.import_data(data_compressed())((d) => {
    data = d;
    preprocess_data();
    update();
  });*/
  update();
}

// add unfilled vertex on click and update graph
function addUnfilledVertex(e) {
  //vertexType = "unfilled"
  data.vertices.push(newVertex(x.invert(e.offsetX), y.invert(e.offsetY), false, false));

  // save to backend
  /*eel.import_data(data_compressed())((d) => {
    data = d;
    preprocess_data();
    update();
  });*/
  update();
}

// add filled vertex on click and update graph
function addFilledVertex(e) {
  //vertexType = "filled"
  data.vertices.push(newVertex(x.invert(e.offsetX), y.invert(e.offsetY), true, false));

  // save to backend
  /*eel.import_data(data_compressed())((d) => {
    data = d;
    preprocess_data();
    update();
  });*/
  update();
}

// create edge on click and update graph
function activateEdge(obj) {
  console.log("activateEdge", activeMode);
  deselect();
  svg.selectAll(".vertex")
    .on("mousedown", function(e) {
      console.log("place_edge");
      d3.select(this).classed("selected", !d3.select(this).classed("selected"));
      console.log(this);
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
      d3.select(this).classed("selected", !d3.select(this).classed("selected") && selected.length < 2);
      addOrRemove(selected, this);
      if(selected.length == 2) {
        let k = document.getElementById("btn-add_khourglass-val").value;
        if (k == "" || k <= 0) {
          document.getElementById("btn-add_khourglass-val").style.border = "2px solid red";
          deselect();
        }
        else {
          document.getElementById("btn-add_khourglass-val").style.border = "1px solid black";
        }

        addEdge(parseInt(k)); // pass in int
        deselect();
      }
    })
    .classed("active", true);
}

// finish creating edge
function deactivateEdge(obj) {
  svg.selectAll(".vertex").on("mousedown", null);
  document.getElementById("btn-add_khourglass-val").style.border = "1px solid black";
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



function activateRemoveEdge(obj) {
  console.log("activateRemoveEdge");
  deselect();
  svg.selectAll(".edge")
    .on("mousedown", function(e,d) {
        console.log(d);
        var index = data.edges.indexOf(d);
        data.edges.splice(index, 1);
        update();
        activateObjects(".edge");
    })
    .classed("active", true);
}

function deactivateRemoveEdge(obj) {
  svg.selectAll(".edge").on("mousedown", null);
}
