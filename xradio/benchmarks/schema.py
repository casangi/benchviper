import dataclasses
from typing import Literal, Optional
import numpy
import xarray
import dask.array

from xradio.schema.typing import Attr, Coord, Coordof, Data, Dataof
from xradio.schema.metamodel import (
    ArraySchema,
    ArraySchemaRef,
    AttrSchemaRef,
    DatasetSchema,
    DictSchema,
)
from xradio.schema.check import (
    check_array,
    check_dataset,
    check_dict,
)
from xradio.schema.dataclass import (
    xarray_dataclass_to_dict_schema,
    xarray_dataclass_to_array_schema,
    xarray_dataclass_to_dataset_schema,
)
from xradio.schema.bases import (
    xarray_dataarray_schema,
    xarray_dataset_schema,
    dict_schema,
)
from xradio.schema.export import export_schema_json_file, import_schema_json_file

Dim1 = Literal["coord"]
Dim2 = Literal["coord2"]
Dim3 = Literal["coord3"]


@xarray_dataarray_schema
class _TestArraySchema:
    """
    Docstring of array schema

    Multiple lines!
    """

    data: Data[Dim1, complex]
    """Docstring of data"""
    coord: Coord[Dim1, float]
    """Docstring of coordinate"""
    attr1: Attr[str]
    """Required attribute"""
    attr2: Attr[int] = 123
    """Required attribute with default"""
    attr3: Optional[Attr[int]] = None
    """Optional attribute with default"""


# The equivalent of the above in the meta-model
TEST_ARRAY_SCHEMA = ArraySchema(
    schema_name=__name__ + "._TestArraySchema",
    dimensions=[["coord"]],
    coordinates=[
        ArraySchemaRef(
            schema_name=None,
            name="coord",
            dtypes=[numpy.dtype(float).str],
            dimensions=[["coord"]],
            coordinates=[],
            attributes=[],
            class_docstring=None,
            data_docstring=None,
            optional=False,
            default=None,
            docstring="Docstring of coordinate",
        ),
    ],
    dtypes=[numpy.dtype(complex).str],
    class_docstring="Docstring of array schema\n\nMultiple lines!",
    data_docstring="Docstring of data",
    attributes=[
        AttrSchemaRef(
            name="attr1",
            type="str",
            optional=False,
            default=None,
            docstring="Required attribute",
        ),
        AttrSchemaRef(
            name="attr2",
            type="int",
            optional=False,
            default=123,
            docstring="Required attribute with default",
        ),
        AttrSchemaRef(
            name="attr3",
            type="int",
            optional=True,
            default=None,
            docstring="Optional attribute with default",
        ),
    ],
)

@dict_schema
class _TestDictSchema:
    """
    Docstring of dict schema

    Multiple lines!
    """

    attr1: str
    """Required attribute"""
    attr2: int = 123
    """Required attribute with default"""
    attr3: Optional[int] = None
    """Optional attribute with default"""


# The equivalent of the above in the meta-model
TEST_DICT_SCHEMA = DictSchema(
    schema_name=__name__ + "._TestDictSchema",
    class_docstring="Docstring of dict schema\n\nMultiple lines!",
    attributes=[
        AttrSchemaRef(
            name="attr1",
            type="str",
            optional=False,
            default=None,
            docstring="Required attribute",
        ),
        AttrSchemaRef(
            name="attr2",
            type="int",
            optional=False,
            default=123,
            docstring="Required attribute with default",
        ),
        AttrSchemaRef(
            name="attr3",
            type="int",
            optional=True,
            default=None,
            docstring="Optional attribute with default",
        ),
    ],
)


@xarray_dataarray_schema
class _TestDatasetSchemaCoord:
    """
    Docstring of array schema for coordinate
    """

    data: Data[Dim1, float]
    """Docstring of coordinate data"""
    attr1: Attr[str]
    """Required attribute"""
    attr2: Attr[int] = 123
    """Required attribute with default"""
    attr3: Optional[Attr[int]] = None
    """Optional attribute with default"""


@xarray_dataset_schema
class _TestDatasetSchema:
    """
    Docstring of dataset schema

    Again multiple lines!
    """

    coord: Coordof[_TestDatasetSchemaCoord]
    """Docstring of coordinate"""
    coord2: Optional[Coord[Dim2, int]]
    """Docstring of second coordinate"""
    data_var: Dataof[_TestArraySchema]
    """Docstring of external data variable"""
    data_var_simple: Optional[Data[Dim2, numpy.float32]]
    """Docstring of simple optional data variable"""
    attr1: Attr[str]
    """Required attribute"""
    attr2: Attr[int] = 123
    """Required attribute with default"""
    attr3: Optional[Attr[int]] = None
    """Optional attribute with default"""


