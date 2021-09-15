import pylhe, uproot, os

def convert_file(ifile, ofile, debug):
    if(not os.path.isfile(ifile)):
        raise FileNotFoundError(f"Inputfile {ifile} does not exists!")
    print(f"converting {ifile.split('/')[-1]} to nanoAOD style root tree")
    arr_nano = pylhe.to_awkward_nanoaod(pylhe.read_lhe_with_attributes(ifile))
    upfile = uproot.recreate(ofile)
    upfile['Events'] = {k:arr_nano[k] for k in ['GenPart','LHEWeight','LHEReweightingWeight']}
    upfile.close()

    if(debug):
        upfile = uproot.open(ofile)
        tree = upfile['Events']
        tree.show()
    
    

if(__name__ == '__main__'):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--ifile',help="input file")
    parser.add_argument('-o','--ofile',help="output file")    
    parser.add_argument('--debug',action='store_true')    
    args = parser.parse_args()
    
    convert_file(args.ifile,args.ofile,args.debug)

    
