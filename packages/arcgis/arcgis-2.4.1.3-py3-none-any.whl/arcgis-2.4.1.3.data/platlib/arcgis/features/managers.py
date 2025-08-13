"""
Helper classes for managing feature layers and datasets.  These class are not created by users directly.
Instances of this class, are available as a properties of feature layers and make it easier to manage them.
"""

from __future__ import absolute_import, annotations
import os
import json
import time
import logging
import uuid
import tempfile
import collections
import concurrent.futures
from enum import Enum
from arcgis._impl.common._mixins import PropertyMap
from arcgis.gis import GIS, _GISResource, Item, ItemDependency
import concurrent.futures as _cf
from typing import Any
from arcgis.auth.tools import LazyLoader
from dataclasses import dataclass
import datetime as _dt
import requests

features = LazyLoader("arcgis.features")
_version = LazyLoader("arcgis.features._version")
_common_utils = LazyLoader("arcgis._impl.common._utils")
_cm = LazyLoader("arcgis.gis._impl._content_manager")
_arcgis_auth = LazyLoader("arcgis.auth")
re = LazyLoader("re")

_log = logging.getLogger()


# pylint: disable=protected-access
# ----------------------------------------------------------------------
def _check_status(url: str, gis: GIS):
    sleep_time: int = 1
    count: int = 1
    params: dict = {"f": "json"}
    session: _arcgis_auth.EsriSession = gis.session

    job_status_exceptions: dict = {
        "esrijobfailed": "Job failed.",
        "failed": "Job failed.",
        "esrijobcancelled": "Job cancelled.",
        "cancelled": "Job cancelled.",
        "esrijobtimedout": "Job timed out.",
        "timedout": "Job timed out.",
    }
    while True:
        resp: requests.Response = session.get(url, params=params)
        resp.raise_for_status()
        job_response: dict = resp.json()

        status: str = job_response.get("status", "").lower()
        if status in job_status_exceptions:
            raise Exception(job_status_exceptions[status])
        elif "error" in job_response:
            raise Exception(job_response["error"])
        elif status == "completed":
            return job_response
        else:
            time.sleep(sleep_time * count)
            count = min(count + 1, 10)


# ----------------------------------------------------------------------
def _get_value_case_insensitive(my_dict, key):
    """
    Retrieves the value associated with the given key in a case-insensitive manner.

    Args:
      my_dict: The dictionary to search.
      key: The key to look for.

    Returns:
      The value associated with the key, or None if the key is not found.
    """
    for k in my_dict.keys():
        if k.lower() == key.lower():
            return my_dict[k]
    return None


###########################################################################


class WebHookEvents(Enum):
    """
    Provides the allowed webhook enumerations for the captured events.
    """

    ALL = "*"
    FEATURESCREATED = "FeaturesCreated"
    FEATURESUPDATED = "FeaturesUpdated"
    FEATURESDELETED = "FeaturesDeleted"
    FEATURESEDITED = "FeaturesEdited"
    ATTACHMENTSCREATED = "AttachmentsCreated"
    ATTACHMENTSUPDATED = "AttachmentsUpdated"
    ATTACHMENTSDELETED = "AttachmentsDeleted"
    LAYERSCHEMACHANGED = "LayerSchemaChanged"
    LAYERDEFINITIONCHANGED = "LayerDefinitionChanged"
    FEATURESERVICEDEFINITIONCHANGED = "FeatureServiceDefinitionChanged"


###########################################################################
@dataclass
class WebHookScheduleInfo:
    """
    This dataclass provides information on how to schedule a webhook.


    =====================================    ===========================================================================
    **Parameter**                             **Description**
    -------------------------------------    ---------------------------------------------------------------------------
    name                                     Required string.  The name of the scheduling task.
    -------------------------------------    ---------------------------------------------------------------------------
    start_at                                 Required datetime.datetime. The start date.
    -------------------------------------    ---------------------------------------------------------------------------
    state                                    Optional String. The state of the task, this can be `enabled` or `disabled`.
    -------------------------------------    ---------------------------------------------------------------------------
    frequency                                Optional String. The default is `minute`. The time interval to run each task.
                                             The allows values are: second, minute, hour, day, week, month, year.
    -------------------------------------    ---------------------------------------------------------------------------
    interval                                 Optional Integer. The value for with the frequency describes.
    =====================================    ===========================================================================


    """

    name: str
    start_at: _dt.datetime
    state: str = "enabled"
    frequency: str = "minute"
    interval: int = 5

    def as_dict(self) -> dict[str, Any]:
        """returns the dataclass as a dictionary"""
        return {
            "name": self.name,
            "startAt": int(self.start_at.timestamp() * 1000),
            "recurrenceInfo": {
                "frequency": self.frequency,
                "interval": self.interval,
            },
        }


