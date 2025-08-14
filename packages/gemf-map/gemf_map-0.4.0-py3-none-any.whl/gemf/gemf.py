"""
This submodule defines the core functionality of the package through the `GEMF` class.
"""

from collections import defaultdict
from concurrent.futures import as_completed
import os
import json
from typing import Dict, List, Callable, Tuple

from gemf.utils import kwargify, listdirs, to_json
from gemf.tiles import (
    AbstractRange,
    BufferTile,
    NamedTileBase,
    SlippyTileMap,
    DiskTile,
    TileBase,
    TileCollection,
    TileRange,
)

# TODO: rename RangeDetails RangeDetailList ? check specification for name

class SIZES:
    DATA = 4
    OFFSET = 8

    HEADER_INFO = DATA + OFFSET

    RANGE = 6 * DATA + OFFSET
    DETAIL = OFFSET + DATA


ENCODING = "ascii"
ENCODING_ERROR = "ignore"


class DetailsNotLoadedError(Exception):
    def __init__(self, **kwargs) -> None:
        super().__init__("`RangeDetails` have not been loaded. Call `gemf.load_details()` before or instantiate `GEMF` with `lazy = False`.", **kwargs)


# auxiliary methods, used to read encoded binary data
def _read_value(f, N):
    """Read N bytes from a binary file and return as int."""
    value_bytes = f.read(N)
    return int.from_bytes(value_bytes, "big")


def _read_int(f):
    """Read int as encoded in GEMF."""
    return _read_value(f, SIZES.DATA)


def _read_offset(f):
    """Read offset as encoded in GEMF."""
    return _read_value(f, SIZES.OFFSET)


def _read_string(f, N):
    """Read string as encoded in GEMF."""
    str_bytes = f.read(N)
    return str_bytes.decode(ENCODING)


# encoding utilities, used to write binary gemf file
def _encode_data(value):
    """Encode a data integer, i.e. as 4 bytes."""
    return (value).to_bytes(SIZES.DATA, "big")


def _encode_offset(value):
    """Encode an offset integer, i.e. as 8 bytes."""
    return (value).to_bytes(SIZES.OFFSET, "big")


def _encode_string(value):
    """Encode a string, with variable byte length."""
    return value.encode(ENCODING, ENCODING_ERROR)


# GEMF classes
class GEMFValueBase:
    """
    Base class defining basic GEMF type behavior. Python primitives are wrapped in
    custom GEMF classes for easier integration in the GEMF workflow.
    """

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return f"{type(self).__name__}: {super().__str__()}"

    def __len__(self):
        """Return the encoded size."""
        return len(self._encode(self))

    def write(self, f, *args, **kwargs):
        """Write the encoded value to a binary gemf file."""
        return f.write(self._encode(self), *args, **kwargs)


class GEMFIntBase(int, GEMFValueBase):
    """Base class for int-like GEMF types."""

    def __new__(cls, value: int, encoding_method: Callable[[int], None]):
        if not isinstance(value, int):
            raise TypeError("`value` must be of type `int`")
        obj = int.__new__(cls, value)
        obj._encode = encoding_method
        return obj


class GEMFInt(GEMFIntBase):
    """Class representing a 4 byte integer."""

    def __new__(cls, value: int) -> None:
        obj = GEMFIntBase.__new__(cls, value, _encode_data)
        return obj


class GEMFOffset(GEMFIntBase):
    """Class representing a 8 byte integer, aka 'offset'."""

    def __new__(cls, value: int) -> None:
        obj = GEMFIntBase.__new__(cls, value, _encode_offset)
        return obj


class GEMFString(GEMFValueBase, str):
    """Class representing a variable size string."""

    def __new__(
        cls, value: str, encoding: str = ENCODING, error: str = ENCODING_ERROR
    ) -> None:
        obj = str.__new__(cls, value)
        obj.encoding = encoding
        obj.error = error
        obj._encode = _encode_string
        return obj


class GEMFList:
    """An iterable of GEMF objects."""

    def __init__(self, items: list) -> None:
        self.items = items

    def __len__(self):
        """Sum of byte-length of member items."""
        return sum([len(item) for item in self.items])

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, idx):
        return self.items[idx]

    def to_dict(self, *args, **kwargs):
        """Return a list of dict-representation of the member items."""
        list_dict = []
        for item in self.items:
            if hasattr(item, "to_dict"):
                list_dict.append(item.to_dict())
            else:
                list_dict.append(to_json(item))
        return list_dict

    def __str__(self) -> str:
        return str(self.to_dict())

    def append(self, item):
        if len(self.items):
            assert isinstance(item, type(self[0])), "Items must be of equal type."
        return self.items.append(item)

    def extend(self, items):
        if len(self.items):
            assert all([isinstance(item, type(self[0])) for item in items]), (
                "Items must be of equal type."
            )
        return self.items.extend(items)

    def write(self, f, *args, **kwargs):
        """Sequentially write binary representation of member items."""
        for item in self.items:
            item.write(f, *args, **kwargs)


