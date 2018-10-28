var resolutionX = 800;
var resolutionY = 600;
var tileSizeX = 100;
var tileSizeY = 100;

var groundTileMap;
var playerSprite;
var playerOffsetX = (resolutionX / 2 - 24);
var playerOffsetY = (resolutionY / 2 - 24);

var player = {
    x: 0,
    y: 0
};


var app = new PIXI.Application(resolutionX, resolutionY);
document.body.appendChild(app.view);

PIXI.loader
        .add("img/imgTanks.png")
        .add('tiles', "img/tiles.json")
        .load(setup);


function setup(loader, resources){
    // Create our tile map based on the ground texture
    // groundTiles = new PIXI.tilemap.CompositeRectTileLayer(0, PIXI.utils.TextureCache['imgs/imgGround.png']);
    // groundTileMap = new PIXI.tilemap.CompositeRectTileLayer(0, PIXI.utils.TextureCache[resources['sand_2']]);
    groundTileMap = new PIXI.tilemap.CompositeRectTileLayer(0, [resources['tiles_image'].texture]);

    // var sand_2 = resources['sand_2'];
    drawGround("snowtile_1.png");

    app.stage.addChild(groundTileMap);

    var tankTexture = new PIXI.Texture(
        PIXI.utils.TextureCache['imgs/imgTanks.png'],
        new PIXI.Rectangle(0 * 48, 0, 48, 48)
    );

    var player1 = createPlayerSprite(tankTexture);


    runGameLoop();
}

// create grounds for snow, desert, forest, and others
function drawGround(groundImangeTexture){

    // set number of tiles needed for the window
    var numberOfTiles = parseInt(resolutionX / tileSizeX) + 10;

    var groundOffsetX = player.x % 100; // Number of tank tiles on x axis
    var groundOffsetY = player.y % 100; // Number of tank tiles on y axis

    // creating floor by adding tiles to ground frame!
    for (var i = -numberOfTiles; i <= numberOfTiles; i++) {
        for (var j = -numberOfTiles; j <= numberOfTiles; j++) {
            groundTileMap.addFrame(groundImangeTexture, i * tileSizeX, j * tileSizeY);
        }
    }

}


function createPlayerSprite(texture){
    playerSprite = new PIXI.Sprite(texture);
    playerSprite.x = playerOffsetX;
    playerSprite.y = playerOffsetY;

    app.stage.addChild(playerSprite);
    playerSprite.interactive = true;

    playerSprite.click = () => {
        alert("I am working!");
    }
    
    return playerSprite;
}


// run game loop
function runGameLoop() {

    groundTileMap.pivot.set(player.x, player.y);
    requestAnimationFrame(runGameLoop);
}


 // set movements via keys aswd and arrows
document.addEventListener('keydown', (e) => {    

     if (e.keyCode == '38' || e.keyCode == '87') {
        // up arrow or w  => move forward 
        player.y -= 10;
    }
    else if (e.keyCode == '40' || e.keyCode == '83') {
        // down arrow or s => move backwards
        player.y += 10;
    }
    else if (e.keyCode == '37' || e.keyCode == '65') {
       // left arrow or a => move to the left
       player.x -= 10;
    }
    else if (e.keyCode == '39' || e.keyCode == '68') {
       // right arrow or d => move to the right
       player.x += 10;
    }
  });

