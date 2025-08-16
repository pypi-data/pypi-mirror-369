""" GIS MCP Server - Main entry point

This module implements an MCP server that connects LLMs to GIS operations using
Shapely and PyProj libraries, enabling AI assistants to perform geospatial operations
and transformations.
"""

import json
import logging
import os
import sys
import argparse
import tempfile
from typing import Any, Dict, List, Optional, Union
import geopandas as gpd
import pandas as pd
import libpysal
import esda
import numpy as np
from libpysal import weights
from libpysal.weights import W, Queen, Rook, DistanceBand, KNN
from libpysal import io as wio
from spreg import OLS

import warnings
warnings.filterwarnings('ignore')  # Suppress warnings for cleaner output

# MCP imports using the new SDK patterns
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("gis-mcp")

# Create FastMCP instance
mcp = FastMCP("GIS MCP")

# Resource handlers
@mcp.resource("gis://operations/basic")
def get_basic_operations() -> Dict[str, List[str]]:
    """List available basic geometric operations."""
    return {
        "operations": [
            "buffer",
            "intersection",
            "union",
            "difference",
            "symmetric_difference"
        ]
    }

@mcp.resource("gis://operations/geometric")
def get_geometric_properties() -> Dict[str, List[str]]:
    """List available geometric property operations."""
    return {
        "operations": [
            "convex_hull",
            "envelope",
            "minimum_rotated_rectangle",
            "get_centroid",
            "get_bounds",
            "get_coordinates",
            "get_geometry_type"
        ]
    }

@mcp.resource("gis://operations/transformations")
def get_transformations() -> Dict[str, List[str]]:
    """List available geometric transformations."""
    return {
        "operations": [
            "rotate_geometry",
            "scale_geometry",
            "translate_geometry"
        ]
    }

@mcp.resource("gis://operations/advanced")
def get_advanced_operations() -> Dict[str, List[str]]:
    """List available advanced operations."""
    return {
        "operations": [
            "triangulate_geometry",
            "voronoi",
            "unary_union_geometries"
        ]
    }

@mcp.resource("gis://operations/measurements")
def get_measurements() -> Dict[str, List[str]]:
    """List available measurement operations."""
    return {
        "operations": [
            "get_length",
            "get_area"
        ]
    }

@mcp.resource("gis://operations/validation")
def get_validation_operations() -> Dict[str, List[str]]:
    """List available validation operations."""
    return {
        "operations": [
            "is_valid",
            "make_valid",
            "simplify"
        ]
    }

@mcp.resource("gis://crs/transformations")
def get_crs_transformations() -> Dict[str, List[str]]:
    """List available CRS transformation operations."""
    return {
        "operations": [
            "transform_coordinates",
            "project_geometry"
        ]
    }

@mcp.resource("gis://crs/info")
def get_crs_info_operations() -> Dict[str, List[str]]:
    """List available CRS information operations."""
    return {
        "operations": [
            "get_crs_info",
            "get_available_crs",
            "get_utm_zone",
            "get_utm_crs",
            "get_geocentric_crs"
        ]
    }

@mcp.resource("gis://crs/geodetic")
def get_geodetic_operations() -> Dict[str, List[str]]:
    """List available geodetic calculation operations."""
    return {
        "operations": [
            "get_geod_info",
            "calculate_geodetic_distance",
            "calculate_geodetic_point",
            "calculate_geodetic_area"
        ]
    }

@mcp.resource("gis://geopandas/io")
def get_geopandas_io() -> Dict[str, List[str]]:
    """List available GeoPandas I/O operations."""
    return {
        "operations": [
            "read_file_gpd",
            "to_file_gpd"
        ]
    }

@mcp.resource("gis://geopandas/joins")
def get_geopandas_joins() -> Dict[str, List[str]]:
    """List available GeoPandas join operations."""
    return {
        "operations": [
            "append_gpd",
            "merge_gpd"]}

@mcp.resource("gis://operation/rasterio")
def get_rasterio_operations() -> Dict[str, List[str]]:
    """List available rasterio operations."""
    return {
        "operations": [
            "metadata_raster",
            "get_raster_crs",
            "clip_raster_with_shapefile",
            "resample_raster",
            "reproject_raster",
            "weighted_band_sum",
            "concat_bands",
            "raster_algebra",
            "compute_ndvi",
            "raster_histogram",
            "tile_raster",
            "raster_band_statistics",
            "extract_band",
        ]
    }

@mcp.resource("gis://operations/esda")
def get_spatial_operations() -> Dict[str, List[str]]:
    """List available spatial analysis operations. This is for esda library. They are using pysal library."""
    return {
        "operations": [
            "getis_ord_g",
            "morans_i",
            "gearys_c",
            "gamma_statistic",
            "moran_local",
            "getis_ord_g_local",
            "join_counts",
            "join_counts_local",
            "adbscan"
        ]
    }

# Tool implementations
@mcp.tool()
def buffer(geometry: str, distance: float, resolution: int = 16, 
        join_style: int = 1, mitre_limit: float = 5.0, 
        single_sided: bool = False) -> Dict[str, Any]:
    """Create a buffer around a geometry."""
    try:
        from shapely import wkt
        geom = wkt.loads(geometry)
        buffered = geom.buffer(
            distance=distance,
            resolution=resolution,
            join_style=join_style,
            mitre_limit=mitre_limit,
            single_sided=single_sided
        )
        return {
            "status": "success",
            "geometry": buffered.wkt,
            "message": "Buffer created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating buffer: {str(e)}")
        raise ValueError(f"Failed to create buffer: {str(e)}")

@mcp.tool()
def intersection(geometry1: str, geometry2: str) -> Dict[str, Any]:
    """Find intersection of two geometries."""
    try:
        from shapely import wkt
        geom1 = wkt.loads(geometry1)
        geom2 = wkt.loads(geometry2)
        result = geom1.intersection(geom2)
        return {
            "status": "success",
            "geometry": result.wkt,
            "message": "Intersection created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating intersection: {str(e)}")
        raise ValueError(f"Failed to create intersection: {str(e)}")

@mcp.tool()
def union(geometry1: str, geometry2: str) -> Dict[str, Any]:
    """Combine two geometries."""
    try:
        from shapely import wkt
        geom1 = wkt.loads(geometry1)
        geom2 = wkt.loads(geometry2)
        result = geom1.union(geom2)
        return {
            "status": "success",
            "geometry": result.wkt,
            "message": "Union created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating union: {str(e)}")
        raise ValueError(f"Failed to create union: {str(e)}")

@mcp.tool()
def difference(geometry1: str, geometry2: str) -> Dict[str, Any]:
    """Find difference between geometries."""
    try:
        from shapely import wkt
        geom1 = wkt.loads(geometry1)
        geom2 = wkt.loads(geometry2)
        result = geom1.difference(geom2)
        return {
            "status": "success",
            "geometry": result.wkt,
            "message": "Difference created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating difference: {str(e)}")
        raise ValueError(f"Failed to create difference: {str(e)}")

@mcp.tool()
def symmetric_difference(geometry1: str, geometry2: str) -> Dict[str, Any]:
    """Find symmetric difference between geometries."""
    try:
        from shapely import wkt
        geom1 = wkt.loads(geometry1)
        geom2 = wkt.loads(geometry2)
        result = geom1.symmetric_difference(geom2)
        return {
            "status": "success",
            "geometry": result.wkt,
            "message": "Symmetric difference created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating symmetric difference: {str(e)}")
        raise ValueError(f"Failed to create symmetric difference: {str(e)}")

@mcp.tool()
def convex_hull(geometry: str) -> Dict[str, Any]:
    """Calculate convex hull of a geometry."""
    try:
        from shapely import wkt
        geom = wkt.loads(geometry)
        result = geom.convex_hull
        return {
            "status": "success",
            "geometry": result.wkt,
            "message": "Convex hull created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating convex hull: {str(e)}")
        raise ValueError(f"Failed to create convex hull: {str(e)}")

@mcp.tool()
def envelope(geometry: str) -> Dict[str, Any]:
    """Get bounding box of a geometry."""
    try:
        from shapely import wkt
        geom = wkt.loads(geometry)
        result = geom.envelope
        return {
            "status": "success",
            "geometry": result.wkt,
            "message": "Envelope created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating envelope: {str(e)}")
        raise ValueError(f"Failed to create envelope: {str(e)}")

@mcp.tool()
def minimum_rotated_rectangle(geometry: str) -> Dict[str, Any]:
    """Get minimum rotated rectangle of a geometry."""
    try:
        from shapely import wkt
        geom = wkt.loads(geometry)
        result = geom.minimum_rotated_rectangle
        return {
            "status": "success",
            "geometry": result.wkt,
            "message": "Minimum rotated rectangle created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating minimum rotated rectangle: {str(e)}")
        raise ValueError(f"Failed to create minimum rotated rectangle: {str(e)}")

@mcp.tool()
def rotate_geometry(geometry: str, angle: float, origin: str = "center", 
                use_radians: bool = False) -> Dict[str, Any]:
    """Rotate a geometry."""
    try:
        from shapely import wkt
        from shapely.affinity import rotate
        geom = wkt.loads(geometry)
        result = rotate(geom, angle=angle, origin=origin, use_radians=use_radians)
        return {
            "status": "success",
            "geometry": result.wkt,
            "message": "Geometry rotated successfully"
        }
    except Exception as e:
        logger.error(f"Error rotating geometry: {str(e)}")
        raise ValueError(f"Failed to rotate geometry: {str(e)}")

@mcp.tool()
def scale_geometry(geometry: str, xfact: float, yfact: float, 
                origin: str = "center") -> Dict[str, Any]:
    """Scale a geometry."""
    try:
        from shapely import wkt
        from shapely.affinity import scale
        geom = wkt.loads(geometry)
        result = scale(geom, xfact=xfact, yfact=yfact, origin=origin)
        return {
            "status": "success",
            "geometry": result.wkt,
            "message": "Geometry scaled successfully"
        }
    except Exception as e:
        logger.error(f"Error scaling geometry: {str(e)}")
        raise ValueError(f"Failed to scale geometry: {str(e)}")

@mcp.tool()
def translate_geometry(geometry: str, xoff: float, yoff: float, 
                    zoff: float = 0.0) -> Dict[str, Any]:
    """Translate a geometry."""
    try:
        from shapely import wkt
        from shapely.affinity import translate
        geom = wkt.loads(geometry)
        result = translate(geom, xoff=xoff, yoff=yoff, zoff=zoff)
        return {
            "status": "success",
            "geometry": result.wkt,
            "message": "Geometry translated successfully"
        }
    except Exception as e:
        logger.error(f"Error translating geometry: {str(e)}")
        raise ValueError(f"Failed to translate geometry: {str(e)}")

