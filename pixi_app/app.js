var canvas = document.getElementsByTagName('canvas')[0];
var renderer = PIXI.autoDetectRenderer(800, 600, {view:canvas});
var stage = createStage();

var mapper;

var loader = new PIXI.loaders.Loader();
loader.add('tiles', "img/tiles2.json")
    .load(setup);

function setup (loader, resources) {
	 
    var tilemap = createMap();
    stage.addChild(tilemap);

    runGame();
}

function createStage(){
    var stage = new PIXI.Container();
    // stage.interactive = true;
    stage.scale.x = 1;
    stage.scale.y = 1;
    return stage;
}

function createMap(){ //tentative map
    
    var tilemap = new PIXI.tilemap.CompositeRectTileLayer(0, PIXI.utils.TextureCache['tiles_image']);
    
    // var tilemap = new PIXI.tilemap.CompositeRectTileLayer(0, [resources['atlas_image'].texture]);
    var size = 32;
    // bah, im too lazy, i just want to specify filenames from atlas
    for (var i=0;i<21;i++)
        for (var j=0;j<9;j++) {
            tilemap.addFrame("sandtile_1.png", i*size, j*size);
            if (i%2==1 && j%2==1)
                tilemap.addFrame("snowtile_2.png", i*size, j*size);
        }

    return tilemap;
}

function runGame() {
    renderer.render(stage);
    requestAnimationFrame(runGame);
}

function onDragStart(event) {
    // store a reference to the data
    // the reason for this is because of multitouch
    // we want to track the movement of this particular touch
    this.data = event.data;
    this.alpha = 0.5;
    this.dragging = true;
}

function onDragEnd() {
    this.alpha = 1;
    this.dragging = false;
    // set the interaction data to null
    this.data = null;
}

function onDragMove() {
    if (this.dragging) {
        var newPosition = this.data.getLocalPosition(this.parent);
        this.x = newPosition.x;
        this.y = newPosition.y;
    }
}
