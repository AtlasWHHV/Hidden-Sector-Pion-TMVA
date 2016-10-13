import sys, os, os.path
import datetime, time
import logging

from ROOT import gSystem, gROOT, gApplication, TMVA, TFile, TTree, TChain, TCut

logging.basicConfig(level=logging.DEBUG)

#######################
# SET OUTPUT LOCATION #
#######################
today       = datetime.date.today()
todayString = today.isoformat()
outputPath  = "/phys/groups/tev/scratch4/users/tommeyer/HiddenValley/Output/%s/" % todayString
try:
	os.mkdir(outputPath)
except OSError:
	if not os.path.isdir(outputPath):
		raise
os.chdir(outputPath)

#################
# ROOT SETTINGS #
#################
gROOT.SetMacroPath( "$ROOTSYS/tmva/test/" )
gROOT.Macro       ( "./TMVAlogon.C"       )
gROOT.LoadMacro   ( "./TMVAGui.C"         )

outName = "HvTrain_NN-MLP-LK.root"
outputFile = TFile( outName, 'Recreate')
logging.info( " Output File: {0}".format(outName) )

factory = TMVA.Factory( "TMVAClassification", outputFile,
            	"!V:!Silent:Color:DrawProgressBar:Transformations=I;G:AnalysisType=Classification" )
factory.SetVerbose( True )
logging.info( " TMVA Factory Created " )

#############
# VARIABLES #
#############
factory.AddVariable("Track_Count", 'F')
factory.AddVariable("Cal_Ratio", 'F')
factory.AddVariable("Jet_Pt", 'F')

#############
# SPECTATOR #
#############
factory.AddSpectator("Event_Num", 'F')
factory.AddSpectator("Jet_Num" ,'F')

################
# PREPARE DATA #
################
dataSetFolder = "TMVA Inputs"
dataPath      = "/phys/groups/tev/scratch4/users/tommeyer/HiddenValley/{0}/".format( dataSetFolder )

sigFileName = "trainingsignal.root"
sigFile     = "{0}/{1}".format(dataPath, sigFileName)

bkgFileName = "trainingbkg.root"
bkgFile     = "{0}/{1}".format(dataPath, bkgFileName)

sigRootFile = TFile.Open( sigFile )
bkgRootFile = TFile.Open( bkgFile )

treeName = "Training_Variables"
sigInput = sigRootFile.Get( treeName )
bkgInput = bkgRootFile.Get( treeName )

#######################
# LOAD DATA INTO TMVA #
#######################
sigWeight = 1.0
bkgWeight = 1.0

factory.AddSignalTree    (sigInput, sigWeight)
factory.AddBackgroundTree(bkgInput, bkgWeight)

########
# CUTS #
########
sigCuts = TCut( "Jet_Pt>25000" )
bkgCuts = TCut( "Jet_Pt>25000" )

#------------------#
# SETUP TRAIN/TEST #
#------------------#
factory.PrepareTrainingAndTestTree(sigCuts, bkgCuts,
	"SplitMode=Random:NormMode=NumEvents:SplitSeed=50:VerboseLevel=Verbose")

logging.info("TMVA Training and Testing Prepared")

#factory.BookMethod( TMVA.Types.kCuts, "Cuts",
#                            "!H:!V:FitMethod=MC:EffSel:SampleSize=200000:VarProp=FSmart" )

factory.BookMethod( TMVA.Types.kBDT, "BDT_A",
                           "!H:!V:NTrees=850:MinNodeSize=5%:MaxDepth=3:BoostType=AdaBoost:AdaBoostBeta=0.5:UseBaggedBoost:BaggedSampleFraction=0.5:SeparationType=GiniIndex:nCuts=20" )

factory.BookMethod( TMVA.Types.kBDT, "BDT_B",
                           "!H:!V:NTrees=850:MinNodeSize=5%:MaxDepth=5:BoostType=AdaBoost:AdaBoostBeta=0.5:UseBaggedBoost:BaggedSampleFraction=0.5:SeparationType=GiniIndex:nCuts=20" )

factory.BookMethod( TMVA::Types::kLikelihood, "LikelihoodA", 
                            "!V:!V:TransformOutput=D:Spline=2:NSmooth=5:NAvEvtPerBin=50" )

factory.BookMethod( TMVA.Types.kLikelihood, "LikelihoodB",
                            "!H:!V:TransformOutput=D:Spline=2:NSmooth=5:NAvEvtPerBin=75" )


#factory.BookMethod( TMVA.Types.kMLP, "MLP", "H:!V:VarTransform=N,D:NCycles=600:HiddenLayers=N+9:TestRate=5:!UseRegulator" )

logging.info(" TMVA METHOD: NN, Likelihood(x2)")

############
# Run TMVA #
############
factory.TrainAllMethods()
factory.TestAllMethods()
factory.EvaluateAllMethods()
outputFile.Write()
outputFile.Close()

gROOT.ProcessLine( "TMVAGui(\"%s\")" % outName )
gApplication.Run()

#########################################################