###########################################################################
class AttachmentManager(object):
    """
    Manager class for manipulating feature layer attachments.

    This class can be created by the user directly if a version is to be specified.

    Otherwise, an instance of this class, called 'attachments',
    is available as a property of the FeatureLayer object, if the layer supports attachments.
    Users call methods on this 'attachments' object to manipulate (create, get, list, delete) attachments.

    =====================   ===========================================
    **Inputs**              **Description**
    ---------------------   -------------------------------------------
    layer                   Required :class:`~arcgis.features.FeatureLayer` . The Feature Layer
                            that supports attachments.
    ---------------------   -------------------------------------------
    version                 Required Version or string. The `Version` class where
                            the branch version will take place or the
                            version name.
    =====================   ===========================================

    """

    def __init__(
        self,
        layer: features.FeatureLayer,
        version: str | _version.Version = None,
    ):
        self._layer = layer
        if isinstance(version, str):
            self._version = version
        elif isinstance(version, _version.Version):
            self._version = version.properties.versionName
        else:
            self._version = None

    def count(
        self,
        where: str | None = None,
        attachment_where: str | None = None,
        object_ids: str | None = None,
        global_ids: str | None = None,
        attachment_types: str | None = None,
        size: tuple[int] | list[int] | None = None,
        keywords: str | None = None,
    ) -> int:
        """
        The count operation returns the total number of attachments that satisfy
        the specific criteria entered as arguments to the method. The default
        count is the number of attachments for all features in the layer.

        =====================   =======================================================
        **Parameters**          **Description**
        ---------------------   -------------------------------------------------------
        where                   Optional String. Clause to specify the set of features
                                for which to return the attachment count.
        ---------------------   -------------------------------------------------------
        attachment_where        Optional String. Clause to specify criteria to apply to
                                the attachments table for which specific attachments to
                                include in the count value.
        ---------------------   -------------------------------------------------------
        object_ids              Optional List. List of *object_id* values to be queried
                                for which to count the number of attachments.
        ---------------------   -------------------------------------------------------
        global_ids              Optional List. List of *global_id* values to be queried
                                for which to count the number of attachments.
        ---------------------   -------------------------------------------------------
        attachment_types        Optional String. Value specifying the specific format
                                of attachments to count. See *attachmentTypes* at
                                the `Query Attachments <https://developers.arcgis.com/rest/services-reference/enterprise/query-attachments-feature-service-layer-.htm>`_
                                page for a list of options to use.
        ---------------------   -------------------------------------------------------
        size                    Optional Integer or integer range. Value or values to
                                to query attachments of a specific size.
        =====================   =======================================================

        :returns:
            Integer of total number of attachments.

        .. code-block:: python

            # Usage Example 1: Default
            >>> from arcgis.gis import GIS
            >>> gis = GIS(profile="your_organizational_profile")

            >>> flyr_item = gis.content.get("<item id>")

            >>> att_mgr = flyr_item.attachments
            >>> att_mgr.count()

            9

            # Usage Example 2: List of Object Ids:
            >>> att_mgr.count(object_ids=[1, 3])

            5

            # Usage Example 3: List of Global Ids:
            >>> att_mgr.count(global_ids=['{D432BA85-8702-437D-B740-C214DDE65846}'])

            2
        """
        url: str = "{}/{}".format(self._layer.url, "queryAttachments")
        if object_ids is None:
            object_ids = []
        if global_ids is None:
            global_ids = []
        if attachment_types is None:
            attachment_types = []
        if where is None and not object_ids and not global_ids:
            where = "1=1"
        if keywords is None:
            keywords = []
        params: dict[str, Any] = {
            "f": "json",
            "definitionExpression": where,
            "attachmentTypes": ",".join(attachment_types),
            "objectIds": ",".join([str(v) for v in object_ids]),
            "globalIds": ",".join([str(v) for v in global_ids]),
            "attachmentsDefinitionExpression": attachment_where or "",
            "keywords": ",".join([str(v) for v in keywords]),
            "size": size,
            "returnCountOnly": True,
        }
        res = self._layer._con._session.get(url=url, params=params)
        res.raise_for_status()
        data: dict[str, Any] = res.json()
        if data.get("attachmentGroups"):
            count_values = [
                d.get("count") for d in data.get("attachmentGroups") if d.get("count")
            ]
            if not count_values:
                attachment_groups = [
                    d.get("attachmentInfos") for d in data.get("attachmentGroups")
                ]
                return sum([len(grp) for grp in attachment_groups])
            return sum([grp["count"] for grp in data["attachmentGroups"]])
        elif "error" in data:
            raise Exception(data["error"])
        else:
            raise Exception(
                "Could not obtain the attachment counts, verify that attachments is enabled."
            )

    def search(
        self,
        where: str = "1=1",
        object_ids: str | None = None,
        global_ids: str | None = None,
        attachment_types: str | None = None,
        size: tuple[int] | list[int] | None = None,
        keywords: str | None = None,
        show_images: bool = False,
        as_df: bool = False,
        return_metadata: bool = False,
        return_url: bool = False,
        max_records: int | None = None,
        offset: int | None = None,
        *,
        attachment_where: str | None = None,
    ):
        """

        The `search` method allows querying the layer for its attachments and returns the results as
        a Pandas DataFrame or dict


        =========================   ===============================================================
        **Parameter**                **Description**
        -------------------------   ---------------------------------------------------------------
        where                       Required string.  The definition expression to be applied to
                                    the related layer/table. From the list of records that are
                                    related to the specified object Ids, only those records that
                                    conform to this expression will be returned.

                                    Example:

                                        where="STATE_NAME = 'Alaska'".

                                    The query results will return all attachments in Alaska.
        -------------------------   ---------------------------------------------------------------
        object_ids                  Optional list/string. The object IDs of this layer/table to be
                                    queried.

                                    Syntax:

                                        object_ids = <object_id1>, <object_id2>

                                    Example:

                                        object_ids = 2

                                    The query results will return attachments only for the specified object id.
        -------------------------   ---------------------------------------------------------------
        global_ids                  Optional list/string. The global IDs of this layer/table to be
                                    queried.

                                    Syntax:

                                        global_ids = <globalIds1>,<globalIds2>

                                    Example:

                                        global_ids = 6s430c5a-kb75-4d52-a0db-b30bg060f0b9, 35f0d027-8fc0-4905-a2f6-373c9600d017

                                    The query results will return attachments only for specified
                                    global id.
        -------------------------   ---------------------------------------------------------------
        attachment_types            Optional list/string. The file format that is supported by
                                    query attachment.

                                    Supported attachment types:
                                    bmp, ecw, emf, eps, ps, gif, img, jp2, jpc, j2k, jpf, jpg,
                                    jpeg, jpe, png, psd, raw, sid, tif, tiff, wmf, wps, avi, mpg,
                                    mpe, mpeg, mov, wmv, aif, mid, rmi, mp2, mp3, mp4, pma, mpv2,
                                    qt, ra, ram, wav, wma, doc, docx, dot, xls, xlsx, xlt, pdf, ppt,
                                    pptx, txt, zip, 7z, gz, gtar, tar, tgz, vrml, gml, json, xml,
                                    mdb, geodatabase

                                    Example:

                                        attachment_types='image/jpeg'
        -------------------------   ---------------------------------------------------------------
        size                        Optional tuple/list. The file size of the attachment is
                                    specified in bytes. You can enter a file size range
                                    (1000,15000) to query for attachments with the specified range.

                                    Example:

                                        size= (1000,15000)

                                    The query results will return all attachments within the
                                    specified file size range (1000 - 15000) bytes.
        -------------------------   ---------------------------------------------------------------
        keywords                    Optional string.  When attachments are uploaded, keywords can
                                    be assigned to the uploaded file.  By passing a keyword value,
                                    the values will be searched.

                                    Example:

                                        keywords='airplanes'
        -------------------------   ---------------------------------------------------------------
        show_images                 Optional bool. The default is False, when the value is True,
                                    the results will be displayed as a HTML table. If the as_df is
                                    set to False, this parameter will be ignored.
        -------------------------   ---------------------------------------------------------------
        as_df                       Optional bool. Default is False, if True, the results will be
                                    a Pandas' DataFrame.  If False, the values will be a list of
                                    dictionary values.
        -------------------------   ---------------------------------------------------------------
        return_metadata             Optional Boolean. If true, metadata stored in the `exifInfo`
                                    column will be returned for attachments that have `exifInfo`.
                                    This option is supported only when "name": "exifInfo" in the
                                    layer's attachmentProperties includes "isEnabled": true. When
                                    set to false, or not set, None is returned for `exifInfo`.
        -------------------------   ---------------------------------------------------------------
        return_url                  Optional Boolean. Specifies whether to return the attachment
                                    URL. The default is false. This parameter is supported if the
                                    `supportsQueryAttachmentsWithReturnUrl` property is true on the
                                    layer. Applications can use this URL to download the attachment
                                    image.
        -------------------------   ---------------------------------------------------------------
        max_records                 Optional Integer. This option fetches query results up to the
                                    `resultRecordCount` specified. When `resultOffset` is specified
                                    and this parameter is not, the feature service defaults to the
                                    `maxRecordCount`. The maximum value for this parameter is the
                                    value of the layer's `maxRecordCount` property. This parameter
                                    only applies if `supportPagination` is true.
        -------------------------   ---------------------------------------------------------------
        offset                      Optional Integer. This parameter is designed to be used in
                                    conjunction with `max_records` to page through a long list of
                                    attachments, one request at a time. This option fetches query
                                    results by skipping a specified number of records. The query
                                    results start from the next record (i.e., resultOffset + 1).
                                    The default value is 0. This parameter only applies when
                                    `supportPagination` is true. You can use this option to fetch
                                    records that are beyond `maxRecordCount` property.
        -------------------------   ---------------------------------------------------------------
        attachment_where            Optional str. The definition expression to be applied to the
                                    attachments table. Only those records that conform to this
                                    expression will be returned. You can get the attachments table
                                    field names to use in the expression by checking the layer's
                                    `attachmentProperties`.
        =========================   ===============================================================

        :return: A Pandas DataFrame or Dict of the attachments of the :class:`~arcgis.features.FeatureLayer`

        """
        import copy

        columns = [
            col.upper()
            for col in [
                "ParentObjectid",
                "ParentGlobalId",
                "Id",
                "Name",
                "GlobalId",
                "ContentType",
                "Size",
                "KeyWords",
                "URL",
                "IMAGE_PREVIEW",
            ]
        ]
        result_offset = 0
        if keywords is None:
            keywords = []
        elif isinstance(keywords, str):
            keywords = keywords.split(",")
        if object_ids is None:
            object_ids = []
        elif isinstance(object_ids, str):
            object_ids = object_ids.split(",")
        if global_ids is None:
            global_ids = []
        elif isinstance(global_ids, str):
            global_ids = global_ids.split(",")
        if attachment_types is None:
            attachment_types = []
        elif isinstance(attachment_types, str):
            attachment_types = attachment_types.split(",")
        if isinstance(size, (tuple, list)):
            size = ",".join(list([str(s) for s in size]))
        elif size is None:
            size = None
        if (
            self._layer._gis._portal.is_arcgisonline == False
            and self._layer.properties.hasAttachments
            and self._layer._gis
            and self._layer._gis.version <= [8, 2]
        ):
            rows = []

            query = self._layer.query(
                where=where,
                object_ids=",".join(map(str, object_ids)),
                global_ids=",".join(global_ids),
                return_ids_only=True,
            )
            if "objectIds" in query:
                token = self._layer._con.token
                for i in query["objectIds"]:
                    attachments = self.get_list(oid=i)
                    for att in attachments:
                        if not token is None:
                            att_path = "{}/{}/attachments/{}?token={}".format(
                                self._layer.url,
                                i,
                                att["id"],
                                self._layer._con.token,
                            )
                        else:
                            att_path = "{}/{}/attachments/{}".format(
                                self._layer.url, i, att["id"]
                            )
                        preview = None
                        if att["contentType"].find("image") > -1:
                            preview = (
                                '<img src="' + att_path + '" width=150 height=150 />'
                            )

                        row = {
                            "PARENTOBJECTID": i,
                            "PARENTGLOBALID": "N/A",
                            "ID": att["id"],
                            "NAME": att["name"],
                            "CONTENTTYPE": att["contentType"],
                            "SIZE": att["size"],
                            "KEYWORDS": "",
                            "IMAGE_PREVIEW": preview,
                        }
                        if "globalId" in att:
                            row["GLOBALID"] = att["globalId"]
                        if as_df and show_images:
                            row["DOWNLOAD_URL"] = (
                                '<a href="%s" target="_blank">DATA</a>' % att_path
                            )
                        else:
                            row["DOWNLOAD_URL"] = "%s" % att_path
                        rows.append(row)

                if (
                    attachment_types is not None and len(attachment_types) > 0
                ):  # performs contenttype search
                    if isinstance(attachment_types, str):
                        attachment_types = attachment_types.split(",")
                    rows = [
                        row
                        for row in rows
                        if os.path.splitext(row["NAME"])[1][1:] in attachment_types
                        or row["CONTENTTYPE"] in attachment_types
                    ]
        else:
            url = "{}/{}".format(self._layer.url, "queryAttachments")

            params = {
                "f": "json",
                "attachmentTypes": ",".join(attachment_types),
                "objectIds": ",".join([str(v) for v in object_ids]),
                "globalIds": ",".join([str(v) for v in global_ids]),
                "definitionExpression": where,
                "keywords": ",".join([str(v) for v in keywords]),
                "size": size,
                "returnMetadata": return_metadata,
                "returnUrl": return_url,
                "resultRecordCount": max_records,
                "resultOffset": offset,
            }
            if offset:
                params["offset"] = offset
            if attachment_where:
                params["attachmentsDefinitionExpression"] = attachment_where or ""

            iterparams = copy.copy(params)
            for k, v in iterparams.items():
                if k in ["objectIds", "globalIds", "attachmentTypes"] and v == "":
                    del params[k]
                elif k == "size" and v is None:
                    del params[k]

            results = self._layer._con.post(url, params)
            rows = []
            if "attachmentGroups" not in results:
                return []
            for result in results["attachmentGroups"]:
                for data in result["attachmentInfos"]:
                    token = self._layer._con.token
                    if not token is None:
                        att_path = "{}/{}/attachments/{}?token={}".format(
                            self._layer.url,
                            result["parentObjectId"],
                            data["id"],
                            self._layer._con.token,
                        )
                    else:
                        att_path = "{}/{}/attachments/{}".format(
                            self._layer.url,
                            result["parentObjectId"],
                            data["id"],
                        )
                    preview = None
                    if data["contentType"].find("image") > -1:
                        preview = '<img src="' + att_path + '" width=150 height=150 />'

                    row = {
                        "PARENTOBJECTID": result["parentObjectId"],
                        "PARENTGLOBALID": result["parentGlobalId"],
                        "ID": data["id"],
                        "NAME": data["name"],
                        "CONTENTTYPE": data["contentType"],
                        "SIZE": data["size"],
                        "KEYWORDS": data["keywords"],
                        "IMAGE_PREVIEW": preview,
                    }
                    if "globalId" in data:
                        row["GLOBALID"] = data["globalId"]
                    if as_df and show_images:
                        row["DOWNLOAD_URL"] = (
                            '<a href="%s" target="_blank">DATA</a>' % att_path
                        )
                    else:
                        row["DOWNLOAD_URL"] = "%s" % att_path
                    rows.append(row)
                    del row

        if as_df == True:
            import pandas as pd

            if show_images:
                from IPython.display import HTML

                pd.set_option("display.max_colwidth", -1)
                return HTML(pd.DataFrame.from_dict(rows).to_html(escape=False))
            else:
                if len(rows) == 0:
                    return pd.DataFrame()
                df = pd.DataFrame.from_dict(rows)
                df.drop(
                    ["DOWNLOAD_URL", "IMAGE_PREVIEW"],
                    axis=1,
                    inplace=True,
                    errors="ignore",
                )
                return df
        else:
            return rows

    def _download_all(self, object_ids=None, save_folder=None, attachment_types=None):
        """
        Downloads all attachments to a specific folder

        =========================   ===============================================================
        **Argument**               **Description**
        -------------------------   ---------------------------------------------------------------
        object_ids                  optional list. A list of object_ids to download data from.
        -------------------------   ---------------------------------------------------------------
        save_folder                 optional string. Path to save data to.
        -------------------------   ---------------------------------------------------------------
        attachment_types            optional string.  Allows the limitation of file types by passing
                                    a string of the item type.

                                    **Example:** image/jpeg
        =========================   ===============================================================

        :return: path to the file where the attachments have downloaded

        """
        results = []
        if save_folder is None:
            save_folder = os.path.join(tempfile.gettempdir(), "attachment_download")
        if not os.path.isdir(save_folder):
            os.makedirs(save_folder)
        attachments = self.search(
            object_ids=object_ids,
            attachment_types=attachment_types,
            as_df=True,
        )
        for row in attachments.to_dict("records"):
            dlpath = os.path.join(
                save_folder,
                "%s" % int(row["PARENTOBJECTID"]),
                "%s" % int(row["ID"]),
            )
            if os.path.isdir(dlpath) == False:
                os.makedirs(dlpath)
            path = self.download(
                oid=int(row["PARENTOBJECTID"]),
                attachment_id=int(row["ID"]),
                save_path=dlpath,
            )
            results.append(path[0])
            del row
        return results

    def get_list(self, oid: str):
        """
        Get the list of attachments for a given OBJECT ID

        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        oid                 Required string of the object id
        ===============     ====================================================================

        :result:
            A list of attachments

        """
        return self._layer._list_attachments(oid)["attachmentInfos"]

    def download(
        self,
        oid: str | None = None,
        attachment_id: str | None = None,
        save_path: str | None = None,
    ):
        """
        Downloads attachment and returns its path on disk.

        The download tool works as follows:

        * If nothing is given, all attachments will be downloaded

          Example: download()

        * If a single oid and attachment_id are given, the single file will download

        * If a list of oid values are given, all the attachments for those object ids will be saved locally.

        =========================   ===============================================================
        **Argument**                **Description**
        -------------------------   ---------------------------------------------------------------
        oid                         Optional list/string. A list of object Ids or a single value
                                    to download data from.
        -------------------------   ---------------------------------------------------------------
        attachment_id               Optional string. Id of the attachment to download. This is only
                                    honored if return_all is False.
        -------------------------   ---------------------------------------------------------------
        save_path                   Optional string. Path to save data to.
        =========================   ===============================================================

        :return: A path to the folder where the attachement are saved


        """
        return_all = False
        if isinstance(oid, str):
            oid = oid.split(",")
            oid_len = len(oid)
        elif isinstance(oid, int):
            oid = str(oid).split(",")
            oid_len = 1
        elif isinstance(oid, (tuple, list)):
            oid_len = len(oid)
        elif oid is None:
            oid_len = 0
        else:
            raise ValueError("oid must be of type list or string")
        if isinstance(attachment_id, str):
            attachment_id = [int(att) for att in attachment_id.split(",")]
            att_len = len(attachment_id)
        elif isinstance(attachment_id, int):
            attachment_id = str(attachment_id).split(",")
            att_len = 1
        elif isinstance(attachment_id, (tuple, list)):
            att_len = len(attachment_id)
        elif attachment_id is None:
            att_len = 0
        else:
            raise ValueError("attachment_id must be of type list or string")
        if oid_len == 1 and att_len > 0:
            return_all = False
        elif oid_len > 1 and att_len > 0:
            raise ValueError(
                "You cannot provide more than one oid when providing attachment_id values."
            )
        else:
            return_all = True

        if not return_all:
            oid = oid[0]
            paths = []
            for att in attachment_id:
                att_path = "{}/{}/attachments/{}".format(self._layer.url, oid, att)
                att_list = self.get_list(int(oid))

                # get attachment file name
                desired_att = [att2 for att2 in att_list if att2["id"] == int(att)]
                if len(desired_att) == 0:  # bad attachment id
                    raise RuntimeError
                else:
                    att_name = desired_att[0]["name"]

                if not save_path:
                    save_path = tempfile.gettempdir()
                if not os.path.isdir(save_path):
                    os.makedirs(save_path)

                path = self._layer._con.get(
                    path=att_path,
                    try_json=False,
                    out_folder=save_path,
                    file_name=att_name,
                    token=self._layer._token,
                    force_bytes=False,
                )
                paths.append(path)
            return paths
        else:
            return self._download_all(object_ids=oid, save_folder=save_path)

    def add(
        self,
        oid: str,
        file_path: str,
        keywords: str | None = None,
        return_moment: bool = False,
    ) -> bool:
        """
        Adds an attachment to a :class:`~arcgis.features.FeatureLayer`. Adding an attachment
        is a feature update, but is support with either the Update or the Create capability.
        The add operation is performed on a feature service feature resource.

        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        oid                 Required string of the object ID.
        ---------------     --------------------------------------------------------------------
        file_path           Required string. Path to the file to be uploaded as a new feature
                            attachment. The content type, size, and name of the attachment will
                            be derived from the uploaded file.
        ---------------     --------------------------------------------------------------------
        keywords            Optional string. Sets a text value that is stored as the keywords
                            value for the attachment. This parameter can be set when the layer has
                            an attachmentProperties property that includes "name": "keywords"
                            with "isEnabled": True. If the attachments have keywords enabled
                            and the layer also includes the attachmentFields property,
                            you can use it to understand properties like keywords field length.
        ---------------     --------------------------------------------------------------------
        return_moment       Optional bool. Specify whether the response will report the time
                            attachments were added. If True, the server will return the time
                            in the response's `editMoment` key. The default is False.
        ===============     ====================================================================

        :return:
            A JSON Response stating 'success' or 'error'

        """
        return self._layer._add_attachment(
            oid,
            file_path,
            keywords=keywords,
            return_moment=return_moment,
            version=self._version,
        )

    def delete(
        self,
        oid: str,
        attachment_id: str,
        return_moment: bool = False,
        rollback_on_failure: bool = True,
    ) -> bool:
        """
        Removes an attachment from a :class:`~arcgis.features.FeatureLayer` . Deleting an attachment is a feature update;
        it requires the Update capability. The deleteAttachments operation is performed on a
        feature service feature resource. This operation is available only if the layer has advertised that it has attachments.
        A layer has attachments if its hasAttachments property is true.

        ===================     ====================================================================
        **Parameter**            **Description**
        -------------------     --------------------------------------------------------------------
        oid                     Required string of the object ID
        -------------------     --------------------------------------------------------------------
        attachment_id           Required string. Ids of attachment to delete.

                                Syntax:

                                    attachment_id = "<attachmentId1>, <attachmentId2>"
        -------------------     --------------------------------------------------------------------
        return_moment           Optional boolean. Specify whether the response will report the time
                                attachments were deleted. If True, the server will report the time
                                in the response's `editMoment` key. The default value is False.
        -------------------     --------------------------------------------------------------------
        rollback_on_failure     Optional boolean. Specifies whether the edits should be applied
                                only if all submitted edits succeed. If False, the server will apply
                                the edits that succeed even if some of the submitted edits fail.
                                If True, the server will apply the edits only if all edits succeed.
                                The default value is true.
        ===================     ====================================================================

        :result:
           JSON response stating 'success' or 'error'
        """
        return self._layer._delete_attachment(
            oid,
            attachment_id,
            return_moment=return_moment,
            rollback_on_failure=rollback_on_failure,
            version=self._version,
        )

    def update(
        self,
        oid: str,
        attachment_id: str,
        file_path: str,
        return_moment: bool = False,
    ) -> bool:
        """
        Updates an existing attachment with a new file

        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        oid                 Required string of the object ID.
        ---------------     --------------------------------------------------------------------
        attachment_id       Required string. Id of the attachment to update.
        ---------------     --------------------------------------------------------------------
        file_path           Required string. Path to file to be uploaded as the updated feature
                            attachment.
        ---------------     --------------------------------------------------------------------
        return_moment       Optional boolean. Specify whether the response will report the time
                            attachments were deleted. If True, the server will report the time
                            in the response's `editMoment` key. The default value is False.
        ===============     ====================================================================

        :result:
           JSON response stating 'success' or 'error'
        """
        return self._layer._update_attachment(
            oid,
            attachment_id,
            file_path,
            return_moment=return_moment,
            version=self._version,
        )


