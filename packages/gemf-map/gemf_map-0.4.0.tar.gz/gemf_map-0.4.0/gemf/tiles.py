"""
This submodule contains supportive functionality to work with tiles contained in a `.gemf` file.
"""

import math
import os
import re
from copy import copy

import itertools
from typing import List, Literal, Optional, Union, Tuple

from gemf.utils import BYTE_STR_JPG_END, BYTE_STR_JPG_START, BYTE_STR_PNG, FORMAT_PATTERNS, get_image_format, listfiles


def validate_zxy(z: int, x: int, y: int):
    """All values need to be castable to int, non-negative. `x` and `y` must be smaller than 602**`z`."""
    n = 2**z
    assert z >= 0 and x >= 0 and y >= 0, "z, x, y must be non-negative."
    assert (0 <= x < n) and (0 <= y < n), f"At zoom {z}, x ({x}) and y ({y}) must be smaller than 2**z = {2**z}."
    assert isinstance(z, int) and isinstance(x, int) and isinstance(y, int), f"All values must be of type `int`"
    return z, x, y


class TileBase:
    """Base class for tiles."""
    def __init__(self, z: int, x: int, y: int, allow_invalid: bool = False, *args, **kwargs) -> None:
        if not allow_invalid: z, x, y = validate_zxy(z, x, y)

        self.z = z
        self.x = x
        self.y = y

    def __str__(self): return f"Tile (Z={self.z}, X={self.x}, Y={self.y})"
    def __repr__(self): return f"Tile ({self.z}, {self.x}, {self.y})"
    def __eq__(self, other): return (self.z == other.z) and (self.x == other.x) and (self.y == other.y)
    def __lt__(self, other): return (self.z < other.z) or (self.z == other.z and (self.x < other.x)) or ((self.z == other.z and (self.x == other.x)) and self.y < other.y)

    @property
    def size_bytes(self):
        raise NotImplementedError(f"TileBase subclass '{self.__class__.__name__}' must specify a `size_bytes` method.")

    def neighbor(self, dx: int = 0, dy: int = 0, allow_invalid: bool = False):
        """
        Get a neighboring tile.

        # Parameters
        - `dx`: neighbor distance in x-direction
        - `dy`: neighbor distance in y-direction
        - `allow_invalid`: whether tiles outside of the range [0, 2**z) should be allowed
        """
        if not allow_invalid:
            n = 2**self.z
            if not ((0 <= (self.x+dx) < n) and (0 <= (self.y+dy) < n)): raise ValueError(f"Invalid neighbor: at zoom {self.z}, x ({self.x}) and y ({self.y}) must be smaller than 2**z = {2**self.z}.")

        n = copy(self)
        n.x = self.x+dx
        n.y = self.y+dy
        return n


class NamedTileBase(TileBase):
    """Base class for named tiles, for tiles that either are already present on disk, or tiles that are intended to be saved to disk."""
    def __init__(self, z: int, x: int, y: int, name: str, format: str, allow_invalid: bool = False) -> None:
        super().__init__(z, x, y, allow_invalid)
        self.name = name
        self.format = format

    # @staticmethod
    # def parse_tilename(tilename: str):
    #     """Extract name, z, x, y and tile format from a file. Expected format: `TILENAME_Z_X_Y.FORMAT`."""
    #     name, z, x, y, format = re.search(r"(.+?)_(\d+?)_(\d+?)_(\d+?)[.](.+)", os.path.basename(tilename)).groups()
    #     return name, int(z), int(x), int(y), format

    # TODO: not applicable for "reference objects" with self.format unknown until loading data
    def get_filename(self) -> str:
        """Re-build filename."""
        filename = f"{self.name}_{self.z}_{self.x}_{self.y}.{self.format}"
        return filename

    def save(self, tiledir: str, determine_image_format: bool = True):
        """Save tile contents to file. Classes inheriting from `NamedTileBase` are expected to implement the `load_bytes()` method, returning the image contents as a byte object."""

        data_bytes = self.load_bytes()
        if determine_image_format and self.format is None:
            self.format = get_image_format(data_bytes, FORMAT_PATTERNS)

        with open(os.path.join(tiledir, self.get_filename()), "wb") as f:
            f.write(data_bytes)


