'''
Helper function to build the heat map
'''

import numpy as np
import math
import time
from scipy.signal import argrelextrema


UNIT_VECTOR_PRECISION = float(10**4)
WAVELENGTH = 299792458 / 915000000

def findOrigin(lng, lat, TxLng, TxLat):
	# find starting indices
	minLat = min(lat)
	maxLat = max(lat)
	stepLat = (maxLat - minLat)/len(lat)
	indexLat = int((float(TxLat)-minLat)/stepLat)

	minLng = min(lng)
	maxLng = max(lng)
	stepLng = (maxLng - minLng)/len(lng)
	indexLng = int((float(TxLng)-minLng)/stepLng)

	return indexLng, indexLat

def distance(lon1_d, lat1_d, lon2_d, lat2_d):

	# DD coordinates 

	r = 6.371e3 # km
	# convert to radians
	lon1 = lon1_d * (np.pi/180) 
	lon2 = lon2_d * (np.pi/180)
	lat1 = lat1_d * (np.pi/180)
	lat2 = lat2_d * (np.pi/180)
	
	d=2*np.arcsin(np.sqrt((np.sin((lat1-lat2)/2))**2 + 
                np.cos(lat1)*np.cos(lat2)*(np.sin((lon1-lon2)/2))**2))
	
	return r*d # km

def powerLoss(distance, frequency): 
	# distance given in km and frequency given in GHz

	return 20*np.log10(distance) + 20*np.log10(frequency) + 92.45

def unitVector(lat, lng, TxLat, TxLng):
	# builds a unit vector between point (lat, lng) and (TxLat, TxLng)

	a = TxLat - lat
	b = TxLng - lng

	magnitude = math.sqrt((a**2) + (b**2))
	a = a / magnitude
	b = b / magnitude
	a = int(a * UNIT_VECTOR_PRECISION + 0.5) / UNIT_VECTOR_PRECISION
	b = int(b * UNIT_VECTOR_PRECISION + 0.5) / UNIT_VECTOR_PRECISION

	return tuple([a,b])

def fresnelZoneRadius(zone, dr, dp, frequency):
	# frequency should be in MHz, distance in m
	frequency = frequency * 1000 # MHz

	return 547.533*math.sqrt(dp*(dr-dp)/(frequency*dr))

def terrainLoss_trivial(udict, unitVector, elevation, TxElevation, buff):
	# loss due to terrain barriers, in build currently
	
	if unitVector in udict:
		peak = int(udict[unitVector])
		if elevation < (peak-buff):
			loss = 25
		elif elevation < peak:
			loss = 0
		else:
			loss = 0
			udict[unitVector] = elevation

	else:
		udict[unitVector] = elevation
		loss = 0

	return loss

def local_diffraction_loss(v,p):
	a_v_0 = 0.0
	if -0.8 <= v and v <= 0:
		a_v_0 = 6.02+(9.0*v)+(1.65*v**2)
	elif 0 < v and v <= 2.4:
		a_v_0 = 6.02+(9.11*v)-1.27*(v**2)
	else:
		a_v_0 = 12.953+20*math.log10(v)
	
	a_0_p = 6.02+(5.556*p)+3.418*(p**2)+0.256*(p**3)

	u_v_p = 0.0
	if v*p <= 3:
		u_v_p = (11.45*v*p)+2.19*((v*p)**2)-0.206*((v*p)**3)-6.02
	elif 3 < v*p and v*p <= 5:
		u_v_p = (13.47*v*p)+1.058*((v*p)**2)-0.048*((v*p)**3)-6.02
	else:
		u_v_p = (20*v*p)-18.2

	return a_v_0+a_0_p+u_v_p

def vFactor(prev_dist, cur_dist, next_dist, los_clearance):
	dist_1 = cur_dist - prev_dist
	dist_2 = next_dist - cur_dist
	alpha = math.tanh(los_clearance/dist_1)
	beta = math.tanh(los_clearance/dist_2)
	return math.sqrt((2*(next_dist-prev_dist)*math.tan(alpha)*math.tan(beta))/(WAVELENGTH/1000))

def curvatureFactor(radius, dist_to_prev, dist_to_next):
	d = dist_to_prev+dist_to_next
	return 0.676*(radius**0.333)*(WAVELENGTH**-0.1667)*(d/(dist_to_prev*dist_to_next))**0.5