@mcp.tool()
def triangulate_geometry(geometry: str) -> Dict[str, Any]:
    """Create a triangulation of a geometry."""
    try:
        from shapely import wkt
        from shapely.ops import triangulate
        geom = wkt.loads(geometry)
        triangles = triangulate(geom)
        return {
            "status": "success",
            "geometries": [tri.wkt for tri in triangles],
            "message": "Triangulation created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating triangulation: {str(e)}")
        raise ValueError(f"Failed to create triangulation: {str(e)}")

@mcp.tool()
def voronoi(geometry: str) -> Dict[str, Any]:
    """Create a Voronoi diagram from points."""
    try:
        from shapely import wkt
        from shapely.ops import voronoi_diagram
        geom = wkt.loads(geometry)
        result = voronoi_diagram(geom)
        return {
            "status": "success",
            "geometry": result.wkt,
            "message": "Voronoi diagram created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating Voronoi diagram: {str(e)}")
        raise ValueError(f"Failed to create Voronoi diagram: {str(e)}")

@mcp.tool()
def unary_union_geometries(geometries: List[str]) -> Dict[str, Any]:
    """Create a union of multiple geometries."""
    try:
        from shapely import wkt
        from shapely.ops import unary_union
        geoms = [wkt.loads(g) for g in geometries]
        result = unary_union(geoms)
        return {
            "status": "success",
            "geometry": result.wkt,
            "message": "Union created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating union: {str(e)}")
        raise ValueError(f"Failed to create union: {str(e)}")

@mcp.tool()
def get_centroid(geometry: str) -> Dict[str, Any]:
    """Get the centroid of a geometry."""
    try:
        from shapely import wkt
        geom = wkt.loads(geometry)
        result = geom.centroid
        return {
            "status": "success",
            "geometry": result.wkt,
            "message": "Centroid calculated successfully"
        }
    except Exception as e:
        logger.error(f"Error calculating centroid: {str(e)}")
        raise ValueError(f"Failed to calculate centroid: {str(e)}")

@mcp.tool()
def get_length(geometry: str) -> Dict[str, Any]:
    """Get the length of a geometry."""
    try:
        from shapely import wkt
        geom = wkt.loads(geometry)
        return {
            "status": "success",
            "length": float(geom.length),
            "message": "Length calculated successfully"
        }
    except Exception as e:
        logger.error(f"Error calculating length: {str(e)}")
        raise ValueError(f"Failed to calculate length: {str(e)}")

@mcp.tool()
def get_area(geometry: str) -> Dict[str, Any]:
    """Get the area of a geometry."""
    try:
        from shapely import wkt
        geom = wkt.loads(geometry)
        return {
            "status": "success",
            "area": float(geom.area),
            "message": "Area calculated successfully"
        }
    except Exception as e:
        logger.error(f"Error calculating area: {str(e)}")
        raise ValueError(f"Failed to calculate area: {str(e)}")

@mcp.tool()
def get_bounds(geometry: str) -> Dict[str, Any]:
    """Get the bounds of a geometry."""
    try:
        from shapely import wkt
        geom = wkt.loads(geometry)
        return {
            "status": "success",
            "bounds": list(geom.bounds),
            "message": "Bounds calculated successfully"
        }
    except Exception as e:
        logger.error(f"Error calculating bounds: {str(e)}")
        raise ValueError(f"Failed to calculate bounds: {str(e)}")

@mcp.tool()
def get_coordinates(geometry: str) -> Dict[str, Any]:
    """Get the coordinates of a geometry."""
    try:
        from shapely import wkt
        geom = wkt.loads(geometry)
        return {
            "status": "success",
            "coordinates": [list(coord) for coord in geom.coords],
            "message": "Coordinates retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting coordinates: {str(e)}")
        raise ValueError(f"Failed to get coordinates: {str(e)}")

@mcp.tool()
def get_geometry_type(geometry: str) -> Dict[str, Any]:
    """Get the type of a geometry."""
    try:
        from shapely import wkt
        geom = wkt.loads(geometry)
        return {
            "status": "success",
            "type": geom.geom_type,
            "message": "Geometry type retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting geometry type: {str(e)}")
        raise ValueError(f"Failed to get geometry type: {str(e)}")

@mcp.tool()
def is_valid(geometry: str) -> Dict[str, Any]:
    """Check if a geometry is valid."""
    try:
        from shapely import wkt
        geom = wkt.loads(geometry)
        return {
            "status": "success",
            "is_valid": bool(geom.is_valid),
            "message": "Geometry validation completed successfully"
        }
    except Exception as e:
        logger.error(f"Error validating geometry: {str(e)}")
        raise ValueError(f"Failed to validate geometry: {str(e)}")

@mcp.tool()
def make_valid(geometry: str) -> Dict[str, Any]:
    """Make a geometry valid."""
    try:
        from shapely import wkt
        geom = wkt.loads(geometry)
        result = geom.make_valid()
        return {
            "status": "success",
            "geometry": result.wkt,
            "message": "Geometry made valid successfully"
        }
    except Exception as e:
        logger.error(f"Error making geometry valid: {str(e)}")
        raise ValueError(f"Failed to make geometry valid: {str(e)}")

@mcp.tool()
def simplify(geometry: str, tolerance: float, 
            preserve_topology: bool = True) -> Dict[str, Any]:
    """Simplify a geometry."""
    try:
        from shapely import wkt
        geom = wkt.loads(geometry)
        result = geom.simplify(tolerance=tolerance, preserve_topology=preserve_topology)
        return {
            "status": "success",
            "geometry": result.wkt,
            "message": "Geometry simplified successfully"
        }
    except Exception as e:
        logger.error(f"Error simplifying geometry: {str(e)}")
        raise ValueError(f"Failed to simplify geometry: {str(e)}")

@mcp.tool()
def transform_coordinates(coordinates: List[float], source_crs: str, 
                        target_crs: str) -> Dict[str, Any]:
    """Transform coordinates between CRS."""
    try:
        from pyproj import Transformer
        transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
        x, y = coordinates
        x_transformed, y_transformed = transformer.transform(x, y)
        return {
            "status": "success",
            "coordinates": [x_transformed, y_transformed],
            "source_crs": source_crs,
            "target_crs": target_crs,
            "message": "Coordinates transformed successfully"
        }
    except Exception as e:
        logger.error(f"Error transforming coordinates: {str(e)}")
        raise ValueError(f"Failed to transform coordinates: {str(e)}")

@mcp.tool()
def project_geometry(geometry: str, source_crs: str, 
                    target_crs: str) -> Dict[str, Any]:
    """Project a geometry between CRS."""
    try:
        from shapely import wkt
        from shapely.ops import transform
        from pyproj import Transformer
        geom = wkt.loads(geometry)
        transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
        projected = transform(transformer.transform, geom)
        return {
            "status": "success",
            "geometry": projected.wkt,
            "source_crs": source_crs,
            "target_crs": target_crs,
            "message": "Geometry projected successfully"
        }
    except Exception as e:
        logger.error(f"Error projecting geometry: {str(e)}")
        raise ValueError(f"Failed to project geometry: {str(e)}")

@mcp.tool()
def get_crs_info(crs: str) -> Dict[str, Any]:
    """Get information about a CRS."""
    try:
        import pyproj
        crs_obj = pyproj.CRS(crs)
        return {
            "status": "success",
            "name": crs_obj.name,
            "type": crs_obj.type_name,
            "axis_info": [axis.direction for axis in crs_obj.axis_info],
            "is_geographic": crs_obj.is_geographic,
            "is_projected": crs_obj.is_projected,
            "datum": str(crs_obj.datum),
            "ellipsoid": str(crs_obj.ellipsoid),
            "prime_meridian": str(crs_obj.prime_meridian),
            "area_of_use": str(crs_obj.area_of_use) if crs_obj.area_of_use else None,
            "message": "CRS information retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting CRS info: {str(e)}")
        raise ValueError(f"Failed to get CRS info: {str(e)}")

@mcp.tool()
def get_available_crs() -> Dict[str, Any]:
    """Get list of available CRS."""
    try:
        import pyproj
        crs_list = []
        for crs in pyproj.database.get_crs_list():
            try:
                crs_info = get_crs_info({"crs": crs})
                crs_list.append({
                    "auth_name": crs.auth_name,
                    "code": crs.code,
                    "name": crs_info["name"],
                    "type": crs_info["type"]
                })
            except:
                continue
        return {
            "status": "success",
            "crs_list": crs_list,
            "message": "Available CRS list retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting available CRS: {str(e)}")
        raise ValueError(f"Failed to get available CRS: {str(e)}")

@mcp.tool()
def get_geod_info(ellps: str = "WGS84", a: Optional[float] = None,
                b: Optional[float] = None, f: Optional[float] = None) -> Dict[str, Any]:
    """Get information about a geodetic calculation."""
    try:
        import pyproj
        geod = pyproj.Geod(ellps=ellps, a=a, b=b, f=f)
        return {
            "status": "success",
            "ellps": geod.ellps,
            "a": geod.a,
            "b": geod.b,
            "f": geod.f,
            "es": geod.es,
            "e": geod.e,
            "message": "Geodetic information retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting geodetic info: {str(e)}")
        raise ValueError(f"Failed to get geodetic info: {str(e)}")

@mcp.tool()
def calculate_geodetic_distance(point1: List[float], point2: List[float], 
                            ellps: str = "WGS84") -> Dict[str, Any]:
    """Calculate geodetic distance between points."""
    try:
        import pyproj
        geod = pyproj.Geod(ellps=ellps)
        lon1, lat1 = point1
        lon2, lat2 = point2
        forward_azimuth, back_azimuth, distance = geod.inv(lon1, lat1, lon2, lat2)
        return {
            "status": "success",
            "distance": distance,
            "forward_azimuth": forward_azimuth,
            "back_azimuth": back_azimuth,
            "ellps": ellps,
            "message": "Geodetic distance calculated successfully"
        }
    except Exception as e:
        logger.error(f"Error calculating geodetic distance: {str(e)}")
        raise ValueError(f"Failed to calculate geodetic distance: {str(e)}")

