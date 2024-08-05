// This file contains utility functions for the map.

function getTilesFromNextZoomLevelAtBorder(tile_x, tile_y, zoom_level, max_zoom_level) {
    // Get additional frame of tiles at the next zoom level
    const new_tiles = [];
    if (zoom_level + 1 <= max_zoom_level) {
        if (tile_x > 1) {
            const tile_x_next_zoom_level = (tile_x - 2) * 2 + 1;
            for (let i = -1; i <= 3; i++) {
                if (tile_y + i >= 0 && tile_y + i < 2 ** zoom_level) {
                    new_tiles.push({x: tile_x_next_zoom_level, y: (tile_y + i) * 2, zoom: zoom_level + 1});
                    new_tiles.push({x: tile_x_next_zoom_level, y: (tile_y + i) * 2 + 1, zoom: zoom_level + 1});
                }
            }
            // Get corner tiles
            if (tile_y > 1) {
                new_tiles.push({x: tile_x_next_zoom_level, y: (tile_y - 2) * 2 + 1, zoom: zoom_level + 1});
            }
            if (tile_y + 4 < 2 ** zoom_level) {
                new_tiles.push({x: tile_x_next_zoom_level, y: (tile_y + 4) * 2, zoom: zoom_level + 1});
            }
        }
        if (tile_x + 4 < 2 ** zoom_level) {
            const tile_x_next_zoom_level = (tile_x + 4) * 2;
            for (let i = -1; i <= 3; i++) {
                if (tile_y + i >= 0 && tile_y + i < 2 ** zoom_level) {
                    new_tiles.push({x: tile_x_next_zoom_level, y: (tile_y + i) * 2, zoom: zoom_level + 1});
                    new_tiles.push({x: tile_x_next_zoom_level, y: (tile_y + i) * 2 + 1, zoom: zoom_level + 1});
                }
            }
            // Get corner tiles
            if (tile_y > 1) {
                new_tiles.push({x: tile_x_next_zoom_level, y: (tile_y - 2) * 2 + 1, zoom: zoom_level + 1});
            }
            if (tile_y + 4 < 2 ** zoom_level) {
                new_tiles.push({x: tile_x_next_zoom_level, y: (tile_y + 4) * 2, zoom: zoom_level + 1});
            }
        }
        if (tile_y > 1) {
            const tile_y_next_zoom_level = (tile_y - 2) * 2 + 1;
            for (let i = -1; i <= 3; i++) {
                if (tile_x + i >= 0 && tile_x + i < 2 ** zoom_level) {
                    new_tiles.push({x: (tile_x + i) * 2, y: tile_y_next_zoom_level, zoom: zoom_level + 1});
                    new_tiles.push({x: (tile_x + i) * 2 + 1, y: tile_y_next_zoom_level, zoom: zoom_level + 1});
                }
            }
        }
        if (tile_y + 3 < 2 ** zoom_level) {
            const tile_y_next_zoom_level = (tile_y + 4) * 2;
            for (let i = -1; i <= 3; i++) {
                if (tile_x + i >= 0 && tile_x + i < 2 ** zoom_level) {
                    new_tiles.push({x: (tile_x + i) * 2, y: tile_y_next_zoom_level, zoom: zoom_level + 1});
                    new_tiles.push({x: (tile_x + i) * 2 + 1, y: tile_y_next_zoom_level, zoom: zoom_level + 1});
                }
            }
        }
    }
    return new_tiles;
}


/**
 * Get the tiles at the next zoom level.
 * @param tiles The tiles at the current zoom level.
 * @param zoom_level The zoom level.
 * @param max_zoom_level The maximum zoom level.
 * @returns {*[]} An array containing the tiles at the next zoom level.
 */
function getTilesFromNextZoomLevel(tiles, zoom_level, max_zoom_level) {
    const new_tiles = [];

    if (zoom_level + 1 <= max_zoom_level) {
        for (const tile of tiles) {
            // The current tile is divided into 4 tiles at the next zoom level
            const tile_x_next_zoom_level = tile.x * 2;
            const tile_y_next_zoom_level = tile.y * 2;
            new_tiles.push({x: tile_x_next_zoom_level, y: tile_y_next_zoom_level, zoom: zoom_level + 1});
            new_tiles.push({x: tile_x_next_zoom_level + 1, y: tile_y_next_zoom_level, zoom: zoom_level + 1});
            new_tiles.push({x: tile_x_next_zoom_level, y: tile_y_next_zoom_level + 1, zoom: zoom_level + 1});
            new_tiles.push({x: tile_x_next_zoom_level + 1, y: tile_y_next_zoom_level + 1, zoom: zoom_level + 1});
        }
    }

    return new_tiles;
}