def partial_obstruction_loss(los_clearance, fz_radius):
	if fz_radius == 0:
		return 0
	return 6*(1-(los_clearance/fz_radius))

def fresnelZoneRadius(zone, dr, dp):
	return 547.533*math.sqrt(dp*(dr-dp)/(449*dr))

def effective_earth_radius_height(total_distance, d1):
	d2 = total_distance-d1
	return (d1*d2) / (12.74*1.33) # atmospheric k-factor

def line_of_sight_clearance(height_1, height_2, total_dist, dist_1, obs_height):
	height_er = effective_earth_radius_height(total_dist, dist_1)
	return height_1+(((height_2-height_1)/total_dist)*dist_1)-height_er-obs_height

def terrainLoss_physics(udict, peak_dict, unit_vector, elevation, TxElevation, buff, TxLng, TxLat, RxLng, RxLat):
	# loss due to terrain barriers, in build currently
	h1 = TxElevation+17 # TxHeight
	h2 = elevation+1.5 # RxHeight

	# Distance to transmitter in km.
	cur_dist_to_tx = distance(TxLng, TxLat, RxLng, RxLat)
	loss = 0
	los_mode = True

	if unit_vector not in peak_dict:
			return 1000
	
	for peak_index in peak_dict[unit_vector]:
		obs_height, obs_dist_to_tx = udict[unit_vector][peak_index]
		if cur_dist_to_tx < obs_dist_to_tx:
			break
		los_clearance = line_of_sight_clearance(h1, h2, cur_dist_to_tx, obs_dist_to_tx, obs_height)
		if los_mode and los_clearance < 0:
			los_mode = False
			loss = 0
		if los_mode:
			partial_fz_radius = 0.6*fresnelZoneRadius(1, cur_dist_to_tx, obs_dist_to_tx)
			loss = max(loss, partial_obstruction_loss(los_clearance, partial_fz_radius))
		elif los_clearance < 0:
			prev_dist_to_tx = obs_dist_to_tx / 2 #0 if i == 0 else udict[unitVector][i-1][1]
			next_dist_to_tx = obs_dist_to_tx / 2 #cur_dist_to_tx if i == len(udict[unitVector])-1 else udict[unitVector][i+1][1]
			p = curvatureFactor(1, obs_dist_to_tx-prev_dist_to_tx, next_dist_to_tx-obs_dist_to_tx)
			v = vFactor(prev_dist_to_tx, obs_dist_to_tx, next_dist_to_tx, los_clearance)
			loss += local_diffraction_loss(v, p)

	return loss

def buildGrid(size):
	# builds the map grid

	# check for odd size
	if (size%2) == 0:
		size += 1

	# build out grid
	grid = []
	for i in range(size):
		column = []
		for j in range(size):
			column.append(0)
		grid.append(column)

	return grid

def buildMesh(indexLng, indexLat, size, lng, lat):
	# builds x and y mesh needed for plotting
	
	# check for odd size
	if (size%2) == 0:
		size += 1

	origin = size//2

	lngArray = np.linspace(lng[indexLng-origin], lng[indexLng+origin], num = size, endpoint = False)
	latArray = np.linspace(lat[indexLat-origin], lat[indexLat+origin], num = size, endpoint = False)
	latMesh, lngMesh = np.meshgrid(latArray, lngArray)

	return lngMesh, latMesh

def FSPL(indexLng, indexLat, size, lng, lat, TxLng, TxLat, frequency):
	# square approximation for FSPL... resulted in a 4.5x speed increase

	# check for odd size
	if (size%2) == 0:
		size += 1

	origin = size//2

	FSPL_list = []

	for i in range(origin):
		FSPL_list.append(powerLoss( distance(float(TxLng), float(TxLat), float(TxLng), lat[i+indexLat]), frequency ))

	return FSPL_list

def elevationGrid(size, elevations, indexLng, indexLat, lng, lat):
	# produces elevation grid centered around transmitter of a given size

	# check for odd size
	if (size%2) == 0:
		size += 1
	origin = size//2

	elevation_grid = buildGrid(size)

	for i in range(origin): # how many times to go out 
		i = i + 1

		for j in range(i):
			elevation_grid[i+origin][int(j)+origin] = elevations[int(j)+indexLng][i+indexLat]
			elevation_grid[-i+origin][int(j)+origin] = elevations[int(j)+indexLng][-i+indexLat]
			if j != 0:
				elevation_grid[i+origin][int(-j)+origin] = elevations[int(-j)+indexLng][i+indexLat]
				elevation_grid[-i+origin][int(-j)+origin] = elevations[int(-j)+indexLng][-i+indexLat]

		for j in np.linspace(-i, i, (2*i)+1):
			elevation_grid[int(j)+origin][i+origin] = elevations[(i+indexLng)][int(j)+indexLat]
			elevation_grid[int(j)+origin][-i+origin] = elevations[-i+indexLng][int(j)+indexLat]

	return elevation_grid

