import sys, os, os.path
import datetime, time

from array import array

import logging
import ROOT
from ROOT import gSystem, gROOT, gApplication, TMVA, TFile, TTree, TChain, TCut, TH1D, TBranch, TCanvas


#=======================================================================================#
st = time.time()

#=== User Defined Variables
methods = ["BDT_A", "BDT_B", "LikelihoodA", "LikelihoodB", "MLP"]
varName	= [
	"Track_Count",
	"Cal_Ratio",
	"Jet_Pt",
	"Event_Num",
	"Jet_Num",
	"Distance",
	"Delta_Phi",
	"Delta_Eta",
	"Delta_R",
	"ClassID"]

dataSetFolder = "TMVA_Inputs"
dataPath      = "/phys/groups/tev/scratch4/users/tommeyer/HiddenValley"
#- Test Data Name
sigFileName   = "testingsignalII.root"
bkgFileName   = "testingbkg.root"
#- Test Tree Name
inTreeName    = "Training_Variables"
#- Name of folder containing xml file
weightFolder  = "2016-05-02"
#-Output Names
outfolderName = "Hv_NeuralNet"
outFilename   = "HvReader_MLP_Test.root"
outTreename   = "NN"
#=======================================================================================#

#=== Variables
#=============
outFile = None
outTree = None
#|- Pointers (For setting branches)
pointer_trkCnt  = array('f', [0]) #- 0 | #-Trained
pointer_calR    = array('f', [0]) #- 1 | #-Trained
pointer_JetpT   = array('f', [0]) #- 2 | #-Trained
pointerS_evntN  = array('f', [0]) #- 3 | #-Spectator
pointerS_jetN   = array('f', [0]) #- 4 | #-Spectator
pointerE_Dist   = array('f', [0]) #- 5 | #-Extra
pointerE_delPhi = array('f', [0]) #- 6 | #-Extra
pointerE_delEta = array('f', [0]) #- 7 | #-Extra
pointerE_DelR   = array('f', [0]) #- 8 | #-Extra
classID         = array('f', [0]) #- 9 | #-Signal(0)/ Background(1)
#|-
nVar      = len(varName)
nTrainVar = 3
nSpecVar  = 2

###############
#|- Input Data
sig_filepath = "{0}/{1}/{2}".format( dataPath, dataSetFolder, sigFileName )
bkg_filepath = "{0}/{1}/{2}".format( dataPath, dataSetFolder, bkgFileName )
sigFile      = TFile.Open( sig_filepath )22
sigTree      = sigFile.Get( inTreeName )
bkgTree      = bkgFile.Get( inTreeName )
#|- Event Loop
reader       = TMVA.Reader( "V:Color:!Silent" ) # TMVA Reader
nSigEvents   = sigTree.GetEntries()
nBkgEvents   = bkgTree.GetEntries()
#|- Method: Pointers
mA_SigOut   = array('f', [0]) # Store Meth1 Sig Eval
mA_BkgOut   = array('f', [0]) # Store Meth1 Bkg Eval
mB_SigOut   = array('f', [0]) # Store Meth2 Sig Eval
mB_BkgOut   = array('f', [0]) # Store Meth2 Bkg Eval
mC_SigOut   = array('f', [0]) # Store Meth3 Sig Eval
mC_BkgOut   = array('f', [0]) # Store Meth3 Bkg Eval
mD_SigOut   = array('f', [0]) # Store Meth4 Sig Eval
mD_BkgOut   = array('f', [0]) # Store Meth4 Bkg Eval
#|- Method Histograms
hmA_Sig      = None
hmA_Bkg      = None
hmB_Sig		 = None
hmB_Bkg		 = None
hmC_Sig      = None
hmC_Bkg      = None
hmD_Sig		 = None
hmD_Bkg		 = None
#|- Output Data
#|- Run time
deltaT       = None # Time for run
#===

logging.basicConfig(level=logging.DEBUG)

