from coffea import processor
import awkward as ak
from coffea.nanoevents.methods import candidate
ak.behavior.update(candidate.behavior)
from coffea import hist

class NanoProcessor(processor.ProcessorABC):
    def __init__(self,aQGC):
        def get_common_axes(var_name,max_pt=2000,max_mass=2000):
            return (
                hist.Cat("dataset", "Dataset"),
                hist.Bin("mass", "$m_{\mathrm{%s}}$ [GeV]"%var_name, 100, 0, max_mass),
                hist.Bin("pt", "$p_{T,\mathrm{%s}}$ [GeV]"%var_name, 100, 0, max_pt),
                hist.Bin("eta", r"$\eta_{\mathrm{%s}}$ [GeV]"%var_name, 60, -6,6),
            )
        
        accumulator = {
            "sumw": processor.defaultdict_accumulator(float),
            "VV": hist.Hist("Events",*get_common_axes("VV",max_mass=3000,max_pt=3000)),
            
            "AK8J0": hist.Hist("Events",*get_common_axes("leading Ak8",max_mass=300)),
            "AK8J1": hist.Hist("Events",*get_common_axes("sub-leading Ak8",max_mass=300)),
            "AK8JJ": hist.Hist("Events",*get_common_axes("JJ",max_mass=3000,max_pt=3000)),
            "AK8JJ_mJJ500": hist.Hist("Events",*get_common_axes("JJ",max_mass=3000,max_pt=3000)),

            "AK8J0_topveto": hist.Hist("Events",*get_common_axes("leading Ak8",max_mass=300)),
            "AK8J1_topveto": hist.Hist("Events",*get_common_axes("sub-leading Ak8",max_mass=300)),
            "AK8JJ_topveto": hist.Hist("Events",*get_common_axes("JJ",max_mass=3000,max_pt=3000)),

            "AK4j0": hist.Hist("Events",*get_common_axes("leading Ak4",max_mass=300)),
            "AK4j1": hist.Hist("Events",*get_common_axes("sub-leading Ak4",max_mass=300)),
            "AK4jj": hist.Hist("Events",*get_common_axes("jj",max_mass=3000,max_pt=3000)),
            "AK4jj_mjj500": hist.Hist("Events",*get_common_axes("jj",max_mass=3000,max_pt=3000)),            
        }

        
        if(aQGC):
            self.smeft_points_dict = {
                "S0":['0p00'],
                "S1":['0p00'],
                "S2":['0p00'],
                "M0":['0p00'],
                "M1":['0p00'],
                "M2":['0p00'],
                "M3":['0p00'],
                "M4":['0p00'],
                "M5":['0p00'],
                "M6":['0p00'],
                "M7":['0p00'],
                "T0":['0p00'],
                "T1":['0p00'],
                "T2":['0p00'],
                "T3":['0p00'],
                "T4":['0p00'],
                "T5":['0p00'],
                "T6":['0p00'],
                "T7":['0p00'],
                "T8":['0p00'],
                "T9":['0p00'],
            }
            self.smeft_points = []
            for name,points_list in self.smeft_points_dict.items():
                for point in points_list:
                    self.smeft_points.append(f'f{name.lower()}_{point}')
            print(self.smeft_points)
            # accumulator.update({
            #     ''
            # })
        
        self._accumulator = processor.dict_accumulator(accumulator)

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

        
        # Js = events.FatJet
        Js = events.GenJetAK8
        
        # 2 FatJets
        cut = (ak.num(Js)>=2)        

        J0,J1 = Js[cut][:,0],Js[cut][:,1]
        for iJ,J in enumerate([J0,J1]):
            output[f'AK8J{iJ}'].fill(dataset=dataset, mass=J.mass, pt=J.pt, eta=J.eta)
            
        JJ = J0 + J1

        output["AK8JJ"].fill(
            dataset=dataset,
            mass = JJ.mass,
            pt = JJ.pt,
            eta = JJ.eta,
        )

        JJ_500=JJ[JJ.mass>500]
        output["AK8JJ_mJJ500"].fill(
            dataset=dataset,
            mass = JJ_500.mass,
            pt = JJ_500.pt,
            eta = JJ_500.eta,
        )

        ntops = ak.num( events.GenPart[abs(events.GenPart.pdgId)==6] )
        Js_topveto = Js[cut & (ntops==0)]
        J0_topveto,J1_topveto = Js_topveto[:,0],Js_topveto[:,1]
        for iJ,J in enumerate([J0_topveto,J1_topveto]):
            output[f'AK8J{iJ}_topveto'].fill(dataset=dataset,mass = J.mass,pt = J.pt,eta = J.eta)

        JJ_topveto = J0_topveto+J1_topveto
        output['AK8JJ_topveto'].fill(
            dataset=dataset,
            mass = JJ_topveto.mass,
            pt = JJ_topveto.pt,
            eta = JJ_topveto.eta,
        )

        # vbf jets

        # js = events.Jet
        js = events.GenJet
        cut = (ak.num(js) >=2)

        j0,j1 = js[cut][:,0],js[cut][:,1]

        for ij,j in enumerate([j0,j1]):
            output[f'AK4j{ij}'].fill(dataset=dataset, mass=j.mass, pt=j.pt, eta=j.eta)
            
        jj = j0 + j1

        output["AK4jj"].fill(
            dataset=dataset,
            mass = jj.mass,
            pt = jj.pt,
            eta = jj.eta,
        )

        jj = jj[jj.mass>500]
        output["AK4jj_mjj500"].fill(
            dataset=dataset,
            mass = jj.mass,
            pt = jj.pt,
            eta = jj.eta,
        )
            
        
        output["sumw"][dataset] += len(events)

        return output

    def postprocess(self, accumulator):
        return accumulator
if(__name__ == '__main__'):
    NanoProcessor(True)
