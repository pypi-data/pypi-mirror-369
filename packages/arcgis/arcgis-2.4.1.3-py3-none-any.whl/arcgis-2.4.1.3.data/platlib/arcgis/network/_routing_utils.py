import logging as _logging
from typing import Optional
import arcgis
from functools import lru_cache
from arcgis.gis import GIS
from arcgis.geoprocessing import import_toolbox as _import_toolbox
from arcgis._impl.common._utils import _validate_url
from arcgis.auth.tools import LazyLoader

_util = LazyLoader("arcgis._impl.common._utils")
_log = _logging.getLogger(__name__)

_use_async = False


@lru_cache(maxsize=50)
def _create_toolbox(url, gis, verbose=False):
    """holds the cached toolbox"""
    return _import_toolbox(url_or_item=url, gis=gis, verbose=verbose)


def get_travel_modes(gis: Optional[GIS] = None):
    """


    Get a list of travel modes that can be used with directions and routing services available in your portal.

    =================================================     ========================================================================
    **Parameter**                                          **Description**
    -------------------------------------------------     ------------------------------------------------------------------------
    gis                                                   Optional, the :class:`~arcgis.gis.GIS` on which this tool runs. If not specified, the active GIS is used.
    =================================================     ========================================================================


    :return: the following as a named tuple:
    * supported_travel_modes - Supported Travel Modes as a FeatureSet
    * default_travel_mode - Default Travel Mode as a str


    See `GetTravelModes <https://developers.arcgis.com/rest/network/api-reference/gettravelmodes-synchronous-task.htm>`_ for additional help.
    """

    if gis is None:
        gis = arcgis.env.active_gis

    url = gis.properties.helperServices.routingUtilities.url
    url = _validate_url(url, gis)
    tbx = _create_toolbox(url, gis)
    return tbx.get_travel_modes()


get_travel_modes.__annotations__ = {"return": tuple}


def get_tool_info(
    service_name: str = "asyncRoute",
    tool_name: str = "FindRoutes",
    gis: Optional[GIS] = None,
    include_network_source_info: bool = False,
):
    """
    Get additional information such as the description of the network dataset used
    for the analysis and the execution limits for a tool in a geoprocessing service.
    See `GetToolInfo <https://developers.arcgis.com/rest/services-reference/enterprise/gettoolinfo-tool.htm>`_
    for additional help.

    =================================================     ========================================================================
    **Parameter**                                          **Description**
    -------------------------------------------------     ------------------------------------------------------------------------
    service_name                                          Required string. Specify the service name containing the tool. The
                                                          parameter value should be specified using one of the following keywords
                                                          that reference a particular geoprocessing service. The default value is
                                                          *asyncRoute*.

                                                          * *asyncClosestFacility* - The asynchronous geoprocessing service
                                                            used to perform the closest facility analysis
                                                          * *asyncLocationAllocation* - The asynchronous geoprocessing service used
                                                            to perform the location-allocation analysis
                                                          * *asyncRoute* - The asynchronous geoprocessing service used to perform the
                                                            route analysis
                                                          * *asyncServiceArea* - The asynchronous geoprocessing service used to perform
                                                            the service area analysis
                                                          * *asyncVRP* - The asynchronous geoprocessing service used to perform the
                                                            vehicle routing problem analysis
                                                          * *syncVRP* - The synchronous geoprocessing service used to perform the vehicle
                                                            routing problem analysis.
                                                          * *asyncODCostMatrix*
    -------------------------------------------------     ------------------------------------------------------------------------
    tool_name                                             Required string. Specify the tool name in the geoprocessing service. The
                                                          parameter value should be a valid tool name in the geoprocessing service
                                                          specified by the *service_name* parameter. The default value is *FindRoutes*.

                                                          Choice list:

                                                          * *EditVehicleRoutingProblem*
                                                          * *FindClosestFacilities*
                                                          * *FindRoutes*
                                                          * *GenerateOriginDestinationCostMatrix*
                                                          * *GenerateServiceAreas*
                                                          * *SolveLocationAllocation*
                                                          * *SolveVehicleRoutingProblem*
    -------------------------------------------------     ------------------------------------------------------------------------
    gis                                                   Optional, the :class:`~arcgis.gis.GIS` on which this tool runs. If not
                                                          specified, the active GIS is used.
    -------------------------------------------------     ------------------------------------------------------------------------
    include_network_source_info                           Specify whether the information of all the source feature classes that
                                                          participate in the network dataset will be included. The default
                                                          value is *False*.
    =================================================     ========================================================================

    Returns:
       Tool Info as a str

    """

    if gis is None:
        gis = arcgis.env.active_gis

    url = gis.properties.helperServices.routingUtilities.url
    url = _validate_url(url, gis)
    tbx = _create_toolbox(url, gis)
    kwargs = {
        "service_name": service_name,
        "tool_name": tool_name,
        "gis": gis,
        "future": False,
        "include_network_source_info": include_network_source_info,
    }

    kwargs = _util.inspect_function_inputs(fn=tbx.get_tool_info, **kwargs)
    return tbx.get_tool_info(**kwargs)


get_tool_info.__annotations__ = {
    "service_name": str,
    "tool_name": str,
    "return": str,
}
