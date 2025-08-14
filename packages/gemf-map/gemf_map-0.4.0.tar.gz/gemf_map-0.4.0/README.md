# GEMF

Python package for the GEMF map format. From the format [specification](https://www.cgtk.co.uk/gemf):

> This tile store format is intended to provide a static (i.e. cannot be updated without regenerating from scratch) file containing a large number of tiles, stored
> in a manner that makes efficient use of SD cards and with which it is easy to access individual tiles very quickly. It is intended to overcome the existing issues
> with the way tiles are stored in most existing Android map applications as these are not very scalable.

`.gemf` files may be used in mobile mapping applications like [Locus](https://www.locusmap.app/)

# Installation
```cmd
pip install gemf-map
```


# Features
**Core features** are...
- reading `.gemf` map files via the `GEMF.from_file()` classmethod
- creating a GEMF object from PNG or JPG tiles via the `GEMF.from_tiles()` classmethod
- writing a newly created GEMF object to file via the `write()` method

**Further features** are...
- spatially subset (crop) a .gemf file
- extracting tiles (PNG or JPG) from binary `.gemf` files via the `save_tiles()` method
- adding tiles to an existing `.gemf` file (TODO)

**Visualization features**:
- show the tiles of a .gemf file on a `folium` map
- show tile boundaries on a map

<!-- TODO: explain lazy laoding -->

# Usage

## Core
```python
from gemf import GEMF

# load an existing .gemf file
my_gemf = GEMF.from_file("MY_GEMF.gemf")

# extract the tiles
my_gemf.save_tiles("PATH/TO/TILEDIR")

# create a GEMF object from tiles on disk
new_gemf = GEMF.from_tiles("PATH/TO/TILEDIR")

# write GEMF object to .gemf file
new_gemf.write("PATH/TO/GEMF_FILE.gemf")
```

## Manipulation
```python
# crop to bounding box (all zoom levels will be cropped accordingly)
gemf_crop = my_gemf.crop(7, 60, 62, 36, 38)
```


## Visualization
<!-- TODO: limitations for large gemf files -->
```python
from gemf.plot import GEMFPlot

# visualize tiles and tile boundaries
gemf_map = GEMFPlot(my_gemf)

# visualize tiles without boundaries
tile_map = GEMFPlot(my_gemf, show_tile_boundaries=False)

# visualize only boundaries (to avoid loading tile contents from disk)
boundary_map = GEMFPlot(my_gemf, show_tiles=False)
```

## Other
```python
# save the embedded tiles to image files
gemf_map.save_tiles("path/to/output/dir")
```