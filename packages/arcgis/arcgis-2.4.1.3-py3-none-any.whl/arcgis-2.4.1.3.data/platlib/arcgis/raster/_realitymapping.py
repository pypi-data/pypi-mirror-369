"""
The realitymapping python API allows automating realitymapping tasks in the server environment.

For more information about realitymapping workflows in ArcGIS, please visit the help documentation at
`Realitymapping in ArcGIS <https://pro.arcgis.com/en/pro-app/latest/help/data/imagery/reality-mapping-in-arcgis-pro.htm>`_

"""

from __future__ import annotations
from typing import Any, Optional, Union
import arcgis
import json
from arcgis.gis import GIS, Item
import collections
from ._util import _initialize_project, _flatten_adjust_settings, _nestify_context
import string as _string
import random as _random

from arcgis.geoprocessing._support import (
    _analysis_job,
    _analysis_job_results,
    _analysis_job_status,
    _layer_input,
)
from arcgis.features.layer import FeatureLayer


###################################################################################################
###
### INTERNAL FUNCTIONS
###
###################################################################################################


def _execute_task(gis, taskname, params):
    gptool_url = gis.properties.helperServices.realityMapping.url
    gptool = arcgis.gis._GISResource(gptool_url, gis)
    task = taskname

    task_url, job_info, job_id = _analysis_job(gptool, task, params)
    # print ('task url is ', task_url)

    job_info = _analysis_job_status(gptool, task_url, job_info)
    job_values = _analysis_job_results(gptool, task_url, job_info, job_id)

    item_properties = {
        "properties": {
            "jobUrl": task_url + "/jobs/" + job_info["jobId"],
            "jobType": "GPServer",
            "jobId": job_info["jobId"],
            "jobStatus": "completed",
        }
    }
    return job_values


def _id_generator(size=6, chars=_string.ascii_uppercase + _string.digits):
    return "".join(_random.choice(chars) for _ in range(size))


###################################################################################################
###################################################################################################
def _create_output_image_service(gis, output_name, task):
    ok = gis.content.is_service_name_available(output_name, "Image Service")
    if not ok:
        raise RuntimeError(
            "An Image Service by this name already exists: " + output_name
        )

    create_parameters = {
        "name": output_name,
        "description": "",
        "capabilities": "Image",
        "properties": {"path": "@", "description": "", "copyright": ""},
    }

    output_service = gis.content.create_service(
        output_name, create_params=create_parameters, service_type="imageService"
    )
    description = "Image Service generated from running the " + task + " tool."
    item_properties = {
        "description": description,
        "tags": "Analysis Result, " + task,
        "snippet": "Analysis Image Service generated from " + task,
    }
    output_service.update(item_properties)
    return output_service


def _update_flight_info(
    flight, project_item, processing_states={}, item_name="", gis=None
):
    # job_info=output_item.properties
    # job_response={}
    # if "jobUrl" in job_info :
    # Get the url of the Analysis job to track the status.

    # job_url = job_info.get("jobUrl")
    # params = {"f": "json"}
    # job_response = gis._con.post(job_url, params)

    resource = flight["resource"]

    rm = project_item.resources
    flight_json = rm.get(resource)

    # flight_json["items"].update({item_name:{"itemId": output_item.itemid, "url":output_item.url}})

    # flight_json['jobs'].update({item_name:{"messages": job_response["messages"], "checked": True, "progress": 100,"success": True}})
    flight_json["processingSettings"].update({item_name: processing_states})

    properties = json.loads(flight["properties"])

    # properties = json.loads(flight['properties'])
    # properties_items =properties["items"]
    # properties_items.append({"product": item_name, "id": output_item.itemid, "created": True})
    # properties.update({"items": properties_items})

    import tempfile, uuid, os

    fname = resource.split("/")[1]
    temp_dir = tempfile.gettempdir()
    temp_file = os.path.join(temp_dir, fname)
    with open(temp_file, "w") as writer:
        json.dump(flight_json, writer)
    del writer

    try:
        rm.update(
            file=temp_file,
            text=flight_json,
            folder_name="flights",
            file_name=fname,
            properties=properties,
        )
    except:
        raise RuntimeError("Error updating the flight resource")


def _create_project(
    name: str,
    definition: Optional[dict[str, Any]] = None,
    sensor_type: str = "Drone",
    scenario_type: str = "Drone",
    *,
    gis: Optional[GIS] = None,
    **kwargs,
):
    """
    Creates a new realitymapping project item on your enterprise.
    This project item can be specified as input to the realitymapping functions as value to the
    image_collection parameter.

    The realitymapping project item can be opened in Reality Maker web app.
    The RMProject includes all project inputs, ancillary data such as image footprints and block adjustment reports,
    intermediate products such as image collections, quick block adjustment results, final products,
    and status at each stage of processing.

    The create_project method also creates a new folder and adds the realitymapping project item to it.
    All the realitymapping products such as the image collection, orthomosaic products etc will be added in the
    same folder. The folder name will be same the project name with the prefix "_realitymapping_"

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    name                   Required string. The name of the project item to be created.
    ------------------     --------------------------------------------------------------------
    definition             Optional dictionary.  The project definition dictionary.
                        the definition contais the template informatios such as adjustSettings,
                        processingStates, rasterType, information about the flights.
    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================

    :return:
        The realitymapping project item

    """

    gis = arcgis.env.active_gis if gis is None else gis

    if sensor_type and sensor_type.lower() not in [
        "drone",
        "satellite",
        "aerialdigital",
        "aerialscanned",
    ]:
        raise RuntimeError(
            "Invalid sensor type. Supported values are 'Drone', 'Satellite', 'AerialDigital', 'AerialScanned'"
        )
    if scenario_type and scenario_type.lower() not in [
        "drone",
        "aerial_nadir",
        "aerial_oblique",
    ]:
        raise RuntimeError(
            "Invalid scenario type. Supported values are 'Drone', 'Aerial_Nadir', 'Aerial_Oblique'"
        )
    if (
        sensor_type
        and sensor_type.lower() == "aerialdigital"
        and scenario_type.lower()
        not in [
            "aerial_nadir",
            "aerial_oblique",
        ]
    ):
        raise RuntimeError(
            "Invalid scenario type for Aerial Digital sensor. Supported values are 'Aerial_Nadir', 'Aerial_Oblique'"
        )
    if sensor_type and sensor_type.lower() == "satellite":
        scenario_type = ""

    folder = None
    folderId = None

    if folder is None:
        folder = "_realitymapping_" + name
    owner = gis.properties.user.username
    try:
        folder_item = gis.content.folders.create(folder, owner)
        folder_dict = folder_item.properties
    except:
        raise RuntimeError(
            "Unable to create folder for Realitymapping Project Item. The project name is not available."
        )
    folder = folder_dict["title"]
    folderId = folder_dict["id"]

    item_properties = {
        "title": name,
        "type": "Reality Mapping Project",
        "properties": {"flightCount": 0, "status": "inProgress"},
    }
    if definition is None:
        definition = {}

    item_properties["text"] = json.dumps(definition)
    item = gis.content.add(item_properties, folder=folder)
    item_data = None
    try:
        item_data = _initialize_project(sensor_type, scenario_type, is_rm=True)
    except:
        pass
    if item_data:
        props = item.properties
        item.update(item_properties=props, data=json.dumps(item_data))
    return item