###########################################################################
class SyncManager(object):
    """
    Manager class for manipulating replicas for syncing disconnected editing of :class:`~arcgis.features.FeatureLayer` .
    This class is not created by users directly.
    An instance of this class, called 'replicas', is available as a property of the :class:`~arcgis.features.FeatureLayerCollection` object,
    if the layer is sync enabled / supports disconnected editing.
    Users call methods on this 'replicas' object to manipulate (create, synchronize, unregister) replicas.
    """

    # http://services.arcgis.com/help/fsDisconnectedEditing.html
    def __init__(self, featsvc):
        self._fs = featsvc

    def get_list(self):
        """returns all the replicas for the feature layer collection"""
        return self._fs._replicas

    # ----------------------------------------------------------------------
    def unregister(self, replica_id: str):
        """
        Unregister a replica from a feature layer collection

        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        replica_id          The replicaID returned by the feature service when the replica was created.
        ===============     ====================================================================

        """
        return self._fs._unregister_replica(replica_id)

    # ----------------------------------------------------------------------
    def get(self, replica_id: str):
        """
        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        replica_id          Required string. replica_id returned by the feature service when
                            the replica was created.
        ===============     ====================================================================

        :return:
            The replica information
        """
        return self._fs._replica_info(replica_id)

    # ----------------------------------------------------------------------
    def create(
        self,
        replica_name: str,
        layers: list[int],
        layer_queries: dict[str, Any] | None = None,
        geometry_filter: dict[str, str] | None = None,
        replica_sr: dict[str, Any] | int | None = None,
        transport_type: str = "esriTransportTypeUrl",
        return_attachments: bool = False,
        return_attachments_databy_url: bool = False,
        asynchronous: bool = False,
        attachments_sync_direction: str = "none",
        sync_model: str = "none",
        data_format: str = "json",
        replica_options: dict[str, Any] | None = None,
        wait: bool = False,
        out_path: str | None = None,
        sync_direction: str | None = None,
        target_type: str = "client",
        transformations: list[str] | None = None,
        time_reference_unknown_client: bool | None = None,
    ):
        """
        The create operation is performed on a
        :class:`~arcgis.features.FeatureLayerCollection` resource. This
        operation creates a replica on the server between the feature service
        and the client based on replica definition criteria supplied by the
        client.

        The feature service must have the *Sync* capability. See `publishing criteria
        <https://enterprise.arcgis.com/en/server/latest/publish-services/windows/prepare-data-for-feature-services.htm>`_
        for details on how to publish services and set capabilities.
        The `Sync overview
        <https://developers.arcgis.com/rest/services-reference/enterprise/sync-overview.htm>`_
        provides additional details and links for details.

        The response to this method includes the *replicaID*, *replica
        generation number*, and data similar to the response from the
        :meth:`~arcgis.features.FeatureLayerCollection.query` operation on
        a service. This information should be kept track of by the client because
        it will be needed when synchronizing changes in the local data with the
        replica created on the server.

        See `Sync response types
        <https://developers.arcgis.com/rest/services-reference/enterprise/response-type-for-sync-operations.htm>`_
        details on the response received.

        The operations allows for register exiting data for the replica by
        using the *replica_options* argument, a dictionary whose key-value pairs are
        detailed `here <https://developers.arcgis.com/rest/services-reference/enterprise/create-replica.htm#GUID-73F56FCD-BA1F-4C8B-AA1B-676C89A7FE64>`_.

        For full details see `Create Replica <https://developers.arcgis.com/rest/services-reference/enterprise/create-replica.htm>`_.

        =============================       ====================================================================
        **Parameter**                        **Description**
        -----------------------------       --------------------------------------------------------------------
        replica_name                        Required string. Name of the replica.
        -----------------------------       --------------------------------------------------------------------
        layers                              Required list. A list of layers and tables to include in the replica.
        -----------------------------       --------------------------------------------------------------------
        layer_queries                       Optional dictionary. In addition to the layers and geometry
                                            parameters, the layer_queries parameter can be used to further define
                                            what is replicated. This parameter allows you to set properties on a
                                            per layer or per table basis. Only the properties for the layers and
                                            tables that you want changed from the default are required.

                                            Example:

                                                | layer_queries = {"0":{"queryOption": "useFilter", "useGeometry": true,
                                                | "where": "requires_inspection = Yes"}}
        -----------------------------       --------------------------------------------------------------------
        geometry_filter                     Optional dictionary. Spatial filter from :mod:`~arcgis.geometry.filters` module
                                            to filter results by a spatial relationship with another geometry.
        -----------------------------       --------------------------------------------------------------------
        replica_sr                          Optional WKID or a spatial reference JSON object. The spatial
                                            reference of the replica geometry.
        -----------------------------       --------------------------------------------------------------------
        transport_type                      The transport_type represents the response format. If the
                                            transport_type is esriTransportTypeUrl, the JSON response is contained
                                            in a file, and the URL link to the file is returned. Otherwise, the
                                            JSON object is returned directly. The default is esriTransportTypeUrl.
                                            If async is true, the results will always be returned as if
                                            transport_type is esriTransportTypeUrl. If dataFormat is sqlite, the
                                            transportFormat will always be esriTransportTypeUrl regardless of how
                                            the parameter is set.

                                            Values:

                                                esriTransportTypeUrl | esriTransportTypeEmbedded.
        -----------------------------       --------------------------------------------------------------------
        return_attachments                  If True, attachments are added to the replica and returned in the
                                            response. Otherwise, attachments are not included. The default is
                                            False. This parameter is only applicable if the feature service has
                                            attachments.
        -----------------------------       --------------------------------------------------------------------
        return_attachments_databy_url       If True, a reference to a URL will be provided for each attachment
                                            returned from create method. Otherwise, attachments are embedded in
                                            the response. The default is True. This parameter is only applicable
                                            if the feature service has attachments and if return_attachments is
                                            True.
        -----------------------------       --------------------------------------------------------------------
        asynchronous                        If True, the request is processed as an asynchronous job, and a URL
                                            is returned that a client can visit to check the status of the job.
                                            See the topic on asynchronous usage for more information. The default
                                            is False.
        -----------------------------       --------------------------------------------------------------------
        attachments_sync_direction          Client can specify the attachmentsSyncDirection when creating a
                                            replica. AttachmentsSyncDirection is currently a createReplica property
                                            and cannot be overridden during sync.

                                            Values:

                                                none, upload, bidirectional
        -----------------------------       --------------------------------------------------------------------
        sync_model                          This parameter is used to indicate that the replica is being created
                                            for per-layer sync or per-replica sync. To determine which model types
                                            are supported by a service, query the supportsPerReplicaSync,
                                            supportsPerLayerSync, and supportsSyncModelNone properties of the Feature
                                            Service. By default, a replica is created for per-replica sync.
                                            If syncModel is perReplica, the syncDirection specified during sync
                                            applies to all layers in the replica. If the syncModel is perLayer, the
                                            syncDirection is defined on a layer-by-layer basis.

                                            If sync_model is perReplica, the response will have replicaServerGen.
                                            A perReplica sync_model requires the replicaServerGen on sync. The
                                            replicaServerGen tells the server the point in time from which to send
                                            back changes. If sync_model is perLayer, the response will include an
                                            array of server generation numbers for the layers in layerServerGens. A
                                            perLayer sync model requires the layerServerGens on sync. The
                                            layerServerGens tell the server the point in time from which to send
                                            back changes for a specific layer. sync_model=none can be used to export
                                            the data without creating a replica. Query the supportsSyncModelNone
                                            property of the feature service to see if this model type is supported.

                                            See the `RollbackOnFailure and Sync Models <https://developers.arcgis.com/rest/services-reference/enterprise/rollbackonfailure-and-sync-models.htm>`_ topic for more details.

                                            Values:

                                                perReplica | perLayer | none

                                            Example:

                                                sync_model = perLayer
        -----------------------------       --------------------------------------------------------------------
        data_format                         The format of the replica geodatabase returned in the response. The
                                            default is json.

                                            Values:

                                                filegdb, json, sqlite, shapefile
        -----------------------------       --------------------------------------------------------------------
        replica_options                     This parameter instructs the create operation to create a new replica
                                            based on an existing replica definition (refReplicaId). It can be used
                                            to specify parameters for registration of existing data for sync. The
                                            operation will create a replica but will not return data. The
                                            responseType returned in the create response will be
                                            esriReplicaResponseTypeInfo.
        -----------------------------       --------------------------------------------------------------------
        wait                                If async, wait to pause the process until the async operation is completed.
        -----------------------------       --------------------------------------------------------------------
        out_path                            out_path - folder path to save the file.
        -----------------------------       --------------------------------------------------------------------
        sync_direction                      Defaults to bidirectional when the targetType is client and download
                                            when the target_type is server. If set, only bidirectional is supported
                                            when target_type is client. If set, only upload or download are
                                            supported when target_type is server.

                                            Values:

                                                download | upload | bidirectional

                                            Example:

                                                sync_direction=download
        -----------------------------       --------------------------------------------------------------------
        target_type                         Can be set to either server or client. If not set, the default is
                                            client. This option was added at 10.5.1.
        -----------------------------       --------------------------------------------------------------------
        transformations                     Optional List. Introduced at 10.8. This parameter applies a datum
                                            transformation on each layer when the spatial reference used in
                                            geometry is different from the layer's spatial reference.
        -----------------------------       --------------------------------------------------------------------
        time_reference_unknown_client       Setting time_reference_unknown_client as true indicates that the client is
                                            capable of working with data values that are not in UTC. If its not set
                                            to true, and the service layer's datesInUnknownTimeZone property is true,
                                            then an error is returned. The default is false

                                            It's possible to define a service's time zone of date fields as unknown.
                                            Setting the time zone as unknown means that date values will be returned
                                            as-is from the database, rather than as date values in UTC. Non-hosted feature
                                            services can be set to use an unknown time zone using ArcGIS Server Manager.
                                            Setting the time zones to unknown also sets the datesInUnknownTimeZone layer property
                                            as true. Currently, hosted feature services do not support this setting.
                                            This setting does not apply to editor tracking date fields which are
                                            stored and returned in UTC even when the time zone is set to unknown.

                                            Most clients released prior to ArcGIS Enterprise 10.9 will not be able
                                            to work with feature services that have an unknown time setting.
                                            The timeReferenceUnknownClient parameter prevents these clients from working
                                            with the service in order to avoid problems..
                                            Setting this parameter to true indicates that the client is capable of working with
                                            unknown date values that are not in UTC.
        =============================       ====================================================================


        :return:
           JSON response if POST request made successfully. Otherwise, return None.


        .. code-block:: python  (optional)

           # USAGE EXAMPLE: Create a replica on server with geometry_filter specified.

           geom_filter = {'geometry':'8608022.3,1006191.2,8937015.9,1498443.1',
                          'geometryType':'esriGeometryEnvelope'}

           fs.replicas.create(replica_name='your_replica_name',
                              layers=[0],
                              geometry_filter=geom_filter,
                              attachments_sync_direction=None,
                              transport_type="esriTransportTypeUrl",
                              return_attachments=True,
                              return_attachments_databy_url=True,
                              asynchronous=True,
                              sync_model="perLayer",
                              target_type="server",
                              data_format="sqlite",
                              out_path=r'/arcgis/home',
                              wait=True)

        """
        if geometry_filter is None:
            extents = self._fs.properties["fullExtent"]
            extents_str = ",".join(
                format(x, "10.3f")
                for x in [
                    extents["xmin"],
                    extents["ymin"],
                    extents["xmax"],
                    extents["ymax"],
                ]
            )
            geometry_filter = {"geometryType": "esriGeometryEnvelope"}
            geometry_filter.update({"geometry": extents_str})
        if not layer_queries:
            # Assures correct number of record counts are returned
            layer_queries = {}
            for layer in layers:
                layer_queries[str(layer)] = {"queryOption": "all"}

        return self._fs._create_replica(
            replica_name=replica_name,
            layers=layers,
            layer_queries=layer_queries,
            geometry_filter=geometry_filter,
            replica_sr=replica_sr,
            transport_type=transport_type,
            return_attachments=return_attachments,
            return_attachments_data_by_url=return_attachments_databy_url,
            asynchronous=asynchronous,
            sync_direction=sync_direction,
            target_type=target_type,
            attachments_sync_direction=attachments_sync_direction,
            sync_model=sync_model,
            data_format=data_format,
            replica_options=replica_options,
            wait=wait,
            out_path=out_path,
            transformations=transformations,
            time_reference_unknown_client=time_reference_unknown_client,
        )

    # ----------------------------------------------------------------------
    def cleanup_change_tracking(
        self,
        layers: list[int],
        retention_period: int,
        period_unit: str = "days",
        min_server_gen: str | None = None,
        replica_id: str | None = None,
        future: bool = False,
    ):
        """

        Change tracking information stored in each feature service layer
        (enabled for Change Tracking) might grow very large. The change
        tracking info used by the feature service to determine the change
        generation number and the features that have changed for a
        particular generation. Clients can purge the change tracking
        content if the changes are already synced-up to all clients and the
        changes are no longer needed.

        Only the owner or the organization administrator can cleanup change
        tracking information.

        ==================     ====================================================================
        **Parameter**           **Description**
        ------------------     --------------------------------------------------------------------
        layers                 Required list. A list of layers and tables to include in the replica.
        ------------------     --------------------------------------------------------------------
        retention_period       Optional Integer. The retention period to use when cleaning up the
                               change tracking information. Change tracking information will be
                               cleaned up if they are older than the retention period.
        ------------------     --------------------------------------------------------------------
        period_unit            Optional String.  The units of the retention period.

                               Values:

                                    `days`, `seconds`, `minutes`, or `hours`

        ------------------     --------------------------------------------------------------------
        min_server_gen         Optional String.  In addition to the retention period, the change
                               tracking can be cleaned by its generation numbers. Older tracking
                               information that has older generation number than the
                               `min_server_gen` will be cleaned.
        ------------------     --------------------------------------------------------------------
        replica_id             Optional String.  The change tracking can also be cleaned by the
                               `replica_id` in addition to the `retention_period` and the
                               `min_server_gen`.
        ------------------     --------------------------------------------------------------------
        future                 Optional boolean. If True, a future object will be returned and the process
                               will not wait for the task to complete. The default is False, which means wait for results.
        ==================     ====================================================================


        :return:
            Boolean or If ``future = True``, then the result is a `Future <https://docs.python.org/3/library/concurrent.futures.html>`_ object. Call ``result()`` to get the response.

        """
        return self._fs._cleanup_change_tracking(
            layers=layers,
            retention_period=retention_period,
            period_unit=period_unit,
            min_server_gen=min_server_gen,
            replica_id=replica_id,
            future=future,
        )

    # ----------------------------------------------------------------------
    def synchronize(
        self,
        replica_id: str,
        transport_type: str = "esriTransportTypeUrl",
        replica_server_gen: int | None = None,
        return_ids_for_adds: bool = False,
        edits: list[dict[str, Any]] | None = None,
        return_attachment_databy_url: bool = False,
        asynchronous: bool = False,
        sync_direction: str = "snapshot",
        sync_layers: str = "perReplica",
        edits_upload_id: dict | None = None,
        edits_upload_format: str | None = None,
        data_format: str = "json",
        rollback_on_failure: bool = False,
    ):
        """
        The synchronize operation synchronizes data between a local copy of data
        created by a client and a feature service based on a *replica_id* value
        obtained when creating the replica. See `Sync overview
        <https://developers.arcgis.com/rest/services-reference/enterprise/sync-overview.htm>`_
        for more information on the process.

        The client obtains the *replica_id* by first calling the
        :meth:`~arcgis.features.managers.SyncManager.create` operation. Synchronize
        applies the client's data changes by importing them onto the server. It
        then exports the changes from the server that have taken place since the
        last time the client retrieved the server's data. Edits can be supplied
        in the *edits* parameter or by using the *edits_uploads_id* and
        *edits_upload_format* arguments to identify a file item containing the
        edits that were previously uploaded using the
        :meth:`~arcgis.features.FeatureLayerCollection.upload` method.

        The response for this operation includes a *replicaID* value, new
        replica generation number, or layer's generation numbers. The response
        has edits or layers according to the *sync_direction*/*sync_layers*
        arguments. Presence of layers and edits in the response is indicated by the
        `responseType <https://developers.arcgis.com/rest/services-reference/enterprise/response-type-for-sync-operations.htm>`_
        key.

        If the *responseType* value is *esriReplicaResponseTypeEdits* or
        *esriReplicaResponseTypeEditsAndData*, the result of this operation can
        include lists of edit results for each layer/table edited. Each edit
        result identifies a single feature in a layer or row in a table and
        indicates if the edits were successful or not. If an edit is not
        successful, the edit result also includes an error code and an error
        description.

        * If *sync_model* is *perReplica* and *sync_direction* is download or
          bidirectional, the :meth:`~arcgis.features.managers.SyncManager.synchronize`
          operation's response will have edits.
        * If *sync_direction* is *snapshot*, the response will have replacement data.
        * If *sync_model* is *perLayer*, and *sync_layers* have *sync_direction*
          as download or bidirectional, the response will have edits.
        * If *sync_layers* have *sync_direction* as download or bidirectional
          for some layers and snapshot for other layers, the response will have edits
          and data.
        * If *sync_direction* for all the layers is snapshot, the response will
          have replacement data.
        * If *sync_model* is *perReplica*, the :meth:`~arcgis.features.managers.SyncManager.create`
          and :meth:`~arcgis.features.managers.SyncManager.synchronize` responses
          contain *replicaServerGen* values.
        * If *sync_model* is *perLayer*, the :meth:`~arcgis.features.managers.SyncManager.create`
          and :meth:`~arcgis.features.managers.SyncManager.synchronize` responses contain
          *layerServerGens* values.

        See `Synchronize Replica <https://developers.arcgis.com/rest/services-reference/synchronize-replica.htm>`_
        for full details on the operation.

        =============================   ====================================================================
        **Parameter**                   **Description**
        -----------------------------   --------------------------------------------------------------------
        replica_id                      Required string. The ID of the replica you want to synchronize.
        -----------------------------   --------------------------------------------------------------------
        transport_type                  Optional String. Represents the format of the response. The default
                                        value is *esriTransportTypeUrl*.

                                        Values:

                                        * *esriTransportTypeUrl* - the response is contained in a file and a
                                          the URL link to the file is returned
                                        * *esriTransportTypeEmbedded* - a JSON object is returned in the
                                          response

                                        .. note::
                                            If *asynchronous* is *True* or *data_format=sqllite*, the
                                            response is always returned by URL.
        -----------------------------   --------------------------------------------------------------------
        replica_server_gen              Required Integer. A generation number that allows the server to keep
                                        track of what changes have already been synchronized.
                                        A new *replicaServerGen* is sent with the response. Clients should
                                        persist this value and use it with the next call to *synchronize*.

                                        ..  note::
                                            Applies when *sync_model* is *perReplica*
        -----------------------------   --------------------------------------------------------------------
        return_ids_for_adds             Optional Boolean. If *True*, the *objectIDs* and *globalIDs* of
                                        features added during the synchronize will be returned to the client
                                        in the *addResults* sections of the response. Otherwise, the IDs are
                                        not returned. The default is *False*.
        -----------------------------   --------------------------------------------------------------------
        edits                           Optional list of dictionaries. Contains The edits the client wants
                                        to apply to the service.

                                        .. note::
                                            This argument can be omitted if the *edits_upload_id* and
                                            *edits_upload_format* arguments are provided instead.

                                        The edits are provided as a list where each element is a dictionary
                                        whose key-value pairs provide:

                                        * *id* - The layer or table ID
                                        * *features* - a dictionary of inserts, updates, and deletes. New
                                          features and updates are provided as lists of :class:`features <arcgis.features.Feature>`.
                                          Deletes are provided as lists of *globalIDs*.
                                        * *attachments* - a dictionary of inserts, updates, and deletes. Deletes
                                          can be specified as a list of *globalIDs*. Updates and adds are
                                          specified using the following set of properties:

                                          - *globalid* - The globalID of the attachment that is to be added or updated.
                                          - *parentGlobalid* - The globalID of the feature associated with the attachment.
                                          - *contentType* - Describes the file type of the attachment (for example, image/jpeg).
                                          - *name* - The file name (for example, hydrant.jpg).
                                          - *data* - The base 64 encoded data if embedding the data. Only required if the attachment
                                            is embedded.
                                          - *url* - The location where the service will upload the attachment file (for example,
                                            http://machinename/arcgisuploads/Hydrant.jpg). Only required if the attachment is not
                                            embedded.

                                          .. note::
                                              If embedding the attachment, set the *data* property, otherwise set *url*.

                                        See `edits <https://developers.arcgis.com/rest/services-reference/enterprise/synchronize-replica.htm#UL_B8C0FE10EF1D4412B8170A3E9C8AAC54>`_
                                        for full details on formatting.
        -----------------------------   --------------------------------------------------------------------
        return_attachment_databy_url    If *True*, a reference to a URL will be provided for each attachment
                                        returned. Otherwise, attachments are embedded in the response. The
                                        default is *True*.

                                        .. note::
                                            Only applies if attachments are included in the replica.
        -----------------------------   --------------------------------------------------------------------
        asynchronous                    If *True*, the request is processed as an asynchronous job and a URL
                                        is returned that a client can visit and check the status. See the
                                        `asynchronous operations <https://developers.arcgis.com/rest/services-reference/enterprise/asynchronous-operations.htm>`_
                                        for more information. The default is False.
        -----------------------------   --------------------------------------------------------------------
        sync_direction                  Optional String. Determines whether to upload, download, or upload
                                        and download. By default, a replica is synchronized bi-directionally.
                                        Only applicable when *sync_model* is *perReplica*. If *sync_model*
                                        is *perLayer*, the *sync_layers* argument contains this information.

                                        Values:

                                        - *download* -
                                             The changes that have taken place on the server since last download are
                                             returned. Client does not need to send any changes. If the changes are sent, service
                                             will ignore them.
                                        - *upload* -
                                             The changes submitted in the edits or editsUploadID/editsUploadFormat
                                             parameters are applied, and no changes are downloaded from the server.
                                        - *bidirectional* -
                                             The changes submitted in the edits or editsUploadID/editsUploadFormat
                                             parameters are applied, and changes on the server are downloaded. This is the default
                                             value.
                                        - *snapshot* -
                                             The current state of the features is downloaded from the server. If any edits
                                             are specified, they will be ignored.
        -----------------------------   --------------------------------------------------------------------
        sync_layers                     Required List of dictionaries specifying layer level criteria for the
                                        operation if *sync_model* is *perLayer*. The information in the
                                        dictionary allows a client to specify layer level generation numbers,
                                        and can also be used to specify individual directions for
                                        synchronization per layer.


                                        Syntax:

                                        .. code-block:: python

                                            >>> flc.replicas.synchronize(...
                                                                         sync_layers = [
                                                                                        {
                                                                                         "id": <layer id>,
                                                                                         "serverGen": <generation number1>,
                                                                                         "serverSibGen": <sib generation number>,
                                                                                         "syncDirection": "<sync_direction1>"
                                                                                         },
                                                                               ...
                                                                            ]
                                                                          ...
                                                                          )

                                        .. note::
                                            This parameter is ignored when *sync_model* is *perReplica*

                                        * If *syncDirection* value is *bidirectional* or *download*,
                                          *serverGen* is required
                                        * The *serverSibGen* is only needed when syncing for replicas where
                                          the *target_type* argument was *server* when created
                                        * For replicas where the *syncModel* value is *perLayer*, the *serverSibGen*
                                          serves the purpose of keeping track of changes already received at the
                                          layer level the same way *replicaServerGen* does at the  replica level.
                                          It is updated when a synchronization completes.
                                        * If this argument is provided and *sync_direction* is provided, layers
                                          in this argument that do not provide a *syncDirection* value will use
                                          the value of *sync_direction*. If *sync_direction* is not specified,
                                          the default *bidirectional* is used.
        -----------------------------   --------------------------------------------------------------------
        edits_upload_id                 Optional String. The ID for the uploaded item that contains the edits
                                        the client wants to apply to the service. Used in conjunction with
                                        *edits_upload_format*.

                                        .. note::
                                            This is the *id* value returned when the edits were added
                                            to the service resources using
                                            :meth:`~arcgis.features.FeatureLayerCollection.upload`.
        -----------------------------   --------------------------------------------------------------------
        edits_upload_format             Optional String. The data format of the data referenced in
                                        *edit_upload_id*.
        -----------------------------   --------------------------------------------------------------------
        data_format                     Optional String. The format for the data returned in the response.
                                        The default value is *json*.

                                        Values:

                                        * *json* - data is embedded in the response
                                        * *sqlite* - a mobile geodatabase is returned which can be used in
                                          ArcGIS runtime applications
        -----------------------------   --------------------------------------------------------------------
        rollback_on_failure             Optional Boolean. Determines the behavior when there are errors
                                        while importing edits on the server during the operation. This only
                                        applies when *sync_direction* is *upload* or *bidirectional*, or
                                        the *syncDirection* key of an individual *sync_layers* element is
                                        *upload* or *bidirectional*. See the `Rollback On Failure and
                                        Sync Model <https://developers.arcgis.com/rest/services-reference/enterprise/rollbackonfailure-and-sync-models.htm>`_
                                        documentation for full details.

                                        * When *True*, if an error occurs while importing edits on the
                                          server, all edits are rolled back and not applied. The
                                          operation returns an error in the response. Use this setting
                                          when the edits are such that you will either want all or none
                                          applied.
                                        * When *False*, if an error occurs while importing an edit on the
                                          server, the operation skips the edit and continues.
                                          that were skipped are returned in the edits results with
                                          information describing why the edits were skipped. This is the
                                          default value.
        -----------------------------   --------------------------------------------------------------------
        close_replica                   Optional Boolean. Indicates whether to unregister the replica
                                        upon completion. The default value is *False*.

                                        * If *True*, the replica will be unregistered when operation
                                          completes.
                                        * If *False*, the replica can continue to be synchronized.
        -----------------------------   --------------------------------------------------------------------
        out_path                        optional String. Path of a folder to save the output to a file.
        =============================   ====================================================================

        :returns:
            A Python dictionary with various keys depending upon inputs.
        """

        if rollback_on_failure:
            if not self._fs.properties["syncCapabilities"]["supportsRollbackOnFailure"]:
                raise Exception("Feature service does not support rollback on failure.")

        # TODO:
        return self._fs._synchronize_replica(
            replica_id=replica_id,
            transport_type=transport_type,
            replica_server_gen=replica_server_gen,
            return_ids_for_adds=return_ids_for_adds,
            edits=edits,
            return_attachment_databy_url=return_attachment_databy_url,
            asynchronous=asynchronous,
            sync_direction=sync_direction,
            sync_layers=sync_layers,
            edits_upload_id=edits_upload_id,
            edits_upload_format=edits_upload_format,
            data_format=data_format,
            rollback_on_failure=rollback_on_failure,
            close_replica=False,
            out_path=None,
        )

    def create_replica_item(
        self,
        replica_name: str,
        item: Item,
        destination_gis: GIS,
        layers: list[int] | None = None,
        extent: dict[str, Any] | None = None,
    ):
        """
        Creates a replicated service from a parent to another GIS.

        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        replica_name        Optional string. Name for replicated item in other GIS
        ---------------     --------------------------------------------------------------------
        item                Required Item to replicate
        ---------------     --------------------------------------------------------------------
        destination_gis     Required :class:`~arcgis.gis.GIS` object
        ---------------     --------------------------------------------------------------------
        layers              Optional list. Layers to replicate in the item
        ---------------     --------------------------------------------------------------------
        extent              Optional dict. Depicts the geometry extent for an item.
        ===============     ====================================================================

        :return:
            The published replica item created
        """
        import tempfile
        import os
        from ..gis import Item

        fs = item.layers[0].container
        if layers is None:
            ls = fs.properties["layers"]
            ts = fs.properties["tables"]
            layers = ""
            for i in ls + ts:
                layers += str(i["id"])
        if extent is None:
            extent = fs.properties["fullExtent"]
            if "spatialReference" in extent:
                del extent["spatialReference"]
        extents_str = ",".join(
            format(x, "10.3f")
            for x in [
                extent["xmin"],
                extent["ymin"],
                extent["xmax"],
                extent["ymax"],
            ]
        )
        geom_filter = {"geometryType": "esriGeometryEnvelope"}
        geom_filter.update({"geometry": extents_str})

        out_path = tempfile.gettempdir()
        from . import FeatureLayerCollection

        isinstance(fs, FeatureLayerCollection)
        db = fs._create_replica(
            replica_name=replica_name,
            layers=layers,
            geometry_filter=geom_filter,
            attachments_sync_direction=None,
            transport_type="esriTransportTypeUrl",
            return_attachments=True,
            return_attachments_data_by_url=True,
            asynchronous=True,
            sync_model="perLayer",
            target_type="server",
            data_format="sqlite",
            # target_type="server",
            out_path=out_path,
            wait=True,
        )
        if os.path.isfile(db) == False:
            raise Exception("Could not create the replica")
        destination_content = destination_gis.content
        folder = destination_content.folders.get()
        item = folder.add(
            item_properties={
                "type": "SQLite Geodatabase",
                "tags": "replication",
                "title": replica_name,
            },
            file=db,
        ).result()
        published = item.publish()
        return published

    def sync_replicated_items(self, parent: Item, child: Item, replica_name: str):
        """
        Synchronizes two replicated items between portals

        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        parent              Required :class:`~arcgis.gis.Item` that points to the feature service
                            that is the parent dataset. (source)
        ---------------     --------------------------------------------------------------------
        child               Required :class:`~arcgis.gis.Item` that points to the feature service
                            that is the child dataset. (target)
        ---------------     --------------------------------------------------------------------
        replica_name        Required string. Name of either parent or child Item
        ===============     ====================================================================

        :result:
            Boolean value. True means service is up to date/synchronized,
            False means the synchronization failed.

        """
        from ..gis import Item

        if isinstance(parent, Item) == False:
            raise ValueError("parent must be an Item")
        if isinstance(child, Item) == False:
            raise ValueError("child must be an Item")
        child_fs = child.layers[0].container
        parent_fs = parent.layers[0].container
        child_replicas = child_fs.replicas
        parent_replicas = parent_fs.replicas
        if child_replicas and parent_replicas:
            child_replica_id = None
            parent_replica_id = None
            child_replica = None
            parent_replica = None
            for replica in child_replicas.get_list():
                if replica["replicaName"].lower() == replica_name.lower():
                    child_replica_id = replica["replicaID"]
                    break
            for replica in parent_replicas.get_list():
                if replica["replicaName"].lower() == replica_name.lower():
                    parent_replica_id = replica["replicaID"]
                    break
            if child_replica_id and parent_replica_id:
                import tempfile
                import os

                child_replica = child_replicas.get(replica_id=child_replica_id)
                parent_replica = parent_replicas.get(replica_id=parent_replica_id)
                delta = parent_fs._synchronize_replica(
                    replica_id=parent_replica_id,
                    transport_type="esriTransportTypeUrl",
                    close_replica=False,
                    return_ids_for_adds=False,
                    return_attachment_databy_url=True,
                    asynchronous=False,
                    sync_direction="download",
                    sync_layers=parent_replica["layerServerGens"],
                    edits_upload_format="sqlite",
                    data_format="sqlite",
                    rollback_on_failure=False,
                    out_path=tempfile.gettempdir(),
                )
                if os.path.isfile(delta) == False:
                    return True
                work, message = child_fs.upload(path=delta)
                if (
                    isinstance(message, dict)
                    and "item" in message
                    and "itemID" in message["item"]
                ):
                    syncLayers_child = child_replica["layerServerGens"]
                    syncLayers_parent = parent_replica["layerServerGens"]
                    for i in range(len(syncLayers_parent)):
                        syncLayers_child[i]["serverSibGen"] = syncLayers_parent[i][
                            "serverGen"
                        ]
                        syncLayers_child[i]["syncDirection"] = "upload"
                    child_fs._synchronize_replica(
                        replica_id=child_replica_id,
                        sync_layers=syncLayers_child,
                        sync_direction=None,
                        edits_upload_id=message["item"]["itemID"],
                        return_ids_for_adds=False,
                        data_format="sqlite",
                        asynchronous=False,
                        edits_upload_format="sqlite",
                        rollback_on_failure=False,
                    )
                    return True
                else:
                    return False
            else:
                raise ValueError(
                    "Could not find replica name %s in both services" % replica_name
                )
        else:
            return False


