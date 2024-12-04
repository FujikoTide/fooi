#
#   Find Orphaned Obsidian Images
#

# TODO:
# add command line functionality
# add error checking where needed
# add dry run mode

import json
from pathlib import Path
import re

DELETEDIR = "DELETE"
SKIP_DIRS = ["DELETE", ".obsidian"]

def main():
    vaultDir = Path(r"")
    deleteDir = Path(vaultDir / DELETEDIR)
    fileList = getFileList(vaultDir)
    imageLinkList = getImageLinkList(fileList)
    imageFileList = getImageFileList(vaultDir)
    # make deletion list a function I suppose?
    deletionList = getDeletionList(imageLinkList, imageFileList)

    logFiles(deleteDir, deletionList)
    moveFiles(vaultDir, deleteDir, deletionList)
    printFiles(deletionList)


def logFiles(deleteDir, deletionList):
    try:
        deleteDir.mkdir()
        print(f"Directory {deleteDir} created successfully.")
    except FileExistsError:
        print(f"Directory {deleteDir} already exists.")
    except PermissionError:
        print(f"Permission denied: Unable to create {deleteDir}.")
    except Exception as e:
        print(f"An error occured: {e}")

    with Path(deleteDir / "filesForDeletion.json").open("w", encoding="utf-8") as deletionFile:
        json.dump(deletionList, deletionFile, indent=4, ensure_ascii=False)


def moveFiles(vaultDir, deleteDir, deletionList):
    for file in deletionList:
        source = vaultDir / file
        destination = deleteDir / file
     
        try:
            with destination.open(mode="xb") as file:
                file.write(source.read_bytes())
        except FileExistsError:
            print(f"File {destination} already exists.")
        else:
            source.unlink()


def printFiles(deletionList):
    print("Files to be deleted (moved to DELETE folder):\n")
    for file in deletionList:
        print(file)
    

def getFileList(vaultDir):
    return list(vaultDir.rglob("*.md"))


def getImageLinkList(fileList):
    imageList = []
    for file in fileList:
        with open(file, 'r', encoding="utf-8") as f:
            match = re.findall("\[\[(.+?(png|jpg|pdf)).*?]]", f.read())
            if len(match) > 0:
                for image in match:
                    imageList.append(image[0])
    
    return imageList

def getDeletionList(imageLinkList, imageFileList):
    deletionList = []
    for imageFile in imageFileList:
        file = Path(imageFile)
        if file.name not in imageLinkList:
            deletionList.append(file.name)
    
    return deletionList

# functionalise the list stuff
def getImageFileList(vaultDir):
    imageFileList = []
    # must be an iterable for isdisjoint to work
    
    pngList = [item for item in vaultDir.rglob("*.png") if set(item.parts).isdisjoint(SKIP_DIRS)]
    if len(pngList) > 0:
        for file in pngList:
            imageFileList.append(file)

    jpgList = [item for item in vaultDir.rglob("*.jpg") if set(item.parts).isdisjoint(SKIP_DIRS)]
    if len(jpgList) > 0:
        for file in jpgList:
            imageFileList.append(file)

    pdfList = [item for item in vaultDir.rglob("*.pdf") if set(item.parts).isdisjoint(SKIP_DIRS)]
    if len(pdfList) > 0:
        for file in pdfList:
            imageFileList.append(file)

    return imageFileList

  
if __name__ == "__main__":
    main()
