#!/usr/bin/env python
import os,json

# operators=["S0","S1","S2","M0","M1","M2","M3","M4","M5","M7","T0","T1","T2","T5","T6","T7","T8","T9"] #April2020 version
operators=["S0","S1","S2","M0","M1","M2","M3","M4","M5","M6","M7","T0","T1","T2","T3","T4","T5","T6","T7","T8","T9"] #August2021 version
# "S0=1 S1=1 S2=1 M0=1 M1=1 M2=1 M3=1 M4=1 M5=1 M7=1 T0=1 T1=1 T2=1 T5=1 T6=1 T7=1 T8=1 T9=1"
skip_operators = ['M6']
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
"T3":15,
"T4":16,
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

def write_snippet(op,op_info):
    f_snippet = open("snippet.cxx","a")
    
    n_points = op_info[1]
    stepsize = op_info[3]
    start = op_info[2]
    end = round(op_info[1]*op_info[3]+op_info[2],2)
    f_snippet.write('for(unsinged int i = 0; i < %i; i++){'%n_points)
    f_snippet.write('//%s=[%i,%.2f,%.2f,%.2f]\n'%(op,n_points,stepsize,start,end))
    f_snippet.write('\treweight_names.push_back(getParName("%s",%.2f,%.2f,i));\n'%(op,start,stepsize))
    f_snippet.write('}\n')

def get_order_string():
    result = ""
    for op in operators:
        if(op in skip_operators):
            continue
        result += f" {op}=1"
    return result
        
def get_customize_card_content(points):
    content = ""
    for op in operators:
        value = points.get(op,0)
        if(value==0):
            content += f"set param_card anoinputs {anoinputs[op]} 0.0"
        else:
            content += f"set param_card anoinputs {anoinputs[op]} {points.get(op,0.0):.2g}"

        if(op != operators[-1]):
            content += "\n"
    print(content)
    return content

def get_reweighting_card_content(reweight_range_csv, debug=False):
    sets=getJsonFromCSV(csvFileName=reweight_range_csv)

    reweighting_card_content = "change helicity False\n"
    reweighting_card_content += "change rwgt_dir rwgt\n"
    reweighting_card_content += "\n"
    sum_points=0
    for op in operators:
        # if(op == 'M6'):
        if(op in skip_operators):
            if(debug):
                print("Operator LM6 has been removed since it is proportional to other couplings.\nNot writing it to reweighting card")
            continue
        reweighting_card_content += f"\n#******************** F{op} ********************"
        for i in range(0,int(sets[op][1])):
            point=100*sets[op][2]+i*100*sets[op][3]
            reweighting_card_content += f"\nlaunch --rwgt_name={getPointName(op,point)}"
            if(sets[op][0]!=12):
                reweighting_card_content += "\n\tset anoinputs 12 0.000000e+00"
            reweighting_card_content += f"\n\tset anoinputs {sets[op][0]} {point/100:8.6f}e-12"
            
            sum_points+=1
    if(debug):
        print("Total number of reweighting points:", sum_points)

    return reweighting_card_content


if(__name__=="__main__"):
    # BosonChannel="VV"
    # sets=getJsonFromCSV(csvFileName='range_veryshort_positive.csv')
    # sets=getJsonFromCSV(csvFileName='range.csv')
    
    # print(sets)
    # with open(BosonChannel+"Range_veryshort.dat","wt") as fout:
    #     fout.write("change helicity False\n")
    #     fout.write("change rwgt_dir rwgt")
    #     fout.write("\n\n")
    #     sum_points=0
    #     if(os.path.isfile("snippet.cxx")):
    #         os.system("rm snippet.cxx")
    #     for op in operators:
    #         write_snippet(op,sets[op])
    #         fout.write("\n#******************** F%s ********************"%op)
    #         for i in range(0,int(sets[op][1])):
    #             point=100*sets[op][2]+i*100*sets[op][3]
    #             fout.write("\nlaunch --rwgt_name=%s"%getPointName(op,point))
    #             if(sets[op][0]!=12):
    #                 fout.write("\n\tset anoinputs 12 0.000000e+00")
    #             fout.write("\n\tset anoinputs %i %8.6fe-12"%(sets[op][0],point/100))
    #             # fout.write("\n")
    #             sum_points+=1
    #         # fout.write("\n\n")
    #     print("Total number of reweighting points:", sum_points)


    with open("VVRange_veryshort.dat","wt") as fout:
        fout.write(get_reweighting_card_content("range_veryshort_positive.csv"))
    
