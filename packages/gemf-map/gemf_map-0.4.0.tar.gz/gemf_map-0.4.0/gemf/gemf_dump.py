"""
This submodule defines the core functionality of the package through the `GEMF` class.
"""

from collections.abc import Callable
import os
import shutil
import json
import warnings

import numpy as np

from .utils import FORMAT_PATTERNS, get_image_format, kwargify, listdirs, to_json
from .tiles import AbstractRange, BufferTile, NamedTileBase, DiskTile, TileCollection, TileRange


ENCODING = "ascii"
ENCODING_ERROR = "ignore"

BYTES_DATA = 4
BYTES_OFFSET = 8


# auxiliary methods, used to read encoded binary data
def _read_value(f, N):
    """Read N bytes from a binary file and return as int."""
    value_bytes = f.read(N)
    return int.from_bytes(value_bytes, "big")

def _read_int(f):
    """Read int as encoded in GEMF."""
    return _read_value(f, BYTES_DATA)

def _read_offset(f):
    """Read offset as encoded in GEMF."""
    return _read_value(f, BYTES_OFFSET)

def _read_string(f, N):
    """Read string as encoded in GEMF."""
    str_bytes = f.read(N)
    return str_bytes.decode(ENCODING)


# encoding utilities, used to write binary gemf file
def _encode_data(value):
    """Encode a data integer, i.e. as 4 bytes."""
    return (value).to_bytes(BYTES_DATA, "big")

def _encode_offset(value):
    """Encode an offset integer, i.e. as 8 bytes."""
    return (value).to_bytes(BYTES_OFFSET, "big")

def _encode_string(value):
    """Encode a string, with variable byte length."""
    return value.encode(ENCODING, ENCODING_ERROR)



# GEMF classes
class GEMFValueBase:
    """
    Base class defining basic GEMF type behavior. Python primitives are wrapped in
    custom GEMF classes for easier integration in the GEMF workflow.
    """
    def __str__(self): return super().__str__()
    def __repr__(self): return f"{type(self).__name__}: {super().__str__()}"

    def __len__(self):
        """Return the encoded size."""
        return len(self._encode(self))

    def write(self, f, *args, **kwargs):
        """Write the encoded value to a binary gemf file."""
        return f.write(self._encode(self), *args, **kwargs)


class GEMFIntBase(int, GEMFValueBase):
    """Base class for int-like GEMF types."""
    def __new__(cls, value: int, encoding_method: Callable[[int], None]):
        assert isinstance(value, int) or np.can_cast(value, int), f"Can't cast {type(value)} to int."
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
    def __new__(cls, value: str, encoding: str = ENCODING, error: str = ENCODING_ERROR) -> None:
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

    def __iter__(self): return iter(self.items)
    def __getitem__(self, idx): return self.items[idx]

    def to_dict(self, *args, **kwargs):
        """Return a list of dict-representation of the member items."""
        list_dict = []
        for item in self.items:
            if hasattr(item, "to_dict"):
                list_dict.append(item.to_dict())
            else:
                list_dict.append(to_json(item))
        return list_dict

    def __str__(self) -> str: return str(self.to_dict())

    def append(self, item):
        if len(self.items): assert isinstance(item, type(self[0])), "Items must be of equal type."
        return self.items.append(item)

    def extend(self, items):
        if len(self.items): assert all([isinstance(item, type(self[0])) for item in items]), "Items must be of equal type."
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

    def to_dict(self, ignore_private: bool = True) -> dict:
        """
        Recursively build a dictionary representation of the GEMF structure.
        Attributes starting with an underscore are supressed by default.
        """
        out_dict = {}

        for key, el in self.__dict__.items():
            if ignore_private and key.startswith("_"): continue

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
            if key.startswith("_"): continue
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

    def __getitem__(self, idx): return self._items[idx]
    def __iter__(self): return iter(self._items)


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
    def __init__(self, sources: list[GEMFSource]) -> None:
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
    def __init__(self, z: int, xmin: int, xmax: int, ymin: int, ymax: int, src_index: int, details_offset: int) -> None:
        self.z = GEMFInt(z)
        self.xmin = GEMFInt(xmin)
        self.xmax = GEMFInt(xmax)
        self.ymin = GEMFInt(ymin)
        self.ymax = GEMFInt(ymax)
        self.src_index = GEMFInt(src_index)
        self.offset = GEMFOffset(details_offset)

    def get_zxy(self, index: int):
        """Get the n-th tile of the range by index. Ranges are traversed in column-major order."""
        tile = AbstractRange(self.z, self.xmin, self.xmax, self.ymin, self.ymax, major="col")[index]
        return tile.z, tile.x, tile.y

    @property
    def num_tiles(self):
        return len(AbstractRange(self.z, self.xmin, self.xmax, self.ymin, self.ymax, major="col"))


