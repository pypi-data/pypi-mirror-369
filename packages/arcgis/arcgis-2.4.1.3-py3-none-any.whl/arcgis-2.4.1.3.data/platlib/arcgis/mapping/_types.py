from __future__ import absolute_import, annotations

import logging
from re import findall
from warnings import warn
from contextlib import contextmanager
from typing import Any, Optional, Union
from arcgis.gis import Item
from arcgis.geoprocessing import import_toolbox
from arcgis.auth.tools import LazyLoader
from datetime import timezone
from arcgis._impl.common._deprecate import deprecated
from arcgis.gis._impl._util import _get_item_url
from arcgis._impl.common._utils import _validate_url

collections = LazyLoader("collections")
json = LazyLoader("json")
os = LazyLoader("os")
pathlib = LazyLoader("pathlib")
tempfile = LazyLoader("tempfile")
time = LazyLoader("time")
datetime = LazyLoader("datetime")
arcgis = LazyLoader("arcgis")
_arcgis_features = LazyLoader("arcgis.features")
_gis = LazyLoader("arcgis.gis")
_mixins = LazyLoader("arcgis._impl.common._mixins")
_geometry = LazyLoader("arcgis.geometry")
_layers = LazyLoader("arcgis.layers")
_log = logging.getLogger(__name__)
_imports = LazyLoader("arcgis._impl.imports")


###########################################################################
@contextmanager
def _tempinput(data):
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write((bytes(data, "UTF-8")))
    temp.close()
    yield temp.name
    os.unlink(temp.name)


###########################################################################
class _ApplicationProperties(object):
    """
    This class is responsible for containing the viewing and editing
    properties of the web map. There are specific objects within this
    object that are applicable only to Collector and Offline Mapping.
    """

    _app_prop = None

    def __init__(self, prop=None):
        template = {"viewing": {}, "offline": {}, "editing": {}}
        if prop and isinstance(prop, (dict, _mixins.PropertyMap)):
            self._app_prop = _mixins.PropertyMap(dict(prop))
        else:
            self._app_prop = _mixins.PropertyMap(template)

    @property
    def properties(self):
        """represents the application properties"""
        return self._app_prop

    # ----------------------------------------------------------------------
    def __repr__(self):
        return json.dumps(dict(self._app_prop))

    # ----------------------------------------------------------------------
    def __str__(self):
        return json.dumps(dict(self._app_prop))

    # ----------------------------------------------------------------------
    @property
    def location_tracking(self):
        """gets the location_tracking value"""
        if (
            "editing" in self._app_prop
            and "locationTracking" in self._app_prop["editing"]
        ):
            return self._app_prop["editing"]["locationTracking"]
        else:
            self._app_prop["editing"]["locationTracking"] = {"enabled": False}
            return self._app_prop["editing"]["locationTracking"]

    # ----------------------------------------------------------------------


###########################################################################
@deprecated(
    deprecated_in="2.4.0",
    removed_in="2.4.2",
    details="Use the PackagingJob class found in `arcgis.map.offline_mapping.PackagingJob` instead.",
)
class PackagingJob(object):
    """
    The ``PackagingJob`` class represents a Single Packaging Job.


    ================  ===============================================================
    **Parameter**      **Description**
    ----------------  ---------------------------------------------------------------
    future            Required `Future <https://docs.python.org/3/library/concurrent.futures.html>`_ object. The async object created by
                      the ``geoprocessing`` :class:`~arcgis.geoprocessing.GPTask`.
    ----------------  ---------------------------------------------------------------
    notify            Optional Boolean.  When set to ``True``, a message will inform the
                      user that the ``geoprocessing`` task has completed. The default is
                      ``False``.
    ================  ===============================================================

    """

    _future = None
    _gis = None
    _start_time = None
    _end_time = None

    # ----------------------------------------------------------------------
    def __init__(self, future, notify=False):
        """
        initializer
        """
        self._future = future
        self._start_time = datetime.datetime.now()
        if notify:
            self._future.add_done_callback(self._notify)
        self._future.add_done_callback(self._set_end_time)

    # ----------------------------------------------------------------------
    @property
    def elapse_time(self):
        """
        Reports the total amout of time that passed while the
        :class:`~arcgis.layers.PackagingJob` ran.

        :return:
            The elapsed time

        """
        if self._end_time:
            return self._end_time - self._start_time
        else:
            return datetime.datetime.now() - self._start_time

    # ----------------------------------------------------------------------
    def _set_end_time(self, future):
        """sets the finish time"""
        self._end_time = datetime.datetime.now()

    # ----------------------------------------------------------------------
    def _notify(self, future):
        """prints finished method"""
        jobid = str(self).replace("<", "").replace(">", "")
        try:
            res = future.result()
            infomsg = "{jobid} finished successfully.".format(jobid=jobid)
            _log.info(infomsg)
            print(infomsg)
        except Exception as e:
            msg = str(e)
            msg = "{jobid} failed: {msg}".format(jobid=jobid, msg=msg)
            _log.info(msg)
            print(msg)

    # ----------------------------------------------------------------------
    def __str__(self):
        return "<Packaging Job>"

    # ----------------------------------------------------------------------
    def __repr__(self):
        return "<Packaging Job>"

    # ----------------------------------------------------------------------
    @property
    def status(self):
        """
        Get the GP status of the call.

        :return:
            A String
        """
        return self._future.done()

    # ----------------------------------------------------------------------
    def cancel(self):
        """
        The ``cancel`` method attempts to cancel the job.

        .. note::
            If the call is currently being executed
            or finished running and cannot be cancelled then the method will
            return ``False``, otherwise the call will be cancelled and the method
            will return True.

        :return:
            A boolean indicating the call will be cancelled (True), or cannot be cancelled (False)
        """
        if self.done():
            return False
        if self.cancelled():
            return False
        return True

    # ----------------------------------------------------------------------
    def cancelled(self):
        """
        The ``cancelled`` method retrieves whether the call was successfully cancelled.

        :return:
            A boolean indicating success (True), or failure (False)
        """
        return self._future.cancelled()

    # ----------------------------------------------------------------------
    def running(self):
        """
        The ``running`` method retrieves whether the call is currently being executed and cannot be cancelled.

        :return:
            A boolean indicating success (True), or failure (False)
        """
        return self._future.running()

    # ----------------------------------------------------------------------
    def done(self):
        """
        The ``done`` method retrieves whether the call was successfully cancelled or finished running.

        :return:
            A boolean indicating success (True), or failure (False)
        """
        return self._future.done()

    # ----------------------------------------------------------------------
    def result(self):
        """
        The ``result`` method retrieves the value returned by the call.

        .. note::
            If the call hasn't yet completed then this method will wait.

        :return:
            An Object
        """
        if self.cancelled():
            return None
        return self._future.result()


