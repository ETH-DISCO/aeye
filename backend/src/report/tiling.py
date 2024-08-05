"""
Module to visualize tiles.
"""
import os

import matplotlib.pyplot as plt
import numpy as np

TILE_X = 15
TILE_Y = 18
ZOOM_LEVEL = 5
MAX_ZOOM_LEVEL = 7
DIST_STEP = 0.
DIST_STEP_2 = 0.3
DEPTH_STEP = 0.5


def get_tiles_from_next_zoom_level_at_border(tile_x, tile_y, zoom_level, max_zoom_level):
    # Get additional frame of tiles at the next zoom level
    new_tiles = []
    if zoom_level + 1 <= max_zoom_level:
        if tile_x > 1:
            tile_x_next_zoom_level = (tile_x - 2) * 2 + 1
            for i in range(-1, 4):
                if 0 <= tile_y + i < 2 ** zoom_level:
                    new_tiles.append({'x': tile_x_next_zoom_level, 'y': (tile_y + i) * 2, 'zoom': zoom_level + 1})
                    new_tiles.append({'x': tile_x_next_zoom_level, 'y': (tile_y + i) * 2 + 1, 'zoom': zoom_level + 1})
            if tile_y > 1:
                new_tiles.append({'x': tile_x_next_zoom_level, 'y': (tile_y - 2) * 2 + 1, 'zoom': zoom_level + 1})
            if tile_y + 4 < 2 ** zoom_level:
                new_tiles.append({'x': tile_x_next_zoom_level, 'y': (tile_y + 4) * 2, 'zoom': zoom_level + 1})
        if tile_x + 4 < 2 ** zoom_level:
            tile_x_next_zoom_level = (tile_x + 4) * 2
            for i in range(-1, 4):
                if 0 <= tile_y + i < 2 ** zoom_level:
                    new_tiles.append({'x': tile_x_next_zoom_level, 'y': (tile_y + i) * 2, 'zoom': zoom_level + 1})
                    new_tiles.append({'x': tile_x_next_zoom_level, 'y': (tile_y + i) * 2 + 1, 'zoom': zoom_level + 1})
            if tile_y > 1:
                new_tiles.append({'x': tile_x_next_zoom_level, 'y': (tile_y - 2) * 2 + 1, 'zoom': zoom_level + 1})
            if tile_y + 4 < 2 ** zoom_level:
                new_tiles.append({'x': tile_x_next_zoom_level, 'y': (tile_y + 4) * 2, 'zoom': zoom_level + 1})
        if tile_y > 1:
            tile_y_next_zoom_level = (tile_y - 2) * 2 + 1
            for i in range(-1, 4):
                if 0 <= tile_x + i < 2 ** zoom_level:
                    new_tiles.append({'x': (tile_x + i) * 2, 'y': tile_y_next_zoom_level, 'zoom': zoom_level + 1})
                    new_tiles.append({'x': (tile_x + i) * 2 + 1, 'y': tile_y_next_zoom_level, 'zoom': zoom_level + 1})
        if tile_y + 3 < 2 ** zoom_level:
            tile_y_next_zoom_level = (tile_y + 4) * 2
            for i in range(-1, 4):
                if 0 <= tile_x + i < 2 ** zoom_level:
                    new_tiles.append({'x': (tile_x + i) * 2, 'y': tile_y_next_zoom_level, 'zoom': zoom_level + 1})
                    new_tiles.append({'x': (tile_x + i) * 2 + 1, 'y': tile_y_next_zoom_level, 'zoom': zoom_level + 1})
    return new_tiles


def get_tiles_from_next_zoom_level(tiles, zoom_level, max_zoom_level):
    new_tiles = []

    if zoom_level + 1 <= max_zoom_level:
        for tile in tiles:
            # The current tile is divided into 4 tiles at the next zoom level
            tile_x_next_zoom_level = tile['x'] * 2
            tile_y_next_zoom_level = tile['y'] * 2
            new_tiles.append({'x': tile_x_next_zoom_level, 'y': tile_y_next_zoom_level, 'zoom': zoom_level + 1})
            new_tiles.append({'x': tile_x_next_zoom_level + 1, 'y': tile_y_next_zoom_level, 'zoom': zoom_level + 1})
            new_tiles.append({'x': tile_x_next_zoom_level, 'y': tile_y_next_zoom_level + 1, 'zoom': zoom_level + 1})
            new_tiles.append({'x': tile_x_next_zoom_level + 1, 'y': tile_y_next_zoom_level + 1, 'zoom': zoom_level + 1})

    return new_tiles


