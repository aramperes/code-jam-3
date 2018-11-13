window["run_pixi_app"] = function() {
var PIXI = require('pixi.js');
var Viewport = require('pixi-viewport');
var PIXI_tilemap = require('pixi-tilemap');

var jdCanvas = document.getElementsByTagName('canvas')[0];
console.log(jdCanvas);
var renderer = PIXI.autoDetectRenderer(800, 600, {backgroundColor: 0xffffff,
    antialias: true, view:jdCanvas});


var stage = new PIXI.Container(); // main
var world = createWorld();
stage.addChild(world);

var mapper;

var loader = new PIXI.loaders.Loader("/static");
loader.add('tiles', "/img/tiles2.json")
        .add('walk', "/img/spritesheets/walkb.json");
loader.load(setup);

function setup (loader, resources) {

    var tilemap = createMap();
    var animChar = createChar();
    world.addChild(tilemap);
    world.addChild(animChar);
    createChar();

    runGame();
}
var worldWidth = 3000,
worldHeight = 3000;

function createWorld(){
    var viewportWorld = new Viewport({
        // var viewport = new Viewport({
            screenWidth: renderer.screen.width,
            screenHeight: renderer.screen.height,
            worldWidth: worldWidth,
            worldHeight: worldHeight,

            interaction: renderer.interaction  // the interaction module is important for wheel() to work properly when renderer.view is placed or scaled
        });
    viewportWorld
        .drag()
        .pinch()
        .wheel()
        .decelerate();
        viewportWorld.scale.set(2);

    return viewportWorld;
}

function createMap(){
    const clientInstance = window["client_instance"];
    const worldDim = clientInstance._world_piece_size * clientInstance._world_piece_count;
    console.log(clientInstance._world_piece_size, clientInstance._world_piece_count);

    var tilemap = new PIXI.tilemap.CompositeRectTileLayer(0, PIXI.utils.TextureCache['tiles_image']);

    // var tilemap = new PIXI.tilemap.CompositeRectTileLayer(0, [resources['atlas_image'].texture]);
    var size = 32;
    // bah, im too lazy, i just want to specify filenames from atlas

    for (let x = 0; x < worldDim; x++) {
        for (let y = 0; y < worldDim; y++) {
            const terrain = clientInstance._world_terrain[x][y];
            const feature = clientInstance._world_features[x][y];
            if (terrain === "D") {
                tilemap.addFrame("sandtile_1.png", x * size, y * size);
            } else if (terrain === "S") {
                tilemap.addFrame("snowtile_2.png", x * size, y * size);
            } else if (terrain === "W") {
                tilemap.addFrame("watertile_2.png", x * size, y * size);
            } else if (terrain === "P") {
                tilemap.addFrame("grasstile_2.png", x * size, y * size);
            } else if (terrain === "F") {
                tilemap.addFrame("grasstile_1.png", x * size, y * size);
            } else {
                console.log("Unknown terrain tile", terrain, "at", x, y);
            }

            if (feature === "fC") {
                if (clientInstance._world_features[x + 1] &&
                    clientInstance._world_features[x + 1][y] === "fC" &&
                    Math.random() < 0.5) {
                    // big house (west part)
                    clientInstance._world_features[x + 1][y] = "fC_bigEast";
                    tilemap.addFrame("house_big_1.png", x * size, y * size);
                } else {
                    // small house
                    tilemap.addFrame("house_small.png", x * size, y * size);
                }
            } else if (feature === "fC_bigEast") {
                tilemap.addFrame("house_big_2.png", x * size, y * size);
            }
        }
    }
    return tilemap;
}


function createChar(){

    var charTextures = [
        PIXI.Texture.fromFrame('walkb_1.png'),
        PIXI.Texture.fromFrame('walkb_2.png'),
    ], i;

    var animCharSprite = new PIXI.extras.AnimatedSprite(charTextures);

    animCharSprite.x = renderer.screen.width / 2 - 20;
    animCharSprite.y = renderer.screen.height / 2;
    animCharSprite.anchor.set(0.5);
    // animCharSprite.gotoAndPlay(0.0000009);
    animCharSprite.scale.set(0.25);

    animCharSprite.buttonMode = true;

    setInteractOb(animCharSprite);

    return(animCharSprite);
}


function runGame() {
    renderer.render(stage);
    requestAnimationFrame(runGame);
}


// === INTERACTION CODE  ===

function setInteractOb(obj){
    obj.interactive = true
    obj.on('pointerdown', onDragStart)
        .on('pointerup', onDragEnd)
        .on('pointerupoutside', onDragEnd)
        .on('pointermove', onDragMove);
    return obj;
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
}