###########################################################################
@deprecated(
    deprecated_in="2.4.0",
    removed_in="2.4.2",
    details="Use the OfflineMapAreaManager class found in `arcgis.map.OfflineMapAreaManager` instead.",
)
class OfflineMapAreaManager(object):
    """
    The ``OfflineMapAreaManager`` is a helper class to manage offline map areas
    for a Web Map :class:`~arcgis.gis.Item`. Objects of this class should not
    be initialized directly, but rather accessed using the
    :attr:`~arcgis.map.Map.offline_areas` property on a
    :class:`~arcgis.map.Map` object.

    .. code-block:: python

        >>> from arcgis.gis import GIS
        >>> from arcgis.map import Map

        >>> gis = GIS(profile="your_Web_GIS_profile")

        >>> wm_item = gis.content.get("<web map id>")
        >>> wm_obj = Map(wm_item)

        >>> oma_mgr = wm_obj.offline_areas
        <arcgis.layers._types.OfflineMapAreaManager at <memory_addr>>

    .. note::
        There are important concepts to understand about offline mapping before
        the properties and methods of this class will function properly. Both
        reference basemaps and operational layers contained in a *Web Map* must
        be configured very specifically before they can be taken offline. See the
        documentation below for full details:

        * `ArcGIS Enterprise <https://enterprise.arcgis.com/en/portal/latest/use/take-maps-offline.htm>`_

          * `Basemap Considerations for ArcGIS Enterprise <https://enterprise.arcgis.com/en/portal/11.2/use/take-maps-offline.htm#ESRI_SECTION2_384E9B7E99EC4460810B947DE70FB2DA>`_

        * `ArcGIS Online <https://doc.arcgis.com/en/arcgis-online/manage-data/take-maps-offline.htm>`_
    """

    _pm = None
    _gis = None
    _tbx = None
    _item = None
    _portal = None
    _web_map = None

    # ----------------------------------------------------------------------
    def __init__(self, item, gis):
        arcgismapping = _imports.get_arcgis_map_mod(True)

        self._gis = gis
        self._portal = gis._portal
        self._item = item
        self._map = arcgismapping.Map(self._item)
        try:
            self._url = self._gis.properties.helperServices.packaging.url
            self._pm = self._gis._tools.packaging

        except Exception:
            warn("GIS does not support creating packages for offline usage")

    # ----------------------------------------------------------------------
    @property
    def offline_properties(self):
        """
        This property allows users to configure the offline properties
        for a webmap.  The `offline_properties` allows for defining
        how available offline editing, basemap, and read-only layers
        behave in the web map application. For further reading about concepts
        for working with web maps offline, see
        `Configure the map to work offline <https://doc.arcgis.com/en/field-maps/latest/prepare-maps/configure-the-map.htm#ESRI_SECTION1_1822CD8DD1E74F08BC4308E03A5677F1>`_.
        Also, see the *applicationProperties* object in the
        `Web Map specification <https://developers.arcgis.com/web-map-specification/objects/applicationProperties>`_.

        ==================     ====================================================================
        **Parameter**          **Description**
        ------------------     --------------------------------------------------------------------
        values                 Required Dict.  The key/value pairs that define the offline
                               application properties.
        ==================     ====================================================================

        The dictionary supports the following keys:

        ==================     ====================================================================
        **Key**                **Values**
        ------------------     --------------------------------------------------------------------
        download               Optional string. Possible values:

                               - *None*
                               - *features*
                               - *features_and_attachments*

                               When editing layers, the edits are always sent to the server. This
                               string argument indicates which data is retrieved from the server.

                               * If argument is *None* - only the schema is written since neither
                                 features nor attachments are retrieved
                               * If argument is *features* - a full sync without downloading
                                 attachments occurs
                               * If argument is *features_and_attachments*, which is the Default -
                                 both features and attachments are retrieved
        ------------------     --------------------------------------------------------------------
        sync                   `sync` applies to editing layers only.  This string value indicates
                               how the data is synced:

                               * ``sync_features_and_attachments``  - bidirectional sync
                               * ``sync_features_upload_attachments`` - bidirectional sync for
                                 features but upload only for attachments
                               * ``upload_features_and_attachments`` - upload only for both features
                                 and attachments (initial replica is just a schema)
        ------------------     --------------------------------------------------------------------
        reference_basemap      The filename of a basemap that has been copied to a mobile device.
                               This can be used instead of the default basemap for the map to
                               reduce downloads.
        ------------------     --------------------------------------------------------------------
        get_attachments        Boolean value that indicates whether to include attachments with the
                               read-only data.
        ==================     ====================================================================

        :return: Dictionary

        .. code-block:: python

            # USAGE EXAMPLE

            >>> from arcgis.gis import GIS
            >>> from arcgis.map import Map

            >>> wm_item = gis.content.get("<web_map_id>")
            >>> wm_obj = Map(wm_item)

            >>> offline_mgr = wm_obj.offline_areas
            >>> offline_mgr.offline_properties = {"download": "features",
                                                  "sync": "sync_features_upload_attachments"}

        """
        dl_lu = {
            "features": "features",
            "featuresAndAttachments": "features_and_attachments",
            "features_and_attachments": "featuresAndAttachments",
            "none": None,
            "None": "none",
            None: "none",
            "syncFeaturesAndAttachments": "sync_features_and_attachments",
            "sync_features_and_attachments": "syncFeaturesAndAttachments",
            "syncFeaturesUploadAttachments": "sync_features_upload_attachments",
            "sync_features_upload_attachments": "syncFeaturesUploadAttachments",
            "uploadFeaturesAndAttachments": "upload_features_and_attachments",
            "upload_features_and_attachments": "uploadFeaturesAndAttachments",
        }
        values = {
            "download": None,
            "sync": None,
            "reference_basemap": None,
            "get_attachments": None,
        }
        if (
            "application_properties" in self._map._webmap
            and "offline" in self._map._webmap.application_properties
        ):
            offline_dict = self._map._webmap.application_properties.offline.dict()
            if "editableLayers" in offline_dict:
                if "download" in offline_dict["editableLayers"]:
                    values["download"] = dl_lu[
                        offline_dict["editableLayers"]["download"]
                    ]
                else:
                    values.pop("download")
                if "sync" in offline_dict["editableLayers"]:
                    values["sync"] = dl_lu[offline_dict["editableLayers"]["sync"]]
                else:
                    values.pop("sync")
            else:
                values.pop("download")
                values.pop("sync")

            if (
                "offlinebasemap" in offline_dict
                and "referenceBasemapName" in offline_dict["offlinebasemap"]
            ):
                values["reference_basemap"] = offline_dict["offlinebasemap"][
                    "referenceBasemapName"
                ]
            else:
                values.pop("reference_basemap")
            if (
                "readonlyLayers" in offline_dict
                and "downloadAttachments" in offline_dict["readonlyLayers"]
            ):
                values["get_attachments"] = offline_dict["readonlyLayers"][
                    "downloadAttachments"
                ]
            else:
                values.pop("get_attachments")
            return values
        else:
            self._map._webmap.application_properties = {"offline": {}}
            return {}

    # ----------------------------------------------------------------------
    @offline_properties.setter
    def offline_properties(self, values: dict[str, Any]):
        """
        See main ``offline_properties`` property docstring.
        """
        dl_lu = {
            "features": "features",
            "featuresAndAttachments": "features_and_attachments",
            "features_and_attachments": "featuresAndAttachments",
            "none": None,
            "None": "none",
            None: "none",
            "syncFeaturesAndAttachments": "sync_features_and_attachments",
            "sync_features_and_attachments": "syncFeaturesAndAttachments",
            "syncFeaturesUploadAttachments": "sync_features_upload_attachments",
            "sync_features_upload_attachments": "syncFeaturesUploadAttachments",
            "uploadFeaturesAndAttachments": "upload_features_and_attachments",
            "upload_features_and_attachments": "uploadFeaturesAndAttachments",
        }
        keys = {
            "download": "download",
            "sync": "sync",
            "reference_basemap": "referenceBasemapName",
            "get_attachments": "downloadAttachments",
        }
        remove = set()
        if "applicationProperties" in self._map._webmap:
            v = self._map._webmap.application_properties.dict()
        else:
            v = self._map._webmap.application_properties = {}
        if "offline" not in v:
            v["offline"] = {
                "editableLayers": {
                    "download": (
                        dl_lu[values["download"]]
                        if "download" in values
                        else remove.add("download")
                    ),
                    "sync": (
                        dl_lu[values["sync"]]
                        if "sync" in values
                        else remove.add("sync")
                    ),
                },
                "offlinebasemap": {
                    "referenceBasemapName": (
                        dl_lu[values["reference_basemap"]]
                        if "reference_basemap" in values
                        else remove.add("reference_basemap")
                    )
                },
                "readonlyLayers": {
                    "downloadAttachments": (
                        values["get_attachments"]
                        if "get_attachments" in values
                        else remove.add("get_attachments")
                    )
                },
            }
        else:
            v["offline"] = {
                "editableLayers": {
                    "download": (
                        dl_lu[values["download"]]
                        if "download" in values
                        else remove.add("download")
                    ),
                    "sync": (
                        dl_lu[values["sync"]]
                        if "sync" in values
                        else remove.add("sync")
                    ),
                },
                "offlinebasemap": {
                    "referenceBasemapName": (
                        dl_lu[values["reference_basemap"]]
                        if "reference_basemap" in values
                        else remove.add("reference_basemap")
                    )
                },
                "readonlyLayers": {
                    "downloadAttachments": (
                        values["get_attachments"]
                        if "get_attachments" in values
                        else remove.add("get_attachments")
                    )
                },
            }
        if "sync" in remove and "download" in remove:
            del v["offline"]["editableLayers"]
        if "sync" in remove:
            del v["offline"]["editableLayers"]["sync"]
        if "download" in remove:
            del v["offline"]["editableLayers"]["download"]
        if "reference_basemap" in remove:
            del v["offline"]["offlinebasemap"]
        if "get_attachments" in remove:
            del v["offline"]["readonlyLayers"]
        del remove
        update_items = {
            "clearEmptyFields": True,
            "text": json.dumps(self._map._webmap.dict()),
        }
        if self._item.update(item_properties=update_items):
            self._item._hydrated = False
            self._item._hydrate()
            arcgismapping = _imports.get_arcgis_map_mod(True)
            self._map = arcgismapping.Map(self._item)
        else:
            raise Exception("Could not update the offline properties.")

    # ----------------------------------------------------------------------
    def _run_async(self, fn, **inputs):
        """runs the inputs asynchronously"""
        import concurrent.futures

        tp = concurrent.futures.ThreadPoolExecutor(1)
        try:
            future = tp.submit(fn=fn, **inputs)
        except:
            future = tp.submit(fn, **inputs)
        tp.shutdown(False)
        return future

    # ----------------------------------------------------------------------
    def create(
        self,
        area: Union[str, list, dict[str, Any]],
        item_properties: Optional[dict[str, Any]] = None,
        folder: Optional[str] = None,
        min_scale: Optional[int] = None,
        max_scale: Optional[int] = None,
        layers_to_ignore: Optional[list[str]] = None,
        refresh_schedule: str = "Never",
        refresh_rates: Optional[dict[str, int]] = None,
        enable_updates: bool = False,
        ignore_layers: Optional[list[str]] = None,
        tile_services: Optional[list[dict[str, str]]] = None,
        future: bool = False,
    ):
        """
        This method creates offline map area items and packages for ArcGIS
        Runtime powered applications to use. The method creates two different
        types of :class:`Items <arcgis.gis.Item>`

        * ``Map Area`` items for the specified extent, bookmark, or polygon
        * ``Map Area Packages`` corresponding to the operational layer(s) and
          basemap layer(s) within the extent, bookmark or polygon area

        .. note::
            Packaging will fail if the size of the offline map area, when
            packaged, is **larger than 2.5 GB**.

            * If packaging fails, try using a smaller bookmark, extent or
              geometry for the *area* argument.
            * If the map contains feature layers that have attachments, you can
              exclude attachments from the offline package to decrease the
              package size.
            * If the map includes tile layers, use the *tile_services* argument
              to constrain the number of levels included in the resulting
              packages. This is typically *required* to reduce the tile package
              size for the basemap layer(s) in ArcGIS Enterprise.

        .. note::
            Only the owner of the Web Map item can create offline map areas.

        ==================     ====================================================================
        **Parameter**          **Description**
        ------------------     --------------------------------------------------------------------
        area                   Required *bookmark*, *extent*, or :class:`~arcgis.geometry.Polygon`
                               object. Specify as either:

                               + bookmark name

                                 .. code-block:: python

                                    >>> wm_item = gis.content.get("<web map id>")
                                    >>> wm_obj = Map(wm_item)

                                    >>> wm_bookmarks = wm_obj.bookmarks
                                    >>> area = wm_bookmarks[0]

                               + extent: as a list of coordinate pairs:

                                 .. code-block:: python

                                    >>> area = [['xmin', 'ymin'], ['xmax', 'ymax']]

                               + extent: as a dictionary:

                                 .. code-block:: python

                                    >>> area = {
                                                'xmin': <value>,
                                                'ymin': <value>,
                                                'xmax': <value>,
                                                'ymax': <value>,
                                                'spatialReference' : {'wkid' : <value>}
                                               }

                               + polygon: as a :class:`~arcgis.gis.Polygon` object


                               .. note::
                                    If spatial reference is not specified,
                                    it is assumed {'wkid': 4326}.

        ------------------     --------------------------------------------------------------------
        item_properties        Required dictionary. See table below for the keys and values.
        ------------------     --------------------------------------------------------------------
        folder                 Optional string. Specify a folder name if you want the offline map
                               area item and the packages to be created inside a folder.

                               .. note::
                                   These items will not display when viewing the content folder in
                                   a web browser. They will display in the *Portal* tab of the
                                   Content Pane in ArcGIS Pro.
        ------------------     --------------------------------------------------------------------
        min_scale              Optional integer. Specify the minimum scale to cache tile and vector
                               tile layers. When zoomed out beyond this scale, cached layers would
                               not display.

                               .. note::
                                   The ``min_scale`` value is always larger than the ``max_scale``.
        ------------------     --------------------------------------------------------------------
        max_scale              Optional integer. Specify the maximum scale to cache tile and vector
                               tile layers. When zoomed in beyond this scale, cached layers would
                               not display.
        ------------------     --------------------------------------------------------------------
        layers_to_ignore       Optional List of layer objects to exclude when creating offline
                               packages. You can get the list of layers in a web map by calling
                               the `layers` property on the `Map` object.
        ------------------     --------------------------------------------------------------------
        refresh_schedule       Optional string. Allows for the scheduling of refreshes at given
                               times.

                               The following are valid variables:

                               + ``Never`` - never refreshes the offline package (default)
                               + ``Daily`` - refreshes everyday
                               + ``Weekly`` - refreshes once a week
                               + ``Monthly`` - refreshes once a month

        ------------------     --------------------------------------------------------------------
        refresh_rates          Optional dict. This parameter allows for the customization of the
                               scheduler.  The dictionary accepts the following:

                               .. code-block:: python

                                   {
                                    "hour" : 1
                                    "minute" = 0
                                    "nthday" = 3
                                    "day_of_week" = 0
                                   }

                               - hour - a value between 0-23 (integers)
                               - minute - a value between 0-60 (integers)
                               - nthday - this is used for monthly only. Thw refresh will occur
                                 on the 'n' day of the month.
                               - day_of_week - a value between 0-6 where 0 is Sunday and 6 is
                                 Saturday.

                               .. code-block:: python

                                   # Example **Daily**: every day at 10:30 AM UTC

                                    >>> refresh_rates = {
                                                         "hour": 10,
                                                         "minute" : 30
                                                        }

                                   # Example **Weekly**: every Wednesday at 11:59 PM UTC

                                    >>> refresh_rates = {
                                                         "hour" : 23,
                                                         "minute" : 59,
                                                         "day_of_week" : 4
                                                        }
        ------------------     --------------------------------------------------------------------
        enable_updates         Optional Boolean.  Allows for the updating of the layers.
        ------------------     --------------------------------------------------------------------
        ignore_layers          Optional List.  A list of individual layers, specified with their
                               service URLs, in the map to ignore. The task generates packages for
                               all map layers by default.

                               .. code-block:: python

                                   >>> ignore_layers = [
                                                        "https://services.arcgis.com/ERmEceOGq5cHrItq/arcgis/rest/services/SaveTheBaySync/FeatureServer/1",
                                                        "https://services.arcgis.com/ERmEceOGq5cHrItq/arcgis/rest/services/WildfireSync/FeatureServer/0"
                                                       ]

        ------------------     --------------------------------------------------------------------
        tile_services          Optional List. An list of Python dictionary objects that contains
                               information about the *export tiles-enabled* services for which
                               tile packages (.tpk or .vtpk) need to be created. Each tile service
                               is specified with its *url* and desired level of details.

                               .. code-block:: python

                                   >>> tile_services = [
                                                        {
                                                         "url": "https://tiledbasemaps.arcgis.com/arcgis/rest/services/World_Imagery/MapServer",
                                                         "levels": "17,18,19"
                                                        }

                               .. note::
                                   This argument **should** be specified when using ArcGIS
                                   Enterprise items. The number of levels included greatly
                                   impacts the overall size of the resulting packages to
                                   keep them under the 2.5 GB limit.
        ------------------     --------------------------------------------------------------------
        future                 Optional boolean. If *True*, a future object will be returned and the
                               process will return control to the user before the task completes.
                               If *False*, control returns once the operation completes. The default
                               is *False*.
        ==================     ====================================================================

        Key:Value Dictionary options for argument ``item_properties``

        =================  =====================================================================
        **Key**            **Value**
        -----------------  ---------------------------------------------------------------------
        description        Optional string. Description of the item.
        -----------------  ---------------------------------------------------------------------
        title              Optional string. Name label of the item.
        -----------------  ---------------------------------------------------------------------
        tags               Optional string of comma-separated values, or a list of
                           strings for each tag.
        -----------------  ---------------------------------------------------------------------
        snippet            Optional string. Provide a short summary (limit to max 250
                           characters) of the what the item is.
        =================  =====================================================================

        :return:
            Map Area :class:`~arcgis.gis.Item`, or if *future=True*, a
            :class:`~arcgis.layers.PackagingJob` object to further query for
            results.

        .. code-block:: python

            # USAGE EXAMPLE #1: Creating offline map areas using *scale* argument

            >>> from arcgis.gis import GIS
            >>> from arcgis.map import Map

            >>> gis = GIS(profile="your_online_organization_profile")

            >>> wm_item = gis.content.get("<web_map_id>")
            >>> wm_obj = Map(wm_item)

            >>> item_prop = {"title": "Clear lake hyperspectral field campaign",
                             "snippet": "Offline package for field data collection using spectro-radiometer",
                             "tags": ["python api", "in-situ data", "field data collection"]}

            >>> aviris_layer = wm_item.content.layers[-1]

            >>> north_bed = wm_obj.bookmarks.list()[-1].name
            >>> wm.offline_areas.create(area=north_bed,
                                        item_properties=item_prop,
                                        folder="clear_lake",
                                        min_scale=9000,
                                        max_scale=4500,
                                        layers_to_ignore=[aviris_layer])

            # USAGE Example #2: ArcGIS Enterprise web map specifying *tile_services*

            >>> gis = GIS(profile="your_enterprise_profile")

            >>> wm_item = gis.content.get("<item_id>")
            >>> wm_obj = Map(wm_item)

            # Enterprise: Get the url for tile services from basemap
            >>> basemap_lyrs = wm_obj.basemap.basemap["baseMapLayers"]
            >>> basemap_lyrs

                [
                 {'id': '18d9e5e151c-layer-2',
                  'title': 'Light_Gray_Export_AGOL_Group',
                  'itemId': '042f5e5aadcb8dbd910ae310b1f26d18',
                  'layerType': 'VectorTileLayer',
                  'styleUrl': 'https:/example.com/portal/sharing/servers/042f5e5aadcb8dbd910ae310b1f26d1/rest/services/World_Basemap_Export_v2/VectorTileServer/resources/styles/root.json'}
                ]

            # Get the specific Tile Layer item to see options for levels
            >>> vtl_item = gis.content.get(basemap_lyrs[0]["itemId"])
            >>> vtl_lyr = vtl_item.layers[0]
            >>> print(f"min levels: {vtl_lyr.properties['minLOD']}")
            >>> print(f"max levels: {vtl_lyr.properties['maxLOD']}")

                min levels: 0
                max levels: 16

            >>> vtl_svc_url = vtl_item.layers[0].url
            >>> vtl_svc_url
            https:/example.com/portal/sharing/servers/042f5e5aadcb8dbd910ae310b1f26d1/rest/services/World_Basemap_Export_v2/VectorTileServer

            # Get a list of bookmark names to iterate through
            >>> bookmarks = wm_obj.bookmarks.list()
            >>> bkmrk_names = [bookmark.name for bookmark in bookmarks]
            >>> bname = bkmrk_names[1]

            >>> oma = offline_mgr.create(area=bname,
                                         item_properties={"title": bname + "_OMA",
                                                          "tags": "offline_mapping,administrative boundaries,parks",
                                                          "snippet": bname + " in County",
                                                          "description": "Offline mapping area in " + bname + " for sync"},
                                         tile_services=[{"url": vtl_svc_url,
                                                         "levels": "6,7,8,9,10,11,12,13"}])
            >>> oma
            <Item title:"County_OMA" type:Map Area owner:gis_user>

            >>> # List packages created:
            >>> for oma_pkg in oma.related_items("Area2Package", "forward"):
            >>>     print(f"{oma_pkg.title:60}{oma_pkg.type}")

            <County_Layer-<id_string>                SQLite Geodatabase
            <VectorTileServe-<id_string>             Vector Tile Package

        .. note::
            This method executes silently. To view informative status messages, set the verbosity environment variable
            as shown below prior to running the method:

            .. code-block:: python

                # USAGE EXAMPLE: setting verbosity

                >>> from arcgis import env
                >>> env.verbose = True
        """
        if future:
            inputs = {
                "area": area,
                "item_properties": item_properties,
                "folder": folder,
                "min_scale": min_scale,
                "max_scale": max_scale,
                "layers_to_ignore": layers_to_ignore,
                "refresh_schedule": refresh_schedule,
                "refresh_rates": refresh_rates,
                "enable_updates": enable_updates,
                "ignore_layers": ignore_layers,
                "tile_services": tile_services,
            }
            future = self._run_async(self._create, **inputs)
            return PackagingJob(future=future)
        else:
            return self._create(
                area=area,
                item_properties=item_properties,
                folder=folder,
                min_scale=min_scale,
                max_scale=max_scale,
                layers_to_ignore=layers_to_ignore,
                refresh_schedule=refresh_schedule,
                refresh_rates=refresh_rates,
                enable_updates=enable_updates,
                ignore_layers=ignore_layers,
                tile_services=tile_services,
            )

    # ----------------------------------------------------------------------
    def _create(
        self,
        area,
        item_properties=None,
        folder=None,
        min_scale=None,
        max_scale=None,
        layers_to_ignore=None,
        refresh_schedule="Never",
        refresh_rates=None,
        enable_updates=False,
        ignore_layers=None,
        tile_services=None,
        future=False,
    ):
        """
        See create method for docstring.
        """
        _dow_lu = {
            0: "SUN",
            1: "MON",
            2: "TUE",
            3: "WED",
            4: "THU",
            5: "FRI",
            6: "SAT",
            7: "SUN",
        }
        # region find if bookmarks or extent is specified
        _bookmark = None
        _extent = None
        if item_properties is None:
            item_properties = {}
        if isinstance(area, str):  # bookmark specified
            _bookmark = area
            area_type = "BOOKMARK"
        elif isinstance(area, (list, tuple)):  # extent specified as list
            _extent = {
                "xmin": area[0][0],
                "ymin": area[0][1],
                "xmax": area[1][0],
                "ymax": area[1][1],
                "spatialReference": {"wkid": 4326},
            }

        elif isinstance(area, dict) and "xmin" in area:  # geocoded extent provided
            _extent = area
            if "spatialReference" not in _extent:
                _extent["spatialReference"] = {"wkid": 4326}
        # endregion

        # region build input parameters - for CreateMapArea tool
        if folder:
            user_folders = list(self._gis.users.me.folders)
            if user_folders:
                matching_folder_ids = [
                    f["id"] for f in user_folders if f["title"] == folder
                ]
                if matching_folder_ids:
                    folder_id = matching_folder_ids[0]
                else:  # said folder not found in user account
                    folder_id = None
            else:  # ignore the folder, output will be created in same folder as web map
                folder_id = None
        else:
            folder_id = None

        if "tags" in item_properties:
            if type(item_properties["tags"]) is list:
                tags = ",".join(item_properties["tags"])
            else:
                tags = item_properties["tags"]
        else:
            tags = None

        if refresh_schedule.lower() in ["daily", "weekly", "monthly"]:
            refresh_schedule = refresh_schedule.lower()
            if refresh_schedule == "daily":
                if refresh_rates and isinstance(refresh_rates, dict):
                    hour = 1
                    minute = 0
                    if "hour" in refresh_rates:
                        hour = refresh_rates["hour"]
                    if "minute" in refresh_rates:
                        minute = refresh_rates["minute"]
                    map_area_refresh_params = {
                        "startDate": int(
                            datetime.datetime.now(tz=timezone.utc).timestamp()
                        )
                        * 1000,
                        "type": "daily",
                        "nthDay": 1,
                        "dayOfWeek": 0,
                    }
                    refresh_schedule = "0 {m} {hour} * * ?".format(m=minute, hour=hour)
                else:
                    map_area_refresh_params = {
                        "startDate": int(
                            datetime.datetime.now(tz=timezone.utc).timestamp()
                        )
                        * 1000,
                        "type": "daily",
                        "nthDay": 1,
                        "dayOfWeek": 0,
                    }
                    refresh_schedule = "0 0 1 * * ?"
            elif refresh_schedule == "weekly":
                if refresh_rates and isinstance(refresh_rates, dict):
                    hour = 1
                    minute = 0
                    dayOfWeek = "MON"
                    if "hour" in refresh_rates:
                        hour = refresh_rates["hour"]
                    if "minute" in refresh_rates:
                        minute = refresh_rates["minute"]
                    if "day_of_week" in refresh_rates:
                        dayOfWeek = refresh_rates["day_of_week"]
                    map_area_refresh_params = {
                        "startDate": int(
                            datetime.datetime.now(tz=timezone.utc).timestamp()
                        )
                        * 1000,
                        "type": "weekly",
                        "nthDay": 1,
                        "dayOfWeek": dayOfWeek,
                    }
                    refresh_schedule = "0 {m} {hour} ? * {dow}".format(
                        m=minute, hour=hour, dow=_dow_lu[dayOfWeek]
                    )
                else:
                    map_area_refresh_params = {
                        "startDate": int(
                            datetime.datetime.now(tz=timezone.utc).timestamp()
                        )
                        * 1000,
                        "type": "weekly",
                        "nthDay": 1,
                        "dayOfWeek": 1,
                    }
                    refresh_schedule = "0 0 1 ? * MON"
            elif refresh_schedule == "monthly":
                if refresh_rates and isinstance(refresh_rates, dict):
                    hour = 1
                    minute = 0
                    nthday = 3
                    dayOfWeek = 0
                    if "hour" in refresh_rates:
                        hour = refresh_rates["hour"]
                    if "minute" in refresh_rates:
                        minute = refresh_rates["minute"]
                    if "nthday" in refresh_rates["nthday"]:
                        nthday = refresh_rates["nthday"]
                    if "day_of_week" in refresh_rates:
                        dayOfWeek = refresh_rates["day_of_week"]
                    map_area_refresh_params = {
                        "startDate": int(
                            datetime.datetime.now(tz=timezone.utc).timestamp()
                        )
                        * 1000,
                        "type": "monthly",
                        "nthDay": nthday,
                        "dayOfWeek": dayOfWeek,
                    }
                    refresh_schedule = "0 {m} {hour} ? * {nthday}#{dow}".format(
                        m=minute, hour=hour, nthday=nthday, dow=dayOfWeek
                    )
                else:
                    map_area_refresh_params = {
                        "startDate": int(
                            datetime.datetime.now(tz=timezone.utc).timestamp()
                        )
                        * 1000,
                        "type": "monthly",
                        "nthDay": 3,
                        "dayOfWeek": 3,
                    }
                    refresh_schedule = "0 0 14 ? * 4#3"
        else:
            refresh_schedule = None
            refresh_rates_cron = None
            map_area_refresh_params = {"type": "never"}

        output_name = {
            "title": item_properties["title"] if "title" in item_properties else None,
            "snippet": (
                item_properties["snippet"] if "snippet" in item_properties else None
            ),
            "description": (
                item_properties["description"]
                if "description" in item_properties
                else None
            ),
            "tags": tags,
            "folderId": folder_id,
            "packageRefreshSchedule": refresh_schedule,
        }

        # endregion

        # region call CreateMapArea tool
        # from arcgis.geoprocessing._tool import Toolbox
        # pkg_tb = Toolbox(url=self._url, gis=self._gis)
        pkg_tb = self._gis._tools.packaging
        if self._gis.version >= [7, 2]:
            if _extent:
                area = _extent
                area_type = "ENVELOPE"
            elif _bookmark:
                area = {"name": _bookmark}
                area_type = "BOOKMARK"

            if isinstance(area, str):
                area_type = "BOOKMARK"
            elif isinstance(area, _geometry.Polygon) or (
                isinstance(area, dict) and "rings" in area
            ):
                area_type = "POLYGON"
            elif isinstance(area, arcgis.geometry.Envelope) or (
                isinstance(area, dict) and "xmin" in area
            ):
                area_type = "ENVELOPE"
            elif isinstance(area, (list, tuple)):
                area_type = "ENVELOPE"
            if refresh_schedule is None:
                output_name.pop("packageRefreshSchedule")
            if folder_id is None:
                output_name.pop("folderId")
            oma_result = pkg_tb.create_map_area(
                map_item_id=self._item.id,
                area_type=area_type,
                area=area,
                output_name=output_name,
            )

        else:
            oma_result = pkg_tb.create_map_area(
                self._item.id, _bookmark, _extent, output_name=output_name
            )
        # endregion

        # Call update on Item with Refresh Information
        # import datetime
        item = _gis.Item(gis=self._gis, itemid=oma_result)
        update_items = {
            "snippet": "Map with no advanced offline settings set (default is assumed to be features and attachments)",
            "title": item_properties["title"] if "title" in item_properties else None,
            "typeKeywords": "Map, Map Area",
            "clearEmptyFields": True,
            "text": json.dumps(
                {
                    "mapAreas": {
                        "mapAreaTileScale": {
                            "minScale": min_scale,
                            "maxScale": max_scale,
                        },
                        "mapAreaRefreshParams": map_area_refresh_params,
                        "mapAreasScheduledUpdatesEnabled": enable_updates,
                    }
                }
            ),
        }
        item.update(item_properties=update_items)
        if _extent is None and area_type == "BOOKMARK":
            for bm in self._map._webmap_dict["bookmarks"]:
                if isinstance(area, dict):
                    if bm["name"].lower() == area["name"].lower():
                        _extent = bm["extent"]
                        break
                else:
                    if bm["name"].lower() == area.lower():
                        _extent = bm["extent"]
                        break
        update_items = {
            "properties": {
                "status": "processing",
                "packageRefreshSchedule": refresh_schedule,
            }
        }
        update_items["properties"].update(item.properties)
        if _extent and not "extent" in item.properties:
            update_items["properties"]["extent"] = _extent
        if area and not "area" in item.properties:
            update_items["properties"]["area"] = _extent
        item.update(item_properties=update_items)
        # End Item Update Refresh Call

        # region build input parameters - for setupMapArea tool
        # map layers to ignore parameter
        map_layers_to_ignore = []
        if isinstance(layers_to_ignore, list):
            for layer in layers_to_ignore:
                if isinstance(layer, _mixins.PropertyMap):
                    if hasattr(layer, "url"):
                        map_layers_to_ignore.append(layer.url)
                elif isinstance(layer, str):
                    map_layers_to_ignore.append(layer)
        elif isinstance(layers_to_ignore, _mixins.PropertyMap):
            if hasattr(layers_to_ignore, "url"):
                map_layers_to_ignore.append(layers_to_ignore.url)
        elif isinstance(layers_to_ignore, str):
            map_layers_to_ignore.append(layers_to_ignore)

        # LOD parameter
        lods = []
        if min_scale or max_scale:
            # find tile and vector tile layers in map
            cached_layers = [
                l
                for l in self._map.content.layers
                if l.layerType in ["VectorTileLayer", "ArcGISTiledMapServiceLayer"]
            ]

            # find tile and vector tile layers in basemap set of layers
            if hasattr(self._map.basemap, "basemap"):
                if "baseMapLayers" in self._map.basemap.basemap:
                    cached_layers_bm = [
                        l
                        for l in self._map.basemap.basemap["baseMapLayers"]
                        if l["layerType"]
                        in ["VectorTileLayer", "ArcGISTiledMapServiceLayer"]
                    ]

                    # combine both the layer lists together
                    cached_layers.extend(cached_layers_bm)

            for cached_layer in cached_layers:
                if cached_layer["layerType"] == "VectorTileLayer":
                    if "url" in cached_layer:
                        layer0_obj = VectorTileLayer(cached_layer["url"], self._gis)
                    elif "itemId" in cached_layer:
                        layer0_obj = VectorTileLayer.fromitem(
                            self._gis.content.get(cached_layer["itemId"])
                        )
                    elif "styleUrl" in cached_layer and cached_layer["title"] in [
                        "OpenStreetMap"
                    ]:
                        res = findall(
                            r"[0-9a-f]{8}(?:[0-9a-f]{4}){3}[0-9a-f]{12}",
                            cached_layer["styleUrl"],
                        )
                        if res:
                            layer0_obj = VectorTileLayer.fromitem(
                                self._gis.content.get(res[0])
                            )
                else:
                    layer0_obj = MapImageLayer(cached_layer["url"], self._gis)

                # region snap logic
                # Objective is to find the LoD that is close to the min scale specified. When scale falls between two
                # levels in the tiling scheme, we will pick the larger limit for min_scale and smaller limit for
                # max_scale.

                # Start by sorting the tileInfo dictionary. Then use Python's bisect_left to find the conservative tile
                # LOD that is closest to min scale. Do similar for max_scale.

                sorted_lods = sorted(
                    layer0_obj.properties.tileInfo.lods,
                    key=lambda x: x["scale"],
                )
                keys = [l["scale"] for l in sorted_lods]

                from bisect import bisect_left

                min_lod_info = sorted_lods[bisect_left(keys, min_scale)]
                max_lod_info = sorted_lods[
                    (
                        bisect_left(keys, max_scale) - 1
                        if bisect_left(keys, max_scale) > 0
                        else 0
                    )
                ]

                lod_span = [
                    str(i)
                    for i in range(min_lod_info["level"], max_lod_info["level"] + 1)
                ]
                lod_span_str = ",".join(lod_span)
                # endregion

                lods.append({"url": layer0_obj.url, "levels": lod_span_str})
            # endregion
        feature_services = None
        if enable_updates:
            if feature_services is None:
                feature_services = {}
                for l in self._map.content.layers:
                    if os.path.dirname(l["url"]) not in feature_services:
                        feature_services[os.path.dirname(l["url"])] = {
                            "url": os.path.dirname(l["url"]),
                            "layers": [int(os.path.basename(l["url"]))],
                            # "returnAttachments": False,
                            # "attachmentsSyncDirection": "upload",
                            # "syncModel": "perLayer",
                            "createPkgDeltas": {"maxDeltaAge": 5},
                        }
                    else:
                        feature_services[os.path.dirname(l["url"])]["layers"].append(
                            int(os.path.basename(l["url"]))
                        )
                feature_services = list(feature_services.values())
        # region call the SetupMapArea tool
        # pkg_tb.setup_map_area(map_area_item_id, map_layers_to_ignore=None, tile_services=None, feature_services=None, gis=None, future=False)
        ts = tile_services if tile_services else lods
        setup_oma_result = pkg_tb.setup_map_area(
            map_area_item_id=oma_result,
            map_layers_to_ignore=map_layers_to_ignore,
            tile_services=ts,
            feature_services=feature_services,
            gis=self._gis,
            future=True,
        )
        if future:
            return setup_oma_result
        # setup_oma_result.result()
        _log.info(str(setup_oma_result.result()))
        # endregion
        return _gis.Item(gis=self._gis, itemid=oma_result)

    # ----------------------------------------------------------------------
    def modify_refresh_schedule(
        self,
        item: _gis.Item,
        refresh_schedule: Optional[str] = None,
        refresh_rates: Optional[dict[str, int]] = None,
    ):
        """
        The ``modify_refresh_schedule`` method modifies an existing offline package's refresh schedule.

        ============================     ====================================================================
        **Parameter**                     **Description**
        ----------------------------     --------------------------------------------------------------------
        item                             Required :class:`~arcgis.gis.Item` object.
                                         This is the Offline Package to update the refresh schedule.
        ----------------------------     --------------------------------------------------------------------
        refresh_schedule                 Optional String.  This is the rate of refreshing.

                                         The following are valid variables:

                                         + Never - never refreshes the offline package (default)
                                         + Daily - refreshes everyday
                                         + Weekly - refreshes once a week
                                         + Monthly - refreshes once a month
        ----------------------------     --------------------------------------------------------------------
        refresh_rates                    Optional dict. This parameter allows for the customization of the
                                         scheduler. Note all time is in UTC.

                                         The dictionary accepts the following:

                                             {
                                             "hour" : 1
                                             "minute" = 0
                                             "nthday" = 3
                                             "day_of_week" = 0
                                             }

                                         - hour - a value between 0-23 (integers)
                                         - minute a value between 0-60 (integers)
                                         - nthday - this is used for monthly only. This say the refresh will occur on the 'x' day of the month.
                                         - day_of_week - a value between 0-6 where 0 is Sunday and 6 is Saturday.

                                         Example **Daily**:

                                             {
                                             "hour": 10,
                                             "minute" : 30
                                             }

                                         This means every day at 10:30 AM UTC

                                         Example **Weekly**:

                                             {
                                             "hour" : 23,
                                             "minute" : 59,
                                             "day_of_week" : 4
                                             }

                                         This means every Wednesday at 11:59 PM UTC

        ============================     ====================================================================

        :return:
            A boolean indicating success (True), or failure (False)


        .. code-block:: python

            ## Updates Offline Package Building Everyday at 10:30 AM UTC

            gis = GIS(profile='owner_profile')
            item = gis.content.get('9b93887c640a4c278765982aa2ec999c')
            oa = wm.offline_areas.modify_refresh_schedule(item.id, 'daily', {'hour' : 10, 'minute' : 30})


        """
        if isinstance(item, str):
            item = self._gis.content.get(item)
        _dow_lu = {
            0: "SUN",
            1: "MON",
            2: "TUE",
            3: "WED",
            4: "THU",
            5: "FRI",
            6: "SAT",
            7: "SUN",
        }
        hour = 1
        minute = 0
        nthday = 3
        dayOfWeek = 0
        if refresh_rates is None:
            refresh_rates = {}
        if refresh_schedule is None or str(refresh_schedule).lower() == "never":
            refresh_schedule = None
            map_area_refresh_params = {"type": "never"}
        elif refresh_schedule.lower() == "daily":
            if "hour" in refresh_rates:
                hour = refresh_rates["hour"]
            if "minute" in refresh_rates:
                minute = refresh_rates["minute"]
            map_area_refresh_params = {
                "startDate": int(datetime.datetime.now(tz=timezone.utc).timestamp())
                * 1000,
                "type": "daily",
                "nthDay": 1,
                "dayOfWeek": 0,
            }
            refresh_schedule = "0 {m} {hour} * * ?".format(m=minute, hour=hour)
        elif refresh_schedule.lower() == "weekly":
            if "hour" in refresh_rates:
                hour = refresh_rates["hour"]
            if "minute" in refresh_rates:
                minute = refresh_rates["minute"]
            if "day_of_week" in refresh_rates:
                dayOfWeek = refresh_rates["day_of_week"]
            map_area_refresh_params = {
                "startDate": int(datetime.datetime.now(tz=timezone.utc).timestamp())
                * 1000,
                "type": "weekly",
                "nthDay": 1,
                "dayOfWeek": dayOfWeek,
            }
            refresh_schedule = "0 {m} {hour} ? * {dow}".format(
                m=minute, hour=hour, dow=_dow_lu[dayOfWeek]
            )
        elif refresh_schedule.lower() == "monthly":
            if "hour" in refresh_rates:
                hour = refresh_rates["hour"]
            if "minute" in refresh_rates:
                minute = refresh_rates["minute"]
            if "nthday" in refresh_rates["nthday"]:
                nthday = refresh_rates["nthday"]
            if "day_of_week" in refresh_rates:
                dayOfWeek = refresh_rates["day_of_week"]
            map_area_refresh_params = {
                "startDate": int(datetime.datetime.now(tz=timezone.utc).timestamp())
                * 1000,
                "type": "monthly",
                "nthDay": nthday,
                "dayOfWeek": dayOfWeek,
            }
            refresh_schedule = "0 {m} {hour} ? * {nthday}#{dow}".format(
                m=minute, hour=hour, nthday=nthday, dow=dayOfWeek
            )
        else:
            raise ValueError(
                (
                    "Invalid refresh_schedule, value"
                    " can only be Never, Daily, Weekly or Monthly."
                )
            )
        text = item.get_data()
        text["mapAreas"]["mapAreaRefreshParams"] = map_area_refresh_params
        update_items = {"clearEmptyFields": True, "text": json.dumps(text)}
        item.update(item_properties=update_items)
        _extent = item.properties["extent"]
        update_items = {
            "properties": {
                "extent": _extent,
                "status": "complete",
                "packageRefreshSchedule": refresh_schedule,
            }
        }
        item.update(item_properties=update_items)
        try:
            self._pm.create_map_area(map_item_id=item.id, future=False)
            return True
        except:
            return False

    # ----------------------------------------------------------------------
    def list(self):
        """
        Retrieves a list of all *Map Area* items for the
        :class:`~arcgis.map.Map` object.

        .. note::
            *Map Area* items and the corresponding offline packages share a relationship
            of type *Area2Package*. You can use this relationship to get the list of
            package items cached for each *map area* item. Refer to the Python snippet
            below for the steps:

        .. code-block:: python

            # USAGE EXAMPLE: Listing Map Area Items

            >>> from arcgis.gis import GIS
            >>> from arcgis.map import Map

            >>> wm_item = gis.content.search("*", "Web Map")[0]
            >>> wm_obj = Map(wm_item)

            >>> all_map_areas = wm.offline_areas.list()
            >>> all_map_areas

            [<Item title:"Ballerup_OMA", type:Map Area owner:gis_user1>,
             <Item title:"Viborg_OMA", type:Map Area owner:gis_user1>]

            # USAGE Example: Inspecting Map Area packages

            >>> area1 = all_map_areas[0]
            >>> area1_packages = area1.related_items("Area2Package","forward")

            >>> for pkg in area1_packages:
            >>>     print(f"{pkg.title}")
            <<<     print(f"{' ' * 2}{pkg.type}")
            >>>     print(f"{' ' * 2}{pkg.homepage}")

            VectorTileServe-<value_string>
              Vector Tile Package
              https://<organziation_url>/home/item.html?id=<item_id>


            DK_lau_data-<value_string>
              SQLite Geodatabase
              https://organization_url/home/item.html?id=<item_id>

        :return:
            A List of *Map Area* :class`items <arcgis.gis.Item>` related to the
            *Web Map* item.
        """
        return self._item.related_items("Map2Area", "forward")

    # ----------------------------------------------------------------------
    def update(
        self,
        offline_map_area_items: Optional[list] = None,
        future: bool = False,
    ):
        """
        The ``update`` method refreshes existing map area packages associated
        with each of the ``Map Area`` items specified. This process updates the
        packages with changes made on the source data since the last time those
        packages were created or refreshed. See `Refresh Map Area Package
        <https://developers.arcgis.com/rest/packaging/api-reference/refresh-map-area-package.htm>`_
        for more information.

        ============================     ====================================================================
        **Parameter**                     **Description**
        ----------------------------     --------------------------------------------------------------------
        offline_map_area_items           Optional list. Specify one or more Map Area
                                         :class:`items <arcgis.gis.Item>` for which the packages need to be
                                         refreshed. If not specified, this method updates all the packages
                                         associated with all the map area items of the web map.

                                         .. note::
                                             To get the list of ``Map Area`` items related to the *Map*
                                             object, call the
                                             :meth:`~arcgis.layers.OfflineMapAreaManager.list` method on
                                             the :class:`~arcgis.layers.OfflineMapAreaManager` for the
                                             *Map*.
        ----------------------------     --------------------------------------------------------------------
        future                           Optional Boolean.
        ============================     ====================================================================

        :return:
            Dictionary containing update status.

        .. note::
            This method executes silently. To view informative status messages,
            set the verbosity environment variable as shown below before running
            the code:

            .. code-block:: python

               USAGE EXAMPLE: setting verbosity

               from arcgis import env
               env.verbose = True
        """
        # find if 1 or a list of area items is provided
        if isinstance(offline_map_area_items, _gis.Item):
            offline_map_area_items = [offline_map_area_items]
        elif isinstance(offline_map_area_items, str):
            offline_map_area_items = [offline_map_area_items]

        # get packages related to the offline area item
        _related_packages = []
        if not offline_map_area_items:  # none specified
            _related_oma_items = self.list()
            for (
                related_oma
            ) in _related_oma_items:  # get all offline packages for this web map
                _related_packages.extend(
                    related_oma.related_items("Area2Package", "forward")
                )

        else:
            for offline_map_area_item in offline_map_area_items:
                if isinstance(offline_map_area_item, _gis.Item):
                    _related_packages.extend(
                        offline_map_area_item.related_items("Area2Package", "forward")
                    )
                elif isinstance(offline_map_area_item, str):
                    offline_map_area_item = _gis.Item(
                        gis=self._gis, itemid=offline_map_area_item
                    )
                    _related_packages.extend(
                        offline_map_area_item.related_items("Area2Package", "forward")
                    )

        # update each of the packages
        if _related_packages:
            _update_list = [{"itemId": i.id} for i in _related_packages]

            # update the packages
            # from arcgis.geoprocessing._tool import Toolbox
            # pkg_tb = Toolbox(self._url, gis=self._gis)

            # result = pkg_tb.refresh_map_area_package(json.dumps(_update_list,
            #                                                    default=_date_handler))
            job = self._pm.refresh_map_area_package(
                packages=json.dumps(_update_list), future=True, gis=self._gis
            )
            if future:
                return job
            return job.result()
        else:
            return None