def get_tiles_from_zoom_level(tile_x, tile_y, zoom_level):
    # Get the number of tiles at the current zoom level
    number_of_tiles = 2 ** zoom_level

    tiles = [{'x': tile_x, 'y': tile_y, 'zoom': zoom_level}]
    # Add tiles in same column
    if tile_y > 0:
        tiles.append({'x': tile_x, 'y': tile_y - 1, 'zoom': zoom_level})
    if tile_y < number_of_tiles - 1:
        tiles.append({'x': tile_x, 'y': tile_y + 1, 'zoom': zoom_level})
    if tile_y < number_of_tiles - 2:
        tiles.append({'x': tile_x, 'y': tile_y + 2, 'zoom': zoom_level})
    if tile_y < number_of_tiles - 3:
        tiles.append({'x': tile_x, 'y': tile_y + 3, 'zoom': zoom_level})

    # Get all neighboring tiles. This means all tiles at a distance of 1, plus tiles at a distance of 2 on the bottom
    # and on the right.
    if tile_x > 0:
        # Go one tile to the left
        tiles.append({'x': tile_x - 1, 'y': tile_y, 'zoom': zoom_level})
        if tile_y > 0:
            tiles.append({'x': tile_x - 1, 'y': tile_y - 1, 'zoom': zoom_level})
        if tile_y < number_of_tiles - 1:
            tiles.append({'x': tile_x - 1, 'y': tile_y + 1, 'zoom': zoom_level})
        if tile_y < number_of_tiles - 2:
            tiles.append({'x': tile_x - 1, 'y': tile_y + 2, 'zoom': zoom_level})
        if tile_y < number_of_tiles - 3:
            tiles.append({'x': tile_x - 1, 'y': tile_y + 3, 'zoom': zoom_level})

    if tile_x < number_of_tiles - 1:
        # Go one tile to the right
        tiles.append({'x': tile_x + 1, 'y': tile_y, 'zoom': zoom_level})
        if tile_y > 0:
            tiles.append({'x': tile_x + 1, 'y': tile_y - 1, 'zoom': zoom_level})
        if tile_y < number_of_tiles - 1:
            tiles.append({'x': tile_x + 1, 'y': tile_y + 1, 'zoom': zoom_level})
        if tile_y < number_of_tiles - 2:
            tiles.append({'x': tile_x + 1, 'y': tile_y + 2, 'zoom': zoom_level})
        if tile_y < number_of_tiles - 3:
            tiles.append({'x': tile_x + 1, 'y': tile_y + 3, 'zoom': zoom_level})

    if tile_x < number_of_tiles - 2:
        # Go two tiles to the right
        tiles.append({'x': tile_x + 2, 'y': tile_y, 'zoom': zoom_level})
        if tile_y > 0:
            tiles.append({'x': tile_x + 2, 'y': tile_y - 1, 'zoom': zoom_level})
        if tile_y < number_of_tiles - 1:
            tiles.append({'x': tile_x + 2, 'y': tile_y + 1, 'zoom': zoom_level})
        if tile_y < number_of_tiles - 2:
            tiles.append({'x': tile_x + 2, 'y': tile_y + 2, 'zoom': zoom_level})
        if tile_y < number_of_tiles - 3:
            tiles.append({'x': tile_x + 2, 'y': tile_y + 3, 'zoom': zoom_level})

    if tile_x < number_of_tiles - 3:
        # Go three tiles to the right
        tiles.append({'x': tile_x + 3, 'y': tile_y, 'zoom': zoom_level})
        if tile_y > 0:
            tiles.append({'x': tile_x + 3, 'y': tile_y - 1, 'zoom': zoom_level})
        if tile_y < number_of_tiles - 1:
            tiles.append({'x': tile_x + 3, 'y': tile_y + 1, 'zoom': zoom_level})
        if tile_y < number_of_tiles - 2:
            tiles.append({'x': tile_x + 3, 'y': tile_y + 2, 'zoom': zoom_level})
        if tile_y < number_of_tiles - 3:
            tiles.append({'x': tile_x + 3, 'y': tile_y + 3, 'zoom': zoom_level})

    return tiles


def get_tiles_from_prev_zoom_level(tile_x, tile_y, zoom_level):
    tiles = []
    if zoom_level > 0:
        tile_x_prev_zoom_level = tile_x // 2
        tile_y_prev_zoom_level = tile_y // 2
        tiles_prev_zoom_level = get_tiles_from_zoom_level(tile_x_prev_zoom_level,
                                                          tile_y_prev_zoom_level, zoom_level - 1)
        tiles.extend(tiles_prev_zoom_level)

    return tiles


