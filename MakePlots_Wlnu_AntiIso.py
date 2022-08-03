"""
test on the anti-Isolated region mixed with signal region
"""
import ROOT 
import numpy as np
from collections import OrderedDict
import sys, os , time
sys.path.append("/work/moh/tools/CMSPLOTS")
#sys.path.append("/afs/cern.ch/work/y/yofeng/public/CMSPLOTS")
from myFunction import THStack2TH1

from SampleManager import DrawConfig, Sample, SampleManager

ROOT.TH1.AddDirectory(ROOT.kFALSE)
ROOT.TH2.AddDirectory(ROOT.kFALSE)
ROOT.TH3.AddDirectory(ROOT.kFALSE)
ROOT.gROOT.SetBatch(True)

ROOT.ROOT.EnableImplicitMT(32)

# boolean flag to set either muon or electron channel
# doMuon = False means the electron channel
doMuon = True

# boolean flag. if set to true, scale the MC cross section by 30%
applyScaling = False

def main():
    input_base = "inputs_EarlyRun3_V10"
    #input_base = "inputs_test"

    if not os.path.exists("root"):
        os.makedirs("root")

    print "Program start..."
    #time_init = time.time()

    # Test run
    # RUN = 323775
    # LUMI = 0.046767743e3
    #RUN = 323778
    LUMI = 59.74e3
    # Update LUMI
    # LUMI = 59.83e3  # nominal
    #lumi_factor = 9.879796e-01
    # lumi_factor = 1.
    # lumi_factor = 1.2
    # lumi_factor = 0.8
    #LUMI = LUMI*lumi_factor

    # Rochester correction
    ROOT.gInterpreter.ProcessLine('#include "RoccoR/RoccoR.cc"')
    ROOT.gInterpreter.ProcessLine('rc = RoccoR("RoccoR/RoccoR2018UL.txt")')
    ROOT.gRandom.SetSeed(1)

    # Trigger efficiency
    ROOT.gROOT.ProcessLine('TFile* f_trig_eff = TFile::Open("data/Efficiencies_muon_generalTracks_Z_Run2018_UL_SingleMuonTriggers.root")')
    ROOT.gROOT.ProcessLine('TH1D* h_trig_eff_data  = (TH1D*)f_trig_eff->Get("NUM_IsoMu24_DEN_CutBasedIdTight_and_PFIsoTight_charge_abseta_pt_efficiencyData")')
    ROOT.gROOT.ProcessLine('TH1D* h_trig_eff_mc  = (TH1D*)f_trig_eff->Get("NUM_IsoMu24_DEN_CutBasedIdTight_and_PFIsoTight_charge_abseta_pt_efficiencyMC")')
    ROOT.gROOT.ProcessLine('f_trig_eff->Close();')

    if doMuon:
        #mmet channel
        #input_antiiso_data    = input_base+"/SingleMuon_Run2018D-UL2018/mmet/input_files.txt"
        input_antiiso_data    = input_base+"/SingleMuon_Run2018-UL2018/mmet/input_files.txt"
        input_antiiso_wl0     = input_base+"/WJetsToLNu_0J_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18NanoAODv9-106X/mmet/input_files.txt"
        input_antiiso_wl1     = input_base+"/WJetsToLNu_1J_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18NanoAODv9-106X/mmet/input_files.txt"
        input_antiiso_wl2     = input_base+"/WJetsToLNu_2J_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18NanoAODv9-106X/mmet/input_files.txt"
        input_antiiso_zxx     = input_base+"/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18NanoAODv9-106X/mmet/input_files.txt"
        input_antiiso_ttbar   = input_base+"/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_RunIISummer20UL18NanoAODv9-106X/mmet/input_files.txt"
        input_antiiso_tbar_1lep = input_base+"/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_RunIISummer20UL18NanoAODv9-106X/mmet/input_files.txt"

        #mm channel
        # input_antiiso_data    = input_base+"/SingleMuon_Run2018-UL2018/mm/input_files.txt"
        # #input_antiiso_wl0     = input_base+"/WJetsToLNu_0J_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18NanoAODv9-106X/mm/input_files.txt"
        # #input_antiiso_wl1     = input_base+"/WJetsToLNu_1J_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18NanoAODv9-106X/mm/input_files.txt"
        # #input_antiiso_wl2     = input_base+"/WJetsToLNu_2J_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18NanoAODv9-106X/mm/input_files.txt"
        # input_antiiso_zxx     = input_base+"/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18NanoAODv9-106X/mm/input_files.txt"
        # input_antiiso_ttbar   = input_base+"/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_RunIISummer20UL18NanoAODv9-106X/mm/input_files.txt"
        # input_antiiso_tbar_1lep = input_base+"/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_RunIISummer20UL18NanoAODv9-106X/mm/input_files.txt"

        # input_antiiso_data    = "inputs/awmunu/input_data.txt"
        # input_antiiso_wl0     = "inputs/awmunu/input_wm0.txt"
        # input_antiiso_wl1     = "inputs/awmunu/input_wm1.txt"
        # input_antiiso_wl2     = "inputs/awmunu/input_wm2.txt"
        # input_antiiso_ttbar   = "inputs/awmunu/input_ttbar_dilepton.txt"
        # input_antiiso_ttbar_1lep = "inputs/awmunu/input_ttbar_singlelepton.txt"
        # input_antiiso_ttbar_0lep = "inputs/awmunu/input_ttbar_hadronic.txt"
        # input_antiiso_ww      = "inputs/awmunu/input_ww.txt"
        # input_antiiso_wz      = "inputs/awmunu/input_wz.txt"
        # input_antiiso_zz      = "inputs/awmunu/input_zz.txt"
        # input_antiiso_zxx     = "inputs/awmunu/input_zxx.txt"
        # input_antiiso_wx0     = "inputs/awmunu/input_wx0.txt"
        # input_antiiso_wx1     = "inputs/awmunu/input_wx1.txt"
        # input_antiiso_wx2     = "inputs/awmunu/input_wx2.txt"
    else:
        input_antiiso_data    = "inputs/awenu/input_data.txt"
        input_antiiso_wl0     = "inputs/awenu/input_we0.txt"
        input_antiiso_wl1     = "inputs/awenu/input_we1.txt"
        input_antiiso_wl2     = "inputs/awenu/input_we2.txt"
        input_antiiso_ttbar   = "inputs/awenu/input_ttbar_dilepton.txt"
        input_antiiso_ttbar_1lep = "inputs/awenu/input_ttbar_singlelepton.txt"
        input_antiiso_ttbar_0lep = "inputs/awenu/input_ttbar_hadronic.txt"
        input_antiiso_ww      = "inputs/awenu/input_ww.txt"
        input_antiiso_wz      = "inputs/awenu/input_wz.txt"
        input_antiiso_zz      = "inputs/awenu/input_zz.txt"
        input_antiiso_zxx     = "inputs/awenu/input_zxx.txt"
        input_antiiso_wx0     = "inputs/awenu/input_wx0.txt"
        input_antiiso_wx1     = "inputs/awenu/input_wx1.txt"
        input_antiiso_wx2     = "inputs/awenu/input_wx2.txt"

    ## for the QCD background estimation (data-driven)
    qcdnorm = 1.0
    mcscale = 1.0
    if applyScaling:
        # scale up the MC for 30%
        mcscale = 1.3
    DataAisoSamp  = Sample(input_antiiso_data, isMC=False, name="Data_aiso", isWSR=True, additionalnorm = qcdnorm, legend = 'QCD', color='226')
    
    # W -> lnu
    Wl0AisoSamp   = Sample(input_antiiso_wl0, isMC=True, name = "wl0_aiso", isWSR=True, additionalnorm= qcdnorm * mcscale, lumi=LUMI)
    Wl1AisoSamp   = Sample(input_antiiso_wl1, isMC=True, name = "wl1_aiso", isWSR=True, additionalnorm= qcdnorm * mcscale, lumi=LUMI)
    Wl2AisoSamp   = Sample(input_antiiso_wl2, isMC=True, name = "wl2_aiso", isWSR=True, additionalnorm= qcdnorm * mcscale, lumi=LUMI)
    
    # ttbar
    TTbarAisoSamp  = Sample(input_antiiso_ttbar, isMC=True, name = "ttbar_dilepton_aiso",     isWSR=True, additionalnorm= qcdnorm * mcscale, lumi=LUMI)
    TT1LepAisoSamp = Sample(input_antiiso_tbar_1lep, isMC=True, name = "ttbar_1lepton_aiso", isWSR=True, additionalnorm= qcdnorm * mcscale, lumi=LUMI)
    #TT0LepAisoSamp = Sample(input_antiiso_ttbar_0lep, isMC=True, name = "ttbar_0lepton_aiso", isWSR=True, additionalnorm= qcdnorm * mcscale)
    
    ## dibosons
    #WWAisoSamp = Sample(input_antiiso_ww, isMC=True, name = "WW_aiso", isWSR=True, additionalnorm= qcdnorm * mcscale)
    #WZAisoSamp = Sample(input_antiiso_wz, isMC=True, name = "WZ_aiso", isWSR=True, additionalnorm= qcdnorm * mcscale)
    #ZZAisoSamp = Sample(input_antiiso_zz, isMC=True, name = "ZZ_aiso", isWSR=True, additionalnorm= qcdnorm * mcscale)
    
    # tau
    #ZXXAisoSamp = Sample(input_antiiso_zxx, isMC=True, name = "ZXX_aiso", isWSR=True, additionalnorm= qcdnorm * mcscale, lumi=LUMI)
    #Wx0AisoSamp = Sample(input_antiiso_wx0, isMC=True, name = "wx0_aiso", isWSR=True, additionalnorm= qcdnorm * mcscale)
    #Wx1AisoSamp = Sample(input_antiiso_wx1, isMC=True, name = "wx1_aiso", isWSR=True, additionalnorm= qcdnorm * mcscale)
    #Wx2AisoSamp = Sample(input_antiiso_wx2, isMC=True, name = "wx2_aiso", isWSR=True, additionalnorm= qcdnorm * mcscale)

    #sampMan = SampleManager(DataAisoSamp, [Wl0AisoSamp, Wl1AisoSamp, Wl2AisoSamp, TTbarAisoSamp, TT1LepAisoSamp, TT0LepAisoSamp, WWAisoSamp, WZAisoSamp, ZZAisoSamp, ZXXAisoSamp, Wx0AisoSamp, Wx1AisoSamp, Wx2AisoSamp])
    """sampMan = SampleManager(DataAisoSamp, 
                                [Wl0AisoSamp, Wl1AisoSamp, Wl2AisoSamp, TTbarAisoSamp, 
                                TT1LepAisoSamp, ZXXAisoSamp]
                            )"""

    #FOR MMET
    sampMan = SampleManager(DataAisoSamp, 
                                [Wl0AisoSamp, Wl1AisoSamp, Wl2AisoSamp, TTbarAisoSamp, 
                                TT1LepAisoSamp]
                            )
    sampMan.groupMCs(["ttbar_dilepton_aiso", "ttbar_1lepton_aiso"], "ttbar", 46, "t#bar{t}")
    sampMan.groupMCs(['wl0_aiso', 'wl1_aiso', 'wl2_aiso'], "wlnu", 92,"W#rightarrow#mu#nu")
    
    #FOR MM
    # sampMan = SampleManager(DataAisoSamp, 
    #                             [ZXXAisoSamp, TTbarAisoSamp, 
    #                             TT1LepAisoSamp]
    #                         )
    # sampMan.groupMCs(["ttbar_dilepton_aiso", "ttbar_1lepton_aiso"], "ttbar", 46, "t#bar{t}")
    # sampMan.groupMCs(["ZXX_aiso"], "DY", 92, "Z#rightarrow ll")

    #sampMan.groupMCs(["WW_aiso", "WZ_aiso", "ZZ_aiso", "ZXX_aiso", "wx0_aiso", "wx1_aiso", "wx2_aiso"], "EWK", 216, "EWK")
    #sampMan.groupMCs(["ttbar_dilepton_aiso", "ttbar_1lepton_aiso", "ttbar_0lepton_aiso"], "ttbar", 96, "t#bar{t}")
    #label = "W#rightarrow#mu#nu" if doMuon else "W#rightarrow e#nu"
    #sampMan.groupMCs(['wl0_aiso', 'wl1_aiso', 'wl2_aiso'], "wlnu", 92, label)

    sampMan.DefineAll("Lep_pt",     "pt_1")
    sampMan.DefineAll("Lep_eta",    "eta_1")
    sampMan.DefineAll("Lep_phi",    "phi_1")
    sampMan.DefineAll("Lep_mass",   "mass_1")
    sampMan.DefineAll("Lep_q",      "q_1")

    # muon and electron isolation distributions are different
    # more coarse binning for electrons to make sure enough statistics
    if doMuon:
        #signal region
        sampMan.DefineAll("w_iso4", "(iso_1 < 0.15)")
        
        #background region
        sampMan.DefineAll("w_iso5", "(iso_1 > 0.20 && iso_1 < 0.25)")
        sampMan.DefineAll("w_iso6", "(iso_1 > 0.25 && iso_1 < 0.30)")
        sampMan.DefineAll("w_iso7", "(iso_1 > 0.30 && iso_1 < 0.35)")
        sampMan.DefineAll("w_iso8", "(iso_1 > 0.35 && iso_1 < 0.40)")
        sampMan.DefineAll("w_iso9", "(iso_1 > 0.40 && iso_1 < 0.45)")
        sampMan.DefineAll("w_iso10", "(iso_1 > 0.45 && iso_1 < 0.50)")
        sampMan.DefineAll("w_iso11", "(iso_1 > 0.50 && iso_1 < 0.55)")
        sampMan.DefineAll("w_iso12", "(iso_1 > 0.55 && iso_1 < 0.60)")
        sampMan.DefineAll("w_iso13", "(iso_1 > 0.60 && iso_1 < 0.65)")

        """sampMan.DefineAll("w_iso5", "(relIso > 0.20 && relIso < 0.25)")
        sampMan.DefineAll("w_iso6", "(relIso > 0.25 && relIso < 0.30)")
        sampMan.DefineAll("w_iso7", "(relIso > 0.30 && relIso < 0.35)")
        sampMan.DefineAll("w_iso8", "(relIso > 0.35 && relIso < 0.40)")
        sampMan.DefineAll("w_iso9", "(relIso > 0.40 && relIso < 0.45)")
        sampMan.DefineAll("w_iso10", "(relIso > 0.45 && relIso < 0.50)")
        sampMan.DefineAll("w_iso11", "(relIso > 0.50 && relIso < 0.55)")
        sampMan.DefineAll("w_iso12", "(relIso > 0.55 && relIso < 0.60)")
        sampMan.DefineAll("w_iso13", "(relIso > 0.60 && relIso < 0.65)")"""
        
        isobins = ["w_iso4", "w_iso5", "w_iso6", "w_iso7", "w_iso8", "w_iso9", "w_iso10", "w_iso11", "w_iso12", "w_iso13"]
    else:
        # separate the EB and EE and correct the electron isolation
        # based on the EB and EE (because of a bug in the code)
        sampMan.DefineAll("isEB",   "fabs(Lep_eta) <= 1.4442")
        sampMan.DefineAll("RelIso", "isEB ? (relIso + 0.0287 - 0.0478) : (relIso + 0.0445 - 0.0658)")
        sampMan.DefineAll("w_iso4", "(RelIso > 0.15 && RelIso < 0.20)")
        sampMan.DefineAll("w_iso5", "(RelIso > 0.20 && RelIso < 0.25)")
        sampMan.DefineAll("w_iso6", "(RelIso > 0.25 && RelIso < 0.30)")
        sampMan.DefineAll("w_iso7", "(RelIso > 0.30 && RelIso < 0.35)")
        sampMan.DefineAll("w_iso8", "(RelIso > 0.35 && RelIso < 0.40)")
        sampMan.DefineAll("w_iso9", "(RelIso > 0.40 && RelIso < 0.45)")
        sampMan.DefineAll("w_iso10", "(RelIso > 0.45 && RelIso < 0.55)")
        sampMan.DefineAll("w_iso11", "(RelIso > 0.55 && RelIso < 0.70)")
        isobins = ["iso4", "iso5", "iso6", "iso7", "iso8", "iso9", "iso10", "iso11"]

    #sampMan.DefineMC("met_pt", "metVars[1]", excludes=['Data_aiso'])
    #sampMan.DefineMC("met_phi", "TVector2::Phi_mpi_pi(metVarsPhi[1])", excludes=['Data_aiso'])
    # Data does not run any recoil corrections
    #DataAisoSamp.Define("met_pt", "metVars[0]")
    #DataAisoSamp.Define("met_phi", "TVector2::Phi_mpi_pi(metVarsPhi[0])")

    sampMan.DefineAll("met_phi", "metphi_uncorrected")
    sampMan.DefineAll("met", "met_uncorrected")

    #MMET:
    sampMan.DefineAll("mtCorr", "mt_1")
    sampMan.DefineAll("ptOmT", "Lep_pt/mtCorr")

    #MM:
    #sampMan.DefineAll("mtCorr", "m_vis")
    #sampMan.DefineAll("ptOmT", "Lep_pt/m_vis")

    # recoil variables
    #sampMan.DefineAll("V2W", "UVec(pt_1, phi_1, met_pt, met_phi)")
    #sampMan.DefineAll("WpT", "V2W.Mod()")
    #sampMan.DefineAll("Wphi", "TVector2::Phi_mpi_pi(V2W.Phi())")

    # charge
    lepname = "mu" if doMuon else "e"
    sampMan.DefineAll(lepname+"plus",  "Lep_q > 0")
    sampMan.DefineAll(lepname+"minus", "Lep_q < 0")
    chgbins = [lepname+"plus", lepname + "minus"]

    # WpT bins
    #sampMan.DefineAll("WpT_bin0",  "WpT>=0.")
    sampMan.DefineAll("WpT_bin0",  "Lep_pt>=0.")  #TODO: Changes this generic binning
    wptbins = ["WpT_bin0"]

    # eta bins for electrons: barral and endcap
    sampMan.DefineAll("lepEta_bin0", "1.0")
    sampMan.DefineAll("lepEta_bin1", "abs(Lep_eta) <= 1.4442") 
    sampMan.DefineAll("lepEta_bin2", "abs(Lep_eta) > 1.4442")

    if doMuon:
        etabins = ["lepEta_bin0"]
    else:
        etabins = ["lepEta_bin0", "lepEta_bin1", "lepEta_bin2"]

    sampMan.DefineMC("Lep_trig_eff_data", "h_trig_eff_data->GetBinContent(\
        h_trig_eff_data->GetXaxis()->FindBin(Lep_q),\
        h_trig_eff_data->GetYaxis()->FindBin(TMath::Min((Float_t)2.3999, (Float_t)abs(Lep_eta))),\
        h_trig_eff_data->GetZaxis()->FindBin(TMath::Max((Float_t)26.001, TMath::Min((Float_t)199.999, (Float_t)Lep_pt)))\
    )")
    sampMan.DefineMC("Lep_trig_eff_mc", "h_trig_eff_mc->GetBinContent(\
        h_trig_eff_mc->GetXaxis()->FindBin(Lep_q),\
        h_trig_eff_mc->GetYaxis()->FindBin(TMath::Min((Float_t)2.3999, (Float_t)abs(Lep_eta))),\
        h_trig_eff_mc->GetZaxis()->FindBin(TMath::Max((Float_t)26.001, TMath::Min((Float_t)199.999, (Float_t)Lep_pt)))\
    )")
    sampMan.DefineMC("trig_eff_weight",
        "Lep_trig_eff_data / Lep_trig_eff_mc"
    )
    sampMan.DefineMC("weight_WoVpt", "weight_WoVpt_noTrigWeight*trig_eff_weight")

    for iso in isobins:
        for wpt in wptbins:
            for lepeta in etabins:
                for chg in chgbins:
                    #sampMan.DefineAll("weight_{}_{}_{}_{}".format(chg, iso,  wpt, lepeta), "w_{} * weight_WoVpt * {} * {} * {}".format(iso, wpt, lepeta, chg))
                    sampMan.DefineAll("weight_{}_{}_{}_{}".format(chg, iso,  wpt, lepeta), "{} * weight_WoVpt * {} * {} * {}".format(iso, wpt, lepeta, chg))
                    #sampMan.DefineAll("weight_{}_{}_{}_{}".format(chg, iso, wpt, lepeta), "w_{} * weight_{} * {} * {}".format(iso, chg, wpt, lepeta))

    nbins = 12*2
    xmin = 0
    xmax = 120

    """print(sampMan.mcs)
    print("sum of weight_WoVpt for data: ", sampMan.data.rdf.Sum("weight_WoVpt").GetValue())
    MCSsum = 0
    for i in range(len(sampMan.mcs)):
        MCSsum += sampMan.mcs[i].rdf.Sum("weight_WoVpt").GetValue()
        print(sampMan.mcs[i].rdf.Sum("weight_WoVpt").GetValue())
    print("sum of weight_WoVpt for mcs : ", MCSsum)
    print()
    print()
    print()"""

    for iso in isobins:
        for wpt in wptbins:
            for lepeta in etabins:
                for chg in chgbins:
                    #print("at line 251, broadcasting", iso, wpt, lepeta, chg)
                    strname = "weight_{}_{}_{}_{}".format(chg, iso, wpt, lepeta)

                    outputname = "histo_wjetsAntiIso_fullrange_mtcorr_" + strname 
                    sampMan.cacheDraw("mtCorr", outputname, nbins,  xmin, xmax, DrawConfig(xmin=xmin, xmax=xmax, xlabel="m_{T} [GeV]", dology=True, ymin=1,ymax=1e8, donormalizebin=False, addOverflow=False, addUnderflow=False, showratio=True), weightname = strname)
                    
                    outputname = "histo_wjetsAntiIso_fullrange_met_" + strname 
                    sampMan.cacheDraw("met", outputname, nbins,  xmin, xmax, DrawConfig(xmin=xmin, xmax=xmax, xlabel="MET [GeV]", dology=True, ymin=1,ymax=1e8, donormalizebin=False, addOverflow=False, addUnderflow=False, showratio=True), weightname = strname)

                    outputname = "histo_wjetsAntiIso_fullrange_ptOmT_" + strname 
                    sampMan.cacheDraw("ptOmT", outputname, nbins,  xmin, xmax, DrawConfig(xmin=xmin, xmax=xmax, xlabel="pT / mT [GeV]", dology=True, ymin=1,ymax=1e8, donormalizebin=False, addOverflow=False, addUnderflow=False, showratio=True), weightname = strname)
                    #outputname = "histo_wjetsAntiIso_fullrange_lepEta_" + strname
                    #sampMan.cacheDraw("Lep_eta", outputname, 24, -2.4, 2.4, DrawConfig(xmin=-2.4, xmax=2.4, xlabel="Lepton Eta", dology=True, ymax=2e6, donormalizebin=False, addOverflow=False, addUnderflow=False, showratio=True), weightname = strname)

    #cols = ROOT.vector('string')(); cols.push_back("Lep_eta");
    #d2 = Wl0AisoSamp.rdf.Display(cols)
    #d2.Print()

    strname = "weight_WoVpt"
    outputname = "histo_wjetsAntiIso_fullrange_lepEta_" + strname
    sampMan.cacheDraw("Lep_eta", outputname, 24, -2.4, 2.4, DrawConfig(xmin=-2.4, xmax=2.4, xlabel="Lepton Eta", dology=True, ymax=2e6, donormalizebin=False, addOverflow=False, addUnderflow=False, showratio=True), weightname = strname)

    print("Pre launch Draw")
    sampMan.launchDraw()
    print("Post launch Draw")


    hmts_comp = OrderedDict()
    for iso in isobins:
        for wpt in wptbins:
            for lepeta in etabins:
                for chg in chgbins:
                    strname = "weight_{}_{}_{}_{}".format(chg, iso, wpt, lepeta)
                    
                    # for mT
                    outputname = "histo_wjetsAntiIso_fullrange_mtcorr_" + strname
                    hstacked = THStack2TH1(sampMan.hsmcs[outputname])
                    for ibin in xrange(hstacked.GetNbinsX()+1):
                        # hstacked should always be above 0
                        hstacked.SetBinContent(ibin, max(hstacked.GetBinContent(ibin), 0))
                    sampMan.hdatas[outputname].Add( hstacked, -1.0 )
                    hmts_comp[strname] = sampMan.hdatas[outputname]
                    hmts_comp[strname].SetName(outputname)

                    """# for MET
                    outputname = "histo_wjetsAntiIso_fullrange_met_" + strname
                    hstacked = THStack2TH1(sampMan.hsmcs[outputname])
                    for ibin in xrange(hstacked.GetNbinsX()+1):
                        # hstacked should always be above 0
                        hstacked.SetBinContent(ibin, max(hstacked.GetBinContent(ibin), 0))
                    sampMan.hdatas[outputname].Add( hstacked, -1.0 )
                    hmts_comp[strname] = sampMan.hdatas[outputname]
                    hmts_comp[strname].SetName(outputname)

                    # for ptOmT
                    outputname = "histo_wjetsAntiIso_fullrange_ptOmT_" + strname
                    hstacked = THStack2TH1(sampMan.hsmcs[outputname])
                    for ibin in xrange(hstacked.GetNbinsX()+1):
                        # hstacked should always be above 0
                        hstacked.SetBinContent(ibin, max(hstacked.GetBinContent(ibin), 0))
                    sampMan.hdatas[outputname].Add( hstacked, -1.0 )
                    hmts_comp[strname] = sampMan.hdatas[outputname]
                    hmts_comp[strname].SetName(outputname)"""

                    ## for lepton eta with mT cuts
                    #strname += "_mtCut"
                    #outputname = "histo_wjetsAntiIso_fullrange_lepEta_" + strname
                    #hstacked = THStack2TH1(sampMan.hsmcs[outputname])
                    #for ibin in xrange(hstacked.GetNbinsX()+1):
                    #    # hstacked should always be above 0
                    #    hstacked.SetBinContent(ibin, max(hstacked.GetBinContent(ibin), 0))
                    #sampMan.hdatas[outputname].Add( hstacked, -1.0 )
                    #hetas_mtCut_comp[strname] = sampMan.hdatas[outputname]
                    #hetas_mtCut_comp[strname].SetName(outputname)

    if applyScaling:
        postfix = "nu_applyScaling.root"
    else:
        postfix = "nu.root"
    outfile = ROOT.TFile.Open("root/output_qcdshape_fullrange_"+lepname+"_"+postfix, "recreate")

    for variable in ["mtcorr", "met", "ptOmT"]:
        hmts_comp = OrderedDict()
        for iso in isobins:
            for wpt in wptbins:
                for lepeta in etabins:
                    for chg in chgbins:
                        strname = "weight_{}_{}_{}_{}".format(chg, iso, wpt, lepeta)

                        outputname = "histo_wjetsAntiIso_fullrange_"+variable+"_" + strname
                        hstacked = THStack2TH1(sampMan.hsmcs[outputname])
                        for ibin in xrange(hstacked.GetNbinsX()+1):
                            # hstacked should always be above 0
                            hstacked.SetBinContent(ibin, max(hstacked.GetBinContent(ibin), 0))
                        sampMan.hdatas[outputname].Add( hstacked, -1.0 )
                        hmts_comp[strname] = sampMan.hdatas[outputname]
                        hmts_comp[strname].SetName(outputname)

        odir = outfile.mkdir(variable)
        for wpt in wptbins:
            for iso in isobins[:-1]:
                for lepeta in etabins:
                    for chg in chgbins:
                        i = int(iso[5:])
                        iso_next = "w_iso" + str(i+1)
                        #strname = "weight_{}_{}_{}_{}".format(chg, iso, wpt, lepeta)
                        #strname_next = "weight_{}_{}_{}_{}".format(chg, iso_next, wpt, lepeta)
                        strname = "weight_{}_{}_{}_{}".format(chg, iso, wpt, lepeta)
                        strname_next = "weight_{}_{}_{}_{}".format(chg, iso_next, wpt, lepeta)
                        outputname = "histo_wjetsAntiIso_fullrange_"+ variable + "_" + strname

                        hcenter = hmts_comp[strname]
                        hup = hmts_comp[strname_next].Clone(outputname+"_shapeUp")
                        hdown = hmts_comp[strname_next].Clone(outputname+"_shapeDown")
                        hup.Scale(hcenter.Integral() / (hup.Integral()+1e-6))
                        for ibin in xrange(1, hcenter.GetNbinsX()+1):
                            center = hcenter.GetBinContent(ibin)
                            up = hup.GetBinContent(ibin)
                            hdown.SetBinContent(ibin, max(2*center - up, 0))

                            hcenter.SetBinContent(ibin, max(center, 0))
                            hup.SetBinContent(ibin, max(up, 0))
                        hcenter.SetDirectory(odir)
                        hcenter.Write()
                        hup.SetDirectory(odir)
                        hup.Write()
                        hdown.SetDirectory(odir)
                        hdown.Write()



    """for wpt in wptbins:
        odir = outfile.mkdir(wpt)
        outfile.cd(wpt)
        for iso in isobins[:-1]:
            # skip the last iso bin as it is used for the uncertaintiy of the previous iso bin
            for lepeta in etabins:
                for chg in chgbins:

                    i = int(iso[5:])
                    iso_next = "w_iso" + str(i+1)
                    #strname = "weight_{}_{}_{}_{}".format(chg, iso, wpt, lepeta)
                    #strname_next = "weight_{}_{}_{}_{}".format(chg, iso_next, wpt, lepeta)
                    strname = "weight_{}_{}_{}_{}".format(chg, iso, wpt, lepeta)
                    strname_next = "weight_{}_{}_{}_{}".format(chg, iso_next, wpt, lepeta)

                    #mtcorr
                    outputname = "histo_wjetsAntiIso_fullrange_mtcorr_" + strname

                    hcenter = hmts_comp[strname]
                    hup = hmts_comp[strname_next].Clone(outputname+"_shapeUp")
                    hdown = hmts_comp[strname_next].Clone(outputname+"_shapeDown")
                    hup.Scale(hcenter.Integral() / (hup.Integral()+1e-6))
                    for ibin in xrange(1, hcenter.GetNbinsX()+1):
                        center = hcenter.GetBinContent(ibin)
                        up = hup.GetBinContent(ibin)
                        hdown.SetBinContent(ibin, max(2*center - up, 0))

                        hcenter.SetBinContent(ibin, max(center, 0))
                        hup.SetBinContent(ibin, max(up, 0))
                    hcenter.SetDirectory(odir)
                    hcenter.Write()
                    hup.SetDirectory(odir)
                    hup.Write()
                    hdown.SetDirectory(odir)
                    hdown.Write()

                    #met
                    outputname = "histo_wjetsAntiIso_fullrange_met_" + strname

                    hcenter = hmts_comp[strname]
                    hup = hmts_comp[strname_next].Clone(outputname+"_shapeUp")
                    hdown = hmts_comp[strname_next].Clone(outputname+"_shapeDown")
                    hup.Scale(hcenter.Integral() / (hup.Integral()+1e-6))
                    for ibin in xrange(1, hcenter.GetNbinsX()+1):
                        center = hcenter.GetBinContent(ibin)
                        up = hup.GetBinContent(ibin)
                        hdown.SetBinContent(ibin, max(2*center - up, 0))

                        hcenter.SetBinContent(ibin, max(center, 0))
                        hup.SetBinContent(ibin, max(up, 0))
                    hcenter.SetDirectory(odir)
                    hcenter.Write()
                    hup.SetDirectory(odir)
                    hup.Write()
                    hdown.SetDirectory(odir)
                    hdown.Write()

                    #ptOmT
                    outputname = "histo_wjetsAntiIso_fullrange_ptOmT_" + strname

                    hcenter = hmts_comp[strname]
                    hup = hmts_comp[strname_next].Clone(outputname+"_shapeUp")
                    hdown = hmts_comp[strname_next].Clone(outputname+"_shapeDown")
                    hup.Scale(hcenter.Integral() / (hup.Integral()+1e-6))
                    for ibin in xrange(1, hcenter.GetNbinsX()+1):
                        center = hcenter.GetBinContent(ibin)
                        up = hup.GetBinContent(ibin)
                        hdown.SetBinContent(ibin, max(2*center - up, 0))

                        hcenter.SetBinContent(ibin, max(center, 0))
                        hup.SetBinContent(ibin, max(up, 0))
                    hcenter.SetDirectory(odir)
                    hcenter.Write()
                    hup.SetDirectory(odir)
                    hup.Write()
                    hdown.SetDirectory(odir)
                    hdown.Write()"""

    outfile.Close()


    sampMan.dumpCounts()

    print "Program end..."

    raw_input()
    
    return 

if __name__ == "__main__":
   main()
