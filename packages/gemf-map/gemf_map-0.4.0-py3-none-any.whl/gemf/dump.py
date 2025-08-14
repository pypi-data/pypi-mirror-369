def lonlat2xy(lon, lat, zoom):
    """Convert longitude and latitude to x and y coordinates of a tile."""
    lat_rad = math.radians(lat)
    n = 2 ** zoom
    xtile = int((lon + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)  # asinh(tan(x)) = log(tan(x) + sec(x))
    return xtile, ytile

def filter_tiles_between(z, xmin, ymin, xmax, ymax):
    """Get all tiles in a rectangular area."""
    return sorted([(z, x_, y_) for x_, y_ in itertools.product(range(xmin, xmax+1), range(ymin, ymax+1))])


# class TileCollection
@staticmethod
def grid_idx2xy(z: int, idx: int):
    idx = validate_int(idx)
    if (idx >= 2**(2*z)) and (idx >= 0): raise IndexError(f"At zoom {z}, index {idx} out of bounds for number of tiles {2**(2*z)}")
    y, x = divmod(idx, n:=2**z)
    return x, y

# class TileRange
@classmethod
def from_limits(cls, z: int, xmin: int, xmax: int, ymin: int, ymax: int, tile: Type[TileBase] = TileBase, sort: bool = True, *args, **kwargs) -> None:
    """"""
    z, xmin, xmax, ymin, ymax = validate_int([z, xmin, xmax, ymin, ymax])

    xs = [x for x in range(xmin, xmax+1)]
    ys = [y for y in range(ymin, ymax+1)]

    tiles = [tile(z, x, y, *args, **kwargs) for x, y in itertools.product(xs, ys)]
    return cls(z, tiles, sort)




class GEMFTileBase:
    """
    Base class representing a single tile in the GEMF ecosystem.
    Intended to be used as a base class in combination with classes inheriting from `TileBase`.
    """
    def __init__(self, verbose: bool = VERBOSE) -> None:
        self._verbose = verbose

    def __len__(self) -> int:
        return len(self.load_bytes())

    def to_dict(self) -> str: return str(self)

    def write(self, f):
        if self._verbose: print("Writing data...")
        data_bytes = self.load_bytes()
        f.write(data_bytes)



class GEMFDataSectionOld(GEMFList):
    """
    Sequential aggregate of encoded tile data as specified in section '4. Data Area' of the format specification.

    This class is lazy, i.e. the tile data is not stored into memory upon creation. It only serves as a utility
    """
    def __init__(self, data: list[GEMFTile | GEMFBufferTile]) -> None:
        super().__init__(data)


import inspect

def kwargify(loc):
    curr_init = getattr(loc["__class__"], "__init__")
    params = inspect.signature(curr_init).parameters
    kwargs = {key: loc[key] for key in params if key != "self"}
    return kwargs

class A:
    def __init__(self, a, **kwargs) -> None:        # A needs to accept kwargs to pass down the mro() chain
        print("init A", locals())
        self.a = a
        super().__init__(**kwargs)                  # A is not end-of-inheritance: kwargs important to pass parameters down mro() chain

class B:
    def __init__(self, b, **kwargs) -> None:        # B is "end of inheritance chain" -> **kwargs to "swallow" excess parameters, leave if excess parameters are not supported
        print("init B", locals())
        self.b = b
        super().__init__()                          # B is "end of inheritance chain" -> does not need to pass on kwargs

class C(A, B):
    def __init__(self, a, b) -> None:
        print("init C")
        super().__init__(**kwargify(locals()))      # all parameters have to be consumed (rest will be passed to object.__init__)

print("mro:", C.mro())
c = C(1, 2)
print(c.__dict__)
print("a:", c.a)
print("b:", c.b)


# class GEMF
def _read_datasection(self, f, headerinfo: HeaderInfo, sourcedata: SourceData, rangedata: RangeData, rangedetails: RangeDetails):
    ADDRESS = len(headerinfo) + len(sourcedata) + len(rangedata)
    f.seek(ADDRESS)

    data = GEMFDataSection([])
    for rangedetail in rangedetails:
        f.seek(rangedetail.address)
        tile_bytes = f.read(rangedetail.length)

        range_idx = rangedetail._range_idx
        tile_idx = rangedetail._tile_idx

        range_ = rangedata[range_idx]

        z, x, y = range_.get_zxy(tile_idx)
        tile = GEMFBufferTile(z, x, y, range_idx, tile_idx, tile_bytes)
        data.append(tile)

    return data

def validate_int(values: Union[List[Any], Any]):
    """If possible, value(s) will be cast to a Python int. If not, will raise a `ValueError`."""
    if not (isinstance(values, int) or all([isinstance(val_, int) for val_ in values])):
        raise ValueError(f"All values must be of type `int`; types: {[type(val) for val in values]}")
    return values
