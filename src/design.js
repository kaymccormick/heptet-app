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
  x: stage.getWidth() / 2,
  y: 50,
  width: 100,
    height: 400,
  stroke: 'black',
  strokeWidth: 4
});

// add the shape to the layer
layer.add(circle);

// add the layer to the stage
stage.add(layer);

// draw the image
layer.draw();