###########################################################################
@deprecated(
    deprecated_in="2.4.0",
    removed_in="2.4.2",
    details="Use the EnterpriseVectorTileLayerManager class found in `arcgis.layers.EnterpriseVectorTileLayerManager` instead.",
)
class EnterpriseVectorTileLayerManager(arcgis.gis._GISResource):
    """
    The ``EnterpriseVectorTileLayerManager`` class allows administration (if access permits) of ArcGIS Enterprise hosted vector tile layers.
    A Hosted Vector Tile Service is published through a Feature Layer and these methods can only be
    applied to such Vector Tile Services.
    A :class:`~arcgis.layers.VectorTileLayer` offers access to layer content.

    .. note:: Url must be admin url such as: ``https://services.myserver.com/arcgis/server/admin/services/serviceName.VectorTileServer/``
    """

    _gptbx = None

    def __init__(self, url, gis=None, vect_tile_lyr=None):
        if url.split("/")[-1].isdigit():
            url = url.replace(f"/{url.split('/')[-1]}", "")
        if gis.version <= [8, 4]:
            raise Warning("Manager not available. Update version of Enterprise")
        super(EnterpriseVectorTileLayerManager, self).__init__(url, gis)
        self._vtl = vect_tile_lyr
        self._is_hosted = self.properties["portalProperties"]["isHosted"]

    # ----------------------------------------------------------------------
    def edit(self, service_dictionairy):
        """
        This operation edits the properties of a service. To edit a service,
        you need to submit the complete JSON representation of the service,
        which includes the updates to the service properties.
        Editing a service can cause the service to be restarted with updated properties.

        The JSON representation of a service contains the following four sections:

        * Service description properties—Common properties that are shared by all services. These properties typically identify a specific service.
        * Service framework properties—Properties targeted toward the framework that hosts the GIS service. They define the life cycle and load balancing of the service.
        * Service type properties—Properties targeted toward the core service type as seen by the server administrator. Since these properties are associated with a server object, they vary across the service types.
        * Extension properties—Represent the extensions that are enabled on the service.

        .. note::
            The JSON is submitted to the operation URL as a value of the
            parameter service. You can leave out the serviceName and type parameters
            in the JSON representation. Any other properties that are left out are not persisted by the server.

        ===================     ====================================================================
        **Parameter**            **Description**
        -------------------     --------------------------------------------------------------------
        service_dictionary      Required dict. The JSON representation of the service and the
                                properties that have been updated or added.

                                Example:

                                    |    {
                                    |        "serviceName": "RI_Fed2019_WM",
                                    |        "type": "VectorTileServer",
                                    |        "description": "",
                                    |        "capabilities": "TilesOnly,Tilemap",
                                    |        "extensions": [],
                                    |        "frameworkProperties": {},
                                    |        "datasets": []
                                    |        }
        ===================     ====================================================================


        :return: boolean
        """
        vtl_service = _layers.Service(self.url, self._gis)
        return vtl_service.edit(service_dictionairy)

    # ----------------------------------------------------------------------
    def start(self):
        """This operation starts a service and loads the service's configuration."""
        vtl_service = _layers.Service(self.url, self._gis)
        return vtl_service.start()

    # ----------------------------------------------------------------------
    def stop(self):
        """
        This operation stops all instances of a service. Once a service is
        stopped, it cannot process any incoming requests. Performing this
        operation will stop the respective servers, terminating all pods
        that run this service.
        """
        vtl_service = _layers.Service(self.url, self._gis)
        return vtl_service.stop()

    # ----------------------------------------------------------------------
    def change_provider(self, provider: str):
        """
        The changeProvider operation updates an individual service to use
        either a dedicated or a shared instance type. When a qualified service
        is published, the service is automatically set to use shared instances.

        When using this operation, services may populate other provider types
        as values for the provider parameter, such as ArcObjects and SDS.
        While these are valid provider types, this operation does not support
        changing the provider of such services to either ArcObjects11 or DMaps.
        Services with ArcObjects or SDS as their provider cannot change their instance type.

        ======================      =======================================================
        **Parameter**                **Description**
        ----------------------      -------------------------------------------------------
        provider                    Optional String. Specifies the service instance as either
                                    a shared ("DMaps") or dedicated ("ArcObjects11") instance
                                    type. These values are case sensitive.
        ======================      =======================================================

        :return: Boolean

        """
        if provider in ["ArcObjects11", "DMaps"]:
            vtl_service = _layers.Service(self.url, self._gis)
            return vtl_service.change_provider(provider)
        return False

    # ----------------------------------------------------------------------
    def delete(self):
        """
        This operation deletes an individual service, stopping the service
        and removing all associated resources and configurations.
        """
        vtl_service = _layers.Service(self.url, self._gis)
        return vtl_service.delete()

    # ----------------------------------------------------------------------
    @property
    def _tbx(self):
        """gets the toolbox"""
        if self._gptbx is None:
            self._gptbx = import_toolbox(
                url_or_item=self._gis.hosting_servers[0].url
                + "/System/CachingControllers/GPServer",
                gis=self._gis,
            )
            self._gptbx._is_fa = True
        return self._gptbx

    # ----------------------------------------------------------------------
    def rebuild_cache(self, min_scale=None, max_scale=None):
        """
        The rebuild_cache operation updates the vector tile layer cache to reflect
        any changes made.
        The results of the operation is the url to the vector tile service once it is
        done rebuilding.

        ======================      =======================================================
        **Parameter**                **Description**
        ----------------------      -------------------------------------------------------
        min_scale                   Optional Float. Represents the minimum scale of the tiles.
                                    If nothing is provided, default value is used.
        ----------------------      -------------------------------------------------------
        max_scale                   Optional Float. Represents the maximum scale of the tiles.
                                    If nothing is provided, default value is used.
        ======================      =======================================================
        """
        return self._tbx.manage_vector_tile_cache(
            service_name=self.properties.serviceName,
            service_folder="Hosted",
            min_scale=min_scale,
            max_scale=max_scale,
        )


