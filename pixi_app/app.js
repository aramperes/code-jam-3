

var jdCanvas = document.getElementsByTagName('canvas')[0];
var renderer = PIXI.autoDetectRenderer(800, 600, {backgroundColor: 0xffffff,
    antialias: true, view:jdCanvas});


var stage = createStage();

var mapper;

var loader = new PIXI.loaders.Loader();
loader.add('atlas', 'basic/atlas.json')
        .add('tiles', "imgs/sprite/tiles2.json")
        .add('walk', "imgs/spritesheets/walkb.json");
loader.load(setup);

function setup (loader, resources) {
	 
    var tilemap = createMap();
    stage.addChild(tilemap);
    createChar();

    runGame();
}

function createStage(){
    var stage = new PIXI.Container();
    // stage.interactive = true;
    stage.scale.x = 1;
    stage.scale.y = 1;


    return stage;
}

function createMap(){
    
    var tilemap = new PIXI.tilemap.CompositeRectTileLayer(0, PIXI.utils.TextureCache['tiles_image']);
    maplength = 84 // number of tiles for length of map 2688px
    mapwidth = 63 // number of tiles for width of map 2688px
    
    // var tilemap = new PIXI.tilemap.CompositeRectTileLayer(0, [resources['atlas_image'].texture]);
    var size = 32;
    // bah, im too lazy, i just want to specify filenames from atlas
    for (var i = 0 ; i < maplength; i++) 
        for (var j = 0 ;j < mapwidth; j++) {
            tilemap.addFrame("sandtile_1.png", i*size, j*size);
            if (i%2==1 && j%2==1)
                tilemap.addFrame("snowtile_2.png", i*size, j*size);
        }

        // addInteraction(tilemap);

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

    animCharSprite.interactive = true;
    
    animCharSprite
        .on('pointerdown', onDragStart)
        .on('pointerup', onDragEnd)
        .on('pointerupoutside', onDragEnd)
        .on('pointermove', onDragMove);

    stage.addChild(animCharSprite);
}


function runGame() {
    renderer.render(stage);
    requestAnimationFrame(runGame);
}


// === INTERACTION CODE  ===

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
