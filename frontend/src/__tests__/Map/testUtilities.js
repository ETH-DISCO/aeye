// Test ClustersMap component
// ----------------------------------------------------------------------------
import {expect, test} from '@jest/globals'
import {LRUCache} from "lru-cache";

const {
    convertIndexToTile,
    convertTileToIndex,
    getTilesToFetch,
    getTilesFromZoomLevel
} = require('../../Map/utilities');

// Test fetchTileData
// ----------------------------------------------------------------------------
test('convertIndexToTile', async () => {
    const index_0 = 0;
    const tile_0 = convertIndexToTile(index_0);
    expect(tile_0.x).toBe(0);
    expect(tile_0.y).toBe(0);
    expect(tile_0.zoom).toBe(0);

    const index_5 = 5;
    const tile_5 = convertIndexToTile(index_5);
    expect(tile_5.x).toBe(0);
    expect(tile_5.y).toBe(0);
    expect(tile_5.zoom).toBe(2);

    const index_13390 = 13390;
    const tile_13390 = convertIndexToTile(index_13390);
    expect(tile_13390.zoom).toBe(7);
    expect(tile_13390.x).toBe(61);
    expect(tile_13390.y).toBe(121);

    const index_16085 = 16085;
    const tile_16085 = convertIndexToTile(index_16085);
    expect(tile_16085.zoom).toBe(7);
    expect(tile_16085.x).toBe(83);
    expect(tile_16085.y).toBe(0);

    const index_5461 = 5461;
    const tile_5461 = convertIndexToTile(index_5461);
    expect(tile_5461.zoom).toBe(7);
    expect(tile_5461.x).toBe(0);
    expect(tile_5461.y).toBe(0);

    const index = 12234;
    const tile = convertIndexToTile(index);
    process.stdout.write(`tile: ${JSON.stringify(tile)}\n`);
});

// Test convertTileToIndex
// ----------------------------------------------------------------------------
test('convertTileToIndex', async () => {
    const tile_0 = {x: 0, y: 0, zoom: 0};
    const index_0 = convertTileToIndex(tile_0.x, tile_0.y, tile_0.zoom);
    expect(index_0).toBe(0);

    const tile_5 = {x: 0, y: 0, zoom: 2};
    const index_5 = convertTileToIndex(tile_5.x, tile_5.y, tile_5.zoom);
    expect(index_5).toBe(5);

    const tile_13390 = {x: 61, y: 121, zoom: 7};
    const index_13390 = convertTileToIndex(tile_13390.x, tile_13390.y, tile_13390.zoom);
    expect(index_13390).toBe(13390);

    const tile_16085 = {x: 83, y: 0, zoom: 7};
    const index_16085 = convertTileToIndex(tile_16085.x, tile_16085.y, tile_16085.zoom);
    expect(index_16085).toBe(16085);

    const tile_5461 = {x: 0, y: 0, zoom: 7};
    const index_5461 = convertTileToIndex(tile_5461.x, tile_5461.y, tile_5461.zoom);
    expect(index_5461).toBe(5461);

    const tile = {x: 26, y: 58, zoom: 6};
    const index = convertTileToIndex(tile.x, tile.y, tile.zoom);
    process.stdout.write(`index: ${index}\n`);
});


// Test getTilesToFetch
// ----------------------------------------------------------------------------
test('getTilesToFetch', async () => {
    const tilesCache = new LRUCache({
        max: 1000,
        updateAgeOnHas: true,
        updateAgeOnGet: true
    });
    const tile = {x: 17, y: 18, zoom: 5};
    const tiles = getTilesToFetch(tile.x, tile.y, tile.zoom, 7, tilesCache);
    // Check that the tiles are unique
    const uniqueTiles = new Set(tiles);
    expect(uniqueTiles.size).toBe(tiles.length);
    expect(tiles.length).toBe(25 * 3 + (25 * 4 + 44) * 5);
});


// Test getTilesFromZoomLevel
// ----------------------------------------------------------------------------
test('getTilesFromZoomLevel', async () => {
    let tiles = getTilesFromZoomLevel(5, 7, 5);
    expect(tiles.length).toBe(20);
    tiles = getTilesFromZoomLevel(1, 1, 1);
    expect(tiles.length).toBe(4);
});
