#!/usr/bin/env python3

from pprint import pprint
import tifffile, geojson, os, random, string
import numpy as np
print("Numpy v", np.__version__)
import cv2
print("OpenCV v", cv2.__version__)

os.environ["OPENCV_IO_MAX_IMAGE_PIXELS"] = str(pow(2,40))

labelMask = "${tiffFilePath}"
rr = "${rowValues}" 
st = int(rr.split(",")[0].split(":")[1])
nd = int(rr.split(",")[1].split(":")[1].strip("[]"))

random_10_letters = ''.join(random.choice(string.ascii_letters) for _ in range(10))
geojson_file = "poly_{}.geojson".format(random_10_letters)

print([labelMask, st, nd, rr])

slide = tifffile.imread(labelMask)
print(f"    Dimensions: {slide.shape}")

# Convert the 4D array to 2D by selecting the 2nd and 3rd dimensions
image_2d = np.squeeze(slide)  # Removes the 1st and 4th singleton dimensions
# Alternatively, you could directly select like this:
# image_2d = image[0, :, :, 0]
print(f"    New Dimensions: {image_2d.shape}")

arrayShapes=[]
for i in range(st, nd):
	if i % 50 == 0:
		print("Progress: "+str(np.round((i-st) / (nd-st), decimals=4)*100 )+"%")
	
	slide2 = (image_2d == i).astype(np.uint8)
	contours, hierarchy = cv2.findContours(slide2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	for contour in contours:
		# Convert contour to Python list and ensure it's in the correct format
		coordinates = [[float(x), float(y)] for [[x, y]] in contour.tolist()] # Switch (y, x) to (x, y) for GeoJSON
		# Ensure the polygon is closed by adding the first point to the end, if necessary
		if coordinates[0] != coordinates[-1]:
			coordinates.append(coordinates[0])  # Close the polygon
		# Create a Polygon geometry for the ROI
		polygon = geojson.Polygon([coordinates])
		# Create a GeoJSON feature for the ROI
		feature = geojson.Feature(geometry=polygon, properties={"roi_value": int(i)})
		# Add the feature to the feature list
		arrayShapes.append(feature)

# Create a GeoJSON FeatureCollection
feature_collection = geojson.FeatureCollection(arrayShapes)

# Export the GeoJSON to a file
with open(geojson_file, 'w') as f:
	geojson.dump(feature_collection, f)

print(f"GeoJSON file saved to {geojson_file}")


