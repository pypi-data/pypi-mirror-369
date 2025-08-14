"""
Visualization utilties for GEMF files.
"""

import base64
from typing import Dict, List, Optional

import folium
from folium import FeatureGroup
from folium.plugins import FeatureGroupSubGroup

from branca.element import MacroElement
from jinja2 import Template
import mercantile

from gemf import GEMF
from gemf.tiles import AbstractRange


def gemf_tile_loader(g: GEMF):
    """Wrap the GEMF tile finding and tile byte loading for visualization with folium."""

    def _get_tile(z, x, y):
        detail = g.get_range_detail_zxy(z, x, y)
        if detail is None:
            return None
        else:
            return detail.load_bytes()

    return _get_tile



class LocalTileLayerAll(MacroElement):
    """Add multiple zoom levels at once."""
    # TODO: dynamic loading: apparently needs a flask server?
    def __init__(self, tile_func, *zooms: int):
        super().__init__()
        self._name = "LocalTileLayerAll"
        self.tile_func = tile_func
        self.min_zoom = min(zooms)
        self.max_zoom = max(zooms)

        # Build a dictionary { "z/x/y": "data:image/png;base64,..." }
        tiles = {}
        for z in range(self.min_zoom, self.max_zoom + 1):
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
    """Create a tile layer for a single zoom level."""
    # TODO: min_zoom_show param
    def __init__(self, tile_func, id: int, *zooms: int):
        super().__init__()
        self._name = "LocalTileLayer"
        self.tile_func = tile_func
        self.min_zoom = min(zooms)
        self.max_zoom = max(zooms)

        # Unique instance ID
        self._instance_id = int(id)

        # Build dictionary { "z/x/y": "data:image/png;base64,..." }
        tiles = {}
        for z in range(self.min_zoom, self.max_zoom + 1):
            for x in range(2**z):
                for y in range(2**z):
                    data = tile_func(z, x, y)
                    if data is None:
                        continue
                    b64 = base64.b64encode(data).decode()
                    tiles[f"{z}/{x}/{y}"] = f"data:image/png;base64,{b64}"

        # Use unique window variable name for tile data
        tiles_js = f"window.tileData_{self._instance_id} = " + str(tiles) + ";"
        self.tiles_script = f"<script>{tiles_js}</script>"

        # Leaflet custom tile layer with unique class and variable names
        self._template = Template(f"""
        {{% macro script(this, kwargs) %}}
        var CustomTileLayer_{self._instance_id} = L.TileLayer.extend({{
            getTileUrl: function(coords) {{
                var key = coords.z + "/" + coords.x + "/" + coords.y;
                return window.tileData_{self._instance_id}[key] || "";
            }}
        }});
        var layer_{self._instance_id} = new CustomTileLayer_{self._instance_id}({{minZoom: {{{{this.min_zoom}}}}, maxZoom: {{{{this.max_zoom}}}}}});
        layer_{self._instance_id}.addTo({{{{this._parent.get_name()}}}});
        layer_{self._instance_id}.on('tileload', function(e) {{
            e.tile.title = e.tile.src.match(/\\d+\\/\\d+\\/\\d+/)[0]; // Show z/x/y on hover
        }});
        {{% endmacro %}}
        """)

    def render(self, **kwargs):
        # Add the base64 dictionary to the HTML head
        self._parent.get_root().html.add_child(folium.Element(self.tiles_script))
        super().render(**kwargs)


