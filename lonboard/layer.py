from __future__ import annotations

import warnings
from pathlib import Path

import geopandas as gpd
import pyarrow as pa
import traitlets
from anywidget import AnyWidget

from lonboard.constants import EPSG_4326, EXTENSION_NAME, OGC_84
from lonboard.geoarrow.geopandas_interop import geopandas_to_geoarrow
from lonboard.traits import ColorAccessor, FloatAccessor, PyarrowTableTrait
from lonboard.viewport import compute_view

# bundler yields lonboard/static/{index.js,styles.css}
bundler_output_dir = Path(__file__).parent / "static"


class BaseLayer(AnyWidget):
    pass
    # Note: this _repr_keys is useful if subclassing directly from ipywidgets.Widget, as
    # that will try to print all the included keys by default
    # def _repr_keys(self):
    #     # Exclude the table_buffer from the repr; otherwise printing the buffer will
    #     # often crash the kernel.

    #     # TODO: also exclude keys when numpy array?
    #     exclude_keys = {"table_buffer"}
    #     for key in super()._repr_keys():
    #         if key in exclude_keys:
    #             continue

    #         yield key


class ScatterplotLayer(BaseLayer):
    _esm = bundler_output_dir / "scatterplot-layer.js"
    _layer_type = traitlets.Unicode("scatterplot").tag(sync=True)
    _initial_view_state = traitlets.Dict().tag(sync=True)

    table = PyarrowTableTrait(
        allowed_geometry_types={EXTENSION_NAME.POINT, EXTENSION_NAME.MULTIPOINT}
    )

    radius_units = traitlets.Unicode("meters", allow_none=True).tag(sync=True)
    radius_scale = traitlets.Float(allow_none=True).tag(sync=True)
    radius_min_pixels = traitlets.Float(allow_none=True).tag(sync=True)
    radius_max_pixels = traitlets.Float(allow_none=True).tag(sync=True)
    line_width_units = traitlets.Float(allow_none=True).tag(sync=True)
    line_width_scale = traitlets.Float(allow_none=True).tag(sync=True)
    line_width_min_pixels = traitlets.Float(allow_none=True).tag(sync=True)
    line_width_max_pixels = traitlets.Float(allow_none=True).tag(sync=True)
    stroked = traitlets.Bool(allow_none=True).tag(sync=True)
    filled = traitlets.Bool(allow_none=True).tag(sync=True)
    billboard = traitlets.Bool(allow_none=True).tag(sync=True)
    antialiasing = traitlets.Bool(allow_none=True).tag(sync=True)
    get_radius = FloatAccessor()
    get_fill_color = ColorAccessor()
    get_line_color = ColorAccessor()
    get_line_width = FloatAccessor()

    @classmethod
    def from_geopandas(cls, gdf: gpd.GeoDataFrame, **kwargs) -> ScatterplotLayer:
        if gdf.crs and gdf.crs not in [EPSG_4326, OGC_84]:
            warnings.warn("GeoDataFrame being reprojected to EPSG:4326")
            gdf = gdf.to_crs(OGC_84)

        table = geopandas_to_geoarrow(gdf)
        return cls(table=table, **kwargs)

    @traitlets.default("_initial_view_state")
    def _default_initial_view_state(self):
        return compute_view(self.table)

    @traitlets.validate("get_radius")
    def _validate_get_radius_length(self, proposal):
        if isinstance(proposal["value"], (pa.ChunkedArray, pa.Array)):
            if len(proposal["value"]) != len(self.table):
                raise traitlets.TraitError(
                    "`get_radius` must have same length as table"
                )

        return proposal["value"]

    @traitlets.validate("get_fill_color")
    def _validate_get_fill_color_length(self, proposal):
        if isinstance(proposal["value"], (pa.ChunkedArray, pa.Array)):
            if len(proposal["value"]) != len(self.table):
                raise traitlets.TraitError(
                    "`get_fill_color` must have same length as table"
                )

        return proposal["value"]

    @traitlets.validate("get_line_color")
    def _validate_get_line_color_length(self, proposal):
        if isinstance(proposal["value"], (pa.ChunkedArray, pa.Array)):
            if len(proposal["value"]) != len(self.table):
                raise traitlets.TraitError(
                    "`get_line_color` must have same length as table"
                )

        return proposal["value"]

    @traitlets.validate("get_line_width")
    def _validate_get_line_width_length(self, proposal):
        if isinstance(proposal["value"], (pa.ChunkedArray, pa.Array)):
            if len(proposal["value"]) != len(self.table):
                raise traitlets.TraitError(
                    "`get_line_width` must have same length as table"
                )

        return proposal["value"]


