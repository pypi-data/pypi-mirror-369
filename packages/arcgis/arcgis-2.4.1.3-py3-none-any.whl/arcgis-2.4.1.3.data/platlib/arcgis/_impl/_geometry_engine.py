import os
from enum import Enum


class GeometryEngine(Enum):
    # Available geometry engines
    ARCPY = "arcpy"
    GDAL = "gdal"
    SHAPELY = "shapely"
    SHAPEFILE = "shapefile"
    FIONA = "fiona"


class GeometryEngineManager:
    """
    Manages detection and selection of a spatial geometry engine.

    Setting "ARCGIS_GEOMETRY_ENGINE" environment variable to "arcpy", "gdal", "fiona", or "shapely" will prioritize your preferred engine.
    """

    def __init__(self):
        """Initialize and select an engine."""
        self._detect_available_engines()
        self.engine = self._select_engine()  # Store the selected engine

    def _detect_available_engines(self):
        """
        Check for installed spatial libraries.
        If we can import, we assume it is available.
        """
        self.available_engines = {
            GeometryEngine.ARCPY: self._is_installed("arcpy"),
            GeometryEngine.SHAPEFILE: self._is_installed("shapefile"),
            GeometryEngine.SHAPELY: self._is_installed("shapely"),
            GeometryEngine.GDAL: self._is_installed("osgeo"),
            GeometryEngine.FIONA: self._is_installed("fiona"),
        }

    def _is_installed(self, module_name):
        """Check if a module is installed."""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False

    def _select_engine(self):
        """Select the best available engine, prioritizing user preference."""
        # Get the preferred engine from the environment variable ARCGIS_GEOMETRY_ENGINE
        preferred_engine = os.getenv("ARCGIS_GEOMETRY_ENGINE", "").lower()

        # Check if the preferred engine is in the list of available engines
        if preferred_engine in GeometryEngine._value2member_map_:
            selected_engine = GeometryEngine(preferred_engine)
            # If the preferred engine is available, return it
            if self.available_engines.get(selected_engine, False):
                return selected_engine  # Use user-specified engine if available

        # Default priority order: arcpy > gdal > shapefile > fiona
        # Iterate through the default engines and select the first available one
        for engine in [
            GeometryEngine.ARCPY,
            GeometryEngine.GDAL,
            GeometryEngine.SHAPEFILE,
            GeometryEngine.SHAPELY,
            GeometryEngine.FIONA,
        ]:
            if self.available_engines[engine]:
                return engine  # Return the first available engine from the default priority order


# Create a global instance so all modules can import it
ge = GeometryEngineManager()
SELECTED_ENGINE = ge.engine
HAS_ARCPY = ge.available_engines[GeometryEngine.ARCPY]
HAS_PYSHP = ge.available_engines[GeometryEngine.SHAPEFILE]
HAS_SHAPELY = ge.available_engines[GeometryEngine.SHAPELY]
HAS_GDAL = ge.available_engines[GeometryEngine.GDAL]
HAS_FIONA = ge.available_engines[GeometryEngine.FIONA]
