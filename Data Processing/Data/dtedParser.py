'''
This script gives lat, lng, and elevation data for Boston, UK
'''
import constants
import matplotlib.pyplot as plt
import numpy as np
from dted import Tile

town_to_tiles = {
	constants.BOSTON : [["dted/UK/Boston/n53_w001_1arc_v3.dt2", "dted/UK/Boston/n53_e000_1arc_v3.dt2"], ["dted/UK/Boston/n52_w001_1arc_v3.dt2", "dted/UK/Boston/n52_e000_1arc_v3.dt2"]],
	constants.LONDON : [["dted/UK/London/n51_w001_1arc_v3.dt2", "dted/UK/London/n51_e000_1arc_v3.dt2"]],
	constants.MERTHYR : [["dted/UK/MerthyrTydfil/n52_w005_1arc_v3.dt2", "dted/UK/MerthyrTydfil/n52_w004_1arc_v3.dt2"], ["dted/UK/MerthyrTydfil/n51_w005_1arc_v3.dt2", "dted/UK/MerthyrTydfil/n51_w004_1arc_v3.dt2"]],
	constants.NOTTINGHAM : [["dted/UK/Nottingham/n53_w002_1arc_v3.dt2", "dted/UK/Nottingham/n53_w001_1arc_v3.dt2"], ["dted/UK/Nottingham/n52_w002_1arc_v3.dt2", "dted/UK/Nottingham/n52_w001_1arc_v3.dt2"]],
	constants.SCARHILL : [["dted/UK/ScarHill/n57_w004_1arc_v3.dt2", "dted/UK/ScarHill/n57_w003_1arc_v3.dt2"], ["dted/UK/ScarHill/n56_w004_1arc_v3.dt2", "dted/UK/ScarHill/n56_w003_1arc_v3.dt2"]],
	constants.SOUTHHAMPTON : [["dted/UK/SouthHampton/n51_w002_1arc_v3.dt2", "dted/UK/SouthHampton/n51_w001_1arc_v3.dt2"], ["dted/UK/SouthHampton/n50_w002_1arc_v3.dt2", "dted/UK/SouthHampton/n50_w001_1arc_v3.dt2"]],
	constants.STEVENAGE : [["dted/UK/Stevenage/n52_w001_1arc_v3.dt2", "dted/UK/Stevenage/n52_e000_1arc_v3.dt2"], ["dted/UK/Stevenage/n51_w001_1arc_v3.dt2", "dted/UK/Stevenage/n51_e000_1arc_v3.dt2"]]
}

town_to_coordinates = {
	constants.BOSTON : [[-1, 1], [52, 54]],
	constants.LONDON : [[-1, 1], [51, 52]],
	constants.MERTHYR : [[-5, -3], [51, 53]],
	constants.NOTTINGHAM : [[-2, 0], [52, 54]],
	constants.SCARHILL : [[-4, -2], [56, 58]],
	constants.SOUTHHAMPTON : [[-2, 0], [50, 52]],
	constants.STEVENAGE : [[-1, 1], [51, 53]]
}

def get_dted(city_id, plot = 0):
	tiles = town_to_tiles.get(city_id)
	coordinates = town_to_coordinates.get(city_id)

	for i in range(len(tiles)):
		for j in range(len(tiles[0])):
			tiles[i][j] = Tile(tiles[i][j]).data

	for row in range(len(tiles)):
		tiles[row] = np.concatenate(tiles[row], axis = 0)

	elevations = []
	for i in range(len(tiles[0])):
		temp = []
		for j in range(len(tiles)):
			temp.append(tiles[len(tiles) - 1 - j][i])
		elevations.append(np.concatenate(temp, axis=0))


	lng = np.linspace(coordinates[0][0], coordinates[0][1], num = len(elevations), endpoint = False)
	lat = np.linspace(coordinates[1][0],coordinates[1][1], num = len(elevations[0]), endpoint = False)

	if plot == 1:
		# plot
		latMesh, lngMesh = np.meshgrid(lat, lng)
		fig, ax = plt.subplots(figsize=(3*(coordinates[0][1] - coordinates[0][0]), 4* (coordinates[1][1] - coordinates[1][0])))
		c = plt.pcolormesh(lngMesh, latMesh, np.array(elevations), shading = 'auto')
		fig.colorbar(c)
		plt.show()

	return lng, lat, elevations