def FSPLGrid(size, lng, lat, indexLng, indexLat, TxLng, TxLat):
	# produces elevation grid centered around transmitter of a given size

	# temporary check for odd size
	if (size%2) == 0:
		size += 1

	# fill in grid
	origin = size//2

	FSPL_grid = buildGrid(size)

	for i in range(origin): # how many times to go out 
		i = i + 1

		for j in range(i):
			FSPL_grid[i+origin][int(j)+origin] = powerLoss(distance(float(TxLng), float(TxLat), lng[int(j)+indexLng], lat[i+indexLat]), 1)
			FSPL_grid[-i+origin][int(j)+origin] = powerLoss(distance(float(TxLng), float(TxLat), lng[int(j)+indexLng], lat[-i+indexLat]), 1)
			if j != 0:
				FSPL_grid[i+origin][int(-j)+origin] = powerLoss(distance(float(TxLng), float(TxLat), lng[int(-j)+indexLng], lat[i+indexLat]), 1)
				FSPL_grid[-i+origin][int(-j)+origin] = powerLoss(distance(float(TxLng), float(TxLat), lng[int(-j)+indexLng], lat[-i+indexLat]), 1)


		for j in np.linspace(-i, i, (2*i)+1):
			FSPL_grid[int(j)+origin][i+origin] = powerLoss(distance(float(TxLng), float(TxLat), lng[(i+indexLng)], lat[int(j)+indexLat]), 1)
			FSPL_grid[int(j)+origin][-i+origin] = powerLoss(distance(float(TxLng), float(TxLat), lng[-i+indexLng], lat[int(j)+indexLat]), 1)

	return FSPL_grid

def buildMap(size, lng, lat, indexLng, indexLat, TxLng, TxLat, elevations, frequency):
	# combines elevationGrid and FSPLGrid for efficiency and builds map in radial circles

	# temporary check for odd size
	if (size%2) == 0:
		size += 1

	# fill in grid
	origin = size//2

	elevation_grid = buildGrid(size)
	power_grid = buildGrid(size)

	for i in range(origin): # how many times to go out 
		i = i + 1

		for j in range(i):
			power_grid[i+origin][int(j)+origin] = powerLoss(distance(float(TxLng), float(TxLat), lng[int(j)+indexLng], lat[i+indexLat]), 1)
			elevation_grid[i+origin][int(j)+origin] = elevations[int(j)+indexLng][i+indexLat]

			power_grid[-i+origin][int(j)+origin] = powerLoss(distance(float(TxLng), float(TxLat), lng[int(j)+indexLng], lat[-i+indexLat]), 1)
			elevation_grid[-i+origin][int(j)+origin] = elevations[int(j)+indexLng][-i+indexLat]

			if j != 0:
				power_grid[i+origin][int(-j)+origin] = powerLoss(distance(float(TxLng), float(TxLat), lng[int(-j)+indexLng], lat[i+indexLat]), 1)
				elevation_grid[i+origin][int(-j)+origin] = elevations[int(-j)+indexLng][i+indexLat]

				power_grid[-i+origin][int(-j)+origin] = powerLoss(distance(float(TxLng), float(TxLat), lng[int(-j)+indexLng], lat[-i+indexLat]), 1)
				elevation_grid[-i+origin][int(-j)+origin] = elevations[int(-j)+indexLng][-i+indexLat]


		for j in np.linspace(-i, i, (2*i)+1):
			power_grid[int(j)+origin][i+origin] = powerLoss(distance(float(TxLng), float(TxLat), lng[(i+indexLng)], lat[int(j)+indexLat]), 1)
			elevation_grid[int(j)+origin][i+origin] = elevations[(i+indexLng)][int(j)+indexLat]

			power_grid[int(j)+origin][-i+origin] = powerLoss(distance(float(TxLng), float(TxLat), lng[-i+indexLng], lat[int(j)+indexLat]), 1)
			elevation_grid[int(j)+origin][-i+origin] = elevations[-i+indexLng][int(j)+indexLat]

	return elevation_grid, power_grid

