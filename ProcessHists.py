import ROOT
import re
import numpy as np
from CMSPLOTS.myFunction import AddOverflowsTH1, RebinHisto
from modules.qcdExtrapolater import ExtrapolateQCD
from modules.cardMaker import MakeWJetsCards, MakeZJetsCards, GenerateRunCommand
from modules.histProcessor import ProcessHists, CopyandMergeTau
from modules.mass_bins import mass_bins
from collections import OrderedDict

ROOT.gROOT.SetBatch(True)


def RunPreparations(fwsig_input, fwsig_rebin, fwsig_mergeTau, fqcd_input, fqcd_rebin, fqcd_input_scaled, fqcd_rebin_scaled, fqcd_output, lepname = "mu", is5TeV = False, mass_bins = mass_bins, outdir_card = "cards", fzsig_input = None):
    """
    rebin the mT hists for sig and qcd bkg,
    merge tau (wx) process to sig (wlnu),
    exptrapolate the qcd shape from anti-isolated to isolated
    genereate datacard
    """
    includeUnderflow = False
    includeOverflow = True

    ProcessHists(fwsig_input, fwsig_rebin, mass_bins, includeUnderflow, includeOverflow)
    # merge the tau processes into the signal process
    CopyandMergeTau(fwsig_rebin, fwsig_mergeTau)

    # for QCD
    ProcessHists(fqcd_input, fqcd_rebin, mass_bins, includeUnderflow, includeOverflow)
    ProcessHists(fqcd_input_scaled, fqcd_rebin_scaled, mass_bins, includeUnderflow, includeOverflow)

    # extrapolate the QCD template from anti-isolated region to isolated region
    ExtrapolateQCD(fqcd_rebin, fqcd_output, [lepname+"plus", lepname+"minus"], "WpT_bin0", ["lepEta_bin0"], fname_scaled=fqcd_rebin_scaled, rebinned = True, is5TeV = is5TeV)

    # generate card based on the signal and qcd templates
    card_plus = MakeWJetsCards(fwsig_mergeTau, fqcd_output, lepname+"plus", "WpT_bin0", "lepEta_bin0", rebinned = True, nMTBins = len(mass_bins)-1, is5TeV = is5TeV, outdir = outdir_card)
    card_minus = MakeWJetsCards(fwsig_mergeTau, fqcd_output, lepname+"minus", "WpT_bin0", "lepEta_bin0", rebinned = True, nMTBins = len(mass_bins)-1, is5TeV = is5TeV, outdir = outdir_card)

    card_z = None
    if fzsig_input:
        # generate z card
        card_z = MakeZJetsCards(fzsig_input, lepname+lepname, rebinned = False, is5TeV = is5TeV, outdir = outdir_card)

    return card_plus, card_minus, card_z

