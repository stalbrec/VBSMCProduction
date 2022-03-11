#!/usr/bin/env python3
from pylhe import read_lhe_with_attributes, to_awkward_nanoaod
import os


pdgid_lut = {1:'d',2:'u',3:'s',4:'c',5:'b',6:'t',23:'Z',12:'ve',14:'vmu',16:'vt',22:'γ',21:'g'}
# pdgid_lut_anti = {-i:'#bar{%s}'%pdgid_lut[i] for i in pdgid_lut.keys()}
pdgid_lut_anti = {-i:'%s~'%pdgid_lut[i] for i in pdgid_lut.keys()}

pdgid_lut.update(pdgid_lut_anti)

pdgid_lut_2 = {11:'e-',13:'mu-',15:'tau-',-24:'W-'}
pdgid_lut.update(pdgid_lut_2)
pdgid_lut_2_anti = {-i:pdgid_lut_2[i].replace('-','+') for i in pdgid_lut_2.keys()}
pdgid_lut.update(pdgid_lut_2_anti)

import numpy as np
from hist import Hist
from prettytable import PrettyTable        
def print_particles(particles):
    lhe_table = PrettyTable()
    lhe_table.field_names = ['index','pdgid','status','parent1','parent2','pt','mass','eta']
    for index,p in enumerate(particles):            
        lhe_table.add_row([index,str(pdgid_lut.get(p.pdgId,p.pdgId)),p.status,p.parent1,p.parent2,p.pt,p.mass,p.eta])
    print(lhe_table)

def draw_particle_tree(particles):
    try:
        from asciiplotter import Canvas
    except:
        print('In order to draw process tree please install package "asciiplotter"!')
    def build_tree(particles_):
        from copy import deepcopy
        particles_indices = [i+1 for i in range(len(particles_))]
        tree = []
        layer = [0]
        while layer != []:
            new_layer = []
            new_layer_parent1 = []
            new_layer_obj = []
            for ip in particles_indices:
                p = particles_[ip-1]
                if(p.parent1 in layer or p.parent2 in layer):
                    new_layer.append(ip)
                    new_layer_parent1.append(p.parent1)
                    new_layer_obj.append(p)

            new_layer = [x for _,x in sorted(zip(new_layer_parent1,new_layer))]
            for p in new_layer:
                particles_indices.remove(p)
            if(new_layer != []):
                tree.append(new_layer)
            layer = new_layer
        return tree
    
    tree  = build_tree(particles)

    
    heights = [len(l) for l in tree]
    max_height = max(heights)
    
    layers = len(tree)*2 + 1

    node_height = 5
    layer_width = 7

    #pad layers
    filled_tree = []
    for layer in tree:
        filled_layer = []
        prepending,appending = 0,0
        if len(layer)<max_height:
            prepending = (max_height - len(layer)) //2
            appending = (max_height-len(layer)) - prepending
        for i in range(prepending):
            filled_layer.append(None)
        filled_layer += layer
        for i in range(appending):
            filled_layer.append(None)

        filled_tree.append(filled_layer)

    padding = 2
    c_width = padding + layer_width*layers + padding
    c_height = padding + max_height*node_height +padding
    
    c = Canvas(height=c_height,width=c_width)
    #c.fill('#')
    xpos = padding+layer_width
    particle_pos = {}
    for layer in filled_tree:
        ypos = padding + node_height//2
        for node in layer:
            if(node is not None):
                particle_pos.update({node:(xpos,ypos)})
            ypos += node_height
            
        xpos += 2*layer_width


    for ip,pos in particle_pos.items():
        p = particles[ip-1]
        line_char = '.'
        if(p.parent1 != 0):
            parent1_pos = particle_pos[p.parent1]
            c.line(pos[0]-1,pos[1],parent1_pos[0]+1,parent1_pos[1],line_char)
        if(p.parent2 != 0):
            parent2_pos = particle_pos[p.parent2]
            c.line(pos[0]-1,pos[1],parent2_pos[0]+1,parent2_pos[1],line_char)
            
    for ip,pos in particle_pos.items():
        p = particles[ip-1]
        node_text = str(pdgid_lut.get(p.pdgId,p.pdgId))
        c.text(pos[0],pos[1],node_text)
        
    print(c)
        
def process(args):
    events = to_awkward_nanoaod(read_lhe_with_attributes(args.lhe))

    ievent = 0
    for event in events:
        if(args.maxEvents > 0 and ievent>args.maxEvents):
            break
        ievent += 1
        

        print_particles(event.GenPart)
        draw_particle_tree(event.GenPart)
if(__name__=='__main__'):
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("--lhe",type=str,help='lhe file to be processed')
    parser.add_argument("--maxEvents",default=-1,type=int,help='maximum number of events to process per LHE file')
    args = parser.parse_args()
 
    process(args)