def _dataclass_to_dict(obj, ignore=[]):
    return {
        f.name: getattr(obj, f.name)
        for f in dataclasses.fields(type(obj))
        if f.name not in ignore
    }


# The equivalent of the above in the meta-model
TEST_DATASET_SCHEMA = DatasetSchema(
    schema_name=__name__ + "._TestDatasetSchema",
    dimensions=[["coord"], ["coord", "coord2"]],
    coordinates=[
        ArraySchemaRef(
            schema_name=__name__ + "._TestDatasetSchemaCoord",
            name="coord",
            dtypes=[numpy.dtype(float).str],
            dimensions=[["coord"]],
            optional=False,
            default=None,
            docstring="Docstring of coordinate",
            coordinates=[],
            attributes=_dataclass_to_dict(TEST_ARRAY_SCHEMA)["attributes"],
            class_docstring="Docstring of array schema for coordinate",
            data_docstring="Docstring of coordinate data",
        ),
        ArraySchemaRef(
            schema_name=None,
            name="coord2",
            dtypes=[numpy.dtype(int).str],
            dimensions=[["coord2"]],
            coordinates=[],
            attributes=[],
            class_docstring=None,
            data_docstring=None,
            optional=True,
            default=None,
            docstring="Docstring of second coordinate",
        ),
    ],
    data_vars=[
        ArraySchemaRef(
            name="data_var",
            optional=False,
            default=None,
            docstring="Docstring of external data variable",
            **_dataclass_to_dict(TEST_ARRAY_SCHEMA),
        ),
        ArraySchemaRef(
            schema_name=None,
            name="data_var_simple",
            dtypes=[numpy.dtype(numpy.float32).str],
            dimensions=[["coord2"]],
            coordinates=[],
            attributes=[],
            class_docstring=None,
            data_docstring=None,
            optional=True,
            default=None,
            docstring="Docstring of simple optional data variable",
        ),
    ],
    attributes=[
        AttrSchemaRef(
            name="attr1",
            type="str",
            optional=False,
            default=None,
            docstring="Required attribute",
        ),
        AttrSchemaRef(
            name="attr2",
            type="int",
            optional=False,
            default=123,
            docstring="Required attribute with default",
        ),
        AttrSchemaRef(
            name="attr3",
            type="int",
            optional=True,
            default=None,
            docstring="Optional attribute with default",
        ),
    ],
    class_docstring="Docstring of dataset schema\n\nAgain multiple lines!",
)


