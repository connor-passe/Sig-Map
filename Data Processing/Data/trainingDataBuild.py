import csv
from helpers import createPathElevation, getSlope
from dtedParser import get_dted
import numpy as np
from scipy.signal import argrelextrema

# This will be used to compress the paths (i.e. [1,5,5,5,1] becomes [1,5,1]), 
# so non knife-edge peaks can be considered
def remove_adjacent(path, dist):
     return [(a,c) for a,b,c in zip(path, path[1:]+[not path[-1]], dist) if a != b]

# create header, can add to file if helpful
header = ['frequency', 'power loss']

cities = ['boston', 'london', 'merthyr', 'nottingham', 'scarhill', 'southampton', 'stevenage']
 
frequencies = ['449', '915', '1802', '2695', '3602', '5850']


cur_city = 0
# for file in UK dataset
for city in cities:
	print("City: ", city)
	lng, lat, elevations = get_dted(cur_city)
	#Call then increment
	cur_city += 1
	for frequency in frequencies:
		#Resets Data Array before each frequency
		data = []
		f = open('UKDataset/'+city+frequency+'.csv', 'r')
		reader = csv.reader(f)

		info = []
		for row in reader:
			info.append(row)
		f.close()

		# get relevant info from UK header
		TxLat = float(info[1][0].split(' ')[-2])
		TxLon = float(info[2][0].split(' ')[-2])
		frequency = float(info[3][0].split(' ')[-2])/1000
		TxPower = float(info[5][0].split(' ')[-2])
		TxHeight = float(info[4][0].split(' ')[-2])

		print("Frequency: ", frequency)
		print("Row Count: ", len(info))
		power_cache = {}
		
		# for each data point, determine parameters for each point here
		counter = 0
		for i in range(len(info)-10):
			if frequency == 1.8025 and city == 'boston': 
				tempList = info[i+10][0].split(" ")[1].split("\t")
				RxPower = float(tempList[3])
				RxLng = float(tempList[2])
				RxLat = float(tempList[1])
			else:
				RxPower = float(info[i+10][4])
				RxLng = float(info[i+10][3])
				RxLat = float(info[i+10][2])

			path_list, dist_list = createPathElevation(RxLng, RxLat, TxLon, TxLat, lng, lat, elevations, False)
			if len(path_list) == 0 or len(dist_list) == 0:
				data.append([0])
				continue

			compressed_list = remove_adjacent(path_list, dist_list)
			path, dist = list(map(list, zip(*compressed_list)))
			path = np.array(path)
			dist = np.array(dist)

			# Distance between current point and transmitter
			total_dist = dist_list[len(dist_list)-1]

			# Height difference between current point and transmitter
			tx_rx_height_diff = TxHeight - path_list[len(path_list)-1]

			# Indices at which the peaks exist in |path|
			peak_indices = argrelextrema(path, np.greater)[0]

			# Highest peak with respect to the transmitter
			max_peak = 0

			# Average height difference between adjacent peaks
			avg_height_diff = 0

			# Average distance between adjacent peaks
			avg_dist = 0

			# Number of peaks in current |path|
			peak_count = len(peak_indices)

			for j in range(peak_count):
				peak_index = peak_indices[j]
				if j != 0:
					prev_peak_index = peak_indices[j-1]
					avg_height_diff += abs(path[peak_index]-path[prev_peak_index])
					avg_dist += abs(dist[peak_index]-dist[prev_peak_index])

			if peak_count > 1:
				avg_height_diff = avg_height_diff / (peak_count-1)
				avg_dist = avg_dist / (peak_count-1)
				max_peak = max(path_list[:-1])-TxHeight

			# Frequency, RxPower, total distance, Tx/Rx height diff, Avg height diff, Avg dist, Peak count
			data.append([frequency, TxPower - RxPower, total_dist, tx_rx_height_diff, avg_height_diff, avg_dist, max_peak, peak_count])

			if counter % 100000 == 0:
				print(str(counter) + " / " + str(len(info)))
			# print(counter)
			counter += 1
		
		file_path = 'trainingDataset/'+city+str(frequency)+'.csv'
		
		with open(file_path, 'w', newline='') as file:
			writer = csv.writer(file, delimiter=',')
			writer.writerow(['Frequency', 'Power Loss', 'Distance', 'Height Difference', 'Peak Avg. Height Diff', 'Peak Avg. Dist.', 'Max Peak', 'Peak Count'])
			writer.writerows(data)