#!/usr/bin/env python
from __future__ import print_function
import os,sys,glob,argparse,shutil
import card_util

alias={
    'WPM':'w+','WM':'w-','WP':'w+','W':'w+',
    'Z':'z','A':'a',
    'v':'vl',
    'v~':'vl~',
    'j_nob':'j_nob','j':'j',
    'lp':'l+','lm':'l-','v~':'vl~'
}

final_state_alias = {'vv':'NuNu','bb':'BB','j_nobj_nob':'JJnoB','jj':'JJ','lmv':'lep','lpv':'lep'}


class Process(object):
    def __init__(self, args, process, final_states, order, template_dir, out_dir, ufo_model = 'sm-ckm_no_b_mass',name_suffix=''):
        self.bosons = process.split("-")

        self.final_states = [list(final_state) for final_state in final_states]
        
        self.EWK = 'EWK' in order
        self.QCD = 'QCD' in order
        
        self.template_dir = template_dir

        self.name = ''.join([self.bosons[i]+final_state_alias[''.join(self.final_states[i]).replace("~","")] for i in range(2)])
        self.name += 'jj_'
        if(args.semilep):
            self.name = self.name.replace("JJ","had")
            self.name = self.name.replace("jj","JJ")

        self.name += order+'_LO' + name_suffix
        
        self.directory = out_dir+order+"/"+self.name+'/'

        if(not os.path.isdir(self.directory)):
            os.makedirs(self.directory)

        self._flavour_scheme = -1
        self._model = ''
        self.model = ufo_model
        
        self.jet_definition = {
            'madspin': 'u c d s u~ c~ d~ s~ b b~',
            'proc':    'u c d s u~ c~ d~ s~ b b~'
        }

        self.proton_definition = {
            'madspin': 'u c d s u~ c~ d~ s~ b b~',
            'proc':    'u c d s u~ c~ d~ s~ b b~'
        }

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, model):
        self._model = model
        self._flavour_scheme = 5 if 'no_b_mass' in model else 4
        
    def write_cards(self):
        #copy run card
        print('writing cards for:',
              self.bosons[0], '->', self.final_states[0],
              self.bosons[1], '->', self.final_states[1],
              ('EWK' if self.EWK else ''), ('QCD' if self.QCD else ''))

        os.system('cp '+self.template_dir+f'run_card{"_semilep" if args.semilep else ""}.dat '+self.directory+self.name+'_run_card.dat')

        self.write_proc_card()
        # self.write_madspin_card()
        
    def write_proc_card(self):
        with open(self.directory+self.name+'_proc_card.dat','w+') as proc_card:
            # proc_card.write('set group_subprocesses Auto\n')
            # proc_card.write('set ignore_six_quark_processes False\n')
            # proc_card.write('set loop_optimized_output True\n')
            # proc_card.write('set complex_mass_scheme False\n')
            if(self.model != 'sm'):
                proc_card.write(f'import model {self.model}\n')


            if((self._flavour_scheme == 4 and 'b' in self.proton_definition['proc']) or (self._flavour_scheme == 5 and 'b' not in self.proton_definition['proc'])):
                proc_card.write('define p = %s\n'%self.proton_definition['proc'])

            if((self._flavour_scheme == 4 and 'b' in self.jet_definition['proc']) or (self._flavour_scheme == 5 and 'b' not in self.jet_definition['proc'])):
                proc_card.write('define j = %s\n'%self.jet_definition['proc'])
            print(self.final_states)

            if(any('v' in f for f in self.final_states)):
                proc_card.write("define vl = ve vm vt\n")
            if(any('v~' in f for f in self.final_states)):
                proc_card.write("define vl~ = ve~ vm~ vt~\n")

            if(any('lp' in f for f in self.final_states)):
                proc_card.write("define l+ = e+ mu+ ta+\n")
            if(any('lm' in f for f in self.final_states)):
                proc_card.write("define l- = e- mu- ta-\n")

            if(('j_nob' in self.final_states[0] or 'j_nob' in self.final_states[1]) and self._flavour_scheme == 5):
                proc_card.write('define j_nob = u c d s u~ c~ d~ s~\n')

            EWK_order = 4 if (self.EWK) else 2
            QCD_order = 99 if (self.QCD) else 0
            
            boson_str = ' '.join([alias.get(boson,boson) for boson in self.bosons])

            # decays = set([f"{alias[self.bosons[i]]} > {alias[self.final_states[i][0]]} {alias[self.final_states[i][1]]+('' if 'j' in self.final_states[i][1] else '~')}" for i in range(len(self.bosons))])
            decays = dict.fromkeys([f"{alias.get(self.bosons[i],self.bosons[i])} > {alias.get(self.final_states[i][0],self.final_states[i][0])} {alias.get(self.final_states[i][1],self.final_states[i][1])}" for i in range(len(self.bosons))])
            print(decays)
            decay_str = ", ".join(s for s in decays)
            print(decay_str)
            proc_card.write(f'generate p p > {boson_str} j j  QED={EWK_order} QCD={QCD_order}, {decay_str}')
            if('WPM' in self.bosons):
                proc_card.write(' @ 1\n')
                boson_str = boson_str.replace('+','-')
                decay_str = decay_str.replace('+','-')
                proc_card.write(f'add process p p > {boson_str} j j  QED={EWK_order} QCD={QCD_order}, {decay_str} @ 2')
                # proc_card.write('add process p p > %s j j  QED=%i QCD=%i @ 2'%(boson_str,EWK_order,QCD_order))
            proc_card.write('\n')
            proc_card.write(f'output {self.name} {"-" if args.semilep else ""}-nojpeg\n')
            

    def write_madspin_card(self):
        with open(self.directory+self.name+'_madspin_card.dat','wb') as madspin_card:
            madspin_card.write("set BW_cut 15\n")
            madspin_card.write("set ms_dir ./madspingrid\n")
            madspin_card.write("set max_running_process 1\n")
            if('v' in self.final_states[0] or 'v' in self.final_states[1]):
                madspin_card.write("define vl = ve vm vt\n")
                madspin_card.write("define vl~ = ve~ vm~ vt~\n")
            if('l' in self.final_states[0] or 'l' in self.final_states[1]):
                madspin_card.write("define l = ve vm vt\n")
                madspin_card.write("define l- = e- m- vt~\n")

            if('j_nob' in self.final_states[0] or 'j_nob' in self.final_states[1]):
                madspin_card.write('define j_nob = u c d s u~ c~ d~ s~\n')

            # if((self._flavour_scheme == 4 and 'b' in self.proton_definition['madspin']) or (self._flavour_scheme == 5 and 'b' not in self.proton_definition['madspin'])):
            #     madspin_card.write('define p = %s\n'%self.proton_definition['madspin'])

            if((self._flavour_scheme == 4 and 'b' in self.jet_definition['madspin']) or (self._flavour_scheme == 5 and 'b' not in self.jet_definition['madspin'])):
                madspin_card.write('define j = %s\n'%self.jet_definition['madspin'])

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
    parser.add_argument('--dest',default='VBS_cards', help='provide the directory where you want the cards')
    parser.add_argument('--order',nargs='+',default=['EWK','QCD','EWK_QCD'], help='list of orders, e.g. default = [EWK,QCD,EWK_QCD]')
    parser.add_argument('--test',action='store_true',help='parse produced cards for errors using genproduction parsing script')
    parser.add_argument('--comparisonSamples',action='store_true',help='write cards for comparison samples (osWW and WZ with 4f scheme but bs in jets in madspin card.)')
    parser.add_argument('--semilep',action='store_true',help='write cards for semileptonic samples')
    
    
    args = parser.parse_args()

    script_dir = os.getcwd()
    
    outDIR = args.dest+('' if args.dest[-1]=='/' else '/')

    n_sets_cards = 0

    jet_with_b = 'u c d s u~ c~ d~ s~ b b~'

    jet_no_b = 'u c d s u~ c~ d~ s~'

    processes_4f_comparison = {
        "WP-WM":[
            (("j","j"),("j","j"))
        ],
        "Z-WPM":[
            (("v","v~"),("j","j")),
            (("b","b~"),("j","j")),
            (("j_nob","j_nob"),("j","j"))
        ]
    }

    processes_5f_hadronic={
        "Z-Z":[
            (("v","v~"),("j_nob","j_nob")),
            (("v","v~"),("j","j")),
            (("v","v~"),("b","b~")),
            (("b","b~"),("j_nob","j_nob")),
            (("j","j"),("j","j"))        
        ],
        "Z-WPM":[
            (("v","v~"),("j","j")),
            (("b","b~"),("j","j")),
            (("j_nob","j_nob"),("j","j"))
        ],
        "WPM-WPM":[
            (("j","j"),("j","j"))
        ],
        "WP-WM":[
            (("j","j"),("j","j"))
        ]
        }

    processes_5f_semilep={
        "WM-Z":[
            (("lm","v~"),("j","j"))
        ],
        "WP-Z":[
            (("lp","v"),("j","j"))
        ],
        "WP-WM":[            
            (("j","j"),("lm","v~")),
            (("lp","v"),("j","j")),
        ],
        "WP-WP":[
            (("lp","v"),("j","j")),
        ],
        "WM-WM":[
            (("lm","v~"),("j","j")),
        ],
        }

    if(args.semilep):
        processes_5f_base = processes_5f_semilep
    else:
        processes_5f_base = processes_5f_hadronic

    if(args.comparisonSamples):
        processes = processes_4f_comparison
    else:
        processes = processes_5f_base
        

    for order in args.order:
        for bosons, final_states in processes.items():
            for final_state in final_states:
                # for madspin_jet_definition,proc_jet_definition in [(jet,jet),(jet_nob,jet),(jet_nob,jet_nob)]:

                this_process = Process(args, bosons, final_state, order, args.cards, outDIR, ufo_model =  'sm' if args.comparisonSamples else 'sm-ckm_no_b_mass',name_suffix='_SM_mjj100_pTj10' if args.semilep else '')
                # this_process.jet_definition['proc'] = 'u c d s u~ c~ d~ s~'
                # this_process.jet_definition['madspin'] = 'u c d s u~ c~ d~ s~'

                if(args.comparisonSamples):
                    this_process.proton_definition['proc'] = jet_no_b
                    this_process.jet_definition['proc'] = jet_no_b

                    this_process.jet_definition['madspin'] = jet_with_b 
                else:
                    this_process.jet_definition['proc'] = jet_with_b
                    this_process.jet_definition['madspin'] = jet_with_b 
                
                this_process.write_cards()
                

                if(args.test):
                    card_util.parse_cards(this_process.directory)
                n_sets_cards += 1

    print('produced',n_sets_cards,'sets of cards')
