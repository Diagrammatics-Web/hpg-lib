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
};

var activeButton = false;
var activeMode = false;


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

function idStr(e) {
  return "("+e.multiEdge.source.id+"/"+e.multiEdge.target.id+")."+e.multiEdge.id+"."+e.heId;
}

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
      edgePath.push(e.multiEdge.edge);
      while(boundaryVertices.indexOf(e.multiEdge.target)==-1)// && confirm("Continue?"))
      {
          e = e.twin;
          console.log("swith to",idStr(e));
          if(e.multiEdge.source.type=="unfilled") {
            for(var i=0; i<tripIndex; i++) {
                e = e.prev;
                console.log("unfilled turn to",idStr(e));
            }
          } else {
            for(var i=0; i<tripIndex; i++) {
                e = e.next;
                console.log("filled turn to",idStr(e));
            }
          }
          edgePath.push(e.multiEdge.edge);
          update();
      }

    });
}

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