###########################################################################
class WebHook(object):
    """
    The Webhook represents a single hook instance.
    """

    _properties = None
    _url = None
    _gis = None
    # ----------------------------------------------------------------------

    def __init__(self, url, gis):
        self._url = url
        self._gis = gis

    # ----------------------------------------------------------------------
    def __str__(self):
        """returns the class as a string"""
        return f"< WebHook @ {self._url} >"

    # ----------------------------------------------------------------------
    def __repr__(self):
        return self.__str__()

    # ----------------------------------------------------------------------
    @property
    def properties(self) -> PropertyMap:
        """
        Returns the WebHook's properties

        :return: PropertyMap
        """
        if self._properties is None:
            self._properties = PropertyMap(
                self._gis._con.post(self._url, {"f": "json"})
            )
        return self._properties

    # ----------------------------------------------------------------------
    def edit(
        self,
        name: str | None = None,
        change_types: WebHookEvents | str | None = None,
        hook_url: str | None = None,
        signature_key: str | None = None,
        active: bool | None = None,
        schedule_info: WebHookScheduleInfo | dict[str, Any] | None = None,
        payload_format: str | None = None,
    ) -> dict:
        """
        Updates the existing WebHook's Properties.

        =====================================    ===========================================================================
        **Parameter**                             **Description**
        -------------------------------------    ---------------------------------------------------------------------------
        name                                     Optional String. Use valid name for a webhook. This name needs to be unique per service.
        -------------------------------------    ---------------------------------------------------------------------------
        hook_url                                 Optional String.  The URL to which the payloads will be delivered.
        -------------------------------------    ---------------------------------------------------------------------------
        change_types                             Optional :class:`~arcgis.features.managers.WebHookEvents` or String.
                                                 The default is "*", which means all events.  This is a
                                                 comma separated list of values that will fire off the web hook.  The list
                                                 each supported type is below.
        -------------------------------------    ---------------------------------------------------------------------------
        signature_key                            Optional String. If specified, the key will be used in generating the HMAC
                                                 hex digest of value using sha256 hash function and is return in the
                                                 x-esriHook-Signature header.
        -------------------------------------    ---------------------------------------------------------------------------
        active                                   Optional bool. Enable or disable call backs when the webhook is triggered.
        -------------------------------------    ---------------------------------------------------------------------------
        schedule_info                            Optional :class:`~arcgis.features.managers.WebHookScheduleInfo` or Dict.
                                                 Allows the trigger to be used as a given schedule.

                                                 Example Dictionary:


                                                     | {
                                                     |    "name" : "Every-5seconds",
                                                     |    "startAt" : 1478280677536,
                                                     |    "state" : "enabled",
                                                     |    "recurrenceInfo" : {
                                                     |     "frequency" : "second",
                                                     |     "interval" : 5
                                                     |   }
                                                     | }

        -------------------------------------    ---------------------------------------------------------------------------
        payload_format                           Optional String. The payload can be sent in pretty format or standard.
                                                 The default is `json`.
        =====================================    ===========================================================================


        A list of allowed web hook triggers is shown below.

        =====================================    ===========================================================================
        **Name**                                 **Triggered When**
        -------------------------------------    ---------------------------------------------------------------------------
        `*`                                      Wildcard event. Any time any event is triggered.
        -------------------------------------    ---------------------------------------------------------------------------
        `FeaturesCreated`                        A new feature is created
        -------------------------------------    ---------------------------------------------------------------------------
        `FeaturesUpdated`                        Any time a feature is updated
        -------------------------------------    ---------------------------------------------------------------------------
        `FeaturesDeleted`                        Any time a feature is deleted
        -------------------------------------    ---------------------------------------------------------------------------
        `FeaturesEdited`                         Any time a feature is edited (insert or update or delete)
        -------------------------------------    ---------------------------------------------------------------------------
        `AttachmentsCreated`                     Any time adding a new attachment to a feature
        -------------------------------------    ---------------------------------------------------------------------------
        `AttachmentsUpdated`                     Any time updating a feature attachment
        -------------------------------------    ---------------------------------------------------------------------------
        `AttachmentsDeleted`                     Any time an attachment is deleted from a feature
        -------------------------------------    ---------------------------------------------------------------------------
        `LayerSchemaChanged`                     Any time a schema is changed in a layer
        -------------------------------------    ---------------------------------------------------------------------------
        `LayerDefinitionChanged`                 Any time a layer definition is changed
        -------------------------------------    ---------------------------------------------------------------------------
        `FeatureServiceDefinitionChanged`        Any time a feature service is changed
        =====================================    ===========================================================================


        :return: Response of edit as a dict.

        """
        props = dict(self.properties)
        url = f"{self._url}/edit"
        if isinstance(schedule_info, WebHookScheduleInfo):
            schedule_info = schedule_info.as_dict()
        if isinstance(change_types, list):
            ctypes = []
            for ct in change_types:
                if isinstance(ct, WebHookEvents):
                    ctypes.append(ct.value)
                else:
                    ctypes.append(ct)

            change_types = ",".join(ctypes)
        elif isinstance(change_types, WebHookEvents):
            change_types = change_types.value
        elif change_types is None:
            change_types = ",".join(self.properties["changeTypes"])
        params = {
            "f": "json",
            "name": name,
            "changeTypes": change_types,
            "signatureKey": signature_key,
            "hookUrl": hook_url,
            "active": active,
            "scheduleInfo": schedule_info,
            "payloadFormat": payload_format,
        }
        for k in list(params.keys()):
            if params[k] is None:
                params.pop(k)
            del k
        props.update(params)
        resp = self._gis._con.post(url, props)
        self._properties = PropertyMap(resp)
        return resp

    # ----------------------------------------------------------------------
    def delete(self) -> bool:
        """
        Deletes the current webhook from the system

        :return: Boolean, True if successful
        """
        url = f"{self._url}/delete"
        params = {"f": "json"}
        resp = self._gis._con.post(url, params)
        return resp["status"] == "success"


