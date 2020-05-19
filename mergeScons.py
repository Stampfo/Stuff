import os
import shutil


def getListOffolder():  
    listOfFile = os.listdir()     
    folders=[]
    for entry in listOfFile:
        if os.path.isdir(entry):
            subfolder=os.listdir(entry)
            concounter=0
            for file in subfolder:
                if '.scon' in file or '.co7' in file:
                    concounter+=1
            if concounter==1:
                folders.append(entry)
            
    return folders    

def mergeallfolders(targetfolder,folders):
    if targetfolder not in os.listdir():
        os.mkdir(targetfolder)
    for folder in folders:
        files=os.listdir(folder)
        for file in files:
            shutil.move(folder+'//'+file,targetfolder+'//'+file)
            
            
def findname():
    listofFile = os.listdir()
    for entry in listofFile:
        if '.dxf' in entry:
            name=entry[:-4]+'merged'
            break
        elif '.gds' in entry:
            name=entry[:-4]+'merged'
            break
        else: 
            name='Mergedfiles'
    return name

name=findname()
folders=getListOffolder()
mergeallfolders(name,folders)
