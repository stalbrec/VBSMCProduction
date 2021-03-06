# VBS samples

## Madgraph cards

## LHE Analyzer

required packages:
- [lhereader](https://github.com/AndreasAlbert/lhereader)
- [pyjet](https://github.com/scikit-hep/pyjet)
- [hist](https://github.com/scikit-hep/hist)
- [awkward-1.0](https://github.com/scikit-hep/awkward-1.0)
- [mplhep](https://github.com/scikit-hep/mplhep)
- [scikit-hep](https://github.com/scikit-hep/scikit-hep)

## LHE Particle Printer
required packages:
- [scikit-image](https://github.com/scikit-hep/scikit-image) for fast implementation of bresenham algorithm 
- [asciiplotter](https://github.com/stalbrec/asciiplotter)
- my fork of `pylhe` (see below)


## nanoAOD style LHE-root files

converting with `conver_lhe.py` requires `uproot-4.1.2` and local installation of my `pylhe` branch: [github.com:stalbrec/pylhe/nanoaodstyle](https://github.com/stalbrec/pylhe/tree/nanoaodstyle)


## coffeaGrinder

in order to submit dask worker to HTCondor@DESY i had to modify dask-jobqueue very minimally. So make sure to use my fork:

```
git clone -b htcondor-desy https://github.com/stalbrec/dask-jobqueue
cd dask-jobqueue
pip install -e .
```

