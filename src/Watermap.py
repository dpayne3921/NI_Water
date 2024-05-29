import geopandas as gpd
import folium
from folium import LayerControl

# Define the paths to the GML files
data_paths = {
    "Catchment Stakeholder Group": "C:/Users/Dpayn/MLE/NI_Water/data/CatchmentStakeholderGroup.gml",
    "Local Management Area": "C:/Users/Dpayn/MLE/NI_Water/data/LocalManagementArea.gml",
    "River Segment": "C:/Users/Dpayn/MLE/NI_Water/data/RiverSegment.gml",
    "Transitional Water Bodies - 1st Cycle": "C:/Users/Dpayn/MLE/NI_Water/data/TransitionalWaterBodies-1st-cycle.gml",
    "Lake Water Bodies": "C:/Users/Dpayn/MLE/NI_Water/data/Lake_Water_Bodies_2016.shp",
    "Surface Drinking Water Protected Areas": "C:/Users/Dpayn/MLE/NI_Water/data/Surface_Drinking_Water_Protected_Areas_2016.shp"
}

# Define the path to the GeoJSON file
geojson_path = r"C:\Users\Dpayn\MLE\NI_Water\data\Register_of_Private_Water_Supplies_in_Northern_Ireland_(24_04_2020).geojson"

# Load the files into GeoDataFrames
gdfs = {name: gpd.read_file(path) for name, path in data_paths.items()}

# Load the GeoJSON file into a GeoDataFrame
water_supply_gdf = gpd.read_file(geojson_path)

# Reproject all GeoDataFrames to a projected CRS (e.g., EPSG:3857)
gdfs = {name: gdf.to_crs(epsg=3857) for name, gdf in gdfs.items()}
water_supply_gdf = water_supply_gdf.to_crs(epsg=3857)

# Inspect each GeoDataFrame
for name, gdf in gdfs.items():
    print(f"--- {name} ---")
    print(gdf.info())
    print(gdf.head())
    print("\n")

print("--- Register of Private Water Supplies ---")
print(water_supply_gdf.info())
print(water_supply_gdf.head())
print("\n")

# Function to simplify geometries for better performance
def simplify_geometries(gdf, tolerance=0.001):
    gdf['geometry'] = gdf['geometry'].simplify(tolerance, preserve_topology=True)
    return gdf

# Simplify GeoDataFrames
gdfs = {name: simplify_geometries(gdf) for name, gdf in gdfs.items()}
water_supply_gdf = simplify_geometries(water_supply_gdf)

# Function to create a style function for GeoJSON layers
def generic_style_function(color='blue'):
    return lambda feature: {
        'fillColor': color,
        'color': color,
        'weight': 2,
        'fillOpacity': 0.5
    }

# Example of different colors for each layer
layer_colors = {
    "Catchment Stakeholder Group": 'green',
    "Local Management Area": 'orange',
    "River Segment": 'blue',
    "Transitional Water Bodies - 1st Cycle": 'red',
    "Lake Water Bodies": 'purple',
    "Surface Drinking Water Protected Areas": 'yellow'
}

# Example specific style function for River Segment based on SEGMENT_TYPE
def river_segment_style_function(feature):
    type_color_mapping = {
        'Y': 'blue',   # Real segment
        'N': 'green',  # Real underground segment
        'L': 'purple', # Virtual lake segment
        'T': 'black',  # Virtual transitional water segment
        'C': 'purple', # Virtual coastal water segment
        'V': 'gray',   # Unclassified virtual segment
        None: 'gray'   # Default color for features with None SEGMENT_TYPE
    }
    type_value = feature['properties'].get('SEGMENT_TYPE', None)  # None if type not specified

    return {
        'fillColor': type_color_mapping.get(type_value, 'gray'),
        'color': type_color_mapping.get(type_value, 'gray'),
        'weight': 1,
        'fillOpacity': 0.5
    }

# Determine the center of the map based on the data
center_lat = sum([gdf.geometry.centroid.y.mean() for gdf in gdfs.values()]) / len(gdfs)
center_lon = sum([gdf.geometry.centroid.x.mean() for gdf in gdfs.values()]) / len(gdfs)

# Create a base map centered around the data
m = folium.Map(location=[center_lat, center_lon], zoom_start=10)

# Add each GeoDataFrame as a separate layer
for name, gdf in gdfs.items():
    if name == "River Segment":
        # Add river segments layer with different SEGMENT_TYPE values if available
        for segment_type in gdf["SEGMENT_TYPE"].dropna().unique():  # Drop null values
            segment_gdf = gdf[gdf["SEGMENT_TYPE"] == segment_type]
            folium.GeoJson(
                segment_gdf,
                name=f"River Segment - {segment_type}",
                style_function=river_segment_style_function,
                #tooltip=folium.GeoJsonTooltip(fields=['SEGMENT_TYPE'])
            ).add_to(m)
    elif name == "Catchment Stakeholder Group":
        # Add Catchment Stakeholder Group layer with tooltip
        folium.GeoJson(
            gdf,
            name=name,
            style_function=generic_style_function('green'),
            tooltip=folium.GeoJsonTooltip(fields=['NAME'])
        ).add_to(m)
    else:
        color = layer_colors.get(name, 'blue')  # Default to blue if color not specified
        folium.GeoJson(
            gdf,
            name=name,
            style_function=generic_style_function(color)
        ).add_to(m)

# Add the register of private water supplies as a layer
folium.GeoJson(
    water_supply_gdf,
    name="Register of Private Water Supplies",
    style_function=generic_style_function('black')
).add_to(m)

# Add layer control to the map
folium.LayerControl().add_to(m)

# Save the map as an HTML file
m.save("output_map.html")
