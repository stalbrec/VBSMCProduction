#!/usr/bin/env python
import os,shutil,glob
import argparse,sys

#name of participating particles (as you want them to appear in file/directory name:
processes=[('WP','WP'),('WM','WM'),('WP','WM'),('WP','Z'),('WM','Z'),('Z','Z')]
#alias of particle used in MadGraph5_aMCatNLO
alias={'WM':'w-','WP':'w+','Z':'z','A':'a'}

class Process:
    def __init__(self,card_dir,dest_dir,bosonPair=('WP','WP')):
        (self.X,self.Y)=bosonPair
        self.process_dir='aQGC_%shad%shadJJ_EWK_LO_NPle1' % (self.X,self.Y)
        print "process: " +self.X+" and " +self.Y
        self.card_dir=card_dir
        self.templateName=card_dir.split('/')[-2]
        print(card_dir)
        print(self.templateName)
        self.dest_dir=dest_dir
        
    def editMadspin(self):
        with open(self.dest_dir+self.process_dir+'/'+self.templateName+'_madspin_card.dat', "rt") as fin:
            with open(self.dest_dir+self.process_dir+'/'+self.process_dir+'_madspin_card.dat', "wt") as fout:
                for line in fin:
                    if 'Boson1' in line:
                        fout.write(line.replace('Boson1',alias[self.X]))
                    elif 'Boson2' in line:
                        fout.write(line.replace('Boson2',alias[self.Y]))
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
                        fout.write(line.replace('XhadYhad','%shad%shad' % (self.X,self.Y)))
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
    parser.add_argument('--year', nargs='?', default='2016')
    # parser.add_argument('bar', nargs='+', help='bar help')

    #make changes to these cards:
    parser.add_argument('--cards',default='2016/aQGC_XhadYhadJJ_EWK_LO_NPle1/')

    #provide the directory where you want the cards:
    parser.add_argument('--dest',default='aQGC_VVjj_hadronic/')

    
    args = parser.parse_args()

    print(args)

    outDIR = args.dest+('' if args.dest[-1]=='/' else '/')
    outDIR += args.year+'/'
    if(not os.path.exists(outDIR)):
       os.makedirs(outDIR)
     
    os.chdir(outDIR)
    for dir in glob.glob("aQGC*"):
        shutil.rmtree(dir)
    os.chdir('../../')

    for process in processes:
        P=Process(args.cards,outDIR,process)
        P.createCards()