class RangeList(GEMFList):
    """Wrap a list of `GEMFRange`s."""
    def __init__(self, ranges: list[GEMFRange]) -> None:
        super().__init__(ranges)


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
    def from_root(cls, root_dir: str, headerinfo: HeaderInfo, sourcedata: SourceData, mode: str = "split", **kwargs):
        """
        Create a `RangeData` object from the previously loaded GEMF objects.
        Additionally, return a list of `TileRange` objects, which are required for further GEMF creation steps.
        """
        range_list = RangeList([])
        tileranges = []

        # traverse all source dirs
        for i_source, source in enumerate(sourcedata.sources):

            # collect tile ranges (aka rectangular collections of tiles)
            tc = TileCollection.from_tiledir(os.path.join(root_dir, source.name))                                   # first, collect all tiles in source dir
            tileranges_ = tc.to_tileranges(mode=mode, **kwargs)                                                     # split collection into valid tileranges
            num_ranges = len(tileranges_)

            OFFSET = len(headerinfo) + len(sourcedata) + len(RangeData.dummy(num_ranges)) + len(range_list)         # initial offset for details based on previous sections and length of RangeData

            # iterate over all found tile ranges
            for tr_ in tileranges_:
                # create corresponding GEMF object and collect objects
                gemf_range = GEMFRange(tr_.z, tr_.xmin, tr_.xmax, tr_.ymin, tr_.ymax, i_source, OFFSET)
                tileranges.append(tr_)
                range_list.append(gemf_range)

                # advance offset to block of range details, corresponding to the next range
                num_tiles = len(tr_)
                OFFSET += num_tiles * len(RangeDetail.dummy())

        rangedata = cls(range_list)
        return rangedata, tileranges

    @property
    def num_tiles(self):
        """Number of tiles contained in `RangeData`."""
        return sum([range.num_tiles for range in self.ranges])

    @classmethod
    def dummy(cls, num_ranges: int):
        """Return a dummy instance of `RangeData` for easy computation of expected size."""
        return cls(GEMFList([GEMFRange(0, 0, 0, 0, 0, 0, 0) for _ in range(num_ranges)]))

    # def write(self, f):
    #     range_: GEMFRange

    #     for range_ in self:
    #         f.seek(range_.offset)
    #         for tile in range_:
    #             tile.write(f)


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
    def __init__(self, address: int, length: int, **kwargs) -> None:
        self.address = GEMFOffset(address)
        self.length = GEMFInt(length)

        super().__init__(**kwargs)

    def __len__(self): return len(self.address) + len(self.length)

    @classmethod
    def dummy(cls):
        """Return a dummy instance of `RangeDetail` for easy computation of expected size."""
        return cls(0, 0)

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
    def __init__(self, range_details: list[RangeDetail]) -> None:
        super().__init__(range_details)

    @classmethod
    def from_root(cls, headerinfo: HeaderInfo, sourcedata: SourceData, rangedata: RangeData, tileranges: list[TileRange]):
        """Create a `RangeDetails` object from the previously loaded GEMF objects and a set of `TileRange` objects."""
        rangedetails = RangeDetails([])
        # data = GEMFDataSection([])

        # determine initial byte position after header, source data, range data and range details
        OFFSET = len(headerinfo) + len(sourcedata) + len(rangedata) + len(RangeDetails.dummy(rangedata.num_tiles))

        # iterate through all tileranges and create a RangeDetail from it
        for i_range, tr_ in enumerate(tileranges):
            for i_tile, tile in enumerate(tr_):
                len_image_bytes = os.stat(tile.get_filepath()).st_size
                # image_bytes = tile.load_bytes()
                # len_image_bytes = len(image_bytes)
                # data.append(GEMFTile.from_tile(tile, i_range, i_tile))

                rangedetail = GEMFTile.from_tile(OFFSET, tile)
                rangedetail._range_idx = i_range
                rangedetail._tile_idx = i_tile

                # rangedetail = RangeDetail(OFFSET, len_image_bytes)
                # rangedetail._z = tile.z
                # rangedetail._x = tile.x
                # rangedetail._y = tile.y
                rangedetails.append(rangedetail)

                OFFSET += len_image_bytes

        return rangedetails
        # return rangedetails, data

    @classmethod
    def dummy(cls, num_tiles: int):
        """Return a dummy instance of `RangeDetails` for easy computation of expected size."""
        return cls([RangeDetail.dummy() for _ in range(num_tiles)])
        # return cls([RangeDetail(0, 0) for _ in range(num_tiles)])

    # def write(self, f):
    #     """Serialize the GEMF data section by loading the associated tile's data and writing to file."""
    #     print("writing RangeDetails")
    #     # iterate over range details
    #     for range_detail in self:
    #         data_bytes = range_detail.load_bytes()
    #         f.write(data_bytes)

    # @staticmethod
    # def write(f, rangedata: RangeData):
    #     range_: GEMFRange

    #     for range_ in rangedata:
    #         f.seek(range_.offset)
    #         for tile in range_:
    #             tile.write(f)