class PathLayer(BaseLayer):
    _esm = bundler_output_dir / "path-layer.js"
    _layer_type = traitlets.Unicode("path").tag(sync=True)
    _initial_view_state = traitlets.Dict().tag(sync=True)

    table = PyarrowTableTrait(
        allowed_geometry_types={
            EXTENSION_NAME.LINESTRING,
            EXTENSION_NAME.MULTILINESTRING,
        }
    )

    width_units = traitlets.Unicode(allow_none=True).tag(sync=True)
    width_scale = traitlets.Float(allow_none=True).tag(sync=True)
    width_min_pixels = traitlets.Float(allow_none=True).tag(sync=True)
    width_max_pixels = traitlets.Float(allow_none=True).tag(sync=True)
    joint_rounded = traitlets.Bool(allow_none=True).tag(sync=True)
    cap_rounded = traitlets.Bool(allow_none=True).tag(sync=True)
    miter_limit = traitlets.Int(allow_none=True).tag(sync=True)
    billboard = traitlets.Bool(allow_none=True).tag(sync=True)
    get_color = ColorAccessor()
    get_width = FloatAccessor()

    @classmethod
    def from_geopandas(cls, gdf: gpd.GeoDataFrame, **kwargs) -> PathLayer:
        if gdf.crs and gdf.crs not in [EPSG_4326, OGC_84]:
            warnings.warn("GeoDataFrame being reprojected to EPSG:4326")
            gdf = gdf.to_crs(OGC_84)

        table = geopandas_to_geoarrow(gdf)
        return cls(table=table, **kwargs)

    @traitlets.default("_initial_view_state")
    def _default_initial_view_state(self):
        return compute_view(self.table)

    @traitlets.validate("get_color")
    def _validate_get_color_length(self, proposal):
        if isinstance(proposal["value"], (pa.ChunkedArray, pa.Array)):
            if len(proposal["value"]) != len(self.table):
                raise traitlets.TraitError("`get_color` must have same length as table")

        return proposal["value"]

    @traitlets.validate("get_width")
    def _validate_get_width_length(self, proposal):
        if isinstance(proposal["value"], (pa.ChunkedArray, pa.Array)):
            if len(proposal["value"]) != len(self.table):
                raise traitlets.TraitError("`get_width` must have same length as table")

        return proposal["value"]


class SolidPolygonLayer(BaseLayer):
    _esm = bundler_output_dir / "solid-polygon-layer.js"
    _layer_type = traitlets.Unicode("solid-polygon").tag(sync=True)
    _initial_view_state = traitlets.Dict().tag(sync=True)

    table = PyarrowTableTrait(
        allowed_geometry_types={EXTENSION_NAME.POLYGON, EXTENSION_NAME.MULTIPOLYGON}
    )

    filled = traitlets.Bool(allow_none=True).tag(sync=True)
    extruded = traitlets.Bool(allow_none=True).tag(sync=True)
    wireframe = traitlets.Bool(allow_none=True).tag(sync=True)
    elevation_scale = traitlets.Float(allow_none=True).tag(sync=True)
    get_elevation = FloatAccessor()
    get_fill_color = ColorAccessor()
    get_line_color = ColorAccessor()

    @classmethod
    def from_geopandas(cls, gdf: gpd.GeoDataFrame, **kwargs) -> SolidPolygonLayer:
        if gdf.crs and gdf.crs not in [EPSG_4326, OGC_84]:
            warnings.warn("GeoDataFrame being reprojected to EPSG:4326")
            gdf = gdf.to_crs(OGC_84)

        table = geopandas_to_geoarrow(gdf)
        return cls(table=table, **kwargs)

    @traitlets.default("_initial_view_state")
    def _default_initial_view_state(self):
        return compute_view(self.table)

    @traitlets.validate("get_elevation")
    def _validate_get_elevation_length(self, proposal):
        if isinstance(proposal["value"], (pa.ChunkedArray, pa.Array)):
            if len(proposal["value"]) != len(self.table):
                raise traitlets.TraitError(
                    "`get_elevation` must have same length as table"
                )

        return proposal["value"]

    @traitlets.validate("get_fill_color")
    def _validate_get_fill_color_length(self, proposal):
        if isinstance(proposal["value"], (pa.ChunkedArray, pa.Array)):
            if len(proposal["value"]) != len(self.table):
                raise traitlets.TraitError(
                    "`get_fill_color` must have same length as table"
                )

        return proposal["value"]

    @traitlets.validate("get_line_color")
    def _validate_get_line_color_length(self, proposal):
        if isinstance(proposal["value"], (pa.ChunkedArray, pa.Array)):
            if len(proposal["value"]) != len(self.table):
                raise traitlets.TraitError(
                    "`get_line_color` must have same length as table"
                )

        return proposal["value"]