###########################################################################
@deprecated(
    deprecated_in="2.4.0",
    removed_in="2.4.2",
    details="Use the VectorTileLayerManager class found in `arcgis.layers.VectorTileLayerManager` instead.",
)
class VectorTileLayerManager(arcgis.gis._GISResource):
    """
    The ``VectorTileLayerManager`` class allows administration (if access permits) of ArcGIS Online Hosted Vector Tile Layers.
    A Hosted Vector Tile Service is published through a Feature Layer and these methods can only be
    applied to such Vector Tile Services.
    A :class:`~arcgis.layers.VectorTileLayer` offers access to layer content.

    .. note::
        Url must be admin url such as: ``https://services.myserver.com/arcgis/rest/admin/services/serviceName/VectorTileServer/``
    """

    def __init__(self, url, gis=None, vect_tile_lyr=None):
        if url.split("/")[-1].isdigit():
            url = url.replace(f"/{url.split('/')[-1]}", "")
        super(VectorTileLayerManager, self).__init__(url, gis)
        self._vtl = vect_tile_lyr
        self._source_type = (
            self.properties["sourceType"]
            if "sourceType" in self.properties
            else self.properties["sourceServiceType"]
        )

    # ----------------------------------------------------------------------
    def edit_tile_service(
        self,
        source_item_id: str | None = None,
        export_tiles_allowed: bool | None = None,
        min_scale: float | None = None,
        max_scale: float | None = None,
        max_export_tile_count: int | None = None,
        layers: list[dict] | None = None,
        cache_max_age: int | None = None,
        max_zoom: int | None = None,
    ) -> dict:
        """
        The edit operation enables editing many parameters in the service definition as well as
        the source_item_id which can be found by looking at the Vector Tile Layer's related items.

        ======================      =======================================================
        **Parameter**                **Description**
        ----------------------      -------------------------------------------------------
        source_item_id              Optional String. The Source Item ID is the GeoWarehouse
                                    Item ID of the tile service.
        ----------------------      -------------------------------------------------------
        export_tiles_allowed        Optional boolean. ``exports_tiles_allowed`` sets
                                    the value to let users export tiles
        ----------------------      -------------------------------------------------------
        min_scale                   Optional float. Sets the services minimum scale for
                                    caching. At the moment this parameter can only be set if
                                    the Vector Tile Layer was published through a service directory.
        ----------------------      -------------------------------------------------------
        max_scale                   Optional float. Sets the services maximum scale for
                                    caching. At the moment this parameter can only be set if
                                    the Vector Tile Layer was published through a service directory.
        ----------------------      -------------------------------------------------------
        max_export_tile_count       Optional int. ``max_export_tile_count`` sets the
                                    maximum amount of tiles to be exported from a single
                                    call.
        ----------------------      -------------------------------------------------------
        layers                      Optional list of dictionaries. Each dict representing a layer.

                                    Syntax Example:

                                        | layers = [{
                                        |        "name": "Layer Name",
                                        |        "id": 1159321,
                                        |        "layerId": 0,
                                        |        "tableName": "tableName",
                                        |        "type": "Feature Layer",
                                        |        "xssTrustedFields": ""
                                        |    }]
        ----------------------      -------------------------------------------------------
        cache_max_age               Optional int. The maximum cache age. At the moment this
                                    parameter can only be set if the Vector Tile Layer was
                                    published through a feature service.
        ----------------------      -------------------------------------------------------
        max_zoom                    Optional int. The maximum zoom level. At the moment this
                                    parameter can only be set if the Vector Tile Layer was
                                    published through a feature service.
        ======================      =======================================================

        .. code-block:: python

            # USAGE EXAMPLE

            >>> from arcgis.layers import VectorTileLayer
            >>> from arcgis.gis import GIS

            # connect to your GIS and get the tile layer item
            >>> gis = GIS(url, username, password)

            >>> vector_layer_item = gis.content.get('abcd_item-id')
            >>> source_item_id = vector_tile_item.related_items(rel_type="Service2Data", direction="forward")[0]["id"]
            >>> vector_tile_layer = VectorTileLayer.fromitem(vector_layer_item)
            >>> vtl_manager = vector_tile_layer.manager
            >>> vtl_manager.edit_tile_service(
                                            min_scale = 50,
                                            max_scale = 100,
                                            source_item_id = source_item_id,
                                            export_tiles_allowed = True,
                                            max_Export_Tile_Count = 10000
                                            )
        """
        # Parameters depend on how the vector tile layer was published.
        feature_service_pub = True if self._source_type == "FeatureServer" else False

        params = {
            "f": "json",
            "serviceDefinition": {},
        }
        if max_export_tile_count:
            params["serviceDefinition"]["maxExportTilesCount"] = max_export_tile_count
        if export_tiles_allowed and export_tiles_allowed in [True, False]:
            params["serviceDefinition"]["exportTilesAllowed"] = export_tiles_allowed
        if source_item_id:
            params["sourceItemId"] = source_item_id
        if layers:
            params["serviceDefinition"]["layerProperties"] = {"layers": layers}

        # These parameters depend on publish source.
        if min_scale and feature_service_pub is False:
            params["serviceDefinition"]["minScale"] = min_scale
        if max_scale and feature_service_pub is False:
            params["serviceDefinition"]["maxScale"] = max_scale
        if cache_max_age and feature_service_pub is True:
            params["serviceDefinition"]["cacheMaxAge"] = cache_max_age
        if max_zoom and feature_service_pub is False:
            params["serviceDefinition"]["maxZoom"] = max_zoom

        # endpoint and post call
        url = self._url + "/edit"
        return self._con.post(path=url, params=params)

    # ----------------------------------------------------------------------
    def update_tiles(self, merge_bundle: bool = False) -> dict:
        """
        The update_tiles operation supports updating the cooking extent and
        cache levels in a Hosted Vector Tile Service. The results of the
        operation is a response indicating success and a url
        to the Job Statistics page, or failure.

        It is recommended to use the `rebuild_cache` method when your layer has been
        published through a Feature Layer since edits require regeneration of the tiles.

        ===============     ====================================================
        **Parameter**        **Description**
        ---------------     ----------------------------------------------------
        merge_bundle        Optional bool. Default is False. This parameter will
                            only be set if the Vector Tile Layer has been published
                            through a service directory.
        ===============     ====================================================

        :returns:
           Dictionary. If the product is not ArcGIS Online tile service, the
           result will be None.

        .. code-block:: python

            # USAGE EXAMPLE

            >>> from arcgis.layers import VectorTileLayer
            >>> from arcgis.gis import GIS

            # connect to your GIS and get the web map item
            >>> gis = GIS(url, username, password)
            >>> vector_layer_item = gis.content.get('abcd_item-id')
            >>> vector_tile_layer = VectorTileLayer.fromitem(vector_layer_item)
            >>> vtl_manager = vector_tile_layer.manager
            >>> update_tiles = vtl_manager.update_tiles()
            >>> type(update_tiles)
            <Dictionary>
        """
        # Parameters depend on how the vector tile layer was published.
        feature_service_pub = True if self._source_type == "FeatureServer" else False

        params = {"f": "json"}
        if feature_service_pub:
            url = "%s/updateTiles" % self._url
        else:
            url = "%s/update" % self._url
            params["mergeBundles"] = merge_bundle
        return self._con.post(url, params)

    # ----------------------------------------------------------------------
    def refresh(self):
        """
        The refresh operation clears and refreshes the service cache.
        """
        url = self._url + "/refresh"
        params = {"f": "json"}
        return self._con.post(path=url, params=params)

    # ----------------------------------------------------------------------
    def rebuild_cache(self):
        """
        The rebuild_cache operation update the vector tile layer cache to reflect
        any changes made to the feature layer used to publish this vector tile layer.
        The results of the operation is a response indicating success, which
        redirects you to the Job Statistics page, or failure.
        """
        url = self._url + "/rebuildCache"
        params = {"f": "json"}
        return self._con.get(url, params)

    # ----------------------------------------------------------------------
    def status(self) -> dict:
        """
        The status operation returns a dictionary indicating
        whether a service is started (available) or stopped.
        """
        url = self._url + "/status"
        params = {"f": "json"}
        return self._con.get(url, params)

    # ----------------------------------------------------------------------
    def jobs(self) -> dict:
        """
        The tile service job summary (jobs) resource represents a
        summary of all jobs associated with a vector tile service.
        Each job contains a jobid that corresponds to the specific
        jobid run and redirects you to the Job Statistics page.

        """
        url = self._url + "/jobs"
        params = {"f": "json"}
        return self._con.get(url, params)

    # ----------------------------------------------------------------------
    def job_statistics(self, job_id: str) -> dict:
        """
        The tile service job summary (jobs) resource represents a
        summary of all jobs associated with a vector tile service.
        Each job contains a jobid that corresponds to the specific
        jobid run and redirects you to the Job Statistics page.

        """
        url = self._url + "/jobs/{job_id}".format(job_id=job_id)
        params = {"f": "json"}
        return self._con.post(url, params)

    # ----------------------------------------------------------------------
    def delete_job(self, job_id: str) -> dict:
        """
        This operation deletes the specified asynchronous job being run by
        the geoprocessing service. If the current status of the job is
        SUBMITTED or EXECUTING, it will cancel the job. Regardless of status,
        it will remove all information about the job from the system. To cancel a
        job in progress without removing information, use the Cancel Job operation.
        """
        url = self._url + "jobs/{job_id}/delete".format(job_id=job_id)
        params = {"f": "json"}
        return self._con.post(url, params)

    # ----------------------------------------------------------------------
    def cancel_job(self, job_id: str) -> dict:
        """
        The cancel operation supports cancelling a job while update
        tiles is running from a hosted feature service. The result of this
        operation is a response indicating success or failure with error
        code and description.
        """
        url = self._url + "jobs/{job_id}/cancel".format(job_id=job_id)
        params = {"f": "json"}
        return self._con.post(url, params)

    # ----------------------------------------------------------------------
    def rerun_job(self, code, job_id: str) -> dict:
        """
        The ``rerun_job`` operation supports re-running a canceled job from a
        hosted map service. The result of this operation is a response
        indicating success or failure with error code and description.

        ===============     ====================================================
        **Parameter**        **Description**
        ---------------     ----------------------------------------------------
        code                required string, parameter used to re-run a given
                            jobs with a specific error
                            code: ``ALL | ERROR | CANCELED``
        ---------------     ----------------------------------------------------
        job_id              required string, job to reprocess
        ===============     ====================================================

        :returns:
           A boolean or dictionary
        """
        url = self._url + "/jobs/%s/rerun" % job_id
        params = {"f": "json", "rerun": code}
        return self._con.post(url, params)

    ######################### These Methods Only Apply to VTL Service from a Service Directory #################################
    def swap(self, target_service_name):
        """
        The swap operation replaces the current service cache with an existing one.

        .. note::
            The ``swap`` operation is for ArcGIS Online only and can only be used for a Vector
            Tile Layer published from a service directory.

        ====================        ====================================================
        **Parameter**                **Description**
        --------------------        ----------------------------------------------------
        target_service_name         Required string. Name of service you want to swap with.
        ====================        ====================================================

        :return: Dictionary indicating success or error
        """
        if self._source_type != "FeatureServer":
            url = self._url + "/swap"
            params = {"f": "json", "targetServiceName": target_service_name}
            return self._con.post(url, params)
        return None

    # ----------------------------------------------------------------------
    def delete_tiles(self):
        """
        The ``delete_tiles`` method deletes tiles from the current cache.

        .. note::
            The ``delete_tiles`` operation is for ArcGIS Online only and can only
            be used for a Vector Tile Layer published from a service directory.

        :return:
           A dictionary

        .. code-block:: python

            # USAGE EXAMPLE

            >>> from arcgis.layers import VectorTileLayer
            >>> from arcgis.gis import GIS

            # connect to your GIS
            >>> gis = GIS(url, username, password)

            >>> vector_layer_item = gis.content.get('abcd_item-id')
            >>> vector_tile_layer = VectorTileLayer.fromitem(vector_layer_item)
            >>> vtl_manager = vector_tile_layer.manager
            >>> deleted_tiles = vtl_manager.delete_tiles()
            >>> type(deleted_tiles)
        """
        if self._source_type != "FeatureServer":
            params = {
                "f": "json",
            }
            url = self._url + "/delete"
            return self._con.post(url, params)
        return None


###########################################################################
@deprecated(
    deprecated_in="2.4.0",
    removed_in="2.4.2",
    details="Use the SymbolService class found in `arcgis.layers.SymbolService` instead.",
)
class SymbolService:
    """
    Symbol service is an ArcGIS Server utility service that provides access
    to operations to build and generate images for Esri symbols to be
    consumed by internal and external web applications.
    """

    _url = None
    _gis = None
    _properties = None

    def __init__(self, url: str, gis: arcgis.gis.GIS = None):
        self._url = url
        if gis is None:
            gis = arcgis.env.active_gis
        self._gis = gis

    @property
    def properties(self) -> dict[str, Any]:
        """returns the service's properties"""
        if self._properties is None:
            self._properties = arcgis._impl.common._isd.InsensitiveDict(
                self._gis._con.get(self._url, {"f": "json"})
            )
        return self._properties

    def generate_symbol(self, svg: str) -> dict:
        """converts an SVG Image to a CIM Compatible Image"""
        url = f"{self._url}/generateSymbol"
        params = {"f": "json"}
        files = {"svgImage": svg}
        return self._gis._con.post_multipart(url, params, files=files)

    def generate_image(
        self,
        item: Item,
        name: str | None = None,
        dict_features: dict[str, Any] | None = None,
        size: str = "200,200",
        scale: float = 1,
        anchor: bool = False,
        image_format: str = "png",
        dpi: int = 96,
        file_path: str | pathlib.Path = None,
    ) -> str:
        """
        Returns a single symbol based on a web style item.

        ============================    ===================================================================================================================
        **Parameter**                    **Description**
        ----------------------------    -------------------------------------------------------------------------------------------------------------------
        item                            Required Item. The web style ArcGIS Enterprise portal item ID. The web style must belong to the same organization
                                        the ArcGIS Server is federated to.
        ----------------------------    -------------------------------------------------------------------------------------------------------------------
        name                            Optional String. The web style ArcGIS Enterprise portal item ID. The web style must belong to the same organization
                                        the ArcGIS Server is federated to.
        ----------------------------    -------------------------------------------------------------------------------------------------------------------
        dict_features                   Optional dict[str, Any]. The attributes and configuration key and value pairs for dictionary-based styles.
        ----------------------------    -------------------------------------------------------------------------------------------------------------------
        size                            Optional String. The size (width and height) of the exported image in pixels. If the size is not specified, the
                                        image will be constrained by the requested symbol's size.
        ----------------------------    -------------------------------------------------------------------------------------------------------------------
        scale                           Optional Float. A value of 1.0 implies the symbol is not scaled. Setting the value to 1.5 scales the image to 50
                                        percent more than the image's original size. Settings the value to 0.5 reduces the image's original size by 50
                                        percent.
                                        If both the size and scale parameters are specified, both changes will be honored; the symbol will be scaled to the
                                        value set for scale and resized to the value set for the size parameter.
        ----------------------------    -------------------------------------------------------------------------------------------------------------------
        anchor                          Optional Bool. The symbol placement in the image. When set to true, the original symbol anchor point placement in
                                        the image is honored. When set to false, the symbol is centered to the image. Having the image centered can be
                                        useful if you want to preview the whole symbol without taking symbol offset or anchor points into account. The
                                        default value is false.
        ----------------------------    -------------------------------------------------------------------------------------------------------------------
        image_format                    Optional String. The output image format. The default format is png. The allowed values are: png, png8, png24,
                                        png32, jpg, bmp, gif, svg, and svgz.
        ----------------------------    -------------------------------------------------------------------------------------------------------------------
        dpi                             Optional Int. The device resolution of the exported image (dots per inch). If the dpi value is not specified, an
                                        image with a default DPI of 96 will be exported.
        ----------------------------    -------------------------------------------------------------------------------------------------------------------
        file_path                       Optional String | pathlib.Path. The full save path with the file name to the save location.  The folder must exist.
        ============================    ===================================================================================================================

        :return: String

        """
        save_file_name: str = None
        save_folder: str = None
        if file_path:
            save_folder, save_file_name = os.path.dirname(file_path), os.path.basename(
                file_path
            )
        else:
            save_folder, save_file_name = (
                tempfile.gettempdir(),
                f"symbol_file.{image_format}",
            )
        if name is None and dict_features is None:
            raise ValueError("A name or dict_features must be provided.")
        image_formats: list[str] = [
            "png",
            "png8",
            "png24",
            "png32",
            "jpg",
            "bmp",
            "gif",
            "svg",
            "svgz",
        ]
        if image_format.lower() not in image_formats:
            raise ValueError(f"Invalid image format: {image_format}")
        params: dict[str, Any] = {
            "webstyle": item.itemid,
            "symbolName": name or "",
            "dictionaryFeatures": dict_features or "",
            "size": size,
            "scaleFactor": scale,
            "centerAnchorPoint": anchor,
            "dpi": dpi,
            "f": "image",
            "imageFormat": image_format,
        }
        url: str = f"{self._url}/generateImage"
        return self._gis._con.get(
            url,
            params,
            try_json=False,
            file_name=save_file_name,
            out_folder=save_folder,
        )