###########################################################################
class WebHookServiceManager(object):
    """
    The `WebHookServiceManager` allows owners and administrators wire feature
    service specific events to :class:`~arcgis.features.FeatureLayerCollection`.
    """

    _fc = None
    _url = None
    _gis = None
    # ----------------------------------------------------------------------

    def __init__(self, url, fc, gis) -> None:
        self._url = url
        self._fc = fc
        self._gis = gis

    # ----------------------------------------------------------------------
    def __str__(self):
        """returns the class as a string"""
        return f"< WebHookServiceManager @ {self._url} >"

    # ----------------------------------------------------------------------
    def __repr__(self):
        return self.__str__()

    # ----------------------------------------------------------------------
    @property
    def properties(self) -> PropertyMap:
        """
        Gets the properties for the WebHook Service Manager and returns
        a PropertyMap object
        """
        return PropertyMap(self._gis._con.post(self._url, {"f": "json"}))

    # ----------------------------------------------------------------------
    @property
    def list(self) -> tuple:
        """
        Get a list of web hooks on the :class:`~arcgis.features.FeatureLayerCollection`

        :return: tuple[:class:`~arcgis.features.managers.WebHook`]

        """
        resp = self._gis._con.post(self._url, {"f": "json"})
        ret = [
            WebHook(url=self._url + f"/{d['globalId']}", gis=self._gis) for d in resp
        ]
        return ret

    # ----------------------------------------------------------------------
    def create(
        self,
        name: str,
        hook_url: str,
        change_types: WebHookEvents | str = WebHookEvents.ALL,
        signature_key: str | None = None,
        active: bool = False,
        schedule_info: dict[str, Any] | WebHookScheduleInfo | None = None,
        payload_format: str = "json",
        content_type: str | None = None,
    ) -> WebHook:
        """

        Creates a new Feature Collection Web Hook


        =====================================    ===========================================================================
        **Parameter**                             **Description**
        -------------------------------------    ---------------------------------------------------------------------------
        name                                     Required String. Use valid name for a webhook. This name needs to be unique per service.
        -------------------------------------    ---------------------------------------------------------------------------
        hook_url                                 Required String.  The URL to which the payloads will be delivered.
        -------------------------------------    ---------------------------------------------------------------------------
        change_types                             Optional WebHookEvents or String.  The default is "WebHookEvents.ALL", which means all events.  This is a
                                                 comma separated list of values that will fire off the web hook.  The list
                                                 each supported type is below.
        -------------------------------------    ---------------------------------------------------------------------------
        signature_key                            Optional String. If specified, the key will be used in generating the HMAC
                                                 hex digest of value using sha256 hash function and is return in the
                                                 x-esriHook-Signature header.
        -------------------------------------    ---------------------------------------------------------------------------
        active                                   Optional bool. Enable or disable call backs when the webhook is triggered.
        -------------------------------------    ---------------------------------------------------------------------------
        schedule_info                            Optional Dict or `WebHookScheduleInfo`. Allows the trigger to be used as a given schedule.

                                                 Example Dictionary:

                                                     | {
                                                     |   "name" : "Every-5seconds",
                                                     |   "startAt" : 1478280677536,
                                                     |   "state" : "enabled"
                                                     |   "recurrenceInfo" : {
                                                     |     "frequency" : "second",
                                                     |     "interval" : 5
                                                     |   }
                                                     | }

        -------------------------------------    ---------------------------------------------------------------------------
        payload_format                           Optional String. The payload can be sent in pretty format or standard.
                                                 The default is `json`.
        -------------------------------------    ---------------------------------------------------------------------------
        content_type                             Optional String. The Content Type is used to indicate the media type of the
                                                 resource. The media type is a string sent along with the file indicating
                                                 the format of the file.
        =====================================    ===========================================================================


        A list of allowed web hook triggers is shown below.

        =====================================    ===========================================================================
        **Name**                                 **Triggered When**
        -------------------------------------    ---------------------------------------------------------------------------
        `*`                                      Wildcard event. Any time any event is triggered.
        -------------------------------------    ---------------------------------------------------------------------------
        `FeaturesCreated`                        A new feature is created
        -------------------------------------    ---------------------------------------------------------------------------
        `FeaturesUpdated`                        Any time a feature is updated
        -------------------------------------    ---------------------------------------------------------------------------
        `FeaturesDeleted`                        Any time a feature is deleted
        -------------------------------------    ---------------------------------------------------------------------------
        `FeaturesEdited`                         Any time a feature is edited (insert or update or delete)
        -------------------------------------    ---------------------------------------------------------------------------
        `AttachmentsCreated`                     Any time adding a new attachment to a feature
        -------------------------------------    ---------------------------------------------------------------------------
        `AttachmentsUpdated`                     Any time updating a feature attachment
        -------------------------------------    ---------------------------------------------------------------------------
        `AttachmentsDeleted`                     Any time an attachment is deleted from a feature
        -------------------------------------    ---------------------------------------------------------------------------
        `LayerSchemaChanged`                     Any time a schema is changed in a layer
        -------------------------------------    ---------------------------------------------------------------------------
        `LayerDefinitionChanged`                 Any time a layer definition is changed
        -------------------------------------    ---------------------------------------------------------------------------
        `FeatureServiceDefinitionChanged`        Any time a feature service is changed
        =====================================    ===========================================================================

        :return:
            A :class:`~arcgis.features.managers.WebHook` object

        """
        url = f"{self._url}/create"
        if isinstance(change_types, list):
            ctnew = []
            for ct in change_types:
                if isinstance(ct, str):
                    ctnew.append(ct)
                elif isinstance(ct, WebHookEvents):
                    ctnew.append(ct.value)
            change_types = ",".join(ctnew)
        elif isinstance(change_types, WebHookEvents):
            change_types = change_types.value
        if isinstance(schedule_info, WebHookScheduleInfo):
            schedule_info = schedule_info.as_dict()
        params = {
            "f": "json",
            "name": name,
            "changeTypes": change_types,
            "signatureKey": signature_key,
            "hookUrl": hook_url,
            "active": active,
            "scheduleInfo": schedule_info,
            "payloadFormat": payload_format,
        }
        if content_type:
            params["contentType"] = content_type
        resp = self._gis._con.post(url, params)
        if not "url" in resp:
            if "globalId" in resp:
                guid = resp.get("globalId")
            elif "id" in resp:
                guid = resp.get("id")
            else:
                raise Exception(str(resp))
            hook_url = self._url + f"/{guid}"
            return WebHook(url=hook_url, gis=self._gis)
        else:
            return WebHook(url=resp["url"], gis=self._gis)

    # ----------------------------------------------------------------------
    def enable_hooks(self) -> bool:
        """
        The `enable_hooks` operation restarts a deactivated webhook. When
        activated, payloads will be delivered to the payload URL when the
        webhook is invoked.

        :return: Bool, True if successful

        """
        url = f"{self._url}/activateAll"
        params = {"f": "json"}
        return self._gis._con.post(url, params).get("status", "failed") == "success"

    # ----------------------------------------------------------------------
    def disable_hooks(self) -> bool:
        """
        The `disable_hooks` will turn off all web hooks for the current service.

        :return: Bool, True if successful

        """
        url = f"{self._url}/deactivateAll"
        params = {"f": "json"}
        return self._gis._con.post(url, params).get("status", "failed") == "success"

    # ----------------------------------------------------------------------
    def delete_all_hooks(self) -> bool:
        """
        The `delete_all_hooks` operation will permanently remove the specified webhook.

        :return: Bool, True if successful

        """
        url = f"{self._url}/deleteAll"
        params = {"f": "json"}
        return self._gis._con.post(url, params).get("status", "failed") == "success"