def _add_mission(
    project,
    image_list: list,
    mission_name: Optional[str] = None,
    image_collection: Optional[str] = None,
    raster_type_name: Optional[str] = None,
    raster_type_params: Optional[dict[str, Any]] = None,
    out_sr: Optional[dict[str, Any]] = None,
    context: Optional[dict[str, Any]] = None,
    *,
    gis: Optional[GIS] = None,
    **kwargs,
):
    """
    Add flights to the realitymapping project item. You can add imagery from one or more drone flights 
    to your realitymapping project item.

    ======================               ====================================================================
    **Parameter**                        **Description**
    ----------------------               --------------------------------------------------------------------
    project_item                         Required Item. The realitymapping project item to which the flight has to be added
    ----------------------               --------------------------------------------------------------------
    image_list                           Required, the list of input images to be added to
                                         the image collection being created. This parameter can
                                         be a list of image paths or a path to a folder containing the images

                                         The function can create hosted imagery layers on enterprise from 
                                         local raster datasets by uploading the data to the server.    
    ----------------------               --------------------------------------------------------------------
    flight_name                          Optional string. The name of the flight.
    ----------------------               --------------------------------------------------------------------
    image_collection                     Optional string, the name of the image collection to create.
                  
                                         The image collection can be an existing image service, in \
                                         which the function will create a mosaic dataset and the existing \
                                         hosted image service will then point to the new mosaic dataset.

                                         If the image collection does not exist, a new multi-tenant \
                                         service will be created.

                                         This parameter can be the Item representing an existing image_collection \
                                         or it can be a string representing the name of the image_collection \
                                         (either existing or to be created.)

                                         The image collection will be created in the same folder as the one created
                                         by the create_project method
    ----------------------               --------------------------------------------------------------------
    raster_type_name                     Optional string. The name of the raster type to use for adding data to \
                                         the image collection. Default is "UAV/UAS"

                                         Example:

                                            "UAV/UAS"
    ----------------------               --------------------------------------------------------------------
    raster_type_params                   Optional dict. Additional ``raster_type`` specific parameters.
        
                                         The process of add rasters to the image collection can be \
                                         controlled by specifying additional raster type arguments.

                                         The raster type parameters argument is a dictionary.

                                         The dictionary can contain productType, processingTemplate, \
                                         pansharpenType, Filter, pansharpenWeights, ConstantZ, \
                                         dem, zoffset, CorrectGeoid, ZFactor, StretchType, \
                                         ScaleFactor, ValidRange

                                         Please check the table below (Supported Raster Types), \
                                         for more details about the product types, \
                                         processing templates, pansharpen weights for each raster type. 

                                         - Possible values for pansharpenType - ["Mean", "IHS", "Brovey", "Esri", "Mean", "Gram-Schmidt"]
                                         - Possible values for filter - [None, "Sharpen", "SharpenMore"]
                                         - Value for StretchType dictionary can be as follows:

                                           - "None"
                                           - "MinMax; <min>; <max>"
                                           - "PercentMinMax; <MinPercent>; <MaxPercent>"
                                           - "StdDev; <NumberOfStandardDeviation>"
                                           Example: {"StretchType": "MinMax; <min>; <max>"}
                                         - Value for ValidRange dictionary can be as follows:

                                           - "<MaskMinValue>, <MaskMaxValue>"
                                           Example: {"ValidRange": "10, 200"}

                                         Example:

                                            {"productType":"All","processingTemplate":"Pansharpen",
                                            "pansharpenType":"Gram-Schmidt","filter":"SharpenMore",
                                            "pansharpenWeights":"0.85 0.7 0.35 1","constantZ":-9999}
    ----------------------               --------------------------------------------------------------------
    out_sr                               Optional integer. Additional parameters of the service.
                            
                                         The following additional parameters can be specified:

                                         - Spatial reference of the image_collection; The well-known ID of \
                                         the spatial reference or a spatial reference dictionary object for the \
                                         input geometries.

                                         If the raster type name is set to "UAV/UAS", the spatial reference of the
                                         output image collection will be determined by the raster type parameters defined.
    ----------------------               --------------------------------------------------------------------
    context                              Optional dict. The context parameter is used to provide additional input parameters.
    
                                         Syntax: {"image_collection_properties": {"imageCollectionType":"Satellite"},"byref":True}
                                        
                                         Use ``image_collection_properties`` key to set value for imageCollectionType.

                                         .. note::

                                            The "imageCollectionType" property is important for image collection that will later on be adjusted by realitymapping system service. 
                                            Based on the image collection type, the realitymapping system service will choose different algorithm for adjustment. 
                                            Therefore, if the image collection is created by reference, the requester should set this 
                                            property based on the type of images in the image collection using the following keywords. 
                                            If the imageCollectionType is not set, it defaults to "UAV/UAS"

                                         If ``byref`` is set to 'True', the data will not be uploaded. If it is not set, the default is 'False'

                                         The context parameter can also be used to specify whether to build overviews, \
                                         build footprints, to specify pixel value that represents the NoData etc.


                                         Example:

                                            | {"buildFootprints":True,                                            
                                            | "footprintsArguments":{"method":"RADIOMETRY","minValue":1,"maxValue":5,
                                            | "shrinkDistance":50,"skipOverviews":True,"updateBoundary":True,
                                            | "maintainEdge":False,"simplification":None,"numVertices":20,
                                            | "minThinnessRatio":0.05,"maxSliverSize":20,"requestSize":2000,
                                            | "minRegionSize":100},
                                            | "defineNodata":True,                                            
                                            | "noDataArguments":{"noDataValues":[500],"numberOfBand":99,"compositeValue":True},                                            
                                            | "buildOverview":True}

                                         The context parameter can be used to add new fields when creating \
                                         the image collection.


                                         Example:

                                            | {"fields": [{"name": "cloud_cover", "type": "Long"},
                                            | {"name": "cloud_shadow_count", "type": "Long"}]}
    ----------------------               --------------------------------------------------------------------
    gis                                  Keyword only parameter. Optional :class:`~arcgis.gis.GIS` object. The GIS on which this tool runs. If not specified, the active GIS is used.
    ----------------------               --------------------------------------------------------------------
    future                               Keyword only parameter. Optional boolean. If True, the result will be a GPJob object and 
                                         results will be returned asynchronously.
    ======================               ====================================================================

    :return: The imagery layer item

    """
    gis = arcgis.env.active_gis if gis is None else gis
    project_item = project._project_item
    resource_manager = project_item.resources
    oid = project.mission_count

    for f in gis.users.me.folders:
        if f._fid == project_item.ownerFolder:
            folder = f.properties
            break

    from datetime import datetime
    from arcgis.raster.analytics import create_image_collection

    if image_collection is None:
        image_collection = "image_collection" + "_" + _id_generator()

    if raster_type_name is None:
        raster_type_name = "UAV/UAS"

    if mission_name is None:
        mission_name = "mission" + "_" + _id_generator()
    fname = f"{mission_name}.json"
    workspace_name = fname.replace(".json", "")
    # timestamp = datetime.timestamp()
    # workspace_name = f"{mission_name}_{timestamp}"

    if context is None:
        context = {"workspace": workspace_name}
    else:
        context["workspace"] = workspace_name

    if out_sr is None and project._spatial_reference is not None:
        out_sr = project._spatial_reference["spatialReference"]
        if isinstance(out_sr, arcgis._impl.common._mixins.PropertyMap):
            out_sr = dict(out_sr)

    output_collection = create_image_collection(
        image_collection=image_collection,
        input_rasters=image_list,
        raster_type_name=raster_type_name,
        raster_type_params=raster_type_params,
        out_sr=out_sr,
        context=context,
        gis=gis,
        folder=folder,
    )

    try:
        if output_collection and project._spatial_reference is None:
            # Get the lyr SR and set it on the SR instance variable
            lyr = output_collection.layers[0]
            project._spatial_reference = {
                "spatialReference": lyr.extent.spatialReference
            }
            props = None
            # Get the project item data to update the SR for the portal item
            project_data = project_item.get_data()
            project_data.update(project._spatial_reference)

            if "wkid" in project._spatial_reference:
                wkid = project._spatial_reference["wkid"]
                props = {"spatialReference": wkid}
            elif "wkt" in project._spatial_reference:
                wkt = project._spatial_reference["wkt"]
                props = {"spatialReference": wkt}
            elif "wkt2" in project._spatial_reference:
                wkt_2 = project._spatial_reference["wkt2"]
                props = {"spatialReference": wkt_2}

            project_item.update(item_properties=props, data=project_data)
    except:
        pass

    try:
        job_info = output_collection.properties
        job_response = {}
        if "jobUrl" in job_info:
            # Get the url of the Analysis job to track the status.

            job_url = job_info.get("jobUrl")
            params = {"f": "json"}
            job_response = gis._con.post(job_url, params)

        mission_json = {
            "items": {"imageCollection": {}},
            "jobs": {
                "imageCollection": {"checked": True, "progress": 100, "success": True},
                "adjustment": {"checked": False, "mode": "Quick"},
                "ortho": {"checked": False},
                "matchControlPoint": {"checked": False},
                "queryControlPoints": {"checked": False},
                "computeControlPoints": {"checked": False},
                "appendControlPoints": {"checked": False},
            },
            "rasterType": "UAV/UAS",
            "cameraInfo": {},
            "sourceData": {},
            "spatialReference": {},
            "adjustSettings": {},
            "processingSettings": {},
            "mapping": {
                "basemap": {
                    "title": "Topographic",
                    "baseMapLayers": [
                        {
                            "layerType": "ArcGISTiledMapServiceLayer",
                            "opacity": 1,
                            "visibility": True,
                            "url": "https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer",
                        }
                    ],
                },
                "referenceData": [],
                "layers": {"visibilities": {"footprint": False}},
            },
            "projectVersion": 1,
            "createTS": "",
            "oid": oid,
            "gcsExtent": {},
            "workspace": workspace_name,
        }

        mission_json.update(
            {
                "items": {
                    "imageCollection": {
                        "itemId": output_collection.itemid,
                        "url": output_collection.url,
                    }
                }
            }
        )

        mission_json["jobs"]["imageCollection"].update(
            {"messages": job_response["messages"]}
        )

        mission_json.update({"rasterType": raster_type_name})

        def get_camera_props(cam_props):
            cam_props_lower = dict((k.lower(), v) for k, v in cam_props.items())
            cam_dict = {
                "make": cam_props_lower.get("maker", ""),
                "focalLength": cam_props_lower.get("focallength", ""),
                "model": cam_props_lower.get("model", ""),
                "cols": cam_props_lower.get("columns", ""),
                "rows": cam_props_lower.get("rows", ""),
                "pixelSize": cam_props_lower.get("pixelsize", ""),
            }
            return cam_dict

        cam_props = {}
        try:
            if "cameraProperties" in raster_type_params:
                cam_props = get_camera_props(raster_type_params["cameraProperties"])
            else:
                try:
                    lyr = output_collection.layers[0]
                    cam_info = lyr.query_gps_info()
                    cam_props = cam_info["cameras"][0]
                except:
                    # older servers may not have query gps info rest end point
                    pass
        except:
            pass

        mission_json.update({"cameraInfo": cam_props})

        gps_data = []
        gps_info_list = ["name", "lat", "long", "alt", "acq"]

        if (
            raster_type_params is not None
            and isinstance(raster_type_params, dict)
            and "gps" in raster_type_params
        ):
            for ele in raster_type_params["gps"]:
                dict_gps = dict(zip(gps_info_list, ele))
                gps_data.append(dict_gps)
        if not gps_data:
            try:
                lyr = output_collection.layers[0]
                gps_info = lyr.query_gps_info()["images"]
                for img_info in gps_info:
                    from arcgis.raster._util import _to_datetime

                    acq = _to_datetime(img_info["acquisitionDate"]).isoformat()
                    gps = img_info["gps"]
                    name = img_info["name"]
                    lat = gps["latitude"]
                    long = gps["longitude"]
                    alt = gps["altitude"]
                    gps_val = [name, lat, long, alt, acq]
                    dict_gps = dict(zip(gps_info_list, gps_val))
                    gps_data.append(dict_gps)
            except:
                # older servers may not have query gps info rest end point
                pass

        try:
            lyr = output_collection.layers[0]
            query_output = lyr.query(
                where="OBJECTID=1",
                out_fields="AcquisitionDate",
                return_all_records=False,
                return_geometry=False,
            )
            acq_date = query_output["features"][0]["attributes"]["AcquisitionDate"]
            from datetime import datetime

            ts = int(acq_date) / 1000
            flight_date = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
        except:
            dt = datetime.now()
            flight_date = dt.strftime("%Y-%m-%d")

        image_count = output_collection.layers[0].query(return_count_only=True)

        mission_json.update(
            {
                "sourceData": {
                    "gps": gps_data,
                    "imageCount": image_count,
                    "flightDate": flight_date,
                }
            }
        )

        project_id = datetime.now().strftime("%Y%m%d%H%M%S")
        mission_json.update({"projectId": project_id})

        ts = int(datetime.timestamp(datetime.now())) * 1000
        mission_json.update({"createTS": ts})

        ## Set extent
        try:
            gcs_extent = {}
            extent_arr = output_collection.extent
            if extent_arr is not None:
                gcs_extent = {
                    "xmin": extent_arr[0][0],
                    "ymin": extent_arr[0][1],
                    "xmax": extent_arr[1][0],
                    "ymax": extent_arr[1][1],
                    "spatialReference": {"wkid": 4326},
                }
        except:
            gcs_extent = {}

        projected_extent = {}
        try:
            projected_extent = dict(output_collection.layers[0].extent)
        except:
            projected_extent = {}

        mission_json.update(
            {"gcsExtent": gcs_extent, "projectedExtent": projected_extent}
        )

        try:
            coverage_area = output_collection.layers[0].query_boundary()["area"]
            mission_json.update({"coverage": coverage_area})
        except:
            pass

        try:
            resource_manager.add(
                file_name=fname,
                text=mission_json,
                folder_name="flights",
                properties={
                    "oid": oid,
                    "imageCount": image_count,
                    "createTS": ts,
                    "items": [
                        {
                            "product": "imageCollection",
                            "id": output_collection.id,
                            "created": True,
                        }
                    ],
                    "gcpItems": [],
                    "baStatus": "succeeded",
                },
            )
            prj_data = project_item.get_data()
            flights_list = prj_data.get("flights", [])
            flights_list.append({"oid": oid, "createTS": ts})
            prj_data.update({"flights": flights_list})
            prj_data.update({"projectVersion": 2, "rasterType": raster_type_name})

            project_properties = project_item.properties
            flight_count = project_properties.get("flightCount", 0)
            flight_count = flight_count + 1

            image_count_ex = project_properties.get("imageCount", 0)
            image_count_ex = image_count + image_count_ex

            project_properties.update(
                {"flightCount": flight_count, "imageCount": image_count}
            )
            project_item.update(
                item_properties={"properties": project_properties},
                data=json.dumps(prj_data),
            )

            # project_item.update(data=json.dumps(prj_data))
        except:
            raise RuntimeError("Error adding the mission")
    except:
        raise RuntimeError("Error updating the mission JSON")
    return output_collection, mission_name