@mcp.tool()
def calculate_geodetic_point(start_point: List[float], azimuth: float, 
                        distance: float, ellps: str = "WGS84") -> Dict[str, Any]:
    """Calculate point at given distance and azimuth."""
    try:
        import pyproj
        geod = pyproj.Geod(ellps=ellps)
        lon, lat = start_point
        lon2, lat2, back_azimuth = geod.fwd(lon, lat, azimuth, distance)
        return {
            "status": "success",
            "point": [lon2, lat2],
            "back_azimuth": back_azimuth,
            "ellps": ellps,
            "message": "Geodetic point calculated successfully"
        }
    except Exception as e:
        logger.error(f"Error calculating geodetic point: {str(e)}")
        raise ValueError(f"Failed to calculate geodetic point: {str(e)}")

@mcp.tool()
def calculate_geodetic_area(geometry: str, ellps: str = "WGS84") -> Dict[str, Any]:
    """Calculate area of a polygon using geodetic calculations."""
    try:
        import pyproj
        from shapely import wkt
        geod = pyproj.Geod(ellps=ellps)
        polygon = wkt.loads(geometry)
        area = abs(geod.geometry_area_perimeter(polygon)[0])
        return {
            "status": "success",
            "area": float(area),
            "ellps": ellps,
            "message": "Geodetic area calculated successfully"
        }
    except Exception as e:
        logger.error(f"Error calculating geodetic area: {str(e)}")
        raise ValueError(f"Failed to calculate geodetic area: {str(e)}")

@mcp.tool()
def get_utm_zone(coordinates: List[float]) -> Dict[str, Any]:
    """Get UTM zone for given coordinates."""
    try:
        import pyproj
        lon, lat = coordinates
        zone = pyproj.database.query_utm_crs_info(
            datum_name="WGS84",
            area_of_interest=pyproj.aoi.AreaOfInterest(
                west_lon_degree=lon,
                south_lat_degree=lat,
                east_lon_degree=lon,
                north_lat_degree=lat
            )
        )[0].to_authority()[1]
        return {
            "status": "success",
            "zone": zone,
            "message": "UTM zone retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting UTM zone: {str(e)}")
        raise ValueError(f"Failed to get UTM zone: {str(e)}")

@mcp.tool()
def get_utm_crs(coordinates: List[float]) -> Dict[str, Any]:
    """Get UTM CRS for given coordinates."""
    try:
        import pyproj
        lon, lat = coordinates
        crs = pyproj.database.query_utm_crs_info(
            datum_name="WGS84",
            area_of_interest=pyproj.aoi.AreaOfInterest(
                west_lon_degree=lon,
                south_lat_degree=lat,
                east_lon_degree=lon,
                north_lat_degree=lat
            )
        )[0].to_wkt()
        return {
            "status": "success",
            "crs": crs,
            "message": "UTM CRS retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting UTM CRS: {str(e)}")
        raise ValueError(f"Failed to get UTM CRS: {str(e)}")

@mcp.tool()
def get_geocentric_crs(coordinates: List[float]) -> Dict[str, Any]:
    """Get geocentric CRS for given coordinates."""
    try:
        import pyproj
        lon, lat = coordinates
        crs = pyproj.database.query_geocentric_crs_info(
            datum_name="WGS84",
            area_of_interest=pyproj.aoi.AreaOfInterest(
                west_lon_degree=lon,
                south_lat_degree=lat,
                east_lon_degree=lon,
                north_lat_degree=lat
            )
        )[0].to_wkt()
        return {
            "status": "success",
            "crs": crs,
            "message": "Geocentric CRS retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting geocentric CRS: {str(e)}")
        raise ValueError(f"Failed to get geocentric CRS: {str(e)}")