###########################################################################
@deprecated(
    deprecated_in="2.4.0",
    removed_in="2.4.2",
    details="Use the VectorTileLayer class found in `arcgis.layers.VectorTileLayer` instead.",
)
class VectorTileLayer(arcgis.gis.Layer):
    """
    A Vector Tile Layer is a type of data layer used to access and display
    tiled data and its corresponding styles. This is stored as an item in ArcGIS
    and is used to access a vector tile service. Layer data include its
    name, description, and any overriding style definition.
    """

    def __init__(self, url, gis=None):
        super(VectorTileLayer, self).__init__(url, gis)

    # ----------------------------------------------------------------------
    @classmethod
    def fromitem(cls, item) -> VectorTileLayer:
        if not item.type == "Vector Tile Service":
            raise TypeError(
                "Item must be a type of Vector Tile Service, not " + item.type
            )
        if item._gis._use_private_url_only:
            url: str = _get_item_url(item=item)
        else:
            url: str = item.url
        return cls(url, item._gis)

    # ----------------------------------------------------------------------
    @property
    def styles(self) -> dict:
        """
        The styles property returns styles for vector tiles in Mapbox GL
        Style specification version 8. The response for this styles resource
        includes the sprite and glyphs properties, with a relative path
        to the Vector Tile Sprite and Vector Tile Font resources.
        It also includes the version property,
        which represents the version of the style specification.
        """
        url = "{url}/resources/styles".format(url=self._url)
        params = {"f": "json"}
        return self._con.get(path=url, params=params)

    # ----------------------------------------------------------------------
    @property
    def tile_map(self) -> dict:
        """
        The tile_map property describes a quadtree of tiles and can be used to
        avoid requesting tiles that don't exist in the server. Each node
        of the tree has an associated tile. The root node (lod 0) covers
        the entire extent of the data. Children are identified by their position
        with NW, NE, SW, and SE. Tiles are identified by lod/h/v, where h and v
        are indexes on a 2^lod by 2^lod grid . These values are derived from the
        position in the tree. The tree has a variable depth. A node doesn't have
        children if the complexity of the data in the associated tile is below
        a threshold. This threshold is based on a combination of number of
        features, attributes, and vertices.

        """
        url = "{url}/tilemap".format(url=self._url)
        return self._con.get(path=url, params={})

    # ----------------------------------------------------------------------
    @property
    def manager(self) -> VectorTileLayerManager:
        """
        The ``manager`` property returns an instance of :class:`~arcgis.layers.VectorTileLayerManager` class or
        :class:`~arcgis.layers.EnterpriseVectorTileLayerManager` class
        which provides methods and properties for administering this service.
        """
        if self._gis._portal.is_arcgisonline:
            rd = {"/rest/services/": "/rest/admin/services/"}
            adminURL = self._str_replace(self._url, rd)
            if adminURL.split("/")[-1].isdigit():
                adminURL = adminURL.replace(f'/{adminURL.split("/")[-1]}', "")
            self._admin = VectorTileLayerManager(adminURL, self._gis, self)
        else:
            rd = {
                "/rest/": "/admin/",
                "/VectorTileServer": ".VectorTileServer",
            }
            adminURL = self._str_replace(self._url, rd)
            if adminURL.split("/")[-1].isdigit():
                adminURL = adminURL.replace(f'/{adminURL.split("/")[-1]}', "")
            self._admin = EnterpriseVectorTileLayerManager(adminURL, self._gis, self)
        return self._admin

    # ----------------------------------------------------------------------
    @property
    def info(self) -> list:
        """
        The ``info`` property retrieves the relative paths to a list of resource files.

        :return:
           A list of relative paths
        """
        url = "{url}/resources/info".format(url=self._url)
        params = {"f": "json"}
        res = self._con.get(path=url, params=params)
        return res["resourceInfo"]

    # ----------------------------------------------------------------------
    def tile_fonts(self, fontstack: str, stack_range: str):
        """
        The ``tile_fonts`` method retrieves glyphs in
        `protocol buffer format. <https://developers.google.com/protocol-buffers/>`_

        ============================    ===================================================================================================================
        **Parameter**                    **Description**
        ----------------------------    -------------------------------------------------------------------------------------------------------------------
        fontstack                       Required string.

                                        .. note::
                                            The template url for this font resource is represented in the
                                            `Vector Tile Style <https://developers.arcgis.com/rest/services-reference/enterprise/vector-tile-style.htm>`_
                                            resource.
        ----------------------------    -------------------------------------------------------------------------------------------------------------------
        stack_range                     Required string that depict a range. Ex: "0-255"
        ============================    ===================================================================================================================

        :return:
            Glyphs in PBF format
        """
        url = "{url}/resources/fonts/{fontstack}/{stack_range}.pbf".format(
            url=self._url, fontstack=fontstack, stack_range=stack_range
        )
        params = {}
        return self._con.get(path=url, params=params, force_bytes=True)

    # ----------------------------------------------------------------------
    def vector_tile(self, level: int, row: int, column: int):
        """
        The ``vector_tile`` method represents a single vector tile for the map.

        .. note::
            The bytes for the tile at the specified level, row and column are
            returned in PBF format. If a tile is not found, an error is returned.

        ============================    ================================================
        **Parameter**                    **Description**
        ----------------------------    ------------------------------------------------
        level                           Required string. A level number as a string.
        ----------------------------    ------------------------------------------------
        row                             Required string. Number of the row that the tile
                                        belongs to.
        ----------------------------    ------------------------------------------------
        column                          Required string. Number of the column that tile
                                        belongs to.
        ============================    ================================================

        :returns:
            Bytes in PBF format
        """
        url = "{url}/tile/{level}/{row}/{column}.pbf".format(
            url=self._url, level=level, row=row, column=column
        )
        params = {}
        return self._con.get(path=url, params=params, try_json=False, force_bytes=True)

    # ----------------------------------------------------------------------
    def tile_sprite(self, out_format: str = "sprite.json") -> dict:
        """
        The ``tile_sprite`` resource retrieves sprite images and metadata.

        ============================    ================================================
        **Parameter**                    **Description**
        ----------------------------    ------------------------------------------------
        out_format                      Optional string. Default is "sprite.json".

                                        Values: ``sprite.json`` | ``sprite.png`` | ``sprite@2x.png``
        ============================    ================================================

        :return:
            Sprite image and metadata.
        """
        url = "{url}/resources/sprites/{f}".format(url=self._url, f=out_format)
        return self._con.get(path=url, params={})

    # ----------------------------------------------------------------------
    def export_tiles(
        self,
        levels: str | None = None,
        export_extent: dict[str, Any] | None = None,
        polygon: dict[str, Any] | _geometry.Polygon | None = None,
        create_item: bool = False,
    ) -> str | Item:
        """
        Export vector tile layer

        =====================       =======================================================
        **Parameter**                **Description**
        ---------------------       -------------------------------------------------------
        levels                      Optional string.Specifies the tiled service levels to export.
                                    The values should correspond to Level IDs. The values
                                    can be comma-separated values or a range of values.
                                    Ensure that the tiles are present at each specified level.

                                    .. code-block:: python

                                        # Example:

                                        # Comma-separated values
                                        >>> levels=1,2,3,4,5,6,7,8,9

                                        //Range values
                                        >>> levels=1-4, 7-9
        ---------------------       -------------------------------------------------------
        export_extent               Optional dictionary of the extent (bounding box) of the vector
                                    tile package to be exported.
                                    The extent should be within the specified spatial reference.
                                    The default value is the full extent of the tiled map service.

                                    .. code-block:: python

                                        # Example:

                                        >>> export_extent = {
                                                             "xmin": -109.55, "ymin" : 25.76,
                                                             "xmax": -86.39, "ymax" : 49.94,
                                                             "spatialReference": {"wkid": 4326}
                                                            }
        ---------------------       -------------------------------------------------------
        polygon                     Optional dictionary.
                                    Introduced at 10.7. A JSON representation of a polygon,
                                    containing an array of rings and a spatialReference.

                                    .. code-block:: python

                                        # Example:

                                        polygon = {
                                                   "rings": [
                                                             [[6453,16815],[10653,16423],
                                                             [14549,5204],[-7003,6939],
                                                             [6453,16815]],[[914,7992],
                                                             [3140,11429],[1510,10525],
                                                             [914,7992]]
                                                            ],
                                                   "spatialReference": {"wkid": 54004}
                                                  }
        ---------------------       -------------------------------------------------------
        create_item                 Optional boolean. Indicated whether an item will be created
                                    from the export (True) or a path to a downloaded file (False).
                                    Default is False. ArcGIS Online Only.
        =====================       =======================================================

        :returns:
            A list of exported item dictionaries or a single path
        """
        if not self.properties.exportTilesAllowed:
            raise arcgis.gis.Error(
                "Export Tiles operation is not allowed for this service. Enable offline mode."
            )

        params = {
            "f": "json",
            "exportBy": "levelId",
            "storageFormatType": "Compact",
            "tilePackage": False,
            "optimizeTilesForSize": False,
        }
        params["levels"] = levels if levels else None
        params["exportExtent"] = export_extent if export_extent else "DEFAULT"
        # parameter introduced at 10.7
        if polygon and self.gis.version >= [7, 1]:
            params["polygon"] = polygon
        if create_item is True:
            params["createItem"] = "on"
        url = "{url}/exportTiles".format(url=self._url)

        # a job is returned from the get
        exportJob = self._con.get(path=url, params=params)

        # get the job information
        path = "%s/jobs/%s" % (self._url, exportJob["jobId"])

        resp_params = {"f": "json"}
        job_response = self._con.post(path, resp_params)

        if "status" in job_response or "jobStatus" in job_response:
            status = job_response.get("status") or job_response.get("jobStatus")
            i = 0
            while not status == "esriJobSucceeded":
                if i < 10:
                    i = i + 1
                time.sleep(i)

                job_response = self._con.post(path, resp_params)
                status = job_response.get("status") or job_response.get("jobStatus")
                if status in [
                    "esriJobFailed",
                    "esriJobCancelling",
                    "esriJobCancelled",
                    "esriJobTimedOut",
                ]:
                    print(str(job_response["messages"]))
                    raise Exception("Job Failed with status " + status)
        else:
            raise Exception("No job results.")

        if "results" in job_response:
            value = job_response["results"]["out_service_url"]["paramUrl"]
            result_path = path + "/" + value
            params = {"f": "json"}
            allResults = self._con.get(path=result_path, params=params)

            if "value" in allResults:
                value = allResults["value"]
                params = {"f": "json"}
                gpRes = self._con.get(path=value, params=params)
                return gpRes["files"]
            else:
                return None
        elif "output" in job_response:
            allResults = job_response["output"]
            if allResults["itemId"]:
                return _gis.Item(gis=self._gis, itemid=allResults["itemId"])
            else:
                if self._gis._portal.is_arcgisonline:
                    return [
                        self._con.get(url, try_json=False, add_token=False)
                        for url in allResults["outputUrl"]
                    ]
                else:
                    return [
                        self._con.get(url, try_json=False)
                        for url in allResults["outputUrl"]
                    ]
        else:
            raise Exception(job_response)

    # ----------------------------------------------------------------------
    def _str_replace(self, mystring, rd):
        """Replaces a value based on a key/value pair where the
        key is the text to replace and the value is the new value.

        The find/replace is case insensitive.

        """
        import re

        patternDict = {}
        for key, value in rd.items():
            pattern = re.compile(re.escape(key), re.IGNORECASE)
            patternDict[value] = pattern
        for key in patternDict:
            regex_obj = patternDict[key]
            mystring = regex_obj.sub(key, mystring)
        return mystring


###########################################################################
@deprecated(
    deprecated_in="2.4.0",
    removed_in="2.4.2",
    details="Use the EnterpriseMapImageLayerManager class found in `arcgis.layers.EnterpriseMapImageLayerManager` instead.",
)
class EnterpriseMapImageLayerManager(arcgis.gis._GISResource):
    """
    The ``EnterpriseMapImageLayerManager`` class allows administration (if access permits) of ArcGIS Enterprise Map Image Layers and Tile Layers.
    A :class:`~arcgis.layers.MapImageLayer` offers access to layer content.

    .. note:: Url must be admin url such as: ``https://services.myserver.com/arcgis/rest/admin/services/serviceName/MapServer/``
    """

    def __init__(self, url, gis=None, map_img_lyr=None):
        if url.split("/")[-1].isdigit():
            url = url.replace(f"/{url.split('/')[-1]}", "")
        super(EnterpriseMapImageLayerManager, self).__init__(url, gis)
        self._ms = map_img_lyr

    # ----------------------------------------------------------------------
    def edit(self, service_dictionary):
        """
        To edit a service, you need to submit the complete JSON
        representation of the service, which includes the updates to the
        service properties. Editing a service causes the service to be
        restarted with updated properties.

        ===================     ====================================================================
        **Parameter**            **Description**
        -------------------     --------------------------------------------------------------------
        service_dictionary      Required dict. The service JSON as a dictionary.
        ===================     ====================================================================


        :return: boolean
        """
        mil_service = _layers.Service(self.url, self._gis)
        return mil_service.edit(service_dictionary)

    # ----------------------------------------------------------------------
    def start(self):
        """starts the specific service"""
        mil_service = _layers.Service(self.url, self._gis)
        return mil_service.start()

    # ----------------------------------------------------------------------
    def stop(self):
        """stops the specific service"""
        mil_service = _layers.Service(self.url, self._gis)
        return mil_service.stop()

    # ----------------------------------------------------------------------
    def change_provider(self, provider: str):
        """
        Allows for the switching of the service provide and how it is hosted on the ArcGIS Server instance.

        Provider parameter options:

        + `ArcObjects` means the service is running under the ArcMap runtime i.e. published from ArcMap
        + `ArcObjects11`: means the service is running under the ArcGIS Pro runtime i.e. published from ArcGIS Pro
        + `DMaps`: means the service is running in the shared instance pool (and thus running under the ArcGIS Pro provider runtime)

        :return: Boolean

        """
        mil_service = _layers.Service(self.url, self._gis)
        return mil_service.change_provider(provider)

    # ----------------------------------------------------------------------
    def delete(self):
        """deletes a service from arcgis server"""
        mil_service = _layers.Service(self.url, self._gis)
        return mil_service.delete()


###########################################################################
@deprecated(
    deprecated_in="2.4.0",
    removed_in="2.4.2",
    details="Use the MapImageLayerManager class found in `arcgis.layers.MapImageLayerManager` instead.",
)
class MapImageLayerManager(arcgis.gis._GISResource):
    """
    The ``MapImageLayerManager`` class allows administration (if access permits) of ArcGIS Online Hosted Tile Layers
    or Cached Map Services.
    A :class:`~arcgis.layers.MapImageLayer` offers access to the Map Server endpoints
    that allow you to edit the tile service, update tiles, refresh, and more.

    To use this manager off of the MapImageLayer Class, pass in a url ending with /MapServer
    when instantiating that class.

    .. note::
        Map Image Layers are created from Enterprise Services and their manager can
        be accessed through the EnterpriseMapImageLayerManager.
    """

    def __init__(self, url, gis=None, map_img_lyr=None):
        if url.split("/")[-1].isdigit():
            url = url.replace(f"/{url.split('/')[-1]}", "")
        super(MapImageLayerManager, self).__init__(url, gis)
        self._ms = map_img_lyr

    # ----------------------------------------------------------------------
    def refresh(self):
        """
        The ``refresh`` operation refreshes a service, which clears the web
        server cache for the service.
        """
        url = self._url + "/refresh"
        params = {"f": "json"}

        res = self._con.post(url, params)

        super(MapImageLayerManager, self)._refresh()
        if self._ms:
            self._ms._refresh()

        return res

    # ----------------------------------------------------------------------
    def cancel_job(self, job_id):
        """
        The ``cancel_job`` operation supports cancelling a job while update
        tiles is running from a hosted feature service. The result of this
        operation is a response indicating success or failure with error
        code and description.

        ===============     ====================================================
        **Parameter**        **Description**
        ---------------     ----------------------------------------------------
        job_id               Required String. The job id to cancel.
        ===============     ====================================================

        """
        url = self._url + "/jobs/%s/cancel" % job_id
        params = {"f": "json"}
        return self._con.post(url, params)

    # ----------------------------------------------------------------------
    def job_statistics(self, job_id: str):
        """
        Returns the job statistics for the given jobId

        """
        url = self._url + "/jobs/%s" % job_id
        params = {"f": "json"}
        return self._con.post(url, params)

    # ----------------------------------------------------------------------
    def import_tiles(
        self,
        item: _gis.Item,
        levels: Optional[Union[str, list[int]]] = None,
        extent: Optional[Union[str, dict[str, int]]] = None,
        merge: bool = False,
        replace: bool = False,
    ):
        """
        The ``import_tiles`` method imports tiles from an :class:`~arcgis.gis.Item` object.

        Before executing this operation, you will need to make certain the following prerequisites are met:

        - Upload the TPK you wish to merge with the existing service, take note of its item ID.
        - Make certain that the uploaded TPK, TPKX item's tiling scheme matches with the service you wish to import into.
        - The source service LOD's should include all the LOD's that are part of the imported TPK item. For example, if the source service has tiles from levels 0 through 10, you can import tiles only within these levels and not above it.


        ===============     ====================================================
        **Parameter**        **Description**
        ---------------     ----------------------------------------------------
        item                Required ItemId or :class:`~arcgis.gis.Item` object. The TPK file's item id.
                            This TPK file contains to-be-extracted bundle files
                            which are then merged into an existing cache service.
        ---------------     ----------------------------------------------------
        levels              Optional String / List of integers, The level of details
                            to update. Example: "1,2,10,20" or [1,2,10,20]
        ---------------     ----------------------------------------------------
        extent              Optional String / Dict. The area to update as Xmin, YMin, XMax, YMax
                            example: "-100,-50,200,500" or
                            {'xmin':100, 'ymin':200, 'xmax':105, 'ymax':205}
        ---------------     ----------------------------------------------------
        merge               Optional Boolean. Default is false and applicable to
                            compact cache storage format. It controls whether
                            the bundle files from the TPK file are merged with
                            the one in the existing cached service. Otherwise,
                            the bundle files are overwritten.
        ---------------     ----------------------------------------------------
        replace             Optional Boolean. Default is false, applicable to
                            compact cache storage format and used when
                            merge=true. It controls whether the new tiles will
                            replace the existing ones when merging bundles.
        ===============     ====================================================
        :return:
            A dictionary

        .. code-block:: python

            # USAGE EXAMPLE
            >>> from arcgis.layers import MapImageLayer
            >>> from arcgis.gis import GIS
            # connect to your GIS and get the web map item
            >>> gis = GIS(url, username, password)
            >>> map_image_layer = MapImageLayer("<url>", gis)
            >>> mil_manager = map_image_layer.manager
            >>> imported_tiles = mil_manager.import_tiles(item="<item-id>",
                                                          levels = "11-20",
                                                          extent = {"xmin":6224324.092137296,
                                                                    "ymin":487347.5253569535,
                                                                    "xmax":11473407.698535524,
                                                                    "ymax":4239488.369818687,
                                                                    "spatialReference":{"wkid":102100}
                                                                    },
                                                          merge = True,
                                                        replace = True
                                                          )
            >>> type(imported_tiles)
            <Dictionary>
        """
        params = {
            "f": "json",
            "sourceItemId": None,
            "extent": extent,
            "levels": levels,
            "mergeBundle": merge,
            "replaceTiles": replace,
        }
        if isinstance(item, str):
            params["sourceItemId"] = item
        elif isinstance(item, _gis.Item):
            params["sourceItemId"] = item.itemid
        else:
            raise ValueError("The `item` must be a string or Item")
        if self._gis.version >= [10, 3]:
            url = self._url + "/import"
        else:
            url = self._url + "/importTiles"
        res = self._con.post(url, params)
        return res

    # ----------------------------------------------------------------------
    def update_tiles(
        self,
        levels: Optional[Union[str, list[int]]] = None,
        extent: Optional[Union[str, dict[str, int]]] = None,
        merge: bool = False,
        replace: bool = False,
    ):
        """
        The ``update_tiles`` method starts tile generation for ArcGIS Online. The levels of detail
        and the extent are needed to determine the area where tiles need
        to be rebuilt.

        .. note::
            The ``update_tiles`` operation is for ArcGIS Online only.

        ===============     ====================================================
        **Parameter**        **Description**
        ---------------     ----------------------------------------------------
        levels              Optional String / List of integers, The level of details
                            to update. Example: "1,2,10,20" or [1,2,10,20]
        ---------------     ----------------------------------------------------
        extent              Optional String / Dict. The area to update as Xmin, YMin, XMax, YMax
                            Example:
                                "-100,-50,200,500" or {'xmin':100, 'ymin':200, 'xmax':105, 'ymax':205}
        ---------------     ----------------------------------------------------
        merge               Optional Boolean. Default is false and applicable to
                            compact cache storage format. It controls whether
                            the bundle files from the TPK file are merged with
                            the one in the existing cached service. Otherwise,
                            the bundle files are overwritten.
        ---------------     ----------------------------------------------------
        replace             Optional Boolean. Default is false, applicable to
                            compact cache storage format and used when
                            merge=true. It controls whether the new tiles will
                            replace the existing ones when merging bundles.
        ===============     ====================================================

        :return:
           Dictionary. If the product is not ArcGIS Online tile service, the
           result will be None.

        .. code-block:: python

            # USAGE EXAMPLE

            >>> from arcgis.layers import MapImageLayer
            >>> from arcgis.gis import GIS

            # connect to your GIS and get the web map item
            >>> gis = GIS(url, username, password)
            >>> map_image_layer = MapImageLayer("<url>", gis)
            >>> mil_manager = map_image_layer.manager
            >>> update_tiles = mil_manager.update_tiles(levels = "11-20",
                                                        extent = {"xmin":6224324.092137296,
                                                                    "ymin":487347.5253569535,
                                                                    "xmax":11473407.698535524,
                                                                    "ymax":4239488.369818687,
                                                                    "spatialReference":{"wkid":102100}
                                                                    }
                                                        )
            >>> type(update_tiles)
            <Dictionary>
        """
        if self._gis._portal.is_arcgisonline:
            if self._gis.version >= [10, 3]:
                url = "%s/update" % self._url
            else:
                url = "%s/updateTiles" % self._url

            params = {
                "f": "json",
                "mergeBundle": merge,
                "replaceTiles": replace,
            }
            if levels:
                if isinstance(levels, list):
                    levels = ",".join(str(e) for e in levels)
                params["levels"] = levels
            if extent:
                if isinstance(extent, dict):
                    extent2 = "{},{},{},{}".format(
                        extent["xmin"],
                        extent["ymin"],
                        extent["xmax"],
                        extent["ymax"],
                    )
                    extent = extent2
                params["extent"] = extent
            return self._con.post(url, params)
        return None

    # ----------------------------------------------------------------------
    @property
    def rerun_job(self, job_id: str, code: str):
        """
        The ``rerun_job`` operation supports re-running a canceled job from a
        hosted map service. The result of this operation is a response
        indicating success or failure with error code and description.

        ===============     ====================================================
        **Parameter**        **Description**
        ---------------     ----------------------------------------------------
        job_id              required string, job to reprocess
        ---------------     ----------------------------------------------------
        code                required string, parameter used to re-run a given
                            jobs with a specific error
                            code: ``ALL | ERROR | CANCELED``
        ===============     ====================================================

        :return:
           A boolean or dictionary
        """
        url = self._url + "/jobs/%s/rerun" % job_id
        params = {"f": "json", "rerun": code}
        return self._con.post(url, params)

    # ----------------------------------------------------------------------
    def edit_tile_service(
        self,
        service_definition: Optional[str] = None,
        min_scale: Optional[float] = None,
        max_scale: Optional[float] = None,
        source_item_id: Optional[str] = None,
        export_tiles_allowed: bool = False,
        max_export_tile_count: float = 100000,
    ):
        """
        The ``edit_tile_service`` operation updates a Tile Service's properties.

        =====================     ======================================================
        **Parameter**              **Description**
        ---------------------     ------------------------------------------------------
        service_definition        Required String. Updates a service definition.
        ---------------------     ------------------------------------------------------
        min_scale                 Required float. Sets the services minimum scale for
                                  caching.
        ---------------------     ------------------------------------------------------
        max_scale                 Required float. Sets the services maximum scale for
                                  caching.
        ---------------------     ------------------------------------------------------
        source_item_id            Required String. The Source Item ID is the
                                  GeoWarehouse Item ID of the map service
        ---------------------     ------------------------------------------------------
        export_tiles_allowed      Required boolean. ``exports_tiles_allowed`` sets the
                                  value to let users export tiles
        ---------------------     ------------------------------------------------------
        max_export_tile_count     Optional float. ``max_export_tile_count`` sets the
                                  maximum amount of tiles to be exported from a single
                                  call.

                                  .. note::
                                      The default value is 100000.
        =====================     ======================================================

        .. code-block:: python

            # USAGE EXAMPLE

            >>> from arcgis.layers import MapImageLayer
            >>> from arcgis.gis import GIS

            # connect to your GIS and get the web map item
            >>> gis = GIS(url, username, password)
            >>> map_image_layer = MapImageLayer("<url>", gis)
            >>> mil_manager = map_image_layer.manager
            >>> mil_manager.edit_tile_service(service_definition = "updated service definition",
                                              min_scale = 50,
                                              max_scale = 100,
                                              source_item_id = "geowarehouse_item_id",
                                              export_tiles_allowed = True,
                                              max_Export_Tile_Count = 10000
                                             )
        """
        params = {
            "f": "json",
        }
        if not service_definition is None:
            params["serviceDefinition"] = service_definition
        if not min_scale is None:
            params["minScale"] = float(min_scale)
        if not max_scale is None:
            params["maxScale"] = float(max_scale)
        if not source_item_id is None:
            params["sourceItemId"] = source_item_id
        if not export_tiles_allowed is None:
            params["exportTilesAllowed"] = export_tiles_allowed
        if not max_export_tile_count is None:
            params["maxExportTileCount"] = int(max_export_tile_count)
        url = self._url + "/edit"
        return self._con.post(url, params)

    # ----------------------------------------------------------------------
    def delete_tiles(self, levels: str, extent: Optional[dict[str, int]] = None):
        """
        The ``delete_tiles`` method deletes tiles from the current cache.

        ===============     ====================================================
        **Parameter**        **Description**
        ---------------     ----------------------------------------------------
        levels              Required string, The level to delete.
                            Example, 0-5,10,11-20 or 1,2,3 or 0-5
        ---------------     ----------------------------------------------------
        extent              Optional dictionary,  If specified, the tiles within
                            this extent will be deleted or will be deleted based
                            on the service's full extent.
        ===============     ====================================================

        :return:
           A dictionary

        .. code-block:: python

            # USAGE EXAMPLE

            >>> from arcgis.layers import MapImageLayer
            >>> from arcgis.gis import GIS

            # connect to your GIS and get the web map item
            >>> gis = GIS(url, username, password)
            >>> map_image_layer = MapImageLayer("<url>", gis)
            >>> mil_manager = map_image_layer.manager
            >>> deleted_tiles = mil_manager.delete_tiles(levels = "11-20",
                                                  extent = {"xmin":6224324.092137296,
                                                            "ymin":487347.5253569535,
                                                            "xmax":11473407.698535524,
                                                            "ymax":4239488.369818687,
                                                            "spatialReference":{"wkid":102100}
                                                            }
                                                  )
            >>> type(deleted_tiles)
            <Dictionary>
        """
        params = {
            "f": "json",
            "levels": levels,
        }
        if extent:
            params["extent"] = extent
        url = self._url + "/deleteTiles"
        return self._con.post(url, params)


