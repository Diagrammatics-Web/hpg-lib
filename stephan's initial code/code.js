var modes = {
  "select": {
    activate: activateSelect,
    deactivate: deactivateSelect
  },
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
};

var activeButton = false;
var activeMode = false;

var selectedElement = false;

function deselect() {
  d3.selectAll(selected).classed("selected", false);
  selected = [];
}

function activateButton(obj, mode) {
  if(activeButton) {
    activeButton.style.borderStyle = 'outset';
  }
  activeButton = obj;
  activeButton.style.borderStyle = 'inset';
  if(activeMode) {
    activeMode.deactivate();
  }
  activeMode = modes[mode];
  activeMode.activate();
}

function activateSelect(obj) {
  mode = "select";
}

function deactivateSelect(obj) {
  //deactivateAllObjects();
  //svg.selectAll(".vertex").on("mousedown", null);
  //body.on("keypress", null);
}

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

body.on("keypress", function(e) {
  if(e.keyCode === 32 || e.keyCode === 13){
    deselect();
  }
});
var nodrag = d3.drag()
  //.on("dragstart", null)
  .on("drag", null);
  //.on("dragend", null);

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

function deactivateMove(obj) {
  svg.style('cursor', 'default');
  deselect();
  svg.selectAll(".vertex").on("mousedown", null);
  svg.call(nodrag);
  svg.on('mousedown.drag', null);
  deactivateAllObjects();
}


function activateFilled(obj) {
  mode = "place_filled";
  deselect();
  //boundary_circle.classed("active", true);
  svg.on('click', addFilledVertex);
}

function deactivateFilled(obj) {
  //boundary_circle.classed("active", false);
  svg.on('click', null);
}


function activateUnfilled(obj) {
  mode = "place_unfilled";
  deselect();
  //boundary_circle.classed("active", true);
  svg.on('click', addUnfilledVertex);
}

function deactivateUnfilled(obj) {
  //boundary_circle.classed("active", false);
  svg.on('click', null);
}


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

function deactivateToggle(obj) {
  svg.selectAll(".vertex").on("click", null);
}


function deactivateAllObjects() {
  svg.selectAll("*").classed("active", false);
}

function activateObjects(selector) {
  svg.selectAll(selector).classed("active", true);
}


function newVertex(x, y, type) {
  return {x:x, y:y, id: ++maxVertexId, type:type};
}

function addVertex(e) {
  var vertexType = "filled";
  if (e.shiftKey) {
    vertexType = "unfilled"
  }
  data.vertices.push(newVertex(x.invert(e.offsetX), y.invert(e.offsetY), vertexType));
  update();
}


function addUnfilledVertex(e) {
  vertexType = "unfilled"
  data.vertices.push(newVertex(x.invert(e.offsetX), y.invert(e.offsetY), vertexType));
  update();
}

function addFilledVertex(e) {
  vertexType = "filled"
  data.vertices.push(newVertex(x.invert(e.offsetX), y.invert(e.offsetY), vertexType));
  update();
}


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
  //svg.on('click', addFilledVertex);
}


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
  //svg.on('click', addFilledVertex);
}

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
  //svg.on('click', addFilledVertex);
}

function deactivateEdge(obj) {
  svg.selectAll(".vertex").on("mousedown", null);
}


//activateButton(document.querySelector('#btn-select'),'select');
