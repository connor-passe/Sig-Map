'''
This script loads the UK datasets
'''

import constants
import csv
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator
import numpy as np

city_to_csv = {
	constants.BOSTON : 'UKDataset/boston{}.csv',
	constants.MERTHYR : 'UKDataset/merthyr{}.csv',
	constants.LONDON : 'UKDataset/london{}.csv',
	constants.NOTTINGHAM : 'UKDataset/nottingham{}.csv',
	constants.SCARHILL : 'UKDataset/scarhill{}.csv',
	constants.SOUTHHAMPTON : 'UKDataset/southampton{}.csv',
	constants.STEVENAGE : 'UKDataset/stevenage{}.csv'
}

def load(city_id, frequency, plot = 0):
	# load data
	f = open(city_to_csv.get(city_id).format(frequency), 'r')
	reader = csv.reader(f)

	info = []
	for row in reader:
		info.append(row)

	# city = info[0]

	# parse data
	TxLat = info[1][0].split(' ')[-2]
	TxLon = info[2][0].split(' ')[-2]
	frequency = info[3][0].split(' ')[-2]
	TxHeight = info[4][0].split(' ')[-2]
	TxPower = float(info[5][0].split(' ')[-2])
	RxHeight = info[6][0].split(' ')[-2]
	noiseFloor = info[7][0].split(' ')[-2]

	xCoord = []
	yCoord = []
	power = []


	for i in range(len(info)-10):
		
		# lat
		xCoord.append(float(info[i+10][2]))

		# lng
		yCoord.append(float(info[i+10][3]))

		power.append(float(info[i+10][4]))
	
	# Plot with flag
	if plot == 1:
		fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
		surf = ax.plot_trisurf(np.array(xCoord), np.array(yCoord), np.array(power), cmap=cm.jet, linewidth=0.01)
		plt.show()

	return TxHeight, RxHeight, TxLat, TxLon, TxPower, xCoord, yCoord, power