###########################################################################
@deprecated(
    deprecated_in="2.4.0",
    removed_in="2.4.2",
    details="Use the MapImageLayer class found in `arcgis.layers.MapImageLayer` instead.",
)
class MapImageLayer(arcgis.gis.Layer):
    """
    The ``MapImageLayer`` allows you to display and analyze data from sublayers defined in a map service,
    exporting images instead of features. Map service images are dynamically generated on the server based on a request,
    which includes an LOD (level of detail), a bounding box, dpi, spatial reference and other options.
    The exported image is of the entire map extent specified.

    .. note::
        ``MapImageLayer`` does not display tiled images. To display tiled map service layers, see ``TileLayer``.
    """

    def __init__(self, url, gis=None):
        """
        .. Creates a map image layer given a URL. The URL will typically look like the following.

            https://<hostname>/arcgis/rest/services/<service-name>/MapServer

        :param url: the layer location
        :param gis: the GIS to which this layer belongs
        """
        super(MapImageLayer, self).__init__(url, gis)

        self._populate_layers()
        self._admin = None
        try:
            from arcgis.gis.server._service._adminfactory import (
                AdminServiceGen,
            )

            self.service = AdminServiceGen(service=self, gis=gis)
        except:
            pass

    @classmethod
    def fromitem(cls, item: _gis.Item):
        if not item.type == "Map Service":
            raise TypeError("item must be a type of Map Service, not " + item.type)
        if item._gis._use_private_url_only:
            url: str = _get_item_url(item=item)
        else:
            url: str = _validate_url(item.url, item._gis)
        return cls(url, item._gis)

    @property
    def _lyr_dict(self):
        url = self.url

        if "lods" in self.properties:
            lyr_dict = {"type": "ArcGISTiledMapServiceLayer", "url": url}

        else:
            lyr_dict = {"type": type(self).__name__, "url": url}

        if self._token is not None:
            lyr_dict["serviceToken"] = self._token or self._con.token

        if self.filter is not None:
            lyr_dict["filter"] = self.filter
        if self._time_filter is not None:
            lyr_dict["time"] = self._time_filter
        return lyr_dict

    @property
    def _lyr_json(self):
        url = self.url
        if self._token is not None:
            token = self._token or self._con.token
            url += "?token=" + token

        if "lods" in self.properties:
            lyr_dict = {"type": "ArcGISTiledMapServiceLayer", "url": url}
        else:
            lyr_dict = {"type": type(self).__name__, "url": url}

        if self.filter is not None:
            lyr_dict["options"] = json.dumps({"definition_expression": self.filter})
        if self._time_filter is not None:
            lyr_dict["time"] = self._time_filter
        return lyr_dict

    def _populate_layers(self):
        layers = []
        tables = []
        if "layers" in self.properties and self.properties.layers:
            for lyr in self.properties.layers:
                if "subLayerIds" in lyr and lyr.subLayerIds is not None:  # Group Layer
                    lyr = arcgis.gis.Layer(self.url + "/" + str(lyr.id), self._gis)
                else:
                    lyr = arcgis.layers._msl.MapServiceLayer(
                        self.url + "/" + str(lyr.id), self._gis
                    )
                layers.append(lyr)
        if "tables" in self.properties and self.properties.tables:
            for lyr in self.properties.tables:
                lyr = arcgis.layers._msl.MapServiceLayer(
                    self.url + "/" + str(lyr.id), self._gis, self
                )
                tables.append(lyr)

        self.layers = layers
        self.tables = tables

    def _str_replace(self, mystring, rd):
        """Replaces a value based on a key/value pair where the
        key is the text to replace and the value is the new value.

        The find/replace is case insensitive.

        """
        import re

        patternDict = {}
        for key, value in rd.items():
            pattern = re.compile(re.escape(key), re.IGNORECASE)
            patternDict[value] = pattern
        for key in patternDict:
            regex_obj = patternDict[key]
            mystring = regex_obj.sub(key, mystring)
        return mystring

    @property
    def manager(self):
        """
        The ``manager`` property returns an instance of :class:`~arcgis.layers.MapImageLayerManager` class
        for ArcGIS Online and :class:`~arcgis.layers.EnterpriseMapImageLayerManager` class for ArcGIS Enterprise
        which provides methods and properties for administering this service.
        """
        if self._admin is None:
            if self._gis._portal.is_arcgisonline:
                rd = {"/rest/services/": "/rest/admin/services/"}
                adminURL = self._str_replace(self._url, rd)
                if adminURL.split("/")[-1].isdigit():
                    adminURL = adminURL.replace(f'/{adminURL.split("/")[-1]}', "")
                self._admin = MapImageLayerManager(adminURL, self._gis, self)
            else:
                rd = {"/rest/": "/admin/", "/MapServer": ".MapServer"}
                adminURL = self._str_replace(self._url, rd)
                if adminURL.split("/")[-1].isdigit():
                    adminURL = adminURL.replace(f'/{adminURL.split("/")[-1]}', "")
                self._admin = EnterpriseMapImageLayerManager(adminURL, self._gis, self)
        return self._admin

    # ----------------------------------------------------------------------
    def create_dynamic_layer(self, layer: dict[str, Any]):
        """
        The ``create_dynamic_layer`` method creates a dynamic layer.
        A dynamic layer / table represents a single layer / table of a map service published by ArcGIS Server
        or of a registered workspace. This resource is supported only when the map image layer
        supports dynamic layers, as indicated by ``supportsDynamicLayers`` on
        the map image layer properties.

        =================     ====================================================================
        **Parameter**          **Description**
        -----------------     --------------------------------------------------------------------
        layer                 Required dict.  Dynamic layer/table source definition.

                              Syntax:

                                  | {
                                  |   "id": <layerOrTableId>,
                                  |   "source": <layer source>, //required
                                  |   "definitionExpression": "<definitionExpression>",
                                  |   "drawingInfo":
                                  |   {
                                  |     "renderer": <renderer>,
                                  |     "transparency": <transparency>,
                                  |     "scaleSymbols": <true,false>,
                                  |     "showLabels": <true,false>,
                                  |     "labelingInfo": <labeling info>
                                  |   },
                                  |   "layerTimeOptions": //supported only for time enabled map layers
                                  |   {
                                  |     "useTime" : <true,false>,
                                  |     "timeDataCumulative" : <true,false>,
                                  |     "timeOffset" : <timeOffset>,
                                  |     "timeOffsetUnits" : "<esriTimeUnitsCenturies,esriTimeUnitsDays,
                                  |                       esriTimeUnitsDecades,esriTimeUnitsHours,
                                  |                       esriTimeUnitsMilliseconds,esriTimeUnitsMinutes,
                                  |                       esriTimeUnitsMonths,esriTimeUnitsSeconds,
                                  |                       esriTimeUnitsWeeks,esriTimeUnitsYears |
                                  |                       esriTimeUnitsUnknown>"
                                  |   }
                                  | }
        =================     ====================================================================

        :return:
            :class:`~arcgis.features.FeatureLayer` or None (if not enabled)

        .. code-block:: python

            # USAGE EXAMPLE

            >>> from arcgis.layers import MapImageLayer
            >>> from arcgis.gis import GIS

            # connect to your GIS and get the web map item
            >>> gis = GIS(url, username, password)

            >>> map_image_item = gis.content.get("2aaddab96684405880d27f5261125061")
            >>> layer_to_add ={
                                "id": <layerId>,
                                "source": <layer source>
                                "definitionExpression": "<definitionExpression>",
                                "drawingInfo":
                                {
                                  "renderer": <renderer>,
                                  "transparency": <transparency>,
                                  "scaleSymbols": <true>,
                                  "showLabels": <true>,
                                  "labelingInfo": <labeling info>
                                },
                                "layerTimeOptions":
                                {
                                  "useTime" : <true,false>,
                                  "timeDataCumulative" : <true>,
                                  "timeOffset" : <timeOffset>,
                                  "timeOffsetUnits" : "<esriTimeUnitsCenturies>"
                                }
                              }
            >>> new_layer = map_image_item.create_dynamic_layer(layer= layer_to_add)
            >>>type(new_layer)
            <arcgis.features.FeatureLayer>

        """
        if (
            "supportsDynamicLayers" in self.properties
            and self.properties["supportsDynamicLayers"]
        ):
            from urllib.parse import urlencode

            url = "%s/dynamicLayer" % self._url
            d = urlencode(layer)
            url += "?layer=%s" % d
            return _arcgis_features.FeatureLayer(
                url=url, gis=self._gis, dynamic_layer=layer
            )
        return None

    # ----------------------------------------------------------------------
    @property
    def kml(self):
        """
        The ``kml`` method retrieves the KML file for the layer.

        :return:
            A KML file
        """
        url = "{url}/kml/mapImage.kmz".format(url=self._url)
        return self._con.get(
            url,
            {"f": "json"},
            file_name="mapImage.kmz",
            out_folder=tempfile.gettempdir(),
        )

    # ----------------------------------------------------------------------
    @property
    def item_info(self):
        """
        The ``item_info`` method retrieves the service's item's information.

        :return:
            A dictionary
        """
        url = "{url}/info/iteminfo".format(url=self._url)
        params = {"f": "json"}
        return self._con.get(url, params)

    # ----------------------------------------------------------------------
    @property
    def legend(self):
        """
        The ``legend`` property represents a map service's legend. It returns
        the legend information for all layers in the service. Each layer's
        legend information includes the symbol images and labels for each
        symbol. Each symbol is an image of size 20 x 20 pixels at 96 DPI.
        Additional information for each layer such as the layer ID, name,
        and min and max scales are also included.

        .. note::
            The legend symbols include the base64 encoded imageData as well as
            a url that could be used to retrieve the image from the server.

        :returns:
            Dictionary of legend information
        """
        url = "%s/legend" % self._url
        return self._con.get(path=url, params={"f": "json"})

    # ----------------------------------------------------------------------
    @property
    def metadata(self):
        """
        The ``metadata`` property retrieves the service's XML metadata file

        :return:
            An XML metadata file
        """
        url = "{url}/info/metadata".format(url=self._url)
        params = {"f": "json"}
        resp = self._con.get(url, params, return_raw_response=True)
        return resp.text

    # ----------------------------------------------------------------------
    def thumbnail(self, out_path: Optional[str] = None):
        """
        The ``thumbnail`` method retrieves the thumbnail.

        .. note::
            If a thumbnail is present, this operation will download the image to local disk.

        :return:
            A path to the downloaded thumbnail, or None.
        """
        if out_path is None:
            out_path = tempfile.gettempdir()
        url = "{url}/info/thumbnail".format(url=self._url)
        params = {"f": "json"}
        if out_path is None:
            out_path = tempfile.gettempdir()
        return self._con.get(
            url, params, out_folder=out_path, file_name="thumbnail.png"
        )

    # ----------------------------------------------------------------------
    def identify(
        self,
        geometry: Union[_geometry.Geometry, list],
        map_extent: str,
        image_display: Optional[str] = None,
        geometry_type: str = "Point",
        sr: Optional[Union[dict[str, Any], str, _geometry.SpatialReference]] = None,
        layer_defs: Optional[dict[str, Any]] = None,
        time_value: Optional[Union[list[str], str]] = None,
        time_options: Optional[dict] = None,
        layers: str = "all",
        tolerance: Optional[int] = None,
        return_geometry: bool = True,
        max_offset: Optional[int] = None,
        precision: int = 4,
        dynamic_layers: Optional[dict[str, Any]] = None,
        return_z: bool = False,
        return_m: bool = False,
        gdb_version: Optional[str] = None,
        return_unformatted: bool = False,
        return_field_name: bool = False,
        transformations: Optional[Union[list[dict], list[int]]] = None,
        map_range_values: Optional[list[dict[str, Any]]] = None,
        layer_range_values: Optional[dict[str, Any]] = None,
        layer_parameters: Optional[list[dict[str, Any]]] = None,
        **kwargs,
    ):
        """
        The ``identify`` operation is performed on a map service resource
        to discover features at a geographic location. The result of this
        operation is an identify results resource.

        .. note::
            Each identified result includes its ``name``, ``layer ID``, ``layer name``, ``geometry``,
            ``geometry type``, and other attributes of that result as name-value pairs.

        ==================     ====================================================================
        **Parameter**           **Description**
        ------------------     --------------------------------------------------------------------
        geometry               Required :class:`~arcgis.geometry.Geometry` or list. The geometry
                               to identify on. The type of the geometry is specified by the
                               `geometryType` parameter. The structure of the geometries is same as
                               the structure of the JSON geometry objects returned by the API (See
                               `Geometry Objects <https://developers.arcgis.com/documentation/common-data-types/geometry-objects.htm>`_).
                               In addition to the JSON structures, for points and envelopes, you
                               can specify the geometries with a simpler comma-separated syntax.
        ------------------     --------------------------------------------------------------------
        geometry_type          Required string.The type of geometry specified by the geometry
                               parameter. The geometry type could be a point, line, polygon, or an
                               envelope.
                               Values:
                                    "Point" | "Multipoint" | "Polyline" | "Polygon" | "Envelope"
        ------------------     --------------------------------------------------------------------
        map_extent             Required string. The extent or bounding box of the map currently
                               being viewed.
        ------------------     --------------------------------------------------------------------
        sr                     Optional dict, string, or SpatialReference. The well-known ID of the
                               spatial reference of the input and output geometries as well as the
                               map_extent. If sr is not specified, the geometry and the map_extent
                               are assumed to be in the spatial reference of the map, and the
                               output geometries are also in the spatial reference of the map.
        ------------------     --------------------------------------------------------------------
        layer_defs             Optional dict. Allows you to filter the features of individual
                               layers in the exported map by specifying definition expressions for
                               those layers. Definition expression for a layer that is
                               published with the service will be always honored.
        ------------------     --------------------------------------------------------------------
        time_value             Optional list. The time instant or the time extent of the features
                               to be identified.
        ------------------     --------------------------------------------------------------------
        time_options           Optional dict. The time options per layer. Users can indicate
                               whether or not the layer should use the time extent specified by the
                               time parameter or not, whether to draw the layer features
                               cumulatively or not and the time offsets for the layer.
        ------------------     --------------------------------------------------------------------
        layers                 Optional string. The layers to perform the identify operation on.
                               There are three ways to specify which layers to identify on:

                               - ``top``: Only the top-most layer at the specified location.
                               - ``visible``: All visible layers at the specified location.
                               - ``all``: All layers at the specified location.
        ------------------     --------------------------------------------------------------------
        tolerance              Optional integer. The distance in screen pixels from the specified
                               geometry within which the ``identify`` operation should be performed. The value for
                               the tolerance is an integer.
        ------------------     --------------------------------------------------------------------
        image_display          Optional string. The screen image display parameters (width, height,
                               and DPI) of the map being currently viewed. The mapExtent and the
                               image_display parameters are used by the server to determine the
                               layers visible in the current extent. They are also used to
                               calculate the distance on the map to search based on the tolerance
                               in screen pixels.

                               Syntax:

                                    <width>, <height>, <dpi>
        ------------------     --------------------------------------------------------------------
        return_geometry        Optional boolean. If true, the resultset will include the geometries
                               associated with each result. The default is true.
        ------------------     --------------------------------------------------------------------
        max_offset             Optional integer. This option can be used to specify the maximum
                               allowable offset to be used for generalizing geometries returned by
                               the identify operation.
        ------------------     --------------------------------------------------------------------
        precision              Optional integer. This option can be used to specify the number of
                               decimal places in the response geometries returned by the identify
                               operation. This applies to X and Y values only (not m or z-values).
        ------------------     --------------------------------------------------------------------
        dynamic_layers         Optional dict. Use dynamicLayers property to reorder layers and
                               change the layer data source. dynamicLayers can also be used to add
                               new layer that was not defined in the map used to create the map
                               service. The new layer should have its source pointing to one of the
                               registered workspaces that was defined at the time the map service
                               was created.
                               The order of dynamicLayers array defines the layer drawing order.
                               The first element of the dynamicLayers is stacked on top of all
                               other layers. When defining a dynamic layer, source is required.
        ------------------     --------------------------------------------------------------------
        return_z               Optional boolean. If true, Z values will be included in the results
                               if the features have Z values. Otherwise, Z values are not returned.
                               The default is false.
        ------------------     --------------------------------------------------------------------
        return_m               Optional boolean.If true, M values will be included in the results
                               if the features have M values. Otherwise, M values are not returned.
                               The default is false.
        ------------------     --------------------------------------------------------------------
        gdb_version            Optional string. Switch map layers to point to an alternate
                               geodatabase version.
        ------------------     --------------------------------------------------------------------
        return_unformatted     Optional boolean. If true, the values in the result will not be
                               formatted i.e. numbers will be returned as is and dates will be
                               returned as epoch values. The default is False.
        ------------------     --------------------------------------------------------------------
        return_field_name      Optional boolean. Default is False. If true, field names will be
                               returned instead of field aliases.
        ------------------     --------------------------------------------------------------------
        transformations        Optional list. Use this parameter to apply one or more datum
                               transformations to the map when sr is different than the map
                               service's spatial reference. It is an array of transformation
                               elements.
                               Transformations specified here are used to project features from
                               layers within a map service to sr.
        ------------------     --------------------------------------------------------------------
        map_range_values       Optional list of dictionary(ies). Allows for the filtering features in
                               the exported map from all layer that are within the specified range
                               instant or extent.
        ------------------     --------------------------------------------------------------------
        layer_range_values     Optional Dictionary. Allows for the filtering of features
                               for each individual layer that are within the specified range instant or
                               extent.
        ------------------     --------------------------------------------------------------------
        layer_parameters       Optional list of dictionary(ies). Allows for the filtering of the
                               features of individual layers in the exported map by specifying value(s)
                               to an array of pre-authored parameterized filters for those layers. When
                               value is not specified for any parameter in a request, the default
                               value, that is assigned during authoring time, gets used instead.
        ==================     ====================================================================

        :return:
            A dictionary

        .. code-block:: python

            # USAGE EXAMPLE

            >>> from arcgis.layers import MapImageLayer
            >>> from arcgis.gis import GIS

            # connect to your GIS and get the web map item
            >>> gis = GIS(url, username, password)

            >>> map_image_item = gis.content.get("2aaddab96684405880d27f5261125061")
            >>> identified = map_image_item.identify(geometry = geom1,
                                        geometry_type = "Multipoint",
                                        image_display = "width",
                                        return_geometry =True,
                                        return_z = True,
                                        retrun_m = True,
                                        return_field_name = True,
                                        )
            >>> type(identified)
            <Dictionary>
        """

        if geometry_type.find("esriGeometry") == -1:
            geometry_type = "esriGeometry" + geometry_type
        if sr is None:
            sr = kwargs.pop("sr", None)
        if layer_defs is None:
            layer_defs = kwargs.pop("layerDefs", None)
        if time_value is None:
            time_value = kwargs.pop("layerTimeOptions", None)
        if return_geometry is None:
            return_geometry = kwargs.pop("returnGeometry", True)
        if return_m is None:
            return_m = kwargs.pop("returnM", False)
        if return_z is None:
            return_z = kwargs.pop("returnZ", False)
        if max_offset is None:
            max_offset = kwargs.pop("maxAllowableOffset", None)
        if precision is None:
            precision = kwargs.pop("geometryPrecision", None)
        if dynamic_layers is None:
            dynamic_layers = kwargs.pop("dynamicLayers", None)
        if gdb_version is None:
            gdb_version = kwargs.pop("gdbVersion", None)

        params = {
            "f": "json",
            "geometry": geometry,
            "geometryType": geometry_type,
            "tolerance": tolerance,
            "mapExtent": map_extent,
            "imageDisplay": image_display,
        }
        if sr:
            params["sr"] = sr
        if layer_defs:
            params["layerDefs"] = layer_defs
        if time_value:
            params["time"] = time_value
        if time_options:
            params["layerTimeOptions"] = time_options
        if layers:
            params["layers"] = layers
        if tolerance:
            params["tolerance"] = tolerance
        if return_geometry is not None:
            params["returnGeometry"] = return_geometry
        if max_offset:
            params["maxAllowableOffset"] = max_offset
        if precision:
            params["geometryPrecision"] = precision
        if dynamic_layers:
            params["dynamicLayers"] = dynamic_layers
        if return_m is not None:
            params["returnM"] = return_m
        if return_z is not None:
            params["returnZ"] = return_z
        if gdb_version:
            params["gdbVersion"] = gdb_version
        if return_unformatted is not None:
            params["returnUnformattedValues"] = return_unformatted
        if return_field_name is not None:
            params["returnFieldName"] = return_field_name
        if transformations:
            params["datumTransformations"] = transformations
        if map_range_values:
            params["mapRangeValues"] = map_range_values
        if layer_range_values:
            params["layerRangeValues"] = layer_range_values
        if layer_parameters:
            params["layerParameterValues"] = layer_parameters
        identifyURL = "{url}/identify".format(url=self._url)
        return self._con.post(identifyURL, params)

    # ----------------------------------------------------------------------
    def find(
        self,
        search_text: str,
        layers: str,
        contains: bool = True,
        search_fields: Optional[str] = None,
        sr: Optional[Union[dict[str, Any], str, _geometry.SpatialReference]] = None,
        layer_defs: Optional[dict[str, Any]] = None,
        return_geometry: bool = True,
        max_offset: Optional[int] = None,
        precision: Optional[int] = None,
        dynamic_layers: Optional[dict[str, Any]] = None,
        return_z: bool = False,
        return_m: bool = False,
        gdb_version: Optional[str] = None,
        return_unformatted: bool = False,
        return_field_name: bool = False,
        transformations: Optional[Union[list[int], list[dict[str, Any]]]] = None,
        map_range_values: Optional[list[dict[str, Any]]] = None,
        layer_range_values: Optional[dict[str, Any]] = None,
        layer_parameters: Optional[list[dict[str, Any]]] = None,
        **kwargs,
    ):
        """
        The ``find`` method performs the map service ``find`` operation.

        ==================     ====================================================================
        **Parameter**           **Description**
        ------------------     --------------------------------------------------------------------
        search_text            Required string.The search string. This is the text that is searched
                               across the layers and fields the user specifies.
        ------------------     --------------------------------------------------------------------
        layers                 Optional string. The layers to perform the identify operation on.
                               There are three ways to specify which layers to identify on:

                               - top: Only the top-most layer at the specified location.
                               - visible: All visible layers at the specified location.
                               - all: All layers at the specified location.
        ------------------     --------------------------------------------------------------------
        contains               Optional boolean. If false, the operation searches for an exact
                               match of the search_text string. An exact match is case sensitive.
                               Otherwise, it searches for a value that contains the search_text
                               provided. This search is not case sensitive. The default is true.
        ------------------     --------------------------------------------------------------------
        search_fields          Optional string. List of field names to look in.
        ------------------     --------------------------------------------------------------------
        sr                     Optional dict, string, or SpatialReference. The well-known ID of the
                               spatial reference of the input and output geometries as well as the
                               map_extent. If sr is not specified, the geometry and the map_extent
                               are assumed to be in the spatial reference of the map, and the
                               output geometries are also in the spatial reference of the map.
        ------------------     --------------------------------------------------------------------
        layer_defs             Optional dict. Allows you to filter the features of individual
                               layers in the exported map by specifying definition expressions for
                               those layers. Definition expression for a layer that is
                               published with the service will be always honored.
        ------------------     --------------------------------------------------------------------
        return_geometry        Optional boolean. If true, the resultset will include the geometries
                               associated with each result. The default is true.
        ------------------     --------------------------------------------------------------------
        max_offset             Optional integer. This option can be used to specify the maximum
                               allowable offset to be used for generalizing geometries returned by
                               the identify operation.
        ------------------     --------------------------------------------------------------------
        precision              Optional integer. This option can be used to specify the number of
                               decimal places in the response geometries returned by the identify
                               operation. This applies to X and Y values only (not m or z-values).
        ------------------     --------------------------------------------------------------------
        dynamic_layers         Optional dict. Use dynamicLayers property to reorder layers and
                               change the layer data source. dynamicLayers can also be used to add
                               new layer that was not defined in the map used to create the map
                               service. The new layer should have its source pointing to one of the
                               registered workspaces that was defined at the time the map service
                               was created.
                               The order of dynamicLayers array defines the layer drawing order.
                               The first element of the dynamicLayers is stacked on top of all
                               other layers. When defining a dynamic layer, source is required.
        ------------------     --------------------------------------------------------------------
        return_z               Optional boolean. If true, Z values will be included in the results
                               if the features have Z values. Otherwise, Z values are not returned.
                               The default is false.
        ------------------     --------------------------------------------------------------------
        return_m               Optional boolean.If true, M values will be included in the results
                               if the features have M values. Otherwise, M values are not returned.
                               The default is false.
        ------------------     --------------------------------------------------------------------
        gdb_version            Optional string. Switch map layers to point to an alternate
                               geodatabase version.
        ------------------     --------------------------------------------------------------------
        return_unformatted     Optional boolean. If true, the values in the result will not be
                               formatted i.e. numbers will be returned as is and dates will be
                               returned as epoch values.
        ------------------     --------------------------------------------------------------------
        return_field_name      Optional boolean. If true, field names will be returned instead of
                               field aliases.
        ------------------     --------------------------------------------------------------------
        transformations        Optional list. Use this parameter to apply one or more datum
                               transformations to the map when sr is different from the map
                               service's spatial reference. It is an array of transformation
                               elements.
        ------------------     --------------------------------------------------------------------
        map_range_values       Optional list. Allows you to filter features in the exported map
                               from all layer that are within the specified range instant or
                               extent.
        ------------------     --------------------------------------------------------------------
        layer_range_values     Optional dictionary. Allows you to filter features for each
                               individual layer that are within the specified range instant or
                               extent. Note: Check range infos at the layer resources for the
                               available ranges.
        ------------------     --------------------------------------------------------------------
        layer_parameters       Optional list. Allows you to filter the features of individual
                               layers in the exported map by specifying value(s) to an array of
                               pre-authored parameterized filters for those layers. When value is
                               not specified for any parameter in a request, the default value,
                               that is assigned during authoring time, gets used instead.
        ==================     ====================================================================

        :return:
            A dictionary

        .. code-block:: python

            # USAGE EXAMPLE

            >>> from arcgis.layers import MapImageLayer
            >>> from arcgis.gis import GIS

            # connect to your GIS and get the web map item
            >>> gis = GIS(url, username, password)

            >>> map_image_item = gis.content.get("2aaddab96684405880d27f5261125061")
            >>> search_results = map_image_item.find(search_text = "Hurricane Data",
                                    contains = True,
                                    layers = "top",
                                    return_geometry = False,
                                    max_offset = 100,
                                    return_z = True,
                                    return_m = False,
                                    )
            >>> type(search_results)
            <Dictionary>

        """
        url = "{url}/find".format(url=self._url)
        params = {
            "f": "json",
            "searchText": search_text,
            "contains": contains,
        }
        if search_fields:
            params["searchFields"] = search_fields
        if sr:
            params["sr"] = sr
        if layer_defs:
            params["layerDefs"] = layer_defs
        if return_geometry is not None:
            params["returnGeometry"] = return_geometry
        if max_offset:
            params["maxAllowableOffset"] = max_offset
        if precision:
            params["geometryPrecision"] = precision
        if dynamic_layers:
            params["dynamicLayers"] = dynamic_layers
        if return_z is not None:
            params["returnZ"] = return_z
        if return_m is not None:
            params["returnM"] = return_m
        if gdb_version:
            params["gdbVersion"] = gdb_version
        if layers:
            params["layers"] = layers
        if return_unformatted is not None:
            params["returnUnformattedValues"] = return_unformatted
        if return_field_name is not None:
            params["returnFieldName"] = return_field_name
        if transformations:
            params["datumTransformations"] = transformations
        if map_range_values:
            params["mapRangeValues"] = map_range_values
        if layer_range_values:
            params["layerRangeValues"] = layer_range_values
        if layer_parameters:
            params["layerParameterValues"] = layer_parameters
        if len(kwargs) > 0:
            for k, v in kwargs.items():
                params[k] = v
        res = self._con.post(
            path=url,
            postdata=params,
        )
        return res

    # ----------------------------------------------------------------------
    def generate_kml(
        self,
        save_location: str,
        name: str,
        layers: str,
        options: str = "composite",
    ):
        """
        The ``generate_Kml`` operation is performed on a map service resource.
        The result of this operation is a KML document wrapped in a KMZ
        file.

        .. note::
            The document contains a network link to the KML Service
            endpoint with properties and parameters you specify.

        =================     ====================================================================
        **Parameter**          **Description**
        -----------------     --------------------------------------------------------------------
        save_location         Required string. Save folder.
        -----------------     --------------------------------------------------------------------
        name                  Required string. The name of the resulting KML document.
                              This is the name that appears in the Places panel of Google Earth.
        -----------------     --------------------------------------------------------------------
        layers                Required string. the layers to perform the generateKML operation on.
                              The layers are specified as a comma-separated list of layer ids.
        -----------------     --------------------------------------------------------------------
        options               Required string. The layer drawing options. Based on the option
                              chosen, the layers are drawn as one composite image, as separate
                              images, or as vectors. When the KML capability is enabled, the
                              ArcGIS Server administrator has the option of setting the layer
                              operations allowed. If vectors are not allowed, then the caller will
                              not be able to get vectors. Instead, the caller receives a single
                              composite image.
                              values: composite, separateImage, nonComposite
        =================     ====================================================================

        :return:
            A string to the file path

        """
        kmlURL = self._url + "/generateKml"
        params = {
            "f": "json",
            "docName": name,
            "layers": layers,
            "layerOptions": options,
        }
        return self._con.get(
            kmlURL,
            params,
            out_folder=save_location,
        )

    # ----------------------------------------------------------------------
    def export_map(
        self,
        bbox: str,
        bbox_sr: Optional[int] = None,
        size: str = "600,550",
        dpi: int = 200,
        image_sr: Optional[int] = None,
        image_format: int = "png",
        layer_defs: Optional[dict[str, Any]] = None,
        layers: Optional[str] = None,
        transparent: bool = False,
        time_value: Optional[Union[list[int], list[datetime.datetime]]] = None,
        time_options: Optional[dict[str, Any]] = None,
        dynamic_layers: Optional[dict[str, Any]] = None,
        gdb_version: Optional[str] = None,
        scale: Optional[float] = None,
        rotation: Optional[float] = None,
        transformation: Optional[Union[list[int], list[dict[str, Any]]]] = None,
        map_range_values: Optional[list[dict[str, Any]]] = None,
        layer_range_values: Optional[list[dict[str, Any]]] = None,
        layer_parameter: Optional[list[dict[str, Any]]] = None,
        f: str = "json",
        save_folder: Optional[str] = None,
        save_file: Optional[str] = None,
        **kwargs,
    ):
        """
        The ``export_map`` operation is performed on a map service resource.
        The result of this operation is a map image resource. This
        resource provides information about the exported map image such
        as its URL, its width and height, extent and scale.

        ==================     ====================================================================
        **Parameter**           **Description**
        ------------------     --------------------------------------------------------------------
        bbox                   Required string. The extent (bounding box) of the exported image.
                               Unless the bbox_sr parameter has been specified, the bbox is assumed
                               to be in the spatial reference of the map.
        ------------------     --------------------------------------------------------------------
        bbox_sr                Optional integer, :class:`~arcgis.geometry.SpatialReference`. The spatial reference of the bbox.
        ------------------     --------------------------------------------------------------------
        size                   Optional string. size - size of image in pixels
        ------------------     --------------------------------------------------------------------
        dpi                    Optional integer. dots per inch
        ------------------     --------------------------------------------------------------------
        image_sr               Optional integer, :class:`~arcgis.geometry.SpatialReference`.
                               The spatial reference of the output image.
        ------------------     --------------------------------------------------------------------
        image_format           Optional string. The format of the exported image.
                               The default format is .png.
                               Values:
                                    png | png8 | png24 | jpg | pdf | bmp | gif | svg | svgz | emf | ps | png32
        ------------------     --------------------------------------------------------------------
        layer_defs             Optional dict. Allows you to filter the features of individual
                               layers in the exported map by specifying definition expressions for
                               those layers. Definition expression for a layer that is
                               published with the service will be always honored.
        ------------------     --------------------------------------------------------------------
        layers                 Optional string. Determines which layers appear on the exported map.
                               There are four ways to specify which layers are shown:

                               ``show``: Only the layers specified in this list will be exported.

                               ``hide``: All layers except those specified in this list will be exported.

                               ``include``: In addition to the layers exported by default, the layers specified in this list will be exported.

                               ``exclude``: The layers exported by default excluding those specified in this list will be exported.
        ------------------     --------------------------------------------------------------------
        transparent            Optional boolean. If true, the image will be exported with the
                               background color of the map set as its transparent color. The
                               default is false.

                               .. note::
                                Only the .png and .gif formats support
                                transparency.
        ------------------     --------------------------------------------------------------------
        time_value             Optional list. The time instant or the time extent of the features
                               to be identified.
        ------------------     --------------------------------------------------------------------
        time_options           Optional dict. The time options per layer. Users can indicate
                               whether or not the layer should use the time extent specified by the
                               time parameter or not, whether to draw the layer features
                               cumulatively or not and the time offsets for the layer.
        ------------------     --------------------------------------------------------------------
        dynamic_layers         Optional dict. Use dynamicLayers property to reorder layers and
                               change the layer data source. dynamicLayers can also be used to add
                               new layer that was not defined in the map used to create the map
                               service. The new layer should have its source pointing to one of the
                               registered workspaces that was defined at the time the map service
                               was created.
                               The order of dynamicLayers array defines the layer drawing order.
                               The first element of the dynamicLayers is stacked on top of all
                               other layers. When defining a dynamic layer, source is required.
        ------------------     --------------------------------------------------------------------
        gdb_version            Optional string. Switch map layers to point to an alternate
                               geodatabase version.
        ------------------     --------------------------------------------------------------------
        scale                  Optional float. Use this parameter to export a map image at a
                               specific map scale, with the map centered around the center of the
                               specified bounding box (bbox)
        ------------------     --------------------------------------------------------------------
        rotation               Optional float. Use this parameter to export a map image rotated at
                               a specific angle, with the map centered around the center of the
                               specified bounding box (bbox). It could be positive or negative
                               number.
        ------------------     --------------------------------------------------------------------
        transformations        Optional list. Use this parameter to apply one or more datum
                               transformations to the map when sr is different than the map
                               service's spatial reference. It is an array of transformation
                               elements.
        ------------------     --------------------------------------------------------------------
        map_range_values       Optional list. Allows you to filter features in the exported map
                               from all layer that are within the specified range instant or
                               extent.
        ------------------     --------------------------------------------------------------------
        layer_range_values     Optional dictionary. Allows you to filter features for each
                               individual layer that are within the specified range instant or
                               extent. Note: Check range infos at the layer resources for the
                               available ranges.
        ------------------     --------------------------------------------------------------------
        layer_parameter        Optional list. Allows you to filter the features of individual
                               layers in the exported map by specifying value(s) to an array of
                               pre-authored parameterized filters for those layers. When value is
                               not specified for any parameter in a request, the default value,
                               that is assigned during authoring time, gets used instead.
        ==================     ====================================================================

        :return:
            A string, image of the map.

        .. code-block:: python

            # USAGE EXAMPLE

            >>> from arcgis.layers import MapImageLayer
            >>> from arcgis.gis import GIS

            # connect to your GIS and get the web map item
            >>> gis = GIS(url, username, password)

            >>> map_image_item = gis.content.get("2aaddab96684405880d27f5261125061")
            >>> map_image_item.export_map(bbox="-104,35.6,-94.32,41",
                                          bbox_sr = 4326,
                                          image_format ="png",
                                          layers = "include",
                                          transparent = True,
                                          scale = 40.0,
                                          rotation = -45.0
                                          )
        """

        params = {}
        params["f"] = f
        params["bbox"] = bbox
        if bbox_sr:
            params["bboxSR"] = bbox_sr
        if dpi is not None:
            params["dpi"] = dpi
        if size is not None:
            params["size"] = size
        if image_sr is not None and isinstance(image_sr, int):
            params["imageSR"] = {"wkid": image_sr}
        if image_format is not None:
            params["format"] = image_format
        if layer_defs is not None:
            params["layerDefs"] = layer_defs
        if layers is not None:
            params["layers"] = layers
        if transparent is not None:
            params["transparent"] = transparent
        if time_value is not None:
            params["time"] = time_value
        if time_options is not None:
            params["layerTimeOptions"] = time_options
        if dynamic_layers is not None:
            params["dynamicLayers"] = dynamic_layers
        if scale is not None:
            params["mapScale"] = scale
        if rotation is not None:
            params["rotation"] = rotation
        if gdb_version is not None:
            params["gdbVersion"] = gdb_version
        if transformation is not None:
            params["datumTransformations"] = transformation
        if map_range_values is not None:
            params["mapRangeValues"] = map_range_values
        if layer_range_values is not None:
            params["layerRangeValues"] = layer_range_values
        if layer_parameter:
            params["layerParameterValues"] = layer_parameter
        url = self._url + "/export"
        if len(kwargs) > 0:
            for k, v in kwargs.items():
                params[k] = v
        # return self._con.get(exportURL, params)

        if f == "json":
            return self._con.post(url, params)
        elif f == "image":
            if save_folder is not None and save_file is not None:
                return self._con.post(
                    url,
                    params,
                    out_folder=save_folder,
                    try_json=False,
                    file_name=save_file,
                )
            else:
                return self._con.post(url, params, try_json=False, force_bytes=True)
        elif f == "kmz":
            return self._con.post(
                url, params, out_folder=save_folder, file_name=save_file
            )
        else:
            print("Unsupported output format")

    # ----------------------------------------------------------------------
    def estimate_export_tiles_size(
        self,
        export_by: str,
        levels: str,
        tile_package: bool = False,
        export_extent: str = "DEFAULT",
        area_of_interest: Optional[Union[dict[str, Any], _geometry.Polygon]] = None,
        asynchronous: bool = True,
        **kwargs,
    ):
        """
        The ``estimate_export_tiles_size`` method is an asynchronous task that
        allows estimation of the size of the tile package or the cache data
        set that you download using the :attr:`~arcgis.layers.MapImageLayer.export_tiles` operation. This
        operation can also be used to estimate the tile count in a tile
        package and determine if it will exceed the ``maxExportTileCount``
        limit set by the administrator of the service. The result of this
        operation is ``MapServiceJob``. This job response contains reference
        to ``Map Service Result`` resource that returns the total size of the
        cache to be exported (in bytes) and the number of tiles that will
        be exported.

        ==================     ====================================================================
        **Parameter**           **Description**
        ------------------     --------------------------------------------------------------------
        export_by              Required string. The criteria that will be used to select the tile
                               service levels to export. The values can be Level IDs, cache scales
                               or the Resolution (in the case of image services).
                               Values:
                                    "levelId" | "resolution" | "scale"
        ------------------     --------------------------------------------------------------------
        levels                 Required string. Specify the tiled service levels for which you want
                               to get the estimates. The values should correspond to Level IDs,
                               cache scales or the Resolution as specified in export_by parameter.
                               The values can be comma separated values or a range.

                               Example 1: 1,2,3,4,5,6,7,8,9
                               Example 2: 1-4,7-9
        ------------------     --------------------------------------------------------------------
        tile_package           Optional boolean. Allows estimating the size for either a tile
                               package or a cache raster data set. Specify the value true for tile
                               packages format and false for Cache Raster data set. The default
                               value is False
        ------------------     --------------------------------------------------------------------
        export_extent          The extent (bounding box) of the tile package or the cache dataset
                               to be exported. If extent does not include a spatial reference, the
                               extent values are assumed to be in the spatial reference of the map.
                               The default value is full extent of the tiled map service.
                               Syntax: <xmin>, <ymin>, <xmax>, <ymax>
                               Example: -104,35.6,-94.32,41
        ------------------     --------------------------------------------------------------------
        area_of_interest       Optional dictionary or Polygon. This allows exporting tiles within
                               the specified polygon areas. This parameter supersedes extent
                               parameter.

                               Example:

                                    | { "features": [{"geometry":{"rings":[[[-100,35],
                                    |       [-100,45],[-90,45],[-90,35],[-100,35]]],
                                    |       "spatialReference":{"wkid":4326}}}]}
        ------------------     --------------------------------------------------------------------
        asynchronous           Optional boolean. The estimate function is run asynchronously
                               requiring the tool status to be checked manually to force it to
                               run synchronously the tool will check the status until the
                               estimation completes.  The default is True, which means the status
                               of the job and results need to be checked manually.  If the value
                               is set to False, the function will wait until the task completes.
        ==================     ====================================================================

        :return: dictionary

        """
        if self.properties["exportTilesAllowed"] == False:
            return
        import time

        url = self._url + "/estimateExportTilesSize"
        params = {
            "f": "json",
            "levels": levels,
            "exportBy": export_by,
            "tilePackage": tile_package,
            "exportExtent": export_extent,
        }
        params["levels"] = levels
        if len(kwargs) > 0:
            for k, v in kwargs.items():
                params[k] = v
        if not area_of_interest is None:
            params["areaOfInterest"] = area_of_interest
        if asynchronous == True:
            return self._con.get(url, params)
        else:
            exportJob = self._con.get(url, params)

            path = "%s/jobs/%s" % (url, exportJob["jobId"])

            params = {"f": "json"}
            job_response = self._con.post(path, params)

            if "status" in job_response or "jobStatus" in job_response:
                status = job_response.get("status") or job_response.get("jobStatus")
                while not status == "esriJobSucceeded":
                    time.sleep(5)

                    job_response = self._con.post(path, params)
                    status = job_response.get("status") or job_response.get("jobStatus")
                    if status in [
                        "esriJobFailed",
                        "esriJobCancelling",
                        "esriJobCancelled",
                        "esriJobTimedOut",
                    ]:
                        print(str(job_response["messages"]))
                        raise Exception("Job Failed with status " + status)
                    else:
                        path += (
                            "/" + job_response["results"]["out_service_url"]["paramUrl"]
                        )
                        out_service_resp = self._con.post(path)["value"]
                        return out_service_resp
                path += "/" + job_response["results"]["out_service_url"]["paramUrl"]
                out_service_resp = self._con.post(path)["value"]
                return out_service_resp
            else:
                raise Exception("No job results.")

    # ----------------------------------------------------------------------
    def export_tiles(
        self,
        levels: str,
        export_by: str = "LevelID",
        tile_package: bool = True,
        export_extent: Optional[Union[dict[str, Any], str]] = None,
        optimize_for_size: bool = True,
        compression: int = 75,
        area_of_interest: Optional[Union[dict[str, Any], _geometry.Polygon]] = None,
        asynchronous: bool = False,
        storage_format: Optional[str] = None,
        **kwargs,
    ):
        """
        The ``export_Tiles`` operation is performed as an asynchronous task and
        allows client applications to download map tiles from a server for
        offline use. This operation is performed on a ``Map Service`` that
        allows clients to export cache tiles. The result of this operation
        is a ``Map Service Job``. This job response contains a reference to the
        ``Map Service Result`` resource, which returns a URL to the resulting
        tile package (.tpk) or a cache raster dataset.
        ``export_Tiles`` can be enabled in a service by using ArcGIS Desktop
        or the ArcGIS Server Administrator Directory. In ArcGIS Desktop
        make an admin or publisher connection to the server, go to service
        properties, and enable ``Allow Clients`` to ``Export Cache Tiles`` in the
        advanced caching page of the ``Service Editor``. You can also specify
        the maximum tiles clients will be allowed to download.

        .. note::
            The default maximum allowed tile count is 100,000. To enable this capability
            using the Administrator Directory, edit the service, and set the
            properties ``exportTilesAllowed`` = ``True`` and ``maxExportTilesCount`` = 100000.

        .. note::
            In ArcGIS Server 10.2.2 and later versions, exportTiles is supported as an
            operation of the Map Server. The use of the
            ``http://Map_Service/exportTiles/submitJob`` operation is deprecated.
            You can provide arguments to the exportTiles operation as defined
            in the following parameters table:


        ==================     ====================================================================
        **Parameter**           **Description**
        ------------------     --------------------------------------------------------------------
        levels                 Required string. Specifies the tiled service levels to export. The
                               values should correspond to Level IDs, cache scales. or the
                               resolution as specified in export_by parameter. The values can be
                               comma separated values or a range. Make sure tiles are present at
                               the levels where you attempt to export tiles.
                               Example 1: 1,2,3,4,5,6,7,8,9
                               Example 2: 1-4,7-9
        ------------------     --------------------------------------------------------------------
        export_by              Required string. The criteria that will be used to select the tile
                               service levels to export. The values can be Level IDs, cache scales.
                               or the resolution.  The default is 'LevelID'.
                               Values:
                                    `levelId | resolution | scale`
        ------------------     --------------------------------------------------------------------
        tile_package           Optional boolean. Allows exporting either a tile package or a cache
                               raster data set. If the value is true, output will be in tile
                               package format, and if the value is false, a cache raster data
                               set is returned. The default value is True.
        ------------------     --------------------------------------------------------------------
        export_extent          Optional dictionary or string. The extent (bounding box) of the tile
                               package or the cache dataset to be exported. If extent does not
                               include a spatial reference, the extent values are assumed to be in
                               the spatial reference of the map. The default value is full extent
                               of the tiled map service.
                               Syntax:
                                    <xmin>, <ymin>, <xmax>, <ymax>
                               Example 1: -104,35.6,-94.32,41
                               Example 2:
                                    | {"xmin" : -109.55, "ymin" : 25.76,
                                    | "xmax" : -86.39, "ymax" : 49.94,
                                    | "spatialReference" : {"wkid" : 4326}}
        ------------------     --------------------------------------------------------------------
        optimize_for_size      Optional boolean. Use this parameter to enable compression of JPEG
                               tiles and reduce the size of the downloaded tile package or the
                               cache raster data set. Compressing tiles slightly compromises the
                               quality of tiles but helps reduce the size of the download. Try
                               sample compressions to determine the optimal compression before
                               using this feature.
                               The default value is True.
        ------------------     --------------------------------------------------------------------
        compression=75,        Optional integer. When optimize_for_size=true, you can specify a
                               compression factor. The value must be between 0 and 100. The value
                               cannot be greater than the default compression already set on the
                               original tile. For example, if the default value is 75, the value
                               of compressionQuality must be between 0 and 75. A value greater
                               than 75 in this example will attempt to up sample an already
                               compressed tile and will further degrade the quality of tiles.
        ------------------     --------------------------------------------------------------------
        area_of_interest       Optional dictionary, Polygon. The area_of_interest polygon allows
                               exporting tiles within the specified polygon areas. This parameter
                               supersedes the exportExtent parameter.

                               Example:

                                   | { "features": [{"geometry":{"rings":[[[-100,35],
                                   |   [-100,45],[-90,45],[-90,35],[-100,35]]],
                                   |   "spatialReference":{"wkid":4326}}}]}
        ------------------     --------------------------------------------------------------------
        asynchronous           Optional boolean. Default False, this value ensures the returns are
                               returned to the user instead of the user having the check the job
                               status manually.
        ------------------     --------------------------------------------------------------------
        storage_format         Optional string. Specifies the type of tile package that will be created.

                               | ``tpk`` - Tiles are stored using Compact storage format. It is supported across the ArcGIS platform.
                               | ``tpkx`` - Tiles are stored using CompactV2 storage format, which provides better performance on network shares and cloud store directories. This improved and simplified package structure type is supported by newer versions of ArcGIS products such as ArcGIS Online 7.1, ArcGIS Enterprise 10.7, and ArcGIS Runtime 100.5. This is the default.
        ==================     ====================================================================

        :return:
            A path to download file is asynchronous is ``False``. If ``True``, a dictionary is returned.
        """

        params = {
            "f": "json",
            "tilePackage": tile_package,
            "exportExtent": export_extent,
            "optimizeTilesForSize": optimize_for_size,
            "compressionQuality": compression,
            "exportBy": export_by,
            "levels": levels,
        }
        if not storage_format is None:
            storage_lu = {
                "esriMapCacheStorageModeCompact": "esriMapCacheStorageModeCompact",
                "esrimapcachestoragemodecompact": "esriMapCacheStorageModeCompact",
                "esriMapCacheStorageModeCompactV2": "esriMapCacheStorageModeCompactV2",
                "esrimapcachestoragemodecompactv2": "esriMapCacheStorageModeCompactV2",
                "tpk": "esriMapCacheStorageModeCompact",
                "tpkx": "esriMapCacheStorageModeCompactV2",
            }
            params["storageFormat"] = storage_lu[str(storage_format).lower()]
        if len(kwargs) > 0:
            for k, v in kwargs.items():
                params[k] = v
        url = self._url + "/exportTiles"
        if area_of_interest is not None:
            params["areaOfInterest"] = area_of_interest

        if asynchronous == True:
            return self._con.get(path=url, params=params)
        else:
            exportJob = self._con.get(path=url, params=params)

            path = "%s/jobs/%s" % (url, exportJob["jobId"])

            params = {"f": "json"}
            job_response = self._con.post(path, params)

            if "status" in job_response or "jobStatus" in job_response:
                status = job_response.get("status") or job_response.get("jobStatus")
                while not status == "esriJobSucceeded":
                    time.sleep(5)

                    job_response = self._con.post(path, params)
                    status = job_response.get("status") or job_response.get("jobStatus")
                    if status in [
                        "esriJobFailed",
                        "esriJobCancelling",
                        "esriJobCancelled",
                        "esriJobTimedOut",
                    ]:
                        print(str(job_response["messages"]))
                        raise Exception("Job Failed with status " + status)
            else:
                raise Exception("No job results.")

            if "results" in job_response:
                allResults = job_response["results"]

                for k, v in allResults.items():
                    if k == "out_service_url":
                        value = list(v.values())[0]
                        params = {"f": "json"}
                        gpRes = self._con.get(path=path + "/" + value, params=params)
                        if tile_package == True:
                            gpOutput = self._con.get(gpRes["value"])
                            files = []
                            for f in gpOutput["files"]:
                                name = f["name"]
                                dlURL = f["url"]
                                files.append(
                                    self._con.get(
                                        dlURL,
                                        params,
                                        out_folder=tempfile.gettempdir(),
                                        file_name=name,
                                    )
                                )
                            return files
                        else:
                            return self._con.get(path=gpRes["value"])["folders"]
                    else:
                        return None
            elif "output" in job_response:
                allResults = job_response["output"]
                if allResults["itemId"]:
                    return _gis.Item(gis=self._gis, itemid=allResults["itemId"])
                else:
                    if self._gis._portal.is_arcgisonline:
                        return [
                            self._con.get(url, try_json=False, add_token=False)
                            for url in allResults["outputUrl"]
                        ]
                    else:
                        return [
                            self._con.get(url, try_json=False)
                            for url in allResults["outputUrl"]
                        ]
            else:
                raise Exception(job_response)


