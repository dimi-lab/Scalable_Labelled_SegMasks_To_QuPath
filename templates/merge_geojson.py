#!/usr/bin/env python3

import pandas as pd
print("Pandas v", pd.__version__)
import geopandas as gpd
print("Geopandas v", gpd.__version__)
import os, glob

# List of input GeoJSON files ${geojsonfiles}
geojson_files = glob.glob("poly_*.geojson")
output_file = "merged_output.geojson"

# Initialize an empty GeoDataFrame
merged_gdf = gpd.GeoDataFrame()
# Read and concatenate each GeoJSON file
for file in geojson_files:
    if os.path.exists(file):  # Check if the file exists
        gdf = gpd.read_file(file)
        merged_gdf = gpd.GeoDataFrame(pd.concat([merged_gdf, gdf], ignore_index=True))
    else:
        print(f"File {file} does not exist. Skipping.")

# Check if the CRS (Coordinate Reference System) is consistent
if not merged_gdf.empty and not merged_gdf.crs:
    # Set the CRS of the merged GeoDataFrame if none of the inputs had a defined CRS
    merged_gdf.set_crs("EPSG:4326", inplace=True)  # Assuming WGS84 CRS

# Save the merged GeoDataFrame to a new GeoJSON file
merged_gdf.to_file(output_file, driver="GeoJSON")

print(f"Merged GeoJSON saved to {output_file}")