class GEMFSectionBase:
    """
    Base class representing a GEMF section.

    **Properties**
    - the length of a section equals the length of its binary representation.
    - the `write()` method is responsible for ultimately serializing the map as a binary GEMF file
    """

    def __len__(self):
        """
        The length of a section equals the length of its binary representation.
        It is the sum of the binary length of its children elements.
        """
        return sum([len(value) for key, value in self.__dict__.items() if not key.startswith("_")])

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.__dict__}"

    def to_dict(self, ignore_private: bool = True) -> dict:
        """
        Recursively build a dictionary representation of the GEMF structure.
        Attributes starting with an underscore are supressed by default.
        """
        out_dict = {}

        for key, el in self.__dict__.items():
            if ignore_private and key.startswith("_"):
                continue

            if hasattr(el, "to_dict"):
                out_dict[key] = el.to_dict(ignore_private)
            else:
                out_dict[key] = to_json(el)

        return out_dict

    def write(self, f, *args, **kwargs):
        """
        Recursively write the binary representation of the object and its child objects.
        Attributes starting with an underscore are not included in the serialization.
        """
        for key, val in self.__dict__.items():
            if key.startswith("_"):
                continue
            val.write(f, *args, **kwargs)


class ObjectDescriptor:
    """Utility class with the purpose of renaming general fieldnames of `GEMFList` to subclass-specific names."""

    def __init__(self, name) -> None:
        self.name = name

    def __get__(self, obj, objtype=None):
        value = getattr(obj, self.name)
        return value

    def __set__(self, obj, value):
        setattr(obj, self.name, value)


class GEMFListSectionBase(GEMFSectionBase):
    """
    Base class for GEMF sections which are comprised of two attributes:
    - a count of child elements
    - a list of child elements
    """

    _items = ObjectDescriptor("items")
    _num_items = ObjectDescriptor("num_items")

    def __init__(self, itemlist: GEMFList) -> None:
        self._num_items = GEMFInt(len(itemlist.items))
        self._items = itemlist

    def __getitem__(self, idx):
        return self._items[idx]

    def __iter__(self):
        return iter(self._items)


class HeaderInfo(GEMFSectionBase):
    """
    GEMF meta-information as specified in section '3.1 Overall Header' of the format specification.

    # Parameters
    - `GEMF version`: file format version
    - `tile_size`: size of contained tiles
    """

    def __init__(self, version: int, tile_size: int) -> None:
        self.version = GEMFInt(version)
        self.tile_size = GEMFInt(tile_size)


class GEMFSource(GEMFSectionBase):
    """
    A single GEMF source, aka tile provider (see section '3.2 Source Data')

    # Parameters
    - `index`: source index, 0-indexed
    - `name_length`: length of encoded source name
    - `name`: encoded source name
    """

    def __init__(self, index: int, name: str) -> None:
        self.index = GEMFInt(index)
        self.name_length = GEMFInt(len(name.encode(ENCODING, ENCODING_ERROR)))
        self.name = GEMFString(name)


class SourceList(GEMFList):
    """Wrap a list of `GEMFSource`s."""

    def __init__(self, sources: List[GEMFSource]) -> None:
        super().__init__(sources)


class SourceData(GEMFListSectionBase):
    """
    Information on the contained sources as specified in section '3.2 Source Data' of the format specification.

    # Parameters
    - `num_sources`: number of contained sources
    - `sources`: list of sources
    """

    # renaming the attributes of `GEMFListSectionBase` to adhere with the specification naming convention
    _num_items = ObjectDescriptor("num_sources")
    _items = ObjectDescriptor("sources")

    def __init__(self, sourcelist: SourceList) -> None:
        super().__init__(sourcelist)

    @classmethod
    def from_root(cls, root_dir: str):
        """Create a `SourceData` object from a root directory of tiles."""
        gemfsources = []
        for i, source_name in enumerate(listdirs(root_dir)):
            gemfsources.append(GEMFSource(i, source_name))

        return SourceData(SourceList(gemfsources))