@mcp.tool()
def read_file_gpd(file_path: str) -> Dict[str, Any]:
    """Reads a geospatial file and returns stats and a data preview."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        gdf = gpd.read_file(file_path)
        preview = gdf.head(5).to_dict(orient="records")
        
        return {
            "status": "success",
            "columns": list(gdf.columns),
            "column_types": gdf.dtypes.astype(str).to_dict(),
            "num_rows": len(gdf),
            "num_columns": gdf.shape[1],
            "crs": str(gdf.crs),
            "bounds": gdf.total_bounds.tolist(),  # [minx, miny, maxx, maxy]
            "preview": preview,
            "message": f"File loaded successfully with {len(gdf)} rows and {gdf.shape[1]} columns"
        }

    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to read file: {str(e)}"
        }


@mcp.tool()
def append_gpd(shapefile1_path: str, shapefile2_path: str, output_path: str) -> Dict[str, Any]:
    """ Reads two shapefiles directly, concatenates them vertically."""
    try:
        # Configure a basic logger for demonstration
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

        # Step 1: Read the two shapefiles into GeoDataFrames.
        logger.info(f"Reading {shapefile1_path}...")
        gdf1 = gpd.read_file(shapefile1_path)
        
        logger.info(f"Reading {shapefile2_path}...")
        gdf2 = gpd.read_file(shapefile2_path)

        # Step 2: Ensure the Coordinate Reference Systems (CRS) match.
        if gdf1.crs != gdf2.crs:
            logger.warning(
                f"CRS mismatch: GDF1 has '{gdf1.crs}' and GDF2 has '{gdf2.crs}'. "
                "Reprojecting GDF2."
            )
            gdf2 = gdf2.to_crs(gdf1.crs)

        # Step 3: Concatenate the two GeoDataFrames.
        combined_gdf = pd.concat([gdf1, gdf2], ignore_index=True)

        # Step 4: Save the combined GeoDataFrame to a new shapefile.
        logger.info(f"Saving combined shapefile to {output_path}...")
        combined_gdf.to_file(output_path, driver='ESRI Shapefile')

        return {
            "status": "success",
            "message": f"Shapefiles concatenated successfully into '{output_path}'.",
            "info": {
                "output_path": output_path,
                "num_features": len(combined_gdf),
                "crs": str(combined_gdf.crs),
                "columns": list(combined_gdf.columns)
            }
        }
    
    except Exception as e:
        logger.error(f"Error processing shapefiles: {str(e)}")
        raise ValueError(f"Failed to process shapefiles: {str(e)}")

@mcp.tool()
def merge_gpd(shapefile1_path: str, shapefile2_path: str, output_path: str) -> Dict[str, Any]:
    """ 
    Merges two shapefiles based on common attribute columns,
    This function performs a database-style join, not a spatial join.
    Args:
        left_shapefile_path: Path to the left shapefile. The geometry from this file is preserved.
        right_shapefile_path: Path to the right shapefile to merge.
        output_path: Path to save the merged output shapefile.
        how: Type of merge. One of 'left', 'right', 'outer', 'inner'. Defaults to 'inner'.
        on: Column name to join on. Must be found in both shapefiles.
        left_on: Column name to join on in the left shapefile.
        right_on: Column name to join on in the right shapefile.
        suffixes: Suffix to apply to overlapping column names.
    """
    try :
        # Step 1: Read the two shapefiles directly into GeoDataFrames.
        logger.info(f"Reading left shapefile: {left_shapefile_path}...")
        left_gdf = gpd.read_file(left_shapefile_path)
        
        logger.info(f"Reading right shapefile: {right_shapefile_path}...")
        # For an attribute join, we only need the attribute data from the right file.
        # We can drop its geometry column to make the merge cleaner and more memory-efficient.
        right_df = pd.DataFrame(gpd.read_file(right_shapefile_path).drop(columns='geometry'))

         # Step 2: Perform the merge operation using the optimized geopandas.merge.
        # This function correctly handles the geometry of the left GeoDataFrame.
        logger.info(f"Performing '{how}' merge...")
        merged_gdf = gpd.merge(
            left_gdf,
            right_df,
            how=how,
            on=on,
            left_on=left_on,
            right_on=right_on,
            suffixes=suffixes
        )

        if merged_gdf.empty:
            logger.warning("The merge result is empty. No matching records were found.")

        # Step 3: Save the merged GeoDataFrame to a new shapefile.
        logger.info(f"Saving merged shapefile to {output_path}...")
        merged_gdf.to_file(output_path, driver='ESRI Shapefile')

        return {
            "status": "success",
            "message": f"Shapefiles merged successfully into '{output_path}'.",
            "info": {
                "output_path": output_path,
                "merge_type": how,
                "num_features": len(merged_gdf),
                "crs": str(merged_gdf.crs),
                "columns": list(merged_gdf.columns)
            }
        }
    except Exception as e:
        logger.error(f"Error merging shapefiles: {str(e)}")
        raise ValueError(f"Failed to merge shapefiles: {str(e)}")



@mcp.tool()
def metadata_raster(path_or_url: str) -> Dict[str, Any]:
    """
    Open a raster dataset in read-only mode and return metadata.
    
    This tool supports two modes based on the provided string:
    1. A local filesystem path (e.g., "D:\\Data\\my_raster.tif").
    2. An HTTPS URL (e.g., "https://example.com/my_raster.tif").
    
    The input must be a single string that is either a valid file path
    on the local machine or a valid HTTPS URL pointing to a raster.
    """
    try:
        # Import numpy first to ensure NumPy's C-API is initialized
        import numpy as np
        import rasterio

        # Remove any backticks (`) if the client wrapped the path_or_url in them
        cleaned = path_or_url.replace("`", "")

        # Determine if the string is an HTTPS URL or a local file path
        if cleaned.lower().startswith("https://"):
            # For HTTPS URLs, let Rasterio/GDAL handle remote access directly
            dataset = rasterio.open(cleaned)
        else:
            # Treat as local filesystem path
            local_path = os.path.expanduser(cleaned)

            # Verify that the file exists on disk
            if not os.path.isfile(local_path):
                raise FileNotFoundError(f"Raster file not found at '{local_path}'.")

            # Open the local file in read-only mode
            dataset = rasterio.open(local_path)

        # Build a mapping from band index to its data type (dtype)
        band_dtypes = {i: dtype for i, dtype in zip(dataset.indexes, dataset.dtypes)}

        # Collect core metadata fields in simple Python types
        meta: Dict[str, Any] = {
            "name": dataset.name,                                       # Full URI or filesystem path
            "mode": dataset.mode,                                       # Mode should be 'r' for read                                 
            "driver": dataset.driver,                                   # GDAL driver, e.g. "GTiff"
            "width": dataset.width,                                     # Number of columns
            "height": dataset.height,                                   # Number of rows
            "count": dataset.count,                                     # Number of bands
            "bounds": dataset.bounds,                                   # Show bounding box
            "band_dtypes": band_dtypes,                                 # { band_index: dtype_string }
            "no_data": dataset.nodatavals,                              # Number of NoData values in each band
            "crs": dataset.crs.to_string() if dataset.crs else None,    # CRS as EPSG string or None
            "transform": list(dataset.transform),                       # Affine transform coefficients (6 floats)
        }

        # Return a success status along with metadata
        return {
            "status": "success",
            "metadata": meta,
            "message": f"Raster dataset opened successfully from '{cleaned}'."
        }

    except Exception as e:
        # Log the error for debugging purposes, then raise ValueError so MCP can relay it
        logger.error(f"Error opening raster '{path_or_url}': {str(e)}")
        raise ValueError(f"Failed to open raster '{path_or_url}': {str(e)}")

@mcp.tool()
def get_raster_crs(path_or_url: str) -> Dict[str, Any]:
    """
    Retrieve the Coordinate Reference System (CRS) of a raster dataset.
    
    Opens the raster (local path or HTTPS URL), reads its DatasetReader.crs
    attribute as a PROJ.4-style dict, and also returns the WKT representation.
    """
    try:
        import numpy as np
        import rasterio

        # Strip backticks if the client wrapped the input in them
        cleaned = path_or_url.replace("`", "")

        # Open remote or local dataset
        if cleaned.lower().startswith("https://"):
            src = rasterio.open(cleaned)
        else:
            local_path = os.path.expanduser(cleaned)
            if not os.path.isfile(local_path):
                raise FileNotFoundError(f"Raster file not found at '{local_path}'.")
            src = rasterio.open(local_path)

        # Access the CRS object on the opened dataset
        crs_obj = src.crs
        src.close()

        if crs_obj is None:
            raise ValueError("No CRS defined for this dataset.")

        # Convert CRS to PROJ.4‐style dict and WKT string
        proj4_dict = crs_obj.to_dict()    # e.g., {'init': 'epsg:32618'}
        wkt_str    = crs_obj.to_wkt()     # full WKT representation

        return {
            "status":      "success",
            "proj4":       proj4_dict,
            "wkt":         wkt_str,
            "message":     "CRS retrieved successfully"
        }

    except Exception as e:
        # Log and re-raise as ValueError for MCP error propagation
        logger.error(f"Error retrieving CRS for '{path_or_url}': {e}")
        raise ValueError(f"Failed to retrieve CRS: {e}")

@mcp.tool()
def clip_raster_with_shapefile(
    raster_path_or_url: str,
    shapefile_path: str,
    destination: str
) -> Dict[str, Any]:
    """
    Clip a raster dataset using polygons from a shapefile and write the result.
    Converts the shapefile's CRS to match the raster's CRS if they are different.
    
    Parameters:
    - raster_path_or_url: local path or HTTPS URL of the source raster.
    - shapefile_path:     local filesystem path to a .shp file containing polygons.
    - destination:        local path where the masked raster will be written.
    """
    try:
        import numpy as np
        import rasterio
        import rasterio.mask
        from rasterio.warp import transform_geom
        import pyproj
        import fiona

        # Clean paths
        raster_clean = raster_path_or_url.replace("`", "")
        shp_clean = shapefile_path.replace("`", "")
        dst_clean = destination.replace("`", "")

        # Verify shapefile exists
        shp_path = os.path.expanduser(shp_clean)
        if not os.path.isfile(shp_path):
            raise FileNotFoundError(f"Shapefile not found at '{shp_path}'.")

        # Open the raster
        if raster_clean.lower().startswith("https://"):
            src = rasterio.open(raster_clean)
        else:
            src_path = os.path.expanduser(raster_clean)
            if not os.path.isfile(src_path):
                raise FileNotFoundError(f"Raster not found at '{src_path}'.")
            src = rasterio.open(src_path)

        raster_crs = src.crs  # Get raster CRS

        # Read geometries from shapefile and check CRS
        with fiona.open(shp_path, "r") as shp:
            shapefile_crs = pyproj.CRS(shp.crs)  # Get shapefile CRS
            shapes: List[Dict[str, Any]] = [feat["geometry"] for feat in shp]

            # Convert geometries to raster CRS if necessary
            if shapefile_crs != raster_crs:
                shapes = [transform_geom(str(shapefile_crs), str(raster_crs), shape) for shape in shapes]

        # Apply mask: crop to shapes and set outside pixels to zero
        out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
        out_meta = src.meta.copy()
        src.close()

        # Update metadata for the masked output
        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })

        # Ensure destination directory exists
        dst_path = os.path.expanduser(dst_clean)
        os.makedirs(os.path.dirname(dst_path) or ".", exist_ok=True)

        # Write the masked raster
        with rasterio.open(dst_path, "w", **out_meta) as dst:
            dst.write(out_image)

        return {
            "status": "success",
            "destination": dst_path,
            "message": f"Raster masked and saved to '{dst_path}'."
        }

    except Exception as e:
        print(f"Error: {e}")
        raise ValueError(f"Failed to mask raster: {e}")

@mcp.tool()
def resample_raster(
    source: str,
    scale_factor: float,
    resampling: str,
    destination: str
) -> Dict[str, Any]:
    """
    Resample a raster dataset by a scale factor and save the result.
    
    Parameters:
    - source:       local path or HTTPS URL of the source raster.
    - scale_factor: multiplicative factor for width/height 
                    (e.g., 0.5 to halve resolution, 2.0 to double).
    - resampling:   resampling method name: "nearest", "bilinear", "cubic", etc.
    - destination:  local filesystem path for the resampled raster.
    """
    try:
        import numpy as np
        import rasterio
        from rasterio.enums import Resampling
        from rasterio.transform import Affine

        # Strip backticks if present
        src_clean = source.replace("`", "")
        dst_clean = destination.replace("`", "")

        # Open source (remote or local)
        if src_clean.lower().startswith("https://"):
            src = rasterio.open(src_clean)
        else:
            src_path = os.path.expanduser(src_clean)
            if not os.path.isfile(src_path):
                raise FileNotFoundError(f"Source raster not found at '{src_path}'.")
            src = rasterio.open(src_path)

        # Validate scale factor
        if scale_factor <= 0:
            raise ValueError("Scale factor must be positive.")

        # Compute new dimensions
        new_width  = int(src.width  * scale_factor)
        new_height = int(src.height * scale_factor)

        if new_width == 0 or new_height == 0:
            raise ValueError("Resulting raster dimensions are zero. Check scale_factor.")

        # Map resampling method string to Resampling enum
        resampling_enum = getattr(Resampling, resampling.lower(), Resampling.nearest)

        # Read and resample all bands
        data = src.read(
            out_shape=(src.count, new_height, new_width),
            resampling=resampling_enum
        )

        # Validate resampled data
        if data is None or data.size == 0:
            raise ValueError("No data was resampled.")

        # Calculate the new transform to reflect the resampling
        new_transform = src.transform * Affine.scale(
            (src.width  / new_width),
            (src.height / new_height)
        )

        # Update profile
        profile = src.profile.copy()
        profile.update({
            "height":    new_height,
            "width":     new_width,
            "transform": new_transform
        })
        src.close()

        # Ensure destination directory exists
        dst_path = os.path.expanduser(dst_clean)
        os.makedirs(os.path.dirname(dst_path) or ".", exist_ok=True)

        # Write the resampled raster
        with rasterio.open(dst_path, "w", **profile) as dst:
            dst.write(data)

        return {
            "status":      "success",
            "destination": dst_path,
            "message":     f"Raster resampled by factor {scale_factor} using '{resampling}' and saved to '{dst_path}'."
        }

    except Exception as e:
        # Log error and raise for MCP to report
        logger.error(f"Error resampling raster '{source}': {e}")
        raise ValueError(f"Failed to resample raster: {e}")

@mcp.tool()
def reproject_raster(
    source: str,
    target_crs: str,
    destination: str,
    resampling: str = "nearest"
) -> Dict[str, Any]:
    """
    Reproject a raster dataset to a new CRS and save the result.
    
    Parameters:
    - source:      local path or HTTPS URL of the source raster.
    - target_crs:  target CRS string (e.g., "EPSG:4326").
    - destination: local filesystem path for the reprojected raster.
    - resampling:  resampling method: "nearest", "bilinear", "cubic", etc.
    """
    try:
        import numpy as np
        import rasterio
        from rasterio.warp import calculate_default_transform, reproject, Resampling

        # Strip backticks if present
        src_clean = source.replace("`", "")
        dst_clean = destination.replace("`", "")

        # Open source (remote or local)
        if src_clean.lower().startswith("https://"):
            src = rasterio.open(src_clean)
        else:
            src_path = os.path.expanduser(src_clean)
            if not os.path.isfile(src_path):
                raise FileNotFoundError(f"Source raster not found at '{src_path}'.")
            src = rasterio.open(src_path)

        # Calculate transform and dimensions for the target CRS
        transform, width, height = calculate_default_transform(
            src.crs, target_crs, src.width, src.height, *src.bounds
        )

        # Update profile for output
        profile = src.profile.copy()
        profile.update({
            "crs": target_crs,
            "transform": transform,
            "width": width,
            "height": height
        })
        src.close()

        # Map resampling method string to Resampling enum
        resampling_enum = getattr(Resampling, resampling.lower(), Resampling.nearest)

        # Ensure destination directory exists
        dst_path = os.path.expanduser(dst_clean)
        os.makedirs(os.path.dirname(dst_path) or ".", exist_ok=True)

        # Perform reprojection and write output
        with rasterio.open(dst_path, "w", **profile) as dst:
            for i in range(1, profile["count"] + 1):
                reproject(
                    source=rasterio.open(src_clean).read(i),
                    destination=rasterio.band(dst, i),
                    src_transform=profile["transform"],  # placeholder, will be overwritten
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=target_crs,
                    resampling=resampling_enum
                )

        return {
            "status":      "success",
            "destination": dst_path,
            "message":     f"Raster reprojected to '{target_crs}' and saved to '{dst_path}'."
        }

    except Exception as e:
        logger.error(f"Error reprojecting raster '{source}' to '{target_crs}': {e}")
        raise ValueError(f"Failed to reproject raster: {e}")

@mcp.tool()
def extract_band(
    source: str,
    band_index: int,
    destination: str
) -> Dict[str, Any]:
    """
    Extract a specific band from a multi-band raster and save it as a single-band GeoTIFF.

    Parameters:
    - source:      path or URL of the input raster.
    - band_index:  index of the band to extract (1-based).
    - destination: path to save the extracted band raster.
    """
    try:
        import rasterio

        src_path = os.path.expanduser(source.replace("`", ""))
        dst_path = os.path.expanduser(destination.replace("`", ""))

        with rasterio.open(src_path) as src:
            if band_index < 1 or band_index > src.count:
                raise ValueError(f"Band index {band_index} is out of range. This raster has {src.count} bands.")

            band = src.read(band_index)
            profile = src.profile.copy()
            profile.update({
                "count": 1
            })

        os.makedirs(os.path.dirname(dst_path) or ".", exist_ok=True)

        with rasterio.open(dst_path, "w", **profile) as dst:
            dst.write(band, 1)

        return {
            "status": "success",
            "destination": dst_path,
            "message": f"Band {band_index} extracted and saved to '{dst_path}'."
        }

    except Exception as e:
        raise ValueError(f"Failed to extract band: {e}")

@mcp.tool()
def raster_band_statistics(
    source: str
) -> Dict[str, Any]:
    """
    Calculate min, max, mean, and std for each band of a raster.

    Parameters:
    - source: path to input raster (local or URL).
    """
    try:
        import numpy as np
        import rasterio

        src_path = os.path.expanduser(source.replace("`", ""))
        stats = {}

        with rasterio.open(src_path) as src:
            for i in range(1, src.count + 1):
                band = src.read(i, masked=True)  # masked array handles NoData
                stats[f"Band {i}"] = {
                    "min": float(band.min()),
                    "max": float(band.max()),
                    "mean": float(band.mean()),
                    "std": float(band.std())
                }

        return {
            "status": "success",
            "statistics": stats,
            "message": f"Band-wise statistics computed successfully."
        }

    except Exception as e:
        raise ValueError(f"Failed to compute statistics: {e}")

@mcp.tool()
def tile_raster(
    source: str,
    tile_size: int,
    destination_dir: str
) -> Dict[str, Any]:
    """
    Split a raster into square tiles of a given size and save them individually.

    Parameters:
    - source:         input raster path.
    - tile_size:      size of each tile (e.g., 256 or 512).
    - destination_dir: directory to store the tiles.
    """
    try:
        import os
        import rasterio
        from rasterio.windows import Window

        src_path = os.path.expanduser(source.replace("`", ""))
        dst_dir = os.path.expanduser(destination_dir.replace("`", ""))
        os.makedirs(dst_dir, exist_ok=True)

        tile_count = 0

        with rasterio.open(src_path) as src:
            profile = src.profile.copy()
            for i in range(0, src.height, tile_size):
                for j in range(0, src.width, tile_size):
                    window = Window(j, i, tile_size, tile_size)
                    transform = src.window_transform(window)
                    data = src.read(window=window)

                    out_profile = profile.copy()
                    out_profile.update({
                        "height": data.shape[1],
                        "width": data.shape[2],
                        "transform": transform
                    })

                    tile_path = os.path.join(dst_dir, f"tile_{i}_{j}.tif")
                    with rasterio.open(tile_path, "w", **out_profile) as dst:
                        dst.write(data)

                    tile_count += 1

        return {
            "status": "success",
            "tiles_created": tile_count,
            "message": f"{tile_count} tiles created and saved in '{dst_dir}'."
        }

    except Exception as e:
        raise ValueError(f"Failed to tile raster: {e}")

@mcp.tool()
def raster_histogram(
    source: str,
    bins: int = 256
) -> Dict[str, Any]:
    """
    Compute histogram of pixel values for each band.

    Parameters:
    - source: path to input raster.
    - bins:   number of histogram bins.
    """
    try:
        import rasterio
        import numpy as np
        import os

        src_path = os.path.expanduser(source.replace("`", ""))
        histograms = {}

        with rasterio.open(src_path) as src:
            for i in range(1, src.count + 1):
                band = src.read(i, masked=True)
                hist, bin_edges = np.histogram(band.compressed(), bins=bins)
                histograms[f"Band {i}"] = {
                    "histogram": hist.tolist(),
                    "bin_edges": bin_edges.tolist()
                }

        return {
            "status": "success",
            "histograms": histograms,
            "message": f"Histogram computed for all bands."
        }

    except Exception as e:
        raise ValueError(f"Failed to compute histogram: {e}")

@mcp.tool()
def compute_ndvi(
    source: str,
    red_band_index: int,
    nir_band_index: int,
    destination: str
) -> Dict[str, Any]:
    """
    Compute NDVI (Normalized Difference Vegetation Index) and save to GeoTIFF.

    Parameters:
    - source:            input raster path.
    - red_band_index:    index of red band (1-based).
    - nir_band_index:    index of near-infrared band (1-based).
    - destination:       output NDVI raster path.
    """
    try:
        import rasterio
        import numpy as np

        src_path = os.path.expanduser(source.replace("`", ""))
        dst_path = os.path.expanduser(destination.replace("`", ""))

        with rasterio.open(src_path) as src:
            red = src.read(red_band_index).astype("float32")
            nir = src.read(nir_band_index).astype("float32")
            ndvi = (nir - red) / (nir + red + 1e-6)  # avoid division by zero

            profile = src.profile.copy()
            profile.update(dtype="float32", count=1)

        os.makedirs(os.path.dirname(dst_path) or ".", exist_ok=True)

        with rasterio.open(dst_path, "w", **profile) as dst:
            dst.write(ndvi, 1)

        return {
            "status": "success",
            "destination": dst_path,
            "message": f"NDVI calculated and saved to '{dst_path}'."
        }

    except Exception as e:
        raise ValueError(f"Failed to compute NDVI: {e}")

@mcp.tool()
def raster_algebra(
    raster1: str,
    raster2: str,
    band_index: int,
    operation: str,  # User selects "add" or "subtract"
    destination: str
) -> Dict[str, Any]:
    """
    Perform algebraic operations (addition or subtraction) on two raster bands, 
    handling alignment issues automatically.

    Parameters:
    - raster1:     Path to the first raster (.tif).
    - raster2:     Path to the second raster (.tif).
    - band_index:  Index of the band to process (1-based index).
    - operation:   Either "add" or "subtract" to specify the calculation.
    - destination: Path to save the result as a new raster.

    The function aligns rasters if needed, applies the selected operation, and saves the result.
    """
    try:
        import rasterio
        import numpy as np
        from rasterio.warp import reproject, calculate_default_transform, Resampling

        # Expand file paths
        r1 = os.path.expanduser(raster1.replace("`", ""))
        r2 = os.path.expanduser(raster2.replace("`", ""))
        dst = os.path.expanduser(destination.replace("`", ""))

        # Open the raster files
        with rasterio.open(r1) as src1, rasterio.open(r2) as src2:
            # Ensure alignment of rasters
            if src1.crs != src2.crs or src1.transform != src2.transform or src1.shape != src2.shape:
                transform, width, height = calculate_default_transform(
                    src2.crs, src1.crs, src2.width, src2.height, *src2.bounds
                )
                aligned_data = np.zeros((height, width), dtype="float32")
                reproject(
                    source=src2.read(band_index),
                    destination=aligned_data,
                    src_transform=src2.transform,
                    src_crs=src2.crs,
                    dst_transform=transform,
                    dst_crs=src1.crs,
                    resampling=Resampling.bilinear
                )
                band2 = aligned_data
            else:
                band2 = src2.read(band_index).astype("float32")

            band1 = src1.read(band_index).astype("float32")

            # Perform the selected operation
            if operation.lower() == "add":
                result = band1 + band2
            elif operation.lower() == "subtract":
                result = band1 - band2
            else:
                raise ValueError("Invalid operation. Use 'add' or 'subtract'.")

            # Prepare output raster metadata
            profile = src1.profile.copy()
            profile.update(dtype="float32", count=1)

        # Ensure the output directory exists
        os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)

        # Save the result to a new raster file
        with rasterio.open(dst, "w", **profile) as dstfile:
            dstfile.write(result, 1)

        return {
            "status": "success",
            "destination": dst,
            "message": f"Raster operation '{operation}' completed and saved."
        }

    except Exception as e:
        raise ValueError(f"Failed to perform raster operation: {e}")

@mcp.tool()
def concat_bands(
    folder_path: str,
    destination: str
) -> Dict[str, Any]:
    """
    Concatenate multiple single-band raster files into one multi-band raster, 
    handling alignment issues automatically.

    Parameters:
    - folder_path:   Path to folder containing input raster files (e.g. GeoTIFFs).
    - destination:   Path to output multi-band raster file.

    Notes:
    - Files are read in sorted order by filename.
    - If rasters have mismatched CRS, resolution, or dimensions, they are aligned automatically.
    """
    try:
        import rasterio
        import numpy as np
        from rasterio.warp import reproject, calculate_default_transform, Resampling
        from glob import glob

        folder_path = os.path.expanduser(folder_path.replace("`", ""))
        dst_path = os.path.expanduser(destination.replace("`", ""))

        # Collect single-band TIFF files in folder
        files = sorted(glob(os.path.join(folder_path, "*.tif")))

        if len(files) == 0:
            raise ValueError("No .tif files found in folder.")

        # Read properties of the first file for reference
        with rasterio.open(files[0]) as ref:
            meta = ref.meta.copy()
            height, width = ref.height, ref.width
            crs = ref.crs
            transform = ref.transform
            dtype = ref.dtypes[0]

        meta.update(count=len(files), dtype=dtype)

        os.makedirs(os.path.dirname(dst_path) or ".", exist_ok=True)

        with rasterio.open(dst_path, "w", **meta) as dst:
            for idx, fp in enumerate(files, start=1):
                with rasterio.open(fp) as src:
                    band = src.read(1)

                    # Auto-align raster if size or CRS mismatch occurs
                    if src.height != height or src.width != width or src.crs != crs or src.transform != transform:
                        new_transform, new_width, new_height = calculate_default_transform(
                            src.crs, crs, src.width, src.height, *src.bounds
                        )
                        aligned_band = np.zeros((new_height, new_width), dtype=dtype)
                        reproject(
                            source=band,
                            destination=aligned_band,
                            src_transform=src.transform,
                            src_crs=src.crs,
                            dst_transform=new_transform,
                            dst_crs=crs,
                            resampling=Resampling.bilinear
                        )
                        band = aligned_band

                    dst.write(band, idx)

        return {
            "status": "success",
            "destination": dst_path,
            "message": f"{len(files)} single-band rasters concatenated into '{dst_path}'."
        }

    except Exception as e:
        raise ValueError(f"Failed to concatenate rasters: {e}")

@mcp.tool()
def weighted_band_sum(
    source: str,
    weights: List[float],
    destination: str
) -> Dict[str, Any]:
    """
    Compute a weighted sum of all bands in a raster using specified weights.

    Parameters:
    - source:      Path to the input multi-band raster file.
    - weights:     List of weights (must match number of bands and sum to 1).
    - destination: Path to save the output single-band raster.
    """
    try:
        import os
        import numpy as np
        import rasterio

        src_path = os.path.expanduser(source.replace("`", ""))
        dst_path = os.path.expanduser(destination.replace("`", ""))

        with rasterio.open(src_path) as src:
            count = src.count
            if len(weights) != count:
                raise ValueError(f"Number of weights ({len(weights)}) does not match number of bands ({count}).")

            if not np.isclose(sum(weights), 1.0, atol=1e-6):
                raise ValueError("Sum of weights must be 1.0.")

            weighted = np.zeros((src.height, src.width), dtype="float32")

            for i in range(1, count + 1):
                band = src.read(i).astype("float32")
                weighted += weights[i - 1] * band

            profile = src.profile.copy()
            profile.update(dtype="float32", count=1)

        os.makedirs(os.path.dirname(dst_path) or ".", exist_ok=True)

        with rasterio.open(dst_path, "w", **profile) as dst:
            dst.write(weighted, 1)

        return {
            "status": "success",
            "destination": dst_path,
            "message": f"Weighted band sum computed and saved to '{dst_path}'."
        }

    except Exception as e:
        raise ValueError(f"Failed to compute weighted sum: {e}")


@mcp.tool()
def getis_ord_g(
    shapefile_path: str,
    dependent_var: str = "LAND_USE",
    target_crs: str = "EPSG:4326",
    distance_threshold: float = 100000
) -> Dict[str, Any]:
    """Compute Getis-Ord G for global hot spot analysis."""
    try:
        # Clean backticks from string parameters
        shapefile_path = shapefile_path.replace("`", "")
        dependent_var = dependent_var.replace("`", "")
        target_crs = target_crs.replace("`", "")

        # Validate input file
        if not os.path.exists(shapefile_path):
            logger.error(f"Shapefile not found: {shapefile_path}")
            return {"status": "error", "message": f"Shapefile not found: {shapefile_path}"}

        # Load GeoDataFrame
        gdf = gpd.read_file(shapefile_path)
        
        # Validate dependent variable
        if dependent_var not in gdf.columns:
            logger.error(f"Dependent variable '{dependent_var}' not found in columns")
            return {"status": "error", "message": f"Dependent variable '{dependent_var}' not found in shapefile columns"}

        # Reproject to target CRS
        gdf = gdf.to_crs(target_crs)

        # Convert distance_threshold to degrees if using geographic CRS (e.g., EPSG:4326)
        effective_threshold = distance_threshold
        unit = "meters"
        if target_crs == "EPSG:4326":
            effective_threshold = distance_threshold / 111000
            unit = "degrees"

        # Extract dependent data
        dependent = gdf[dependent_var].values.astype(np.float64)

        # Create distance-based spatial weights matrix
        w = libpysal.weights.DistanceBand.from_dataframe(gdf, threshold=effective_threshold, binary=False)
        w.transform = 'r'

        # Handle islands
        for island in w.islands:
            w.weights[island] = [0] * len(w.weights[island])
            w.cardinalities[island] = 0

        # Getis-Ord G
        getis = esda.G(dependent, w)

        # Prepare GeoDataFrame preview
        preview = gdf[['geometry', dependent_var]].copy()
        preview['geometry'] = preview['geometry'].apply(lambda g: g.wkt)
        preview = preview.head(5).to_dict(orient="records")

        return {
            "status": "success",
            "message": f"Getis-Ord G analysis completed successfully (distance threshold: {effective_threshold} {unit})",
            "result": {
                "shapefile_path": shapefile_path,
                "getis_ord_g": {
                    "G": float(getis.G),
                    "p_value": float(getis.p_sim),
                    "z_score": float(getis.z_sim)
                },
                "data_preview": preview
            }
        }
    
    except Exception as e:
        logger.error(f"Error performing Getis-Ord G analysis: {str(e)}")
        return {"status": "error", "message": f"Failed to perform Getis-Ord G analysis: {str(e)}"}


def pysal_load_data(shapefile_path: str, dependent_var: str, target_crs: str, distance_threshold: float):
    """Common loader and weight creation for esda statistics."""
    if not os.path.exists(shapefile_path):
        return None, None, None, None, f"Shapefile not found: {shapefile_path}"

    gdf = gpd.read_file(shapefile_path)
    if dependent_var not in gdf.columns:
        return None, None, None, None, f"Dependent variable '{dependent_var}' not found in shapefile columns"

    gdf = gdf.to_crs(target_crs)

    effective_threshold = distance_threshold
    unit = "meters"
    if target_crs.upper() == "EPSG:4326":
        effective_threshold = distance_threshold / 111000
        unit = "degrees"

    y = gdf[dependent_var].values.astype(np.float64)
    w = libpysal.weights.DistanceBand.from_dataframe(gdf, threshold=effective_threshold, binary=False)
    w.transform = 'r'

    for island in w.islands:
        w.weights[island] = [0] * len(w.weights[island])
        w.cardinalities[island] = 0

    return gdf, y, w, (effective_threshold, unit), None


@mcp.tool()
def morans_i(shapefile_path: str, dependent_var: str = "LAND_USE", target_crs: str = "EPSG:4326", distance_threshold: float = 100000) -> Dict[str, Any]:
    """Compute Moran's I Global Autocorrelation Statistic."""
    gdf, y, w, (threshold, unit), err = pysal_load_data(shapefile_path, dependent_var, target_crs, distance_threshold)
    if err:
        return {"status": "error", "message": err}

    stat = esda.Moran(y, w)
    preview = gdf[['geometry', dependent_var]].head(5).assign(
        geometry=lambda df: df.geometry.apply(lambda g: g.wkt)
    ).to_dict(orient="records")

    return {
        "status": "success",
        "message": f"Moran's I completed successfully (threshold: {threshold} {unit})",
        "result": {
            "I": float(stat.I),
            "p_value": float(stat.p_sim),
            "z_score": float(stat.z_sim),
            "data_preview": preview
        }
    }