def get_tiles(tile_x, tile_y, zoom_level, max_zoom_level):
    # At the current zoom level, consider a 4x4 grid of tiles around the effective window. Then, fetch the same
    # region at the next zoom level and the next zoom level after that.
    tiles = get_tiles_from_zoom_level(tile_x, tile_y, zoom_level)
    tiles_next_zoom_level = get_tiles_from_next_zoom_level(tiles, zoom_level, max_zoom_level)
    tiles_at_border = get_tiles_from_next_zoom_level_at_border(tile_x, tile_y, zoom_level, max_zoom_level)
    tiles_next_zoom_level.extend(tiles_at_border)
    tiles_next_next_zoom_level = get_tiles_from_next_zoom_level(tiles_next_zoom_level, zoom_level + 1, max_zoom_level)
    # Add everything to tiles
    tiles.extend(tiles_next_zoom_level)
    tiles.extend(tiles_next_next_zoom_level)
    # Return the list of tiles
    return tiles


def plot_tiles(tiles):
    """
    Function to plot tiles as 3D rectangles.

    Args:
    tiles (list of tuples): Each tuple contains 3D coordinates in the form (x, y, z, dx, dy, dz).
    """

    # Create two new figures and add a 3D subplot
    fig1 = plt.figure(figsize=(15, 15))
    fig10 = plt.figure(figsize=(15, 15))
    fig11 = plt.figure(figsize=(15, 15))
    fig2 = plt.figure(figsize=(25, 15))
    ax1 = fig1.add_subplot(111, projection='3d')
    ax10 = fig10.add_subplot(111, projection='3d')
    ax11 = fig11.add_subplot(111, projection='3d')
    ax2 = fig2.add_subplot(111, projection='3d')
    ax1.view_init(18, -60)
    ax10.view_init(18, -60)
    ax11.view_init(18, -60)
    ax2.view_init(15, 45)

    # Define the color and transparency of the rectangles
    color = (0, 0, 1, 0.1)
    edge_color = (1, 1, 1, 1)
    slightly_stronger_color = (0, 0, 1, 0.15)

    # Find the minimum and maximum values for x and y at depth 0
    min_x_1 = min([tile[0] for tile in tiles if tile[2] == 0])
    max_x_1 = max([tile[0] for tile in tiles if tile[2] == 0])
    min_y_1 = min([tile[1] for tile in tiles if tile[2] == 0])
    max_y_1 = max([tile[1] for tile in tiles if tile[2] == 0])

    # Find the limits at depth DEPTH_STEP
    min_x_2 = min([tile[0] for tile in tiles if tile[2] == DEPTH_STEP])
    max_x_2 = max([tile[0] for tile in tiles if tile[2] == DEPTH_STEP])
    min_y_2 = min([tile[1] for tile in tiles if tile[2] == DEPTH_STEP])
    max_y_2 = max([tile[1] for tile in tiles if tile[2] == DEPTH_STEP])

    # Find the minimum and maximum values for x and y at depth 2 * DEPTH_STEP
    min_x_3 = min([tile[0] for tile in tiles if tile[2] == 2 * DEPTH_STEP])
    min_y_3 = min([tile[1] for tile in tiles if tile[2] == 2 * DEPTH_STEP])

    # Generate first plot with just a representation of the tiling
    for tile in tiles:
        x, y, z, dx, dy, dz = tile
        if z <= 2 * DEPTH_STEP:
            if (z == DEPTH_STEP and x == 2 and y == 2) or (z == DEPTH_STEP * 2 and x == min_x_3 and y == min_y_3):
                # Draw the rectangle at the highest zoom level
                ax1.bar3d(x, y, z, dx - DIST_STEP, dy - DIST_STEP, -DEPTH_STEP, color=slightly_stronger_color,
                          edgecolor=edge_color)
            elif not ((z == DEPTH_STEP and (x == min_x_2 or x == max_x_2 or y == min_y_2 or y == max_y_2)) or
                      (z == 0 * 2 and (x == min_x_1 or x == max_x_1 or y == min_y_1 or y == max_y_1)) or
                      (z == 0 and (x == min_x_1 + 1 or x == max_x_1 - 1 or y == min_y_1 + 1 or y == max_y_1 - 1))):
                ax1.bar3d(x, y, z, dx - DIST_STEP, dy - DIST_STEP, dz, color=color, edgecolor=edge_color)
            else:
                continue

    # Generate partial plots with a representation of the tiling.
    # The first plot has only the first level of the tiling.
    for tile in tiles:
        x, y, z, dx, dy, dz = tile
        if z <= 2 * DEPTH_STEP:
            if (z == DEPTH_STEP and x == 2 and y == 2) or (z == DEPTH_STEP * 2 and x == min_x_3 and y == min_y_3):
                # Draw the rectangle at the highest zoom level
                ax10.bar3d(x, y, z, dx - DIST_STEP, dy - DIST_STEP, 0, color=(1, 1, 1, 0), edgecolor=(1, 1, 1, 0))
            if not ((z == DEPTH_STEP and (x == min_x_2 or x == max_x_2 or y == min_y_2 or y == max_y_2)) or
                    (z == 0 * 2 and (x == min_x_1 or x == max_x_1 or y == min_y_1 or y == max_y_1)) or
                    (z == 0 and (x == min_x_1 + 1 or x == max_x_1 - 1 or y == min_y_1 + 1 or y == max_y_1 - 1))):
                if z == 2 * DEPTH_STEP:
                    ax10.bar3d(x, y, z, dx - DIST_STEP, dy - DIST_STEP, dz, color=color, edgecolor=edge_color)
                else:
                    ax10.bar3d(x, y, z, dx - DIST_STEP, dy - DIST_STEP, dz, color=(1, 1, 1, 0), edgecolor=(1, 1, 1, 0))
            else:
                continue

    # The second plot has the first and second levels of the tiling.
    for tile in tiles:
        x, y, z, dx, dy, dz = tile
        if z <= 2 * DEPTH_STEP:
            if z == DEPTH_STEP * 2 and x == min_x_3 and y == min_y_3:
                # Draw the rectangle at the highest zoom level
                ax11.bar3d(x, y, z, dx - DIST_STEP, dy - DIST_STEP, -DEPTH_STEP, color=slightly_stronger_color,
                           edgecolor=edge_color)
            elif not ((z == DEPTH_STEP and (x == min_x_2 or x == max_x_2 or y == min_y_2 or y == max_y_2)) or
                      (z == 0 * 2 and (x == min_x_1 or x == max_x_1 or y == min_y_1 or y == max_y_1)) or
                      (z == 0 and (x == min_x_1 + 1 or x == max_x_1 - 1 or y == min_y_1 + 1 or y == max_y_1 - 1))):
                if z == 2 * DEPTH_STEP or z == DEPTH_STEP:
                    ax11.bar3d(x, y, z, dx - DIST_STEP, dy - DIST_STEP, dz, color=color, edgecolor=edge_color)
                else:
                    ax11.bar3d(x, y, z, dx - DIST_STEP, dy - DIST_STEP, dz, color=(1, 1, 1, 0), edgecolor=(1, 1, 1, 0))
            else:
                continue

    # Find the limits of the plots at all depths
    min_values_x = [1000, 1000, 1000, 1000, 1000]
    min_values_y = [1000, 1000, 1000, 1000, 1000]
    max_values_x = [-1000, -1000, -1000, -1000, -1000]
    max_values_y = [-1000, -1000, -1000, -1000, -1000]

    for tile in tiles:
        x, y, z, dx, dy, dz = tile
        i = int(z / DEPTH_STEP)
        if i != 0 and i != 1:
            min_values_x[i] = min(min_values_x[i], x)
            min_values_y[i] = min(min_values_y[i], y)
            max_values_x[i] = max(max_values_x[i], x + dx - DIST_STEP_2)
            max_values_y[i] = max(max_values_y[i], y + dy - DIST_STEP_2)
        elif i == 1:
            min_values_x[i] = min(min_values_x[i], x + dx)
            min_values_y[i] = min(min_values_y[i], y + dx)
            max_values_x[i] = max(max_values_x[i], x - DIST_STEP_2)
            max_values_y[i] = max(max_values_y[i], y - DIST_STEP_2)
        else:
            min_values_x[i] = min(min_values_x[i], x + 2 * dx)
            min_values_y[i] = min(min_values_y[i], y + 2 * dy)
            max_values_x[i] = max(max_values_x[i], x - dx - DIST_STEP_2)
            max_values_y[i] = max(max_values_y[i], y - dy - DIST_STEP_2)

    # Plot surfaces between one depth and the next
    for i in range(4, 0, -1):
        X = np.array([[min_values_x[i], max_values_x[i], max_values_x[i], min_values_x[i]],
                      [min_values_x[i - 1], max_values_x[i - 1], max_values_x[i - 1], min_values_x[i - 1]]])
        Y = np.array([[min_values_y[i], min_values_y[i], max_values_y[i], max_values_y[i]],
                      [min_values_y[i - 1], min_values_y[i - 1], max_values_y[i - 1], max_values_y[i - 1]]])
        Z = np.array([[i * DEPTH_STEP, i * DEPTH_STEP, i * DEPTH_STEP, i * DEPTH_STEP],
                      [(i - 1) * DEPTH_STEP, (i - 1) * DEPTH_STEP, (i - 1) * DEPTH_STEP, (i - 1) * DEPTH_STEP]])
        ax2.plot_surface(X, Y, Z, color=color)

    # Deactivate grid and axis
    ax1.grid(False)
    ax1.axis('off')
    ax10.grid(False)
    ax10.axis('off')
    ax11.grid(False)
    ax11.axis('off')
    ax2.grid(False)
    ax2.axis('off')

    # Save the plots
    if not os.path.exists('tiling_plots'):
        os.makedirs('tiling_plots')
    fig1.savefig('tiling_plots/tiling1.png', dpi=500)
    fig2.savefig('tiling_plots/tiling2.png', dpi=500)
    fig10.savefig('tiling_plots/tiling1-0.png', dpi=500)
    fig11.savefig('tiling_plots/tiling1-1.png', dpi=500)


