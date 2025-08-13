from __future__ import annotations
from typing import Any, Literal
import datetime as _dt

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
import urllib
from arcgis._impl.common._filters import GeometryFilter, StatisticFilter
from arcgis._impl.common._utils import _date_handler
from arcgis.auth import EsriSession
from arcgis.geometry import Geometry
import concurrent.futures
import copy
import json
from arcgis._impl.common._isd import InsensitiveDict
from arcgis._impl.common._mixins import PropertyMap
from arcgis.auth.tools import LazyLoader

arcgis_features = LazyLoader("arcgis.features")
pd = LazyLoader("pandas")


# ----------------------------------------------------------------------
def _encode_params(params: dict[str, Any]) -> dict[str, Any]:
    """
    Encodes the parameters for the request.

    :param params: dict
    :return: dict
    """
    if isinstance(params, dict):
        for k, v in copy.copy(params).items():
            if isinstance(v, (tuple, dict, list, bool)):
                params[k] = json.dumps(v, default=_date_handler)
            elif isinstance(v, PropertyMap):
                params[k] = json.dumps(dict(v), default=_date_handler)
            elif isinstance(v, InsensitiveDict):
                params[k] = v.json
    return params


class QueryParameters(BaseModel):
    model_config = ConfigDict(
        extra="ignore", use_enum_values=True, populate_by_name=True
    )
    where: str = Field(
        "1=1",
        alias="where",
        description="""Optional string. SQL-92 WHERE clause syntax on the fields in the layer
                    is supported for most data sources. Some data sources have restrictions
                    on what is supported. Hosted feature services in ArcGIS Enterprise running
                    on a spatiotemporal data source only support a subset of SQL-92.
                    Below is a list of supported SQL-92 with spatiotemporal-based feature services:

                    ('<=' | '>=' | '<' | '>' | '=' | '!=' | '<>' | LIKE)
                    (AND | OR)
                    (IS | IS_NOT)
                    (IN | NOT_IN) ( '(' ( expr ( ',' expr )* )? ')' )
                    COLUMN_NAME BETWEEN LITERAL_VALUE AND LITERAL_VALUE
                    """,
    )
    out_fields: str | list[str] | None = Field(
        "*",
        alias="outFields",
        description="""Optional list of fields to be included in the returned result set.
                    This list is a comma-delimited list of field names. You can also specify
                    the wildcard "*" as the value of this parameter. In this case, the query
                    results include all the field values.

                    .. note::
                        If specifying `return_count_only`, `return_id_only`, or `return_extent_only`
                        as True, do not specify this parameter in order to avoid errors.
                    """,
    )
    text: str | None = Field(
        None,
        alias="text",
        description="Optional String. A literal search text. If the layer has a display field associated with it, the server searches for this text in this field. Only used when querying a Map Feature Layer.",
    )
    time_filter: list[_dt.datetime] | str | None = Field(
        None,
        alias="timeFilter",
        description="""Optional list. The format is of [<startTime>, <endTime>] using
                    datetime.date, datetime.datetime or timestamp in milliseconds.
                    Syntax: time_filter=[<startTime>, <endTime>] ; specified as
                            datetime.date, datetime.datetime or timestamp in
                            milliseconds.
                    """,
    )
    geometry_filter: dict | None = Field(
        None,
        alias="geometryFilter",
        description="Optional from :attr:`~arcgis.geometry.filters`. Allows for the information to be filtered on spatial relationship with another geometry.",
    )
    return_geometry: bool | None = Field(
        True,
        alias="returnGeometry",
        description="Optional boolean. If true, geometry is returned with the query.",
    )
    return_count_only: bool | None = Field(
        False,
        alias="returnCountOnly",
        strict=True,
        description="""Optional boolean. If true, the response only includes the count
                    (number of features/records) that would be returned by a query.
                    Otherwise, the response is a feature set. The default is false. This
                    option supersedes the returnIdsOnly parameter. If
                    returnCountOnly = true, the response will return both the count and
                    the extent.
                    """,
    )
    return_ids_only: bool | None = Field(
        False,
        alias="returnIdsOnly",
        description="""Optional boolean. Default is False.  If true, the response only
                                            includes an array of object IDs. Otherwise, the response is a
                                            feature set. When object_ids are specified, setting this parameter to
                                            true is invalid.
                    """,
    )
    return_distinct_values: bool | None = Field(
        False,
        alias="returnDistinctValues",
        description="""Optional boolean.  If true, it returns distinct values based on the
                    fields specified in out_fields. This parameter applies only if the
                    `supportsAdvancedQueries` property of the layer is true. This parameter
                    can be used with return_count_only to return the count of distinct
                    values of subfields.

                    .. note::
                        Make sure to set return_geometry to False if this is set to True.
                        Otherwise, reliable results will not be returned.
                    """,
    )
    return_extent_only: bool | None = Field(
        False,
        alias="returnExtentOnly",
        description="""Optional boolean. If true, the response only includes the extent of
                    the features that would be returned by the query. If
                    returnCountOnly=true, the response will return both the count and
                    the extent.
                    The default is false. This parameter applies only if the
                    `supportsReturningQueryExtent` property of the layer is true.
                    """,
    )
    group_by_fields_for_statistics: str | None = Field(
        None,
        alias="groupByFieldsForStatistics",
        description="""Optional string. One or more field names on which the values need to
                    be grouped for calculating the statistics.
                    example: STATE_NAME, GENDER
                    """,
    )
    statistic_filter: dict | list[dict] | None = Field(
        None,
        alias="outStatistics",
        description="""Optional ``StatisticFilter`` instance. The definitions for one or more field-based
                    statistics can be added, e.g. statisticType, onStatisticField, or
                    outStatisticFieldName.

                    Syntax:

                    sf = StatisticFilter()
                    sf.add(statisticType="count", onStatisticField="1", outStatisticFieldName="total")
                    sf.filter
                    """,
    )
    result_offset: int | None = Field(
        None,
        alias="resultOffset",
        description="""Optional integer. This option can be used for fetching query results
                    by skipping the specified number of records and starting from the
                    next record (that is, resultOffset + 1th). This option is ignored
                    if return_all_records is True (i.e. by default).
                    """,
    )
    result_record_count: int | None = Field(
        None,
        alias="resultRecordCount",
        description="""Optional integer. This option can be used for fetching query results
                    up to the result_record_count specified. When result_offset is
                    specified but this parameter is not, the map service defaults it to
                    max_record_count. The maximum value for this parameter is the value
                    of the layer's max_record_count property. This option is ignored if
                    return_all_records is True (i.e. by default).
                    """,
    )
    object_ids: list[str] | str | None = Field(
        None,
        alias="objectIds",
        description="""Optional string. The object IDs of this layer or table to be queried.
                    The object ID values should be a comma-separated string.

                    .. note::
                        There might be a drop in performance if the layer/table data
                        source resides in an enterprise geodatabase and more than
                        1,000 object_ids are specified.
                    """,
    )
    distance: int | None = Field(
        None,
        alias="distance",
        description="""Optional integer. The buffer distance for the input geometries.
                    The distance unit is specified by units. For example, if the
                    distance is 100, the query geometry is a point, units is set to
                    meters, and all points within 100 meters of the point are returned.
                    """,
    )
    units: (
        Literal[
            "esriSRUnit_Meter",
            "esriSRUnit_StatuteMile",
            "esriSRUnit_Foot",
            "esriSRUnit_Kilometer",
            "esriSRUnit_NauticalMile",
            "esriSRUnit_USNauticalMile",
        ]
        | None
    ) = Field(
        None,
        alias="units",
        description="""Optional string. The unit for calculating the buffer distance. If
                    unit is not specified, the unit is derived from the geometry spatial
                    reference. If the geometry spatial reference is not specified, the
                    unit is derived from the feature service data spatial reference.
                    This parameter only applies if `supportsQueryWithDistance` is true.
                    """,
    )
    max_allowable_offset: int | None = Field(
        None,
        alias="maxAllowableOffset",
        description="""Optional float. This option can be used to specify the
                    max_allowable_offset to be used for generalizing geometries returned
                    by the query operation.
                    The max_allowable_offset is in the units of out_sr. If out_sr is not
                    specified, max_allowable_offset is assumed to be in the unit of the
                    spatial reference of the layer.
                    """,
    )
    out_sr: dict[str, Any] | str | int | None = Field(
        None,
        alias="outSR",
        description="Optional Integer: The WKID for the spatial reference of the returned geometry. Alternately, a SpatialReference object.",
    )
    geometry_precision: int | None = Field(
        None,
        alias="geometryPrecision",
        description="""Optional Integer. This option can be used to specify the number of
                    decimal places in the response geometries returned by the query
                    operation.
                    This applies to X and Y values only (not m or z-values).
                    """,
    )
    gdb_version: str | None = Field(
        None,
        alias="gdbVersion",
        description="""Optional string. The geodatabase version to query. This parameter
                    applies only if the isDataVersioned property of the layer is true.
                    If this is not specified, the query will apply to the published
                    map's version.
                    """,
    )
    order_by_fields: list[str] | str | None = Field(
        None,
        alias="orderByFields",
        description="""Optional string. One or more field names on which the
                    features/records need to be ordered. Use ASC or DESC for ascending
                    or descending, respectively, following every field to control the
                    ordering.
                    example: STATE_NAME ASC, RACE DESC, GENDER

                    .. note::
                        If specifying `return_count_only`, `return_id_only`, or `return_extent_only`
                        as True, do not specify this parameter in order to avoid errors.
                    """,
    )
    out_statistics: list[dict[str, Any]] | None = Field(
        None,
        alias="outStatistics",
        description="""Optional list of dictionaries. The definitions for one or more field-based
                    statistics to be calculated.

                    Syntax:

                    [
                        {
                            "statisticType": "<count | sum | min | max | avg | stddev | var>",
                            "onStatisticField": "Field1",
                            "outStatisticFieldName": "Out_Field_Name1"
                        },
                        {
                            "statisticType": "<count | sum | min | max | avg | stddev | var>",
                            "onStatisticField": "Field2",
                            "outStatisticFieldName": "Out_Field_Name2"
                        }
                    ]
                    """,
    )
    return_z: bool | None = Field(
        False,
        alias="returnZ",
        description="Optional boolean. If true, Z values are included in the results if the features have Z values. Otherwise, Z values are not returned.",
    )
    return_m: bool | None = Field(
        False,
        alias="returnM",
        description="Optional boolean. If true, M values are included in the results if the features have M values. Otherwise, M values are not returned.",
    )
    multipatch_option: tuple | None = Field(
        None,
        alias="multipatchOption",
        description="Optional x/y footprint. This option dictates how the geometry of a multipatch feature will be returned.",
    )
    quantization_parameters: dict[str, Any] | None = Field(
        None,
        alias="quantizationParameters",
        description="Optional dict. Used to project the geometry onto a virtual grid, likely representing pixels on the screen.",
    )
    return_centroid: bool | None = Field(
        False,
        alias="returnCentroid",
        description="""Optional boolean. Used to return the geometry centroid associated
                    with each feature returned. If true, the result includes the geometry
                    centroid. The default is false. Only supported on layer with
                    polygon geometry type.
                    """,
    )
    return_all_records: bool | None = Field(
        True,
        alias="returnAllRecords",
        description="""Optional boolean. When True, the query operation will call the
                    service until all records that satisfy the where_clause are
                    returned. Note: result_offset and result_record_count will be
                    ignored if return_all_records is True. Also, if return_count_only,
                    return_ids_only, or return_extent_only are True, this parameter
                    will be ignored. If this parameter is set to False but no other limit is
                    specified, the default is True.
                    """,
    )
    result_type: Literal["standard", "tile"] | None = Field(
        None,
        alias="resultType",
        description="Optional string. The result_type parameter can be used to control the number of features returned by the query operation.",
    )
    historic_moment: int | _dt.datetime | None = Field(
        None,
        alias="historicMoment",
        description="""Optional integer. The historic moment to query. This parameter
                    applies only if the layer is archiving enabled and the
                    supportsQueryWithHistoricMoment property is set to true. This
                    property is provided in the layer resource.

                    If historic_moment is not specified, the query will apply to the
                    current features.
                    """,
    )
    sql_format: Literal["standard", "native"] | None = Field(
        None,
        alias="sqlFormat",
        description="""Optional string.  The sql_format parameter can be either standard
                    SQL92 standard or it can use the native SQL of the underlying
                    datastore native. The default is none which means the sql_format
                    depends on useStandardizedQuery parameter.
                    """,
    )
    return_true_curves: bool | None = Field(
        False,
        alias="returnTrueCurves",
        description="""Optional boolean. When set to true, returns true curves in output
                    geometries. When set to false, curves are converted to densified
                    polylines or polygons.
                    """,
    )
    return_exceeded_limit_features: bool | None = Field(
        None,
        alias="returnExceededLimitFeatures",
        description="""Optional boolean. Optional parameter which is true by default. When
                    set to true, features are returned even when the results include
                    'exceededTransferLimit': True.

                    When set to false and querying with resultType = tile features are
                    not returned when the results include 'exceededTransferLimit': True.
                    This allows a client to find the resolution in which the transfer
                    limit is no longer exceeded without making multiple calls.
                    """,
    )
    datum_transformation: int | dict[str, Any] | None = Field(
        None,
        alias="datumTransformation",
        description="""Optional Integer/Dictionary.  This parameter applies a datum transformation while
                    projecting geometries in the results when out_sr is different than the layer's spatial
                    reference. When specifying transformations, you need to think about which datum
                    transformation best projects the layer (not the feature service) to the `outSR` and
                    `sourceSpatialReference` property in the layer properties. For a list of valid datum
                    transformation ID values ad well-known text strings, see `Coordinate systems and
                    transformations <https://developers.arcgis.com/net/latest/wpf/guide/coordinate-systems-and-transformations.htm>`_.
                    For more information on datum transformations, please see the transformation
                    parameter in the `Project operation <https://developers.arcgis.com/rest/services-reference/project.htm>`_.

                    **Examples**


                        ===========     ===================================
                        Inputs          Description
                        -----------     -----------------------------------
                        WKID            Integer. Ex: datum_transformation=4326
                        -----------     -----------------------------------
                        WKT             Dict. Ex: datum_transformation={"wkt": "<WKT>"}
                        -----------     -----------------------------------
                        Composite       Dict. Ex: datum_transformation=```{'geoTransforms':[{'wkid':<id>,'forward':<true|false>},{'wkt':'<WKT>','forward':<True|False>}]}```
                        ===========     ===================================
                    """,
    )
    range_values: dict[str, Any] | None = Field(
        None,
        alias="rangeValues",
        description="""Optional List. Allows you to filter features from the layer that are
                    within the specified range instant or extent. Only used when querying a Map Feature Layer.

                    .. code-block:: python

                        >>> range_values = [
                                            {
                                                "name": "range name" ,
                                                # single value or a value-range
                                                "value": <value> or [ <value1>, <value2> ]

                                            },
                                            {
                                                "name": "range name 2",
                                                "value": <value> or  [ <value3>, <value4> ]
                                            }
                                            ]


                    .. note::

                        `None` is allowed in value-range case to indicate infinity

                        .. code-block:: python

                            # all features with values <= 1500
                            >>> range_values = [
                                                {"name" : "range name",
                                                    "value" : [None, 1500]}
                                                ]

                            # all features with values >= 1000
                            >>> range_values = [
                                                {"name" : "range name",
                                                    "value" : [1000, None]}
                                                ]
                    """,
    )
    parameter_values: dict[str, Any] | None = Field(
        None,
        alias="parameterValues",
        description="""Optional Dict. Allows you to filter the layers by specifying
                    value(s) to an array of pre-authored parameterized filters for those
                    layers. When value is not specified for any parameter in a request,
                    the default value, that is assigned during authoring time, gets used
                    instead. Only used when querying a Map Feature Layer.

                    When a `parameterInfo` allows multiple values, you must pass them in
                    an array.

                    .. note::
                        Check `parameterValues` at the `Query (Map Service/Layer) <https://developers.arcgis.com/rest/services-reference/enterprise/query-map-service-layer-.htm#GUID-403AC0F3-4B48-45BD-B473-E52E790FD296>`_
                        for details on parameterized filters.
                    """,
    )
    format_3d_objects: (
        Literal[
            "3D_dae",
            "3D_dwg",
            "3D_fbx",
            "3D_glb",
            "3D_gltf",
            "3D_ifc",
            "3D_obj",
            "3D_shapebuffer",
            "3D_shapebufferg",
            "3D_usdc",
            "3D_usdz",
        ]
        | None
    ) = Field(
        None,
        alias="formatOf3DObjects",
        description="""Optional string. Specifies the 3D format that will be used to request
                    a feature. If set to a valid format ID (see layer resource), the geometry
                    of the feature response will be a 3D envelope of the 3D object and will
                    include asset maps for the 3D object. Since formats are created asynchronously,
                    review the flags field in the asset map to determine if the format is available
                    (conversionStatus is COMPLETED). If conversionStatus is INPROGRESS, the format
                    is not ready. Request the feature again later.

                    If a feature does not have the specified format, the feature will still be returned
                    according to the query parameters (such as the where clause), but the
                    asset mapping will be missing.
                    """,
    )
    time_reference_unknown_client: bool | None = Field(
        None,
        alias="timeReferenceUnknownClient",
        description="""Optional boolean. Setting `time_reference_unknown_client` as True
                    indicates that the client is capable of working with data values that
                    are not in UTC. If its not set to true, and the service layer's
                    datesInUnknownTimeZone property is true, then an error is returned.
                    The default is False

                    Its possible to define a service's time zone of date fields as unknown.
                    Setting the time zone as unknown means that date values will be returned
                    as-is from the database, rather than as date values in UTC. Non-hosted
                    feature services can be set to use an unknown time zone using
                    ArcGIS Server Manager. Setting the time zones to unknown also
                    sets the datesInUnknownTimeZone layer property as true. Currently,
                    hosted feature services do not support this setting. This setting does
                    not apply to editor tracking date fields which are stored and returned
                    in UTC even when the time zone is set to unknown.

                    Most clients released prior to ArcGIS Enterprise 10.9 will not be able
                    to work with feature services that have an unknown time setting.
                    """,
    )

    @field_validator("statistic_filter", mode="before")
    def validate_statistic_filter(cls, value):
        if value and isinstance(value, StatisticFilter):
            return value.filter  # Assumes `filter` is a method on StatisticFilter
        return value

    @field_validator("time_filter", mode="before")
    def validate_time_filter(cls, value):
        if isinstance(value, list):
            starttime = _date_handler(value[0])
            endtime = _date_handler(value[1])
            if starttime is None:
                starttime = "null"
            if endtime is None:
                endtime = "null"
            value = "%s,%s" % (starttime, endtime)
        return value

    @field_validator("geometry_filter", mode="before")
    def validate_geometry_filter(cls, value):
        if isinstance(value, GeometryFilter):
            return value.filter
        return value

    @field_validator("out_fields", mode="before")
    def validate_out_fields(cls, value):
        if isinstance(value, (list, tuple)):
            return ",".join(value)
        return value

    @field_validator("order_by_fields", mode="before")
    def validate_order_by_fields(cls, value):
        if isinstance(value, (list, tuple)):
            return ",".join(value)
        return value

    @field_validator("object_ids", mode="before")
    def validate_object_ids(cls, value):
        if isinstance(value, (list, tuple)):
            return ",".join(map(str, value))
        return value

    @model_validator(mode="before")
    def check_parameters(cls, values):
        # If either return_ids_only or return_count_only or return_extent_only is True, set return_all_records to False
        if (
            values.get("return_ids_only")
            or values.get("return_count_only")
            or values.get("return_extent_only")
            or values.get("result_record_count") is not None
        ):
            values["return_all_records"] = False

        # Check the conditions for order_by_fields
        if not values.get("return_all_records") or values.get("out_statistics") is None:
            if (
                values.get("return_count_only")
                or values.get("return_extent_only")
                or values.get("return_ids_only")
            ):
                # Set order_by_fields to None if the conditions are met
                values["order_by_fields"] = None

        return values


