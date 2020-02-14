#!/usr/bin/env python
import os,json
anoinputs={
"S0":[1,1],
"S1":[2,2],
# "S2":[-1,3],
"M0":[3,4],
"M1":[4,5],
"M2":[5,6],
"M3":[6,7],
"M4":[7,8],
"M5":[8,9],
"M6":[9,10],
"M7":[10,11],
"T0":[11,12],
"T1":[12,13],
"T2":[13,14],
"T5":[16,17],
"T6":[17,18],
"T7":[18,19],
"T8":[19,20],    
"T9":[20,21]
}

def getJsonFromCSV(newModel=True,csvFileName='range_short.csv'):
    ranges={} 
    with open(csvFileName) as csvFile:
        i=0
        for l in csvFile:
            info = l.split(';')
            operator = str(info[0].replace('"',''))
            anoinput = anoinputs[operator][1] if newModel else anoinputs[operator][0]
            range_list=[round( float( e.strip().replace(',','.') ), 2 ) for e in info[1:] ]
            ranges.update({operator:[anoinput]+range_list })
    return ranges





def getPointName_old(set,point):
    name="F%s_"%set
    # point=10*startx+i*10*increment
    point = 10 * point
    # print(point ,'->',point/1000,(-point%1000))
    if(point>=0):
        name+="%ip%02.0f"%(point/100,(point%100))
    else:
        name+="m%ip%02.0f"%(-point/100,(-point%100))    
    return name


def getPointName(set,point):
    name="F%s_"%set
    name+="%.2f"%(point/100)
    name = name.replace('.','p')
    if('-' in name):
        name = name.replace('-','m')
    return name


def writeReweightCard(cardsName,newModel,csvFile):
    operators=["S0","S1","S2","M0","M1","M2","M3","M4","M5","M6","M7","T0","T1","T2","T5","T6","T7","T8","T9"] if newModel else ["S0","S1","M0","M1","M2","M3","M4","M5","M6","M7","T0","T1","T2","T5","T6","T7","T8","T9"]
    sets=getJsonFromCSV(newModel,csvFile)
    with open(cardsName+'/'+cardsName.split('/')[-1]+"_reweight_card.dat","wt") as fout:
        fout.write("change helicity False\n")
        fout.write("change rwgt_dir rwgt")
        fout.write("\n\n")
        sum_points=0

        for op in operators:
            for i in range(0,int(sets[op][1])):
                point=100*sets[op][2]+i*100*sets[op][3]
                fout.write("\n#******************** F%s ********************"%op)
                fout.write("\nlaunch --rwgt_name=%s"%getPointName(op,point))
                if(newModel):
                    if(sets[op][0]!=12):
                        fout.write("\n\tset anoinputs 12 0.000000e+00")
                else:
                    if(sets[op][0]!=11):
                        fout.write("\n\tset anoinputs 11 0.000000e+00")
                        
                fout.write("\n\tset anoinputs %i %8.6fe-12"%(sets[op][0],point/100))
                # fout.write("\n\n")
                sum_points+=1
        
if(__name__=="__main__"):
    BosonChannel="VV"
    # operators=["S0","S1","S2","M0","M1","M2","M3","M4","M5","M6","M7","T0","T1","T2","T5","T6","T7","T8","T9"]
    operators=["S0","S1","M0","M1","M2","M3","M4","M5","M6","M7","T0","T1","T2","T5","T6","T7","T8","T9"]
    sets=getJsonFromCSV(newModel=False,csvFileName='range.csv')
    # sets=json.load(open('range.json','r'))
    # with open(BosonChannel+'Range.csv','rb') as csvfile:
    #     snippet=''
    #     snippet2=''
    #     NPoint=0
    #     setreader=csv.DictReader(csvfile)
    #     for row in setreader:
    #         sets.update({row['parameter']:[
    #                 int(row['anoinput']),
    #                 int(row['Npoints']),
    #                 float(row['start']),
    #                 float(row['stepsize'])
    #                 ]})

    #         snippet+='//%s=[%i,%.2f,%.2f,%.2f]\n'%(row['parameter'],int(row['Npoints']),float(row['stepsize']),float(row['start']),float(row['end']))
    #         snippet+='for(unsigned int i=0; i<%i; i++){\n'%int(row['Npoints'])
    #         snippet+='reweight_names.push_back(getParName("%s",%.2ff,%.2ff,i));\n'%(row['parameter'],float(row['start']),float(row['stepsize']))
    #         snippet+='}\n'

    #         NPoint+=int(row['Npoints'])
    #         snippet2+='if(parameter_index<%i){\n'%NPoint
    #         snippet2+='std::string parameter_string="%s";\n'%row['parameter']
    #         snippet2+='reweight_names.push_back(getParName("%s",%.2ff,%.2ff,parameter_index-%i));\n'%(row['parameter'],float(row['start']),float(row['stepsize']),(NPoint-int(row['Npoints'])))
    #         snippet2+='}else '

    #     print('snippet for MjjHists:')
    #     print(snippet)

    #     print('snippet for PDFHists:')
    #     print(snippet2)


    
    print(sets)
    with open(BosonChannel+"Range.dat","wt") as fout:
        fout.write("change helicity False\n")
        fout.write("change rwgt_dir rwgt")
        fout.write("\n\n")
        sum_points=0

        for op in operators:
            for i in range(0,int(sets[op][1])):
                point=100*sets[op][2]+i*100*sets[op][3]
                fout.write("\n#******************** F%s ********************"%op)
                fout.write("\nlaunch --rwgt_name=%s"%getPointName(op,point))
                if(sets[op][0]!=11):
                    fout.write("\n\tset anoinputs 11 0.000000e+00")
                fout.write("\n\tset anoinputs %i %8.6fe-12"%(sets[op][0],point/100))
                # fout.write("\n\n")
                sum_points+=1
        print("Total number of reweighting points:", sum_points)