@mcp.tool()
def gearys_c(shapefile_path: str, dependent_var: str = "LAND_USE", target_crs: str = "EPSG:4326", distance_threshold: float = 100000) -> Dict[str, Any]:
    """Compute Global Geary's C Autocorrelation Statistic."""
    gdf, y, w, (threshold, unit), err = pysal_load_data(shapefile_path, dependent_var, target_crs, distance_threshold)
    if err:
        return {"status": "error", "message": err}

    stat = esda.Geary(y, w)
    preview = gdf[['geometry', dependent_var]].head(5).assign(
        geometry=lambda df: df.geometry.apply(lambda g: g.wkt)
    ).to_dict(orient="records")

    return {
        "status": "success",
        "message": f"Geary's C completed successfully (threshold: {threshold} {unit})",
        "result": {
            "C": float(stat.C),
            "p_value": float(stat.p_sim),
            "z_score": float(stat.z_sim),
            "data_preview": preview
        }
    }


@mcp.tool()
def gamma_statistic(shapefile_path: str, dependent_var: str = "LAND_USE", target_crs: str = "EPSG:4326", distance_threshold: float = 100000) -> Dict[str, Any]:
    """Compute Gamma Statistic for spatial autocorrelation."""
    gdf, y, w, (threshold, unit), err = pysal_load_data(shapefile_path, dependent_var, target_crs, distance_threshold)
    if err:
        return {"status": "error", "message": err}

    stat = esda.Gamma(y, w)
    preview = gdf[['geometry', dependent_var]].head(5).assign(
        geometry=lambda df: df.geometry.apply(lambda g: g.wkt)
    ).to_dict(orient="records")

    return {
        "status": "success",
        "message": f"Gamma Statistic completed successfully (threshold: {threshold} {unit})",
        "result": {
            "Gamma": float(stat.gamma),
            "p_value": float(stat.p_value) if hasattr(stat, "p_value") else None,
            "data_preview": preview
        }
    }