class DiskTile(NamedTileBase):
    """A regular tile, present on disk."""
    def __init__(self, z: int, x: int, y: int, tiledir: str, name: str, format: str, allow_invalid: bool = False) -> None:
        self.name = name
        self.format = format
        self.tiledir = tiledir
        super().__init__(z, x, y, name, format, allow_invalid)

    @property
    def size_bytes(self):
        return os.stat(self.get_filepath()).st_size

    @classmethod
    def from_file(cls, tile_file: str) -> None:
        """Create a `Tile` object from a file on disk."""
        return cls(**DiskTile.parse_filepath(tile_file), allow_invalid=False)

    # TODO: what does python staticmethod even do?
    @staticmethod
    def parse_filepath(tile_file: str) -> tuple:
        """Parse filepath of a tile into its components, in the order necessary for the `Tile` constructor."""
        tiledir = os.path.dirname(tile_file)
        name, z, x, y, format = re.search(r"(.+?)_(\d+?)_(\d+?)_(\d+?)[.](.+)", os.path.basename(tile_file)).groups()
        return {"z": int(z), "x":  int(x), "y":  int(y), "tiledir":  tiledir, "name":  name, "format": format}

    @staticmethod
    def compose_filepath(z, x, y, tiledir, name, format):
        filename = f"{name}_{z}_{x}_{y}.{format}"
        return os.path.join(tiledir, filename)

    def load_bytes(self):
        """Load the tile's image content as bytes."""
        with open(self.get_filepath(), "rb") as f:
            data_bytes = f.read()
        return data_bytes

    def get_filepath(self) -> str:
        """Return the whole filepath to the tile file."""
        return os.path.join(self.tiledir, self.get_filename())


class BufferTile(NamedTileBase):
    """
    A tile with its image contents in memory. Useful for reading tile images from map files and storing them.

    # Parameters
    - `z, x, y`: tile coordinates
    - `data`: tile data as bytes
    - `name`: an optional name for storing the tile contents to file
    - `format`: an optional image format used as file ending when storing the tile to file
    - `allow_invalid`: whether to raise an error when the tile coordinates are invalid; by default raises an error
    """
    def __init__(self, z: int, x: int, y: int, data: bytes, name: str = "tile", format: Optional[str] = None, allow_invalid: bool = False) -> None:

        # if format == "get_image_format": format = get_image_format(data, format_patterns=FORMAT_PATTERNS, raise_errors=True)
        super().__init__(z, x, y, name, format, allow_invalid)

        self.data = data

    def load_bytes(self):
        """Return the binary image data."""
        return self.data


class EmptyTile(BufferTile):
    """Represents an empty tile. Optionally, magic numbers or other "empty tile data" may be passed via the `data` parameter."""
    def __init__(self, z: int, x: int, y: int, data: bytes = bytes(), name: str = "tile", allow_invalid: bool = False) -> None:
        super().__init__(z, x, y, data, name, allow_invalid)


class EmptyPNG(EmptyTile):
    # TODO: remove?
    """Represents a tile with zero-length PNG data."""
    def __init__(self, z, x, y, allow_invalid: bool = False) -> None:
        super().__init__(z, x, y, bytes(), name="empty_png", allow_invalid=allow_invalid)

    def load_bytes(self): return BYTE_STR_PNG


class EmptyJPG(EmptyTile):
    # TODO: remove?
    """Represents a tile with zero-length JPG data."""
    def __init__(self, z, x, y, allow_invalid: bool = False) -> None:
        super().__init__(z, x, y, bytes(), name="empty_jpg", allow_invalid=allow_invalid)

    def load_bytes(self): return BYTE_STR_JPG_START + BYTE_STR_JPG_END