###########################################################################
class FeatureLayerCollectionManager(_GISResource):
    """
    Allows updating the definition (if access permits) of a :class:`~arcgis.features.FeatureLayerCollection`.
    This class is not created by users directly.
    An instance of this class, called 'manager', is available as a property of the :class:`~arcgis.features.FeatureLayerCollection` object.

    Users call methods on this 'manager' object to manage the feature layer collection.
    """

    _layers = None
    _tables = None

    def __init__(self, url, gis=None, fs=None):
        super(FeatureLayerCollectionManager, self).__init__(url, gis)
        self._fs = fs
        self._wh = None
        self._tp = _cf.ThreadPoolExecutor(5)

    @property
    def layers(self) -> list:
        """
        Returns a list of :class:`~arcgis.features.managers.FeatureLayerManager` to work with FeatureLayers

        :returns: List[:class:`~arcgis.features.managers.FeatureLayerManager`]
        """
        self._layers = []
        if "layers" in self.properties:
            for table in self.properties.layers:
                try:
                    self._layers.append(
                        FeatureLayerManager(
                            self.url + "/" + str(table["id"]), self._gis
                        )
                    )
                except Exception as e:
                    _log.error(str(e))

        return self._layers

    @property
    def tables(self) -> list:
        """
        Returns a list of :class:`~arcgis.features.managers.FeatureLayerManager` to work with tables

        :returns: List[:class:`~arcgis.features.managers.FeatureLayerManager`]
        """
        self._tables = []
        if "tables" in self.properties:
            for table in self.properties.tables:
                try:
                    self._tables.append(
                        FeatureLayerManager(
                            self.url + "/" + str(table["id"]), self._gis
                        )
                    )
                except Exception as e:
                    _log.error(str(e))
        return self._tables

    def _populate_layers(self):
        """
        populates layers and tables in the managed feature service
        """
        return

    @property
    def webhook_manager(self) -> WebHookServiceManager:
        """
        :return:
            :class:`~arcgis.features.managers.WebHookServiceManager`
        """
        if self._gis.version >= [8, 2] and self._gis._portal.is_arcgisonline:
            if self._wh is None:
                self._wh = WebHookServiceManager(
                    url=self._url + "/WebHooks", fc=self._fs, gis=self._gis
                )
            return self._wh
        elif self._gis.version >= [8, 2] and self._gis._portal.is_arcgisonline == False:
            return self._fs.service.webhook_manager
        return None

    # ----------------------------------------------------------------------
    def refresh(self):
        """refreshes a feature layer collection"""
        params = {"f": "json"}
        refresh_url = self._url + "/refresh"
        res = self._con.post(refresh_url, params)

        super(FeatureLayerCollectionManager, self)._refresh()
        self._populate_layers()

        self._fs._refresh()
        self._fs._populate_layers()

        return res

    # ----------------------------------------------------------------------
    @property
    def generate_service_definition(self):
        """
        Returns a dictionary can be used for service generation.

        :return: dict or None (if not supported on the service)

        """
        return self._generate_mapservice_definition()

    # ----------------------------------------------------------------------
    def _generate_mapservice_definition(self):
        """
        This operation returns a map service JSON that can be used to
        create a service.

        If a service does not support this operation, None is returned.

        :return:
           dictionary
        """
        params = {
            "f": "json",
        }
        url = "%s/generateMapServiceDefinition" % self._url
        try:
            res = self._con.post(url, params)
        except:
            res = None
        return res

    # ----------------------------------------------------------------------
    def _perform_insert(self, layer_definition, table=False):
        """
        This adds the layer definition to the feature service definition. It also
        checks for the field mappings and returns them for future appends of data.
        We have to do this because the field names can change when adding a new layer, especially in Enterprise
        which depends on a geodatabase design and thus some field names are reserved.
        """
        # Add new layer to definition
        if isinstance(layer_definition, PropertyMap):
            layer_definition = dict(layer_definition)

        # Extract original field names for comparison later
        original_field_names = [
            field["name"] for field in layer_definition.get("fields", [])
        ]

        if table:
            self.add_to_definition({"tables": [layer_definition]})
            for table in self.properties.tables:
                if table["name"] == layer_definition["name"]:
                    fl_index = table["id"]
                    break
        else:
            self.add_to_definition({"layers": [layer_definition]})
            # Find the index at which the layer was added
            for layer in self.properties.layers:
                if layer["name"] == layer_definition["name"]:
                    fl_index = layer["id"]
                    break

        # Check if any field names have changed
        updated_fields_names = [
            field["name"] for field in self.properties.layers[fl_index]["fields"]
        ]
        field_mappings = []
        for original_field in original_field_names:
            for updated_field in updated_fields_names:
                if original_field != updated_field and original_field in updated_field:
                    field_mappings.append(
                        {"name": updated_field, "sourceName": original_field}
                    )
                    # Log or send a warning about the change
                    print(
                        f"Warning: Field '{original_field}' was renamed to '{updated_field}'"
                    )

        # Return the index and field mappings to use for future appends
        return fl_index, field_mappings

    # ----------------------------------------------------------------------
    def insert_layer(self, data_path: str, name: str = None):
        """
        This method will create a feature layer or table and insert it into the existing feature service.
        If your data path will publish more than one layer or table, only the first will be added.

        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        data_path              Required string. The path to the data to be inserted.

                               .. note::
                                   Shapefiles and file geodatabases must be in a .zip file.
        ------------------     --------------------------------------------------------------------
        name                   Optional string. The name of the layer or table to be created.
        ==================     ====================================================================
        """
        # Check that the user is the owner of both the source and the published item or has administrative privileges
        new_item = None
        orig_item = self._gis.content.get(self.properties.serviceItemId)
        if (
            self._gis.users.me.username != orig_item.owner
            and "portal:admin:updateItems" not in self._gis.users.me.privileges
        ):
            raise AssertionError(
                "You must own the service to insert data to it or have administrative privileges."
            )
        # Get the data related
        related_items = orig_item.related_items(rel_type="Service2Data")
        for i in related_items:
            if (
                self._gis.users.me.username != i.owner
                and "portal:admin:updateItems" not in self._gis.users.me.privileges
            ):
                raise AssertionError(
                    "You must own the service data to insert data or have the administrative privilege to update items (portal:admin:updateItems)."
                )

        # Get the name for new service if None passed, ensure data_path has all special characters removed and spaces removed
        if name is None:
            name = os.path.basename(data_path)
            name = re.sub(r"\.", "_", name)

        # Get the file type
        file_type = os.path.splitext(data_path)[1]
        file_types = {
            ".csv": "CSV",
            ".sqlite": "SQLite",
            ".xls": "Excel",
            ".xlsx": "Excel",
            ".xml": "XML",
            ".sd": "Service Definition",
            ".zip": "Zipfile",
        }
        file_type = file_types.get(file_type, None)
        if file_type is None:
            raise ValueError(
                "File type not supported. Supported file types are: zipped shapefiles, zipped file geodatabases, CSV, Excel, XML, SQLite, and Service Definition."
            )

        # Check if the zipfile is a shapefile or file geodatabase
        if file_type == "Zipfile":
            shapefile = _common_utils._is_shapefile(data_path)
            if shapefile:
                file_type = "Shapefile"
            else:
                file_type = "File Geodatabase"

        # Add to the same folder as the service
        folder_id = orig_item.ownerFolder
        if folder_id:
            folder = self._gis.content.folders.get(folder_id)
        else:
            folder = self._gis.content.folders.get()

        try:
            file_item = folder.add(
                item_properties={
                    "type": file_type,
                    "title": name,
                    "tags": "inserted",
                },
                file=data_path,
            ).result()
        except Exception as e:
            if "Item with this filename already exists" not in str(e):
                raise e
            # rename the file item if it already exists with unique id appended
            file_item = folder.add(
                item_properties={
                    "type": file_type,
                    "title": name,
                    "tags": "inserted",
                    "fileName": os.path.splitext(data_path)[0]
                    + "_"
                    + str(uuid.uuid4())[0:5]
                    + ".zip",
                },
                file=data_path,
            ).result()

        publish_parameters = {}
        lyr_info = {}
        if not self._gis._is_arcgisonline:
            # FileGeodatabase has to be published first to get the layer info
            new_item = file_item.publish()
            lyr_info = new_item.layers[0].properties
        else:
            # Analyze the file to get publish parameters
            analyze_ft = file_type.lower().replace(" ", "")
            publish_parameters = self._gis.content.analyze(
                item=file_item, file_type=analyze_ft
            )["publishParameters"]

        # Get the layer info which will be used to append the data
        if file_type == "CSV" or file_type == "Excel":
            lyr_info = publish_parameters["layerInfo"]
        elif not lyr_info:
            # Shapefile or file geodatabase online
            lyr_info = publish_parameters["layers"][0]

        try:
            # Insert layer or table
            if file_type == "File Geodatabase":
                upload_format = "filegdb"
            else:
                upload_format = file_type.lower()
            if lyr_info and lyr_info["type"] == "Feature Layer":
                index, field_mappings = self._perform_insert(lyr_info)
                append_item_id = file_item.id
                layer_mappings = []
                if (
                    upload_format
                    not in orig_item.layers[index].properties["supportedAppendFormats"]
                    or new_item
                ):
                    upload_format = "featureService"
                    if not new_item:
                        # special case
                        new_item = file_item.publish()
                    append_item_id = new_item.id
                    layer_mappings = [{"id": index, "sourceId": 0}]
                # Use append
                orig_item.layers[index].append(
                    item_id=append_item_id,
                    upload_format=upload_format,
                    source_table_name=lyr_info["name"],
                    field_mappings=field_mappings,
                    layer_mappings=layer_mappings,
                    upsert=True,  # avoid duplicate append
                )
            elif lyr_info["type"] == "Table":
                index, field_mappings = self._perform_insert(lyr_info, table=True)
                orig_item.tables[index].append(
                    item_id=file_item.id,
                    upload_format=upload_format,
                    source_info=lyr_info,
                    field_mappings=field_mappings,
                    layer_mappings=[{"id": index, "sourceId": 0}],
                    return_messages=True,
                )

        except Exception as e:
            raise e
        finally:
            # Remove items created since no need for them anymore
            # relationship not needed for hosted services
            self._gis.content.delete_items([file_item], permanent=True)
            if new_item:
                self._gis.content.delete_items([new_item], permanent=True)

        return orig_item

    def swap_view(
        self,
        index: int,
        new_source: features.FeatureLayer | features.Table,
        future: bool = False,
    ) -> dict | concurrent.futures.Future:
        """
        Swaps the Data Source Layer with a different parent layer.

        ==================     ====================================================================
        **Parameter**           **Description**
        ------------------     --------------------------------------------------------------------
        index                  Required int. The index of the layer on the view to replace.
        ------------------     --------------------------------------------------------------------
        new_source             Required FeatureLayer or Table. The layer to replace the existing
                               source with.
        ------------------     --------------------------------------------------------------------
        future                 Optional Bool. When True, a Future object will be returned else a
                               JSON object.
        ==================     ====================================================================

        :return: dict | concurrent.futures.Future
        """
        return self._swap_view(
            view=self._fs, index=index, new_source=new_source, future=future
        )

    def _swap_view(
        self,
        view: features.FeatureLayerCollection,
        index: int,
        new_source: features.FeatureLayer | features.Table,
        future: bool = False,
    ) -> dict | concurrent.futures.Future:
        """
        Swaps the Data Source Layer with a different parent layer.

        ==================     ====================================================================
        **Parameter**           **Description**
        ------------------     --------------------------------------------------------------------
        view                   Required FeatureLayerCollection. The view feature layer collection
                               to update.
        ------------------     --------------------------------------------------------------------
        index                  Required int. The index of the layer on the view to replace.
        ------------------     --------------------------------------------------------------------
        new_source             Required FeatureLayer or Table. The layer to replace the existing
                               source with.
        ------------------     --------------------------------------------------------------------
        future                 Optional Bool. When True, a Future object will be returned else a
                               JSON object. This parameter is only honored for the ArcGIS Online
                               platform.
        ==================     ====================================================================

        :return: dict | concurrent.futures.Future
        """
        keys: list[str] = [
            "currentVersion",
            "id",
            "name",
            "type",
            "displayField",
            "description",
            "copyrightText",
            "defaultVisibility",
            "editingInfo",
            "isDataVersioned",
            "hasContingentValuesDefinition",
            "supportsAppend",
            "supportsCalculate",
            "supportsASyncCalculate",
            "supportsTruncate",
            "supportsAttachmentsByUploadId",
            "supportsAttachmentsResizing",
            "supportsRollbackOnFailureParameter",
            "supportsStatistics",
            "supportsExceedsLimitStatistics",
            "supportsAdvancedQueries",
            "supportsValidateSql",
            "supportsCoordinatesQuantization",
            "supportsLayerOverrides",
            "supportsTilesAndBasicQueriesMode",
            "supportsFieldDescriptionProperty",
            "supportsQuantizationEditMode",
            "supportsApplyEditsWithGlobalIds",
            "supportsMultiScaleGeometry",
            "supportsReturningQueryGeometry",
            "hasGeometryProperties",
            "geometryProperties",
            "advancedQueryCapabilities",
            "advancedQueryAnalyticCapabilities",
            "advancedEditingCapabilities",
            "infoInEstimates",
            "useStandardizedQueries",
            "geometryType",
            "minScale",
            "maxScale",
            "extent",
            "drawingInfo",
            "allowGeometryUpdates",
            "hasAttachments",
            "htmlPopupType",
            "hasMetadata",
            "hasM",
            "hasZ",
            "objectIdField",
            "uniqueIdField",
            "globalIdField",
            "typeIdField",
            "dateFieldsTimeReference",
            "preferredTimeReference",
            "types",
            "templates",
            "supportedQueryFormats",
            "supportedAppendFormats",
            "supportedExportFormats",
            "supportedSpatialRelationships",
            "supportedContingentValuesFormats",
            "supportedSyncDataOptions",
            "hasStaticData",
            "maxRecordCount",
            "standardMaxRecordCount",
            "standardMaxRecordCountNoGeometry",
            "tileMaxRecordCount",
            "maxRecordCountFactor",
            "capabilities",
            "url",
            "adminLayerInfo",
        ]
        if isinstance(new_source, features.FeatureLayer):
            flc_lyr_info: features.FeatureLayer = view.layers[index]
        elif isinstance(new_source, features.Table):
            flc_lyr_info: features.Table = view.tables[index]
        props: dict = {
            key: new_source.properties[key]
            for key in keys
            if key in new_source.properties
        }
        if new_source._con.token:
            props["url"] = new_source.url + f"?token={new_source._con.token}"
        else:
            props["url"] = new_source.url
        if "viewLayerDefinition" in flc_lyr_info.manager.properties["adminLayerInfo"]:
            props["adminLayerInfo"] = {}
            props["adminLayerInfo"]["viewLayerDefinition"] = (
                flc_lyr_info.manager.properties["adminLayerInfo"]["viewLayerDefinition"]
            )
            props["adminLayerInfo"]["viewLayerDefinition"]["sourceServiceName"] = (
                os.path.basename(os.path.dirname(os.path.dirname(new_source.url)))
            )
            props["adminLayerInfo"]["viewLayerDefinition"].pop("sourceId", None)
        if isinstance(new_source, features.FeatureLayer):
            delete_json: dict = {"layers": [{"id": index}], "tables": []}
            add_json: dict = {"layers": [props]}
        elif isinstance(new_source, features.Table):
            delete_json: dict = {"layers": [], "tables": [{"id": index}]}
            add_json: dict = {"tables": [props]}
        view.manager.delete_from_definition(delete_json)
        if future and self._gis._is_arcgisonline:
            return view.manager.add_to_definition(add_json, future=True)
        else:
            if future and self._gis._is_arcgisonline == False:
                _log.warning(
                    "Enterprise does not support asynchronous view swap, using synchronous method."
                )
            return view.manager.add_to_definition(add_json, future=False)

    # ----------------------------------------------------------------------
    def create_view(
        self,
        name: str,
        spatial_reference: dict[str, Any] | None = None,
        extent: dict[str, int] | None = None,
        allow_schema_changes: bool = True,
        updateable: bool = True,
        capabilities: str = "Query",
        view_layers: list[int] | None = None,
        view_tables: list[int] | None = None,
        *,
        description: str | None = None,
        tags: str | None = None,
        snippet: str | None = None,
        overwrite: bool | None = None,
        set_item_id: str | None = None,
        preserve_layer_ids: bool = True,
        visible_fields: list[str] | None = None,
        query: str | None = None,
        folder: _cm.Folder | str | None = None,
    ):
        """
        Creates a view of an existing feature service. You can create a view, if you need a different view of the data
        represented by a hosted feature layer, for example, you want to apply different editor settings, apply different
        styles or filters, define which features or fields are available, or share the data to different groups than
        the hosted feature layer  create a hosted feature layer view of that hosted feature layer.

        When you create a feature layer view, a new hosted feature layer item is added to Content. This new layer is a
        view of the data in the hosted feature layer, which means updates made to the data appear in the hosted feature
        layer and all of its hosted feature layer views. However, since the view is a separate layer, you can change
        properties and settings on this item separately from the hosted feature layer from which it is created.

        For example, you can allow members of your organization to edit the hosted feature layer but share a read-only
        feature layer view with the public.

        To learn more about views visit: https://doc.arcgis.com/en/arcgis-online/share-maps/create-hosted-views.htm

        ====================     ====================================================================
        **Parameter**             **Description**
        --------------------     --------------------------------------------------------------------
        name                     Required string. Name of the new view item
        --------------------     --------------------------------------------------------------------
        spatial_reference        Optional dict. Specify the spatial reference of the view
        --------------------     --------------------------------------------------------------------
        extent                   Optional dict. Specify the extent of the view
        --------------------     --------------------------------------------------------------------
        allow_schema_changes     Optional bool. Default is True. Determines if a view can alter a
                                 service's schema.
        --------------------     --------------------------------------------------------------------
        updateable               Optional bool. Default is True. Determines if view can update values
        --------------------     --------------------------------------------------------------------
        capabilities             Optional string. Specify capabilities as a comma separated string.
                                 For example "Query, Update, Delete". Default is 'Query'.
        --------------------     --------------------------------------------------------------------
        view_layers              Optional list. Specify list of layers present in the FeatureLayerCollection
                                 that you want in the view.
        --------------------     --------------------------------------------------------------------
        view_tables              Optional list. Specify list of tables present in the FeatureLayerCollection
                                 that you want in the view.
        --------------------     --------------------------------------------------------------------
        description              Optional String. A user-friendly description for the published dataset.
        --------------------     --------------------------------------------------------------------
        tags                     Optional String. The comma separated string of descriptive words.
        --------------------     --------------------------------------------------------------------
        snippet                  Optional String. A short description of the view item.
        --------------------     --------------------------------------------------------------------
        overwrite                Not supported.

                                 .. note::
                                     To overwrite the data used in a hosted feature layer view, you
                                     must overwrite the hosted feature layer from which it was
                                     created. See the `ArcGIS Online Overwrite hosted feature layers <https://doc.arcgis.com/en/arcgis-online/manage-data/manage-hosted-feature-layers.htm#ESRI_SECTION1_1D3A87A80E3E4CD2A71744715F1522FE>`_
                                     or the `ArcGIS Enterprise Overwrite hosted feature layers <https://enterprise.arcgis.com/en/portal/latest/use/manage-hosted-feature-layers.htm#ESRI_SECTION1_1D3A87A80E3E4CD2A71744715F1522FE>`_
                                     documentation for requirements and considerations for
                                     overwriting. See also `Considerations when creating hosted feature layer views <https://doc.arcgis.com/en/arcgis-online/manage-data/create-hosted-views.htm#GUID-E4F46139-1F6E-4036-8C4F-EF73C2C2CE72>`_
                                     for additional criteria for overwriting.
        --------------------     --------------------------------------------------------------------
        set_item_id              Optional String. If set, the item id is defined by the user rather
                                 than the system. The parameter requires
                                 *ArcGIS Enterprise 11.1 or higher*.

                                 .. note::
                                     This parameter is not available for ArcGIS Online.
        --------------------     --------------------------------------------------------------------
        preserve_layer_ids       Optional Boolean. Preserves the layer's `id` on it's definition when `True`.  The default is `True`.
        --------------------     --------------------------------------------------------------------
        visible_fields           Optional list[str] or None. A list of visible fields to display.
        --------------------     --------------------------------------------------------------------
        query                    Optional String. A SQL statement that defines the view.
        --------------------     --------------------------------------------------------------------
        folder                   Optional string or Folder. The folder to which the view will be saved.
        ====================     ====================================================================

        .. code-block:: python  (optional)

           USAGE EXAMPLE: Create a view from a hosted feature layer

           crime_fl_item = gis.content.search("2012 crime")[0]
           crime_flc = FeatureLayerCollection.fromitem(crime_fl_item)

           # Create a view with just the first layer
           crime_view = crime_flc.manager.create_view(name='Crime in 2012", updateable=False,
                                                        view_layers=[crime_flc.layers[0]])

        .. code-block:: python (optional)

            USAGE EXAMPLE: Create an editable view

            crime_fl_item = gis.content.search("2012 crime")[0]
            crime_flc = FeatureLayerCollection.fromitem(crime_fl_item)
            crime_view = crime_flc.manager.create_view(name=uuid.uuid4().hex[:9], # create random name
                                                       updateable=True,
                                                       allow_schema_changes=False,
                                                       capabilities="Query,Update,Delete")

        :return:
            Returns the newly created :class:`~arcgis.gis.Item` for the view.
        """
        # check name doesn't contain invalid characters
        invalid_char_regex: str = r"[$&+,:;=?@#|'<>.^*()%!-]"
        if len(re.findall(invalid_char_regex, name)) > 0:
            raise ValueError(
                "The service `name` cannot contain any spaces or special characters except underscores."
            )

        # check if hosted service
        if "serviceItemId" not in self.properties:
            raise Exception(
                "A registered hosted feature service is required to use create_view"
            )

        # get the FeatureLayerCollection
        gis = self._gis
        content = gis.content
        item = content.get(itemid=self.properties["serviceItemId"])
        fs = features.FeatureLayerCollection(url=item.url, gis=gis)

        rest_url = gis.resturl

        # get the owner of the service
        user = item["owner"] if "owner" in item else gis.users.me.username

        # get create service endpoint
        url = "%s/content/users/%s/createService" % (rest_url, user)

        # handle for tables
        if spatial_reference is None and "spatialReference" in fs.properties:
            # else it stays the spatial reference given or None
            spatial_reference = fs.properties["spatialReference"]

        create_params = {
            "name": name,
            "isView": True,
            "sourceSchemaChangesAllowed": allow_schema_changes,
            "isUpdatableView": updateable,
            "spatialReference": spatial_reference,
            "initialExtent": extent or fs.properties["initialExtent"],
            "capabilities": capabilities or fs.properties["capabilities"],
            "preserveLayerIds": preserve_layer_ids,
            "options": {"dataSourceType": "relational"},
        }

        params = {
            "f": "json",
            "isView": True,
            "createParameters": json.dumps(create_params),
            "tags": tags if tags else ",".join(item.tags),
            "snippet": snippet if snippet else item.snippet,
            "description": description if description else item.description,
            "outputType": "featureService",
        }
        if set_item_id:
            params["itemIdToCreate"] = set_item_id
        if overwrite:
            _log.warning(
                "overwrite is currently not supported on this platform, and will not be honored"
            )

        res = gis._session.post(url=url, data=params).json()
        if res["success"] == False:
            if "error" in res and "already exists" in res["error"]["message"]:
                new_name = _common_utils._get_unique_name(name)
                create_params["name"] = new_name
                params["createParameters"] = json.dumps(create_params)
                res = gis._session.post(url=url, data=params).json()
            else:
                raise Exception(res["error"]["message"])
        # Get the view feature layer collection
        view_item = content.get(res["itemId"])
        fs_view = features.FeatureLayerCollection(url=view_item.url, gis=gis)

        # If folder provided, move the view to the folder
        if folder:
            # The move method allows string or Folder object
            view_item.move(folder)

        add_def = {"layers": [], "tables": []}

        def is_none_or_empty(view_param):
            if not view_param:  # Handles None and empty lists/dicts
                return True
            if isinstance(view_param, dict):
                return all(v is None for v in view_param.values())
            return False

        def create_layer_definition(layer, fs, data=None):
            return {
                "adminLayerInfo": {
                    "popupInfo": (
                        data.get("popupInfo") if data and "popupInfo" in data else None
                    ),
                    "viewLayerDefinition": {
                        "sourceServiceName": os.path.basename(os.path.dirname(fs.url)),
                        "sourceLayerId": layer.manager.properties["id"],
                        "sourceLayerFields": "*",
                    },
                },
                "name": layer.manager.properties["name"],
            }

        def create_table_definition(table, fs):
            return {
                "adminLayerInfo": {
                    "viewLayerDefinition": {
                        "sourceServiceName": os.path.basename(os.path.dirname(fs.url)),
                        "sourceLayerId": table.manager.properties["id"],
                        "sourceLayerFields": "*",
                    },
                },
                "id": table.manager.properties["id"],
                "name": table.manager.properties["name"],
                "type": "Table",
            }

        def process_layers(layers, fs, data_fetcher=None):
            return [
                create_layer_definition(
                    layer, fs, data_fetcher(layer) if data_fetcher else None
                )
                for layer in layers
            ]

        def process_tables(tables, fs):
            return [create_table_definition(table, fs) for table in tables]

        def add_definitions(fs, view_layers, view_tables):
            add_def = {"layers": [], "tables": []}

            if is_none_or_empty(view_layers) and is_none_or_empty(view_tables):
                # Process all layers and tables when view_layers/tables are not specified
                add_def["layers"] = process_layers(fs.layers, fs)
                add_def["tables"] = process_tables(fs.tables, fs)
            else:
                # Process specified layers and tables
                if view_layers:
                    add_def["layers"] = process_layers(
                        view_layers, fs, lambda lyr: lyr.properties
                    )
                if view_tables:
                    add_def["tables"] = process_tables(view_tables, fs)

            return add_def

        def update_layer_definition(layer_manager, values, gis_online):
            if gis_online:
                return layer_manager.update_definition(values, future=True).result()
            else:
                return layer_manager.update_definition(values)

        def update_view_extent(fs_view, extent):
            if extent and fs_view.layers:
                for vw_lyr in fs_view.layers:
                    vw_lyr.manager.update_definition(
                        {
                            "viewLayerDefinition": {
                                "filter": {
                                    "operator": "esriSpatialRelIntersects",
                                    "value": {
                                        "geometryType": "esriGeometryEnvelope",
                                        "geometry": extent,
                                    },
                                }
                            }
                        }
                    )

        def update_item_data(view_item, item, view_layers):
            if view_layers:
                data = item.get_data()
                if "layers" in data:
                    item_upd_dict = {
                        "layers": [
                            ilyr
                            for ilyr in data["layers"]
                            for lyr in view_layers
                            if int(lyr.url.split("/")[-1]) == ilyr["id"]
                        ]
                    }
                    view_item.update(data=item_upd_dict)
            else:
                view_item.update(data=item.get_data())

        def set_visible_fields_and_query(item, visible_fields, query, gis):
            if visible_fields or query:
                values = {}
                fields = item.layers[0].properties["fields"]
                if visible_fields:
                    field_names = [f.lower() for f in visible_fields]
                    values["fields"] = [
                        {
                            "name": fld["name"],
                            "visible": fld["name"].lower() in field_names,
                        }
                        for fld in fields
                    ]
                else:
                    values["fields"] = [
                        {"name": fld["name"], "visible": True} for fld in fields
                    ]

                if query:
                    values["viewDefinitionQuery"] = query

                if values:
                    flc = features.FeatureLayerCollection.fromitem(item)
                    lyr = flc.layers[0]
                    update_layer_definition(lyr.manager, values, gis._is_arcgisonline)

        add_def = add_definitions(fs, view_layers, view_tables)
        fs_view.manager.add_to_definition(add_def, future=gis._is_arcgisonline)

        update_view_extent(fs_view, extent)

        view_item = item  # Assuming view_item is passed as item
        update_item_data(view_item, item, view_layers)

        item = gis.content.get(res["itemId"])
        set_visible_fields_and_query(item, visible_fields, query, gis)

        return item

    # ----------------------------------------------------------------------
    def _refresh_callback(self, *args, **kwargs):
        """function to refresh the service post add or update definition for async operations"""
        try:
            self._hydrated = False
            self.refresh()
        except:
            self._hydrated = False

    # ----------------------------------------------------------------------
    def add_to_definition(self, json_dict: dict[str, Any], future: bool = False):
        """
        The add_to_definition operation supports adding a definition
        property to a hosted feature layer collection service. The result of this
        operation is a response indicating success or failure with error
        code and description.

        This function will allow users to change or add additional values
        to an already published service.

        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        json_dict           Required dict. The part to add to the hosted service. The format
                            can be derived from the `properties` property.
                            For layer level modifications, run updates on each individual feature
                            service layer object.

                            Find more information on what this dictionary can contain at:
                            https://developers.arcgis.com/rest/services-reference/enterprise/feature-service/#json-response-syntax
        ---------------     --------------------------------------------------------------------
        future              Optional, If True, a future object will be returns and the process
                            will not wait for the task to complete.
                            The default is False, which means wait for results.
        ===============     ====================================================================

        :return:
           JSON message as dictionary when `future=False` else If ``future = True``,
           then the result is a `Future <https://docs.python.org/3/library/concurrent.futures.html>`_ object. Call ``result()`` to get the response.

        """

        if isinstance(json_dict, PropertyMap):
            json_dict = dict(json_dict)

        params = {
            "f": "json",
            "addToDefinition": json.dumps(json_dict),
            "async": json.dumps(future),
        }
        adddefn_url = self._url + "/addToDefinition"
        res = self._con.post(adddefn_url, params)
        status_url: str = _get_value_case_insensitive(res, "statusurl")
        if future and status_url:
            executor = _cf.ThreadPoolExecutor(1)
            futureobj = executor.submit(
                _check_status,
                **{
                    "url": status_url,
                    "gis": self._gis,
                },
            )
            futureobj.add_done_callback(self._refresh_callback)
            executor.shutdown(False)
            return futureobj
        self.refresh()
        return res

    # ----------------------------------------------------------------------
    def update_definition(self, json_dict: dict[str, Any], future: bool = False):
        """
        The update_definition operation supports updating a definition
        property in a hosted feature layer collection service. The result of this
        operation is a response indicating success or failure with error
        code and description.

        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        json_dict           Required dict. The part to add to the hosted service. The format
                            can be derived from the `properties` property.
                            For layer level modifications, run updates on each individual feature
                            service layer object.
        ---------------     --------------------------------------------------------------------
        future              Optional boolean. If True, a future object will be returns and the process
                            will not wait for the task to complete.
                            The default is False, which means wait for results.
        ===============     ====================================================================

        :return:
           JSON message as dictionary when `future=False`
           when `future=True`, `Future <https://docs.python.org/3/library/concurrent.futures.html>`_ object is returned. Call ``result()`` to get the response.

        """
        definition = None
        if json_dict is not None:
            if isinstance(json_dict, PropertyMap):
                definition = dict(json_dict)
            if isinstance(json_dict, collections.OrderedDict):
                definition = json_dict
            else:
                definition = collections.OrderedDict()
                if "hasStaticData" in json_dict:
                    definition["hasStaticData"] = json_dict["hasStaticData"]
                if "allowGeometryUpdates" in json_dict:
                    definition["allowGeometryUpdates"] = json_dict[
                        "allowGeometryUpdates"
                    ]
                if "capabilities" in json_dict:
                    definition["capabilities"] = json_dict["capabilities"]
                if "editorTrackingInfo" in json_dict:
                    definition["editorTrackingInfo"] = collections.OrderedDict()
                    if "enableEditorTracking" in json_dict["editorTrackingInfo"]:
                        definition["editorTrackingInfo"]["enableEditorTracking"] = (
                            json_dict["editorTrackingInfo"]["enableEditorTracking"]
                        )

                    if (
                        "enableOwnershipAccessControl"
                        in json_dict["editorTrackingInfo"]
                    ):
                        definition["editorTrackingInfo"][
                            "enableOwnershipAccessControl"
                        ] = json_dict["editorTrackingInfo"][
                            "enableOwnershipAccessControl"
                        ]

                    if "allowOthersToUpdate" in json_dict["editorTrackingInfo"]:
                        definition["editorTrackingInfo"]["allowOthersToUpdate"] = (
                            json_dict["editorTrackingInfo"]["allowOthersToUpdate"]
                        )

                    if "allowOthersToDelete" in json_dict["editorTrackingInfo"]:
                        definition["editorTrackingInfo"]["allowOthersToDelete"] = (
                            json_dict["editorTrackingInfo"]["allowOthersToDelete"]
                        )

                    if "allowOthersToQuery" in json_dict["editorTrackingInfo"]:
                        definition["editorTrackingInfo"]["allowOthersToQuery"] = (
                            json_dict["editorTrackingInfo"]["allowOthersToQuery"]
                        )
                    if isinstance(json_dict["editorTrackingInfo"], dict):
                        for key, val in json_dict["editorTrackingInfo"].items():
                            if key not in definition["editorTrackingInfo"]:
                                definition["editorTrackingInfo"][key] = val
                if isinstance(json_dict, dict):
                    for key, val in json_dict.items():
                        if key not in definition:
                            definition[key] = val

        params = {
            "f": "json",
            "updateDefinition": json.dumps(obj=definition, separators=(",", ":")),
            "async": json.dumps(future),
        }
        u_url = self._url + "/updateDefinition"
        res = self._con.post(u_url, params)
        status_url: str = _get_value_case_insensitive(res, "statusurl")
        if future and status_url:
            executor = _cf.ThreadPoolExecutor(1)
            futureobj = executor.submit(
                _check_status,
                **{
                    "url": status_url,
                    "gis": self._gis,
                },
            )
            futureobj.add_done_callback(self._refresh_callback)
            executor.shutdown(False)
            return futureobj
        self.refresh()
        return res

    # ----------------------------------------------------------------------
    def delete_from_definition(self, json_dict: dict[str, Any], future: bool = False):
        """
        The delete_from_definition operation supports deleting a
        definition property from a hosted feature layer collection service. The result of
        this operation is a response indicating success or failure with
        error code and description.
        See `Delete From Definition (Feature Service) <https://developers.arcgis.com/rest/services-reference/delete-from-definition-feature-service-.htm>`_
        for additional information on this function.

        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        json_dict           Required dict. The part to add to the hosted service. The format
                            can be derived from the `properties` property.
                            For layer level modifications, run updates on each individual feature
                            service layer object.
        ---------------     --------------------------------------------------------------------
        future              Optional boolean. If True, a future object will be returns and the process
                            will not wait for the task to complete.
                            The default is False, which means wait for results.
        ===============     ====================================================================

        :return:
           JSON message as dictionary when `future=False` else If ``future = True``,
           then the result is a `Future <https://docs.python.org/3/library/concurrent.futures.html>`_ object. Call ``result()`` to get the response.

        """
        params = {
            "f": "json",
            "deleteFromDefinition": json.dumps(json_dict),
            "async": json.dumps(future),
        }
        u_url = self._url + "/deleteFromDefinition"
        res = self._con.post(u_url, params)
        status_url: str = _get_value_case_insensitive(res, "statusurl")
        if future and status_url:
            executor = _cf.ThreadPoolExecutor(1)
            futureobj = executor.submit(
                _check_status,
                **{
                    "url": status_url,
                    "gis": self._gis,
                },
            )
            futureobj.add_done_callback(self._refresh_callback)
            executor.shutdown(False)
            return futureobj
        self.refresh()
        return res

    # ----------------------------------------------------------------------
    def overwrite(self, data_file: str):
        """
        Overwrite all the features and layers in a hosted feature layer collection service. This operation removes
        all features but retains the properties (such as metadata, itemID) and capabilities configured on the service.
        There are some limits to using this operation:

        1. Only hosted feature layer collection services can be overwritten

        2. The original data used to publish this layer should be available on the portal

        3. The data file used to overwrite should be of the same format and filename as the original that was used to publish the layer

        4. In older versions of Enterprise (pre-11.2), the schema (column names, column data types) of the data_file should be the same as original. You can have additional or fewer rows (features).

        In addition to overwriting the features, this operation also updates the data of the item used to published this
        layer.

        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        data_file           Required string. Path to the file used to overwrite the hosted
                            feature layer collection.
        ===============     ====================================================================

        :return: JSON message as dictionary such as {'success':True} or {'error':'error message'}
        """
        if data_file and (
            not isinstance(data_file, str)
            or not os.path.exists(data_file)
            or not os.path.isfile(data_file)
        ):
            raise ValueError(
                "The data file provided does not exist or could not be accessed."
            )

        # check for outstanding replicas
        if hasattr(self._fs, "replicas") and bool(self._fs.replicas.get_list()):
            raise Exception(
                "Service cannot be overwritten if Sync is enabled and replicas exist."
            )

        # region Get Item associated with the service
        if "serviceItemId" in self.properties.keys():
            feature_layer_item = self._gis.content.get(self.properties["serviceItemId"])
        else:
            return {
                "Error": "Can only overwrite a Hosted Feature Layer Collection (Feature Service)"
            }
        # endregion

        # region find data item related to this hosted feature layer
        related_data_items = feature_layer_item.related_items("Service2Data", "forward")
        if len(related_data_items) > 0:
            related_data_item = related_data_items[0]
        else:
            return {
                "Error": "Cannot find related data item used to publish this Feature Layer"
            }

        # Check that file type and name are the same:
        if os.path.basename(data_file) != related_data_item["name"]:
            raise ValueError(
                "The name and extension of the file must be the same as the original data."
            )

        # find if we are overwriting only a hosted table
        hosted_table = False
        if not feature_layer_item.layers and feature_layer_item.tables:
            hosted_table = True
        # endregion

        params = None
        # overwriting for online and enterprise is different
        # if online or hosted table then use minimal parameters
        if (
            related_data_item.type
            in ["CSV", "Shapefile", "File Geodatabase", "Microsoft Excel"]
            and self._gis._portal.is_arcgisonline
            or (hosted_table is True and related_data_item.type != "Service Definition")
        ):
            # construct a full publishParameters that is a combination of existing Feature Layer definition
            # and original publishParameters.json used for publishing the service the first time

            # get old publishParameters.json
            path = (
                "content/items/"
                + feature_layer_item.itemid
                + "/info/publishParameters.json"
            )
            postdata = {"f": "json"}

            old_publish_parameters = self._gis._con.post(path, postdata)

            # get FeatureServer definition
            feature_service_def = dict(self.properties)

            # Get definition of each layer and table, remove fields in the dict
            layers_dict = []
            tables_dict = []
            for layer in self.layers:
                layer_def = dict(layer.properties)
                if "fields" in layer_def.keys():
                    layer_def.pop("fields")
                layers_dict.append(layer_def)

            for table in self.tables:
                table_def = dict(table.properties)
                if "fields" in table_def.keys():
                    table_def.pop("fields")
                tables_dict.append(table_def)

            # Splice the detailed table and layer def with FeatureServer def
            feature_service_def["layers"] = layers_dict
            feature_service_def["tables"] = tables_dict
            from pathlib import Path

            service_name = Path(self.url).parts[-2]  # get service name from url
            feature_service_def["name"] = service_name

            # combine both old publish params and full feature service definition
            publish_parameters = feature_service_def
            publish_parameters.update(old_publish_parameters)

        # enterprise overwriting params creation
        elif related_data_item.type in [
            "CSV",
            "Shapefile",
            "File Geodatabase",
            "Microsoft Excel",
        ]:
            path = (
                "content/items/"
                + feature_layer_item.itemid
                + "/info/publishParameters.json"
            )
            postdata = {"f": "json"}

            old_publish_parameters = self._gis._con.post(path, postdata)
            base_url = feature_layer_item.privateUrl
            lyr_url_info = "%s/layers" % base_url
            fs_url = "%s" % base_url
            # layer_info gets information on the layers and tables of an item
            layer_info = self._gis._con.get(lyr_url_info, {"f": "json"})
            [lyr.pop("fields") for lyr in layer_info["layers"]]
            [lyr.pop("fields") for lyr in layer_info["tables"]]
            feature_service_def = self._gis._con.get(fs_url, {"f": "json"})
            feature_service_def["tables"] = []
            feature_service_def["layers"] = []
            feature_service_def.update(layer_info)
            publish_parameters = feature_service_def
            publish_parameters.update(old_publish_parameters)
        else:
            # overwriting a SD case - no need for detailed publish parameters
            publish_parameters = None

        if related_data_item.update(item_properties=params, data=data_file):
            published_item = related_data_item.publish(
                publish_parameters, overwrite=True
            )
            if published_item is not None:
                return {"success": True}
            else:
                return {
                    "error": "Unable to overwrite the hosted feature layer collection"
                }
        else:
            return {"error": "Unable to update related data item with new data"}

    # ----------------------------------------------------------------------

    def _gen_overwrite_publishParameters(self, flc_item):
        """
        This internal method generates publishParameters for overwriting a hosted feature layer collection. This is used
        by Item.publish() method when user wants to originate the overwrite process from the data item instead of
        the hosted feature layer.

        :param flc_item: The Feature Layer Collection Item object that is being overwritten
        :return: JSON message as dictionary with to be used as publishParameters payload in the publish REST call.
        """

        # region Get Item associated with the service
        if "serviceItemId" in self.properties.keys():
            feature_layer_item = self._gis.content.get(self.properties["serviceItemId"])
        else:
            return {"error": "Can only overwrite a hosted feature layer collection"}
        # endregion

        # region find data item related to this hosted feature layer
        related_data_items = feature_layer_item.related_items("Service2Data", "forward")
        if len(related_data_items) > 0:
            related_data_item = related_data_items[0]
        else:
            return {
                "error": "Cannot find related data item used to publish this feature layer"
            }

        # endregion

        # region Construct publish parameters for Portal / Enterprise
        params = None
        if (
            related_data_item.type
            in ["CSV", "Shapefile", "File Geodatabase", "Microsoft Excel"]
            and self._gis._portal.is_arcgisonline == False
        ):
            params = {
                "name": related_data_item.name,
                "title": related_data_item.title,
                "tags": related_data_item.tags,
                "type": related_data_item.type,
                "overwrite": True,
                "overwriteService": "on",
                "useDescription": "on",
            }
            base_url = feature_layer_item.privateUrl
            lyr_url_info = "%s/layers" % base_url
            fs_url = "%s" % base_url
            layer_info = self._gis._con.get(lyr_url_info, {"f": "json"})
            [lyr.pop("fields") for lyr in layer_info["layers"]]
            [lyr.pop("fields") for lyr in layer_info["tables"]]
            feature_service_def = self._gis._con.get(fs_url, {"f": "json"})
            feature_service_def["tables"] = []
            feature_service_def["layers"] = []
            feature_service_def.update(layer_info)
            publish_parameters = feature_service_def
            publish_parameters["name"] = feature_layer_item.title
            publish_parameters["_ssl"] = False
            for idx, lyr in enumerate(publish_parameters["layers"]):
                lyr["parentLayerId"] = -1
                for k in {
                    "sourceSpatialReference",
                    "isCoGoEnabled",
                    "parentLayer",
                    "isDataArchived",
                    "cimVersion",
                }:
                    lyr.pop(k, None)
            for idx, lyr in enumerate(publish_parameters["tables"]):
                lyr["parentLayerId"] = -1
                for k in {
                    "sourceSpatialReference",
                    "isCoGoEnabled",
                    "parentLayer",
                    "isDataArchived",
                    "cimVersion",
                }:
                    lyr.pop(k, None)
        # endregion

        # region Construct publish parameters for AGO
        elif (
            related_data_item.type
            in ["CSV", "Shapefile", "File Geodatabase", "Microsoft Excel"]
            and self._gis._portal.is_arcgisonline
        ):
            # construct a full publishParameters that is a combination of existing Feature Layer definition
            # and original publishParameters.json used for publishing the service the first time

            # get old publishParameters.json
            path = (
                "content/items/"
                + feature_layer_item.itemid
                + "/info/publishParameters.json"
            )
            postdata = {"f": "json"}

            old_publish_parameters = self._gis._con.post(path, postdata)

            # get FeatureServer definition
            feature_service_def = dict(self.properties)

            # Get definition of each layer and table, remove fields in the dict
            layers_dict = []
            tables_dict = []
            for layer in self.layers:
                layer_def = dict(layer.properties)
                if "fields" in layer_def.keys():
                    dump = layer_def.pop("fields")
                layers_dict.append(layer_def)

            for table in self.tables:
                table_def = dict(table.properties)
                if "fields" in table_def.keys():
                    dump = table_def.pop("fields")
                tables_dict.append(table_def)

            # Splice the detailed table and layer def with FeatureServer def
            feature_service_def["layers"] = layers_dict
            feature_service_def["tables"] = tables_dict
            from pathlib import Path

            service_name = Path(self.url).parts[-2]  # get service name from url
            feature_service_def["name"] = service_name

            # combine both old publish params and full feature service definition
            publish_parameters = feature_service_def
            publish_parameters.update(old_publish_parameters)
        else:
            # overwriting a SD case - no need for detailed publish parameters
            publish_parameters = None
        # endregion

        return (publish_parameters, params)