class GEMFRange(GEMFSectionBase):
    """
    A single GEMF range, aka rectangular collection of tiles (see section '3.3 Range Data')

    # Parameters
    - `z`: the range's zoom level
    - `xmin`: the range's minimum x coordinate
    - `xmax`: the range's maximum x coordinate
    - `ymin`: the range's minimum y coordinate
    - `ymax`: the range's maximum y coordinate
    - `src_index`: the index of the corresponding source
    - `offset`: the start byte of the corresponding 'Range Detail' in the binary file
    """

    size = 6 * SIZES.DATA + SIZES.OFFSET; """Static attribute: size of a `GEMFRange` if serialized."""

    def __init__(
        self,
        z: int,
        xmin: int,
        xmax: int,
        ymin: int,
        ymax: int,
        src_index: int,
        details_offset: int,
        first_tile_idx: int,
    ) -> None:
        self.z = GEMFInt(z)
        self.xmin = GEMFInt(xmin)
        self.xmax = GEMFInt(xmax)
        self.ymin = GEMFInt(ymin)
        self.ymax = GEMFInt(ymax)
        self.src_index = GEMFInt(src_index)
        self.offset = GEMFOffset(details_offset)

        self._first_tile_idx = first_tile_idx

    def get_zxy(self, index: int):
        """Get the n-th tile of the range by index. Ranges are traversed in column-major order."""
        return self.z, *AbstractRange.index2xy(
            index, self.xmin, self.xmax, self.ymin, self.ymax, major="col"
        )


    @property
    def num_tiles(self):
        return AbstractRange.len(self.xmin, self.xmax, self.ymin, self.ymax)

    @property
    def bounds(self):
        return self.xmin, self.xmax, self.ymin, self.ymax


class RangeList(GEMFList):
    """Wrap a list of `GEMFRange`s."""

    def __init__(self, ranges: List[GEMFRange]) -> None:
        super().__init__(ranges)


# TODO: move outside of class?
def ranges_from_root(
    root_dir: str, sourcedata: SourceData, mode: str = "split", **kwargs
):
    range_dict = {}

    # collect tile ranges (aka rectangular collections of tiles)
    for i_source, source in enumerate(sourcedata.sources):
        tc = TileCollection.from_tiledir(os.path.join(root_dir, source.name))                                   # first, collect all tiles in source dir
        tileranges_ = tc.to_tileranges(mode=mode, **kwargs)                                                     # split collection into valid tileranges
        range_dict[i_source] = tileranges_

    return range_dict


class RangeData(GEMFListSectionBase):
    """
    Information on the contained ranges as specified in section '3.3 Range Data' of the format specification.

    # Parameters
    - `num_ranges`: number of contained ranges
    - `ranges`: list of ranges
    """

    # renaming the attributes of `GEMFListSectionBase` to adhere with the specification naming convention
    _num_items = ObjectDescriptor("num_ranges")
    _items = ObjectDescriptor("ranges")

    @classmethod
    def from_root(
        cls,
        root_dir: str,
        headerinfo: HeaderInfo,
        sourcedata: SourceData,
        mode: str = "split",
        **kwargs,
    ):
        """
        Create a `RangeData` object from the previously loaded GEMF objects.
        Additionally, return a list of `TileRange` objects, which are required for further GEMF creation steps.
        """

        range_dict = ranges_from_root(root_dir, sourcedata, mode=mode, **kwargs)
        return cls.from_ranges(range_dict, headerinfo, sourcedata)

    @classmethod
    def from_ranges(
        cls,
        range_dict: Dict[int, List[TileRange]],
        headerinfo: HeaderInfo,
        sourcedata: SourceData,
    ):
        """
        Create a `RangeData` object from the previously loaded GEMF objects.
        Additionally, return a list of `TileRange` objects, which are required for further GEMF creation steps.
        """
        tile_count = 0
        range_list = RangeList([])
        tileranges = []

        # traverse all source dirs
        for i_source, ranges in range_dict.items():
            num_ranges = len(ranges)

            OFFSET = (
                len(headerinfo)
                + len(sourcedata)
                + RangeData.size(num_ranges)
                + len(range_list)
            )  # initial offset for details based on previous sections and length of RangeData

            # iterate over all found tile ranges
            for range_ in ranges:
                # create corresponding GEMF object and collect objects
                gemf_range = GEMFRange(
                    range_.z,
                    range_.xmin,
                    range_.xmax,
                    range_.ymin,
                    range_.ymax,
                    i_source,
                    OFFSET,
                    tile_count,
                )
                tileranges.append(range_)
                range_list.append(gemf_range)

                # advance offset to block of range details, corresponding to the next range
                num_tiles = len(range_)
                OFFSET += num_tiles * RangeDetail.size
                tile_count += num_tiles

        rangedata = cls(range_list)
        return rangedata, tileranges

    @property
    def num_tiles(self):
        """Number of tiles contained in `RangeData`."""
        return sum([range.num_tiles for range in self.ranges])

    @staticmethod
    def size(num_ranges: int):
        """Pre-compute the size of a `RangeData` object if serialized."""
        return SIZES.DATA + num_ranges * GEMFRange.size


