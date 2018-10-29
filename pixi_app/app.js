var jdCanvas = document.getElementsByTagName('canvas')[0];
var renderer = PIXI.autoDetectRenderer(800, 600, {backgroundColor: 0xffffff,
    antialias: true, view:jdCanvas});


var stage = new PIXI.Container(); // main
var world = createWorld();
stage.addChild(world);

var mapper;

var loader = new PIXI.loaders.Loader();
loader.add('tiles', "img/tiles2.json")
        .add('walk', "img/spritesheets/walkb.json");
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
    var viewportWorld = new PIXI.extras.Viewport({
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
        viewportWorld.scale.set(0.5);
        
    return viewportWorld;
}

function createMap(){
    
    var tilemap = new PIXI.tilemap.CompositeRectTileLayer(0, PIXI.utils.TextureCache['tiles_image']);
    maplength = 84 /3 // number of tiles for length of map 2688px
    mapwidth = 63 / 3 // number of tiles for width of map 2688px
    
    // var tilemap = new PIXI.tilemap.CompositeRectTileLayer(0, [resources['atlas_image'].texture]);
    var size = 32;
    // bah, im too lazy, i just want to specify filenames from atlas
    for (var i = 0 ; i < maplength; i++) {
        for (var j = 0 ;j < mapwidth; j++) {
            tilemap.addFrame("sandtile_1.png", i*size, j*size);
            if (i%2==1 && j%2==1)
                tilemap.addFrame("snowtile_2.png", i*size, j*size);
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
    animCharSprite.scale.set(1);
    animCharSprite.click = () => {
        alert("I am walkin here!!!");
    }

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
