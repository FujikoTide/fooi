#
#   Find Orphaned Obsidian Images
#

# TODO:
# add error checking where needed
# add hard kill mode

import argparse
import json
from pathlib import Path
import re


parser = argparse.ArgumentParser(
    prog="fooi", 
    description="Finds files orphaned when notes are deleted in Obsidian.", 
    epilog="Thank you for using fooi !",
    add_help=True, 
    allow_abbrev=True
)

parser.add_argument("path")
parser.add_argument("delpath")
parser.add_argument("-e", "--extensions", required=True, action="append")
parser.add_argument("-dr", "--dryrun", required=False, action="store_true", default=False)
parser.add_argument("-l", "--logging", required=False, action="store_false", default=True)
parser.add_argument("-pr", "--print", required=False, action="store_true", default=False)
parser.add_argument("-k", "--kill", required=False, action="store_true", default=False)

args = parser.parse_args()

target_dir = Path(args.path)
if not target_dir.exists():
    print("The target directory doesn't exist")
    raise SystemExit(1)
else:
    VAULT_DIR = target_dir
    # print(VAULT_DIR)

DELETE_DIR = Path(args.delpath)
# print(DELETE_DIR)

ORPHANED_FILE_EXTENSIONS = args.extensions
SKIP_DIRS = [DELETE_DIR, ".obsidian"]

dryRun = args.dryrun
logToFile = args.logging
printToScreen = args.print
hardKillMode = args.kill


def main():
    fileList = getFileList()
    embedLinkList = getEmbedList(fileList)
    prospectiveFileList = getProspectiveFileList()
    deletionList = getDeletionList(embedLinkList, prospectiveFileList)
    if len(deletionList) > 0: 
        if logToFile and not dryRun:
            logFiles(deletionList)
        if not dryRun:
            createDir()
            moveFiles(deletionList)
        if printToScreen:    
            printFiles(deletionList)
    else:
        print("No orphaned files found.")


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
        
    print(f"Files to be deleted (moved to {DELETE_DIR} folder):\n")


def printFiles(deletionList):
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


def getDeletionList(embedLinkList, prospectiveFileList):
    deletionList = []

    for embedFile in prospectiveFileList:
        file = Path(embedFile)
        if file.name not in embedLinkList:
            deletionList.append(file.name)
    
    return deletionList


def filterFiles(fileType):
    return [file for file in VAULT_DIR.rglob(f"*.{fileType}") if set(file.parts).isdisjoint(SKIP_DIRS)]


def getProspectiveFileList():
    prospectiveFileList = []
    
    for fileType in ORPHANED_FILE_EXTENSIONS:
        fileTypeList = filterFiles(fileType)
        if len(fileTypeList) > 0:
            for file in fileTypeList:
                prospectiveFileList.append(file)

    return prospectiveFileList

  
if __name__ == "__main__":
    main()