gROOT.SetMacroPath( "$ROOTSYS/tmva/test/" )
gROOT.Macro       ( "./TMVAlogon.C"       )
gROOT.LoadMacro   ( "./TMVAGui.C"         )

#========================#
def outputFolder():
	outputPath  = "/{0}/Output/{1}/".format(dataPath, outfolderName)
	try:
		os.mkdir(outputPath)
	except OSError:
		if not os.path.isdir(outputPath):
			raise
	os.chdir(outputPath)
#========================#

###########
# Prepare #
###########

def prepare_reader():
	reader.AddVariable(varName[0], pointer_trkCnt )
	reader.AddVariable(varName[1], pointer_calR   )
	reader.AddVariable(varName[2], pointer_JetpT  )

	reader.AddSpectator(varName[3], pointerS_evntN )
	reader.AddSpectator(varName[4], pointerS_jetN  )
	logging.info(" #|---Reader Variables Set---|#")

# Loads signal and background file
def loadTestData():
	logging.info(" #|---Number of Variables:   {0}".format(nVar) )
	logging.info(" #|---Number of Sig Entries: {0}".format(nSigEvents) )
	logging.info(" #|---Number of Bkg Entries: {0}".format(nBkgEvents) )

	#sigTree.SetBranchAddress( varName[0], pointer_trkCnt )
	#sigTree.SetBranchAddress( varName[1], pointer_calR   )
	#sigTree.SetBranchAddress( varName[2], pointer_JetpT  )
	#sigTree.SetBranchAddress( varName[3], pointerS_evntN )
	#sigTree.SetBranchAddress( varName[4], pointerS_jetN  )
	#sigTree.SetBranchAddress( varName[5], pointerE_Dist)
	#sigTree.SetBranchAddress( varName[6], pointerE_delPhi)
	#sigTree.SetBranchAddress( varName[7], pointerE_delEta)
	#sigTree.SetBranchAddress( varName[8], pointerE_DelR)

	#sigTree.Scan("*")
#	#bkgTree.SetBranchAddress( varName[0], pointer_trkCnt )
#	#bkgTree.SetBranchAddress( varName[1], pointer_calR   )F
#	#bkgTree.SetBranchAddress( varName[2], pointer_JetpT  )
#	#bkgTree.SetBranchAddress( varName[3], pointerS_evntN )
	#bkgTree.SetBranchAddress( varName[4], pointerS_jetN  )