# TODO: need to make abstract for all tile types
def get_tile_row(start: DiskTile, end: DiskTile, allow_invalid: bool = False):
    """Get a row of tiles. Used to determine rectangular tile areas."""
    return [DiskTile(start.z, x_, start.y, start.tiledir, start.name, start.format, allow_invalid) for x_ in range(start.x, end.x+1)]


class TileCollection:
    """An arbitrary collection of tiles."""
    def __init__(self, tiles: List[DiskTile], sort: bool = True) -> None:
        if sort:
            self.tiles = sorted(tiles, key=sort if (sort is not True) else None)
        else:
            self.tiles = tiles
        self.is_sorted = True if sort else False

    def __len__(self): return len(self.tiles)
    def __iter__(self): return iter(self.tiles)
    def __repr__(self): return f"{type(self).__name__}: {str(self.tiles)}"

    def __add__(self, other): return TileCollection([*self.tiles, *other.tiles], sort=self.is_sorted and other.is_sorted)

    def __getitem__(self, index: Union[Tuple[int], int]):

        if isinstance(index, int):
            return self.tiles[index]
        else:
            z, x, y = index
            return self.get_tile(z, x, y)

    @classmethod
    def from_tiledir(cls, tile_dir):
        tile_files = listfiles(tile_dir, formats=["png", "jpg"])
        tiles = [DiskTile.from_file(os.path.join(tile_dir, tile_file)) for tile_file in tile_files]
        return cls(tiles)

    @staticmethod
    def grid_xy2idx(z: int, x: int, y: int):
        z, x, y = validate_zxy(z, x, y)
        n = 2**z
        return y*n + x

    def get_index(self, z: int, x: int, y: int):
        try:
            return self.tiles.index(tile := DiskTile(z,x,y))
        except AttributeError as exc:
            raise AttributeError(f"{tile} not in {(type(self).__name__)}") from exc

    def get_tile(self, z: int, x: int, y: int):
        return self.tiles[self.get_index(z, x, y)]

    def to_tile_levels(self):
        levels = []
        zs = {tile.z for tile in self.tiles}
        for z in zs:
            tiles_z = self.filter_tiles("z", z)
            tilelevel = TileLevel(z, tiles_z)
            levels.append(tilelevel)
        return levels

    def to_tileranges(self, mode: Literal["split", "fill"] = "fill", **kwargs):
        """
        Convert an unstructured `TileCollection` into rectangular `TileRange` object(s).
        First, the collection will be split into different (z) levels, then each level is split into one or more ranges,
        where the conversion behavior is controlled by the parameter `mode`. Further `kwargs` are passed to `TileLevel.make_range()`.
        """
        levels = self.to_tile_levels()
        return [range for level in levels for range in level.make_range(mode, **kwargs)]

    def filter_tiles(self, key, val, tiles=None): return [tile for tile in (tiles or self.tiles) if getattr(tile, key) == val]