/**
 * Get the tiles to fetch for a given tile.
 * @param tile_x The x coordinate of the tile.
 * @param tile_y The y coordinate of the tile.
 * @param zoom_level The zoom level.
 * @returns {*[]} An array containing the tiles to fetch.
 */
export function getTilesFromZoomLevel(tile_x, tile_y, zoom_level) {
    // Get the number of tiles at the current zoom level
    const number_of_tiles = 2 ** zoom_level;
    const tiles = [];

    tiles.push({x: tile_x, y: tile_y, zoom: zoom_level});
    if (tile_y > 0)
        tiles.push({x: tile_x, y: tile_y - 1, zoom: zoom_level});
    if (tile_y < number_of_tiles - 1)
        tiles.push({x: tile_x, y: tile_y + 1, zoom: zoom_level});
    if (tile_y < number_of_tiles - 2)
        tiles.push({x: tile_x, y: tile_y + 2, zoom: zoom_level});
    if (tile_y < number_of_tiles - 3)
        tiles.push({x: tile_x, y: tile_y + 3, zoom: zoom_level});

    if (tile_x > 0) {
        tiles.push({x: tile_x - 1, y: tile_y, zoom: zoom_level});
        if (tile_y > 0)
            tiles.push({x: tile_x - 1, y: tile_y - 1, zoom: zoom_level});
        if (tile_y < number_of_tiles - 1)
            tiles.push({x: tile_x - 1, y: tile_y + 1, zoom: zoom_level});
        if (tile_y < number_of_tiles - 2)
            tiles.push({x: tile_x - 1, y: tile_y + 2, zoom: zoom_level});
        if (tile_y < number_of_tiles - 3)
            tiles.push({x: tile_x - 1, y: tile_y + 3, zoom: zoom_level});
    }
    if (tile_x < number_of_tiles - 1) {
        tiles.push({x: tile_x + 1, y: tile_y, zoom: zoom_level});
        if (tile_y > 0)
            tiles.push({x: tile_x + 1, y: tile_y - 1, zoom: zoom_level});
        if (tile_y < number_of_tiles - 1)
            tiles.push({x: tile_x + 1, y: tile_y + 1, zoom: zoom_level});
        if (tile_y < number_of_tiles - 2)
            tiles.push({x: tile_x + 1, y: tile_y + 2, zoom: zoom_level});
        if (tile_y < number_of_tiles - 3)
            tiles.push({x: tile_x + 1, y: tile_y + 3, zoom: zoom_level});
    }
    if (tile_x < number_of_tiles - 2) {
        tiles.push({x: tile_x + 2, y: tile_y, zoom: zoom_level});
        if (tile_y > 0)
            tiles.push({x: tile_x + 2, y: tile_y - 1, zoom: zoom_level});
        if (tile_y < number_of_tiles - 1)
            tiles.push({x: tile_x + 2, y: tile_y + 1, zoom: zoom_level});
        if (tile_y < number_of_tiles - 2)
            tiles.push({x: tile_x + 2, y: tile_y + 2, zoom: zoom_level});
        if (tile_y < number_of_tiles - 3)
            tiles.push({x: tile_x + 2, y: tile_y + 3, zoom: zoom_level});
    }
    if (tile_x < number_of_tiles - 3) {
        tiles.push({x: tile_x + 3, y: tile_y, zoom: zoom_level});
        if (tile_y > 0)
            tiles.push({x: tile_x + 3, y: tile_y - 1, zoom: zoom_level});
        if (tile_y < number_of_tiles - 1)
            tiles.push({x: tile_x + 3, y: tile_y + 1, zoom: zoom_level});
        if (tile_y < number_of_tiles - 2)
            tiles.push({x: tile_x + 3, y: tile_y + 2, zoom: zoom_level});
        if (tile_y < number_of_tiles - 3)
            tiles.push({x: tile_x + 3, y: tile_y + 3, zoom: zoom_level});
    }

    return tiles;
}


export function convertTileToIndex(tile_x, tile_y, zoom_level) {
    // The index is given by sum_{i=0}^{zoom_level-1} 4^i + (2 ** zoom_level) * tile.x + tile.y
    let index = 0;
    for (let i = 0; i < zoom_level; i++) {
        index += 4 ** i;
    }
    index += (2 ** zoom_level) * tile_x + tile_y;
    return index;
}

export function convertIndexToTile(index) {
    // The index is given by sum_{i=0}^{zoom_level-1} 4^i + (2 ** zoom_level) * tile.x + tile.y
    let i = 0;
    let sum = 0;
    while (sum < index) {
        sum += 4 ** i;
        i++;
    }
    if (sum === index) {
        return {x: 0, y: 0, zoom: i};
    }
    sum -= 4 ** (i - 1);
    const zoom_level = i - 1;
    let tile_x = Math.floor((index - sum) / (2 ** zoom_level));
    let tile_y = index - sum - (2 ** zoom_level) * tile_x;
    return {x: tile_x, y: tile_y, zoom: zoom_level};
}