@mcp.tool()
def moran_local(shapefile_path: str, dependent_var: str = "LAND_USE", target_crs: str = "EPSG:4326",
                distance_threshold: float = 100000) -> Dict[str, Any]:
    """Local Moran's I."""
    gdf, y, w, (threshold, unit), err = pysal_load_data(shapefile_path, dependent_var, target_crs, distance_threshold)
    if err:
        return {"status": "error", "message": err}

    stat = esda.Moran_Local(y, w)
    preview = gdf[['geometry', dependent_var]].head(5).copy()
    preview['geometry'] = preview['geometry'].apply(lambda g: g.wkt)

    # Return local statistics array summary
    return {
        "status": "success",
        "message": f"Local Moran's I completed successfully (threshold: {threshold} {unit})",
        "result": {
            "Is": stat.Is.tolist(),
            "p_values": stat.p_sim.tolist(),
            "z_scores": stat.z_sim.tolist(),
            "data_preview": preview.to_dict(orient="records")
        }
    }


@mcp.tool()
def getis_ord_g_local(shapefile_path: str, dependent_var: str = "LAND_USE", target_crs: str = "EPSG:4326",
                      distance_threshold: float = 100000) -> Dict[str, Any]:
    """Local Getis-Ord G."""
    gdf, y, w, (threshold, unit), err = pysal_load_data(shapefile_path, dependent_var, target_crs, distance_threshold)
    if err:
        return {"status": "error", "message": err}

    stat = esda.G_Local(y, w)
    preview = gdf[['geometry', dependent_var]].head(5).copy()
    preview['geometry'] = preview['geometry'].apply(lambda g: g.wkt)

    return {
        "status": "success",
        "message": f"Local Getis-Ord G completed successfully (threshold: {threshold} {unit})",
        "result": {
            "G_local": stat.Gs.tolist(),
            "p_values": stat.p_sim.tolist(),
            "z_scores": stat.z_sim.tolist(),
            "data_preview": preview.to_dict(orient="records")
        }
    }


@mcp.tool()
def join_counts(shapefile_path: str, dependent_var: str = "LAND_USE", target_crs: str = "EPSG:4326",
                distance_threshold: float = 100000) -> Dict[str, Any]:
    """Global Binary Join Counts."""
    gdf, y, w, (threshold, unit), err = pysal_load_data(shapefile_path, dependent_var, target_crs, distance_threshold)
    if err:
        return {"status": "error", "message": err}

    # Join counts requires binary/categorical data - user must ensure y is binary (0/1 or True/False)
    stat = esda.Join_Counts(y, w)
    preview = gdf[['geometry', dependent_var]].head(5).copy()
    preview['geometry'] = preview['geometry'].apply(lambda g: g.wkt)

    return {
        "status": "success",
        "message": f"Join Counts completed successfully (threshold: {threshold} {unit})",
        "result": {
            "join_counts": stat.jc,
            "expected": stat.expected,
            "variance": stat.variance,
            "z_score": stat.z_score,
            "p_value": stat.p_value,
            "data_preview": preview.to_dict(orient="records")
        }
    }


