#!/usr/bin/env python
from __future__ import print_function
import os,sys,glob,argparse,shutil
processes={
    "Z-Z":[
        ("vv","j_nobj_nob"),
        ("vv","bb"),
        ("bb","j_nobj_nob"),
        ("jj","jj")        
    ],
    "Z-WPM":[
        ("vv","jj"),
        ("bb","jj"),
        ("j_nobj_nob","jj")        
    ],
    "WPM-WPM":[
        ("jj","jj")        
    ],
    "WP-WM":[
        ("jj","jj")        
    ]
}
alias={'WPM':'w+','WM':'w-','WP':'w+','W':'w+','Z':'z','A':'a','v':'vl','j_nob':'j_nob','j':'j','b':'b'}
# final_state_alias = {'vv':'2Nu','bb':'2B','j_nobj_nob':'2JnoB','jj':'2J'}
final_state_alias = {'vv':'NuNu','bb':'BB','j_nobj_nob':'JJnoB','jj':'JJ'}

exclusion = {
    'EWK':{
        'top':["WP-WM","WPM-WPM","ZWPM"],
        'higgs':processes.keys()
    },
    'QCD':{
        'top':["WP-WM"],
        'higgs': []
    }
}

class Process:
    def __init__(self, process, final_states, order, template_dir, out_dir):
        self.bosons = process.split("-")
        self.final_states = [list(final_state) if 'nob' not in final_state else ['j_nob','j_nob'] for final_state in final_states]
        self.EWK = 'EWK' in order
        self.QCD = 'QCD' in order
        
        self.template_dir = template_dir

        self.name = ''.join([self.bosons[i]+final_state_alias[''.join(self.final_states[i])] for i in range(2)])
        self.name += 'jj_'+order+'_LO'
        self.directory = out_dir+order+"/"+self.name+'/'
        os.makedirs(self.directory)

        self.exclusions = set()
        if(self.EWK):
            if(process in exclusion["EWK"]["top"]):
                self.exclusions.add(" t t~")
            if(process in exclusion["EWK"]["higgs"]):
                self.exclusions.add(" h")
        if(self.QCD):
            if(process in exclusion["QCD"]["top"]):
                self.exclusions.add(" t t~")
            if(process in exclusion["QCD"]["higgs"]):
                self.exclusions.add(" h")

        
    def copy_run_card(self):
        os.system('cp '+self.template_dir+'run_card.dat '+self.directory+self.name+'_run_card.dat')

        
    def write_proc_card(self):
        with open(self.directory+self.name+'_proc_card.dat','wb') as proc_card:
            proc_card.write('set group_subprocesses Auto\n')
            proc_card.write('set ignore_six_quark_processes False\n')
            proc_card.write('set loop_optimized_output True\n')
            proc_card.write('set complex_mass_scheme False\n')
            proc_card.write('import model sm-ckm_no_b_mass\n')
            proc_card.write('define p = g u c d s u~ c~ d~ s~\n')
            EWK_order = 4 if (self.EWK) else 2
            QCD_order = 99 if (self.QCD) else 0
            
            boson_str = ' '.join([alias[boson] for boson in self.bosons])
            exclusion_str = ('/' if len(self.exclusions)>0 else '') + ''.join(self.exclusions)
            proc_card.write('generate p p > %s j j %s QED=%i QCD=%i'%(boson_str,exclusion_str,EWK_order,QCD_order))
            if('WPM' in self.bosons):
                proc_card.write(' @ 1\n')
                boson_str = boson_str.replace('+','-')
                proc_card.write('add process p p > %s j j %s QED=%i QCD=%i @ 2'%(boson_str,exclusion_str,EWK_order,QCD_order))
            proc_card.write('\n')
            proc_card.write('output %s -nojpeg\n'%self.name)
            

    def write_madspin_card(self):
        with open(self.directory+self.name+'_madspin_card.dat','wb') as madspin_card:
            madspin_card.write("set BW_cut 15\n")
            madspin_card.write("set ms_dir ./madspingrid\n")
            madspin_card.write("set max_running_process 1\n")
            if('v' in self.final_states[0] or 'v' in self.final_states[1]):
                madspin_card.write("define vl = ve vm vt\n")
                madspin_card.write("define vl~ = ve~ vm~ vt~\n")
            if('j_nob' in self.final_states[0] or 'j_nob' in self.final_states[1]):
                madspin_card.write('define j_nob = u c d s u~ c~ d~ s~\n')
            
            decay_lines = set()
            for boson,final_state in zip(self.bosons,self.final_states):
                final_state_list = [alias[final_state[0]],alias[final_state[1]]+('' if 'j' in final_state[1] else '~')]
                if 'wpm' == boson.lower():
                    decay_lines.add("decay %s > %s\n"%(alias['WP'],' '.join(final_state_list) ))
                    decay_lines.add("decay %s > %s\n"%(alias['WM'],' '.join(final_state_list) ))
                else:
                    decay_lines.add("decay %s > %s\n"%(alias[boson],' '.join(final_state_list) ))
            madspin_card.writelines(decay_lines)
            madspin_card.write("launch\n")

            
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--cards',default='templates/SM/2017/', help='make changes to these cards (only run_cards)')
    parser.add_argument('--dest',default='VVjj_hadronic/2017/', help='provide the directory where you want the cards')
    parser.add_argument('--order',nargs='+',default=['EWK','QCD','EWK_QCD'], help='list of orders, e.g. default = [EWK,QCD,EWK_QCD]')
    
    
    args = parser.parse_args()

    outDIR = args.dest+('' if args.dest[-1]=='/' else '/')
    if(not os.path.exists(outDIR)):
       os.makedirs(outDIR)
     
    os.chdir(outDIR)
    
    for sub_dir in args.order:
        if(os.path.isdir(sub_dir)):
            shutil.rmtree(sub_dir)
    os.chdir("../../")
    n_sets_cards = 0 
    for order in args.order:
        for bosons, final_states in processes.items():
            for final_state in final_states:
                this_process = Process(bosons, final_state, order, args.cards, outDIR)
                this_process.copy_run_card()
                this_process.write_proc_card()
                this_process.write_madspin_card()
                n_sets_cards += 1

    print('produced',n_sets_cards,'sets of cards')