def preComputePeaks(udict, peak_dict, indexLat, indexLng, TxLng, TxLat, lng, lat, origin, elevations):

	for n in range(origin):
		n = n + 1

		for i in np.linspace(-n+1, n-1, (2*n)-1):
			i = int(i)

			# y = n (top)
			unit_vector = unitVector(lng[indexLng + i], lat[indexLat + n], TxLng, TxLat)
			RxLng = lng[indexLng+i]
			RxLat = lat[indexLat+n]
			elevation = int(elevations[indexLng+i][indexLat+n])
			cur_dist = distance(TxLng, TxLat, RxLng, RxLat)
			if unit_vector not in udict:
				udict[unit_vector] = []
			udict[unit_vector].append((elevation, cur_dist))

			# y = -n (bottom)
			unit_vector = unitVector(lng[indexLng + i], lat[indexLat - n], TxLng, TxLat)
			RxLng = lng[indexLng+i]
			RxLat = lat[indexLat-n]
			elevation = int(elevations[indexLng+i][indexLat-n])
			cur_dist = distance(TxLng, TxLat, RxLng, RxLat)
			if unit_vector not in udict:
				udict[unit_vector] = []
			udict[unit_vector].append((elevation, cur_dist))

		for j in np.linspace(-n, n, (2*n)+1):
			j = int(j)

			# x = n (right)
			unit_vector = unitVector(lng[indexLng + n], lat[indexLat + j], TxLng, TxLat)
			RxLng = lng[indexLng+n]
			RxLat = lat[indexLat+j]
			elevation = int(elevations[indexLng+n][indexLat+j])
			cur_dist = distance(TxLng, TxLat, RxLng, RxLat)
			if unit_vector not in udict:
				udict[unit_vector] = []
			udict[unit_vector].append((elevation, cur_dist))

			# x = -n (left)
			unit_vector = unitVector(lng[indexLng - n], lat[indexLat + j], TxLng, TxLat)
			RxLng = lng[indexLng-n]
			RxLat = lat[indexLat+j]
			elevation = int(elevations[indexLng-n][indexLat+j])
			cur_dist = distance(TxLng, TxLat, RxLng, RxLat)
			if unit_vector not in udict:
				udict[unit_vector] = []
			udict[unit_vector].append((elevation, cur_dist))
	
	elevation_count = 0
	peak_count = 0
	k = 0
	for unit_vector, elevations_distances in udict.items():
		udict[unit_vector] = sorted(elevations_distances, key=lambda x: x[1])
		elevations, distances = zip(*udict[unit_vector])
		elevations = np.array(elevations)
		peak_indices = argrelextrema(elevations, np.greater)[0]
		peak_dict[unit_vector] = peak_indices
		peak_count += len(peak_indices)
		elevation_count += len(elevations)

	return 0

