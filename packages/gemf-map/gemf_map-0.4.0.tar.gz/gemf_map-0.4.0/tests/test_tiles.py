import pytest

import mercantile
import numpy as np

from gemf.tiles import SlippyTileMap


# TODO: use https://mercantile.readthedocs.io/en/stable/api/mercantile.html to validate tile logic?

np.random.seed(123)

N_points = 100
coords = np.random.rand(N_points, 2) * 2 - 1
coords[:, 0] *= 180     # lon
coords[:, 1] *= 85      # lat (mercator bound to ~85deg)

@pytest.mark.parametrize("zoom", list(range(8)))
@pytest.mark.parametrize("lon, lat", coords)
def test_slipp_tile_map(zoom, lon, lat):
    x_tile, y_tile = SlippyTileMap.lonlat_to_tile(zoom, lon, lat)
    tile = mercantile.tile(lon, lat, zoom)
    assert x_tile == tile.x, "Coordinate x of tile not equal to mercantile"
    assert y_tile == tile.y, "Coordinate y of tile not equal to mercantile"
