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

VAULT_DIR = Path(r"")
DELETE_DIR = "DELETE"
SKIP_DIRS = [DELETE_DIR, ".obsidian"]
ORPHANED_FILE_EXTENSIONS = ["png", "jpg", "pdf"]

def main():
    deleteDir = Path(VAULT_DIR / DELETE_DIR)
    fileList = getFileList()
    embedLinkList = getImageLinkList(fileList)
    orphanedFileList = getOrphanedFileList()
    deletionList = getDeletionList(embedLinkList, orphanedFileList)
    logFiles(deleteDir, deletionList)
    moveFiles(deleteDir, deletionList)
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


def moveFiles(deleteDir, deletionList):
    for file in deletionList:
        source = VAULT_DIR / file
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
    

def getFileList():
    return list(VAULT_DIR.rglob("*.md"))


def getImageLinkList(fileList):
    embedList = []
    for file in fileList:
        with open(file, 'r', encoding="utf-8") as f:
            match = re.findall("\[\[(.+?(png|jpg|pdf)).*?]]", f.read())
            if len(match) > 0:
                for image in match:
                    embedList.append(image[0])
    
    return embedList

def getDeletionList(embedLinkList, orphanedFileList):
    deletionList = []
    for embedFile in orphanedFileList:
        file = Path(embedFile)
        if file.name not in embedLinkList:
            deletionList.append(file.name)
    
    return deletionList


def filterDirectories(fileType):
    return [item for item in VAULT_DIR.rglob(f"*.{fileType}") if set(item.parts).isdisjoint(SKIP_DIRS)]


def getOrphanedFileList():
    orphanedFileList = []
    
    for fileType in ORPHANED_FILE_EXTENSIONS:
        fileTypeList = filterDirectories(fileType)
        if len(fileTypeList) > 0:
            for file in fileTypeList:
                orphanedFileList.append(file)

    return orphanedFileList

  
if __name__ == "__main__":
    main()