def prepareOutput():

	global outFile ; global outTree
	outFile = TFile( outFilename, "Recreate" )
	outTree = TTree( outTreename, "Output of MLP Evaluation" )
	logging.info( " #|---Output File: {0}".format(outFilename) )

	outTree.Branch( "mA_Sig" , mA_SigOut , "{0}/F".format( "mA_Sig" ))
	outTree.Branch( "mA_Bkg" , mA_BkgOut , "{0}/F".format( "mA_Bkg" ))

	outTree.Branch( "mB_Sig" , mB_SigOut , "{0}/F".format( "mB_Sig" ))
	outTree.Branch( "mB_Bkg" , mB_BkgOut , "{0}/F".format( "mB_Bkg" ))

	outTree.Branch( "mC_Sig" , mC_SigOut , "{0}/F".format( "mC_Sig" ))
	outTree.Branch( "mC_Bkg" , mC_BkgOut , "{0}/F".format( "mC_Bkg" ))

	outTree.Branch( "mD_Sig" , mD_SigOut , "{0}/F".format( "mD_Sig" ))
	outTree.Branch( "mD_Bkg" , mD_BkgOut , "{0}/F".format( "mD_Bkg" ))

	outTree.Branch( varName[0], pointer_trkCnt  , "{0}/F".format( varName[0] ))
	outTree.Branch( varName[1], pointer_calR    , "{0}/F".format( varName[1] ))
	outTree.Branch( varName[2], pointer_JetpT   , "{0}/F".format( varName[2] ))
	outTree.Branch( varName[3], pointerS_evntN  , "{0}/F".format( varName[3] ))
	outTree.Branch( varName[4], pointerS_jetN   , "{0}/F".format( varName[4] ))
	outTree.Branch( varName[5], pointerE_Dist   , "{0}/F".format( varName[5] ))
	outTree.Branch( varName[6], pointerE_delPhi , "{0}/F".format( varName[6] ))
	outTree.Branch( varName[7], pointerE_delEta , "{0}/F".format( varName[7] ))
	outTree.Branch( varName[8], pointerE_DelR   , "{0}/F".format( varName[8] ))
	outTree.Branch( varName[9], classID         , "{0}/F".format( varName[9] ))
	print outTree
	
	global hmA_Sig ; global hmA_Bkg
	hmA_Sig = TH1D("hmA_Sig", "{0}".format(methods[0]), 100, -10., 10. )
	hmA_Bkg = TH1D("hmA_Bkg", "{0}".format(methods[0]), 100, -10., 10. )
	
	global hmB_Sig ; global hmB_Bkg
	hmB_Sig = TH1D("hmB_Sig", "{0}".format(methods[1]), 100, -10., 10. )
	hmB_Bkg = TH1D("hmB_Bkg", "{0}".format(methods[1]), 100, -10., 10. )

	global hmC_Sig ; global hmC_Bkg	
	hmC_Sig = TH1D("hmC_Sig", "{0}".format(methods[2]), 100, -10., 10. )
	hmC_Bkg = TH1D("hmC_Bkg", "{0}".format(methods[2]), 100, -10., 10. )
	
	global hmD_Sig ; global hmD_Bkg
	hmD_Sig = TH1D("hmD_Sig", "{0}".format(methods[3]), 100, -10., 10. )
	hmD_Bkg = TH1D("hmD_Bkg", "{0}".format(methods[3]), 100, -10., 10. )


########
# TMVA #
########


def startTMVA():
	reader.BookMVA( methods[0],"{0}/Output/{1}/weights/TMVAClassification_MLP.weights.xml".format(dataPath, weightFolder))

	logging.info(" #|---Beginning Sig Evaluation---|#")
	classID[0] = 0 #set classID = 0
	eventLoop(nSigEvents, classID[0])
	logging.info(" #|---Finished Sig Evaluation---|#")

	logging.info(" #|---Beginning Bkg Evaluation---|#")
	classID[0] = 1 #set ClassID = 0
	eventLoop(nBkgEvents, classID[0])
	logging.info(" #|---Finished Bkg Evaluation---|#")