if __name__  == "__main__":
    do13TeV = True
    do5TeV = False

    # scan fit range
    mass_bins_test = OrderedDict()
    mass_bins_test[0] = np.array([0., 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120])
    mass_bins_test[1] = np.array([5., 15, 25, 35, 45, 55, 65, 75, 85, 95, 105, 120])
    mass_bins_test[2] = np.array([10., 20, 30, 40, 50, 60, 70, 80, 90, 100, 120])
    mass_bins_test[3] = np.array([15., 25, 35, 45, 55, 65, 75, 85, 95, 105, 120])
    mass_bins_test[4] = np.array([20., 30, 40, 50, 60, 70, 80, 90, 100, 120])
    mass_bins_test[5] = np.array([25., 35, 45, 55, 65, 75, 85, 95, 105, 120])
    mass_bins_test[6] = np.array([30., 40, 50, 60, 70, 80, 90, 100, 120])
    mass_bins_test[7] = np.array([35., 45, 55, 65, 75, 85, 95, 105, 120])
    mass_bins_test[8] = np.array([40., 50, 60, 70, 80, 90, 100, 120])
    mass_bins_test[9] = np.array([45., 55, 65, 75, 85, 95, 105, 120])
    mass_bins_test[10] = np.array([50., 60, 70, 80, 90, 100, 120])

    if do13TeV:
        card_mu_plus = None
        card_mu_minus = None
        card_zmumu = None
        card_e_plus = None
        card_e_minus = None
        card_zee = None

        # 13TeV muon
        fzsig_mumu_input = "root/output_shapes_mumu.root"
        fzsig_ee_input = "root/output_shapes_ee.root"

        for key, val in mass_bins_test.items():
            # muon channel
            fwsig_input = "root/output_shapes_munu.root"
            fwsig_rebin = f"root/test{key}/output_shapes_munu_Rebin.root"
            fwsig_mergeTau = f"root/test{key}/output_shapes_munu_mergeTau.root"

            fqcd_input = "root/output_qcdshape_munu.root"
            fqcd_rebin = f"root/test{key}/output_qcdshape_munu_Rebin.root"
            fqcd_input_scaled = "root/output_qcdshape_munu_applyScaling.root"
            fqcd_rebin_scaled = f"root/test{key}/output_qcdshape_munu_Rebin_applyScaling.root"
            fqcd_output = f"root/test{key}/qcdshape_extrapolated_munu.root"

            card_mu_plus, card_mu_minus, card_zmumu = RunPreparations(fwsig_input, fwsig_rebin, fwsig_mergeTau, fqcd_input, fqcd_rebin, fqcd_input_scaled, fqcd_rebin_scaled, fqcd_output, "mu", outdir_card = f"cards/test{key}", mass_bins = val, fzsig_input=fzsig_mumu_input)

            # electron channel
            fwsig_input = "root/output_shapes_enu.root"
            fwsig_rebin = f"root/test{key}/output_shapes_enu_Rebin.root"
            fwsig_mergeTau = f"root/test{key}/output_shapes_enu_mergeTau.root"

            fqcd_input = "root/output_qcdshape_enu.root"
            fqcd_rebin = f"root/test{key}/output_qcdshape_enu_Rebin.root"
            fqcd_input_scaled = "root/output_qcdshape_enu_applyScaling.root"
            fqcd_rebin_scaled = f"root/test{key}/output_qcdshape_enu_Rebin_applyScaling.root"
            fqcd_output = f"root/test{key}/qcdshape_extrapolated_enu.root"

            card_e_plus, card_e_minus, card_zee = RunPreparations(fwsig_input, fwsig_rebin, fwsig_mergeTau, fqcd_input, fqcd_rebin, fqcd_input_scaled, fqcd_rebin_scaled, fqcd_output, "e", outdir_card = f"cards/test{key}", mass_bins = val, fzsig_input=fzsig_ee_input)

            # combine all datacard into a big fit
            GenerateRunCommand([card_mu_plus, card_mu_minus, card_zmumu, card_e_plus, card_e_minus, card_zee], ["muplus", "muminus", "zmumu", "eplus", "eminus", "zee"])


    if do5TeV:
        # 5TeV muon channel
        fwsig_input = "root/output_shapes_munu_5TeV.root"
        fwsig_rebin = "root/output_shapes_munu_Rebin_5TeV.root"
        fwsig_mergeTau = "root/output_shapes_munu_mergeTau_5TeV.root"

        fqcd_input = "root/output_qcdshape_munu_5TeV.root"
        fqcd_rebin = "root/output_qcdshape_munu_Rebin_5TeV.root"
        fqcd_input_scaled = "root/output_qcdshape_munu_applyScaling_5TeV.root"
        fqcd_rebin_scaled = "root/output_qcdshape_munu_Rebin_applyScaling_5TeV.root"
        fqcd_output = "root/qcdshape_extrapolated_munu_5TeV.root"

        RunPreparations(fwsig_input, fwsig_rebin, fwsig_mergeTau, fqcd_input, fqcd_rebin, fqcd_input_scaled, fqcd_rebin_scaled, fqcd_output, "mu", is5TeV = True)


        # 5TeV electron channel
        fwsig_input = "root/output_shapes_enu_5TeV.root"
        fwsig_rebin = "root/output_shapes_enu_Rebin_5TeV.root"
        fwsig_mergeTau = "root/output_shapes_enu_mergeTau_5TeV.root"

        fqcd_input = "root/output_qcdshape_enu_5TeV.root"
        fqcd_rebin = "root/output_qcdshape_enu_Rebin_5TeV.root"
        fqcd_input_scaled = "root/output_qcdshape_enu_applyScaling_5TeV.root"
        fqcd_rebin_scaled = "root/output_qcdshape_enu_Rebin_applyScaling_5TeV.root"
        fqcd_output = "root/qcdshape_extrapolated_enu_5TeV.root"

        RunPreparations(fwsig_input, fwsig_rebin, fwsig_mergeTau, fqcd_input, fqcd_rebin, fqcd_input_scaled, fqcd_rebin_scaled, fqcd_output, "e", is5TeV = True)