class RangeDetail(GEMFSectionBase):
    """
    A single GEMF range detail, aka tile info (see section '3.4 Range Details')

    **Note**: This implementation does not fully follow the paradigm described in the format specification. Since the concept of a range detail
      and the corresponding data is so closely related, we unify the two in the class `RangeDetail`. It both serves as the direct representation
      of a GEMF range detail through the parameters `address` and `length`, and as such inherits from `GEMFSectionBase` for automatic serialization.
      Additionally, derived classes shall provide the functionality to ultimately load and write binary tile data from associated tile objects.

    # Parameters
    - `address`: the start byte of the corresponding data in the binary file
    - `length`: the length of the encoded data corresponding to this `RangeDetail`
    """
    size = SIZES.OFFSET + SIZES.DATA;   """Static attribute: size of a `RangeDetail` if serialized."""

    def __init__(self, address: int, length: int, **kwargs) -> None:
        self.address = GEMFOffset(address)
        self.length = GEMFInt(length)

        super().__init__(**kwargs)

    def __len__(self):
        return len(self.address) + len(self.length)

    def to_dict(self):
        return {"address": self.address, "length": self.length}

    def write(self, f, *args, **kwargs):
        for val in [self.address, self.length]:
            val.write(f, *args, **kwargs)

    def to_dict_data(self):
        """Representation of subclasses with additional attributes for `GEMFDataSection`."""
        return f"{type(self).__name__}"

    def write_data(self, f):
        data_bytes = self.load_bytes()
        f.write(data_bytes)


class RangeDetails(GEMFList):
    """
    Information on the contained tiles as specified in section '3.4 Range Details' of the format specification.
    """

    def __init__(self, range_details: List[RangeDetail]) -> None:
        super().__init__(range_details)

    @classmethod
    def from_tiles(
        cls,
        headerinfo: HeaderInfo,
        sourcedata: SourceData,
        rangedata: RangeData,
        tileranges: List[TileRange],
    ):
        """Create a `RangeDetails` object from the previously loaded GEMF objects and a set of `TileRange` objects."""
        rangedetails = RangeDetails([])

        # determine initial byte position after header, source data, range data and range details
        OFFSET = (
            len(headerinfo)
            + len(sourcedata)
            + len(rangedata)
            + RangeDetails.size(rangedata.num_tiles)
        )

        # iterate through all tileranges and create a RangeDetail from it
        for i_range, tr_ in enumerate(tileranges):
            for i_tile, tile in enumerate(tr_):
                # instantiate correct detail class
                if isinstance(tile, DiskTile):
                    # TODO: i_range in constructor
                    rangedetail = GEMFTile.from_tile(OFFSET, tile)
                elif isinstance(tile, BufferTile):
                    rangedetail = GEMFBufferTile.from_tile(OFFSET, tile)    # TODO: implement
                elif isinstance(tile, GEMFTileReference):
                    rangedetail = GEMFTileReference(
                        OFFSET, tile.length, tile._file, tile.z, tile.x, tile.y,
                        tile.address, i_range, i_tile
                    )
                else:
                    raise ValueError(f"No corresponding GEMF tile class for {type(tile)}")

                rangedetail._range_idx = i_range
                rangedetail._tile_idx = i_tile

                rangedetails.append(rangedetail)

                OFFSET += tile.size_bytes

        return rangedetails

    @staticmethod
    def size(num_tiles: int):
        """Pre-compute the size of a `RangeDetails` object if serialized."""
        return num_tiles * RangeDetail.size


class GEMFHeaderSection(GEMFSectionBase):
    """
    All meta-information of the GEMF map file as specified in section '3. Header Area' of the format specification.
    """

    def __init__(
        self,
        header_info: HeaderInfo,
        source_data: SourceData,
        range_data: RangeData,
        range_details: RangeDetails,
    ) -> None:
        self.header_info = header_info
        self.source_data = source_data
        self.range_data = range_data
        self.range_details = range_details


