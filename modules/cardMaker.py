"""
code to generate the W(lnv) cards for tfCombine. 
"""

from collections import OrderedDict
from modules.Binnings import Vptbins
from re import A
import ROOT
import os

class Process(object):
    """
    define one process and related information for the cards
    """
    def __init__(self,**kwargs):
        self.name = kwargs.get('name', 'sig')
        self.hname = kwargs.get('hname', 'htest')
        self.hsys  = kwargs.get('hsys', 'htest_sys')
        self.isObs = kwargs.get('isObs', False) # if it is the observation
        self.isSignal = kwargs.get('isSignal', False) # no contraint on the strength if true
        self.rate = kwargs.get('rate', -1.0)
        self.isMC = kwargs.get('isMC', False) # contraint on lumi if true
        self.isV = kwargs.get('isV', False) # recoil sys if true
        self.isQCD = kwargs.get('isQCD', False) # fake QCD
        self.xsecUnc = kwargs.get('xsecUnc', "0.10") # uncertainty on the cross section

        # a bit hacky, to point to the correct file location
        # - by default the fits run on lpc
        prefix_LPC = "/uscms/home/yfeng/nobackup/WpT/Cards/TestCode/WpTAnalysis/"
        self.fname = prefix_LPC + kwargs.get('fname', 'test.root')

        #  regulation
        if self.isObs:
            self.isSignal = False
            self.isMC = False
            self.isV = False
            self.isQCD = False
            self.xsecUnc = "-1.0"

        if self.isSignal:
            self.isMC = True # signal process is always uing MC template
            self.isV = True
            self.isQCD = False
            self.xsecUnc = "-1.0"

        if self.isQCD:
            self.isMC = False # QCD is always using data driven
            self.isV = False
            self.xsecUnc = "-1.0"


class Nuisance(object):
    """
    define one nuisance and related information for making cards
    """
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'lumi')
        self.type = kwargs.get('type', 'lnN')
        assert self.type in ['lnN', 'shape'], "Nuisance type can only be lnN or shape"
        # valuemap saves how much one process is affected by the nuisance parameter
        # key is the process name, value is the uncertainty
        self.valuemap = kwargs.get('valuemap', {})
    
    def __getitem__(self, key):
        return self.valuemap.get(key, '-')
    
    def __setitem__(self, key, val):
        self.valuemap[key] = val


def WriteCard(data, processes, nuisgroups, cardname):
    """
    write the datacard provided with data, processes, and nuisances
    """
    dirpath = cardname.rpartition('/')[0]
    if not os.path.exists(dirpath):
        print(f"Make the directory {dirpath}")
        os.makedirs(dirpath)

    ofile = open(cardname, "w")
    ofile.write("imax 1 number of channels\n")
    ofile.write("jmax {} number of processes -1\n".format(len(processes)-1))
    ofile.write("kmax * number of nuisance parameters\n\n")
    # observation
    ofile.write("Observation -1\n\n")
    if data:
        # for signal mc xsec cards, no data entry
        ofile.write("shapes {pname:<30} * {fname:<40} {hname:<50}\n".format(pname = "data_obs", fname = data.fname, hname = data.hname))

    for proc in processes:
        ofile.write("shapes {pname:<30} * {fname:<40} {hname:<50} {hsys}$SYSTEMATIC\n".format(pname = proc.name, fname = proc.fname, hname = proc.hname, hsys = proc.hsys))
    ofile.write("\n")

    ofile.write("{:<40}".format("bin"))
    for proc in processes:
        # one data card is one bin
        ofile.write(" {binname:<10}".format(binname="bin1"))
    ofile.write("\n")

    ofile.write("{:<40}".format("process"))
    for proc in processes:
        ofile.write(" {pname:<10}".format(pname=proc.name))
    ofile.write("\n")

    ofile.write("{:<40}".format("process"))
    isig = 0
    ibkg = 1
    for proc in processes:
        if proc.isSignal or proc.isQCD:
            ofile.write(f" {isig:<10}")
            isig -= 1
        else:
            ofile.write(f" {ibkg:<10}")
            ibkg += 1
    ofile.write("\n")

    ofile.write("{:<40}".format("rate"))
    for proc in processes:
        ofile.write(" {:<10}".format("-1.0"))
    ofile.write("\n\n")

    ## write out all systematics
    for nuisgroup in nuisgroups.values():
        for nuis in nuisgroup:
            ofile.write(f"{nuis.name:<30} {nuis.type:<10}")
            for proc in processes:
                ofile.write(" {:<10}".format(nuis[proc.name]))
            ofile.write("\n")
    ofile.write("\n")

    # write out nuisance groups
    for gname, gnuisances in nuisgroups.items():
        ofile.write(f"{gname:<30} group =")
        for nuis in gnuisances:
            ofile.write(f" {nuis.name}")
        ofile.write("\n")

    ofile.close()
    