class TileLevel(TileCollection):
    """A collection of tiles of equal zoom level."""
    def __init__(self, z: int, tiles: List[DiskTile], sort: bool = True) -> None:
        self.z = z

        xs = [tile.x for tile in tiles]
        ys = [tile.y for tile in tiles]

        self.xmin = min(xs)
        self.xmax = max(xs)
        self.ymin = min(ys)
        self.ymax = max(ys)
        super().__init__(tiles, sort)

    def __repr__(self): return f"{type(self).__name__} (z={self.z}): {str(self.tiles)}"

    @classmethod
    def from_tiledir(cls, tile_dir: str):
        """Create a `TileLevel` from all tile images present in `tile_dir`."""
        tc = TileCollection.from_tiledir(tile_dir)
        return tc.to_tile_levels()

    def is_rect(self):
        """Whether the tiles in the `TileLevel` form a complete rectangular area."""
        tile_coords = {(tile.x, tile.y) for tile in self.tiles}
        tiles_rect = itertools.product(range(self.xmin, self.xmax+1), range(self.ymin, self.ymax+1))
        return all([(xy in tile_coords) for xy in tiles_rect])

    def _split_level(self, **kwargs):
        """Split the `TileLevel` into (multiple) `TileRange` objects by splitting."""
        rects = []
        tiles_non_assigned = sorted(copy(self.tiles))

        while len(tiles_non_assigned):

            curr_rect = []
            curr_tile = tiles_non_assigned[0]
            curr_start = curr_tile
            curr_rect.append(curr_tile)
            tiles_non_assigned.remove(curr_tile)

            while (curr_tile := curr_tile.neighbor(dx=1, allow_invalid=True)) in tiles_non_assigned:
                curr_rect.append(curr_tile)
                tiles_non_assigned.remove(curr_tile)
            next_row = get_tile_row(curr_start.neighbor(dy=1, allow_invalid=True), curr_tile.neighbor(dx=-1, dy=1, allow_invalid=True), allow_invalid=True)
            while all([(tile_ in tiles_non_assigned) for tile_ in next_row]):
                curr_rect.extend(next_row)
                for tile_ in next_row: tiles_non_assigned.remove(tile_)
                next_row = get_tile_row(next_row[0].neighbor(dy=1), next_row[-1].neighbor(dy=1))

            rects.append(TileRange(self.z, curr_rect))

        return rects

    def _fill_level(self, **kwargs):
    # def _fill_level(self, empty_format: Literal["none", "png", "jpg"]):
        """
        Fill the `TileLevel` by adding empty filler tiles to create a single `TileRange`.
        File content of
        """
        # empty_class = getattr(sys.modules[__name__], f"Empty{empty_format.upper()}")
        ar = AbstractRange(self.z, self.xmin, self.xmax, self.ymin, self.ymax)
        tiles = []
        for tile in ar:
            if tile in self:
                tiles.append(tile)
            else:
                tiles.append(EmptyTile(tile.z, tile.x, tile.y, **kwargs))
                # tiles.append(empty_class(tile.z, tile.x, tile.y))

        return TileRange(self.z, tiles)


    def make_range(self, mode: Literal["split", "fill"] = "fill", **kwargs):
        """
        Convert a `TileLevel` into (multiple) `TileRange` objects.

        # Modes:
        - fill: complete the `TileLevel` with empty dummy tiles. Further `kwargs` are passed to the constructor of `EmptyTile`.
        - split: split the `TileLevel` into multiple smaller, rectangular sets. Further `kwargs` are ignored.
        """
        # if len(self.tiles) == 1: return [self]
        # TODO: test if works with single tile TileLevel?

        if mode == "split":
            return self._split_level(**kwargs)
        elif mode == "fill":
            return self._fill_level(**kwargs)
        else:
            raise ValueError(f"Mode {mode} not supported.")


    def print_details(self):
        """Print a comprehensive summary of the `TileLevel`."""
        print(f"{type(self).__name__} ({len(self.tiles)}) | Z = {self.z} | is_rect = {self.is_rect()}")
        print(f"  X: {self.xmin} - {self.xmax}")
        print(f"  Y: {self.ymin} - {self.ymax}")
        for tile in self.tiles: print("   ", tile)


class TileRange(TileLevel):
    """A collection of tiles which form a rectangular area."""
    def __repr__(self): return f"{type(self).__name__} z={self.z} lim={((self.xmin, self.xmax, self.ymin, self.ymax))}"

    def __init__(self, z: int, tiles: List[DiskTile], sort: bool = True) -> None:
        super().__init__(z, tiles, sort)

        if not self.is_rect(): raise RuntimeError("Tried to instantiate `TileRange` with non-rectangular set of tiles.")