if __name__ == "__main__":
    # Get tiles
    tiles = get_tiles(TILE_X, TILE_Y, ZOOM_LEVEL, MAX_ZOOM_LEVEL)
    # Check that there are no duplicates
    assert len(tiles) == len(set([(tile['x'], tile['y'], tile['zoom']) for tile in tiles]))

    # Define list of tiles to plot
    tiles_for_plot = []

    # Find the minimum x and y values at the highest zoom level
    min_tile_x_max_zoom_level = min([tile['x'] for tile in tiles if tile['zoom'] == MAX_ZOOM_LEVEL])
    min_tile_y_max_zoom_level = min([tile['y'] for tile in tiles if tile['zoom'] == MAX_ZOOM_LEVEL])
    for tile in tiles:
        if tile['zoom'] == MAX_ZOOM_LEVEL:
            tiles_for_plot.append((tile['x'] - min_tile_x_max_zoom_level,
                                   tile['y'] - min_tile_y_max_zoom_level, 0, 1, 1, 0))

    for tile in tiles:
        if tile['zoom'] == MAX_ZOOM_LEVEL - 1:
            # Find tile at next zoom level
            tile_x_next_zoom_level = tile['x'] * 2
            tile_y_next_zoom_level = tile['y'] * 2
            # Place the tile over the 4 tiles it generates at the next zoom level
            tiles_for_plot.append((tile_x_next_zoom_level - min_tile_x_max_zoom_level,
                                   tile_y_next_zoom_level - min_tile_y_max_zoom_level,
                                   DEPTH_STEP, 2, 2, 0))

    for tile in tiles:
        if tile['zoom'] == MAX_ZOOM_LEVEL - 2:
            # Find tile at next zoom level
            tile_x_next_zoom_level = tile['x'] * 4
            tile_y_next_zoom_level = tile['y'] * 4
            tiles_for_plot.append((tile_x_next_zoom_level - min_tile_x_max_zoom_level,
                                   tile_y_next_zoom_level - min_tile_y_max_zoom_level,
                                   2 * DEPTH_STEP, 4, 4, 0))

    # Get tiles at previous zoom level
    tiles_prev_zoom_level = get_tiles_from_prev_zoom_level(TILE_X, TILE_Y, ZOOM_LEVEL)

    # Apply the displacement to all tiles
    for tile_prev_zoom_level in tiles_prev_zoom_level:
        tiles_for_plot.append((tile_prev_zoom_level['x'] * 8 - min_tile_x_max_zoom_level,
                               tile_prev_zoom_level['y'] * 8 - min_tile_y_max_zoom_level,
                               3 * DEPTH_STEP, 8, 8, 0))

    # Get tiles at previous zoom level of the previous zoom level
    tiles_prev_prev_zoom_level = get_tiles_from_prev_zoom_level(TILE_X // 2, TILE_Y // 2, ZOOM_LEVEL - 1)

    # Apply the displacement to all tiles
    for tile_prev_prev_zoom_level in tiles_prev_prev_zoom_level:
        tiles_for_plot.append((tile_prev_prev_zoom_level['x'] * 16 - min_tile_x_max_zoom_level,
                               tile_prev_prev_zoom_level['y'] * 16 - min_tile_y_max_zoom_level,
                               4 * DEPTH_STEP, 16, 16, 0))

    # Plot tiles
    plot_tiles(tiles_for_plot)