class TestSchema:
    """
    Benchmarks for schema operations
    Originally adapted from:
    https://github.com/casangi/xradio/blob/main/tests/unit/schema/test_schema.py
    """
    version = "xradio 1.0.2"

    def setup_cache(self):
        # Export schema for import test.
        #
        # This runs once per environment/commit and writes the schema
        # JSON to a well-known file. The benchmark itself can then
        # refer to that file path directly without needing any
        # additional arguments or cached attributes.
        export_schema_json_file(_TestDatasetSchema, "test_dataset_schema.json")

    def time_xarray_dataclass_to_array_schema(self):
        xarray_dataclass_to_array_schema(_TestArraySchema)

    def time_check_array(self):
        data = numpy.zeros(10, dtype=complex)
        coords = [("coord", numpy.arange(10, dtype=float))]
        attrs = {"attr1": "str", "attr2": 123, "attr3": 345}
        array = xarray.DataArray(data, coords, attrs=attrs)
        check_array(array, TEST_ARRAY_SCHEMA)

    # TBD if check_array is checking a failure
    def time_check_array_dask(self):
        data = dask.array.zeros(10, dtype=complex)
        coords = [("coord", numpy.arange(10, dtype=float))]
        attrs = {"attr1": "str", "attr2": 123, "attr3": 345}
        array = xarray.DataArray(data, coords, attrs=attrs)
        check_array(array, TEST_ARRAY_SCHEMA)

    def time_check_array_constructor_array_style(self):
        data = numpy.zeros(10, dtype=complex)
        coords = [("coord", numpy.arange(10, dtype=float))]
        attrs = {"attr1": "str", "attr2": 1234, "attr3": 345}
        array = _TestArraySchema(data=data, coords=coords, attrs=attrs)
        check_array(array, TEST_ARRAY_SCHEMA).expect()

    def time_check_array_constructor_dataclass_style(self):
        array = _TestArraySchema(
            data=numpy.zeros(10, dtype=complex),
            coord=numpy.arange(10, dtype=float),
            attr1="str",
            attr2=1234,
            attr3=345,
        )
        check_array(array, TEST_ARRAY_SCHEMA).expect()

    def time_check_array_constructor_from_dataarray(self):
        data = numpy.zeros(10, dtype=complex)
        coords = [("coord", numpy.arange(10, dtype=float))]
        attrs = {"attr1": "str", "attr2": 1234, "attr3": 345}
        array = xarray.DataArray(data, coords, attrs=attrs)
        array = _TestArraySchema(array)
        check_array(array, TEST_ARRAY_SCHEMA).expect()

    def time_check_array_constructor_from_dataarray_override(self):
        data = numpy.zeros(10, dtype=complex)
        coords = [("coord", numpy.arange(10, dtype=float))]
        attrs = {"attr1": "str", "attr2": 1234, "attr3": 345}
        array = xarray.DataArray(data, coords, attrs=attrs)
        array = _TestArraySchema(
            data=array,
            coords=[("coord", 1 + numpy.arange(10, dtype=float))],
            attrs={"attr1": "strstr", "attr2": 12345},
        )
        check_array(array, TEST_ARRAY_SCHEMA).expect()

    def time_check_array_constructor_auto_coords(self):
        array = _TestArraySchema(
            data=numpy.zeros(10, dtype=complex), attr1="str", attr2=1234, attr3=345
        )
        check_array(array, TEST_ARRAY_SCHEMA).expect()

    def time_check_array_constructor_list(self):
        array = _TestArraySchema(
            data=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            coord=("coord", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], {"asd": "foo"}),
            attr1="str",
            attr2=1234,
            attr3=345,
        )
        check_array(array, TEST_ARRAY_SCHEMA).expect()

    def time_check_array_constructor_defaults(self):
        array = _TestArraySchema(
            numpy.zeros(10, dtype=complex),
            numpy.arange(10, dtype=float),
            "str",
        )
        check_array(array, TEST_ARRAY_SCHEMA).expect()

    def time_check_array_constructor_mixed(self):
        array = _TestArraySchema(
            numpy.zeros(10, dtype=complex),
            attr1="str",
            coords={
                "coord": numpy.arange(10, dtype=float),
            },
            attrs={
                "attr2": 123,
            },
        )
        check_array(array, TEST_ARRAY_SCHEMA).expect()

    def time_check_array_extra_coord(self):
        coords2 = [
            ("coord", numpy.arange(10, dtype=float)),
            ("coord2", numpy.arange(1, dtype=float)),
        ]
        data2 = numpy.zeros(10, dtype=complex)[:, numpy.newaxis]
        attrs = {"attr1": "str", "attr2": 123, "attr3": 345}
        check_array(
            xarray.DataArray(data2, coords2, attrs=attrs), TEST_ARRAY_SCHEMA
        )

    def time_check_array_missing_coord(self):
        data0 = numpy.array(None, dtype=complex)
        attrs = {"attr1": "str", "attr2": 123, "attr3": 345}
        check_array(xarray.DataArray(data0, {}, attrs=attrs), TEST_ARRAY_SCHEMA)

    # TBD if assert has to be not
    def time_check_array_extra_attr(self):
        data = numpy.zeros(10, dtype=complex)
        coords = [("coord", numpy.arange(10, dtype=float))]
        attrs = {"attr1": "str", "attr2": 123, "attr3": 345, "attr4": "asd"}
        array = xarray.DataArray(data, coords, attrs=attrs)
        check_array(array, TEST_ARRAY_SCHEMA)

    def time_check_array_optional_attr(self):
        data = numpy.zeros(10, dtype=complex)
        coords = [("coord", numpy.arange(10, dtype=float))]
        attrs = {"attr1": "str", "attr2": 123}
        array = xarray.DataArray(data, coords, attrs=attrs)
        check_array(array, TEST_ARRAY_SCHEMA)

    def time_xarray_dataclass_to_dict_schema(self):
        xarray_dataclass_to_dict_schema(_TestDictSchema)

    def time_check_dict(self):
        data = {"attr1": "asd", "attr2": 234, "attr3": 345}
        issues = check_dict(data, TEST_DICT_SCHEMA)

    def time_check_dict_optional(self):
        data = {"attr1": "asd", "attr2": 234}
        issues = check_dict(data, TEST_DICT_SCHEMA)

    def time_check_dict_constructor(self):
        data = _TestDictSchema(attr1="asd", attr2=234, attr3=345)
        issues = check_dict(data, TEST_DICT_SCHEMA)

    def time_check_dict_constructor_defaults(self):
        data = _TestDictSchema(attr1="asd")
        issues = check_dict(data, TEST_DICT_SCHEMA)

    def time_xarray_dataclass_to_dataset_schema(self):
        xarray_dataclass_to_dataset_schema(_TestDatasetSchema)

    def time_check_dataset(self):
        attrs = {"attr1": "str", "attr2": 123, "attr3": 345}
        coords = {
            "coord": xarray.DataArray(
                numpy.arange(10, dtype=float), dims=("coord",), attrs=attrs
            ),
            "coord2": numpy.arange(5, dtype=int),
        }
        data_vars = {
            "data_var": ("coord", numpy.zeros(10, dtype=complex), attrs),
            "data_var_simple": ("coord2", numpy.zeros(5, dtype=numpy.float32)),
        }
        dataset = xarray.Dataset(data_vars, coords, attrs)
        check_dataset(dataset, TEST_DATASET_SCHEMA)

    def time_check_dataset_constructor_auto_coords(self):
        attrs = {"attr1": "str", "attr2": 123, "attr3": 345}
        dataset = _TestDatasetSchema(
            data_var=_TestArraySchema(
                dask.array.zeros(10, dtype=complex),
                dims=("coord",),
                coord=xarray.DataArray(
                    numpy.arange(10, dtype=float), dims=("coord",), attrs=attrs
                ),
                attrs=attrs,
            ),
            coord=xarray.DataArray(
                numpy.arange(10, dtype=float), dims=("coord",), attrs=attrs
            ),
            data_var_simple=("coord2", dask.array.zeros(25, dtype=numpy.float32)),
            attr1="str",
            attr2=123,
            attr3=345,
        )
        issues = check_dataset(dataset, TEST_DATASET_SCHEMA)

    def time_check_dataset_extra_datavar(self):
        attrs = {"attr1": "str", "attr2": 123, "attr3": 345}
        coords = {
            "coord2": numpy.arange(5, dtype=int),
            "coord": xarray.DataArray(
                numpy.arange(10, dtype=float), dims=("coord",), attrs=attrs
            ),
        }
        data_vars = {
            "data_var_simple": (("coord2",), numpy.zeros(5, dtype=numpy.float32)),
            "data_var": (("coord",), numpy.zeros(10, dtype=complex), attrs),
            "extra_data_var": (("coord",), numpy.ones(10, dtype=int), attrs),
        }
        dataset = xarray.Dataset(data_vars, coords, attrs)
        check_dataset(dataset, TEST_DATASET_SCHEMA)

    def time_check_dataset_optional_datavar(self):
        attrs = {"attr1": "str", "attr2": 123, "attr3": 345}
        coords = {
            "coord": xarray.DataArray(
                numpy.arange(10, dtype=float), dims=("coord",), attrs=attrs
            ),
            "coord2": numpy.arange(5, dtype=int),
        }
        data_vars = {
            "data_var": (("coord",), numpy.zeros(10, dtype=complex), attrs),
        }
        dataset = xarray.Dataset(data_vars, coords, attrs)
        check_dataset(dataset, TEST_DATASET_SCHEMA)

    def time_check_dataset_optional_coordinate(self):
        attrs = {"attr1": "str", "attr2": 123, "attr3": 345}
        coords = {
            "coord": xarray.DataArray(
                numpy.arange(10, dtype=float), dims=("coord",), attrs=attrs
            ),
        }
        data_vars = {
            "data_var": (("coord",), numpy.zeros(10, dtype=complex), attrs),
        }
        dataset = xarray.Dataset(data_vars, coords, attrs)
        check_dataset(dataset, TEST_DATASET_SCHEMA)

    def time_schema_export(self):
        export_schema_json_file(_TestDatasetSchema, "benchmark_schema_export.json")

    def time_schema_import(self):
        # Import the schema file exported once in ``setup_cache``.
        import_schema_json_file("test_dataset_schema.json")