class GEMFHeaderSection(GEMFSectionBase):
    """
    All meta-information of the GEMF map file as specified in section '3. Header Area' of the format specification.
    """
    def __init__(self, header_info: HeaderInfo,
                 source_data: SourceData,
                 range_data: RangeData,
                 range_details: RangeDetails
                 ) -> None:
        self.header_info = header_info
        self.source_data = source_data
        self.range_data = range_data
        self.range_details = range_details


class GEMFReference(RangeDetail, NamedTileBase):
    """
    Direct successor of the `RangeDetail` class, holding a reference to an existing range detail section in a `.gemf` file.
    """
    # TODO: enable format passing
    def __init__(self, address: int, length: int, file: str, z: int, x: int, y: int) -> None:
        super().__init__(address=address, length=length, z=z, x=x, y=y, name="tile", format=None)
        self._file = file


    def load_bytes(self, f_src=None):
        """Load the tile data from file. Optionally specify `f_src` if the associated source file is already open (useful for repeated access to a source file)."""

        # define logic for reuse below
        def _load(f_src):
            f_src.seek(self.address)
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
    Instead, use `GEMFReference` for existing `.gemf` files or `GEMFTile` for tiles on disc.
    """
    def __init__(self, address: int, length: int, z: int, x: int, y: int, data: bytes, **kwargs) -> None:
    # def __init__(self, address: int, length: int, z: int, x: int, y: int, data: bytes, range_idx: int, tile_idx: int, **kwargs) -> None:
        super().__init__(
            address=address, length=length,         # params for init of RangeDetail
            z=z, x=x, y=y, data=data, **kwargs      # params and additional kwargs for init of BufferTile
        )
        # super(RangeDetail, self).__init__(address, length)
        # RangeDetail.__init__(self, address, length)
        # super(BufferTile, self).__init__(z, x, y, data, **kwargs)
        # BufferTile.__init__(self, z, x, y, data, **kwargs)

    # def __init__(self, z: int, x: int, y: int, range_idx: int, tile_idx: int, data: bytes) -> None:
    #     GEMFTileBase.__init__(self)
    #     BufferTile.__init__(self, z, x, y, data, allow_invalid=False)

    #     self._range_idx = range_idx
    #     self._tile_idx = tile_idx


class GEMFTile(RangeDetail, DiskTile):
    """
    GEMF version of a regular tile, i.e. a tile with a corresponding file on disk.
    Used to load binary data when creating a `.gemf` file from tiles.
    """
    def __init__(self, address: int, z: int, x: int, y: int, tiledir: str, name: str, format: str) -> None:
    # def __init__(self, address: int, z: int, x: int, y: int, range_idx: int, tile_idx: int, tiledir: str, name: str, format: str) -> None:
        filepath = DiskTile.compose_filepath(z, x, y, tiledir, name, format)
        length = os.stat(filepath).st_size
        super().__init__(length=length, **kwargify(locals()))
    # def __init__(self, address: int, tile_file: str, range_idx: int, tile_idx: int) -> None:


    @classmethod
    def from_file(cls, tile_file: str, address: int) -> None:
        return cls(address=address, **DiskTile.parse_filepath(tile_file))
        # super().__init__(self, address=address, length=length, **Tile.parse_filepath(tile_file))


    # def __init__(self, z: int, x: int, y: int, range_idx: int, tile_idx: int, tiledir: str, name: str, format: str) -> None:
    #     GEMFTileBase.__init__(self)
    #     Tile.__init__(self, z, x, y, tiledir, name, format, allow_invalid=False)
    #     self._range_idx = range_idx
    #     self._tile_idx = tile_idx

    @classmethod
    def from_tile(cls, address: int, tile: DiskTile):
    # def from_tile(cls, address: int, length: int, tile: Tile, range_idx: int, tile_idx: int):
        """Utility constructor to instantiate a `GEMFTile` from a regular `Tile`."""
        return cls(address, tile.z, tile.x, tile.y, tile.tiledir, tile.name, tile.format)
        # return cls(address, length, tile.z, tile.x, tile.y, range_idx, tile_idx, tile.tiledir, tile.name, tile.format)


class GEMFDataSection(RangeDetails):
    """
    Sequential aggregate of encoded tile data as specified in section '4. Data Area' of the format specification.

    **Note**: This class is lazy, i.e. it does not load the tile data into memory. It only stores the necessary information to retrieve the binary tile data when requested.
    Hence, in this implementation, the `GEMFDataSection` only differs from `RangeDetails` in the serialization behavior, but holds the same detail data internally.
    """
    def __init__(self, range_details: list[RangeDetail]) -> None:
        super().__init__(range_details)

    def __len__(self):
        """Sum of byte-length of member data."""
        return sum([detail.length for detail in self])

    def to_dict(self, *args, **kwargs):
        return [item.to_dict_data() for item in self]
        # return [item.str_data() for item in self]

    # override the default writing behavior of writing the instance's attributes sequentially
    def write(self, f):
        """Serialize the GEMF data section by loading the associated tile's data and writing to file."""
        print("writing DataSection")
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
    # def __init__(self, header_info: HeaderInfo, source_data: SourceData, range_data: RangeData, range_details: RangeDetails) -> None:
    def __init__(self, gemf_header: GEMFHeaderSection, gemf_data: GEMFDataSection) -> None:
        self.header = gemf_header
        self.data = gemf_data

        # self.header_info = header_info
        # self.source_data = source_data
        # self.range_data = range_data
        # self.range_details = range_details

    @classmethod
    def from_file(cls, gemf_file: str):
        """Read a `.gemf` file from file."""
        gemf = cls(None, None)              # instantiate empty `GEMF` object
        # gemf = cls(None, None, None, None)
        gemf._src = gemf_file

        with open(gemf_file, "rb") as f:    # populate object
            gemf._read_gemf(f)

        return gemf

    @classmethod
    def from_tiles(cls, root_dir: str, mode: str = "split", version: int = 4, tile_size: int = 256):
        """Create a `GEMF` object from tiles."""
        gemf = cls(None, None)

        # TODO: auto-tilesize?

        header_info = HeaderInfo(version, tile_size)
        source_data = SourceData.from_root(root_dir)
        range_data, tileranges = RangeData.from_root(root_dir, header_info, source_data, mode=mode)

        range_details = RangeDetails.from_root(header_info, source_data, range_data, tileranges)
        # rangedetails, data = RangeDetails.from_root(headerinfo, sourcedata, rangedata, tileranges)
        # header = GEMFHeaderSection(header_info, source_data, range_data, range_details)

        gemf.header = GEMFHeaderSection(header_info, source_data, range_data, range_details)
        gemf.data = GEMFDataSection(range_details.items)

        gemf._src = root_dir

        return gemf

    def write(self, gemf_file: str):
        """Serialize the `GEMF` object to file."""
        os.makedirs(os.path.dirname(gemf_file), exist_ok=True)

        with open(gemf_file, "wb") as f:
            super().write(f)


    # TODO: editing methods
    def add_source(self): pass
    def add_range(self): pass

    def save_tiles(self, tiledir_root: str, save_empty: bool = False):
        """Save the `GEMF` object's tiles to file."""
        # TODO: leave .gemf file open if data is just References?

        if os.path.exists(tiledir_root):
            shutil.rmtree(tiledir_root)
        os.makedirs(tiledir_root)

        # create all source subdirectories
        for source in self.header.source_data:
            os.makedirs(os.path.join(tiledir_root, source.name))

        # write tiles
        for data in self.data:
            src = self.header.source_data[self.header.range_data[data._range_idx].src_index]

            if data.length > 0 or save_empty:
                data.save(os.path.join(tiledir_root, src.name))


    def _read_gemf(self, f):
    # def _read_gemf(self, f, greedy: bool = False):
        # self.header_info = self._read_header(f)
        # self.source_data = self._read_source_data(f, self.header_info)
        # self.range_data = self._read_range_data(f, self.header_info, self.source_data)
        # self.range_details = self._read_range_details(f, self.header_info, self.source_data, self.range_data)

        header_info = self._read_header(f)
        source_data = self._read_source_data(f, header_info)
        range_data = self._read_range_data(f, header_info, source_data)
        range_details = self._read_range_details(f, header_info, source_data, range_data)

        self.header = GEMFHeaderSection(header_info, source_data, range_data, range_details)
        self.data = GEMFDataSection(range_details.items)

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

        rangelist = RangeList([])
        for _ in range(num_ranges):
            z = _read_int(f)
            xmin = _read_int(f)
            xmax = _read_int(f)
            ymin = _read_int(f)
            ymax = _read_int(f)
            src_idx = _read_int(f)
            offset_details = _read_offset(f)

            rangelist.append(GEMFRange(z, xmin, xmax, ymin, ymax, src_idx, offset_details))

        return RangeData(rangelist)

    def _read_range_details(self, f, headerinfo: HeaderInfo, sourcedata: SourceData, rangedata: RangeData):
        f.seek(len(headerinfo) + len(sourcedata) + len(rangedata))

        rangedetails = RangeDetails([])
        for i_range, range_ in enumerate(rangedata):
            for i_tile in range(range_.num_tiles):
                address = _read_offset(f)
                len_data = _read_int(f)

                range_: RangeData

                range_ = rangedata[i_range]
                z, x, y = range_.get_zxy(i_tile)

                rangedetail = GEMFReference(address, len_data, f.name, z, x, y)
                # rangedetail = RangeDetail(address, len_data)
                rangedetail._range_idx = i_range
                rangedetail._tile_idx = i_tile

                rangedetails.append(rangedetail)
        return rangedetails

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

