#!/usr/bin/env python3

import tifffile, csv, random, string
import numpy as np

labelMask = "${tiffFilePath}"
#labelMask = "SLIDE-3006_FullPanel_WholeCellMask.tiff"
interval = 200

random_5_letters = ''.join(random.choice(string.ascii_letters) for _ in range(5))
output_csv = "pixleSplitOut_{}.csv".format(random_5_letters)

slide = tifffile.imread(labelMask)
print(f" Dimensions: {slide.shape}")
topMx = np.max(slide)+1
print(" > Last Label:"+str(topMx))
       
# Create intervals from 1 to topMx with the given interval
intervals = [(i, min(i + interval - 1, topMx)) for i in range(1, topMx, interval)]
print(" N Intervals:"+str(len(intervals)))

# Write intervals to CSV file
with open(output_csv, mode='w', newline='') as file:
	writer = csv.writer(file)
	writer.writerow(['Start', 'End'])
	writer.writerows(intervals)
	
print(f"Intervals written to {output_csv}")