###################################################################################################
###
### PUBLIC API
###
###################################################################################################
def is_supported(gis=None):
    """
    Returns True if the GIS supports realitymapping. If a gis isn't specified,
    checks if :meth:`~arcgis.env.active_gis` supports realitymapping
    """
    gis = arcgis.env.active_gis if gis is None else gis
    if "realityMapping" in gis.properties.helperServices:
        return True
    else:
        return False


###################################################################################################
## Compute Sensor model
###################################################################################################
def compute_sensor_model(
    mission,
    mode: str = "Quick",
    location_accuracy: str = "High",
    context: Optional[dict[str, Any]] = None,
    *,
    gis: Optional[GIS] = None,
    future: bool = False,
    **kwargs,
):
    """
    compute_sensor_model computes the bundle block adjustment for the image collection
    and applies the frame xform to the images. It will also generate the control point
    table, solution table, solution points table and flight path table.
    These tables will not be published as Portal items.

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    mission                Required, the input image collection on which to compute
                           the sensor model.
                           The mission can be a RMMission object, an image service URL or portal Item or a datastore URI.

                           The mission must exist.
    ------------------     --------------------------------------------------------------------
    mode                   Optional string.  the mode to be used for bundle block adjustment
                           Only the following modes are supported:

                           - 'Quick' : Computes tie points and adjustment at 8x of the source imagery resolution

                           - 'Full'  : adjust the images in Quick mode then at 1x of the source imagery resolution

                           - 'Refine' : adjust the image at 1x of the source imagery resolution

                           By default, 'Quick' mode is applied to compute the sensor model.
    ------------------     --------------------------------------------------------------------
    location_accuracy      Optional string. this option allows users to specify the GPS location accuracy level of the
                           source image. It determines how far the underline tool will search for neighboring
                           matching images, then calculate tie points and compute adjustments.

                           Possible values for location_accuracy are:

                           - 'VeryHigh'    : Imagery was collected with a high-accuracy, differential GPS, such as RTK or PPK. This option will hold image locations fixed during block adjustment

                           - 'High'    : GPS accuracy is 0 to 10 meters, and the tool uses a maximum of 4 by 3 images

                           - 'Medium'  : GPS accuracy of 10 to 20 meters, and the tool uses a maximum of 4 by 6 images

                           - 'Low'     : GPS accuracy of 20 to 50 meters, and the tool uses a maximum of 4 by 12 images

                           - 'VeryLow' : GPS accuracy is more than 50 meters, and the tool uses a maximum of 4 by 20 images

                           The default location_accuracy is 'High'
    ------------------     --------------------------------------------------------------------
    context                Optional dictionary. The context parameter is used to configure additional client settings
                           for block adjustment. The supported configurable parameters are for compute mosaic dataset
                           candidates after the adjustment.

                           Example:

                               {
                               "computeCandidate": False,
                               "maxoverlap": 0.6,
                               "maxloss": 0.05,
                               }
    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================

    :return:
        The imagery layer url

    """

    gis = arcgis.env.active_gis if gis is None else gis
    update_flight_json = False
    flight_json_details = {}
    from ._realitymapping_mission import RMMission

    image_collection = mission
    if isinstance(mission, RMMission):
        image_collection = mission.image_collection
        update_flight_json = True
        settings = {}

        try:
            project = mission._project
            project_adj_settings = project.settings
            if (
                isinstance(project_adj_settings, dict)
                and ("template" in project_adj_settings.keys())
                and "adjustSettings" in project_adj_settings["template"].keys()
            ):
                project_adj_settings = project_adj_settings["template"][
                    "adjustSettings"
                ]
            keys_to_pop = ["parallelProcessingFactor"]

            if isinstance(context, dict):
                adjust_options = context.pop("adjustOptions", [])
                adjust_options = _flatten_adjust_settings(adjust_options)
                # context is flattened
                context.update(adjust_options)
                # update adj dict with all the params from context
                project_adj_settings.update(context)
                # pop the keys that are not relevant to the adj settings
                for key in keys_to_pop:
                    project_adj_settings.pop(key, None)
                # update context with default values from project_adj_settings if they are not present in context
                context.update(project_adj_settings)
                _nestify_context(context)

                if (
                    project_adj_settings["locationAccuracy"].lower()
                    != location_accuracy.lower()
                ):
                    project_adj_settings.update({"locationAccuracy": location_accuracy})
            elif context is None:
                context = dict(project_adj_settings)
                _nestify_context(context)
            # update the settings to update flight json
            settings = project_adj_settings
        except:
            adj_dict = {}
            if isinstance(context, dict):
                context_new = {k.lower(): v for k, v in context.items()}
                adj_keys = [
                    "computeCandidate",
                    "maxOverlap",
                    "maxLoss",
                    "maxResidual",
                    "initPointResolution",
                    "k",
                    "p",
                    "principalPoint",
                    "focalLength",
                ]
                adj_dict = {
                    k: context_new[k.lower()]
                    for k in adj_keys
                    if k.lower() in context_new
                }
                adj_dict.update({"locationAccuracy": location_accuracy})
                settings = adj_dict

        settings.update({"mode": mode})
        flight_json_details = {
            "update_flight_json": update_flight_json,
            "mission": mission,
            "item_name": "adjustment",
            "adjust_settings": settings,
        }

    return gis._tools.realitymapping.compute_sensor_model(
        image_collection=image_collection,
        mode=mode,
        location_accuracy=location_accuracy,
        context=context,
        future=future,
        flight_json_details=flight_json_details,
        **kwargs,
    )


###################################################################################################
## Alter processing states
###################################################################################################
def alter_processing_states(
    mission,
    new_states: dict[str, Any],
    *,
    gis: Optional[GIS] = None,
    future: bool = False,
    **kwargs,
):
    """
    Alter the processing states of the image collection.
    The states are stored as key property "Orthomapping".
    The content of the state is a dictionary including
    several properties which can be set based on the process
    done on the image collection.

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    mission                Required, This is the image collection that will be adjusted.

                           The mission can be a RMMission object, an image service URL or portal Item or a datastore URI.

                           The mission must exist.
    ------------------     --------------------------------------------------------------------
    new_states             Required dictionary. The state to set on the image_collection

                           This a dictionary of states that should be set on the image collection
                           The new states that can be set on the image collection are:
                           blockadjustment, dem, gcp, seamlines, colorcorrection, adjust_index, imagetype

                           Example:

                               | {"blockadjustment": "raw",
                               |  "dem": "Dense_Natual_Neighbor",
                               |  "seamlines":"VORONOI",
                               |  "colorcorrection":"SingleColor",
                               |  "imagetype": "UAV/UAS",
                               |  "adjust_index": 0}
    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================

    :return:
        The result will be the newly set states dictionary

    """
    gis = arcgis.env.active_gis if gis is None else gis
    from ._realitymapping_mission import RMMission

    image_collection = mission
    if isinstance(mission, RMMission):
        image_collection = image_collection.image_collection

    return gis._tools.realitymapping.alter_processing_states(
        image_collection=image_collection,
        new_states=new_states,
        future=future,
        **kwargs,
    )