@mcp.tool()
def join_counts_local(shapefile_path: str, dependent_var: str = "LAND_USE", target_crs: str = "EPSG:4326",
                      distance_threshold: float = 100000) -> Dict[str, Any]:
    """Local Join Counts."""
    gdf, y, w, (threshold, unit), err = pysal_load_data(shapefile_path, dependent_var, target_crs, distance_threshold)
    if err:
        return {"status": "error", "message": err}

    stat = esda.Join_Counts_Local(y, w)
    preview = gdf[['geometry', dependent_var]].head(5).copy()
    preview['geometry'] = preview['geometry'].apply(lambda g: g.wkt)

    return {
        "status": "success",
        "message": f"Local Join Counts completed successfully (threshold: {threshold} {unit})",
        "result": {
            "local_join_counts": stat.local_join_counts.tolist(),
            "data_preview": preview.to_dict(orient="records")
        }
    }


@mcp.tool()
def adbscan(shapefile_path: str, dependent_var: str = None, target_crs: str = "EPSG:4326",
            distance_threshold: float = 100000, eps: float = 0.1, min_samples: int = 5) -> Dict[str, Any]:
    """Adaptive DBSCAN clustering (requires coordinates, no dependent_var)."""
    if not os.path.exists(shapefile_path):
        return {"status": "error", "message": f"Shapefile not found: {shapefile_path}"}
    gdf = gpd.read_file(shapefile_path)
    gdf = gdf.to_crs(target_crs)

    coords = np.array(list(gdf.geometry.apply(lambda g: (g.x, g.y))))
    stat = esda.adbscan.ADBSCAN(coords, eps=eps, min_samples=min_samples)

    preview = gdf[['geometry']].head(5).copy()
    preview['geometry'] = preview['geometry'].apply(lambda g: g.wkt)

    return {
        "status": "success",
        "message": f"A-DBSCAN clustering completed successfully (eps={eps}, min_samples={min_samples})",
        "result": {
            "labels": stat.labels_.tolist(),
            "core_sample_indices": stat.core_sample_indices_.tolist(),
            "components": stat.components_.tolist() if hasattr(stat, "components_") else None,
            "data_preview": preview.to_dict(orient="records")
        }
    }

@mcp.tool()
def weights_from_shapefile(shapefile_path: str, contiguity: str = "queen", id_field: Optional[str] = None) -> Dict[str, Any]:

    """Create a spatial weights (W) from a shapefile using contiguity.

    - contiguity: 'queen' or 'rook' (default 'queen')
    - id_field: optional attribute name to use as observation IDs
    """
    try:
        if not os.path.exists(shapefile_path):
            return {"status": "error", "message": f"Shapefile not found: {shapefile_path}"}

        contiguity_lower = (contiguity or "").lower()
        if contiguity_lower == "queen":
            w = libpysal.weights.Queen.from_shapefile(shapefile_path, idVariable=id_field)
        elif contiguity_lower == "rook":
            w = libpysal.weights.Rook.from_shapefile(shapefile_path, idVariable=id_field)
        else:
            # Fallback to generic W loader if an unrecognized contiguity is provided
            w = libpysal.weights.W.from_shapefile(shapefile_path, idVariable=id_field)

        ids = w.id_order
        neighbor_counts = [w.cardinalities[i] for i in ids]
        islands = list(w.islands) if hasattr(w, "islands") else []

        preview_ids = ids[:5]
        neighbors_preview = {i: w.neighbors.get(i, []) for i in preview_ids}
        weights_preview = {i: w.weights.get(i, []) for i in preview_ids}

        result = {
            "n": int(w.n),
            "id_count": int(len(ids)),
            "id_field": id_field,
            "contiguity": contiguity_lower if contiguity_lower in {"queen", "rook"} else "generic",
            "neighbors_stats": {
                "min": int(min(neighbor_counts)) if neighbor_counts else 0,
                "max": int(max(neighbor_counts)) if neighbor_counts else 0,
                "mean": float(np.mean(neighbor_counts)) if neighbor_counts else 0.0,
            },
            "islands": islands,
            "neighbors_preview": neighbors_preview,
            "weights_preview": weights_preview,
        }

        return {
            "status": "success",
            "message": "Spatial weights constructed successfully",
            "result": result,
        }

    except Exception as e:
        logger.error(f"Error creating spatial weights from shapefile: {str(e)}")
        return {"status": "error", "message": f"Failed to create spatial weights: {str(e)}"}