def MakeWJetsCards(fname_mc, fname_qcd, channel, wptbin, etabin, doWpT = False, rebinned = False, is5TeV = False, nMTBins = 9, outdir = "cards", applyLFU = False):
    # prefix of all histo names
    prefix = ""
    if rebinned:
        prefix = "Rebinned_"

    # from lumi    
    unc_lumi = {}
    unc_lumi['lumi_13TeV'] = 1.017
    unc_lumi['lumi_5TeV'] = 1.019

    # from eff calculations
    unc_effstat = {}
    unc_effstat['effstat_muplus_13TeV'] = 1.0022
    unc_effstat['effstat_muminus_13TeV'] = 1.0021
    unc_effstat['effstat_eplus_13TeV'] = 1.0059
    unc_effstat['effstat_eminus_13TeV'] = 1.0053
    unc_effstat['effstat_muplus_5TeV'] = 1.0023
    unc_effstat['effstat_muminus_5TeV'] = 1.0021
    unc_effstat['effstat_eplus_5TeV'] = 1.0080
    unc_effstat['effstat_eminus_5TeV'] = 1.0077

    # data
    data = Process(name = "data_obs", fname = fname_mc,
                   hname = prefix + "histo_wjets_{}_mT_1_{}_{}_data".format(channel, wptbin, etabin),
                   isObs = True,
                   )
    # sig processes
    sigs = []
    if not doWpT:
        sig = Process(name = GetSigName(channel, applyLFU), fname = fname_mc, 
                     hname = prefix + "histo_wjets_{}_mT_1_{}_{}_grouped_wsig".format( channel, wptbin, etabin),
                     hsys  = prefix + "histo_wjets_{}_mT_1_{}_{}_grouped_wsig_".format(channel, wptbin, etabin),
                     isSignal = True,
                     isMC = True,
                     isV = True,
                     isQCD = False
                     ) 
        sigs.append(sig)
    else:
        wpttruthbins  = ["WpT_truth_bin1", "WpT_truth_bin2", "WpT_truth_bin3", "WpT_truth_bin4", "WpT_truth_bin5", "WpT_truth_bin6", "WpT_truth_bin7", "WpT_truth_bin8", "WpT_truth_bin9"]
        for wpttruthbin in wpttruthbins:
            sig = Process(name = channel+"_"+wpttruthbin+"_sig", fname = fname_mc,
                     hname = prefix + "histo_wjets_{}_mT_1_{}_{}_{}_signalMC".format( wpttruthbin, channel, wptbin, etabin, wpttruthbin),
                     hsys  = prefix + "histo_wjets_{}_mT_1_{}_{}_{}_signalMC_".format(wpttruthbin, channel, wptbin, etabin, wpttruthbin),
                     isSignal = True,
                     isMC = True,
                     isV = True,
                     isQCD = False
                     )
            sigs.append(sig)

    # ttbar bkg
    sname = "ttbar3" if not is5TeV else "ttbar1"
    ttbar = Process(name = "tt", fname = fname_mc,
                    hname = prefix + "histo_wjets_{}_mT_1_{}_{}_grouped_{}".format(channel, wptbin, etabin, sname),
                    hsys  = prefix + "histo_wjets_{}_mT_1_{}_{}_grouped_{}_".format(channel, wptbin, etabin, sname),
                    isSignal = False,
                    isMC = True,
                    isV = False,
                    isQCD = False,
                    xsecUnc = "1.10"
                )
    # Z bkg
    sname = "zxx9" if not is5TeV else "zxx6"
    zxx = Process(name = "zxx", fname = fname_mc,
                  hname = prefix + "histo_wjets_{}_mT_1_{}_{}_grouped_{}".format(channel, wptbin, etabin, sname),
                  hsys  = prefix + "histo_wjets_{}_mT_1_{}_{}_grouped_{}_".format(channel, wptbin, etabin, sname),
                  isSignal = False,
                  isMC = True,
                  isV = True,
                  isQCD = False,
                  xsecUnc = "1.03"
                  )
    # W->tau + nu bkg
    sname = "wx10" if not is5TeV else "wx7"
    wtau = Process(name = "taunu", fname = fname_mc,
                   hname = prefix + "histo_wjets_{}_mT_1_{}_{}_grouped_{}".format(channel, wptbin, etabin, sname),
                   hsys  = prefix + "histo_wjets_{}_mT_1_{}_{}_grouped_{}_".format(channel, wptbin, etabin, sname),
                   isSignal = False,
                   isMC = True,
                   isV = True,
                   isQCD = False,
                   xsecUnc = "1.10"
                )
    # VV bkg
    sname = "vv6" if not is5TeV else "vv2"
    vv = Process(name = "VV", fname = fname_mc,
                 hname = prefix + "histo_wjets_{}_mT_1_{}_{}_grouped_{}".format(channel, wptbin, etabin, sname),
                 hsys  = prefix + "histo_wjets_{}_mT_1_{}_{}_grouped_{}_".format(channel, wptbin, etabin, sname),
                 isSignal = False,
                 isMC = True,
                 isV = False,
                 isQCD = False,
                 xsecUnc = "1.10"
                 )
    # QCD bkg
    qcd = Process(name = "QCD_"+channel+"_"+etabin+"_"+wptbin, fname = fname_qcd,
                  hname = "h_QCD_Extrapolated_{}_{}_{}".format(channel, etabin, wptbin),
                  #hsys = "h_QCD_Extrapolated_{}_lepEta_".format(channel),
                  hsys = "h_QCD_Extrapolated_",
                  isSignal = False,
                  isMC = False,
                  isV = False,
                  isQCD = True,
                )

    # list of all processes
    #processes = sigs + [ttbar, zxx, wtau, vv, qcd]
    processes = sigs + [ttbar, zxx, vv, qcd]
    
    lepname = "mu" if "mu" in channel else "e"
    era = "13TeV" if not is5TeV else "5TeV"

    # define different nuisance parameters, their groups,
    # and the impacts on each process
    nuisgroups = OrderedDict()

    nuis_lumi = Nuisance(name = "lumi_" + era, type = "lnN")
    for proc in processes:
        if proc.isMC:
            nuis_lumi[proc.name] = unc_lumi[nuis_lumi.name]
    nuisgroups["lumi"] = [nuis_lumi]

    nuisgroups["mcsec"] = []
    for proc in processes:
        if not proc.isSignal and proc.isMC:
            nuis_norm = Nuisance(name = "norm_" + proc.name, type = "lnN")
            nuis_norm[proc.name] = proc.xsecUnc
            nuisgroups["mcsec"].append(nuis_norm)

    # correction systematics
    # in Aram's ntuples, defined here: https://github.com/MiT-HEP/MitEwk13TeV/blob/CMSSW_94X/NtupleMod/eleNtupleMod.C#L71
    # and here: https://github.com/MiT-HEP/MitEwk13TeV/blob/CMSSW_94X/NtupleMod/muonNtupleMod.C#L81
    # 1 is MC, 2 is FSR, 3 is Bkg, 4 is tagpt, 
    # 8 is ecal prefire
    # 10 is muon prefire
    # correlate MC systematic, ECAL and muon prefire 
    # between electron and muon channel
    # uncorrelate FSR, bkg, tagpt in electron ahd muon channel
    nuis_SysWeight1 = Nuisance(name = "SysWeight1", type = "shape")
    nuis_SysWeight2 = Nuisance(name = lepname + "_SysWeight2", type = "shape")
    nuis_SysWeight3 = Nuisance(name = lepname + "_SysWeight3", type = "shape")
    nuis_SysWeight4 = Nuisance(name = lepname + "_SysWeight4", type = "shape")
    #nuis_Sysweight5 = Nuisance(name = channel + "_SysWeight5", type = "shape")
    nuis_SysWeight8 = Nuisance(name = "SysWeight8", type = "shape")
    nuis_SysWeight10 = Nuisance(name = "SysWeight10", type = "shape")
    nuisgroups["effsys"] = [nuis_SysWeight1, nuis_SysWeight2, nuis_SysWeight3, nuis_SysWeight4]
    nuisgroups["prefire"] = [nuis_SysWeight8, nuis_SysWeight10]
    #nuisgroups["sfsys"].append(nuis_Sysweight5)
    for proc in processes:
        if not proc.isQCD:
            # all the samples except the QCD apply the corrections
            # so they should be affected by sf systematics
            for sysweight in nuisgroups["effsys"] + nuisgroups["prefire"]:
                sysweight[proc.name] = 1.0

    nuis_effstat = Nuisance(name = "effstat_" + channel + "_" + era, type = "lnN")
    for proc in processes:
        if proc.isSignal:
            # only apply eff/sf stat uncertainty to signals for now
            nuis_effstat[proc.name] = unc_effstat[nuis_effstat.name]
    nuisgroups["effstat"] = [nuis_effstat]

    # recoil correction systematics
    # in Aram's ntuples, defined here: https://github.com/MiT-HEP/MitEwk13TeV/blob/CMSSW_94X/NtupleMod/eleNtupleMod.C#L65
    # 1 is central correction, 2 is correction with different eta bins, 3 is correction using Gaussian kernels, 
    # 6-15 are corrections with different statistical uncertainties
    nuisgroups["recoil"] = []
    recoil_indices = ["2", "3", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"]
    for iuvar in recoil_indices:
        nuis_SysRecoil = Nuisance(name = lepname + "_SysRecoil" + iuvar, type = "shape")
        for proc in processes:
            if proc.isV:
                # all the V processes (including W and Z) apply the recoil corrections
                nuis_SysRecoil[proc.name] = 1.0
        nuisgroups["recoil"].append(nuis_SysRecoil)

    # qcd stat
    # this is hard coded for now. Will be improved later
    nuisgroups["qcdbkg"] = []
    prefix = channel + "_" + etabin + "_" + wptbin
    nbins = nMTBins
    for ibin in range(1, nbins+1):
        nuis_QCDStat = Nuisance(name = prefix + f"_bin{ibin}shape", type = "shape")
        for proc in processes:
            if proc.isQCD:
                nuis_QCDStat[proc.name] = 1.0
        nuisgroups["qcdbkg"].append(nuis_QCDStat)

    if True:
        nuis_QCDMCCont = Nuisance(name = prefix + "_ScaledMCshape", type = "shape")
        for proc in processes:
            if proc.isQCD:
                nuis_QCDMCCont[proc.name] = 1.0
        nuisgroups["qcdbkg"].append(nuis_QCDMCCont)

    # theory systematics
    # qcd scale
    nuisgroups["qcdscale"] = []
    for wpt in range(len(Vptbins)-1):
        for par in ["MuF", "MuR", "MuFMuR"]:
            nuis_QCDScale = Nuisance(name = par+str(wpt), type = "shape")
            for proc in processes:
                if proc.isSignal:
                    nuis_QCDScale[proc.name] = 1.0
            nuisgroups["qcdscale"].append(nuis_QCDScale)

    # pdf + alphaS variations
    nuisgroups["pdfalphaS"] = []
    pdf_indices = list(range(1, 101))
    for ipdf in pdf_indices:
        nuis_PDF = Nuisance(name = f"PDF{ipdf}", type = "shape")
        for proc in processes:
            if proc.isSignal:
                nuis_PDF[proc.name] = 1.0
        nuisgroups["pdfalphaS"].append(nuis_PDF)
    
    # alphaS variations
    nuis_alphaS = Nuisance(name = "alphaS", type = "shape")
    for proc in processes:
        if proc.isSignal:
            nuis_alphaS[proc.name] = 1.0
    nuisgroups["pdfalphaS"].append(nuis_alphaS)

    # tau fraction variation in the signal process
    #nuis_TauFrac = Nuisance(name = "SysTauFrac", type = "shape")
    #for proc in processes:
    #    if proc.isSignal:
    #        nuis_TauFrac[proc.name] = 1.0
    #nuisgroups["othersys"] = [nuis_TauFrac]

    #
    # writing datacards
    #
    cardname = f"{outdir}/datacard_{channel}_{etabin}_{wptbin}.txt"
    if is5TeV:
        cardname = f"{outdir}/datacard_{channel}_{etabin}_{wptbin}_5TeV.txt"
    WriteCard(data, processes, nuisgroups, cardname)

    return cardname


def MakeZJetsCards(fname, channel, rebinned = False, is5TeV = False, outdir = "cards", applyLFU = False):
    """
    Generate the combine datacard for Z+jets signal region
    """
    # prefix of all histo names
    prefix = ""
    if rebinned:
        prefix = "Rebinned_"

    # from lumi    
    unc_lumi = {}
    unc_lumi['lumi_13TeV'] = 1.017
    unc_lumi['lumi_5TeV'] = 1.019

    # from eff calculations
    unc_effstat = {}
    unc_effstat['effstat_muplus_13TeV'] = 1.0020
    unc_effstat['effstat_muminus_13TeV'] = 1.0020
    unc_effstat['effstat_eplus_13TeV'] = 1.0041
    unc_effstat['effstat_eminus_13TeV'] = 1.0041
    unc_effstat['effstat_muplus_5TeV'] = 1.0019
    unc_effstat['effstat_muminus_5TeV'] = 1.0019
    unc_effstat['effstat_eplus_5TeV'] = 1.0061
    unc_effstat['effstat_eminus_5TeV'] = 1.0061

    # data
    data = Process(name = "data_obs", fname = fname,
                   hname = prefix + f"histo_zjets_zmass_{channel}_weight_0_data",
                   isObs = True,
                   )
    # sig processes
    sigs = []
    sig = Process(name = GetSigName(channel ,applyLFU), fname = fname, 
                 hname = prefix + f"histo_zjets_zmass_{channel}_weight_0_grouped_DY0",
                 hsys = prefix + f"histo_zjets_zmass_{channel}_weight_0_grouped_DY0_",
                 isSignal = True,
                 isMC = True,
                 isV = True,
                 isQCD = False
                 ) 
    sigs.append(sig)

    # ttbar bkg
    sname = "ttbar1" if not is5TeV else "ttbar1"
    ttbar = Process(name = "tt", fname = fname,
                    hname = prefix + f"histo_zjets_zmass_{channel}_weight_0_grouped_ttbar1",
                    hsys = prefix + f"histo_zjets_zmass_{channel}_weight_0_grouped_ttbar1_",
                    isSignal = False,
                    isMC = True,
                    isV = False,
                    isQCD = False,
                    xsecUnc = "1.10"
                )
    # EWK bkg
    sname = "EWK2" if not is5TeV else "EWK2"
    ewk = Process(name = "EWK", fname = fname,
                 hname = prefix + f"histo_zjets_zmass_{channel}_weight_0_grouped_EWK2",
                 hsys = prefix + f"histo_zjets_zmass_{channel}_weight_0_grouped_EWK2_",
                 isSignal = False,
                 isMC = True,
                 isV = False,
                 isQCD = False,
                 xsecUnc = "1.10"
                 )

    # list of all processes
    #processes = sigs + [ttbar, zxx, wtau, vv, qcd]
    processes = sigs + [ttbar, ewk]
    
    lepname = "mu" if "mu" in channel else "e"
    era = "13TeV" if not is5TeV else "5TeV"

    # define different nuisance parameters, their groups,
    # and the impacts on each process
    nuisgroups = OrderedDict()

    nuis_lumi = Nuisance(name = "lumi_" + era, type = "lnN")
    for proc in processes:
        if proc.isMC:
            nuis_lumi[proc.name] = unc_lumi[nuis_lumi.name]
    nuisgroups["lumi"] = [nuis_lumi]

    nuisgroups["mcsec"] = []
    for proc in processes:
        if not proc.isSignal and proc.isMC:
            nuis_norm = Nuisance(name = "norm_" + proc.name, type = "lnN")
            nuis_norm[proc.name] = proc.xsecUnc
            nuisgroups["mcsec"].append(nuis_norm)

    # correction systematics
    # in Aram's ntuples, defined here: https://github.com/MiT-HEP/MitEwk13TeV/blob/CMSSW_94X/NtupleMod/eleNtupleMod.C#L71
    # and here: https://github.com/MiT-HEP/MitEwk13TeV/blob/CMSSW_94X/NtupleMod/muonNtupleMod.C#L81
    # 1 is MC, 2 is FSR, 3 is Bkg, 4 is tagpt, 
    # 8 is ecal prefire
    # 10 is muon prefire
    # correlate MC systematic, ECAL and muon prefire 
    # between electron and muon channel
    # uncorrelate FSR, bkg, tagpt in electron ahd muon channel
    nuis_SysWeight1 = Nuisance(name = "SysWeight1", type = "shape")
    nuis_SysWeight2 = Nuisance(name = lepname + "_SysWeight2", type = "shape")
    nuis_SysWeight3 = Nuisance(name = lepname + "_SysWeight3", type = "shape")
    nuis_SysWeight4 = Nuisance(name = lepname + "_SysWeight4", type = "shape")
    nuis_SysWeight8 = Nuisance(name = "SysWeight8", type = "shape")
    nuis_SysWeight10 = Nuisance(name = "SysWeight10", type = "shape")
    nuisgroups["effsys"] = [nuis_SysWeight1, nuis_SysWeight2, nuis_SysWeight3, nuis_SysWeight4]
    nuisgroups["prefire"] = [nuis_SysWeight8, nuis_SysWeight10]
    for proc in processes:
        if not proc.isQCD:
            # all the samples except the QCD apply the corrections
            # so they should be affected by sf systematics
            for sysweight in nuisgroups["effsys"] + nuisgroups["prefire"]:
                sysweight[proc.name] = 1.0

    nuis_effstat_plus = Nuisance(name = "effstat_" + lepname + "plus_" + era, type = "lnN")
    nuis_effstat_minus = Nuisance(name = "effstat_" + lepname + "minus_" + era, type = "lnN")
    for proc in processes:
        if proc.isSignal:
            # only apply eff/sf stat uncertainty to signals for now
            nuis_effstat_plus[proc.name] = unc_effstat[nuis_effstat_plus.name]
            nuis_effstat_minus[proc.name] = unc_effstat[nuis_effstat_minus.name]
    nuisgroups["effstat"] = [nuis_effstat_plus, nuis_effstat_minus]

    # theory systematics
    # qcd scale
    nuisgroups["qcdscale"] = []
    for wpt in range(len(Vptbins)-1):
        for par in ["MuF", "MuR", "MuFMuR"]:
            nuis_QCDScale = Nuisance(name = par+str(wpt), type = "shape")
            for proc in processes:
                if proc.isSignal:
                    nuis_QCDScale[proc.name] = 1.0
            nuisgroups["qcdscale"].append(nuis_QCDScale)

    # pdf + alphaS variations
    nuisgroups["pdfalphaS"] = []
    pdf_indices = list(range(1, 101))
    for ipdf in pdf_indices:
        nuis_PDF = Nuisance(name = f"PDF{ipdf}", type = "shape")
        for proc in processes:
            if proc.isSignal:
                nuis_PDF[proc.name] = 1.0
        nuisgroups["pdfalphaS"].append(nuis_PDF)
    
    # alphaS variations
    nuis_alphaS = Nuisance(name = "alphaS", type = "shape")
    for proc in processes:
        if proc.isSignal:
            nuis_alphaS[proc.name] = 1.0
    nuisgroups["pdfalphaS"].append(nuis_alphaS)

    #
    # writing datacards
    #
    cardname = f"{outdir}/datacard_{channel}.txt"
    if is5TeV:
        cardname = f"{outdir}/datacard_{channel}_5TeV.txt"
    WriteCard(data, processes, nuisgroups, cardname)

    return cardname


def combineCards(labels, cards, oname):
    """
    genrate and run the command to combine cards in different bins
    """
    cmd = "cd cards; combineCards.py"
    for label, card in zip(labels, cards):
        cmd += " {}={}".format(label, card)
    cmd += " > {}; cd ../".format(oname)
    print(("combine cards with {}".format(cmd)))
    os.system(cmd)


def GenerateRunCommand(output: str, cards: list, channels: list, cards_xsec: list = [], prefix: str = "./", applyLFU: bool = False):
    """
    generate the script with commands to run combine.
    inputs can probably be improved here
    """
    assert len(cards) == len(channels), "cards and channels should have the same length"
    if len(cards_xsec) > 0:
        # if provided xsec cards, then it should have the same length as the hist cards and channels        
        assert len(cards_xsec) == len(channels), "xsec cards and channels should have the same length"

    # these partitions can be changed depending on the directories and organizations
    card0 = cards[0]
    workdir = prefix + card0.rpartition('/')[0]

    for idx, card in enumerate(cards):
        cards[idx] = card.split('/')[-1]
    
    for idx, card_xsec in enumerate(cards_xsec):
        cards_xsec[idx] = card_xsec.split('/')[-1]

    cmd = ""
    cmd += "#!/bin/bash\n\n"
    cmd += f"cd {workdir}\n\n\n"

    cmd += f"combineCards.py"
    for channel, card in zip(channels, cards):
        if card == None:
            continue
        cmd += f" {channel}={card}"
    if len(cards_xsec) > 0:
        for channel, card_xsec in zip(channels, cards_xsec):
            if card_xsec == None:
                continue
            cmd += f" {channel}_xsec={card_xsec}"
    cmd += f" > {output}.txt\n"

    if len(cards_xsec) > 0:
        wplus = set()
        wminus = set()
        zinc = set()
        # add the syntax to do the absolute xsec, charge asymmetry, and ratio measurements
        for channel in channels:
            signame = GetSigName(channel, applyLFU)
            if "plus" in channel:
                wplus.add(signame)
            elif "minus" in channel:
                wminus.add(signame)
            else:
                # others are z's
                zinc.add(signame)
        winc = wplus.union(wminus)

        cmd += '\n\n'
        cmd += '# syntax for absolute xsec, charge asymmetry, and xsec ratios\n'
        cmd += '\n\n\n'
        cmd += f'echo \"Wplus_sig sumGroup = {" ".join(sig for sig in wplus)}\" >> {output}.txt\n'
        cmd += f'echo \"Wminus_sig sumGroup = {" ".join(sig for sig in wminus)}\" >> {output}.txt\n'
        cmd += f'echo \"Winc_sig sumGroup = {" ".join(sig for sig in winc)}\" >> {output}.txt\n'
        cmd += f'echo \"Zinc_sig sumGroup = {" ".join(sig for sig in zinc)}\" >> {output}.txt\n'
        cmd += f'echo \"WchgAsym chargeMetaGroup = Wplus_sig Wminus_sig\" >> {output}.txt\n'
        cmd += f'echo \"WchgRatio ratioMetaGroup = Wplus_sig Wminus_sig\" >> {output}.txt\n'
        cmd += f'echo \"WZRatio ratioMetaGroup = Winc_sig Zinc_sig\" >> {output}.txt\n'
        cmd += '\n\n'

    cmd += f"text2hdf5.py {output}.txt"
    if len(cards_xsec) > 0:
        for channel in channels:
            cmd += f" --maskedChan {channel}_xsec"
        cmd += " --X-allow-no-background"
    cmd += "\n"
    cmd += f"combinetf.py {output}.hdf5 --binByBinStat --computeHistErrors --saveHists --doImpacts --output {output}.root\n"

    # write outputs to scripts
    with open(f"{workdir}/{output}.sh", "w") as f:
        f.write(cmd)
    os.system(f"chmod +x {workdir}/{output}.sh")


def GetXSec(channel: str, is5TeV: bool = False):
    """
    return the MC Xsec given a channel and sqrtS.
    for longer term can read this from some root/txt files
    """
    xsecs = {}
    xsecs["5TeV"] = {}
    xsecs["13TeV"] = {}
    xsecs["13TeV"]["eplus"] = 1e6
    xsecs["13TeV"]["eminus"] = 1e6
    xsecs["13TeV"]["muplus"] = 1e6
    xsecs["13TeV"]["muminus"] = 1e6
    xsecs["13TeV"]["ee"] = 1e6
    xsecs["13TeV"]["mumu"] = 1e6

    xsecs["5TeV"]["eplus"] = 5e5
    xsecs["5TeV"]["eminus"] = 5e5
    xsecs["5TeV"]["muplus"] = 5e5
    xsecs["5TeV"]["muminus"] = 5e5
    xsecs["5TeV"]["ee"] = 5e5
    xsecs["5TeV"]["mumu"] = 5e5

    return xsecs["5TeV" if is5TeV else "13TeV"][channel]


def MakeXSecCard(channel: str, is5TeV: bool = False, outdir: str = "cards", applyLFU: bool = False):
    """
    Generate the root file with xsec result, and also the datacard
    """
    # get the xsec result
    xsec = GetXSec(channel, is5TeV)

    # write the xsec result to a root file
    fname = f"{outdir}/xsec_{channel}.root"
    f = ROOT.TFile(fname, "RECREATE")
    hname = f"xsec_{channel}_inAcc"
    h = ROOT.TH1D(hname, hname, 1, 0, 1)
    h.SetBinContent(1, xsec)
    h.SetBinError(1, 0)
    h.Write()
    f.Close()

    # sig mc xsec
    sig = Process(name = GetSigName(channel, applyLFU), fname = fname, 
                 hname = hname,
                 hsys = hname+"_",
                 isSignal = True,
                 isMC = True,
                 isV = True,
                 isQCD = False
                 ) 

    # get the datacard
    cardname = f"{outdir}/datacard_{channel}_xsec_InAcc.txt"
    if is5TeV:
        cardname = f"{outdir}/datacard_{channel}_xsec_InAcc_5TeV.txt"

    nuisgroups = OrderedDict()
    processes = [sig]
    WriteCard(None, processes, nuisgroups, cardname)

    return cardname


def GetSigName(channel: str, applyLFU: bool = False):
    """
    return the signal process name
    """
    signame = channel
    if applyLFU:
        signame = signame.replace("e", "lep").replace("mu", "lep")
    return signame + "_sig"