######################

class LocalTileLayerMine(MacroElement):
    # TODO: dynamic loading: apparently needs a flask server?
    def __init__(self, tile_func, zoom: int, min_zoom: int, max_zoom: int):
        super().__init__()
        self._name = "LocalTileLayer"
        self.tile_func = tile_func
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.min_zoom = zoom
        self.max_zoom = zoom
        self.zoom = zoom

        # Build a dictionary { "z/x/y": "data:image/png;base64,..." }
        tiles = {}
        # for z in range(self.min_zoom, self.max_zoom + 1):
        z = self.zoom
        for x in range(2**z):
            for y in range(2**z):
                data = tile_func(z, x, y)
                if data is None:
                    continue

                b64 = base64.b64encode(data).decode()
                tiles[f"{z}/{x}/{y}"] = f"data:image/png;base64,{b64}"

        tiles_js = "window.tileData = " + str(tiles) + ";"
        self.tiles_script = f"<script>{tiles_js}</script>"

        # Leaflet custom tile layer
        self._template = Template("""
        {% macro script(this, kwargs) %}
        var CustomTileLayer = L.TileLayer.extend({
            getTileUrl: function(coords) {
                var key = coords.z + "/" + coords.x + "/" + coords.y;
                return window.tileData[key] || "";
            }
        });
        var layer = new CustomTileLayer({minZoom: {{this.min_zoom}}, maxZoom: {{this.max_zoom}}});
        layer.addTo({{this._parent.get_name()}});
        layer.on('tileload', function(e) {
            e.tile.title = e.tile.src.match(/\\d+\\/\\d+\\/\\d+/)[0]; // Show z/x/y on hover
        });
        {% endmacro %}
        """)

    def render(self, **kwargs):
        # Add the base64 dictionary to the HTML head
        self._parent.get_root().html.add_child(folium.Element(self.tiles_script))
        super().render(**kwargs)


