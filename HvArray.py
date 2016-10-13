import sys
import numpy as np
import scipy
from ROOT import TVector2
from datetime import datetime
import logging
import root_numpy as rnp

logging.basicConfig(level=logging.INFO)

def loader(loadChoice):
	# Signal
	sigFilePath = "/phys/groups/tev/scratch3/users/HV/WHHV/ntup_001"
	sigFileName = "ntup_aod_*"
	sigFiles    = "{0}/{1}".format(sigFilePath, sigFileName)

	# Background
	bkgFolderName = "mc12_8TeV.147912.Pythia8_AU2CT10_jetjet_JZ2W.merge.NTUP_COMMON.e1126_s1469_s1470_r6262_p1575_tid05435083_00"
	bkgFilePath   = "/phys/groups/tev/scratch4/users/gwatts/GRIDDS/{0}/{0}".format(bkgFolderName)
	bkgFileName   = "NTUP_COMMON.05435083._*"
	bkgFiles      = "{0}/{1}".format(bkgFilePath, bkgFileName)

	# Variables
	emFrac = "jet_AntiKt4LCTopo_emfrac"

	trkPt  = "trk_pt"
	jetPt  = "jet_AntiKt4LCTopo_pt"

	trkPhi = "trk_phi_wrtPV"
	jetPhi = "jet_AntiKt4LCTopo_phi"

	trkEta = "trk_eta"
	jetEta = "jet_AntiKt4LCTopo_eta"

	pdgId  = "mc_pdgId" #7
	vx_x   = "mc_vx_x" #8
	vx_y   = "mc_vx_y" #9
	child  = "mc_child_index" #10
	mc_eta = "mc_eta" #11
	mc_phi = "mc_phi" #12

	branchNames = [emFrac, trkPt, trkPhi, jetPhi, trkEta, jetEta, jetPt, pdgId, vx_x, vx_y,child,mc_eta,mc_phi]

	# Setup Arrays
	logging.info("Loading TFiles into Numpy Array")

	if loadChoice.lower() == "signal":
		sigArray = rnp.root2array( sigFiles, "physics", branchNames)
		return sigArray
	elif loadChoice.lower() == "background":
		bkgArray = rnp.root2array( bkgFiles, "physics", branchNames)
		return bkgArray
	else:
		print "No data type given, specify 'signal' or 'background' in arguments"
		sys.exit()


def make_training_array(rootData,checker):
	# Data Variable order: 0-emFrac 1-trkPt 2-trkPhi 3-jetPhi 4-trkEta 5-jetEta 6-jetPt
	logging.info('Beginning Hidden Valley array processing')
	starttime = datetime.now()
	#rootData    = loader("signal")
	#dt= np.dtype([('0',np.float64),('1',np.float64),('2',np.float64),('3',np.float64),('4',np.float64)])
	outputArray = []
			#{'names':['f0','f1','f2','f3','f4'], 'formats':[np.float64,np.float64,np.float64,np.float64,np.float64]})

	eventCounter = 0

	while (eventCounter < len(rootData)):
		lenJet   = len( rootData[eventCounter][0] )
		lenTrack = len( rootData[eventCounter][2] )
		jetCounter = 1
		if (eventCounter%500 == 0):
					logging.warning('Event Number: {0}'.format(eventCounter))
		if lenJet > 0:
			for n in range(0,lenJet):
				jetPrimer = [] #temp array for loop

				# Define variables
				emFrac = rootData[eventCounter][0][n]
				jetPt  = rootData[eventCounter][6][n]
				jetEta = rootData[eventCounter][5][n]
				jetPhi = rootData[eventCounter][3][n]
				pdgId  = rootData[eventCounter][7]
				vx_x   = rootData[eventCounter][8]
				vx_y   =rootData[eventCounter][9]
				child = rootData[eventCounter][10]
				mc_eta = rootData[eventCounter][11]
				mc_phi = rootData[eventCounter][12]


				# Calculate new variables
				calRatio = calculate_calratio(emFrac)
				trkCount = count_track(rootData[eventCounter], lenTrack, jetPhi, jetEta)

				## COMMENT THIS OUT IF YOU ARE DOING BACKGROUND
				if (checker == "signal"):

					Lxy = radius_check(rootData[eventCounter], jetPhi,jetEta)

					if (Lxy == False):
						pass

					else:
						jetPrimer = [eventCounter, jetCounter, jetPt, calRatio, trkCount, Lxy, deltaPhi, deltaEta, deltaR]
						outputArray.append(jetPrimer)



				elif(checker == "background") :
					jetPrimer = [eventCounter, jetCounter, jetPt, calRatio, trkCount]
					outputArray.append(jetPrimer)
				else:
					print "Not a valid option."
					sys.exit()

				'''if(eventCounter%1000 == 0):
					logging.info(eventCounter)'''

				jetCounter += 1
		else:
			logging.warning(" No Jets in event ")
		eventCounter += 1
	logging.info("Hidden Valley Data Processing Complete")
	#print("Array before conversion")
	outputArray = np.array(outputArray)
	#print(outputArray)

	#outputArray = np.delete(outputArray, 0, 0)