###################################################################################################
## Get processing states
###################################################################################################
def get_processing_states(
    mission, *, gis: Optional[GIS] = None, future: bool = False, **kwargs
):
    """
    Retrieve the processing states of the image collection

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    mission                Required, This is the image collection that will be adjusted.

                           The mission can be a RMMission object, an image service URL or portal Item or a datastore URI.

                           The mission must exist.
    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================

    :return:
        The result will be the newly set states dictionary

    """

    gis = arcgis.env.active_gis if gis is None else gis
    from ._realitymapping_mission import RMMission

    image_collection = mission
    if isinstance(mission, RMMission):
        image_collection = mission.image_collection

    return gis._tools.realitymapping.get_processing_states(
        image_collection=image_collection, future=future, **kwargs
    )


###################################################################################################
## Match control points
###################################################################################################
def match_control_points(
    mission,
    control_points: list[dict[str, Any]],
    similarity: str = "High",
    context: Optional[dict[str, Any]] = None,
    *,
    gis: Optional[GIS] = None,
    future: bool = False,
    **kwargs,
):
    """
    The match_control_points is a function that takes a collection of ground control points
    as input (control points to be specified as a list of dictionary objects), and each of the 
    ground control points needs at least one matching tie point in the control point sets. 
    The function will compute the remaining matching tie points for all control point sets.
    
    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    mission                Required, the input image collection that will be adjusted.

                           The mission can be a RMMission object, an image service URL or portal Item or a datastore URI.
                            
                           The mission must exist.
    ------------------     --------------------------------------------------------------------
    control_points         Required, a list of control point sets objects.

                           The schema of control points follows the schema 
                           of the mosaic dataset control point table. 

                           The control point object should contain the point geometry, pointID, type, status and the
                           imagePoints. (the imagePoints attribute inside the control points object lists the imageIDs)

                           -- pointID (int) - The ID of the point within the control point table.

                           -- type (int)    - The type of the control point as determined by its numeric value

                                                 1: Tie Point 
                                                 2: Ground Control Point.
                                                 3: Check Point

                           -- status (int)  - The status of the point. A value of 0 indicates that the point will not be used in computation. A non-zero value indicates otherwise.

                           -- imageID (int) - Image identification using the ObjectID from the mosaic dataset footprint table.

                           Example:

                               | [{
                               | "status": 1,
                               | "type": 2,
                               | "x": -117.0926538,
                               | "y": 34.00704253,
                               | "z": 634.2175,
                               | "spatialReference": {
                               |     "wkid": 4326
                               | }, // default WGS84
                               | "imagePointSpatialReference": {}, // default ICS
                               | "pointId": 1,
                               | "xyAccuracy": "0.008602325",
                               | "zAccuracy": "0.015",
                               | "imagePoints": [{
                               |     "imageID": 1,
                               |     "x": 2986.5435987557084,
                               |     "y": -2042.5193648409431,
                               |     "u": 3057.4580682832734,
                               |     "v": -1909.1506872159698
                               | },
                               | {
                               |     "imageID": 2,
                               |     "x": 1838.2814361401108,
                               |     "y": -2594.5280063817972,
                               |     "u": 3059.4079724863363,
                               |     "v": -2961.292545463305
                               | },
                               | {
                               |     "imageID": 12,
                               |     "x": 5332.855578204663,
                               |     "y": -2533.2805429751907,
                               |     "u": 614.2338676573158,
                               |     "v": -165.10836768947297
                               | },
                               | {
                               |     "imageID": 13,
                               |     "x": 4932.0895715254455,
                               |     "y": -1833.8401744114287,
                               |     "u": 616.9396928182223,
                               |     "v": -1243.1445126959693
                               | }]
                               | },
                               | …
                               | …
                               | ] 
    ------------------     --------------------------------------------------------------------
    similarity             Optional string. Choose the tolerance level for your control point matching. 

                           - Low- The similarity tolerance for finding control points will be low. \
                           This option will produce the most control points, \
                           but some may have a higher level of error. 

                           - Medium - The similarity tolerance for finding control points will be medium.
                           
                           - High - The similarity tolerance for finding control points will be high. \
                           This option will produce the least number of control points, \
                           but each matching pair will have a lower level of error. This is the default. 
    ------------------     --------------------------------------------------------------------
    context                Optional dictionary.Additional settings such as the input control points 
                           spatial reference can be specified here. 

                           For Example:

                                {"groundControlPointsSpatialReference": {"wkid": 3459}, "imagePointSpatialReference": {"wkid": 3459}}

                           Note: The ground control points spatial reference and image point spatial reference 
                           spatial reference set in the context parameter is to decide the returned point set's 
                           ground control points spatial reference and image point spatial reference. 
                           If these two parameters are not set here, the tool will use the spatial reference 
                           defined in the input point set. And if no spatial reference is defined in the point set,
                           then the default ground control points coordinates are in lon/lat and image points 
                           coordinates are in image coordinate system. 
    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================

    :return:
        A list of dictionary objects

    """
    gis = arcgis.env.active_gis if gis is None else gis
    update_flight_json = False
    flight_json_details = {}
    from ._realitymapping_mission import RMMission

    image_collection = mission
    if isinstance(mission, RMMission):
        image_collection = mission.image_collection
        update_flight_json = True

        flight_json_details = {
            "update_flight_json": update_flight_json,
            "mission": mission,
            "item_name": "matchControlPoint",
        }

    return gis._tools.realitymapping.match_control_points(
        image_collection=image_collection,
        control_points=control_points,
        similarity=similarity,
        context=context,
        future=future,
        flight_json_details=flight_json_details,
        **kwargs,
    )


###################################################################################################
## Compute Control Points
###################################################################################################
def compute_control_points(
    mission,
    reference_image=None,
    image_location_accuracy: str = "High",
    context: Optional[dict[str, Any]] = None,
    *,
    gis: Optional[GIS] = None,
    future: bool = False,
    **kwargs,
):
    """
    This service tool is used for computing matching control points between images
    within an image collection and/or matching control points between the image 
    collection images and the reference image.
    `Compute Control Points <https://pro.arcgis.com/en/pro-app/tool-reference/data-management/compute-control-points.htm>`_
    
    ====================================    ====================================================================
    **Parameter**                            **Description**
    ------------------------------------    --------------------------------------------------------------------
    mission                                 Required. This is the image collection that will be adjusted.

                                            The mission can be a RMMission object, an image service URL or portal Item or a datastore URI.
                            
                                            The mission must exist.
    ------------------------------------    --------------------------------------------------------------------
    reference_image                         This is the reference image service that can be used to generate ground control 
                                            points set with the image service. 
                                            It can be a portal Item or an image service URL or a URI
    ------------------------------------    --------------------------------------------------------------------
    image_location_accuracy                 Optional string. This option allows you to specify the GPS location accuracy 
                                            level of the source image. It determines how far the tool will search for 
                                            neighboring matching images for calculating tie points and block adjustments. 
                                            
                                            The following are the available options:
                                            Low, Medium, High

                                            - Low- GPS accuracy of 20 to 50 meters, and the tool uses a maximum of 4 by 12 images. 

                                            - Medium- GPS accuracy of 10 to 20 meters, and the tool uses a maximum of 4 by 6 images. 

                                            - High- GPS accuracy of 0 to 10 meters, and the tool uses a maximum of 4 by 3 images.

                                            If the image collection is created from satellite data, it will be automatically switched 
                                            to use RPC adjustment mode. In this case, the mode need not be explicitly set by the user.

                                            Default is High
    ------------------------------------    --------------------------------------------------------------------
    context                                 Optional dictionary. Context contains additional environment settings that affect 
                                            output control points generation. 
                                            
                                            Possible keys and their possible values are: 

                                            pointSimilarity- Sets LOW, MEDIUM, or HIGH tolerance for computing control points with varying levels of potential error.
                                                             
                                            - LOW tolerance will produce the most control point, but may have a higher \
                                              level of error.

                                            - HIGH tolerance will produce the least number of control point, \
                                              but each matching pair will have a lower level of error.

                                            - MEDIUM tolerance will set the similarity tolerance to medium.

                                            pointDensity- Sets the number of tie points (LOW, MEDIUM, or HIGH), to be created. 
                                                          
                                            - LOW point density will create the fewest number of tie points. \

                                            - MEDIUM point density will create a moderate number of tie points. \

                                            - HIGH point density will create the highest number of tie points. \

                                            pointDistribution- Randomly generates points that are better for overlapping areas with irregular shapes.
                                                               
                                            - RANDOM- will generate points that are better for overlapping areas \
                                              with irregular shapes.

                                            - REGULAR- will generate points based on a \
                                              fixed pattern and uses the point density to determine how frequently to create points.

                                            Example:

                                                {
                                                "pointSimilarity":"MEDIUM",
                                                "pointDensity": "MEDIUM",
                                                "pointDistribution": "RANDOM"
                                                }
    ------------------------------------    --------------------------------------------------------------------
    gis                                     Optional :class:`~arcgis.gis.GIS` . the GIS on which this tool runs. If not specified, the active GIS is used.
    ====================================    ====================================================================

    :return:
        The imagery layer url

    """
    gis = arcgis.env.active_gis if gis is None else gis
    update_flight_json = False
    flight_json_details = {}
    from ._realitymapping_mission import RMMission

    image_collection = mission
    if isinstance(mission, RMMission):
        image_collection = mission.image_collection
        update_flight_json = True

        flight_json_details = {
            "update_flight_json": update_flight_json,
            "mission": mission,
            "item_name": "computeControlPoints",
        }

    return gis._tools.realitymapping.compute_control_points(
        image_collection=image_collection,
        reference_image=reference_image,
        image_location_accuracy=image_location_accuracy,
        context=context,
        future=future,
        flight_json_details=flight_json_details,
        **kwargs,
    )