class GEMFTileReference(RangeDetail, NamedTileBase):
    """
    Direct successor of the `RangeDetail` class, holding a reference to an existing range detail section in a `.gemf` file.

    # TODO: explain new params
    """

    # TODO: enable format passing
    def __init__(
        self,
        address: int, length: int, file: str, z: int, x: int, y: int,
        address_src: int, range_idx: int = None, tile_idx: int = None,
    ) -> None:
        super().__init__(
            address=address, length=length, z=z, x=x, y=y, name="tile", format=None
        )
        # __slots__ = ("address", "length", "z", "x", "y", "file", "name", "format")
        self._file = file

        self._range_idx = range_idx
        self._tile_idx = tile_idx
        # self._src = src
        self._src_adress = address_src

    @property
    def size_bytes(self):
        return self.length


    def load_bytes(self, f_src=None):
        """Load the tile data from file. Optionally specify `f_src` if the associated source file is already open (useful for repeated access to a source file)."""

        # define logic for reuse below
        def _load(f_src):
            f_src.seek(self._src_adress)
            data = f_src.read(self.length)
            return data

        # either open associated source file or use open file
        if f_src is None:
            with open(self._file, "rb") as f_in:
                return _load(f_in)
        else:
            return _load(f_src)


class GEMFBufferTile(RangeDetail, BufferTile):
    """
    GEMF version of a buffered tile, i.e. a tile without a corresponding file on disk.
    Used to hold binary data when greedily loading a `.gemf` file.

    **Note**: not suitable for large `.gemf` files, as the whole image data may overwhelm memory capacity.
    Instead, use `GEMFTileReference` for existing `.gemf` files or `GEMFTile` for tiles on disc.
    """
    def __init__(self,
                 address: int, length: int,                             # params for init of RangeDetail
                 z: int, x: int, y: int, data: bytes, **kwargs          # params and additional kwargs for init of BufferTile
                 ) -> None:
        super().__init__(**kwargify(locals()))


class GEMFTile(RangeDetail, DiskTile):
    """
    GEMF version of a regular tile, i.e. a tile with a corresponding file on disk.
    Used to load binary data when creating a `.gemf` file from tiles.
    """
    def __init__(self,
                 address: int, length: int,                                         # params for init of RangeDetail
                 z: int, x: int, y: int, tiledir: str, name: str, format: str       # params for init of Tile
                 ) -> None:
        super().__init__(**kwargify(locals()))

    @classmethod
    def from_file(cls, tile_file: str, address: int) -> None:
        len_image_bytes = os.stat(tile_file).st_size
        return cls(
            address=address,
            length=len_image_bytes,
            **DiskTile.parse_filepath(tile_file),
        )

    @classmethod
    def from_tile(cls, address: int, tile: DiskTile):
        """Utility constructor to instantiate a `GEMFTile` from a regular `Tile`."""
        return cls(address, tile.size_bytes, tile.z, tile.x, tile.y, tile.tiledir, tile.name, tile.format)


class GEMFDataSection(RangeDetails):
    """
    Sequential aggregate of encoded tile data as specified in section '4. Data Area' of the format specification.

    **Note**: This class is non-greedy, i.e. it does not load the tile data into memory. It only stores the necessary information to retrieve the binary tile data when requested.
    Hence, in this implementation, the `GEMFDataSection` only differs from `RangeDetails` in the serialization behavior, but holds the same detail data internally.
    """

    # TODO: why not accept rangedetaillist?
    def __init__(self, range_details: List[RangeDetail]) -> None:
        super().__init__(range_details)

    def __len__(self):
        """Sum of byte-length of member data."""
        return sum([detail.length for detail in self])

    def to_dict(self, *args, **kwargs):
        return [item.to_dict_data() for item in self]

    # override the default writing behavior of writing the instance's attributes sequentially
    def write(self, f):
        """Serialize the GEMF data section by loading the associated tile's data and writing to file."""
        # iterate over range details
        for range_detail in self:
            data_bytes = range_detail.load_bytes()
            f.write(data_bytes)


