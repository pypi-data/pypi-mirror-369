import random
import os.path
from pyxtal import pyxtal
from pyxtal.symmetry import Group
from pyxtal.tolerance import Tol_matrix
from pyxtal.lattice import Lattice
from ase.data import covalent_radii, atomic_numbers
from aegon.libstdio import read_main_input
#------------------------------------------------------------------------------------------------
'''
Unit cell constrictions
'''
def uc_restriction(file):
    '''Obtains the UC restrictions imposed by the user. Format a b c alpha beta gamma.

    out:
    restr_uc (Lattice); Pyxtal object for the lattice
    '''
    pyxtal_lattice = False
    if os.path.isfile(file):
        f=open(file,"r")
        for line in f:
            if not line.startswith('#') and 'fixed_lattice' in line:
                line = line.split()
                a,b,c,alpha,beta,gamma = float(line[1]), float(line[2]), float(line[3]), float(line[4]), float(line[5]), float(line[6])
                pyxtal_lattice = Lattice.from_para(a,b,c,alpha,beta,gamma)
                break
        f.close()
    return pyxtal_lattice

#------------------------------------------------------------------------------------------------
'''
Interatomic distances
'''
def get_percent_tolerances(species, tolerance_percent):
    '''Gets the default tolerances for each pair of atoms in the structure

    out:
    solids_tolerances (list), List containing tuples with each min int dist, [(s1,s2,d1),(s1,s3,d2),...]
    pyxtal_tolerances (Tol_matrix), PyXtal object used for atomic tolerance in generation of structures
    '''
    pyxtal_tolerances = Tol_matrix()
    solids_tolerances = []
    species_number = [atomic_numbers[s] for s in species]
    if len(species) == 1:
        s = species[0]
        n = species_number[0]
        r = covalent_radii[n]
        tv = r*tolerance_percent*2
        tv = round(tv,2)
        solids_tolerances.append((s,s,tv))
        pyxtal_tolerances.set_tol(s,s,tv)
    else:
        for i in range(len(species)):
            s1 = species[i]
            r1 = covalent_radii[species_number[i]]
            tv = r1*tolerance_percent
            tv = round(tv,2)
            solids_tolerances.append((s1,s1,tv))
            pyxtal_tolerances.set_tol(s1,s1,tv)
            for j in range(i+1,len(species)):
                s2 = species[j]
                r2 = covalent_radii[species_number[j]]
                tv_mix = (r1+r2)*tolerance_percent
                tv_mix = round(tv_mix,2)
                solids_tolerances.append((s1,s2,tv_mix))
                pyxtal_tolerances.set_tol(s1,s2,tv_mix)
    return solids_tolerances,pyxtal_tolerances

#------------------------------------------------------------------------------------------------
def interatom_restriction(file, species, tolerance_percent):
    pyxtal_mtx_tolerance, solids_tolerances = False,False
    if os.path.isfile(file):
        xfile = open(file,"r")
        flag = False
        for line in xfile:
            if not line.startswith('#') and 'custom_tolerances' in line:
                pyxtal_tolerances = Tol_matrix()
                solids_tolerances = []
                readline = line.split()
                readline = readline[1:]
                for i in readline:
                    x = i.split(',')
                    tupla = (x[0],x[1],float(x[2]))
                    solids_tolerances.append(tupla)
                    pyxtal_tolerances.set_tol(x[0],x[1],float(x[2]))
                flag = True
        if flag == False:
            solids_tolerances, pyxtal_tolerances = get_percent_tolerances(species,tolerance_percent)
        xfile.close()
    return solids_tolerances, pyxtal_tolerances

