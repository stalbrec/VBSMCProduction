from coffea import processor
import awkward as ak
from coffea.nanoevents.methods import candidate
ak.behavior.update(candidate.behavior)
from coffea import hist

class NanoProcessor(processor.ProcessorABC):
    def __init__(self):
        self._accumulator = processor.dict_accumulator({
            "sumw": processor.defaultdict_accumulator(float),
            "mass": hist.Hist(
                "Events",
                hist.Cat("dataset", "Dataset"),
                hist.Bin("mass", "$m_{VV}$ [GeV]", 60, 0, 3000),
            ),
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
        
        print(Vs)
        cut = (ak.num(Vs) == 2)
        VV = Vs[cut][:, 0] + Vs[cut][:, 1]
        print(VV.mass)
        output["sumw"][dataset] += len(events)
        output["mass"].fill(
            dataset=dataset,
            mass=VV.mass,
        )

        return output

    def postprocess(self, accumulator):
        return accumulator