# TODO: unify abstract range and slippytlemap
class AbstractRange:
    """
    Class to collect range arithmetic operations. Tiles are not stored explicitly.

    # Params
    - `z`: the range's zoom level
    - `xmin`: the range's minimum x coordinate
    - `xmax`: the range's maximum x coordinate
    - `ymin`: the range's minimum y coordinate
    - `ymax`: the range's maximum y coordinate
    - `major`: range traversion mode, either 'row' or 'col'; default 'row'


    #### Traversing the range:
    - row: An order like (x0, y0), (x1, y0), ..., (xN, y0) is assumed
    - col: An order like (x0, y0), (x0, y1), ..., (x0, yN) is assumed
    """
    def __init__(self, z: int, xmin: int, xmax: int, ymin: int, ymax: int, major: Literal["row", "col"] = "row") -> None:
        self.z = z
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

        self.major = major

    def __len__(self) -> int:
        cols = self.xmax - self.xmin + 1
        rows = self.ymax - self.ymin + 1
        return cols * rows

    def __iter__(self):
        for index in range(len(self)):
            yield self[index]

    def __getitem__(self, index: int) -> TileBase:
        if index < 0:
            index = len(self) + index
            print("index_new", index)

        if self.major == "row":
            cols = self.xmax - self.xmin + 1
            y_rel, x_rel = divmod(index, cols)
        elif self.major == "col":
            rows = self.ymax - self.ymin + 1
            x_rel, y_rel = divmod(index, rows)
        else:
            raise ValueError("Only supports row-major or column-major ordering.")

        x = self.xmin + x_rel
        y = self.ymin + y_rel
        return TileBase(self.z, x, y)


    @staticmethod
    def index2xy(index: int, xmin: int, xmax: int, ymin: int, ymax: int, major: Literal["row", "col"] = "row"):

        if index > (length := AbstractRange.len(xmin, xmax, ymin, ymax)):
            raise IndexError(f"Index {index} larger than number of tiles in range {length}")

        if major == "row":
            cols = xmax - xmin + 1
            y_rel, x_rel = divmod(index, cols)
        elif major == "col":
            rows = ymax - ymin + 1
            x_rel, y_rel = divmod(index, rows)
        else:
            raise ValueError("Only supports row-major or column-major ordering.")

        x = xmin + x_rel
        y = ymin + y_rel
        return x, y


    @staticmethod
    def xy2index(x: int, y: int, xmin: int, xmax: int, ymin: int, ymax: int, major: Literal["row", "col"] = "row"):

        if not (xmin <= x <= xmax) or not (ymin <= y <= ymax):
            raise IndexError(f"Tile coordinate {(x, y)} not within range")

        dx = x - xmin
        dy = y - ymin

        if major == "row":
            cols = xmax - xmin + 1
            index = dy * cols + dx
            # y_rel, x_rel = divmod(index, cols)
        elif major == "col":
            rows = ymax - ymin + 1
            index = dx * rows + dy
        else:
            raise ValueError("Only supports row-major or column-major ordering.")

        return index


    @staticmethod
    def len(xmin: int, xmax: int, ymin: int, ymax: int) -> int:
        cols = xmax - xmin + 1
        rows = ymax - ymin + 1
        return cols * rows

    @staticmethod
    def get_tiles(z: int, xmin: int, xmax: int, ymin: int, ymax: int, **kwargs) -> List[Tuple[int, int, int]]:
        if not (0 <= xmin <= xmax < 2**z) or not (0 <= ymin <= ymax < 2**z):
            raise ValueError(f"Tile coordinates out of range for zoom {z}.")

        return [(z, x, y) for x in range(xmin, xmax + 1) for y in range(ymin, ymax + 1)]

    @staticmethod
    def intersection(
        coords1: Tuple[int, int, int, int],
        coords2: Tuple[int, int, int, int]
    ) -> Tuple[int, int, int, int]:
        xmin1, xmax1, ymin1, ymax1 = coords1
        xmin2, xmax2, ymin2, ymax2 = coords2
        xmin = max(xmin1, xmin2)
        xmax = min(xmax1, xmax2)
        ymin = max(ymin1, ymin2)
        ymax = min(ymax1, ymax2)

        if xmin > xmax or ymin > ymax:
            return None  # No intersection

        return xmin, xmax, ymin, ymax

    @staticmethod
    def bounds(z: int, xmin: int, xmax: int, ymin: int, ymax: int, major: Literal["row", "col"] = "row") -> Tuple[float, float, float, float]:
        """Return the ul_lon, ul_lat, br_lat, br_lon bounding box for a range."""
        range = AbstractRange(z, xmin, xmax, ymin, ymax, major=major)
        tl, br = range[0], range[-1]

        print("tl", tl)
        print("br", br)

        ul_lon, _, _, ul_lat = SlippyTileMap.bounds(tl.z, tl.x, tl.y)
        _, br_lat, br_lon, _ = SlippyTileMap.bounds(br.z, br.x, br.y)

        return ul_lon, ul_lat, br_lat, br_lon