def buildMap_trivial(size, lng, lat, indexLng, indexLat, TxLng, TxLat, elevations, frequency):
	# combines elevationGrid and FSPLGrid for efficiency and builds map in radial squares
	# where unit vector build is currently taking place

	# temporary check for odd size
	count = 0
	if (size%2) == 0:
		size += 1

	origin = size//2

	# build and initialize map
	elevation_grid = buildGrid(size)
	power_grid = buildGrid(size)
	power_grid[0][0] = np.inf # Ask latter
	TxElevation = elevations[indexLng][indexLat]
	elevations[0][0] = TxElevation # Ask latter

	TxLng = float(TxLng)
	TxLat = float(TxLat)

	# FSPL estimation
	FSPL_list = FSPL(indexLng, indexLat, size, lng, lat, TxLng, TxLat, frequency)

	# collect unit vectors
	udict = {}
	peak_dict = {}

	buff = 1 # 1m buffer

	# fill in map
	for n in range(origin):
		n = n + 1

		for i in np.linspace(-n+1, n-1, (2*n)-1):
			i = int(i)

			# y = i (top)
			unit_vector = unitVector(lng[indexLng+i], lat[indexLat+n], TxLng, TxLat)
			elevation = int(elevations[indexLng+i][indexLat+n])
			elevation_grid[i+origin][n+origin] = elevation
			loss = terrainLoss_trivial(udict, unit_vector, elevation, TxElevation, buff)
			power_grid[i+origin][n+origin] = FSPL_list[n-1] + loss

			# y = -i (bottom)
			unit_vector = unitVector(lng[indexLng+i], lat[indexLat-n], TxLng, TxLat)
			elevation = int(elevations[indexLng+i][indexLat-n])
			elevation_grid[i+origin][-n+origin] = elevation
			loss = terrainLoss_trivial(udict, unit_vector, elevation, TxElevation, buff)
			power_grid[i+origin][-n+origin] = FSPL_list[n-1] + loss

		for j in np.linspace(-n, n, (2*n)+1):
			j = int(j)

			# x = i (right)
			unit_vector = unitVector(lng[indexLng+n], lat[indexLat+j], TxLng, TxLat)
			elevation = int(elevations[indexLng+n][indexLat+j])
			elevation_grid[n+origin][j+origin] = elevation
			loss = terrainLoss_trivial(udict, unit_vector, elevation, TxElevation, buff)
			power_grid[n+origin][j+origin] = FSPL_list[n-1] + loss

			# x = -i (left)
			unit_vector = unitVector(lng[indexLng-n], lat[indexLat+j], TxLng, TxLat)
			elevation = int(elevations[indexLng-n][indexLat+j])
			elevation_grid[-n+origin][j+origin] = elevation
			loss = terrainLoss_trivial(udict, unit_vector, elevation, TxElevation, buff)
			power_grid[-n+origin][j+origin] = FSPL_list[n-1] + loss
			
	return elevation_grid, power_grid

def buildMap_physics(size, lng, lat, indexLng, indexLat, TxLng, TxLat, elevations, frequency):
	# combines elevationGrid and FSPLGrid for efficiency and builds map in radial squares
	# where unit vector build is currently taking place

	# temporary check for odd size
	count = 0
	if (size%2) == 0:
		size += 1

	origin = size//2

	# build and initialize map
	elevation_grid = buildGrid(size)
	power_grid = buildGrid(size)
	power_grid[0][0] = np.inf
	TxElevation = elevations[indexLng][indexLat]
	elevations[0][0] = TxElevation

	TxLng = float(TxLng)
	TxLat = float(TxLat)

	# FSPL estimation
	FSPL_list = FSPL(indexLng, indexLat, size, lng, lat, TxLng, TxLat, frequency)

	# collect unit vectors
	udict = {}
	peak_dict = {}

	buff = 1 # 1m buffer

	preComputePeaks(udict, peak_dict, indexLat, indexLng, TxLng, TxLat, lng, lat, origin, elevations)


	# fill in map
	for n in range(origin):
		n = n + 1

		for i in np.linspace(-n+1, n-1, (2*n)-1):
			i = int(i)

			# y = i (top)
			unit_vector = unitVector(lng[indexLng+i], lat[indexLat+n], TxLng, TxLat)
			RxLng = lng[indexLng+i]
			RxLat = lat[indexLat+n]
			elevation = int(elevations[indexLng+i][indexLat+n])
			elevation_grid[i+origin][n+origin] = elevation
			loss = terrainLoss_physics(udict, peak_dict, unit_vector, elevation, TxElevation, buff, TxLng, TxLat, RxLng, RxLat)
			power_grid[i+origin][n+origin] = FSPL_list[n-1] + loss
			
			
			# y = -i (bottom)
			unit_vector = unitVector(lng[indexLng+i], lat[indexLat-n], TxLng, TxLat)
			RxLng = lng[indexLng+i]
			RxLat = lat[indexLat-n]
			elevation = int(elevations[indexLng+i][indexLat-n])
			elevation_grid[i+origin][-n+origin] = elevation
			loss = terrainLoss_physics(udict, peak_dict, unit_vector, elevation, TxElevation, buff, TxLng, TxLat, RxLng, RxLat)
			power_grid[i+origin][-n+origin] = FSPL_list[n-1] + loss
			
		for j in np.linspace(-n, n, (2*n)+1):
			j = int(j)

			# x = i (right)
			unit_vector = unitVector(lng[indexLng+n], lat[indexLat+j], TxLng, TxLat)
			RxLng = lng[indexLng+n]
			RxLat = lat[indexLat+j]
			elevation = int(elevations[indexLng+n][indexLat+j])
			elevation_grid[n+origin][j+origin] = elevation
			loss = terrainLoss_physics(udict, peak_dict, unit_vector, elevation, TxElevation, buff, TxLng, TxLat, RxLng, RxLat)
			power_grid[n+origin][j+origin] = FSPL_list[n-1] + loss

			# x = -i (left)
			unit_vector = unitVector(lng[indexLng-n], lat[indexLat+j], TxLng, TxLat)
			RxLng = lng[indexLng-n]
			RxLat = lat[indexLat+j]
			elevation = int(elevations[indexLng-n][indexLat+j])
			elevation_grid[-n+origin][j+origin] = elevation
			loss = terrainLoss_physics(udict, peak_dict, unit_vector, elevation, TxElevation, buff, TxLng, TxLat, RxLng, RxLat)
			power_grid[-n+origin][j+origin] = FSPL_list[n-1] + loss
			
			
	return elevation_grid, power_grid

