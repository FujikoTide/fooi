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

# YOUR OBSIDIAN VAULT LOCATION GOES HERE !
VAULT_DIR = Path(r"")
DELETE_DIR = "DELETE2"
SKIP_DIRS = [DELETE_DIR, ".obsidian"]
ORPHANED_FILE_EXTENSIONS = ["png", "jpg", "pdf", "webp"]


def main():
    deleteDir = Path(VAULT_DIR / DELETE_DIR)
    fileList = getFileList()
    embedLinkList = getEmbedList(fileList)
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
    print(f"Files to be deleted (moved to {DELETE_DIR} folder):\n")
    for file in deletionList:
        print(file)
    

def getFileList():
    return list(VAULT_DIR.rglob("*.md"))


def getEmbedList(fileList):
    embedList = []
    extensions = "|".join(ORPHANED_FILE_EXTENSIONS)

    for file in fileList:
        with open(file, 'r', encoding="utf-8") as f:
            match = re.findall(f"\[\[(.+?({extensions})).*?]]", f.read())
            if len(match) > 0:
                for embed in match:
                    embedList.append(embed[0])
    
    return embedList


def getDeletionList(embedLinkList, orphanedFileList):
    deletionList = []
    for embedFile in orphanedFileList:
        file = Path(embedFile)
        if file.name not in embedLinkList:
            deletionList.append(file.name)
    
    return deletionList


def filterFiles(fileType):
    return [file for file in VAULT_DIR.rglob(f"*.{fileType}") if set(file.parts).isdisjoint(SKIP_DIRS)]


def getOrphanedFileList():
    orphanedFileList = []
    
    for fileType in ORPHANED_FILE_EXTENSIONS:
        fileTypeList = filterFiles(fileType)
        if len(fileTypeList) > 0:
            for file in fileTypeList:
                orphanedFileList.append(file)

    return orphanedFileList

  
if __name__ == "__main__":
    main()