class GEMFPlot(folium.Map):
    """
    Visualize the map tiles stored in a GEMF object using `folium.Map`.

    Available visualization layers are:
    - map tiles per zoom level
        - potentially slow for many tiles
        - requires GEMF to be loaded with `lazy=False`
    - tile extents per zoom level
        - performant even for large GEMF files
        - compatible with lazy loading

    **Note:** Due to `folium`'s limitations, the tile visualization embeds the tile content statically into the
    map HTML. For small number of tiles, this is an acceptable solution, however, we can expect performance issues for large
    GEMF files.


    Parameters
    ----------
    gemf : GEMF
        The GEMF object holding the tiles to visualize
    show_tiles : bool
        Whether to add layers of GEMF raster tiles to the map
    show_tiles_at_zoom : bool
        Whether to show the tiles at only their respective zoom level, or at any level. Not implemented yet
    tile_zooms : List[int]
        Pass a list of zoom levels to only visualize certain zoom levels
    show_tile_boundaries : bool
        Whether to add layers of bounding boxes to the map, indicating the tile extents
    cmap : str
        A `matplotlib` colormap name, used to generate the different zoom levels' colors for bounding box visualization

    Further keyword arguments are passed to `folium.Map`, see the [API docs](https://python-visualization.github.io/folium/latest/reference.html#folium.folium.Map)
    for a list of supported arguments. Note that the default values for the options `zoom_start` and `max_bounds`. have been changed in this class.
    """

    # TODO: test lazy loading tile vis: test error on datanotloaded and bbox on lazy
    # TODO: test init without tiles/bbox and later adddition: is layerControl still working?

    def __init__(
        self,
        gemf: GEMF,
        show_tiles: bool = True,
        show_tiles_at_zoom: bool = True,        # TODO: option to show tiles only within correct zoom or globally
        tile_zooms: Optional[List[int]] = None,
        show_tile_boundaries: bool = True,
        cmap: str = "tab10",
        *,

        # folium.Map arguments
        location=None,
        width="100%",
        height="100%",
        left="0%",
        top="0%",
        position="relative",
        tiles="OpenStreetMap",      # maybe "CartoDB Positron" ?
        attr=None,
        min_zoom=None,
        max_zoom=None,
        zoom_start=None,        # non-default
        min_lat=-90,
        max_lat=90,
        min_lon=-180,
        max_lon=180,
        max_bounds=True,        # non-default value
        crs="EPSG3857",
        control_scale=False,
        prefer_canvas=False,
        no_touch=False,
        disable_3d=False,
        png_enabled=False,
        zoom_control=True,
        font_size="1rem",
        **kwargs,
    ):
        self.gemf = gemf
        self._min_zoom = min_zoom
        self._max_zoom = max_zoom
        self._cmap = cmap

        # default to zoom levels present in GEMF
        if tile_zooms is None:
            tile_zooms = self.gemf.get_zoom_levels()
        self._tile_zooms = tile_zooms

        # default to minimum zoom level
        if zoom_start is None:
            zoom_start = min(self.gemf.get_zoom_levels())

        # default to image center determined from tiles
        if location is None:
            location = self.get_image_center_from_tiles()

        super().__init__(
            location,
            width,
            height,
            left,
            top,
            position,
            tiles,
            attr,
            min_zoom,
            max_zoom,
            zoom_start,
            min_lat,
            max_lat,
            min_lon,
            max_lon,
            max_bounds,
            crs,
            control_scale,
            prefer_canvas,
            no_touch,
            disable_3d,
            png_enabled,
            zoom_control,
            font_size,
            **kwargs,
        )


        if show_tiles:
            self.add_tile_layer(tile_zooms)

        if show_tile_boundaries:
            self.add_tile_boundary_layer(tile_zooms)

        folium.LayerControl(collapsed=False).add_to(self)


    def add_tile_layer(self, zooms: List[int] = None):
        """
        Add a layer of GEMF tiles.

        Parameters
        ----------
        zooms : List[int]
            Specify the zoom levels to show
        """
        if not zooms:
            min_zoom_gemf = self._min_zoom if self._min_zoom is not None else min(self.gemf.get_zoom_levels())
            max_zoom_gemf = self._max_zoom if self._max_zoom is not None else max(self.gemf.get_zoom_levels())
            zooms = list(range(min_zoom_gemf, max_zoom_gemf+1))

        zoom_groups = self._add_layer_control_groups(zooms, "Tiles")
        for zoom_ in zooms:
            LocalTileLayer(gemf_tile_loader(self.gemf), zoom_, zoom_).add_to(
                zoom_groups[zoom_]
            )


    def add_range_boundary_layer(self):
        # TODO
        for range_ in self.gemf.ranges:
            ul_lon, ul_lat, br_lat, br_lon = AbstractRange.bounds(range_.z, range_.xmin, range_.xmax, range_.ymin, range_.ymax)


    def add_tile_boundary_layer(self, zooms: List[int] = None, *, zoom_style_dict: Dict[int, Dict] = {}, **style_kwargs):
        """
        Add a layer of GEMF tile boundaries.

        Parameters
        ----------
        zooms : List[int]
            Specify the zoom levels to show
        zoom_style_dict : Dict[int, Dict]
            Pass per-zoom-level visualization parameters. See `folium.Rectangle` for options.
        style_kwargs
            Common visualization parameters for all zoom levels. See `folium.Rectangle` for options.

        Note: the style options are applied with decreasing priority as `zoom_style_dict` > `style_kwargs` > `defaults`
        """
        # default to zoom levels present in GEMF
        if zooms is None:
            zooms = self._tile_zooms

        zoom_groups = self._add_layer_control_groups(zooms, "Tile Outlines", suffix="(bbox)")

        # add rudimentary tile layer
        DEFAULT_STYLE = {
            "weight": 1,
            "fill": False,
            "dash_array": "5, 5"
        }
        DEFAULT_STYLE.update(style_kwargs)


        def generate_colors_matplotlib(n, cmap_name="tab10"):
            import matplotlib as mpl
            import matplotlib.pyplot as plt

            cmap = plt.get_cmap(cmap_name)
            if hasattr(cmap, "colors"):  # discrete colormap
                colors = [mpl.colors.to_hex(c) for c in cmap.colors]
            else:  # continuous colormap — sample evenly
                colors = [mpl.colors.to_hex(cmap(i / max(1, n - 1))) for i in range(n)]

            return [colors[i % len(colors)] for i in range(n)]


        colors = generate_colors_matplotlib(len(zooms), cmap_name=self._cmap)
        zoom_colors = dict(zip(zooms, colors))

        def tile_bounds(tile):
            """Return tile bounds as (west, south, east, north)."""
            bounds = mercantile.bounds(tile)
            return bounds.west, bounds.south, bounds.east, bounds.north

        # draw tile boundary
        for tile in self.gemf.header.range_details:
            z, x, y = tile.z, tile.x, tile.y
            if z not in zooms: continue

            tile = mercantile.Tile(x=x, y=y, z=z)
            west, south, east, north = tile_bounds(tile)

            # update style
            tile_style = DEFAULT_STYLE.copy()               # use default style
            tile_style.update(color=zoom_colors[z])         # update by color assigned to zoom level
            tile_style.update(zoom_style_dict.get(z, {}))   # update by individual custom style per zoom level

            folium.Rectangle(
                bounds=[[south, west], [north, east]],
                tooltip=f"ZXY: {z}/{x}/{y}",
                **tile_style
            ).add_to(zoom_groups[z])

        self._add_legend(zoom_colors)


    # utils
    def get_image_center_from_tiles(self):
        """Determine the center of the plot as the center of the maximum bounds."""
        # TODO: need to extract tiles first then convert to bounds or do in one step
        # get tiles
        tiles = []
        for range_ in self.gemf.header.range_data.ranges:
            tiles_ = AbstractRange.get_tiles(**range_.to_dict())
            tiles.extend(tiles_)

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
        lat_center = (south + north) / 2
        lon_center = (west + east) / 2
        map_center = [lat_center, lon_center]
        return map_center


    def _add_layer_control_groups(self, zooms, group_name, suffix=""):
        """
        Utility to create layer control elements per zoom level.

        Note that a suffix is necessary as feature groups are identified by their name attribute.
        Hence, the shown name needs to be unique.
        """
        # create layer control for folium map
        parent_group = FeatureGroup(name=group_name)
        parent_group.add_to(self)  # 'self' is your folium Map or LayerControl container

        zoom_groups = {}
        for z_ in sorted(zooms):
            sep_ = "└─" if z_ == max(zooms) else "├─"   # create manual visual hierarchy
            zoom_groups[z_] = FeatureGroupSubGroup(parent_group, name=f"{sep_} Zoom {z_} {suffix}")
            zoom_groups[z_].add_to(self)  # Add subgroup to the map/layer collection

        return zoom_groups


    def _add_legend(self, zoom_colors: Dict):
        """Add a legend to the map, indicating the bounding box color for each zoom level."""

        # Add legend HTML
        legend_html = """
        <div style="
            position: fixed;
            top: 10px;
            right: 150px;
            width: 200px;
            background-color: white;
            padding: 10px;
            border: 2px solid grey;
            z-index: 9999;
            font-size: 14px;
        ">
        <b>Zoom Level Colors</b><br>
        """
        sorted_dict = {k: zoom_colors[k] for k in sorted(zoom_colors.keys())}
        for zoom, color in sorted_dict.items():
            legend_html += f'<i style="background:{color};width:18px;height:18px;float:left;margin-right:5px;opacity:0.7"></i>{zoom}<br>'
        legend_html += "</div>"
        self.get_root().html.add_child(folium.Element(legend_html))