#converting list of list to list of tuples
	outputConversion=[(c[0],c[1],c[2],c[3],c[4],c[5],c[6],c[7],c[8]) for c in outputArray]
	outputArray2=np.array(outputConversion, dtype=[("Event_Num",np.float64),("Jet_Num", np.float64),("Jet_Pt",np.float64),("Cal_Ratio",np.float64),("Track_Count",np.float64),("Distance",np.float64),("Delta_Phi",np.float64),("Delta_Eta",np.float64),("Delta_R",np.float64)])

	print 'It took {0} to run'.format(datetime.now() - starttime)
	return outputArray2


def count_track(rootDataEvent, lenTrack, jetPhi, jetEta):
	trkCount = 0
	#logging.debug('Track Length:{0}, trkPhi Length: {1}, trkEta Length: {2}'.format(lenTrack, len(rootDataEvent[2]), len(rootDataEvent[4])))
	for m in range(0, lenTrack):
		trkPhi = rootDataEvent[2][m]
		trkEta = rootDataEvent[4][m]

		#logging.debug('iteration {0}, trkPhi is {1}, trkEta is {2}'.format(m, trkPhi, trkEta))

		deltaPhi = TVector2.Phi_mpi_pi(trkPhi-jetPhi)
		deltaEta = trkEta - jetEta
		deltaR   = deltaPhi**2 + deltaEta**2

		if (deltaR <= .04):
			trkPt = rootDataEvent[1][m] / 1000
			if (trkPt >= 1):
				trkCount += 1
	return trkCount


def calculate_calratio(emFrac):
	calRatio = 0
	if(emFrac>= 1 ):
		calRatio = 0
	elif(emFrac <= 0):
		calRatio  = 20
	else:
		energyRatio = ((1-emFrac) / emFrac)
		calRatio = np.log10(energyRatio)

	return calRatio

def radius_check(rootData, jetPhi,jetEta):
	global deltaR
	global deltaPhi
	global deltaEta
	pdgId = rootData[7]
	vx_x = rootData[8]
	vx_y =rootData[9]
	child = rootData[10]
	mc_eta = rootData[11]
	mc_phi = rootData[12]
	minDeltaR = 1000
	minIndex=-1
	startx=0
	starty=0
	for particles in range(0,len(pdgId)):
		if (pdgId[particles]==36):
			logging.debug("Pion Found!")
			if (len(child[particles])!= 0):
				logging.debug("Has Children")
				deltaPhi = TVector2.Phi_mpi_pi(mc_phi[particles] - jetPhi)
				deltaEta = mc_eta[particles] - jetEta
				deltaR = deltaPhi**2 + deltaEta**2
				if(deltaR<.2 and deltaR < minDeltaR):
					minDeltaR = deltaR
					minIndex = particles
					startx = vx_x[particles]
					starty = vx_y[particles]

	logging.debug("The min index is: {0}".format(minIndex))
	if (minIndex == -1):
		logging.debug("No Higgs correlation")
		return False
	else:
		refnum = child[minIndex][0]
		vxx = vx_x[refnum]
		vxy = vx_y[refnum]
		dX = vxx - startx
		dY = vxy - starty
		distance = (dX**2 + dY**2)**.5
		logging.debug(distance)
		#print ("The vx_x = {0} | the vx_y = {1} | The radius is: {2}".format(vxx, vxy, radius))

		if (2000 < distance):
			logging.debug("***********************************************Inside Calorimeter")
			return distance
		else:
			logging.debug("Outside Calorimeter")
			return False

def save_array(outputArray, outputName):
	#array = np.savetxt(outputName+".txt", outputArray, fmt='%.4e',delimiter = "|")
	outputString = str(outputName)
	logging.info("Creating .Root file")
	rnp.array2root(outputArray,outputString,treename='Training_Variables',mode='recreate')