class GEMF(GEMFSectionBase):
    """
    Core class to read and write map files of the GEMF format. For a detailed description of the file format,
    see https://www.cgtk.co.uk/gemf.

    The `GEMF` class supports...
    - reading `.gemf` map files via the `from_file()` classmethod
    - creating a GEMF object from PNG or JPG tiles via the `from_tiles()` classmethod
    - writing the newly created GEMF object to file via the `write()` method

    Further features are...
    - extracting tiles (PNG or JPG) from binary `.gemf` files via the `save_tiles()` method
    - adding tiles to an existing `.gemf` file (TODO)
    """
    def __init__(self, gemf_header: GEMFHeaderSection, gemf_data: GEMFDataSection) -> None:
        self.header = gemf_header
        self.data = gemf_data

        self._src = None  # expected to be set in classmethods for `GEMF` initialization

    def __len__(self):
        if self.header.range_details is None:
            raise DetailsNotLoadedError
        return super().__len__()

    @property
    def num_sources(self):
        """Number of sources contained in `GEMF`."""
        return self.header.source_data._num_items

    @property
    def num_tiles(self):
        """Number of tiles contained in `GEMF`."""
        return sum([range.num_tiles for range in self.header.range_data])

    # initiation methods
    @classmethod
    def from_file(cls, gemf_file: str, lazy: bool = True):
        """
        Read a `.gemf` file from file.

        If `lazy` is set to `False`, range details will also be loaded into memory, and the full range of features is supported.
        However, for large files, this may take a while.

        The following operations can be performed if `lazy` is `True`:
        - `gemf.num_sources()`
        - `gemf.num_tiles()`

        The following operations require additional loading if the file was loaded lazily:
        - `len(gemf)`
        """
        gemf = cls(None, None)  # instantiate empty `GEMF` object
        gemf._src = gemf_file

        with open(gemf_file, "rb") as f:  # populate object
            gemf._read_gemf(f, lazy)

        return gemf

    @classmethod
    def from_tiles(
        cls,
        root_dir: str,
        mode: str = "split",
        version: int = 4,
        tile_size: int = 256,
        lazy: bool = True,
    ):
        """Create a `GEMF` object from tiles."""
        # TODO: auto-tilesize?
        gemf = cls(None, None)

        header_info = HeaderInfo(version, tile_size)
        source_data = SourceData.from_root(root_dir)
        range_data, tileranges = RangeData.from_root(root_dir, header_info, source_data, mode=mode)

        if lazy:
            range_details = None
            gemf._tileranges = tileranges  # save for later loading of details
        else:
            range_details = RangeDetails.from_tiles(header_info, source_data, range_data, tileranges)
            gemf.data = GEMFDataSection(range_details.items)

        gemf.header = GEMFHeaderSection(header_info, source_data, range_data, range_details)

        gemf._src = root_dir
        return gemf

    # manipulation methods
    def set_tile(self, *args):
        # TODO: implement
        # remove if set_val is None?
        pass

    # TODO: editing methods
    def add_source(self):
        pass

    def add_range(self):
        pass

    def filter_zooms(self, *zooms: int):
        pass

    def crop(
        self,
        z: int,
        xmin: int,
        xmax: int,
        ymin: int,
        ymax: int,
        drop_empty_sources: bool = True,
        lazy: bool = True,
    ):
        """
        Create a spatial subset of the tiles by bounding box.

        The bounding box specified at a specific level is used to determine the output extent and the intersection of all ranges with the output range extent is taken.

        For ranges at other zoom levels, the extent is translated:
        - For higher zoom levels, we translate the range to be congruent with the input range.
        - For lower zoom levels, we translate the range such that the input range is fully contained within the cropped extent. Cropped ranges of lower zoom levels may therefore extend over the input bounds.

        **Note:**
        The cropped output `gemf_cropped` will reference the data in the original `.gemf` file.
        Until written to file via `GEMF.write()`, the original file can not safely be deleted.

        Parameters
        ----------
        z : int
            Zoom level of bounding box
        xmin : int
            Minimum x tile coordinate of bounding box
        xmax : int
            Maximum x tile coordinate of bounding box
        ymin : int
            Minimum y tile coordinate of bounding box
        ymax : int
            Maximum y tile coordinate of bounding box
        drop_empty_sources : bool, optional
            Whether to drop or preserve sources which do not contain any tiles after cropping
        lazy : bool, optional
            Whether ...

        Returns
        -------
        GEMF
            A GEMF object with cropped tile set
        """
        # TODO: transfer GEMFReference file ownership
        ranges_cropped = defaultdict(list)

        # crop/drop each range
        for range_ in self.header.range_data:
            range_: GEMFRange

            # translate bounds to current range zoom level
            if range_.z > z:
                _, x_min_, y_min_ = SlippyTileMap.get_subtile_at_zoom(z, range_.z, xmin, ymin, subtile="tl")
                _, x_max_, y_max_ = SlippyTileMap.get_subtile_at_zoom(z, range_.z, xmax, ymax, subtile="br")
            elif range_.z < z:
                _, x_min_, y_min_ = SlippyTileMap.get_parent_tile_at_zoom(z, range_.z, xmin, ymin)
                _, x_max_, y_max_ = SlippyTileMap.get_parent_tile_at_zoom(z, range_.z, xmax, ymax)
            else:
                x_min_, x_max_, y_min_, y_max_ = xmin, xmax, ymin, ymax

            # find intersecting tiles
            tiles_crop_ = []
            for tile_ in self.get_range_details(range_):
                if AbstractRange.intersection(
                    (x_min_, x_max_, y_min_, y_max_),
                    (tile_.x, tile_.x, tile_.y, tile_.y),
                ):
                    # TODO: need to
                    tiles_crop_.append(tile_)

            if tiles_crop_:
                tilerange_crop_ = TileRange(range_.z, tiles_crop_)
                ranges_cropped[range_.src_index].append(tilerange_crop_)

        # drop sources if no range remains
        if drop_empty_sources:
            source_data = SourceData(SourceList([source_ for source_ in self.header.source_data if source_.index in ranges_cropped]))
        else:
            source_data = self.header.source_data  # TODO: copy needed?

        header_info = HeaderInfo(self.header.header_info.version, self.header.header_info.tile_size)
        range_data, tileranges = RangeData.from_ranges(ranges_cropped, header_info, source_data)

        # TODO: use _load_details
        if lazy:
            # TODO: why is GEMFDataSection slow? replace by something that is not None?
            range_details = None
            data_section = None
        else:
            range_details = RangeDetails.from_tiles(header_info, source_data, range_data, tileranges)
            data_section = GEMFDataSection(range_details.items)

        header = GEMFHeaderSection(header_info, source_data, range_data, range_details)

        gemf_cropped = GEMF(header, data_section)
        # TODO: move this into lazy clause only? is used somewhere else?
        gemf_cropped._tileranges = tileranges  # save for later loading of details

        gemf_cropped._src = self._src

        return gemf_cropped

    def crop_geom(self, geom):
        # TODO questions: adds dependencies? maybe as optional dependencies?
        pass

    def reindex_regions(self, method: str):
        # see tiles.py/RangeCollection
        pass

    # serialization methods
    def write(self, gemf_file: str):
        """Serialize the `GEMF` object to file."""
        if filedir := os.path.dirname(gemf_file):
            os.makedirs(filedir, exist_ok=True)

        with open(gemf_file, "wb") as f:
            super().write(f)

    def save_tiles(self, tiledir_root: str, save_empty: bool = False, workers: int = 4):
        """Save the `GEMF` object's tiles to file."""
        # TODO: leave .gemf file open if data is just References?
        if self.data is None:
            raise DetailsNotLoadedError()

        # create all source subdirectories
        for source in self.header.source_data:
            os.makedirs(os.path.join(tiledir_root, source.name))

        # TODO: better type annot for TileBase, since we get some instance of GEMFTile -> need GEMFTileBase or smth
        def _save_tile(g: GEMF, tiledir_root: str, data: TileBase, save_empty: bool = False):
            """Small wrapper to parallelize tile saving."""
            src = g.header.source_data[g.header.range_data[data._range_idx].src_index]
            if data.length > 0 or save_empty:
                data.save(os.path.join(tiledir_root, src.name))

        # write tiles
        if workers > 1:
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = [executor.submit(
                    _save_tile,
                    self,
                    tiledir_root,
                    data,
                    save_empty
                    ) for data in self.data]

                for future in as_completed(futures):
                    result = future.result()

        else:
            for data in self.data:
                _save_tile(data)

    # other methods
    def load_details(self):
        """
        Load the `RangeDetails` section of the `.gemf` file if `GEMF` was instantiated with `lazy = True`.
        The range details may be required for some operations.
        """
        if self.data is None:
            self._load_details()

    # utility methods
    def _read_gemf(self, f, lazy: bool = False):
        header_info = self._read_header(f)
        source_data = self._read_source_data(f, header_info)
        range_data = self._read_range_data(f, header_info, source_data)

        if lazy:
            range_details = None
            self.data = None
        else:
            range_details = self._read_range_details(f, header_info, source_data, range_data)
            self.data = GEMFDataSection(range_details.items)

        self.header = GEMFHeaderSection(header_info, source_data, range_data, range_details)

    def _read_header(self, f):
        f.seek(0)
        gemf_version = _read_int(f)
        tile_size = _read_int(f)
        headerinfo = HeaderInfo(gemf_version, tile_size)
        return headerinfo

    def _read_source_data(self, f, headerinfo: HeaderInfo):
        f.seek(len(headerinfo))
        num_sources = _read_int(f)
        sourcelist = SourceList([])

        for i_src in range(num_sources):
            src_idx = _read_int(f)
            assert i_src == src_idx
            name_length = _read_int(f)
            name = _read_string(f, name_length)

            sourcelist.append(GEMFSource(i_src, name))

        sourcedata = SourceData(sourcelist)
        return sourcedata

    def _read_range_data(self, f, headerinfo: HeaderInfo, sourcedata: SourceData):
        f.seek(len(headerinfo) + len(sourcedata))
        num_ranges = _read_int(f)

        tile_count = 0
        rangelist = RangeList([])
        for _ in range(num_ranges):
            z = _read_int(f)
            xmin = _read_int(f)
            xmax = _read_int(f)
            ymin = _read_int(f)
            ymax = _read_int(f)
            src_idx = _read_int(f)
            offset_details = _read_offset(f)

            range_ = GEMFRange(z, xmin, xmax, ymin, ymax, src_idx, offset_details, tile_count)
            rangelist.append(range_)
            tile_count += range_.num_tiles

        return RangeData(rangelist)

    def _read_range_details(self, f, headerinfo: HeaderInfo, sourcedata: SourceData, rangedata: RangeData):
        f.seek(len(headerinfo) + len(sourcedata) + len(rangedata))

        rangedetails = RangeDetails([])
        for i_range, range_ in enumerate(rangedata):
            for i_tile in range(range_.num_tiles):
                address = _read_offset(f)
                len_data = _read_int(f)

                range_ = rangedata[i_range]
                z, x, y = range_.get_zxy(i_tile)

                rangedetail = GEMFTileReference(
                    address, len_data, f.name, z, x, y,
                    address, i_range, i_tile,
                    )
                # rangedetail._range_idx = i_range
                # rangedetail._tile_idx = i_tile

                rangedetails.append(rangedetail)
        return rangedetails

    def _load_details(self):
        """Continue loading of `GEMF` by reading the `RangeDetails` section."""

        # read from gemf file
        if os.path.isfile(self._src):
            with open(self._src, "rb") as f:
                range_details = self._read_range_details(
                    f,
                    self.header.header_info,
                    self.header.source_data,
                    self.header.range_data,
                )
                self.header.range_details = range_details
                self.data = GEMFDataSection(range_details.items)

        # read from tiles
        elif os.path.isdir(self._src):
            range_details = RangeDetails.from_tiles(
                self.header.header_info,
                self.header.source_data,
                self.header.range_data,
                self._tileranges,
            )
            del self._tileranges
            self.data = GEMFDataSection(range_details.items)

        else:
            raise ValueError("Unsupported source.")

    # utility functions for information/manipulation
    def get_zoom_levels(self):
        zooms = set()
        for range_ in self.header.range_data:
            zooms.add(range_.z)
        return list(zooms)

    def get_range(self, idx: int) -> GEMFRange:
        return self.header.range_data[idx]

    def get_range_details(self, range: GEMFRange) -> list[DiskTile]:
        """Get range details corresponding to the a range."""
        idx_details = range._first_tile_idx
        details = self.header.range_details[idx_details : idx_details + range.num_tiles]
        return details

    def get_range_detail_zxy(self, z: int, x: int, y: int, src_idx: int = 0):
        GEMFRange
        # find range by z, x, y (if multiple present, use src_idx)
        ranges = [
            range_ for range_ in self.header.range_data
            if (
                range_.z == z and
                range_.src_index == src_idx and
                AbstractRange.intersection(range_.bounds, (x, x, y, y))
            )
        ]

        if len(ranges) == 0:
            return None
        elif len(ranges) > 1:
            pass    # TODO: happens? warn, index?
        else:
            range_found = ranges[0]
            range_found: GEMFRange

            tile_idx = AbstractRange.xy2index(x, y, *range_found.bounds, major="col")
            range_detail = self.header.range_details[range_found._first_tile_idx+tile_idx]

            return range_detail

    def get_bounds_lonlat(self) -> Tuple[float, float]:
        pass
