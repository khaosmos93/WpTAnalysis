import ROOT
import numpy as np
from collections import OrderedDict
import sys
sys.path.append("/uscms_data/d3/yfeng/CMSPLOTS")
from tdrstyle import setTDRStyle
from myFunction import DrawHistos, THStack2TH1
import CMS_lumi
import pickle

from SampleManager import DrawConfig, Sample, SampleManager

ROOT.gROOT.SetBatch(True)
ROOT.ROOT.EnableImplicitMT(10)

dotest = 1
VetoB = False
doSys = False

def main():
    print "Program start..."

    #ROOT.gROOT.ProcessLine('TFile* f_zpt = TFile::Open("results/zpt_weight.root")')
    #ROOT.gROOT.ProcessLine('TH1D* h_zpt_ratio  = (TH1D*)f_zpt->Get("h_zpt_ratio")')

    if dotest:
        input_data    = "inputs/zmumu/input_data.txt"
        input_dy      = "inputs/zmumu/input_zjets.txt"
        input_ttbar   = "inputs/zmumu/input_ttbar_dilepton.txt"
    else:
        input_data    = "inputs/zmumu/input_data.txt"
        input_dy      = "inputs/zmumu/input_zjets.txt"
        input_ttbar   = "inputs/zmumu/input_ttbar_dilepton.txt"
        input_ttbar_1lep = "inputs/zmumu/input_ttbar_singlelepton.txt"
        input_ttbar_0lep = "inputs/zmumu/input_ttbar_hadronic.txt"
        input_ww      = "inputs/zmumu/input_ww.txt"
        input_wz      = "inputs/zmumu/input_wz.txt"
        input_zz      = "inputs/zmumu/input_zz.txt"
        input_zxx     = "inputs/zmumu/input_zxx.txt"

    DataSamp  = Sample(input_data, isMC=False, legend="Data", name="Data", bjetVeto=VetoB)
    DYSamp    = Sample(input_dy,    xsec = 6077.22*1e3,      color=92,  reweightzpt = True, legend="Z#rightarrow#mu#mu", name="DY", bjetVeto=VetoB, isNLO=True)
    TTbarSamp = Sample(input_ttbar, xsec = 831.76*0.105*1e3, color=46, reweightzpt = False, legend="t#bar{t}", name="ttbar2lep", bjetVeto=VetoB)
    if not dotest:
        WWSamp  = Sample(input_ww,  xsec = 12.178*1e3,       color=38, reweightzpt = False, legend="WW2L",     name="WW",  bjetVeto=VetoB, nmcevt=1000000.0 )
        WZSamp  = Sample(input_wz,  xsec = 5.26*1e3,         color=39, reweightzpt = False, legend="WZ3L",     name="WZ",  bjetVeto=VetoB, nmcevt=885000.00 )
        ZZSamp  = Sample(input_zz,  xsec = 0.564*1e3,        color=37, reweightzpt = False, legend="ZZ2L",     name="ZZ",  bjetVeto=VetoB, nmcevt=1000000.0)
        ZXXSamp = Sample(input_zxx, xsec = 1.0,              color=40, reweightzpt = False, legend="ZXX",      name="ZXX",   bjetVeto=VetoB, nmcevt=3.1146101e+11)
        TT1LepSamp = Sample(input_ttbar_1lep,  xsec = 831.76*0.219*1e3, color=47, reweightzpt = False, legend="t#bar{t}", name="ttbar1lep", bjetVeto=VetoB, nmcevt=1.2561491e+09 / 335.0 * 325.0)
        TT0LepSamp = Sample(input_ttbar_0lep,  xsec = 831.76*0.219*1e3, color=48, reweightzpt = False, legend="t#bar{t}", name="ttbar0lep", bjetVeto=VetoB, nmcevt=6.2414786e+09 / 335.0 * 325)

    if not dotest:
        sampMan = SampleManager(DataSamp, [DYSamp, TTbarSamp, WWSamp, WZSamp, ZZSamp, ZXXSamp, TT1LepSamp, TT0LepSamp])
    else:
        sampMan = SampleManager(DataSamp, [DYSamp, TTbarSamp])
    #sampMan.groupMCs(["WW", "WZ", "ZZ", "ZXX"], "EWK", 216, "EWK")
    #sampMan.groupMCs(["ttbar2lep", "ttbar1lep", "ttbar0lep"], "ttbar", 96, "t#bar{t}")
    # this need fix!!!!
    DYSamp.ApplyCut("nMuon>=2")
    ##sampMan.groupMCs(["WW", "WZ", "ZZ", "ZXX"], "EWK", 216, "EWK")
    ##sampMan.groupMCs(["ttbar2lep", "ttbar1lep", "ttbar0lep"], "ttbar", 96, "t#bar{t}")
    sampMan.DefineAll("lep1_corr", "VLep(Muon_corrected_pt[0], Muon_eta[0], Muon_phi[0], 0.)")
    sampMan.DefineAll("lep2_corr", "VLep(Muon_corrected_pt[1], Muon_eta[1], Muon_phi[1], 0.)")
    sampMan.DefineAll("Z", "(lep1_corr + lep2_corr)")
    sampMan.DefineAll("zmass", "Z.M()")
    sampMan.ApplyCutAll("zmass > 60.0 && zmass < 120.0")

    sampMan.DefineAll("zpt", "Z.Pt()")
    sampMan.DefineAll("zy",  "Z.Rapidity()")
    sampMan.DefineAll("zeta",  "Z.Rapidity()")
    sampMan.DefineAll("zphi", "Z.Phi()")

    sampMan.DefineAll("urawvec", "UVec(zpt, zphi, MET_pt, MET_phi)")
    sampMan.DefineAll("uraw_pt",  "urawvec.Mod()")
    sampMan.DefineAll("uraw_phi", "urawvec.Phi()")
    sampMan.DefineAll("uraw1",    "uraw_pt * TMath::Cos(uraw_phi + TMath::Pi() - zphi)")
    sampMan.DefineAll("uraw2",    "uraw_pt * TMath::Sin(uraw_phi + TMath::Pi() - zphi)")

    sampMan.DefineAll("uvec", "UVec(zpt, zphi, MET_corrected_pt, MET_corrected_phi)")
    sampMan.DefineAll("u_pt",  "uvec.Mod()")
    sampMan.DefineAll("u_phi", "uvec.Phi()")
    sampMan.DefineAll("ucor1",    "u_pt * TMath::Cos(u_phi + TMath::Pi() - zphi)")
    sampMan.DefineAll("ucor2",    "u_pt * TMath::Sin(u_phi + TMath::Pi() - zphi)")

    sampMan.DefineAll("LeadMuon_pt",     "Muon_corrected_pt[0]")
    sampMan.DefineAll("LeadMuon_eta",    "Muon_eta[0]")
    sampMan.DefineAll("SubleadMuon_pt",  "Muon_corrected_pt[1]")
    sampMan.DefineAll("SubleadMuon_eta", "Muon_eta[1]")

    #DYSamp.Define("u_pt_corr_central", "TMath::Sqrt(u1_corr_central*u1_corr_central + u2_corr_central*u2_corr_central)")
    #sampMan.DefineAll("u1_corr_central",     "u1"  , excludes=['DY'])


    met_pt_bins = np.array([0., 2.0, 4., 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 33, 36, 39, 42, 45, 48, 51, 55, 60, 65, 70, 75, 80, 90, 100, 110, 120, 135, 150, 165, 180, 200])
    u1_bins = np.array([-20.0, -16, -12, -10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 53, 56, 59, 64, 68, 72, 76, 80, 85, 90, 100])
    u2_bins = np.array([-40, -35, -30, -25., -22., -20, -18, -16, -14, -12, -10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10, 12, 16, 18, 20, 22, 25, 30, 35, 40])
    #u_bins = np.array([0., 2., 4., 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 43, 46, 49, 52, 56, 60, 64, 68, 72, 76, 80, 85, 90, 95, 100, 105, 110, 115, 120, 130, 140, 150])
    phimin = -ROOT.TMath.Pi()
    phimax = ROOT.TMath.Pi()

    eta_bins = np.concatenate((np.linspace(-2.4, -2.0, 3),np.linspace(-1.8,1.8,37), np.linspace(2.0, 2.4, 3)))
    pt_bins = np.concatenate((np.linspace(25, 35, 6),np.linspace(36,55,20), np.linspace(57, 63, 4), np.linspace(66,70,2)))
    mass_bins = np.concatenate((np.linspace(70, 76, 3),np.linspace(78,86,5), np.linspace(87, 96, 10), np.linspace(98,104,5), np.linspace(106, 110, 2)))
    u_bins = np.concatenate((np.linspace(0, 20, 11),np.linspace(24,80,15), np.linspace(85, 109, 4), np.linspace(120,150,3)))

    # z pt befor and after pt reweighting
    sampMan.cacheDraw("zpt",   "histo_zjets_zpt_WoZptWeight_mumu", u_bins, DrawConfig(xmin=0, xmax=150, xlabel='p_{T}^{#mu#mu} [GeV]'), weightname="weight_WoVpt")
    sampMan.cacheDraw("zmass", "histo_zjets_zmass_mumu", mass_bins, DrawConfig(xmin=70, xmax=110, xlabel='m_{#mu#mu} [GeV]'))
    sampMan.cacheDraw("zeta",  "histo_zjets_zeta_mumu", eta_bins, DrawConfig(xmin=-2.5, xmax=2.5, xlabel='#eta_{#mu#mu} [GeV]', ymax=1e7, ylabel='Events / 1'))
    sampMan.cacheDraw("zy",    "histo_zjets_zrapidity_mumu", eta_bins, DrawConfig(xmin=-2.5, xmax=2.5, xlabel='y_{#mu#mu} [GeV]', ymax=1e7, ylabel='Events / 1'))

    #sampMan.cacheDraw("nPV", "histo_nPV_mumu", 10, 0, 10, DrawConfig(xmin=0, xmax=10, xlabel='# PV', ylabel='Events / 1'))

    sampMan.cacheDraw("LeadMuon_pt", "histo_leadMuon_pt_mumu", pt_bins, DrawConfig(xmin=20, xmax=70, xlabel='p_{T}(Leading #mu) [GeV]'))
    sampMan.cacheDraw("LeadMuon_eta", "histo_leadMuon_eta_mumu", eta_bins, DrawConfig(xmin=-2.6, xmax=2.6, xlabel='#eta (Leading #mu) [GeV]', ymax=1e7, ylabel='Events / 1'))
    sampMan.cacheDraw("SubleadMuon_pt", "histo_subleadMuon_pt_mumu", pt_bins, DrawConfig(xmin=20, xmax=70, xlabel='p_{T}(Subleading #mu) [GeV]'))
    sampMan.cacheDraw("SubleadMuon_eta", "histo_subleadMuon_eta_mumu", eta_bins, DrawConfig(xmin=-2.6, xmax=2.6, xlabel='#eta (Subleading #mu) [GeV]', ymax=1e7, ylabel='Events / 1'))

    sampMan.cacheDraw("MET_pt", "histo_zjets_mumu_pfmet_pt", met_pt_bins, DrawConfig(xmin=0, xmax=100, xlabel='PF MET [GeV]'))
    sampMan.cacheDraw("MET_phi", "histo_zjets_mumu_pfmet_phi", 30, phimin, phimax, DrawConfig(xmin=phimin, xmax=phimax, xlabel='PF MET #phi'))

    sampMan.cacheDraw("MET_corrected_pt", "histo_zjets_mumu_pfmet_corrected_pt", met_pt_bins, DrawConfig(xmin=0, xmax=100, xlabel='PF MET [GeV]'))
    sampMan.cacheDraw("MET_corrected_phi", "histo_zjets_mumu_pfmet_corrected_phi", 30, phimin, phimax, DrawConfig(xmin=phimin, xmax=phimax, xlabel='PF MET #phi'))

    sampMan.cacheDraw("uraw1", "histo_zjets_mumu_pfmet_uraw1_pt", u1_bins, DrawConfig(xmin=-20.0, xmax=100.0, xlabel="Raw u_{#parallel} [GeV]", extraText='#mu#mu channel'))
    sampMan.cacheDraw("uraw2", "histo_zjets_mumu_pfmet_uraw2_pt", u2_bins, DrawConfig(xmin=-30.0, xmax=30.0, xlabel= "Raw u_{#perp  } [GeV]", extraText='#mu#mu channel'))

    sampMan.cacheDraw("ucor1", "histo_zjets_mumu_pfmet_ucor1_pt", u1_bins, DrawConfig(xmin=-20.0, xmax=100.0, xlabel="u_{#parallel} [GeV]", extraText='#mu#mu channel'))
    sampMan.cacheDraw("ucor2", "histo_zjets_mumu_pfmet_ucor2_pt", u2_bins, DrawConfig(xmin=-30.0, xmax=30.0, xlabel= "u_{#perp  } [GeV]", extraText='#mu#mu channel'))

    sampMan.launchDraw()

    sampMan.dumpCounts()

    print "Program end..."

    raw_input()
    
    return 

if __name__ == "__main__":
   main()
