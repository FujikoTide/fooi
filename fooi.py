#
#   Find Orphaned Obsidian Images
#

# TODO:
# add error checking where needed
# add dry run mode
# create delete folder according to delete folder path specified
# add hard kill mode
# toggle printing to console

import argparse
import json
from pathlib import Path
import re

ORPHANED_FILE_EXTENSIONS = ["png", "jpg", "pdf", "webp"]


parser = argparse.ArgumentParser(
    prog="fooi", 
    description="Finds files orphaned when notes are deleted in Obsidian.", 
    epilog="Thank you for using fooi !",
    add_help=True, 
    allow_abbrev=True
)

parser.add_argument("-p", "--path", required=False, default=Path.cwd())

parser.add_argument("-dr", "--dryrun", required=False, action="store_true", default=False)

parser.add_argument("-l", "--logging", required=False, action="store_false", default=True)

parser.add_argument("-pr", "--print", required=False, action="store_true", default=False)

parser.add_argument("-d", "--delpath", required=False, default="DELETE")

parser.add_argument("-k", "--kill", required=False, action="store_true", default=False)

parser.add_argument("-e", "--extensions", required=False, action="append")


args = parser.parse_args()

target_dir = Path(args.path)

if not target_dir.exists():
    print("The target directory doesn't exist")
    raise SystemExit(1)
else:
    VAULT_DIR = target_dir
    # print(VAULT_DIR)

dryRun = args.dryrun
logToFile = args.logging
printToScreen = args.print
deleteFolderPath = args.delpath

deltarget_dir = Path(args.delpath)

DELETE_DIR = deltarget_dir
# print(DELETE_DIR)


hardKillMode = args.kill
extensions = args.extensions

print(args)

SKIP_DIRS = [DELETE_DIR, ".obsidian"]



def main():
    fileList = getFileList()
    embedLinkList = getEmbedList(fileList)
    orphanedFileList = getOrphanedFileList()
    deletionList = getDeletionList(embedLinkList, orphanedFileList)
    if logToFile and not dryRun:
        logFiles(deletionList)
    if not dryRun:
        createDir()
        moveFiles(deletionList)
    if printToScreen:    
        printFiles(deletionList)


def createDir():
    try:
        DELETE_DIR.mkdir()
        print(f"Directory {DELETE_DIR} created successfully.")
    except FileExistsError:
        print(f"Directory {DELETE_DIR} already exists.")
    except PermissionError:
        print(f"Permission denied: Unable to create {DELETE_DIR}.")
    except Exception as e:
        print(f"An error occured: {e}")

def logFiles(deletionList):
    with Path(Path.cwd() / "filesForDeletion.json").open("w", encoding="utf-8") as deletionFile:
        json.dump(deletionList, deletionFile, indent=4, ensure_ascii=False)


def moveFiles(deletionList):
    for file in deletionList:
        source = VAULT_DIR / file
        destination = DELETE_DIR / file
     
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