###################################################################################################
## Edit control points
###################################################################################################
def edit_control_points(
    mission,
    control_points: list[dict[str, Any]],
    *,
    gis: Optional[GIS] = None,
    future: bool = False,
    **kwargs,
):
    """
    This service can be used to append additional ground control point sets to
    the image collection's control points. It is recommended that a ground control point (GCP) set
    should contain one ground control point and multiple tie points.
    The service tool can also be used to edit tie point sets.
    The input control points dictionary will always replace the points in the tie points
    table if the point IDs already exist.

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    mission                Required.
                           The mission can be a RMMission object, an image service URL or portal Item or a datastore URI.
                           The mission must exist.
    ------------------     --------------------------------------------------------------------
    control_points         Required, a list of control point sets objects.

                           The schema of control points follows the schema
                           of the mosaic dataset control point table.

                           The control point object should contain the point geometry, pointID, type, status and the
                           imagePoints. (the imagePoints attribute inside the control points object lists the imageIDs)

                           -- pointID (int) - The ID of the point within the control point table.

                           -- type (int)    - The type of the control point as determined by its numeric value

                                                 1: Tie Point
                                                 2: Ground Control Point.
                                                 3: Check Point

                           -- status (int)  - The status of the point. A value of 0 indicates that the point will not be used in computation. A non-zero value indicates otherwise.

                           -- imageID (int) - Image identification using the ObjectID from the mosaic dataset footprint table.

                           Example:

                               | [{
                               | "status": 1,
                               | "type": 2,
                               | "x": -117.0926538,
                               | "y": 34.00704253,
                               | "z": 634.2175,
                               | "spatialReference": {
                               |     "wkid": 4326
                               | }, // default WGS84
                               | "imagePointSpatialReference": {}, // default ICS
                               | "pointId": 1,
                               | "xyAccuracy": "0.008602325",
                               | "zAccuracy": "0.015",
                               | "imagePoints": [{
                               |     "imageID": 1,
                               |     "x": 2986.5435987557084,
                               |     "y": -2042.5193648409431,
                               |     "u": 3057.4580682832734,
                               |     "v": -1909.1506872159698
                               | },
                               | {
                               |     "imageID": 2,
                               |     "x": 1838.2814361401108,
                               |     "y": -2594.5280063817972,
                               |     "u": 3059.4079724863363,
                               |     "v": -2961.292545463305
                               | },
                               | {
                               |     "imageID": 12,
                               |     "x": 5332.855578204663,
                               |     "y": -2533.2805429751907,
                               |     "u": 614.2338676573158,
                               |     "v": -165.10836768947297
                               | },
                               | {
                               |     "imageID": 13,
                               |     "x": 4932.0895715254455,
                               |     "y": -1833.8401744114287,
                               |     "u": 616.9396928182223,
                               |     "v": -1243.1445126959693
                               | }]
                               | },
                               | …
                               | …
                               | ]


    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================

    :return:
        The Imagery layer url

    """

    gis = arcgis.env.active_gis if gis is None else gis
    update_flight_json = False
    flight_json_details = {}
    from ._realitymapping_mission import RMMission

    image_collection = mission
    if isinstance(mission, RMMission):
        image_collection = mission.image_collection
        update_flight_json = True

        flight_json_details = {
            "update_flight_json": update_flight_json,
            "mission": mission,
            "item_name": "appendControlPoints",
        }

    return gis._tools.realitymapping.edit_control_points(
        image_collection=image_collection,
        input_control_points=control_points,
        future=future,
        flight_json_details=flight_json_details,
        **kwargs,
    )


###################################################################################################
## Generate orthomosaic
###################################################################################################
def generate_orthomosaic(
    mission,
    out_ortho,
    regen_seamlines: bool = True,
    recompute_color_correction: bool = True,
    context: Optional[dict[str, Any]] = None,
    *,
    gis: Optional[GIS] = None,
    future: bool = False,
    **kwargs,
):
    """
    Function can be used for generating single ortho-rectified mosaicked image from image collection after
    the block adjustment.

    ===================================    ====================================================================
    **Parameter**                           **Description**
    -----------------------------------    --------------------------------------------------------------------
    mission                                Required. The input image collection that will be used
                                           to generate the ortho-mosaic from.
                                           The mission can be a RMMission object, an image service URL or portal Item or a datastore URI.
                                           The mission must exist.
    -----------------------------------    --------------------------------------------------------------------
    out_ortho                               Required. This is the ortho-mosaicked image converted from the image
                                            collection after the block adjustment.
                                            It can be a url, uri, portal item, or string representing the name of output dem
                                            (either existing or to be created.)
                                            Like Raster Analysis services, the service can be an existing multi-tenant service URL.
    -----------------------------------    --------------------------------------------------------------------
    regen_seamlines                        Optional, boolean.
                                           Choose whether to apply seamlines before the orthomosaic image generation or not.
                                           The seamlines will always be regenerated if this parameter is set to True.
                                           The user can set the seamline options through the context parameter.
                                           If the seamline generation options are not set, the default will be used.

                                           Default value is True
    -----------------------------------    --------------------------------------------------------------------
    recompute_color_correction              Optional, boolean.
                                            Choose whether to apply color correction settings to the output ortho-image or not.
                                            Color correction will always be recomputed if this option is set to True.
                                            The user can configure the compute color correction settings through the context parameter.
                                            If there is no color collection setting, the default will be used.

                                            Default value is True
    -----------------------------------    --------------------------------------------------------------------
    context                                Optional dictionary. Context contains additional environment settings that affect output
                                           image. The supported environment settings for this tool are:

                                           1. Output Spatial Reference (outSR)-the output features will
                                              be projected into the output spatial reference.

                                           2. Extent (extent) - extent that would clip or expand the output image

                                           3. Cell Size (cellSize) - The output raster will have the resolution specified by cell size.

                                           4. Compute Seamlines (seamlinesMethod) - Default.

                                           5. Clipping Geometry (clippingGeometry) - Clips the orthomosaic image to an area of
                                              interest defined by the geometry.

                                           6. Orthomosaic As Overview (orthoMosaicAsOvr) - Adds the orthomosaic as an overview of the image collection.

                                           7. Compute Color Correction (colorcorrectionMethod) — Default.

                                           Example:

                                               | {
                                               |   "outSR": {"wkid": 3516},
                                               |   "extent": {"xmin": 470614.263139,
                                               |             "ymin": 8872849.409968,
                                               |             "xmax": 532307.351827,
                                               |             "ymax": 8920205.372412,
                                               |             "spatialReference": {"wkid": 32628}},
                                               |   "clippingGeometry": {},
                                               |   "orthoMosaicAsOvr": False,
                                               |   "seamlinesMethod": "VORONOI",
                                               |   "minRegionSize": 100,
                                               |   "pixelSize": "",
                                               |   "blendType": "Both",
                                               |   "blendWidth": None,
                                               |   "blendUnit": "Pixels",
                                               |   "requestSize": 1000,
                                               |   "minThinnessRatio": 0.05,
                                               |   "maxSliverSize": 20
                                               |   "colorCorrectionMethod": "DODGING",
                                               |   "dodgingSurface": "Single_Color",
                                               |   "referenceImg": {"url": "``https://...``"},
                                               |   "skipRows": 10,
                                               |   "skipCols": 10,
                                               |   "reCalculateSats": "OVERWRITE"
                                               |  }
    -----------------------------------    --------------------------------------------------------------------
    gis                                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ===================================    ====================================================================

    :return:
        The Orthomosaicked Imagery layer item

    """
    gis = arcgis.env.active_gis if gis is None else gis

    update_flight_json = False
    from ._realitymapping_mission import RMMission

    image_collection = mission
    flight_json_details = {}
    if isinstance(mission, RMMission):
        image_collection = mission.image_collection
        update_flight_json = True

        if mission.workspace:
            if context:
                context["workspace"] = mission.workspace
            else:
                context = {"workspace": mission.workspace}

        if kwargs is not None:
            if "folder" in kwargs:
                folder = kwargs["folder"]
            else:
                for f in gis.users.me.folders:
                    if f._fid == image_collection.ownerFolder:
                        folder = f.properties
                        break
            kwargs.update({"folder": folder})

        color_balance_keys = [
            "targetRaster",
            "skipX",
            "skipY",
            "overwriteStats",
            "dodgingSurface",
            "colorCorrectionMethod",
        ]
        color_balance_dict = {}
        color_balance_dict.update(
            {
                "colorBalance": {
                    "skipX": 0,
                    "skipY": 0,
                    "overwriteStats": "SKIP_EXISTING",
                    "colorCorrectionMethod": "DODGING",
                    "dodgingSurface": "SINGLE_COLOR",
                    "targetImage": "",
                }
            }
        )

        ortho_dict = {}
        if isinstance(context, dict):
            context_new = {k.lower(): v for k, v in context.items()}
            color_balance_dict["colorBalance"].update(
                {
                    k: context_new[k.lower()]
                    for k in color_balance_keys
                    if k.lower() in context_new
                }
            )
            if "colorCorrectionMethod" in color_balance_dict["colorBalance"]:
                color_balance_dict["colorBalance"]["method"] = color_balance_dict[
                    "colorBalance"
                ].pop("colorCorrectionMethod")
            if "dodgingSurface" in color_balance_dict["colorBalance"]:
                color_balance_dict["colorBalance"]["surfaceType"] = color_balance_dict[
                    "colorBalance"
                ].pop("dodgingSurface")

            seamline_keys = [
                "computeCandidate",
                "maxOverlap",
                "maxLoss",
                "pixelSize",
                "blendType",
                "blendUnit",
                "requestSizeType",
                "requestSize",
                "minThinnessRatio",
                "maxSliverSize",
                "seamlinesMethod",
            ]
            seamline_dict = {}
            seamline_dict.update(
                {
                    "seamline": {
                        "seamlinesMethod": "DISPARITY",
                        "minRegionSize": 100,
                        "pixelSize": "",
                        "blendType": "Both",
                        "blendWidth": None,
                        "blendUnit": "Pixels",
                        "requestSizeType": "Pixels",
                        "requestSize": 1000,
                        "minThinnessRatio": 0.05,
                        "maxSliverSize": 20,
                    }
                }
            )

            seamline_dict["seamline"].update(
                {
                    k: context_new[k.lower()]
                    for k in seamline_keys
                    if k.lower() in context_new
                }
            )
            if "seamlinesMethod" in seamline_dict["seamline"]:
                seamline_dict["seamline"]["method"] = seamline_dict["seamline"].pop(
                    "seamlinesMethod"
                )

            ortho_mosaic_as_ovr = context.get("orthoMosaicAsOvr", False)
            ortho_dict = {"ortho": {"orthoMosaicAsOvr": ortho_mosaic_as_ovr}}

            if regen_seamlines:
                ortho_dict.update(seamline_dict)
            if recompute_color_correction:
                ortho_dict.update(color_balance_dict)

        flight_json_details = {
            "update_flight_json": update_flight_json,
            "mission": mission,
            "item_name": "ortho",
            "processing_states": ortho_dict,
        }

    return gis._tools.realitymapping.generate_orthomosaic(
        image_collection=image_collection,
        output_ortho_image=out_ortho,
        regen_seamlines=regen_seamlines,
        recompute_color_correction=recompute_color_correction,
        context=context,
        future=future,
        flight_json_details=flight_json_details,
        **kwargs,
    )


