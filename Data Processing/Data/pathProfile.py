import numpy as np
import math

def createPathElevation(targetLng, targetLat, sourceLng, sourceLat, lng, lat, elevations):
	targetLngIndex = find_nearest_index(lng, targetLng)
	targetLatIndex = find_nearest_index(lat, targetLat)
	#print("Target: ", targetLngIndex, ", ", targetLatIndex)

	sourceLngIndex = find_nearest_index(lng, sourceLng)
	sourceLatIndex = find_nearest_index(lat, sourceLat)
	#print("Source: ", sourceLngIndex, ", ", sourceLatIndex)

	pathElevation = []
	currLat = sourceLatIndex
	currLong = sourceLngIndex

	while (currLat != targetLatIndex or currLong != targetLngIndex):
		pathElevation.append(elevations[currLong][currLat])

		delta_lon, delta_lat = getNextMove(currLat, currLong, targetLatIndex, targetLngIndex)

		currLat += delta_lat
		currLong += delta_lon
	
	return pathElevation

def getSlope(current_lat, current_lon, target_lat, target_lon):
	try:
		slope = (current_lat - target_lat) / (current_lon - target_lon)
	except ZeroDivisionError:
		slope = math.nan
	return slope

def getNextMove(current_lat, current_lon, target_lat, target_lon):
	slope = getSlope(current_lat, current_lon, target_lat, target_lon)

	if slope == math.nan:
		if target_lat > current_lat:
			return 0,1
		else:
			return 0,-1

	if target_lon > current_lon:
		if slope == 0:
			return 1,0
		if slope >= 0.7 and slope < 1.5:
			return 1,1
		if slope >= -1.5 and slope < -0.7:
			return 1, -1
		if slope >= 0.4 and slope < 0.7:
			return 2,1
		if slope >= -0.7 and slope < -0.4:
			return 2,-1
		if slope >= 1.5 and slope < 2.6:
			return 1,2
		if slope >= -2.6 and slope < -1.5:
			return 1,-2
		if slope >= 0 and slope < 0.4:
			return 3, 1
		if slope >= -0.4 and slope < 0:
			return 3,-1
		if slope >= 2.6:
			return 1, 3
		if slope < -2.6:
			return 1,-3
	else:
		if slope == 0:
			return -1,-0
		if slope >= 0.7 and slope < 1.5:
			return -1,-1
		if slope >= -1.5 and slope < -0.7:
			return -1,1
		if slope >= 0.4 and slope < 0.7:
			return -2,-1
		if slope >= -0.7 and slope < -0.4:
			return -2,1
		if slope >= 1.5 and slope < 2.6:
			return -1,-2
		if slope >= -2.6 and slope < -1.5:
			return -1,2
		if slope >= 0 and slope < 0.4:
			return -3,-1
		if slope >= -0.4 and slope < 0:
			return -3,1
		if slope >= 2.6:
			return -1,-3
		if slope < -2.6:
			return -1,3

def find_nearest_index(array, value):
    array = np.asarray(array)
    return (np.abs(array - value)).argmin()