def createPathElevation(targetLng, targetLat, sourceLng, sourceLat, lng, lat, elevations, exact):
	targetLngIndex = find_nearest_index(lng, targetLng)
	targetLatIndex = find_nearest_index(lat, targetLat)

	sourceLngIndex = find_nearest_index(lng, sourceLng)
	sourceLatIndex = find_nearest_index(lat, sourceLat)

	pathElevation = []
	distances = []
	currLat = sourceLatIndex
	currLong = sourceLngIndex
	dist = 0

	while (currLat != targetLatIndex or currLong != targetLngIndex):
		
		pathElevation.append(elevations[currLong][currLat])

		if exact:
			delta_lon, delta_lat = getNextMove_ExactPath(currLat, currLong, targetLatIndex, targetLngIndex)
		else:
			delta_lon, delta_lat = getNextMove(currLat, currLong, targetLatIndex, targetLngIndex)

		dist += distance(lng[currLong], lat[currLat], lng[currLong + delta_lon], lat[currLat + delta_lat])
		distances.append(dist)

		currLat += delta_lat
		currLong += delta_lon
	
	return pathElevation, distances

def getSlope(current_lat, current_lon, target_lat, target_lon):
	if current_lon == target_lon:
		return np.inf
	return (current_lat - target_lat) / (current_lon - target_lon)

def getNextMove_ExactPath(current_lat, current_lon, target_lat, target_lon):
	lat_to_go = target_lat - current_lat
	lon_to_go = target_lon - current_lon

	divider = math.gcd(lat_to_go, lon_to_go)

	return int(lon_to_go / divider), int(lat_to_go / divider)

def getNextMove_old(current_lat, current_lon, target_lat, target_lon):
	slope = getSlope(current_lat, current_lon, target_lat, target_lon)
	if current_lat == target_lat and current_lon == target_lon:
		return 0,0

	if slope == np.inf:
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
			return 1,-1
		if slope >= 0.4 and slope < 0.7:
			return 2,1
		if slope >= -0.7 and slope < -0.4:
			return 2,-1
		if slope >= 1.5 and slope < 2.6:
			return 1,2
		if slope >= -2.6 and slope < -1.5:
			return 1,-2
		if slope >= 0 and slope < 0.4:
			return 3,1
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

def getNextMove(current_lat, current_lon, target_lat, target_lon):
	slope = getSlope(current_lat, current_lon, target_lat, target_lon)

	if slope == np.inf:
		if target_lat > current_lat:
			return 0,1
		else:
			return 0,-1

	if target_lon > current_lon:
		if slope <= 0.5:
			return 1,0
		if slope > 0.5 and slope < 2.2:
			return 1,1
		if slope >= 2.2:
			return 0,1
		if slope >= -2.2 and slope < -0.7:
			return 1,-1
	else:
		if slope == 0:
			return -1,-0
		if slope >= 0.7 and slope < 2.2:
			return -1,-1
		if slope >= -1.5 and slope < -0.7:
			return -1,1

	#Edge Case where the slope is near np.inf but not equal to
	if target_lat > current_lat:
		return 0,1
	else:
		return 0,-1

def find_nearest_index(array, value):
	array = np.asarray(array)
	return (np.abs(array - value)).argmin()

