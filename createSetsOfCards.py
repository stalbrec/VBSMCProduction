import os,sys
from newReweightRange import writeReweightCard
DIR='modelComparison/gridpack_cards/'


def writeCustomizeCard(cardsName,newModel=False):
    N_Pars=22 if newModel else 21
    with open(DIR+cardsName+'/'+cardsName+'_customizecards.dat','w+') as customizeCard:
        if('5f' in cardsName and not newModel and 'varyOnlyPDF' not in cardsName):
            customizeCard.write('set param_card mass 5 0.0\n')
        if('4f' in cardsName and newModel and 'varyOnlyPDF' not in cardsName):
            customizeCard.write('set param_card mass 5 4.7\n')

        for i in range(1,N_Pars):
            if(i==11 and not newModel or i==12 and newModel):
                customizeCard.write('set param_card anoinputs %i 6.5e-12\n'%i)
            else:
                customizeCard.write('set param_card anoinputs %i 0.0\n'%i)
        

def writeExtraModelCard(cardsName,newModel=False):
    model='SM_LS012_LM017_LT012_Ind5_UFO_June19.tar.gz' if newModel else 'SM_LS_LM_LT_UFO.tar.gz'
    with open(DIR+cardsName+'/'+cardsName+'_extramodels.dat','w+') as extramodelsCard:
        extramodelsCard.write('# customized model for EWdim8 EFT in 5f scheme\n')
        extramodelsCard.write(model+'\n')

def copyCommonCards(cardsName,newModel):
    os.system('cp TemplateCards/madspin_card.dat '+DIR+cardsName+'/'+cardsName+'_madspin_card.dat')
    if('5f' in cardsName):
        os.system('cp TemplateCards/run_card_5f.dat '+DIR+cardsName+'/'+cardsName+'_run_card.dat')
    elif('4f' in cardsName):
        if('varyOnlyPDF' in cardsName):
            os.system('cp TemplateCards/run_card_5f_4fPDF.dat '+DIR+cardsName+'/'+cardsName+'_run_card.dat')
        else:
            os.system('cp TemplateCards/run_card_4f.dat '+DIR+cardsName+'/'+cardsName+'_run_card.dat')
    else:
        os.system('cp TemplateCards/run_card.dat '+DIR+cardsName+'/'+cardsName+'_run_card.dat')
    
        
def copyProcCard(cardsName,newModel):
    modelName = 'SM_LSMT_Ind5_UFOv2' if newModel else 'SM_LS_LM_LT_UFO'
    with open('TemplateCards/proc_card.dat','r') as inProcCard:
        with open(DIR+cardsName+'/'+cardsName+'_proc_card.dat','w+') as outProcCard:
            for l in inProcCard:
                if(('4f' in cardsName and 'b b~' in l) and ('varyOnlyPDF' not in cardsName)):
                    outProcCard.write(l.replace('b b~',''))
                elif('output' in l):
                    outProcCard.write(l.replace('CARDSNAME',cardsName))
                elif('import' in l):
                    outProcCard.write(l.replace('MODELNAME',modelName))
                else:
                    outProcCard.write(l)


def writeCards(cardsName,newModel,csvFile):
    if(not os.path.exists(DIR+cardsName)):
        os.makedirs(DIR+cardsName)
    writeCustomizeCard(cardsName,newModel)
    writeExtraModelCard(cardsName,newModel)
    copyCommonCards(cardsName,newModel)
    copyProcCard(cardsName,newModel)
    writeReweightCard(DIR+cardsName,newModel,csvFile)
    
                    
if(__name__=='__main__'):
    csvFile = 'range_short.csv'
    names = []
    for NFlavour in [4,5]:
        # names += ['aQGC_ZhadZhadJJ_%s_QED2_QCD0_%if'%(model,NFlavour) for model in ['newModel','oldModel']]
        # names += ['aQGC_ZhadZhadJJ_%s_QED2_QCD0_%if_varyOnlyPDF'%(model,NFlavour) for model in ['newModel','oldModel']]
        # names += ['aQGC_ZhadZhadJJ_%s_QED4_QCD0_%if'%(model,NFlavour) for model in ['newModel','oldModel']]
        # names += ['aQGC_ZhadZhadJJ_%s_QED4_QCD0_%if_varyOnlyPDF'%(model,NFlavour) for model in ['newModel','oldModel']]
        names += ['aQGC_WPhadWPhadJJ_%s_QED2_QCD0_%if'%(model,NFlavour) for model in ['newModel','oldModel']]

    for name in names:
        print 'creating cards for:',name
        newModel='new' in name or 'LS012' in name
        writeCards(name,newModel,csvFile)
