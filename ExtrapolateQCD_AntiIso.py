import ROOT
import os,sys
import numpy as np
from CMSPLOTS.myFunction import DrawHistos

doMuon = False
doElectron = True
doWpT = False

ROOT.gROOT.SetBatch(True)
ROOT.TH1.AddDirectory(ROOT.kFALSE)
ROOT.TH2.AddDirectory(ROOT.kFALSE)
ROOT.TH3.AddDirectory(ROOT.kFALSE)

etaLabels = {
    "lepEta_bin0": "Full Eta", 
    "lepEta_bin1": "Barrel", 
    "lepEta_bin2": "Endcap"
}
channelLabels = {
    "muplus":  "W^{+}#rightarrow #mu^{+}#nu",
    "muminus": "W^{-}#rightarrow #mu^{-}#nu",
    "eplus":   "W^{+}#rightarrow e^{+}#nu",
    "eminus":  "W^{-}#rightarrow e^{-}#nu",
}

if doWpT:
    wptbins = ["WpT_bin1", "WpT_bin2", "WpT_bin3", "WpT_bin4", "WpT_bin5", "WpT_bin6", "WpT_bin7", "WpT_bin8", "WpT_bin9"]
else:
    wptbins = ["WpT_bin0"]

    #TODO: MORE THAN MT VARIABLE


