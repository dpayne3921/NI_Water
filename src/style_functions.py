# Function to create a style function for GeoJSON layers
def generic_style_function(color='blue'):
    return lambda feature: {
        'fillColor': color,
        'color': color,
        'weight': 2,
        'fillOpacity': 0.5
    }

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