class Query:
    def __init__(
        self,
        layer,
        parameters,
        is_layer: bool = True,
        query_3d: bool = False,
        as_df: bool = False,
    ):
        self.layer = layer
        self.is_layer = is_layer
        self.query_3d = query_3d
        self.as_df = as_df
        self.parameters = self.create_parameters(parameters)
        self.url = None
        self._cached_record_count = None

    def create_parameters(
        self,
        parameters: QueryParameters,
    ) -> dict[str, Any]:
        # create parameters dictionary
        params: dict[str, Any] = parameters.model_dump(
            mode="json", exclude_none=True, by_alias=True
        )
        params["f"] = "json"

        # add optional parameters
        if self.layer._dynamic_layer is not None:
            params["layer"] = self.layer._dynamic_layer

        # Remove parameters that are not supported by 3D feature query
        if self.query_3d:
            del params["returnDistinctValues"]
            del params["returnCountOnly"]
            del params["returnIdsOnly"]

        # Remove parameters that are not supported by table query
        if self.is_layer is False:
            del params["returnCentroid"]
            del params["returnExtentOnly"]
            del params["returnGeometry"]
            del params["returnZ"]
            del params["returnM"]

        # layer specific workflows
        if parameters.out_fields != "*" and parameters.return_distinct_values is False:
            try:
                # Check if object id field is in out_fields. If it isn't, add it.
                # First find the object id field
                object_id_field = [
                    x.name
                    for x in self.layer.properties.fields
                    if x.type == "esriFieldTypeOID"
                ][0]
                # check if in outfields
                if object_id_field not in params["outFields"].split(","):
                    out_fields = object_id_field + "," + params["outFields"]
                    # update out_fields parameter
                    params["outFields"] = out_fields
            except (IndexError, AttributeError):
                pass

        if parameters.time_filter is None and self.layer.time_filter:
            params["time"] = self.layer.time_filter

        # Need to unpack geometry filter into parameters
        geom_filter = params.pop("geometryFilter", None)
        if geom_filter is not None:
            for key, val in parameters.geometry_filter.items():
                params[key] = val
        return params

    def execute(self):
        raw = True if self.query_3d else False
        self._get_url()

        # Two workflows: Return as FeatureSet or return as DataFrame
        return self._query(raw)

    def _get_url(self):
        if self.query_3d and hasattr(self.layer, "_is_3d") and self.layer._is_3d:
            url = self.layer._url + "/query3D"
        elif self.layer._dynamic_layer is None:
            url = self.layer._url + "/query"
        else:
            url = "%s/query" % self.layer._url.split("?")[0]
        self.url = url

    def _content_length(self, encoded_parameters: dict) -> int:
        return (
            len(urllib.parse.urlencode(encoded_parameters, doseq=True) + self.url) + 1
        )

    def _send_request(self, session: EsriSession, encoded_parameters: dict) -> dict:
        url_length: int = self._content_length(encoded_parameters)
        if url_length <= 2000 and encoded_parameters.get("geometry", None) is None:
            # TODO: @achapkowski @jtroe -> Discuss only using POST for all queries
            response = session.get(self.url, params=encoded_parameters)
        else:
            response = session.post(self.url, data=encoded_parameters)
        return response.json()

    def _query(self, raw=False):
        """Returns results of the query for the provided layer and URL."""
        try:
            encoded_parameters = _encode_params(self.parameters)
            # Perform the initial query
            session = self.layer._con._session
            result: dict = self._send_request(session, encoded_parameters)
            return self._process_query_result(result, raw)
        except Exception as query_exception:
            return self._handle_query_exception(query_exception)

    def _process_query_result(self, result, raw):
        """Processes the query result based on the parameters and handles pagination."""
        # Handle errors in the result
        if "error" in result:
            raise ValueError(result)

        # Determine the type of result to return
        if self._is_true(self.parameters.get("returnCountOnly")):
            return result["count"]
        elif self._is_true(self.parameters.get("returnIdsOnly")) or self._is_true(
            self.parameters.get("returnExtentOnly")
        ):
            return result
        elif self.parameters.get("outStatistics", None) or self.parameters.get(
            "groupByFieldsForStatistics", None
        ):
            if self.as_df:
                return self._query_df(result)
            return arcgis_features.FeatureSet.from_dict(result)
        elif self._is_true(raw):
            return result

        features = result.get("features", [])
        if self._needs_more_features(features):
            # Pagination workflow
            if (
                self.parameters.get("objectIds")
                or self.parameters.get("orderByFields")
                or self.parameters.get("geometryFilter")
                or self.parameters.get("statisticFilter")
            ):
                # For certain parameters, we do not expect all records to be returned or they have to be returned in a specific order
                features = self._fetch_all_features_single_thread(features, result)
            else:
                # Otherwise, we use a concurrent workflow with ids to fetch all features
                # This workflow also works if pagination is not supported
                features = self._fetch_all_features_by_chunk()

        result["features"] = features
        if self.as_df:
            return self._query_df(result)
        return arcgis_features.FeatureSet.from_dict(result)

    def _is_true(self, x):
        if isinstance(x, bool) and x:
            return True
        elif isinstance(x, str) and x.lower() == "true":
            return True
        else:
            return False

    def _needs_more_features(self, features):
        """
        Determines if additional query requests are needed to retrieve more features.
        """
        fetched = len(features)
        requested_feature_count = self.parameters.get("resultRecordCount")
        total_available = self._fetch_total_records_count()

        # If we've already fetched everything available, don't fetch more
        if fetched >= total_available:
            return False

        # If user defined a cap, and we haven't hit it, continue
        if requested_feature_count is not None:
            return fetched < requested_feature_count

        # Default case: no user cap, fetch until we've got everything
        return fetched < total_available

    def _fetch_all_features_single_thread(self, features, result):
        """Fetches all features by handling pagination."""
        original_record_count = self.parameters.get("resultRecordCount")
        original_offset = self.parameters.get("resultOffset", 0)

        while result.get("exceededTransferLimit") is True:
            if original_record_count is not None:
                remaining_record_count = original_record_count - len(features)
                if remaining_record_count <= 0:
                    break
                self.parameters["resultRecordCount"] = remaining_record_count

            # len of features is the new offset each time
            self.parameters["resultOffset"] = len(features) + original_offset
            encoded_parameters = _encode_params(self.parameters)
            result: dict = self._send_request(
                session=self.layer._con._session,
                encoded_parameters=encoded_parameters,
            )
            features += result.get("features", [])

        return features

    def _fetch_total_records_count(self):
        if self._cached_record_count is not None:
            # If we have a cached count, return it
            return self._cached_record_count

        count_params = copy.deepcopy(self.parameters)
        count_params["returnCountOnly"] = True
        count_params["returnAllRecords"] = False  # must be false when above True
        count_params = _encode_params(count_params)
        count_result: dict = self._send_request(
            session=self.layer._con._session,
            encoded_parameters=count_params,
        )
        self._cached_record_count = count_result.get("count")
        return self._cached_record_count

    def _fetch_all_ids(self):
        """Query to create a list of object ids."""
        ids = []
        id_params = copy.deepcopy(self.parameters)
        id_params["returnIdsOnly"] = True
        id_params["returnAllRecords"] = False  # must be false when above True
        original_offset = id_params.get("resultOffset", 0)

        # Get the total count of ids
        all_records = self._fetch_total_records_count()
        user_requested_records = id_params.get("resultRecordCount")
        total_count = all_records - original_offset
        if user_requested_records and user_requested_records < total_count:
            total_count = user_requested_records

        # Perform query until all ids are fetched
        while True:
            encoded_params = _encode_params(id_params)
            result: dict = self._send_request(
                session=self.layer._con._session,
                encoded_parameters=encoded_params,
            )
            ids.extend(result.get("objectIds", []))

            if len(ids) >= total_count:
                break
            id_params["resultOffset"] = original_offset + len(ids)
            if id_params.get("resultRecordCount") is not None:
                id_params["resultRecordCount"] = total_count - len(ids)
        return ids

    def _fetch_all_features_by_chunk(self):
        """
        This workflow is used when users specify resultRecordCount.
        """
        features = []  # start from an empty list
        # Step 1: Query for all the ids using the parameters set
        ids = self._fetch_all_ids()

        # Step 2: Define function to fetch a page of features
        def fetch_page(ids_subset):
            page_params = copy.deepcopy(self.parameters)
            if "resultOffset" in page_params:
                del page_params["resultOffset"]
            if "resultRecordCount" in page_params:
                del page_params["resultRecordCount"]
            page_params["objectIds"] = ids_subset
            page_params = _encode_params(page_params)

            return self._send_request(
                session=self.layer._con._session,
                encoded_parameters=page_params,
            )

        # Step 3: Use ThreadPoolExecutor to send multiple requests concurrently
        with concurrent.futures.ThreadPoolExecutor(5) as executor:
            futures = []
            # Calculate the number of requests needed, using page_size for offset increment
            page_size = 200  # anything larger causes the server to crash
            for i in range(0, len(ids), page_size):
                ids_subset = ",".join(str(i) for i in ids[i : i + page_size])
                futures.append(executor.submit(fetch_page, ids_subset))

            # Step 4: Process the results
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if not isinstance(result, dict):
                    result = result.json()
                features += result.get("features", [])
        return features

    def _handle_query_exception(self, query_exception):
        """Handles exceptions raised during the query process."""
        error_messages = [
            "Error performing query operation",
            "HTTP Error 504: GATEWAY_TIMEOUT",
        ]

        if any(msg in str(query_exception) for msg in error_messages):
            return self._retry_query_with_fewer_records()

        raise query_exception

    def _retry_query_with_fewer_records(self):
        """Retries the query with a reduced result record count."""
        max_record = self.parameters.get(
            "resultRecordCount", self._fetch_total_records_count()
        )
        offset = self.parameters.get("resultOffset", 0)

        if max_record < 250:
            raise Exception("Max record count too low; query still failing.")

        result = None
        max_rec = (max_record + 1) // 2  # Halve the record count
        i = 0

        while max_rec * i < max_record:
            self.parameters["resultRecordCount"] = min(
                max_rec, max_record - max_rec * i
            )
            self.parameters["resultOffset"] = offset + max_rec * i

            try:
                records = self._query(raw=True)
                if result:
                    result["features"].extend(records["features"])
                else:
                    result = records
                i += 1
            except Exception as retry_exception:
                raise retry_exception

        return result

    def _query_df(self, result):
        """returns results of a query as a pd.DataFrame"""
        _fld_lu = {
            "esriFieldTypeSmallInteger": pd.Int32Dtype(),
            "esriFieldTypeInteger": pd.Int32Dtype(),
            "esriFieldTypeSingle": pd.Float64Dtype(),
            "esriFieldTypeDouble": pd.Float64Dtype(),
            "esriFieldTypeFloat": pd.Float64Dtype(),
            "esriFieldTypeString": pd.StringDtype(),
            "esriFieldTypeDate": "<M8[ns]",
            "esriFieldTypeOID": pd.Int64Dtype(),
            "esriFieldTypeGeometry": object,
            "esriFieldTypeBlob": object,
            "esriFieldTypeRaster": object,
            "esriFieldTypeGUID": pd.StringDtype(),
            "esriFieldTypeGlobalID": pd.StringDtype(),
            "esriFieldTypeXML": object,
            "esriFieldTypeTimeOnly": pd.StringDtype(),
            "esriFieldTypeDateOnly": "<M8[ns]",
            "esriFieldTypeTimestampOffset": object,
            "esriFieldTypeBigInteger": pd.Int64Dtype(),
        }

        def feature_to_row(feature, sr):
            """:return: a feature from a dict"""
            geom = feature["geometry"] if "geometry" in feature else None
            attribs = feature["attributes"] if "attributes" in feature else {}
            if "centroid" in feature:
                if attribs is None:
                    attribs = {"centroid": feature["centroid"]}
                elif "centroid" in attribs:
                    import uuid

                    fld = "centroid_" + uuid.uuid4().hex[:2]
                    attribs[fld] = feature["centroid"]
                else:
                    attribs["centroid"] = feature["centroid"]
            if geom:
                if "spatialReference" not in geom:
                    geom["spatialReference"] = sr
                attribs["SHAPE"] = Geometry(geom)
            return attribs

        if len(result["features"]) == 0:
            # create columns even if empty dataframe
            columns = {}
            for fld in self.layer.properties.fields:
                fld = dict(fld)
                columns[fld["name"]] = _fld_lu[fld["type"]]
            if (
                "geometryType" in self.layer.properties
                and self.layer.properties.geometryType is not None
            ):
                columns["SHAPE"] = object
            if (
                "return_geometry" in self.parameters
                and self.parameters["return_geometry"] == False
            ):
                columns.pop("SHAPE", None)
            df = pd.DataFrame([], columns=columns.keys()).astype(columns, True)
            if "out_fields" in self.parameters and self.parameters["out_fields"] != "*":
                df = df[self.parameters["out_fields"].split(",")].copy()

            if "SHAPE" in df.columns:
                df["SHAPE"] = arcgis_features.geo._array.GeoArray([])
                df.spatial.set_geometry("SHAPE")
                df.spatial.renderer = self.layer.renderer
                df.spatial._meta.source = self.layer
                df.spatial._meta.geometry_type = (
                    self.layer.properties["geometryType"]
                    .replace("esriGeometry", "")
                    .lower()
                )

            return pd.DataFrame([], columns=columns).astype(columns)
        sr = None
        if "spatialReference" in result:
            sr = result["spatialReference"]

        rows = [feature_to_row(row, sr) for row in result["features"]]
        if len(rows) == 0:
            return None
        df = pd.DataFrame.from_records(data=rows)
        # set based on layer
        df.spatial.renderer = self.layer.renderer
        df.spatial._meta.source = self.layer.url
        if "geometryType" in dict(self.layer.properties):
            df.spatial._meta.geometry_type = (
                self.layer.properties["geometryType"]
                .replace("esriGeometry", "")
                .lower()
            )
        if "SHAPE" in df.columns:
            df.loc[df.SHAPE.isna(), "SHAPE"] = None
            df.spatial.set_geometry("SHAPE")

        # work with the fields and their data types
        dfields = []
        dtypes = {}
        if "fields" in result:
            fields = result["fields"]
            for fld in fields:
                if fld["type"] != "esriFieldTypeGeometry":
                    dtypes[fld["name"]] = _fld_lu[fld["type"]]
                if fld["type"] in [
                    "esriFieldTypeDate",
                    "esriFieldTypeDateOnly",
                    "esriFieldTypeTimestampOffset",
                ]:
                    dfields.append(fld["name"])

        if len(dfields) > 0:
            for fld in [fld for fld in dfields if fld in df.columns]:
                if not pd.api.types.is_datetime64_any_dtype(df[fld]):
                    try:
                        df[fld] = pd.to_datetime(
                            df[fld] / 1000,
                            errors="coerce",
                            unit="s",
                        )
                    except Exception:
                        df[fld] = pd.to_datetime(
                            df[fld],
                            errors="coerce",
                        )

        if dtypes:
            df = df.astype(dtypes)

        return df
