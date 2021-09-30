import os,sys
from subprocess import call

def submit_gridpack(process,card_dir,out_dir):
    genproductions = f"/local-scratch/{os.environ['USER']}/genproductions/bin/MadGraph5_aMCatNLO/"
    if(not os.path.isdir(genproductions)):
        raise FileNotFoundError(f"Can't find genproductions repository in local scratch directory!\n Please run \033[0;33m git clone https://github.com/cms-sw/genproductions.git \033[0m in /local-scratch/{os.environ['USER']}")
    os.chdir(genproductions)
    if(os.path.isfile(f"nohup_{process}.debug")):
        print(f"WARNING: Log-file for process {process} already exists! Skipping..")
        return
    command = f'nohup ./submit_cmsconnect_gridpack_generation.sh {process} {card_dir}/{process} 1 "4 Gb" > nohup_{process}.debug 2>&1 &'
    print(command)
    os.system(command)

if(__name__=="__main__"):
    card_dir_prefix = 'cards/production/2017/13TeV/VBS/'

    gridpacks = {
        "VBS_SM_EWK":
        {
            "processes":
            [
                "WPJJWMJJjj_EWK_LO",
                "WPMJJWPMJJjj_EWK_LO",
                "ZBBWPMJJjj_EWK_LO",
                "ZBBZJJnoBjj_EWK_LO",
                "ZJJnoBWPMJJjj_EWK_LO",
                "ZJJZJJjj_EWK_LO",
                "ZNuNuWPMJJjj_EWK_LO",
                "ZNuNuZBBjj_EWK_LO",
                "ZNuNuZJJjj_EWK_LO",
                "ZNuNuZJJnoBjj_EWK_LO",
            ],
            "card_dir":f'{card_dir_prefix}/VVjj_hadronic/EWK/'
        },
        
        "VBS_SM_QCD":
        {
            "processes":
            ["WPJJWMJJjj_QCD_LO",
             "WPMJJWPMJJjj_QCD_LO",
             "ZBBWPMJJjj_QCD_LO",
             "ZBBZJJnoBjj_QCD_LO",
             "ZJJnoBWPMJJjj_QCD_LO",
             "ZJJZJJjj_QCD_LO",
             "ZNuNuWPMJJjj_QCD_LO",
             "ZNuNuZBBjj_QCD_LO",
             "ZNuNuZJJjj_QCD_LO",
             "ZNuNuZJJnoBjj_QCD_LO"],
            "card_dir":f'{card_dir_prefix}/VVjj_hadronic/QCD/'
        },
        
        "VBS_SM_EWK_QCD":
        {
            "processes":
            ["WPJJWMJJjj_EWK_QCD_LO",
             "WPMJJWPMJJjj_EWK_QCD_LO",
             "ZBBWPMJJjj_EWK_QCD_LO",
             "ZBBZJJnoBjj_EWK_QCD_LO",
             "ZJJnoBWPMJJjj_EWK_QCD_LO",
             "ZJJZJJjj_EWK_QCD_LO",
             "ZNuNuWPMJJjj_EWK_QCD_LO",
             "ZNuNuZBBjj_EWK_QCD_LO",
             "ZNuNuZJJjj_EWK_QCD_LO",
             "ZNuNuZJJnoBjj_EWK_QCD_LO"],
            "card_dir":f'{card_dir_prefix}/VVjj_hadronic/EWK_QCD/'
        }
    }

    out_dir=os.environ['HOME']
    for batch in gridpacks:
        for process in gridpacks[batch]['processes']:
            submit_gridpack(process,gridpacks[batch]['card_dir'],out_dir)
