import 'konva';

var stage = new Konva.Stage({
  container: 'konva_stage',   // id of container <div>
  width: 500,
  height: 500
});

// then create layer
var layer = new Konva.Layer();

// create our shape
var circle = new Konva.Rect({
  x: 10,
  y: 10,
  width: 150,
    height: 200,
  stroke: 'gray',
  strokeWidth: 2
});






// add the shape to the layer
layer.add(circle);

// add the layer to the stage
stage.add(layer);

// draw the image
layer.draw();
