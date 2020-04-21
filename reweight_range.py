#!/usr/bin/env python
import os,json

anoinputs={
"S0":1,
"S1":2,
"S2":3,
"M0":4,
"M1":5,
"M2":6,
"M3":7,
"M4":8,
"M5":9,
"M6":10,
"M7":11,
"T0":12,
"T1":13,
"T2":14,
"T5":17,
"T6":18,
"T7":19,
"T8":20,    
"T9":21
}

def getJsonFromCSV(csvFileName='range_short.csv'):
    ranges={} 
    with open(csvFileName) as csvFile:
        i=0
        for l in csvFile:
            info = l.split(';')
            operator = str(info[0].replace('"',''))
            anoinput = anoinputs[operator]
            range_list=[round( float( e.strip().replace(',','.') ), 2 ) for e in info[1:] ]
            ranges.update({operator:[anoinput]+range_list })
    return ranges

def getPointName(set,point):
    name="F%s_"%set
    name+="%.2f"%(point/100)
    name = name.replace('.','p')
    if('-' in name):
        name = name.replace('-','m')
    return name
        
if(__name__=="__main__"):
    BosonChannel="VV"
    operators=["S0","S1","S2","M0","M1","M2","M3","M4","M5","M7","T0","T1","T2","T5","T6","T7","T8","T9"] #April2020 version
    sets=getJsonFromCSV(csvFileName='range.csv')
    
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
                if(sets[op][0]!=12):
                    fout.write("\n\tset anoinputs 12 0.000000e+00")
                fout.write("\n\tset anoinputs %i %8.6fe-12"%(sets[op][0],point/100))
                # fout.write("\n")
                sum_points+=1
            # fout.write("\n\n")
        print("Total number of reweighting points:", sum_points)