class LocalTileLayer(MacroElement):
    def __init__(self, tile_func, zoom, min_zoom=0, max_zoom=2, layer_group=None, name="Local Tile Layer"):
        super().__init__()
        self._name = "LocalTileLayer"
        self.tile_func = tile_func
        self.zoom = zoom
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.layer_group = layer_group
        self.layer_name = name

        # Build tiles dict for all zooms in range
        tiles = {}
        z = zoom
        for x in range(2**z):
            for y in range(2**z):
                data = tile_func(z, x, y)
                if data is None:
                    continue
                b64 = base64.b64encode(data).decode()
                tiles[f"{z}/{x}/{y}"] = f"data:image/png;base64,{b64}"

        tiles_js = "window.tileData = " + str(tiles) + ";"
        self.tiles_script = f"<script>{tiles_js}</script>"

        self._template = Template("""
        {% macro script(this, kwargs) %}
        var CustomTileLayer = L.TileLayer.extend({
            getTileUrl: function(coords) {
                var key = coords.z + "/" + coords.x + "/" + coords.y;
                return window.tileData[key] || "";
            }
        });

        var layer = new CustomTileLayer({
            minZoom: {{this.min_zoom}},
            maxZoom: {{this.max_zoom}}
        });

        {% if this.layer_group %}
            {{this.layer_group.get_name()}}.addLayer(layer);
        {% else %}
            layer.addTo({{this._parent.get_name()}});
        {% endif %}

        layer.on('tileload', function(e) {
            e.tile.title = e.tile.src.match(/\\d+\\/\\d+\\/\\d+/)[0];  // Show z/x/y on hover
        });
        {% endmacro %}
        """)

    def render(self, **kwargs):
        self._parent.get_root().html.add_child(folium.Element(self.tiles_script))
        super().render(**kwargs)