###########################################################################
class FeatureLayerManager(_GISResource):
    """
    If the *user* has the appropriate privileges to access this class, it allows
    for updating the definition of a :class:`~arcgis.features.FeatureLayer`.
    This class is not typically initialized by end users, but instead accessed
    as the :attr:`~arcgis.features.FeatureLayer.manager` property of the
    :class:`~arcgis.features.FeatureLayer`.

    .. code-block:: python

        # Usage Example
        >>> from arcgis.gis import GIS
        >>> gis = GIS(profile="your_user_profile")

        >>> item = gis.content.search("Flood Damage", "Feature Layer")[0]
        >>> flood_flyr = item.layers[0]
        >>> flood_mgr = flood_flyr.manager
        >>> type(flood_mgr)

        <class 'arcgis.features.managers.FeatureLayerManager'>
    """

    def __init__(self, url, gis=None, **kwargs):
        """initializer"""
        super(FeatureLayerManager, self).__init__(url, gis)
        self._fl = kwargs.pop("fl", None)
        self._hydrate()

    # ----------------------------------------------------------------------
    @property
    def contingent_values(self) -> dict[str, Any]:
        """returns the contingent values for the service endpoint"""
        url: str = f"{self._url}/contingentValues"
        params: dict[str, Any] = {"f": "json"}
        return self._gis._con.get(url, params)

    # ----------------------------------------------------------------------
    @property
    def field_groups(self) -> dict[str, Any]:
        """returns the field groups for the service endpoint"""
        url: str = f"{self._url}/fieldGroups"
        params: dict[str, Any] = {"f": "json"}
        return self._gis._con.get(url, params)

    # ----------------------------------------------------------------------
    @classmethod
    def fromitem(cls, item: Item, layer_id: int = 0):
        """
        Creates a :class:`~arcgis.features.managers.FeatureLayerManager` object from a GIS Item.

        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        item                Required of type :class:`~arcgis.features.FeatureService` that represents
                            a :class:`~arcgis.features.FeatureLayerCollection` .
        ---------------     --------------------------------------------------------------------
        layer_id            Required int. Id of the layer in the
                            :class:`~arcgis.features.FeatureLayerCollection`
        ===============     ====================================================================

        :return:
            :class:`~arcgis.features.FeatureLayer` created from the layer provided.

        """
        if item.type != "Feature Service":
            raise TypeError("item must be a of type Feature Service, not " + item.type)
        from arcgis.features import FeatureLayer

        return FeatureLayer.fromitem(item, layer_id).manager

    # ----------------------------------------------------------------------
    def refresh(self):
        """refreshes a service"""
        params = {"f": "json"}
        u_url = self._url + "/refresh"
        res = self._con.post(u_url, params)

        super(FeatureLayerManager, self)._refresh()
        if self._fl:
            self._fl._refresh()
        return res

    # ----------------------------------------------------------------------
    def add_to_definition(self, json_dict: dict[str, Any], future: bool = False):
        """
        This method adds a definition property to a previously published service.

        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        json_dict           Required dict. The part to add to the hosted service. The format
                            can be derived from the `properties` property. For layer level
                            modifications, run updates on each individual feature layer of the
                            service.

                            Find more information on what this dictionary can contain at:
                            https://developers.arcgis.com/rest/services-reference/enterprise/layer-feature-service/#json-response-syntax
        ---------------     --------------------------------------------------------------------
        future              Optional boolean. The default is *False*, which means to run the
                            method synchronously and wait for results. If *True*, the method runs
                            asynchronously.

                              * Asynchronous operation only supported in ArcGIS Online and
                                ArcGIS Enterprise.
        ===============     ====================================================================

        :return:
           * If run synchronously (*future=False*), a JSON message as a dictionary indicating 'success' or 'error'
           * If run asynchronously (*future = True*):

             * On *ArcGIS Enterprise and ArcGIS Online*, a `Future <https://docs.python.org/3/library/concurrent.futures.html>`_
               object. Call ``result()`` to get the response.
             * Asynchronous operation not supported in ArcGIS Online for Kubernetes.

        .. code-block:: python

            # Usage Example: ArcGIS Enterprise for Kubernetes:
            >>> from arcgis.gis import GIS
            >>> gis = GIS(profile="your_kubernetes_profile")

            >>> item = gis.content.get("<feature_layer_item_id>")
            >>> fl = item.layers[0]

            >>> new_field = {
                              "fields": [
                                    {
                                        "name": "Loc Identifier",
                                        "type": "esriFieldTypeString",
                                        "alias": "safa",
                                        "nullable": True,
                                        "editable": True,
                                        "length": 256,
                                    }
                                ]
                             }
           >>> res = fl.manager.add_to_definition(
                                json_dict=add_field
                    )
           >>> res

           {'success': True}

           # Usage Example 2: ArcGIS Online asynchronous
           >>> gis = GIS(profile="your_online_profile")

           >>> item = gis.content.get("<feature_layer_item_id>")
           >>> fl = item.layers[0]

           >>> new_field = {
                              "fields": [
                                    {
                                        "name": "Loc Identifier",
                                        "type": "esriFieldTypeString",
                                        "alias": "safa",
                                        "nullable": True,
                                        "editable": True,
                                        "length": 256,
                                    }
                                ]
                             }

          >>> future = fl.manager.add_to_definition(
                                            json_dict=add_field,
                                            future=True
                       )
          >>> res = future.result()
          >>> res

          {'submissionTime': <time_value>,
            'lastUpdatedTime': <time_value>,
            'status': 'Completed'}

        """

        if isinstance(json_dict, PropertyMap):
            json_dict = dict(json_dict)

        params = {
            "f": "json",
            "addToDefinition": json.dumps(json_dict),
            "async": json.dumps(future),
        }
        u_url = self._url + "/addToDefinition"

        res = self._con.post(u_url, params)
        status_url = _get_value_case_insensitive(res, "statusurl")
        if future and status_url:
            executor = _cf.ThreadPoolExecutor(1)
            futureobj = executor.submit(
                _check_status,
                **{
                    "url": status_url,
                    "gis": self._gis,
                },
            )
            futureobj.add_done_callback(self._refresh_callback)
            executor.shutdown(False)
            return futureobj
        self.refresh()
        return res

    # ----------------------------------------------------------------------
    def update_definition(self, json_dict: dict[str, Any], future: bool = False):
        """
        This method modifies a definition of a hosted feature layer.

        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        json_dict           Required dict. The part to add to the hosted service. The format
                            can be derived from the `properties` property.
                            For layer level modifications, run updates on each individual feature
                            service layer object.
        ---------------     --------------------------------------------------------------------
        future              Optional boolean. The default is *False*, which means to run the
                            method synchronously and wait for results. If *True*, the method runs
                            asynchronously.

                              * Asynchronous operation only supported in ArcGIS Online and
                                ArcGIS Enteprise.
        ===============     ====================================================================

        :return:
           * If run synchronously (*future=False*), a JSON message as a dictionary indicating 'success' or 'error'
           * If run asynchronously (*future = True*):

             * On *ArcGIS Enterprise and ArcGIS Online*, a `Future <https://docs.python.org/3/library/concurrent.futures.html>`_
               object. Call ``result()`` to get the response.
             * Asynchronous operation not supported in ArcGIS Online for Kubernetes.
        """

        if isinstance(json_dict, PropertyMap):
            json_dict = dict(json_dict)

        params = {
            "f": "json",
            "updateDefinition": json.dumps(json_dict),
            "async": json.dumps(future),
        }

        u_url = self._url + "/updateDefinition"

        res = self._con.post(u_url, params)
        status_url = _get_value_case_insensitive(res, "statusurl")
        if future and status_url:
            executor = _cf.ThreadPoolExecutor(1)
            futureobj = executor.submit(
                _check_status,
                **{
                    "url": status_url,
                    "gis": self._gis,
                },
            )
            futureobj.add_done_callback(self._refresh_callback)
            executor.shutdown(False)
            return futureobj
        self.refresh()
        return res

    # ----------------------------------------------------------------------
    def delete_from_definition(self, json_dict: dict[str, Any], future: bool = False):
        """
        This method deletes a definition property from a hosted feature layer.
        See: `Delete From Definition (Feature Service) <https://developers.arcgis.com/rest/services-reference/delete-from-definition-feature-service-.htm>`_
        for additional information on this function.

        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        json_dict           Required dict. The part to add to the hosted service. The format
                            can be derived from the `properties` property.
                            For layer level modifications, run updates on each individual feature
                            service layer object.
                            Only include the items you want to remove from the FeatureService or layer.
        ---------------     --------------------------------------------------------------------
        future              Optional boolean. The default is *False*, which means to run the
                            method synchronously and wait for results. If *True*, the method runs
                            asynchronously.

                              * Asynchronous operation only supported in ArcGIS Online and
                                ArcGIS Enterprise.
        ===============     ====================================================================

        :return:
           * If run synchronously (*future=False*), a JSON message as a dictionary indicating 'success' or 'error'
           * If run asynchronously (*future = True*):

             * On *ArcGIS Enterprise and ArcGIS Online*, a `Future <https://docs.python.org/3/library/concurrent.futures.html>`_
               object. Call ``result()`` to get the response.
             * Asynchronous operation not supported in ArcGIS Online for Kubernetes.
        """

        if isinstance(json_dict, PropertyMap):
            json_dict = dict(json_dict)

        params = {
            "f": "json",
            "deleteFromDefinition": json.dumps(json_dict),
            "async": json.dumps(future),
        }
        u_url = self._url + "/deleteFromDefinition"

        res = self._con.post(u_url, params)
        status_url = _get_value_case_insensitive(res, "statusurl")
        if future and status_url:
            executor = _cf.ThreadPoolExecutor(1)
            futureobj = executor.submit(
                _check_status,
                **{
                    "url": status_url,
                    "gis": self._gis,
                },
            )
            futureobj.add_done_callback(self._refresh_callback)
            executor.shutdown(False)
            return futureobj
        self.refresh()
        return res

    # ----------------------------------------------------------------------
    def truncate(
        self,
        attachment_only: bool = False,
        asynchronous: bool = False,
        wait: bool = True,
    ):
        """
        The truncate operation supports deleting all features or attachments
        in a hosted feature service layer. The result of this operation is a
        response indicating success or failure with error code and description.
        See `Truncate (Feature Layer) <https://developers.arcgis.com/rest/services-reference/online/truncate-feature-layer-.htm>`_
        for additional information on this method.

        .. note::
            The `truncate` method is restricted to
            :class:`layers <arcgis.features.FeatureLayer>` that:

            - do not serve as the origin in a relationship with other
              layers
            - do not reference the same underlying database tables that are
              referenced by other layers (for example, if the layer was
              published from a layer with a definition query and a
              separate layer has also been published from that source)
            - do not have `sync` enabled

        ===============     ====================================================================
        **Parameter**        **Description**
        ---------------     --------------------------------------------------------------------
        attachment_only     Optional boolean. If True, deletes all the attachments for this layer.
                            None of the layer features will be deleted.
        ---------------     --------------------------------------------------------------------
        asynchronous        Optional boolean. If True, supports asynchronous processing. The
                            default is False. It is recommended to set asynchronous=True for
                            large datasets.
        ---------------     --------------------------------------------------------------------
        wait                Optional boolean. If True, then wait to pause the process until
                            asynchronous operation is completed. Default is True.
        ===============     ====================================================================

        :return:
           JSON Message as dictionary indicating `success` or `error`

        """
        params = {
            "f": "json",
            "attachmentOnly": attachment_only,
            "async": asynchronous,
        }
        u_url = self._url + "/truncate"

        if asynchronous:
            if wait:
                job = self._con.post(u_url, params)
                status = self._get_status(url=job["statusURL"])
                while status["status"] not in (
                    "Completed",
                    "CompletedWithErrors",
                    "Failed",
                ):
                    # wait before checking again
                    time.sleep(2)
                    status = self._get_status(url=job["statusURL"])

                res = status
                self.refresh()
            else:
                res = self._con.post(u_url, params)
                # Leave calling refresh to user since wait is false
        else:
            res = self._con.post(u_url, params)
            self.refresh()
        return res

    # ----------------------------------------------------------------------
    def _refresh_callback(self, *args, **kwargs):
        """function to refresh the service post add or update definition for async operations"""
        try:
            self._hydrated = False
            self.refresh()
        except:
            self._hydrated = False

    # ----------------------------------------------------------------------
    def _get_status(self, url):
        """gets the status when exported async set to True"""
        params = {"f": "json"}
        url += "/status"
        return self._con.get(url, params)