export function getTilesToFetch(tile_x, tile_y, zoom_level, max_zoom_level, tilesCache) {
    // At the current zoom level, consider a 4x4 grid of tiles around the effective window. Then, fetch the same region at the next zoom level and
    // the next zoom level after that. Also, fetch a 4x4 grid at the previous two zoom levels, whose center is the 4x4 region at the current zoom level.
    // This creates a funnel shape wrt the embedding space.
    const tiles = getTilesFromZoomLevel(tile_x, tile_y, zoom_level);
    const tiles_next_zoom_level = getTilesFromNextZoomLevel(tiles, zoom_level, max_zoom_level);
    const tiles_at_border = getTilesFromNextZoomLevelAtBorder(tile_x, tile_y, zoom_level, max_zoom_level);
    tiles_next_zoom_level.push(...tiles_at_border);
    const tiles_next_next_zoom_level = getTilesFromNextZoomLevel(tiles_next_zoom_level, zoom_level + 1, max_zoom_level);
    // Add everything to tiles
    tiles.push(...tiles_next_zoom_level);
    tiles.push(...tiles_next_next_zoom_level);
    // Compute tile_x and tile_y at the previous zoom level
    if (zoom_level > 0) {
        const tile_x_prev_zoom_level = Math.floor(tile_x / 2);
        const tile_y_prev_zoom_level = Math.floor(tile_y / 2);
        const tiles_prev_zoom_level = getTilesFromZoomLevel(tile_x_prev_zoom_level, tile_y_prev_zoom_level, zoom_level - 1);
        tiles.push(...tiles_prev_zoom_level);
    }
    if (zoom_level > 1) {
        const tile_x_prev_prev_zoom_level = Math.floor(tile_x / 4);
        const tile_y_prev_prev_zoom_level = Math.floor(tile_y / 4);
        const tiles_prev_prev_zoom_level = getTilesFromZoomLevel(tile_x_prev_prev_zoom_level, tile_y_prev_prev_zoom_level, zoom_level - 2);
        tiles.push(...tiles_prev_prev_zoom_level);
    }

    // Find out which tiles to fetch. Use has to check if the tile is already in the cache. If it is not, compute its index and add it to the list of tiles to fetch.
    const indexes_of_tiles_to_fetch = [];
    for (const tile of tiles) {
        if (!tilesCache.has(tile.zoom + "-" + tile.x + "-" + tile.y)) {
            indexes_of_tiles_to_fetch.push(convertTileToIndex(tile.x, tile.y, tile.zoom));
        }
    }
    return indexes_of_tiles_to_fetch;
}

export function getTilesForTranslationTicker(tile_x, tile_y, zoom_level, tilesCache) {
    const tiles = getTilesFromZoomLevel(tile_x, tile_y, zoom_level);
    const indexes_of_tiles_to_fetch = [];
    for (const tile of tiles) {
        if (!tilesCache.has(tile.zoom + "-" + tile.x + "-" + tile.y)) {
            indexes_of_tiles_to_fetch.push(convertTileToIndex(tile.x, tile.y, tile.zoom));
        }
    }
    return indexes_of_tiles_to_fetch;
}

export function getTilesForZoomTicker(tile_x, tile_y, zoom_level, max_zoom_level, tilesCache) {
    const tiles = getTilesFromZoomLevel(tile_x, tile_y, zoom_level);
    const tiles_next_zoom_level = getTilesFromNextZoomLevel(tiles, zoom_level, max_zoom_level);
    tiles.push(...tiles_next_zoom_level);
    // Compute tile_x and tile_y at the previous zoom level
    if (zoom_level > 0) {
        const tile_x_prev_zoom_level = Math.floor(tile_x / 2);
        const tile_y_prev_zoom_level = Math.floor(tile_y / 2);
        const tiles_prev_zoom_level = getTilesFromZoomLevel(tile_x_prev_zoom_level, tile_y_prev_zoom_level, zoom_level - 1);
        tiles.push(...tiles_prev_zoom_level);
    }
    const indexes_of_tiles_to_fetch = [];
    for (const tile of tiles) {
        if (!tilesCache.has(tile.zoom + "-" + tile.x + "-" + tile.y)) {
            indexes_of_tiles_to_fetch.push(convertTileToIndex(tile.x, tile.y, tile.zoom));
        }
    }
    return indexes_of_tiles_to_fetch;
}