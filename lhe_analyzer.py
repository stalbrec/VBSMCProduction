# based on Andreas Albert's script here https://github.com/AndreasAlbert/mg5tut_apr21_plots/blob/master/plot_skeleton.py 

import os

import numpy as np
from hist import Hist

from lhereader import LHEReader

from matplotlib import pyplot as plt
import mplhep as hep
plt.style.use(hep.style.CMS)

# for jet clustering using pyjet 
import awkward as ak
from pyjet import cluster
from skhep.math import LorentzVector



def plot(histograms):
    outdir = './plots/'
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    for density in [True,False]:
        for yscale in ['log','linear']:
            for observable in histograms[list(histograms.keys())[0]].keys():
                f,ax = plt.subplots()
                for sample, hists in histograms.items():
                    hep.histplot(hists[observable],label=sample,density=True)
                ax.legend()
            
                ax.set_xlabel(observable)
                ax.set_ylabel("$\Delta N / N$" if density else "Events")
                
                plt.yscale(yscale)
                density_str = 'density' if density else ''
                f.savefig(f"{outdir}/{observable}_{density_str}_yscale_{yscale}.pdf",bbox_inches='tight')

def setup_histograms():
    bins ={
        'mV' : np.linspace(0,200,101),
        'mVV' : np.linspace(0,3000,151),
        'mQQ' : np.linspace(0,200,101),
        'mQQQQ' : np.linspace(0,3000,151),
        'mJ' : np.linspace(0,200,101),
        'mJ0' : np.linspace(0,200,101),
        'mJ1' : np.linspace(0,200,101),
        'mJJ' : np.linspace(0,3000,151),
        'pTJ': np.linspace(0,1500,101),
        'pTJ0': np.linspace(0,1500,101),
        'pTJ1': np.linspace(0,1500,101),
        'etaJ': np.linspace(-6,6,101),
        'etaJ0': np.linspace(-6,6,101),
        'etaJ1': np.linspace(-6,6,101),
        
    } 

    # No need to change this part
    histograms = { 
                    observable : (
                                    Hist.new
                                    .Var(binning, name=observable, label=observable)
                                    .Double()
                                )
                    for observable, binning in bins.items()
    }

    return histograms

def fill_hists(lhe_file,args):    
    reader = LHEReader(lhe_file)
    histograms = setup_histograms()

    ievent = 0
    for event in reader:
        if(args.maxEvents > 0 and ievent>args.maxEvents):
            break
        ievent += 1
        v_pdgids = [23,24]
        vector_indices = [i for i in range(len(event.particles)) if abs(event.particles[i].pdgid) in v_pdgids]
        v_decants = []
        for v_index in vector_indices:
            qs = [p for p in event.particles if p.parent==v_index]
            v_decants.append(qs)

        QQQQ_p4,VV_p4 = None, None
        for i_v,v_index in enumerate(vector_indices):
            QQ_p4 = None
            for q in v_decants[i_v]:
                if QQ_p4:
                    QQ_p4 += q.p4()
                else:
                    QQ_p4 = q.p4()
            V_p4 = event.particles[v_index].p4()
            if VV_p4 :
                VV_p4 += V_p4
                QQQQ_p4 += QQ_p4
            else:
                VV_p4 = V_p4
                QQQQ_p4 = QQ_p4
            
            histograms['mV'].fill(V_p4.mass, weight=event.weights[0])
            histograms['mQQ'].fill(QQ_p4.mass, weight=event.weights[0])
        histograms['mVV'].fill(VV_p4.mass, weight=event.weights[0])
        histograms['mQQQQ'].fill(QQQQ_p4.mass, weight=event.weights[0])

        
        #now lets look at some genjets. for this i use the fastjet python interface pyjet which takes a structured numpy array as input.
        #the following gets all (final state) quarks (up to bs) in the event and puts it first in a array of LHEReader Particle objects:
        #quarks not originating from proton or first particle. < this is not useful
        # quarks = np.array(list(filter(lambda x: (abs(x.pdgid) in (1,2,3,4,5) and x.parent not in (-1,0)),event.particles)))
        #final state quarks
        # particles_to_cluster = np.array(list(filter(lambda x: (abs(x.pdgid) in (1,2,3,4,5) and x.status==1),event.particles)))
        #all final state particles
        particles_to_cluster = np.array(list(filter(lambda x: x.status==1,event.particles)))

        #and then we use awkwards nice zip function to create a strucured but not ragged awkward array, which we convert to numpy. easy 
        particles_to_cluster_struc = ak.zip({
            'pT':np.vectorize(lambda x:x.p4().pt)(particles_to_cluster),
            'eta':np.vectorize(lambda x:x.p4().eta)(particles_to_cluster),
            'phi':np.vectorize(lambda x:x.p4().phi())(particles_to_cluster),
            'mass':np.vectorize(lambda x:x.p4().mass)(particles_to_cluster)
        }).to_numpy()
                
        #cluster genkt jets with R=0.8
        sequence = cluster(particles_to_cluster_struc, R=0.8, p=-1)
        jets = sequence.inclusive_jets()

        #PseudoJets from pyjet do not have any real structure -> converting to LorentzVector (from skhep.math)
        def p4(a):
            return LorentzVector(a.px, a.py, a.pz, a.e)

        if(len(jets)>1):
            JJ = None
            for ijet in [0,1]:
                jet = p4(jets[ijet])            
                if JJ:
                    JJ += jet
                else:
                    JJ = jet
                histograms['mJ%i'%ijet].fill(jet.mass, weight=event.weights[0])
                histograms['pTJ%i'%ijet].fill(jet.pt, weight=event.weights[0])
                histograms['etaJ%i'%ijet].fill(jet.eta, weight=event.weights[0])

                histograms['mJ'].fill(jet.mass, weight=event.weights[0])
                histograms['pTJ'].fill(jet.pt, weight=event.weights[0])
                histograms['etaJ'].fill(jet.eta, weight=event.weights[0])
                
            histograms['mJJ'].fill(JJ.mass, weight=event.weights[0])
            
    return histograms

if(__name__=='__main__'):
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("--maxEvents",default=-1,type=int,help='maximum number of events to process per LHE file')
    args = parser.parse_args()
    
    lhe_files = {
        # 'oldGridpack':'/nfs/dust/cms/user/albrechs/VBS/VBS_SM/gridpacks/test2_lightq/cmsgrid_final.lhe',
        'jetNoB':'/nfs/dust/cms/user/albrechs/VBS/b_veto_test/osWW_Jnob/cmsgrid_final.lhe',        
        'Summer19Gridpack':'/nfs/dust/cms/user/albrechs/VBS/b_veto_test/osWW_withB/cmsgrid_final.lhe'
    }

    hists  = {s:fill_hists(lhe_files[s],args) for s in lhe_files.keys()}

    plot(hists)