###################################################################################################
## Generate report
###################################################################################################
def generate_report(
    mission,
    report_format: str = "PDF",
    *,
    gis: Optional[GIS] = None,
    future: bool = False,
    **kwargs,
):
    """
    This function is used to generate realitymapping report with image collection
    that has been block adjusted. The report would contain information about
    the quality of the adjusted images, the distribution of the control points, etc.
    The output of this service tool is a downloadable html page.

    ===================    ====================================================================
    **Parameter**           **Description**
    -------------------    --------------------------------------------------------------------
    mission                Required. The input image collection that should be
                           used to generate a report from.
                           The mission can be a RMMission object, an image service URL or portal Item or a datastore URI.
                           The mission must exist.
    -------------------    --------------------------------------------------------------------
    report_format          Type of the format to be generated. Possible PDF, HTML. Default - PDF
    -------------------    --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ===================    ====================================================================

    :return:
        The URL of a single html webpage that is a formatted realitymapping report

    """
    gis = arcgis.env.active_gis if gis is None else gis
    update_flight_json = False
    flight_json_details = {}
    from ._realitymapping_mission import RMMission

    image_collection = mission
    if isinstance(mission, RMMission):
        image_collection = mission.image_collection
        update_flight_json = True

        flight_json_details = {
            "update_flight_json": update_flight_json,
            "mission": mission,
            "item_name": "report",
        }

    return gis._tools.realitymapping.generate_report(
        image_collection=image_collection,
        report_format=report_format,
        future=future,
        flight_json_details=flight_json_details,
        **kwargs,
    )


###################################################################################################
## query camera info
###################################################################################################
def query_camera_info(
    camera_query: Optional[str] = None,
    *,
    gis: Optional[GIS] = None,
    future: bool = False,
    **kwargs,
):
    """
    This service tool is used to query specific or the entire digital camera
    database. The digital camera database contains the specs
    of digital camera sensors that were used to capture drone images.

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    camera_query           Required String. This is a SQL query statement that can
                           be used to filter a portion of the digital camera
                           database.
                           Digital camera database can be queried using the fields Make, Model,
                           Focallength, Columns, Rows, PixelSize.

                           Example:

                            "Make='Rollei' and Model='RCP-8325'"
    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================


    :return:
        Data Frame representing the camera database

    """
    gis = arcgis.env.active_gis if gis is None else gis

    return gis._tools.realitymapping.query_camera_info(
        camera_query=camera_query, future=future, **kwargs
    )


###################################################################################################
## query control points
###################################################################################################
def query_control_points(
    mission,
    query: str,
    *,
    gis: Optional[GIS] = None,
    future: bool = False,
    **kwargs,
):
    """
    Query for control points in an image collection. It allows users to query
    among certain control point sets that has ground control points inside.

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    mission                Required, the input image collection on which to query
                           the the control points.

                           The mission can be a RMMission object, an image service URL or portal Item or a datastore URI.

                           The mission must exist.
    ------------------     --------------------------------------------------------------------
    query                  Required string. a SQL statement used for querying the point;

                           Example:

                            "pointID > 100"
    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================


    :return:
        A dictionary object

    """
    gis = arcgis.env.active_gis if gis is None else gis
    update_flight_json = False
    flight_json_details = {}
    from ._realitymapping_mission import RMMission

    image_collection = mission
    if isinstance(mission, RMMission):
        image_collection = mission.image_collection
        update_flight_json = True

        flight_json_details = {
            "update_flight_json": update_flight_json,
            "mission": mission,
            "item_name": "queryControlPoints",
        }

    return gis._tools.realitymapping.query_control_points(
        image_collection=image_collection,
        where=query,
        future=future,
        flight_json_details=flight_json_details,
        **kwargs,
    )


###################################################################################################
## Reset image collection
###################################################################################################
def reset_image_collection(
    mission, *, gis: Optional[GIS] = None, future: bool = False, **kwargs
):
    """
    Reset the image collection. It is used to reset the image collection to its
    original state. The image collection could be adjusted during the orthomapping
    workflow and if the user is not satisfied with the result, they will be able
    to clear any existing adjustment settings and revert the images back to
    un-adjusted state

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    mission                Required, the input image collection to reset
                           The mission can be a RMMission object, an image service URL or portal Item or a datastore URI.

                           The mission must exist.
    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================

    :return:
        A boolean indicating whether the reset was successful or not

    """
    gis = arcgis.env.active_gis if gis is None else gis
    from ._realitymapping_mission import RMMission

    image_collection = mission
    if isinstance(mission, RMMission):
        image_collection = mission.image_collection
        update_flight_json = True

        flight_json_details = {
            "update_flight_json": update_flight_json,
            "mission": mission,
            "item_name": "reset",
        }

    return gis._tools.realitymapping.reset_image_collection(
        image_collection=image_collection,
        future=future,
        flight_json_details=flight_json_details,
        **kwargs,
    )


def compute_spatial_reference_factory_code(latitude: float, longitude: float):
    """
    Computes spatial reference factory code. This value may be used as out_sr value in create image collection function

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    latitude               latitude value in decimal degrees that will be used to compute UTM zone
    ------------------     --------------------------------------------------------------------
    longitude              longitude value in decimal degrees that will be used to compute UTM zone
    ==================     ====================================================================

    :return:
        factory_code : spatial reference factory code
    """
    from math import isnan, fabs, floor

    zone = 0
    if (
        isnan(longitude)
        or isnan(latitude)
        or fabs(longitude) > 180.0
        or fabs(latitude) > 90.0
    ):
        raise RuntimeError("Incorrect latitude or longitude value")

    zone = floor((longitude + 180) / 6) + 1
    if latitude >= 56.0 and latitude < 64.0 and longitude >= 3.0 and longitude < 12.0:
        zone = 32

    if latitude >= 72.0 and latitude < 84.0:
        if longitude >= 0.0 and longitude < 9.0:
            zone = 31
        elif longitude >= 9.0 and longitude < 21.0:
            zone = 33
        elif longitude >= 21.0 and longitude < 33.0:
            zone = 35
        elif longitude >= 33.0 and longitude < 42.0:
            zone = 37

    if latitude >= 0:
        srid = 32601
    else:
        srid = 32701

    factory_code = srid + zone - 1

    return factory_code


###################################################################################################
## Query exif info
###################################################################################################
def query_exif_info(
    input_images, *, gis: Optional[GIS] = None, future: bool = False, **kwargs
):
    """
    The `query_exif_info` reads the Exif header metadata from single or
    multiple images in shared data store. The Exif metadata is usually stored
    in drone image files. Some common Exif metadata information are GPS
    locations, camera model, focal length, and more.

    ==================     ====================================================================
    **Parameter**           **Description**
    ------------------     --------------------------------------------------------------------
    input_images           Required String/list of Strings.  The input images could be a single image path, list of image paths,
                           or a folder path, or a list of folder paths. The image file paths can also be server data store path.

                           Eg:

                           - "\\servername\drone\imagefolder\image_file.jpg"
                           - "/cloudStores/S3DataStore/yvwd13"
                           - "/fileShares/drones/SampleEXIF/YUN_0040.jpg"
                           - ["/fileShares/drones/SampleEXIF/DJI_0002.JPG", "/fileShares/drones/SampleEXIF/YUN_0040.jpg"]
                           - ["/cloudStores/S3DataStore/yvwd13", "/cloudStores/S3DataStore/BogotaFarm"]
    ------------------     --------------------------------------------------------------------
    gis                    Optional :class:`~arcgis.gis.GIS` . The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================

    :return:
        A dictionary object

    """
    gis = arcgis.env.active_gis if gis is None else gis

    return gis._tools.realitymapping.query_exif_info(
        input_images=input_images, future=future, **kwargs
    )


