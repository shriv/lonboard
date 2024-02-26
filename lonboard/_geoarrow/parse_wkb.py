"""Handle GeoArrow tables with WKB-encoded geometry
"""
from typing import Tuple

import pyarrow as pa
import shapely

from lonboard._constants import EXTENSION_NAME
from lonboard._geoarrow.crs import get_field_crs
from lonboard._geoarrow.extension_types import construct_geometry_array


def parse_wkb_table(table: pa.Table) -> pa.Table:
    """Parse a table with a WKB column into GeoArrow-native geometries.

    If no columns are WKB-encoded, returns the input. Note that WKB columns must be
    tagged with an extension name of `geoarrow.wkb` or `ogc.wkb`
    """
    wkb_names = {EXTENSION_NAME.WKB, EXTENSION_NAME.OGC_WKB}
    for field_idx in range(len(table.schema)):
        field = table.field(field_idx)
        column = table.column(field_idx)

        if not field.metadata:
            continue

        extension_type_name = field.metadata.get(b"ARROW:extension:name")
        if extension_type_name in wkb_names:
            new_field, new_column = parse_wkb_column(field, column)
            table = table.set_column(field_idx, new_field, new_column)

    return table


def parse_wkb_column(
    field: pa.Field, column: pa.ChunkedArray
) -> Tuple[pa.Field, pa.ChunkedArray]:
    crs_str = get_field_crs(field)

    # We call shapely.from_wkb on the _entire column_ so that we don't get mixed type
    # arrays in each column.
    shapely_arr = shapely.from_wkb(column)
    new_field, geom_arr = construct_geometry_array(
        shapely_arr,
        crs_str=crs_str,
    )

    # Slice full array to maintain chunking
    chunk_offsets = [0]
    for chunk in column.chunks:
        chunk_offsets.append(len(chunk) + chunk_offsets[-1])

    chunks = []
    for start_slice, end_slice in zip(chunk_offsets[:-1], chunk_offsets[1:]):
        chunks.append(geom_arr.slice(start_slice, end_slice - start_slice))

    return new_field, pa.chunked_array(chunks)