###########################################################################
@deprecated(
    deprecated_in="2.4.0",
    removed_in="2.4.2",
    details="This class will be removed in a later version.",
)
class Events(object):
    @classmethod
    def _create_events(cls, enable=False):
        events = Events()

        events._enable = False
        events._type = "extentChanged"
        events._actions = []

        events.enable = enable

        return events

    @property
    def enable(self):
        return self._enable

    @enable.setter
    def enable(self, value):
        self._enable = bool(value)

    @property
    def type(self):
        return self._type

    @property
    def synced_widgets(self):
        return self._actions

    def sync_widget(self, widgets):
        if self.enable == False:
            raise Exception("Please enable events")

        else:
            if isinstance(widgets, list):
                for widget in widgets:
                    if widget.type == "mapWidget":
                        action_type = "setExtent"
                        self._actions.append(
                            {"type": action_type, "targetId": widget._id}
                        )
                    else:
                        action_type = "filter"
                        widget_id = str(widget._id) + "#main"
                        self._actions.append(
                            {
                                "type": action_type,
                                "by": "geometry",
                                "targetId": widget_id,
                            }
                        )
            else:
                if widgets.type == "mapWidget":
                    action_type = "setExtent"
                    self._actions.append({"type": action_type, "targetId": widgets._id})
                else:
                    action_type = "filter"
                    widget_id = str(widgets._id) + "#main"
                    self._actions.append(
                        {
                            "type": action_type,
                            "by": "geometry",
                            "targetId": widget_id,
                        }
                    )