def ExpltOneBin(variable, isocenters, bincontents, binerrors, isoSR, mTmin, mTmax, suffix="", extraText="", bincontents_scaled = None, binerrors_scaled = None):
    """
    extrapolate the QCD shape from a set of control regions (isocenters) to the signal region (isoSR),
    using linear extrapolation and the 2nd order polynomial function
    """
    graph = ROOT.TGraphErrors(len(bincontents), np.array(isocenters), np.array(bincontents), np.zeros(len(bincontents)), np.array(binerrors))
    f1 = ROOT.TF1("pol1_"+suffix, "[0]*(x-{}) + [1]".format(str(isoSR)), -0.1, 0.60)
    f2 = ROOT.TF1("pol2_"+suffix, "[0]*(x-{isoSR})*(x-{isoSR}) + [1]*(x-{isoSR}) + [2]".format(isoSR=str(isoSR)), -0.1, 0.60)
    # fit range
    fitmin = 0.25
    fitmax = 0.60
    graph.Fit(f1, "R", "", fitmin, fitmax)
    graph.Fit(f2, "R", "", fitmin, fitmax)
    #print("val at Signal region", f1.Eval(isoSR))

    val_pol1_par1 = f1.GetParameter(1)
    err_pol1_par1 = f1.GetParError(1)
    val_pol1_par0 = f1.GetParameter(0)
    err_pol1_par0 = f1.GetParError(0)
    val_pol2_par2 = f2.GetParameter(2)
    err_pol2_par2 = f2.GetParError(2)
    #print("val ", val, " error ", err)

    f1.SetLineStyle(2)
    f1.SetLineColor(46)
    f2.SetLineStyle(2)
    f2.SetLineColor(9)

    graph2 = ROOT.TGraphErrors(1, np.array([isoSR]), np.array([val_pol1_par1]), np.zeros(1), np.array([abs(err_pol1_par1)]))
    graph2.SetMarkerColor(46)
    graph2.SetMarkerStyle(47)
    graph2.SetMarkerSize(2)

    graph3 = ROOT.TGraphErrors(1, np.array([isoSR]), np.array([val_pol2_par2]), np.zeros(1), np.array([abs(err_pol2_par2)]))
    graph3.SetMarkerColor(9)
    graph3.SetMarkerStyle(45)
    graph3.SetMarkerSize(2)

    h_todraws = [graph, f1, f2, graph2, graph3]
    if variable == "mtcorr":
        labels = ["{} < mT < {}".format(mTmin, mTmax), "Pol1 Fit", "Pol1 Extrapolation"]
    elif variable == "met":
        labels = ["{} < MET < {}".format(mTmin, mTmax), "Pol1 Fit", "Pol1 Extrapolation"]
    elif variable == "ptOmT":
        labels = ["{} < pT/mT < {}".format(mTmin, mTmax), "Pol1 Fit", "Pol1 Extrapolation"]
    drawoptions = ["P same", "L", "L", "P same", "P same"]
    legendoptions=["EP", "L", "L", "EP", "EP"]

    # h_todraws = [graph, f1, graph2]
    # if variable == "mtcorr":
    #     labels = ["{} < mT < {}".format(mTmin, mTmax), "Pol1 Fit", "Pol1 Extrapolation"]
    # elif variable == "met":
    #     labels = ["{} < MET < {}".format(mTmin, mTmax), "Pol1 Fit", "Pol1 Extrapolation"]
    # elif variable == "ptOmT":
    #     labels = ["{} < pT/mT < {}".format(mTmin, mTmax), "Pol1 Fit", "Pol1 Extrapolation"]
    # drawoptions = ["P same", "L", "P same"]
    # legendoptions=["EP", "L", "EP"]

    val_scaled_pol1_par1 = None
    err_scaled_pol1_par1 = None
    if bincontents_scaled:
        # repeat the fitting precedure on the scaled templates
        graph_scaled = ROOT.TGraphErrors(len(bincontents), np.array(isocenters), np.array(bincontents_scaled), np.zeros(len(bincontents)), np.array(binerrors_scaled))
        f3 = ROOT.TF1("pol1_scaled"+suffix, "[0]*(x-{}) + [1]".format(str(isoSR)), -0.1, 0.60)
        graph_scaled.Fit(f3, "R", "", fitmin, fitmax)
        val_scaled_pol1_par1 = f3.GetParameter(1)
        err_scaled_pol1_par1 = f3.GetParError(1)

        f3.SetLineStyle(2)
        f3.SetLineColor(30)

        graph_scaled.SetMarkerColor(12)
        graph_scaled.SetMarkerStyle(31)
        graph4 = ROOT.TGraphErrors(1, np.array([isoSR]), np.array([val_scaled_pol1_par1]), np.zeros(1), np.array([abs(err_scaled_pol1_par1)]))
        graph4.SetMarkerColor(30)
        graph4.SetMarkerStyle(41)
        graph4.SetMarkerSize(2)

        h_todraws.append(graph_scaled)
        h_todraws.append(f3)
        h_todraws.append(graph4)

        labels.append("Templates with Scaled MC")
        labels.append("Pol1 Fit with Scaled MC")
        labels.append("Pol1 Extrapolation with Scaled MC")
        
        drawoptions.extend(["P same", "L", "P same"])
        legendoptions.extend(["PE", "L", "PE"])

    DrawHistos( h_todraws, labels, 0, 1.2, "Lepton Relative Isolation", 0.5*min(bincontents), 1.25*max(bincontents), "Bin Content", "QCDBinContentNorm_"+suffix, dology=False, drawoptions=drawoptions, legendoptions=legendoptions, nMaxDigits=3, legendPos=[0.65, 0.18, 0.88, 0.58], lheader=extraText)

    #return (val_pol1_par1, err_pol1_par1), (val_pol1_par0, err_pol1_par0), (val_pol2_par2, err_pol2_par2), (val_scaled_pol1_par1, err_scaled_pol1_par1)
    return (val_pol1_par1, err_pol1_par1), (val_pol1_par0, err_pol1_par0)