@mcp.tool()
def distance_band_weights(
    data_path: str,
    threshold: float,
    binary: bool = True,
    id_field: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a distance-based spatial weights (W) object from point data.

    - data_path: path to point shapefile or GeoPackage
    - threshold: distance threshold for neighbors (in CRS units, e.g., meters)
    - binary: True for binary weights, False for inverse distance weights
    - id_field: optional attribute name to use as observation IDs
    """
    try:
        if not os.path.exists(data_path):
            return {"status": "error", "message": f"Data file not found: {data_path}"}

        gdf = gpd.read_file(data_path)

        if gdf.empty:
            return {"status": "error", "message": "Input file contains no features"}

        # Extract coordinates
        coords = [(geom.x, geom.y) for geom in gdf.geometry]

        # Create DistanceBand weights
        if id_field and id_field in gdf.columns:
            ids = gdf[id_field].tolist()
            w = weights.DistanceBand(coords, threshold=threshold, binary=binary, ids=ids)
        else:
            w = weights.DistanceBand(coords, threshold=threshold, binary=binary)

        ids = w.id_order
        neighbor_counts = [w.cardinalities[i] for i in ids]
        islands = list(w.islands) if hasattr(w, "islands") else []

        # Previews
        preview_ids = ids[:5]
        neighbors_preview = {i: w.neighbors.get(i, []) for i in preview_ids}
        weights_preview = {i: w.weights.get(i, []) for i in preview_ids}

        result = {
            "n": int(w.n),
            "id_count": len(ids),
            "threshold": threshold,
            "binary": binary,
            "id_field": id_field,
            "neighbors_stats": {
                "min": int(min(neighbor_counts)) if neighbor_counts else 0,
                "max": int(max(neighbor_counts)) if neighbor_counts else 0,
                "mean": float(np.mean(neighbor_counts)) if neighbor_counts else 0.0,
            },
            "islands": islands,
            "neighbors_preview": neighbors_preview,
            "weights_preview": weights_preview,
        }

        return {
            "status": "success",
            "message": "DistanceBand spatial weights constructed successfully",
            "result": result,
        }

    except Exception as e:
        logger.error(f"Error creating DistanceBand weights: {str(e)}")
        return {"status": "error", "message": f"Failed to create DistanceBand weights: {str(e)}"}


@mcp.tool()
def knn_weights(
    data_path: str,
    k: int,
    id_field: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a k-nearest neighbors spatial weights (W) object from point data.

    - data_path: path to point shapefile or GeoPackage
    - k: number of nearest neighbors
    - id_field: optional attribute name to use as observation IDs
    """
    try:
        if not os.path.exists(data_path):
            return {"status": "error", "message": f"Data file not found: {data_path}"}

        gdf = gpd.read_file(data_path)

        if gdf.empty:
            return {"status": "error", "message": "Input file contains no features"}

        # Extract coordinates
        coords = [(geom.x, geom.y) for geom in gdf.geometry]

        # Create KNN weights
        if id_field and id_field in gdf.columns:
            ids = gdf[id_field].tolist()
            w = weights.KNN(coords, k=k, ids=ids)
        else:
            w = weights.KNN(coords, k=k)

        ids = w.id_order
        neighbor_counts = [w.cardinalities[i] for i in ids]
        islands = list(w.islands) if hasattr(w, "islands") else []

        # Previews
        preview_ids = ids[:5]
        neighbors_preview = {i: w.neighbors.get(i, []) for i in preview_ids}
        weights_preview = {i: w.weights.get(i, []) for i in preview_ids}

        result = {
            "n": int(w.n),
            "id_count": len(ids),
            "k": k,
            "id_field": id_field,
            "neighbors_stats": {
                "min": int(min(neighbor_counts)) if neighbor_counts else 0,
                "max": int(max(neighbor_counts)) if neighbor_counts else 0,
                "mean": float(np.mean(neighbor_counts)) if neighbor_counts else 0.0,
            },
            "islands": islands,
            "neighbors_preview": neighbors_preview,
            "weights_preview": weights_preview,
        }

        return {
            "status": "success",
            "message": "KNN spatial weights constructed successfully",
            "result": result,
        }

    except Exception as e:
        logger.error(f"Error creating KNN weights: {str(e)}")
        return {"status": "error", "message": f"Failed to create KNN weights: {str(e)}"}



@mcp.tool()
def build_and_transform_weights(
    data_path: str,
    method: str = "queen",
    id_field: Optional[str] = None,
    threshold: Optional[float] = None,
    k: Optional[int] = None,
    binary: bool = True,
    transform_type: str = "r"
) -> Dict[str, Any]:
    """
    Build and transform spatial weights in one step.

    Parameters:
    - data_path: Path to point shapefile or GeoPackage
    - method: 'queen', 'rook', 'distance_band', or 'knn'
    - id_field: Optional field name for IDs
    - threshold: Distance threshold (required if method='distance_band')
    - k: Number of neighbors (required if method='knn')
    - binary: True for binary weights, False for inverse distance (DistanceBand only)
    - transform_type: 'r', 'v', 'b', 'o', or 'd'
    """
    try:
        # --- Step 1: Check file ---
        if not os.path.exists(data_path):
            return {"status": "error", "message": f"Data file not found: {data_path}"}

        gdf = gpd.read_file(data_path)
        if gdf.empty:
            return {"status": "error", "message": "Input file contains no features"}

        coords = [(geom.x, geom.y) for geom in gdf.geometry]

        # --- Step 2: Build weights ---
        method = (method or "").lower()
        if method == "queen":
            w = weights.Queen.from_dataframe(gdf, idVariable=id_field)
        elif method == "rook":
            w = weights.Rook.from_dataframe(gdf, idVariable=id_field)
        elif method == "distance_band":
            if threshold is None:
                return {"status": "error", "message": "Threshold is required for distance_band method"}
            if id_field and id_field in gdf.columns:
                ids = gdf[id_field].tolist()
                w = weights.DistanceBand(coords, threshold=threshold, binary=binary, ids=ids)
            else:
                w = weights.DistanceBand(coords, threshold=threshold, binary=binary)
        elif method == "knn":
            if k is None:
                return {"status": "error", "message": "k is required for knn method"}
            if id_field and id_field in gdf.columns:
                ids = gdf[id_field].tolist()
                w = weights.KNN(coords, k=k, ids=ids)
            else:
                w = weights.KNN(coords, k=k)
        else:
            return {"status": "error", "message": f"Unsupported method: {method}"}

        # --- Step 3: Apply transformation ---
        if not isinstance(w, W):
            return {"status": "error", "message": "Failed to build a valid W object"}
        transform_type = (transform_type or "").lower()
        if transform_type not in {"r", "v", "b", "o", "d"}:
            return {"status": "error", "message": f"Invalid transform type: {transform_type}"}
        w.transform = transform_type

        # --- Step 4: Build result ---
        ids = w.id_order
        neighbor_counts = [w.cardinalities[i] for i in ids]
        islands = list(w.islands) if hasattr(w, "islands") else []
        preview_ids = ids[:5]
        neighbors_preview = {i: w.neighbors.get(i, []) for i in preview_ids}
        weights_preview = {i: w.weights.get(i, []) for i in preview_ids}

        result = {
            "n": int(w.n),
            "id_count": len(ids),
            "method": method,
            "threshold": threshold if method == "distance_band" else None,
            "k": k if method == "knn" else None,
            "binary": binary if method == "distance_band" else None,
            "transform": transform_type,
            "neighbors_stats": {
                "min": int(min(neighbor_counts)) if neighbor_counts else 0,
                "max": int(max(neighbor_counts)) if neighbor_counts else 0,
                "mean": float(np.mean(neighbor_counts)) if neighbor_counts else 0.0,
            },
            "islands": islands,
            "neighbors_preview": neighbors_preview,
            "weights_preview": weights_preview,
        }

        return {
            "status": "success",
            "message": f"{method} spatial weights built and transformed successfully",
            "result": result,
        }

    except Exception as e:
        logger.error(f"Error in build_and_transform_weights: {str(e)}")
        return {"status": "error", "message": f"Failed to build and transform weights: {str(e)}"}




@mcp.tool()
def build_transform_and_save_weights(
    data_path: str,
    method: str = "queen",
    id_field: Optional[str] = None,
    threshold: Optional[float] = None,
    k: Optional[int] = None,
    binary: bool = True,
    transform_type: Optional[str] = None,
    output_path: str = "weights.gal",
    format: str = "gal",
    overwrite: bool = False
) -> Dict[str, Any]:
    """
    Pipeline: Read shapefile, build spatial weights, optionally transform, and save to file.

    Parameters:
    - data_path: Path to point shapefile or GeoPackage
    - method: 'queen', 'rook', 'distance_band', 'knn'
    - id_field: Optional field name for IDs
    - threshold: Distance threshold (required if method='distance_band')
    - k: Number of neighbors (required if method='knn')
    - binary: True for binary weights, False for inverse distance (DistanceBand only)
    - transform_type: 'r', 'v', 'b', 'o', or 'd' (optional)
    - output_path: File path to save weights
    - format: 'gal' or 'gwt'
    - overwrite: Allow overwriting if file exists
    """
    try:
        # --- Step 1: Check input file ---
        if not os.path.exists(data_path):
            return {"status": "error", "message": f"Data file not found: {data_path}"}

        gdf = gpd.read_file(data_path)
        if gdf.empty:
            return {"status": "error", "message": "Input file contains no features"}

        coords = [(geom.x, geom.y) for geom in gdf.geometry]

        # --- Step 2: Build weights ---
        method = (method or "").lower()
        if method == "queen":
            w = weights.Queen.from_dataframe(gdf, idVariable=id_field)
        elif method == "rook":
            w = weights.Rook.from_dataframe(gdf, idVariable=id_field)
        elif method == "distance_band":
            if threshold is None:
                return {"status": "error", "message": "Threshold is required for distance_band method"}
            if id_field and id_field in gdf.columns:
                ids = gdf[id_field].tolist()
                w = weights.DistanceBand(coords, threshold=threshold, binary=binary, ids=ids)
            else:
                w = weights.DistanceBand(coords, threshold=threshold, binary=binary)
        elif method == "knn":
            if k is None:
                return {"status": "error", "message": "k is required for knn method"}
            if id_field and id_field in gdf.columns:
                ids = gdf[id_field].tolist()
                w = weights.KNN(coords, k=k, ids=ids)
            else:
                w = weights.KNN(coords, k=k)
        else:
            return {"status": "error", "message": f"Unsupported method: {method}"}

        # --- Step 3: Apply transformation if given ---
        if transform_type:
            transform_type = (transform_type or "").lower()
            if transform_type not in {"r", "v", "b", "o", "d"}:
                return {"status": "error", "message": f"Invalid transform type: {transform_type}"}
            w.transform = transform_type

        # --- Step 4: Save weights to file ---
        format = (format or "").lower()
        if format not in {"gal", "gwt"}:
            return {"status": "error", "message": f"Invalid format: {format}"}

        if not output_path.lower().endswith(f".{format}"):
            output_path += f".{format}"

        if os.path.exists(output_path) and not overwrite:
            return {"status": "error", "message": f"File already exists: {output_path}. Set overwrite=True to replace it."}

        w.to_file(output_path, format=format)

        # --- Step 5: Build result ---
        return {
            "status": "success",
            "message": f"{method} weights built and saved successfully",
            "result": {
                "path": output_path,
                "format": format,
                "n": int(w.n),
                "transform": getattr(w, "transform", None),
                "islands": list(w.islands) if hasattr(w, "islands") else [],
            },
        }

    except Exception as e:
        logger.error(f"Error in build_transform_and_save_weights: {str(e)}")
        return {"status": "error", "message": f"Failed to build and save weights: {str(e)}"}


@mcp.tool()
def ols_with_spatial_diagnostics_safe(
    data_path: str,
    y_field: str,
    x_fields: List[str],
    weights_path: Optional[str] = None,
    weights_method: str = "queen",
    id_field: Optional[str] = None,
    threshold: Optional[float] = None,
    k: Optional[int] = None,
    binary: bool = True
) -> Dict[str, Any]:
    """
    Safe MCP pipeline: Read shapefile, build/load W, convert numeric, check NaNs, run OLS.

    Parameters:
    - data_path: path to shapefile or GeoPackage
    - y_field: dependent variable column name
    - x_fields: list of independent variable column names
    - weights_path: optional path to existing weights file (.gal or .gwt)
    - weights_method: 'queen', 'rook', 'distance_band', or 'knn' (used if weights_path not provided)
    - id_field: optional attribute name to use as observation IDs
    - threshold: required if method='distance_band'
    - k: required if method='knn'
    - binary: True for binary weights (DistanceBand only)
    """
    try:
        # --- Step 1: Read data ---
        if not os.path.exists(data_path):
            return {"status": "error", "message": f"Data file not found: {data_path}"}

        gdf = gpd.read_file(data_path)
        if gdf.empty:
            return {"status": "error", "message": "Input file contains no features"}

        # --- Step 2: Extract and convert y and X ---
        if y_field not in gdf.columns:
            return {"status": "error", "message": f"Dependent variable '{y_field}' not found in dataset"}
        if any(xf not in gdf.columns for xf in x_fields):
            return {"status": "error", "message": f"Independent variable(s) {x_fields} not found in dataset"}

        y = gdf[[y_field]].astype(float).values
        X = gdf[x_fields].astype(float).values

        # --- Step 3: Check for NaNs or infinite values ---
        if not np.all(np.isfinite(y)):
            return {"status": "error", "message": "Dependent variable contains NaN or infinite values"}
        if not np.all(np.isfinite(X)):
            return {"status": "error", "message": "Independent variables contain NaN or infinite values"}

        # --- Step 4: Load or build weights ---
        if weights_path:
            if not os.path.exists(weights_path):
                return {"status": "error", "message": f"Weights file not found: {weights_path}"}
            w = wio.open(weights_path).read()
        else:
            coords = [(geom.x, geom.y) for geom in gdf.geometry]
            wm = weights_method.lower()
            if wm == "queen":
                w = Queen.from_dataframe(gdf, idVariable=id_field)
            elif wm == "rook":
                w = Rook.from_dataframe(gdf, idVariable=id_field)
            elif wm == "distance_band":
                if threshold is None:
                    return {"status": "error", "message": "Threshold is required for distance_band"}
                ids = gdf[id_field].tolist() if id_field and id_field in gdf.columns else None
                w = DistanceBand(coords, threshold=threshold, binary=binary, ids=ids)
            elif wm == "knn":
                if k is None:
                    return {"status": "error", "message": "k is required for knn"}
                ids = gdf[id_field].tolist() if id_field and id_field in gdf.columns else None
                w = KNN(coords, k=k, ids=ids)
            else:
                return {"status": "error", "message": f"Unsupported weights method: {weights_method}"}

        w.transform = "r"  # Row-standardize for regression

        # --- Step 5: Fit OLS with spatial diagnostics ---
        ols_model = OLS(y, X, w=w, name_y=y_field, name_x=x_fields)

        # --- Step 6: Collect results ---
        results = {
            "n_obs": ols_model.n,
            "r2": float(ols_model.r2),
            "std_error": ols_model.std_err.tolist(),
            "betas": {name: float(beta) for name, beta in zip(ols_model.name_x + [ols_model.name_y], ols_model.betas.flatten())},
            "moran_residual": float(ols_model.moran_res[0]) if hasattr(ols_model, "moran_res") else None,
            "moran_pvalue": float(ols_model.moran_res[1]) if hasattr(ols_model, "moran_res") else None,
        }

        return {
            "status": "success",
            "message": "OLS regression with spatial diagnostics completed successfully",
            "result": results
        }

    except Exception as e:
        logger.error(f"Error in ols_with_spatial_diagnostics_safe: {str(e)}")
        return {"status": "error", "message": f"Failed to run OLS regression: {str(e)}"}






def main():
    """Main entry point for the GIS MCP server."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="GIS MCP Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    try:
        # Start the MCP server
        print("Starting GIS MCP server...")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 

