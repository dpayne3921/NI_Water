import geopandas as gpd
import folium
from style_functions import generic_style_function, river_segment_style_function
from data_processing import simplify_geometries

# Define the paths to the GML files
data_paths = {
    "Catchment Stakeholder Group": "C:/Users/Dpayn/MLE/NI_Water/data/CatchmentStakeholderGroup.gml",
    "Local Management Area": "C:/Users/Dpayn/MLE/NI_Water/data/LocalManagementArea.gml",
    "River Segment": "C:/Users/Dpayn/MLE/NI_Water/data/RiverSegment.gml",
    "Transitional Water Bodies - 1st Cycle": "C:/Users/Dpayn/MLE/NI_Water/data/TransitionalWaterBodies-1st-cycle.gml",
    "Lake Water Bodies": "C:/Users/Dpayn/MLE/NI_Water/data/Lake_Water_Bodies_2016.shp",
    "Surface Drinking Water Protected Areas": "C:/Users/Dpayn/MLE/NI_Water/data/Surface_Drinking_Water_Protected_Areas_2016.shp"
}

# Define layer colors
layer_colors = {
    "Catchment Stakeholder Group": 'green',
    "Local Management Area": 'orange',
    "River Segment": 'blue',
    "Transitional Water Bodies - 1st Cycle": 'red',
    "Lake Water Bodies": 'purple',
    "Surface Drinking Water Protected Areas": 'yellow'
}

# Function to filter GeoDataFrame based on layer name
def filter_by_layer_name(gdf, selected_layers):
    return gdf[gdf["Layer"].isin(selected_layers)]

# Load the files into GeoDataFrames
gdfs = {}
for name, path in data_paths.items():
    gdf = gpd.read_file(path)
    gdf["Layer"] = name  # Add layer name column
    gdfs[name] = gdf

# Function to create map with filtered layers
def create_map(selected_layers):
    # Create a base map
    m = folium.Map(location=[54.7877, -6.4923], zoom_start=8)  # Default center and zoom

    # Apply filters based on selected layers
    filtered_gdfs = {name: filter_by_layer_name(gdf, selected_layers) for name, gdf in gdfs.items()}

    # Simplify GeoDataFrames
    filtered_gdfs = {name: simplify_geometries(gdf) for name, gdf in filtered_gdfs.items()}

    # Add each filtered GeoDataFrame as a separate layer
    for name, gdf in filtered_gdfs.items():
        color = layer_colors.get(name, 'blue')  # Default to blue if color not specified
        folium.GeoJson(
            gdf,
            name=name,
            style_function=generic_style_function(color)
        ).add_to(m)

    # Add layer control to the map
    folium.LayerControl().add_to(m)

    return m

# Create and display the map with default layers
map_default = create_map(["Catchment Stakeholder Group", "River Segment"])
map_default.save("map_default.html")