#------------------------------------------------------------------------------------------------
'''
Restrictions on symmetry
'''
def get_symmetry_constrains(file,str_range, dimension=3):
    ''' This routine extracts a desired range of integers to be used as SGs in the construction of
    structures. The result is presented in list format, eg. range 1-5, range_list = [1,2,3,4,5]. If
    the restriction is not provided, the list ranges from 2-80 for 2D structures and from 2-230 for 3D.

    in: str_range (str), flag to locate the desired range of integers
        dimension (int), list of all numbers within the desired range
    out: range_list (list), list of all numbers within the desired range
    '''
    if os.path.isfile(file):
        f = open(file,'r')
        flag = False
        for line in f:
            if not line.startswith('#') and str_range in line:
                line = line.lstrip('\t\n\r')
                line = line.split()
                readline = line[1].split('-')
                bottom, top = int(readline[0])-1, int(readline[1])
                range_list = [s+1 for s in range(bottom,top)]
                flag = True
                break
        f.close()
        if flag == False and dimension == 2:
            range_list = [i for i in range(2,81)]
        elif flag == False and dimension == 3:
            range_list = [i for i in range(2,231)]
    return range_list

#------------------------------------------------------------------------------------------------
def random_crystal_generator(file):
    df = read_main_input(file)
    composition = df.get_comp(key='COMPOSITION')
    species = [k[0] for k in composition.comp]
    formula_units = df.get_int('formula_units',2)
    atms_per_specie = [k[1]*formula_units for k in composition.comp]
    dimension = df.get_int('dimension',3)
    vol_factor = df.get_float('volume_factor',1.0)
    revisit_syms = df.get_int('revisit_syms',1)
    tol_atomic_overlap = df.get_float('tol_atomic_overlap',0.97)
    number_of_xtals = df.get_int('number_of_xtals',False)
    sym_list = get_symmetry_constrains(file,'symmetries', dimension)
    uc_rest = uc_restriction(file)
    solids_mtx_tolerance, pyxtal_mtx_tolerance = interatom_restriction(file, species, tol_atomic_overlap)
    xtalist_out = []
    xc = 1
    for i in range(revisit_syms):
        if number_of_xtals:
            random.shuffle(sym_list)
        for sym in sym_list:
            xtal = pyxtal()
            if dimension == 2:
                try:
                    xtal.from_random(dimension,sym,species,atms_per_specie,thickness=0.0)
                except:
                    continue
                else:
                    sg = Group (sym)
                    sg_symbol = str(sg.symbol)
                    ase_xtal = xtal.to_ase()
                    print('random_000_'+str(xc).zfill(3)+' ---> SG_'+str(sg_symbol)+"_("+str(sym)+")")
                    xtalist_out.append(ase_xtal)
                    xc = xc + 1
            elif dimension == 3:
                try:
                    if uc_rest:
                        xtal.from_random(dimension,sym,species,atms_per_specie,vol_factor,uc_rest,pyxtal_mtx_tolerance)
                    else:
                        xtal.from_random(dimension,sym,species,atms_per_specie,vol_factor,tm=pyxtal_mtx_tolerance)
                except:
                    continue
                else:
                    sg = Group (sym)
                    sg_symbol = str(sg.symbol)
                    ase_xtal = xtal.to_ase()
                    print('random_000_'+str(xc).zfill(3)+' ---> SG_'+str(sg_symbol)+"_("+str(sym)+")")
                    xtalist_out.append(ase_xtal)
                    xc = xc + 1
            if number_of_xtals!= False and xc == number_of_xtals+1:
                break
    return xtalist_out
#------------------------------------------------------------------------------------------------
input_text = """
---COMPOSITION---
Au 2
Ag 3
---COMPOSITION---
formula_units       2
dimension           3
number_of_xtals     5
symmetries          16-74
fixed_lattice       2.474 8.121 6.138 90.0 90.0 90.0
#custom_tolerances   Ti,Ti,1.2 Ti,O,1.3 O,O,1.2
tol_atomic_overlap  0.90
"""
def test():
    file = 'INPUT.txt'
    with open(file, "w") as f: f.write(input_text)
    x = random_crystal_generator(file)
#------------------------------------------------------------------------------------------------