def buildMap_universal(model, size, lng, lat, indexLng, indexLat, TxLng, TxLat, elevations, frequency):
	
	# temporary check for odd size
	count = 0
	if (size%2) == 0:
		size += 1

	origin = size//2

	# build and initialize map
	elevation_grid = buildGrid(size)
	power_grid = buildGrid(size)
	power_grid[0][0] = np.inf
	TxElevation = elevations[indexLng][indexLat]
	elevations[0][0] = TxElevation

	TxLng = float(TxLng)
	TxLat = float(TxLat)

	# FSPL estimation
	FSPL_list = FSPL(indexLng, indexLat, size, lng, lat, TxLng, TxLat, frequency)

	# collect unit vectors
	udict = {}
	peak_dict = {}
	unit_vector = 0
	path = 0

	buff = 1 # 1m buffer

	# save runtime for trivial mapbuild
	if model == "physics":
		preComputePeaks(udict, peak_dict, indexLat, indexLng, TxLng, TxLat, lng, lat, origin, elevations)


	# fill in map
	for n in range(origin):
		n = n + 1

		for i in np.linspace(-n+1, n-1, (2*n)-1):
			i = int(i)

			# y = i (top)
			RxLng = lng[indexLng+i]
			RxLat = lat[indexLat+n]
			if model != "trivial" and model != "physics":
				path = createPathElevation(RxLng, RxLat, TxLng, TxLat, lng, lat, elevations, False)
			else:
				unit_vector = unitVector(RxLng, RxLat, TxLng, TxLat)
			elevation = int(elevations[indexLng+i][indexLat+n])
			elevation_grid[i+origin][n+origin] = elevation
			loss = terrainLoss_universal(model,udict, peak_dict, unit_vector, path, elevation, TxElevation, buff, TxLng, TxLat, RxLng, RxLat)
			power_grid[i+origin][n+origin] = FSPL_list[n-1] + loss
			
			# y = -i (bottom)
			RxLng = lng[indexLng+i]
			RxLat = lat[indexLat-n]
			if model != "trivial" and model != "physics":
				path = createPathElevation(RxLng, RxLat, TxLng, TxLat, lng, lat, elevations, False)
			else:
				unit_vector = unitVector(RxLng, RxLat, TxLng, TxLat)
			elevation = int(elevations[indexLng+i][indexLat-n])
			elevation_grid[i+origin][-n+origin] = elevation
			loss = terrainLoss_universal(model,udict, peak_dict, unit_vector, path, elevation, TxElevation, buff, TxLng, TxLat, RxLng, RxLat)
			power_grid[i+origin][-n+origin] = FSPL_list[n-1] + loss
			
		for j in np.linspace(-n, n, (2*n)+1):
			j = int(j)

			# x = i (right)
			if model != "trivial" and model != "physics":
				path = createPathElevation(RxLng, RxLat, TxLng, TxLat, lng, lat, elevations, False)
			else:
				unit_vector = unitVector(RxLng, RxLat, TxLng, TxLat)
			elevation = int(elevations[indexLng+n][indexLat+j])
			elevation_grid[n+origin][j+origin] = elevation
			loss = terrainLoss_universal(model,udict, peak_dict, unit_vector, path, elevation, TxElevation, buff, TxLng, TxLat, RxLng, RxLat)
			power_grid[n+origin][j+origin] = FSPL_list[n-1] + loss

			# x = -i (left)
			RxLng = lng[indexLng-n]
			RxLat = lat[indexLat+j]
			if model != "trivial" and model != "physics":
				path = createPathElevation(RxLng, RxLat, TxLng, TxLat, lng, lat, elevations, False)
			else:
				unit_vector = unitVector(lng[indexLng-n], lat[indexLat+j], TxLng, TxLat)
			elevation = int(elevations[indexLng-n][indexLat+j])
			elevation_grid[-n+origin][j+origin] = elevation
			loss = terrainLoss_universal(model,udict, peak_dict, unit_vector, path, elevation, TxElevation, buff, TxLng, TxLat, RxLng, RxLat)
			power_grid[-n+origin][j+origin] = FSPL_list[n-1] + loss
	
	return elevation_grid, power_grid

def terrainLoss_universal(model, udict, peak_dict, unit_vector, path, elevation, TxElevation, buff, TxLng, TxLat, RxLng, RxLat):
	
	if model == "trivial":
		return terrainLoss_trivial(udict, unit_vector, elevation, TxElevation, buff)
	
	elif model == "physics":
		return terrainLoss_physics(udict, peak_dict, unit_vector, elevation, TxElevation, buff, TxLng, TxLat, RxLng, RxLat)

	else:
		return 0