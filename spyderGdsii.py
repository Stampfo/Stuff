# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 21:32:15 2020

@author: Lstaqdev
"""

# OK simplest version of GDSII is: 
# ask user for symbol that is alignmentmarks alignmentmark has to be centered at 0/0 of the subsymbol, I think that 
# is a reasonable restriction

import os

from gdsii.library import Library
from gdsii.elements import *






## Functions used

def openaskfortargetlayerandunits(filename):
    
    with open(filename, 'rb') as stream:
        lib = Library.load(stream)
    
    
    userindex=1
   
    if len(lib)==1:
        print('Only the mainsymbol found, please create a subsymbol for alignmentmarks')
        return
    elif len(lib)>1:
        print('Multiple symbols. Type # of symbol defining marks \n')
        for index,symbol in enumerate(lib):
                print('#'+str(index+1)+' '+str(symbol.name)[1:])
    
    userindex=int(input())
    targetsymbolname=lib[userindex-1].name
    
    
   
    
    return(lib,targetsymbolname,int(round(lib.physical_unit*1e9)))


def recursivesearch(symboltofind,insymbol,x=0,y=0):
    
    global marks
    global symboldictionary
    
    for objects in insymbol:
        if isinstance(objects,SRef):
            if objects.struct_name == symboltofind:
                marks.append((objects.xy[0][0]+x,objects.xy[0][1]+y))
            elif objects.struct_name != symboltofind:
                x1,y1 = objects.xy[0]
                
                recursivesearch(symboltofind,symboldictionary[objects.struct_name],x+x1,y+y1) 




def createsymboldictionary(lib):
    dictlib={}
    for symbols in lib:
        dictlib[symbols.name] = symbols
    return dictlib 



def isreferencedin(structure,instructure):
    for someobject in instructure:
        if isinstance(someobject,SRef) or isinstance(someobject,ARef):
            if someobject.struct_name == structure.name:
                return True
    return False



def findtopstructure(lib):
    for symbols in lib:
        top = True
        for symbols2 in lib:
            if isreferencedin(symbols,symbols2):
                top=False
            
        if top==True:
            return symbols




def findoutermostmarks(marks):   # and sort them
    LL=[0,-100000000]
    LR=[0,-100000000]
    UR=[0,-100000000]
    UL=[0,-100000000]
    for markindex,mark in enumerate(marks):
        LLscore=-mark[0]-mark[1]
        LRscore=-mark[0]+mark[1]
        ULscore=mark[0]-mark[1]
        URscore=mark[0]+mark[1]
        if LLscore>LL[1]:
            LL[1]=LLscore
            LL[0]=markindex
        if LRscore>LR[1]:
            LR[1]=LRscore
            LR[0]=markindex
        if ULscore>UL[1]:
            UL[1]=ULscore
            UL[0]=markindex
        if URscore>UR[1]:
            UR[1]=URscore
            UR[0]=markindex
    return [marks[LL[0]],marks[LR[0]],marks[UL[0]],marks[UR[0]]]



def finddxforGdsii(paths):
    allvectorgraphic=[]
    userindex=1
    for file in paths:
        if '.dxf' in file or '.gds' in file:
            allvectorgraphic.append(file)
    if len(allvectorgraphic)==0:
        print('No design file in folder')
        return
    elif len(allvectorgraphic)>1:
        print('Multiple design files. Type # of file and confirm with enter \n')
        for index,vecfile in enumerate(allvectorgraphic):
                print('#'+str(index+1)+' '+vecfile)
        userindex=int(input())
    return(allvectorgraphic[userindex-1])




def writemarksintoscon(scon,marks,units):
    f=open(scon,'r')
    scontent=f.read()
    if any(regtype in scontent for regtype in ['RL2 ','RL3 ','RL4 ']):
        print('File already has marks, not overwriting')
        return
    sconparts=scontent.split('PC, ')
    if len(marks)==4:
        outputscon=sconparts[0]+'RL4 %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f \n' %(marks[0][0]*units/1000,marks[0][1]*units/1000,marks[1][0]*units/1000,marks[1][1]*units/1000,marks[2][0]*units/1000,marks[2][1]*units/1000,marks[3][0]*units/1000,marks[3][1]*units/1000)
    elif len(marks)==3:
        outputscon=sconparts[0]+'RL3 %.3f, %.3f, %.3f, %.3f, %.3f, %.3f \n' %(marks[0][0]*units/1000,marks[0][1]*units/1000,marks[1][0]*units/1000,marks[1][1]*units/1000,marks[2][0]*units/1000,marks[2][1]*units/1000)    
    elif len(marks)==2:
        outputscon=sconparts[0]+'RL2 %.3f, %.3f, %.3f, %.3f \n' %(marks[0][0]*units/1000,marks[0][1]*units/1000,marks[1][0]*units/1000,marks[1][1]*units/1000) 
    
    for index,i in enumerate(sconparts):
        if index>0:
            outputscon=outputscon+'PC, '+i
        
    outputfilename=scon[:-5]+'Marks'+scon[-5:]
    
    f= open(outputfilename,"w+")
    f.write(outputscon)
    f.close
       

        
def findscon(paths):
    allscon=[]
    userindex=1
    for file in paths:
        if '.scon' in file:
            allscon.append(file)
    if len(allscon)==0:
        print('No Scon file in folder')
        return
    elif len(allscon)>1:
        print('Multiple Scon files. Type # of file and confirm with enter \n')
        for index,sconfile in enumerate(allscon):
                print('#'+str(index+1)+' '+sconfile)
        userindex=int(input())
    return(allscon[userindex-1])



##SCRIPT

paths=os.listdir()   #or could be done with a folder but i think its best to search in the folder the script is sitting in
                        #so ideally there would be only one file in that folder, then program can autofind it
filename=finddxforGdsii(paths)

lib,targetsymbol,units=openaskfortargetlayerandunits(filename)

mainspace = findtopstructure(lib)

symboldictionary = createsymboldictionary(lib)

marks = []

recursivesearch(targetsymbol,mainspace)


usedmarks=findoutermostmarks(marks)


print('These marks are getting used', usedmarks)

scon = findscon(paths)

writemarksintoscon(scon,usedmarks,units)





    