########################

def can_cast(value: Any, target_type: Type):
    try:
        _ = target_type(value)
        return True
    except:
        return False
########################
%load_ext autoreload
%autoreload 2

import os

import gemf

import folium
import mercantile


def tile_bounds(tile):
    """Return tile bounds as (west, south, east, north)."""
    bounds = mercantile.bounds(tile)
    return bounds.west, bounds.south, bounds.east, bounds.north


def tile_list_to_folium_map(
    tiles, map_center=None, zoom_start=2, m=None, **style_kwargs
):
    """
    Create a Folium map showing bounding boxes for a list of (z, x, y) tiles.

    Args:
        tiles: List of (z, x, y) tuples.
        map_center: Optional (lat, lon) tuple. If None, center on first tile.
        zoom_start: Initial zoom level.

    Returns:
        folium.Map object.
    """
    if not tiles:
        raise ValueError("Tile list is empty.")

    # Compute bounds of all tiles
    bounds_list = []
    for z, x, y in tiles:
        tile = mercantile.Tile(x=x, y=y, z=z)
        bounds_list.append(mercantile.bounds(tile))

    # Compute overall bounding box
    west = min(b.west for b in bounds_list)
    south = min(b.south for b in bounds_list)
    east = max(b.east for b in bounds_list)
    north = max(b.north for b in bounds_list)

    # Default center
    if map_center is None:
        lat_center = (south + north) / 2
        lon_center = (west + east) / 2
        map_center = [lat_center, lon_center]

    if m is None:
        m = folium.Map(
            location=map_center,
            zoom_start=zoom_start,
            tiles="CartoDB positron",
            max_bounds=True,
        )

    DEFAULT_STYLE = {
        "color": "blue",
        "weight": 1,
        "fill": False,
    }
    DEFAULT_STYLE.update(style_kwargs)

    for z, x, y in tiles:
        tile = mercantile.Tile(x=x, y=y, z=z)
        west, south, east, north = tile_bounds(tile)
        folium.Rectangle(
            bounds=[[south, west], [north, east]],
            tooltip=f"ZXY: {z}/{x}/{y}",
            **DEFAULT_STYLE,
        ).add_to(m)

    return m
###################