def ExtrapolateQCD(fname, oname, channel, variable, wptbin, etabins, isobins, fname_scaled=None):
    """
    run the QCd extrapolation in all mT bins,
    save the statistical and systematic variations for HComb, and
    make some shape comparison plots
    """
    # fqcd = ROOT.TFile.Open(fname)
    # if fname_scaled:
    #     # qcd templates with scaled MC subtraction
    #     fqcd_scaled = ROOT.TFile.Open(fname_scaled)

    if not os.path.exists("root/QCD"):
        os.makedirs("root/QCD")
    ofile = ROOT.TFile.Open("root/QCD/"+oname, "recreate")

    infile = ROOT.TFile.Open(fname)

    #ADDED BY JULIUS
    #examples of bins: [w_iso6], [lepEta_bin0], [WpT_bin0]

    isomin = isobins[0]
    isomax = isobins[-1]
    #TODO: Make sure these are right
    isocuts = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65]
    isocenters = [(isocuts[i] + isocuts[i+1])/2 for i in range(len(isocuts)-1)]
    
    isoSR = infile.Get("iso_mean").GetMean()
    print(isoSR)
    #isoSR = 0.025 # average isolation value in the signal region

    for etabin in etabins:
        histos_norm = dict()
        histos_scaled_norm = dict()
        fqcd = ROOT.TFile.Open(fname)
        fqcd.Print()

        for iso in isobins:

            hname = "histo_wjetsAntiIso_fullrange_{}_weight_{}_w_{}_{}_{}".format(variable, channel, iso, wptbin, etabin)
            print(hname)
            h = fqcd.Get(hname)
            h.Print()

            # set the overflow and underflow to zero
            h.SetBinContent(0, 0)
            h.SetBinContent(h.GetNbinsX()+1, 0)
            h_norm =  h.Clone(hname+"_Cloned")
            histos_norm[iso] = h_norm

        href = histos_norm[isobins[0]]
        counts = href.Integral()
        for iso in isobins:

            #Normalize histrograms
            histos_norm[iso].Scale(counts / histos_norm[iso].Integral())

        # some histograms to save the trend of function parameter variation as a function of mT
        # mostly for plotting purpose
        h_pol1_par1 = href.Clone("h_pol1_par1_{}_{}_{}".format(channel, etabin, wptbin)) # interception
        h_pol1_par0 = href.Clone("h_pol1_par0_{}_{}_{}".format(channel, etabin, wptbin)) # slope
        h_pol2_par2 = href.Clone("h_pol2_par2_{}_{}_{}".format(channel, etabin, wptbin)) # interception
        #h_scaled_pol1_par1 = href.Clone("h_scaled_pol1_par1_{}_{}_{}".format(channel, etabin, wptbin)) # interception for the scaled templates

        # save the extrapolated shape for HComb
        hnew = href.Clone("h_QCD_Extrapolated_" + channel + "_" + etabin + "_" + wptbin)
        hnew_pol2 = href.Clone("h_QCD_Extrapolated_" + channel + "_" + etabin + "_" + wptbin + "_Pol2shapeUp")
        hnew_scaled = href.Clone("h_QCD_Extrapolated_" + channel + "_" + etabin + "_" + wptbin + "_ScaledMCshapeUp")


        vals_pol1_par1 = []
        #
        # run the linear extrapolation bin-by-bin
        #
        for ibin in xrange(1, histos_norm[isomin].GetNbinsX()+1):
            bincontents = []
            binerrors = []
            for iso, hist in histos_norm.iteritems():
                bincontents.append( hist.GetBinContent(ibin) )
                binerrors.append( hist.GetBinError(ibin) )

            mTmin = histos_norm[isomin].GetBinLowEdge(ibin)
            mTmax = histos_norm[isomin].GetBinLowEdge(ibin) + histos_norm[isomin].GetBinWidth(ibin)
            suffix = variable + "_" + channel+"_bin_"+str(ibin)+"_"+ etabin+"_"+wptbin
            extraText = channelLabels[channel] +" "+ etaLabels[etabin]

            bincontents_scaled = None
            binerrors_scaled = None
            results_pol1_par1, results_pol1_par0 = ExpltOneBin(variable, isocenters, bincontents, binerrors, isoSR, mTmin, mTmax, suffix=suffix, extraText=extraText, bincontents_scaled = bincontents_scaled, binerrors_scaled = binerrors_scaled)

            hnew.SetBinContent(ibin, max(results_pol1_par1[0], 0))
            hnew.SetBinError(ibin, 0.) 

            h_pol1_par1.SetBinContent(ibin, results_pol1_par1[0])
            h_pol1_par1.SetBinError(ibin,   results_pol1_par1[1])
            h_pol1_par0.SetBinContent(ibin, results_pol1_par0[0])
            h_pol1_par0.SetBinError(ibin,   results_pol1_par0[1])
            #h_pol2_par2.SetBinContent(ibin, results_pol2_par2[0])
            #h_pol2_par2.SetBinError(ibin,   results_pol2_par2[1])

            vals_pol1_par1.append(results_pol1_par1)

        # set the bin-by-bin shape variation (stat.) for HComb
        hnew_ups = []
        hnew_downs = []
        for ibin in xrange(1, histos_norm[isomin].GetNbinsX()+1):
            val = max(vals_pol1_par1[ibin-1][0], 0.)
            err = vals_pol1_par1[ibin-1][1]
            hnew_up   = hnew.Clone("h_QCD_Extrapolated_"+channel+"_"+etabin+"_"+wptbin+"_bin{}shapeUp".format(str(ibin)))
            hnew_down = hnew.Clone("h_QCD_Extrapolated_"+channel+"_"+etabin+"_"+wptbin+"_bin{}shapeDown".format(str(ibin)))
            hnew_up.SetBinContent(ibin, val+err)
            hnew_up.SetBinError(ibin, 0.)
            hnew_down.SetBinContent(ibin, max(val-err, 0.))
            hnew_down.SetBinError(ibin, 0.)

            hnew_ups.append(hnew_up)
            hnew_downs.append(hnew_down)

        #STOPPED ADDED BY JULIUS

        # pol2 as another systematic
        hnew_pol2.Scale(hnew.Integral() / hnew_pol2.Integral())
        hnew_pol2Dn = hnew_pol2.Clone("h_QCD_Extrapolated_" + channel + "_" + etabin + "_" + wptbin + "_Pol2shapeDown")
        for ibin in xrange(1, hnew.GetNbinsX()+1):
            hnew_pol2Dn.SetBinContent(ibin, 2*hnew.GetBinContent(ibin) - hnew_pol2.GetBinContent(ibin))
        hnew_ups.append(hnew_pol2)
        hnew_downs.append(hnew_pol2Dn)

        # scaled MC as another systematic
        if fname_scaled:
            hnew_scaled.Scale(hnew.Integral() / hnew_scaled.Integral())
            hnew_scaledDn = hnew_scaled.Clone("h_QCD_Extrapolated_" + channel + "_" + etabin + "_" + wptbin + "_ScaledMCshapeDown")
            for ibin in xrange(1, hnew.GetNbinsX()+1):
                hnew_scaledDn.SetBinContent(ibin, 2*hnew.GetBinContent(ibin) - hnew_scaled.GetBinContent(ibin))
            hnew_ups.append(hnew_scaled)
            hnew_downs.append(hnew_scaledDn)

        h_pol1_par1.SetLineColor(46)
        h_pol1_par1.SetMarkerColor(46)
        h_pol2_par2.Scale(h_pol1_par1.Integral() / h_pol2_par2.Integral())
        h_pol2_par2.SetLineColor(9)
        h_pol2_par2.SetMarkerColor(9)
        h_todraws = [h_pol1_par1, h_pol2_par2]
        labels = ["Pol1 Extrapolation", "Pol2 Extrapolation"]
        # h_todraws = [h_pol1_par1]
        # labels = ["Pol1 Extrapolation"]
        if fname_scaled:
            h_scaled_pol1_par1.SetLineColor(30)
            h_scaled_pol1_par1.SetMarkerColor(30)
            h_todraws.append(h_scaled_pol1_par1)
            labels.append("Scaled MC")
        
        if variable == "mtcorr":
            DrawHistos( h_todraws, labels, 0, 120, "m_{T} [GeV]", 0., 1.25*h_pol1_par1.GetMaximum(), "A.U.", "QCDShapeCompare_"+variable + "_" +channel+"_"+etabin+"_"+wptbin, dology=False, nMaxDigits=3, legendPos=[0.60, 0.72, 0.88, 0.88], lheader=extraText)
        elif variable == "met":
            DrawHistos( h_todraws, labels, 0, 120, "MET [GeV]", 0., 1.25*h_pol1_par1.GetMaximum(), "A.U.", "QCDShapeCompare_"+variable + "_"+channel+"_"+etabin+"_"+wptbin, dology=False, nMaxDigits=3, legendPos=[0.60, 0.72, 0.88, 0.88], lheader=extraText)
        elif variable == "ptOmT":
            DrawHistos( h_todraws, labels, 0, 120, "#frac{p_{T}}{m_{T}} [GeV]", 0., 1.25*h_pol1_par1.GetMaximum(), "A.U.", "QCDShapeCompare_"+variable + "_"+channel+"_"+etabin+"_"+wptbin, dology=False, nMaxDigits=3, legendPos=[0.60, 0.72, 0.88, 0.88], lheader=extraText)

        #
        # write the variations to the output
        #
        ofile.cd()
        hnew.SetDirectory(ofile)
        hnew.Write()
        for h in h_todraws + [h_pol1_par0]:
            h.SetDirectory(ofile)
            h.Write()
        for hnew_up in hnew_ups:
            hnew_up.SetDirectory(ofile)
            hnew_up.Write()
        for hnew_down in hnew_downs:
            hnew_down.SetDirectory(ofile)
            hnew_down.Write()

        number_of_qcd_events = h_todraws[0].Integral()
    
    ofile.Close()
    return number_of_qcd_events