class RangeCollection:
    def __call__(self, ranges: List[TileRange]):
        self.ranges = ranges


    def reindex(self, method: Literal["max_area"]):
        # TODO: implement (maybe max_area, row_major, col_major?)
        pass

    def _reindex_max_area(self):
        # google algo: find rectangular regions of max area in binary mask
        pass


class SlippyTileMap:
    # 0,0 at top left
    @staticmethod
    def lonlat_to_tile(zoom: int, lon: float, lat: float):
        lat_rad = math.radians(lat)
        n = 2 ** zoom
        x_tile = int((lon + 180.0) / 360.0 * n)
        y_tile = int((1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
        return x_tile, y_tile

    @staticmethod
    def tile_to_lonlat(zoom: int, x_tile: int, y_tile: int):
        # of top_left_corner
        n = 2 ** zoom
        lon = x_tile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y_tile / n)))
        lat = math.degrees(lat_rad)
        return lat, lon

    @staticmethod
    def bounds(zoom: int, x_tile: int, y_tile: int):
        # from mercantile
        Z2 = math.pow(2, zoom)

        ul_lon_deg = x_tile / Z2 * 360.0 - 180.0
        ul_lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y_tile / Z2)))
        ul_lat_deg = math.degrees(ul_lat_rad)

        lr_lon_deg = (x_tile + 1) / Z2 * 360.0 - 180.0
        lr_lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * (y_tile + 1) / Z2)))
        lr_lat_deg = math.degrees(lr_lat_rad)
        return ul_lon_deg, lr_lat_deg, lr_lon_deg, ul_lat_deg

    @staticmethod
    def get_parent_tile(zoom: int, x_tile: int, y_tile: int):
        # TODO: test
        return zoom-1, x_tile//2, y_tile//2

    @staticmethod
    def get_subtiles(zoom: int, x_tile: int, y_tile: int):
        # order tl, tr, bl, br
        return [(zoom+1, 2*x_tile+dx, 2*y_tile+dy) for dy in [0, 1] for dx in [0, 1]]

    @staticmethod
    def get_parent_tile_at_zoom(zoom: int, zoom_target: int, x_tile: int, y_tile: int):
        if zoom < zoom_target:
            raise ValueError("Target zoom can't be smaller than source zoom")

        while zoom > zoom_target:
            zoom, x_tile, y_tile = SlippyTileMap.get_parent_tile(zoom, x_tile, y_tile)
            zoom -= 1
        return zoom, x_tile, y_tile

    @staticmethod
    def get_subtile_at_zoom(zoom: int, zoom_target: int, x_tile: int, y_tile: int, subtile: Literal["tl", "tr", "bl", "br"]):
        if zoom > zoom_target:
            raise ValueError("Target zoom can't be larger than source zoom")

        subtile_idx = ["tl", "tr", "bl", "br"].index(subtile)
        while zoom < zoom_target:
            zoom, x_tile, y_tile = SlippyTileMap.get_subtiles(zoom, x_tile, y_tile)[subtile_idx]
            zoom += 1
        return zoom, x_tile, y_tile
