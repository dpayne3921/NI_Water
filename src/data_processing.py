import geopandas as gpd

def simplify_geometries(gdf, tolerance=0.001):
    gdf['geometry'] = gdf['geometry'].simplify(tolerance, preserve_topology=True)
    return gdf