def eventLoop(nEvents, ID):
	for i in range (nEvents):
		if ID == 0:
			sigTree.GetEntry(i)
			pointer_trkCnt[0]  = sigTree.GetLeaf(varName[0]).GetValue(0)      #|Track Count
			pointer_calR[0]    = sigTree.GetLeaf(varName[1]).GetValue(0)      #|Cal Ratio
			pointer_JetpT[0]   = sigTree.GetLeaf(varName[2]).GetValue(0)/1000 #|Jet pT (GeV)
			pointerS_evntN[0]  = sigTree.GetLeaf(varName[3]).GetValue(0)      #|Event N
			pointerS_jetN[0]   = sigTree.GetLeaf(varName[4]).GetValue(0)      #|Jet N
			pointerE_Dist[0]   = sigTree.GetLeaf(varName[5]).GetValue(0)/1000 #|Distance (m)
			pointerE_delPhi[0] = sigTree.GetLeaf(varName[6]).GetValue(0)      #|Delta Eta
			pointerE_delEta[0] = sigTree.GetLeaf(varName[7]).GetValue(0)      #|Delta Phi
			pointerE_DelR[0]   = sigTree.GetLeaf(varName[8]).GetValue(0)      #|Delta R
			if pointer_JetpT[0] >= 25:
				mA_SigOut[0] = reader.EvaluateMVA( methods[0] )
				mB_SigOut[0] = reader.EvaluateMVA( methods[1]  )
				mC_SigOut[0] = reader.EvaluateMVA( methods[2]  )
				mD_SigOut[0] = reader.EvaluateMVA( methods[3]  )
				hmA_Sig.Fill( mA_SigOut[0] )
				hmD_Sig.Fill( mB_SigOut[0] )
				hmC_Sig.Fill( mC_SigOut[0] )
				hmD_Sig.Fill( mD_SigOut[0] )
				outTree.Fill()
		if ID == 1:
			bkgTree.GetEntry(i)
			pointer_trkCnt[0]  = bkgTree.GetLeaf(varName[0]).GetValue(0)      #|Track Count
			pointer_calR[0]    = bkgTree.GetLeaf(varName[1]).GetValue(0)      #|Cal Ratio
			pointer_JetpT[0]   = bkgTree.GetLeaf(varName[2]).GetValue(0)/1000 #|Jet pT
			pointerS_evntN[0]  = bkgTree.GetLeaf(varName[3]).GetValue(0)      #|Event N
			pointerS_jetN[0]   = bkgTree.GetLeaf(varName[4]).GetValue(0)      #|Jet N
			pointerE_Dist[0]   = 0
			pointerE_delEta[0] = 0
			pointerE_delPhi[0] = 0
			pointerE_DelR[0]   = 0
			mA_SigOut[0]       = 0
			mB_SigOut[0]       = 0
			mC_SigOut[0]       = 0
			mD_SigOut[0]       = 0
			if pointer_JetpT[0] >= 25:
				mA_BkgOut[0] = reader.EvaluateMVA( methods[0] )
				mB_BkgOut[0] = reader.EvaluateMVA( methods[1] )
				mC_BkgOut[0] = reader.EvaluateMVA( methods[2] )
				mD_BkgOut[0] = reader.EvaluateMVA( methods[3] )
				hmA_Bkg.Fill( mA_BkgOut[0] )
				hmD_Bkg.Fill( mB_BkgOut[0] )
				hmC_Bkg.Fill( mC_BkgOut[0] )
				hmD_Bkg.Fill( mD_BkgOut[0] )
				outTree.Fill()
		if (i%100000 == 0): #Debug
			logging.info(" #---|Event N     : {0}".format(i) 		     	  )
			logging.info(" #---|MLP_Sig     : {0}".format(mA_SigOut[0]        ))
			logging.debug("#---|Track Count : {0}".format(pointer_trkCnt[0]   ))
			logging.debug("#---|Cal_Ratio   : {0}".format(pointer_calR[0]     ))
			logging.debug("#---|Jet pT      : {0}".format(pointer_JetpT[0]    ))
			logging.debug("#---|Event N     : {0}".format(pointerS_evntN[0]   ))
			logging.debug("#---|Jet N       : {0}".format(pointerS_jetN[0]    ))
			logging.debug("#---|Distance    : {0}".format(pointerE_Dist[0]    ))
			logging.debug("#---|Delta_Phi   : {0}".format(pointerE_delPhi[0]  ))
			logging.debug("#---|Delta_Eta   : {0}".format(pointerE_delEta[0]  ))
			logging.debug("#---|Delta_R     : {0}".format(pointerE_DelR[0]    ))
			logging.debug("#----------------------------------------#")



def writeData():
	outTree.SetDirectory(outFile)
	logging.info ("#|---Writing Output Tree---|#\n")
	outTree.Write()

	logging.debug("#|---Scanning Output Tree---|#")
	outTree.Print()
	outTree.Scan("*")

	logging.info ("#|---Writing Output File---|#\n")
	outFile.Write()
	outFile.Close()


def deltaT():
	global deltaT
	deltaT = time.time() - st
	deltaT = deltaT / 60. #minutes
	return deltaT


########
# MAIN #
########

def main():
	outputFolder()
	prepare_reader()
	loadTestData()
	prepareOutput()
	startTMVA()
	writeData()
	logging.info("######################################")
	logging.info("#         FINISHED EVALUATION        #")
	logging.info("# Time elapsed: %4.4s minutes       #" % deltaT() )
	logging.info("######################################")

if __name__ == "__main__":
	main()

