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
        case "fC": // city
            return "#cc00b7";
        case "fS": // shelter
            return "#7d7d7d";
    }
    return "#000";
}

// load terrain
$.getJSON("/static/terrain.json", (data) => {
    const tileSize = 25;
    const terrain = data["terrain"];
    const features = data["features"];
    const mapWidth = data["width"];
    const mapHeight = data["height"];

    canvasElem.setAttribute("width", String(mapWidth * tileSize));
    canvasElem.setAttribute("height", String(mapHeight * tileSize));

    for (let x = 0; x < mapWidth; x++) {
        for (let y = 0; y < mapHeight; y++) {
            const index = x * mapWidth + y;
            if (x === Math.floor(mapWidth / 2) && Math.floor(y === mapHeight / 2)) {
                context.fillStyle = "#dd0200";
            } else {
                context.fillStyle = colorFor(terrain[index]);
            }
            context.fillRect(x * tileSize, y * tileSize, tileSize, tileSize);
            if (!!features[index]) {
                context.strokeStyle = colorFor(features[index]);
                context.lineWidth = 3;
                context.strokeRect(x * tileSize, y * tileSize, tileSize, tileSize);
            }
        }
    }
});
