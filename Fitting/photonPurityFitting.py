from ROOT import TFile, TFractionFitter, TObjArray

import pprint

_file = TFile("../RootFiles/Isolation_Output.root")


systematics  = ["nominal",
                "FSRDown",
                "FSRUp",
                "ISRDown",
                "ISRUp",
                "JERDown",
                "JERUp",
                "JESDown",
                "JESUp",
                "PDFDown",
                "PDFUp",
                "Q2ScaleDown",
                "Q2ScaleUp",
                "btagWeight_heavyDown",
                "btagWeight_heavyUp",
                "btagWeight_lightDown",
                "btagWeight_lightUp",
                "eleEffWeightDown",
                "eleEffWeightUp",
                "muEffWeightDown",
                "muEffWeightUp",
                "puWeightDown",
                "puWeightUp",
]

results = {}

data = _file.Get("dataObs")
    
for syst in systematics:

    mc = TObjArray(2)
    mc.Add(_file.Get(f"Isolated_{syst}"))
    mc.Add(_file.Get(f"NonPrompt_{syst}"))

    fit = TFractionFitter(data, mc,"q")
    
    status = int(fit.Fit())

    fitResults = fit.GetFitter().Result().Parameters()

    isolatedSF  = data.Integral()*fitResults[0]/mc[0].Integral()
    nonPromptSF = data.Integral()*fitResults[1]/mc[1].Integral()

    isolatedRate = mc[0].GetBinContent(1)*isolatedSF
    nonPromptRate = mc[1].GetBinContent(1)*nonPromptSF
    totalRate = (isolatedRate + nonPromptRate)

    if not status==0:
        print (f"Error in fit while processing {syst} sample: exit status {status}")
    
    phoPurity = isolatedRate / totalRate

    fitError_iso = fit.GetFitter().Result().ParError(0)
    fitError_np = fit.GetFitter().Result().ParError(1)
    isoError = data.Integral()*fitError_iso*mc[0].GetBinContent(1)/mc[0].Integral()
    npError = data.Integral()*fitError_np*mc[1].GetBinContent(1)/mc[1].Integral()

    
    phoPurityErr = ((isoError * (1 + phoPurity) / totalRate)**2 + (npError*phoPurity/totalRate)**2)**0.5

    results[syst] = (phoPurity, phoPurityErr)    

    del fit

pp = pprint.PrettyPrinter(indent=4)
pprint.pprint(results)