if __name__ == "__main__":
    #isobins = ["iso5", "iso6", "iso7", "iso8", "iso9", "iso10", "iso11"]
    isobins = ["iso5", "iso6", "iso7", "iso8", "iso9", "iso10"]
    #lepEtaBins = ["lepEta_bin0", "lepEta_bin1", "lepEta_bin2"]
    lepEtaBins = ["lepEta_bin0"]
    variables = ["mtcorr", "met", "ptOmT"]

    number_of_qcd_events_pos = dict()
    number_of_qcd_events_neg = dict()
    number_of_qcd_events_normed = dict()

    if doMuon:
        fname = "root/output_qcdshape_fullrange_mu_nu.root"
        for variable in variables:
            for wptbin in ["WpT_bin0"]:
                oname = "qcdshape_extrapolated_muplus_" + variable
                events = ExtrapolateQCD(fname, oname+"_"+wptbin+"_muplus.root", "muplus", variable,wptbin, lepEtaBins, isobins)
                number_of_qcd_events_pos[variable] = events

                oname = "qcdshape_extrapolated_muminus_" + variable
                events = ExtrapolateQCD(fname, oname+"_"+wptbin+"_muminus.root", "muminus", variable,wptbin, lepEtaBins, isobins)
                number_of_qcd_events_neg[variable] = events
        
        for variable in variables:
            number_of_qcd_events_normed["{}_pos".format(variable)] = number_of_qcd_events_pos[variable] / number_of_qcd_events_pos["met"]
            number_of_qcd_events_normed["{}_neg".format(variable)] = number_of_qcd_events_neg[variable] / number_of_qcd_events_pos["met"]
        print("Positive: ", number_of_qcd_events_pos)
        print("Negative: ", number_of_qcd_events_neg)
        print(number_of_qcd_events_normed)


    if doElectron:
        fname = "root/output_qcdshape_fullrange_e_nu.root"
        for variable in variables:
            for wptbin in ["WpT_bin0"]:
                oname = "qcdshape_extrapolated_eplus_" + variable
                events = ExtrapolateQCD(fname, oname+"_"+wptbin+"_eplus.root", "eplus", variable,wptbin, lepEtaBins, isobins)
                number_of_qcd_events_pos[variable] = events

                oname = "qcdshape_extrapolated_eminus_" + variable
                events = ExtrapolateQCD(fname, oname+"_"+wptbin+"_eminus.root", "eminus", variable,wptbin, lepEtaBins, isobins)
                number_of_qcd_events_neg[variable] = events

        for variable in variables:
            number_of_qcd_events_normed["{}_pos".format(variable)] = number_of_qcd_events_pos[variable] / number_of_qcd_events_pos["met"]
            number_of_qcd_events_normed["{}_neg".format(variable)] = number_of_qcd_events_neg[variable] / number_of_qcd_events_pos["met"]
        print("Positive: ", number_of_qcd_events_pos)
        print("Negative: ", number_of_qcd_events_neg)
        print(number_of_qcd_events_normed)
