from ROOT import TFile, TTree, TCanvas, TPad
import sys, os, os.path

path = "/phys/groups/tev/scratch4/users/tommeyer/HiddenValley/Output/Hv_NeuralNet"

f = TFile("{0}/HvReader_MLP_Test.root".format(path))
t = f.Get("NN")
# 0-Trackcount 1-Cal 2-Jet_Pt 3-Event_Nim 4-Jet_Num 5-Distance 6-Delta_eta 7-Delta_phi 8-Delta_R
var = [
	"Track_Count",
	"Cal_Ratio",
	"Jet_Pt",
	"Event_Num",
	"Jet_Num",
	"Distance",
	"Delta_Eta",
	"Delta_Phi",
	"Delta_R",
	"ClassID"
]
nnRes   = ["MLP_Sig", "MLP_Bkg"]
classID = ["ClassID==0", "ClassID==1"]

width   = 1200
height  = 600
#-------------------------------#
def plotFolder():
	plotPath  = "/{0}/Plots".format(path)
	try:
		os.mkdir(plotPath)
	except OSError:
		if not os.path.isdir(plotPath):
			raise
	os.chdir(plotPath)
	print "Plotting to %s" % plotPath

def makeCanvas():
	canvas = TCanvas("c1","c1", width, height)
	canvas.Divide(2,1)
	return canvas

def plot_vars():
	for n in range(2):
		#NN RESPONSE
		c1 = makeCanvas()
		plVar = "{0}".format(nnRes[n])
		cut1 = "{0}&&{1}>.5".format(classID[n], nnRes[n])
		cut2 = "{0}&&{1}<.5".format(classID[n], nnRes[n])

		c1.cd(1)
		t.Draw(plVar, cut1)
		c1.cd(2)
		t.Draw(plVar,cut2)

		c1.Print("Plots.pdf")
		c1.SaveAs("./NN_{0}.png".format(nnRes[n]) )
		del c1

		#SIGNAL AND BACKGROUND VARIABLES
		for i in range(9):
			c1 = makeCanvas()
			plVar = "{0}".format(var[i])
			cut1 = "{0}&&{1}>.5".format(classID[n], nnRes[n])
			cut2 = "{0}&&{1}<.5".format(classID[n], nnRes[n])

			if n == 1 and i >= 5:
				return
			c1.cd(1)
			t.Draw(plVar, cut1)
			c1.cd(2)
			t.Draw(plVar, cut2)
			if n == 0:
				c1.Print("Plots.pdf")
				c1.SaveAs( "./NN_Sig_{0}.png".format(var[i]) )
			if n == 1:
				c1.Print("Plots.pdf")
				c1.SaveAs( "./NN_Bkg_{0}.png".format(var[i]) )
			del c1
	print "################################"
	print "#| FINISHED PLOTTING VARIABLES |#"
	print "################################"

		for i in range(9):
			c1 = makeCanvas()
			plVar = "{0}:{1}".format(var[i], nnRes[n])
			cut1 = "{0}&&{1}>.5".format(classID[n], nnRes[n])
			cut2 = "{0}&&{1}<.5".format(classID[n], nnRes[n])

			if n == 1 and i >= 5:
				return
			c1.cd(1)
			t.Draw(plVar, cut1)
			c1.cd(2)
			t.Draw(plVar, cut2)
			if n == 0:
				c1.Print("Plots.pdf")
				c1.SaveAs( "./NN_SigRes_vs_{0}.png".format(var[i]) )
			if n == 1:
				c1.Print("Plots.pdf")
				c1.SaveAs( "./NN_BkgRes_vs_{0}.png".format(var[i]) )
			del c1
	print "###################################"
	print "#| FINISHED PLOTTING COMPARISONS |#"
	print "###################################"



#Plot variables in interesting ranges
#def plot_oddities():


def main():
	plotFolder()
	pdfHold = TCanvas("pdf","pdf", width, height)
	pdfHold.Print("Plots.pdf(")
	plot_vars()
	pdfHold.Print("Plots.pdf)")

if __name__ == "__main__":
	main()
