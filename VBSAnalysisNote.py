from coffea import processor
import awkward as ak
from coffea.nanoevents.methods import candidate
ak.behavior.update(candidate.behavior)
from coffea import hist

class NanoProcessor(processor.ProcessorABC):
    def __init__(self):
        def get_common_axes(var_name,max_pt=2000,max_mass=200):
            return (
                hist.Cat("dataset", "Dataset"),
                hist.Bin("mass", "$m_{%s}$ [GeV]"%var_name, 60, 0, max_mass),
                hist.Bin("pt", "$p_{T,%s}$ [GeV]"%var_name, 60, 0, max_pt),
                hist.Bin("eta", r"$\eta_{%s}$ [GeV]"%var_name, 60, -6,6),                
            )
        
        self._accumulator = processor.dict_accumulator({
            "sumw": processor.defaultdict_accumulator(float),
            "VV": hist.Hist("Events",*get_common_axes("VV",max_mass=3000,max_pt=3000)),
            
            "J0": hist.Hist("Events",*get_common_axes("leading Ak8")),
            "J1": hist.Hist("Events",*get_common_axes("sub-leading Ak8")),
            "JJ": hist.Hist("Events",*get_common_axes("JJ",max_mass=3000,max_pt=3000)),
            "JJ_mJJ500": hist.Hist("Events",*get_common_axes("JJ",max_mass=3000,max_pt=3000)),

            "j0": hist.Hist("Events",*get_common_axes("leading Ak4")),
            "j1": hist.Hist("Events",*get_common_axes("sub-leading Ak4")),
            "jj": hist.Hist("Events",*get_common_axes("jj")),
            "jj_mjj500": hist.Hist("Events",*get_common_axes("jj")),
        })

    @property
    def accumulator(self):
        return self._accumulator

    def process(self, events):
        output = self.accumulator.identity()

        dataset = events.metadata['dataset']
        
        Vs = events.GenPart[(events.GenPart.status == 22) &
                            ((abs(events.GenPart.pdgId) == 23) |
                            (abs(events.GenPart.pdgId) == 24) )
                            ]
        
        cut = (ak.num(Vs) == 2)
        VV = Vs[cut][:, 0] + Vs[cut][:, 1]

        output["VV"].fill(
            dataset=dataset,
            mass=VV.mass,
            pt=VV.pt,
            eta=VV.eta,
        )

        
        Js = events.FatJet
        
        # 2 FatJets
        cut = (ak.num(Js)>=2)        

        J0,J1 = Js[cut][:,0],Js[cut][:,1]
        for iJ,J in enumerate([J0,J1]):
            output[f'J{iJ}'].fill(dataset=dataset, mass=J.mass, pt=J.pt, eta=J.eta)
            
        JJ = J0 + J1

        output["JJ"].fill(
            dataset=dataset,
            mass = JJ.mass,
            pt = JJ.pt,
            eta = JJ.eta,
        )

        JJ=JJ[JJ.mass>500]
        output["JJ_mJJ500"].fill(
            dataset=dataset,
            mass = JJ.mass,
            pt = JJ.pt,
            eta = JJ.eta,
        )

        # vbf jets

        js = events.Jet
        cut = (ak.num(js) >=2)

        j0,j1 = js[cut][:,0],js[cut][:,1]

        for ij,j in enumerate([j0,j1]):
            output[f'j{ij}'].fill(dataset=dataset, mass=j.mass, pt=j.pt, eta=j.eta)
            
        jj = j0 + j1

        output["jj"].fill(
            dataset=dataset,
            mass = jj.mass,
            pt = jj.pt,
            eta = jj.eta,
        )

        jj = jj[jj.mass>500]
        output["jj_mjj500"].fill(
            dataset=dataset,
            mass = jj.mass,
            pt = jj.pt,
            eta = jj.eta,
        )
            
        
        output["sumw"][dataset] += len(events)

        return output

    def postprocess(self, accumulator):
        return accumulator