###################################################################################################
## Reconstruct surface
###################################################################################################
def reconstruct_surface(
    mission,
    scenario: Optional[str] = "DRONE",
    forward_overlap: Optional[int] = None,
    sideward_overlap: Optional[int] = None,
    quality: Optional[str] = "ULTRA",
    area_of_interest: Optional[Union[str, FeatureLayer]] = "AUTO",
    waterbody_features: Optional[FeatureLayer] = None,
    correction_feature: Optional[FeatureLayer] = None,
    reconstruct_options: Optional[str] = None,
    output_dsm_name: Optional[str] = None,
    output_true_ortho_name: Optional[str] = None,
    output_dsm_mesh_name: Optional[str] = None,
    output_point_cloud_name: Optional[str] = None,
    output_mesh_name: Optional[str] = None,
    output_dtm_name: Optional[str] = None,
    context: Optional[dict[str, Any]] = None,
    *,
    gis: Optional[GIS] = None,
    future: bool = False,
    **kwargs,
):
    """
    The `reconstruct_surface` generates a digital surface model (DSM), true
    orthos, 2.5D meshes, 3D meshes, and point clouds from adjusted imagery.

    =========================================================================   ===========================================================================
    **Parameter**                                                                **Description**
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    mission                                                                     Required String/Item. The adjusted input image collection.
                                                                                The mission can be a RMMission object, an image service URL or portal Item or a datastore URI.
                                                                                The mission must exist.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    scenario                                                                    Optional String. Specifies the type of imagery that will be used to generate the output products.

                                                                                - DRONE: The input imagery will be defined as having been acquired with drones or terrestrial cameras.
                                                                                - AERIAL_NADIR: The input imagery will be defined as having been acquired with large, photogrammetric camera systems.
                                                                                - AERIAL_OBLIQUE: The input imagery will be defined as having been acquired with oblique camera systems.
                                                                                - SATELLITE: The input imagery will be defined as having been acquired with a satellite.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    forward_overlap                                                             Optional Integer. The forward (in-strip) overlap percentage that will be used between the images.
                                                                                The default is 60.
                                                                                This parameter is enabled when the scenario parameter is set to AERIAL_NADIR.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    sideward_overlap                                                            Optional Integer. The sideward (cross-strip) overlap percentage that will be used between the images.
                                                                                The default is 30.
                                                                                This parameter is enabled when the scenario parameter is set to AERIAL_NADIR.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    quality                                                                     Optional String. Specifies the quality of the final product.

                                                                                - ULTRA - Input images will be used at their original (full) resolution.
                                                                                - HIGH - Input images will be downsampled two times.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    area_of_interest                                                            Optional :class:`~arcgis.features.FeatureLayer` or String. The area of interest that will
                                                                                be used to select images for processing. The area of interest can be computed automatically
                                                                                or defined using an input feature.
                                                                                If the value contains 3D geometries, the z-component will be ignored. If the value includes
                                                                                overlapping features, the union of these features will be computed.

                                                                                - NONE - All images will be used in processing.
                                                                                - AUTO - The processing extent will be calculated automatically. This is the default.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    waterbody_features                                                          Optional :class:`~arcgis.features.FeatureLayer`. A polygon that will define the extent of large water bodies.
                                                                                For the best results, use a 3D feature.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    correction_features                                                         Optional :class:`~arcgis.features.FeatureLayer`. A polygon that will define the extent of all surfaces that are not water bodies.
                                                                                The value must be a 3D feature.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    reconstruction_options                                                      Optional dict or shared data path (this path must be accessible by the server).
                                                                                This specifies the values for the tool parameters. If this parameter is specified, the properties of
                                                                                the file or dictionary will set the default values for the remaining optional parameters.
                                                                                The list of keywords and an example of this JSON can be found here:
                                                                                `Reconstruct Surface tool <https://pro.arcgis.com/en/pro-app/latest/tool-reference/reality-mapping/reconstruct-surface.htm>`_
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    output_dsm_name                                                             Optional String. You can pass in the name of the output Image Service that should be created by this method to be
                                                                                used as the output for the tool.

                                                                                A RuntimeError is raised if a service by that name already exists.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    output_true_ortho_name                                                      Optional String. You can pass in the name of the output Image Service that should be created by this method to be
                                                                                used as the output for the tool.

                                                                                A RuntimeError is raised if a service by that name already exists.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    output_dsm_mesh_name                                                        Optional String. You can pass in the name of the output Image Service that should be created by this method to be
                                                                                used as the output for the tool.

                                                                                A RuntimeError is raised if a service by that name already exists.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    output_point_cloud_name                                                     Optional String. You can pass in the name of the output Image Service that should be created by this method to be
                                                                                used as the output for the tool.

                                                                                A RuntimeError is raised if a service by that name already exists.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    output_mesh_name                                                            Optional String. You can pass in the name of the output Image Service that should be created by this method to be
                                                                                used as the output for the tool.

                                                                                A RuntimeError is raised if a service by that name already exists.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    output_dtm_name                                                             Optional String. You can pass in the name of the output Image Service that should be created by this method to be
                                                                                used as the output for the tool.

                                                                                A RuntimeError is raised if a service by that name already exists.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    context                                                                     Context contains additional settings that affect task execution.

                                                                                context parameter overwrites values set through arcgis.env parameter

                                                                                This function has the following settings:

                                                                                - Extent (extent): A bounding box that defines the analysis area.

                                                                                    Example:

                                                                                        | {"extent": {"xmin": -122.68,
                                                                                        | "ymin": 45.53,
                                                                                        | "xmax": -122.45,
                                                                                        | "ymax": 45.6,
                                                                                        | "spatialReference": {"wkid": 4326}}}

                                                                                - Cell Size (cellSize): The output raster will have the resolution
                                                                                specified by cell size.

                                                                                    Example:

                                                                                        {'cellSize': 11} or {'cellSize': {'url': <image_service_url>}}  or {'cellSize': 'MaxOfIn'}

                                                                                - Parallel Processing Factor (parallelProcessingFactor): controls
                                                                                Raster Processing (CPU) service instances.

                                                                                    Example:

                                                                                    Syntax example with a specified number of processing instances:

                                                                                        {"parallelProcessingFactor": "2"}

                                                                                    Syntax example with a specified percentage of total
                                                                                    processing instances:

                                                                                        {"parallelProcessingFactor": "60%"}

                                                                                - Output DSM product settings: controls
                                                                                the environment variables for creating the DSM product.

                                                                                    Example:

                                                                                    Syntax example with a specified number of processing instances:

                                                                                        {key: {"outputType": "Tiled", "compression": "JPEG 75", "resamplingMethod": "NEAREST", "cellSize": 10, "noData": 0}}

                                                                                - Output True Ortho product settings: controls
                                                                                the environment variables for creating the DSM product.

                                                                                    Example:

                                                                                    Syntax example with a specified number of processing instances:

                                                                                        {"true_ortho": {"outputType": "Mosaic", "compression": "JPEG 75", "resamplingMethod": "NEAREST", "cellSize": 10, "noData": 0}}
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    gis                                                                         Optional, the GIS on which this tool runs. If not specified, the active GIS is used.
    -------------------------------------------------------------------------   ---------------------------------------------------------------------------
    future                                                                      Optional boolean. If True, the result will be a GPJob object and results will be returned asynchronously.
    =========================================================================   ===========================================================================

    :return: Named Tuple

    """
    gis = arcgis.env.active_gis if gis is None else gis
    from ._realitymapping_mission import RMMission

    update_flight_json = False
    flight_json_details = {}
    image_collection = mission
    if isinstance(mission, RMMission):
        image_collection = mission.image_collection
        update_flight_json = True

        flight_json_details = {
            "update_flight_json": update_flight_json,
            "mission": mission,
            "item_name": "reconstructSurface",
        }

        if mission.workspace:
            if context:
                context["workspace"] = mission.workspace
            else:
                context = {"workspace": mission.workspace}

        if kwargs is not None:
            if "folder" in kwargs:
                folder = kwargs["folder"]
            else:
                for f in gis.users.me.folders:
                    if f._fid == image_collection.ownerFolder:
                        folder = f.properties
                        break
            kwargs.update({"folder": folder})

    return gis._tools.realitymapping.reconstruct_surface(
        image_collection=image_collection,
        scenario=scenario,
        forward_overlap=forward_overlap,
        sideward_overlap=sideward_overlap,
        quality=quality,
        area_of_interest=area_of_interest,
        waterbody_features=waterbody_features,
        correction_feature=correction_feature,
        reconstruct_options=reconstruct_options,
        output_dsm_name=output_dsm_name,
        output_true_ortho_name=output_true_ortho_name,
        output_dsm_mesh_name=output_dsm_mesh_name,
        output_point_cloud_name=output_point_cloud_name,
        output_mesh_name=output_mesh_name,
        output_dtm_name=output_dtm_name,
        context=context,
        future=future,
        flight_json_details=flight_json_details,
        **kwargs,
    )


