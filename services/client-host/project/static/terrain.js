console.log("hello");
const canvasElem = document.getElementById("terrain-canvas");
const context = canvasElem.getContext("2d");

function colorFor(terrainTile) {
    switch (terrainTile) {
        case "P":
            return "#37c36a";
        case "F":
            return "#2d9046";
        case "S":
            return "#d3eeff";
        case "D":
            return "#e5d85d";
        case "W":
            return "#4c7999";
    }
    return "#000";
}

// load terrain
$.getJSON("/static/terrain.json", (data) => {
    const terrain = data["terrain"];
    const mapWidth = terrain.shift();
    const mapHeight = terrain.shift();

    for (let x = 0; x < mapWidth; x++) {
        for (let y = 0; y < mapHeight; y++) {
            const index = x * mapWidth + y;
            if (x === 50 && y === 50) {
                context.fillStyle = "#dd0200";
            } else {
                context.fillStyle = colorFor(terrain[index]);
            }
            context.fillRect(x * 10, y * 10, 10, 10);
        }
    }
    console.log(terrain);
});
