#!/usr/bin/env python
from __future__ import print_function
import os,shutil,glob
import argparse,sys

#name of participating particles (as you want them to appear in file/directory name:
processes={
    'WP-WP':[
        ("jj","jj")
    ],
    'WM-WM':[
        ("jj","jj")
    ],
    'WP-WM':[
        ("jj","jj")
    ],
    'WP-Z':[
        ("jj","jj")
    ],
    'WM-Z':[
        ("jj","jj")
    ],
    'Z-Z':[
        ("vv","j_nobj_nob"),
        ("bb","j_nobj_nob"),
        ("jj","jj")        
    ]
}

final_state_alias = {'vv':'NuNu','bb':'BB','j_nobj_nob':'JJnoB','jj':'JJ'}

#alias of particle used in MadGraph5_aMCatNLO
# alias={'WM':'w-','WP':'w+','Z':'z','A':'a'}
alias={'WPM':'w+','WM':'w-','WP':'w+','W':'w+','Z':'z','A':'a','v':'vl','j_nob':'j_nob','j':'j','b':'b'}

class Process:
    def __init__(self,card_dir,dest_dir,bosonPair='WP-WP',final_states = ('jj','jj')):
        self.X, self.Y = tuple(bosonPair.split('-'))
        self.final_states = [list(final_state) if 'nob' not in final_state else ['j_nob','j_nob'] for final_state in final_states]
        # self.fully_hadronic = all('j' in final_state for final_state in self.final_states)
        self.fully_hadronic = False
        self.process_str = '%shad%shad'%(self.X,self.Y) if self.fully_hadronic else (self.X+final_state_alias[final_states[0]]+self.Y+final_state_alias[final_states[1]])
        self.process_dir='aQGC_%sjj_EWK_LO_NPle1'%self.process_str
        print("process: " +self.X+" and " +self.Y)
        print(self.final_states)
        print(self.process_dir)
        self.card_dir=card_dir
        self.templateName=card_dir.split('/')[-2]
        print(card_dir)
        print(self.templateName)
        self.dest_dir=dest_dir
        
    def editMadspin(self):
        final_state_str_list = [[alias[final_state[0]],alias[final_state[1]]+('' if 'j' in final_state[1] else '~')] for final_state in self.final_states]
        print(final_state_str_list)
        with open(self.dest_dir+self.process_dir+'/'+self.templateName+'_madspin_card.dat', "rt") as fin:
            with open(self.dest_dir+self.process_dir+'/'+self.process_dir+'_madspin_card.dat', "wt") as fout:
                for line in fin:
                    if 'Boson1' in line:
                        if('j_nob' in self.final_states[0] or 'j_nob' in self.final_states[1]):
                            fout.write('define j_nob = u c d s u~ c~ d~ s~\n')
                        fout.write(line.replace('Boson1',alias[self.X]).replace('j j',' '.join(final_state_str_list[0])))
                    elif 'Boson2' in line:
                        # if(self.X != self.Y):
                        if(self.X != self.Y or self.final_states[0] != self.final_states[1]):
                            fout.write(line.replace('Boson2',alias[self.Y]).replace('j j',' '.join(final_state_str_list[1])))
                    else:
                        fout.write(line)
        os.remove(self.dest_dir+self.process_dir+'/'+self.templateName+'_madspin_card.dat')

    def editProc(self):
        with open(self.dest_dir+self.process_dir+'/'+self.templateName+'_proc_card.dat', "rt") as fin:
            with open(self.dest_dir+self.process_dir+'/'+self.process_dir+'_proc_card.dat', "wt") as fout:
                for line in fin:
                    if 'generate' in line:
                        fout.write(line.replace('Boson1 Boson2',alias[self.X]+' '+alias[self.Y]))
                    elif 'output' in line:
                        # fout.write(line.replace('XhadYhad','%shad%shad' % (self.X,self.Y)))
                        fout.write(line.replace('XhadYhad',self.process_str))
                    else:
                        fout.write(line)
        os.remove(self.dest_dir+self.process_dir+'/'+self.templateName+'_proc_card.dat')

    def renameCards(self):
        scriptDir=os.getcwd()
        os.chdir(self.dest_dir+self.process_dir)
        cards = glob.glob("*.dat")
        cards.remove(self.process_dir+'_madspin_card.dat')
        cards.remove(self.process_dir+'_proc_card.dat')
        for card in cards:
            newname=self.process_dir+card[28:]
            shutil.move(card,newname)
        os.chdir(scriptDir)

    def createCards(self):
        shutil.copytree(self.card_dir,self.dest_dir+self.process_dir)
        self.editMadspin()
        self.editProc()
        self.renameCards()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cards',default='templates/aQGC/2017/aQGC_XhadYhadJJ_EWK_LO_NPle1/', help='make changes to these cards')
    parser.add_argument('--dest',default='aQGC_VVjj_hadronic/2017', help='provide the directory where you want the cards')

    
    args = parser.parse_args()

    print(args) 

    copyRangeCardCommand="cp VVRange.dat %s/aQGC_XhadYhadJJ_EWK_LO_NPle1_reweight_card.dat"%args.cards
    print(copyRangeCardCommand)
    os.system(copyRangeCardCommand)
    
    outDIR = args.dest+('' if args.dest[-1]=='/' else '/')
    if(not os.path.exists(outDIR)):
       os.makedirs(outDIR)
     
    os.chdir(outDIR)
    for dir in glob.glob("aQGC*"):
        shutil.rmtree(dir)
    os.chdir('../../')

    for process in processes.keys():
        for final_states in processes[process]:
            P=Process(args.cards,outDIR,process,final_states)
            P.createCards()