class RMProject:
    """

    RMProject represents an Realitymapping Project Item in the portal.

    Usage: ``arcgis.raster.RMProject(project, gis=gis)``

    ====================================     ====================================================================
    **Parameter**                             **Description**
    ------------------------------------     --------------------------------------------------------------------
    project                                  Required string or Realitymapping Project Item

                                             Example:

                                                | project = "RM_project"
                                                | om_item = gis.content.get("85a54236c6364a88a7c7c2b1a31fd901")
                                                | project = rm_item
    ------------------------------------     --------------------------------------------------------------------
    definition                               Optional dictionary. Custom project definition.
    ------------------------------------     --------------------------------------------------------------------
    gis                                      Optional  :class:`~arcgis.gis.GIS` . Represents the GIS object of the Realitymapping
                                             Project item.
    ====================================     ====================================================================

    .. code-block:: python

        # Example Usage

        project = RMProject('rm_proj', gis=gis)

        # Example Usage

        rm_item = gis.content.get("85a54236c6364a88a7c7c2b1a31fd901")
        project = RMProject(rm_item, gis=gis)

    """

    _spatial_reference = None

    def __init__(
        self,
        project=None,
        definition=None,
        sensor_type="Drone",
        scenario_type="Drone",
        *,
        gis: Optional[GIS] = None,
        **kwargs,
    ):
        if not isinstance(project, Item):
            try:
                project = _create_project(
                    name=project,
                    definition=definition,
                    sensor_type=sensor_type,
                    scenario_type=scenario_type,
                    gis=gis,
                )
            except:
                raise RuntimeError("Creation of realitymapping project failed.")

        if project.type == "Reality Mapping Project":  # Reality Mapping Project
            self._project_item = project
        else:
            raise RuntimeError(
                "Invalid project. Project is not of type Reality Mapping Project."
            )
        try:
            self._project_name = self._project_item.title
        except:
            self._project_name = self._project_item.name

        self._mission_list = []
        gis = arcgis.env.active_gis if gis is None else gis
        self._gis = gis

        content = self._gis.content
        fm = content.folders
        for folder in fm.list():
            if folder.properties["id"] == self._project_item.ownerFolder:
                self._folder = folder
                break

    @property
    def missions(self):
        """
        The ``missions`` property returns all the missions associated with the project

        :return: A list of missions of the realitymapping project
        """
        from ._realitymapping_mission import RMMission

        res_list = self._project_item.resources.list()
        self._mission_list = []
        for resource in res_list:
            full_res_name = resource["resource"]
            res_name = full_res_name[
                full_res_name.find("/") + 1 : full_res_name.find(".")
            ]
            self._mission_list.append(RMMission(mission_name=res_name, project=self))

        return self._mission_list

    @property
    def mission_count(self):
        """
        The ``count`` property returns the number of missions associated with the project

        :return: An integer representing the number of missions
        """
        res_list = self._project_item.resources.list()
        return len(res_list)

    @property
    def spatial_reference(self):
        if self._spatial_reference is None:
            try:
                item_data = self._project_item.get_data()
                self._spatial_reference = item_data.get("spatialReference", None)
            except:
                self._spatial_reference = None

        return self._spatial_reference

    @property
    def item(self):
        """
        The ``item`` property returns the portal item associated with the Project.

        :return: A portal item
        """
        return self._project_item

    def delete(self):
        """
        The ``delete`` method deletes the project item from the portal and all the associated products.

        :return: A boolean indicating whether the deletion was successful or not
        """
        deleted = self._folder.delete()
        return deleted

    @property
    def settings(self):
        settings = {}
        try:
            settings = self._project_item.get_data()
        except:
            pass
        return settings

    @settings.setter
    def settings(self, properties_dict):
        """
        The ``settings`` method updates the properties of the project item.

        """
        if properties_dict is None:
            raise ValueError("properties_dict cannot be None")
        item = self._project_item
        props = item.properties
        updated_item = item.update(item_properties=props, data=properties_dict)
        return updated_item

    # def create_project(self, name, definition: Optional[dict[str, Any]] = None):
    #    try:
    #        project_item = _create_project(name=name,
    #                                       definition=definition
    #                                       )
    #        self._project_item = project_item
    #        return True
    #    except:
    #        raise RuntimeError("Creation of realitymapping project failed.")

    def add_mission(
        self,
        image_list: list,
        mission_name: Optional[str] = None,
        image_collection: Optional[str] = None,
        raster_type_name: Optional[str] = None,
        raster_type_params: Optional[dict[str, Any]] = None,
        out_sr: Optional[dict[str, Any]] = None,
        context: Optional[dict[str, Any]] = None,
    ):
        """
        Add missions to the realitymapping project item. You can add imagery from one or more drone flights 
        to your realitymapping project item.

        ======================               ====================================================================
        **Parameter**                        **Description**
        ----------------------               --------------------------------------------------------------------
        project_item                         Required Item. The realitymapping project item to which the flight has to be added
        ----------------------               --------------------------------------------------------------------
        image_list                           Required, the list of input images to be added to
                                             the image collection being created. This parameter can
                                             be a list of image paths or a path to a folder containing the images

                                             The function can create hosted imagery layers on enterprise from 
                                             local raster datasets by uploading the data to the server.    
        ----------------------               --------------------------------------------------------------------
        mission_name                         Optional string. The name of the flight.
        ----------------------               --------------------------------------------------------------------
        image_collection                     Optional string, the name of the image collection to create.
                  
                                             The image collection can be an existing image service, in \
                                             which the function will create a mosaic dataset and the existing \
                                             hosted image service will then point to the new mosaic dataset.

                                             If the image collection does not exist, a new multi-tenant \
                                             service will be created.

                                             This parameter can be the Item representing an existing image_collection \
                                             or it can be a string representing the name of the image_collection \
                                             (either existing or to be created.)

                                             The image collection will be created in the same folder as the one created
                                             by the create_project method
        ----------------------               --------------------------------------------------------------------
        raster_type_name                     Optional string. The name of the raster type to use for adding data to \
                                             the image collection. Default is "UAV/UAS"

                                             Example:

                                                "UAV/UAS"
        ----------------------               --------------------------------------------------------------------
        raster_type_params                   Optional dict. Additional ``raster_type`` specific parameters.
        
                                             The process of add rasters to the image collection can be \
                                             controlled by specifying additional raster type arguments.

                                             The raster type parameters argument is a dictionary.

                                             The dictionary can contain productType, processingTemplate, \
                                             pansharpenType, Filter, pansharpenWeights, ConstantZ, \
                                             dem, zoffset, CorrectGeoid, ZFactor, StretchType, \
                                             ScaleFactor, ValidRange

                                             Please check the table below (Supported Raster Types), \
                                             for more details about the product types, \
                                             processing templates, pansharpen weights for each raster type. 

                                             - Possible values for pansharpenType - ["Mean", "IHS", "Brovey", "Esri", "Mean", "Gram-Schmidt"]
                                             - Possible values for filter - [None, "Sharpen", "SharpenMore"]
                                             - Value for StretchType dictionary can be as follows:

                                               - "None"
                                               - "MinMax; <min>; <max>"
                                               - "PercentMinMax; <MinPercent>; <MaxPercent>"
                                               - "StdDev; <NumberOfStandardDeviation>"
                                               Example: {"StretchType": "MinMax; <min>; <max>"}
                                             - Value for ValidRange dictionary can be as follows:

                                               - "<MaskMinValue>, <MaskMaxValue>"
                                               Example: {"ValidRange": "10, 200"}

                                             Example:

                                                {"productType":"All","processingTemplate":"Pansharpen",
                                                "pansharpenType":"Gram-Schmidt","filter":"SharpenMore",
                                                "pansharpenWeights":"0.85 0.7 0.35 1","constantZ":-9999}
        ----------------------               --------------------------------------------------------------------
        context                              Optional dict. The context parameter is used to provide additional input parameters.
    
                                             Syntax: {"image_collection_properties": {"imageCollectionType":"Satellite"},"byref":True}
                                        
                                             Use ``image_collection_properties`` key to set value for imageCollectionType.

                                             .. note::

                                                The "imageCollectionType" property is important for image collection that will later on be adjusted by realitymapping system service. 
                                                Based on the image collection type, the realitymapping system service will choose different algorithm for adjustment. 
                                                Therefore, if the image collection is created by reference, the requester should set this 
                                                property based on the type of images in the image collection using the following keywords. 
                                                If the imageCollectionType is not set, it defaults to "UAV/UAS"

                                             If ``byref`` is set to 'True', the data will not be uploaded. If it is not set, the default is 'False'

                                             The context parameter can also be used to specify whether to build overviews, \
                                             build footprints, to specify pixel value that represents the NoData etc.


                                             Example:

                                                | {"buildFootprints":True,                                            
                                                | "footprintsArguments":{"method":"RADIOMETRY","minValue":1,"maxValue":5,
                                                | "shrinkDistance":50,"skipOverviews":True,"updateBoundary":True,
                                                | "maintainEdge":False,"simplification":None,"numVertices":20,
                                                | "minThinnessRatio":0.05,"maxSliverSize":20,"requestSize":2000,
                                                | "minRegionSize":100},
                                                | "defineNodata":True,                                            
                                                | "noDataArguments":{"noDataValues":[500],"numberOfBand":99,"compositeValue":True},                                            
                                                | "buildOverview":True}

                                             The context parameter can be used to add new fields when creating \
                                             the image collection.


                                             Example:

                                                | {"fields": [{"name": "cloud_cover", "type": "Long"},
                                                | {"name": "cloud_shadow_count", "type": "Long"}]}
        ======================               ====================================================================

        :return: The imagery layer item

        """

        try:
            from ._realitymapping_mission import RMMission

            collection, mission_name = _add_mission(
                project=self,
                image_list=image_list,
                mission_name=mission_name,
                image_collection=image_collection,
                raster_type_name=raster_type_name,
                raster_type_params=raster_type_params,
                out_sr=out_sr,
                context=context,
            )
            return RMMission(mission_name=mission_name, project=self)

        except:
            raise RuntimeError("Failed to add the mission to the project")

    def get_mission(self, name):
        """
        Returns a RMMission object with the name specified using the name parameter.

        ==================                   ====================================================================
        **Parameter**                         **Description**
        ------------------                   --------------------------------------------------------------------
        name                                 Required string. The name of the RMMission.
        ==================                   ====================================================================

        :return: The imagery layer url


        """
        from ._realitymapping_mission import RMMission

        res_list = self._project_item.resources.list()
        for resource in res_list:
            full_res_name = resource["resource"]
            res_name = full_res_name[
                full_res_name.find("/") + 1 : full_res_name.find(".")
            ]
            if name == res_name:
                return RMMission(mission_name=name, project=self)

    def __repr__(self):
        return "<%s - %s>" % (type(self).__name__, self._project_name)
