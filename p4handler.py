#p4handler
#author: David Korder

import subprocess
import argparse
import os
from pathlib import Path
import shutil

parser = argparse.ArgumentParser()
required = parser.add_argument_group('required arguments')
required.add_argument("--file", help="Path to p4 source file", required=True)
required.add_argument("--target", help="Target for compiled files", required=True)

parser.add_argument("--compiler", help="Compiler path", nargs='?', default="/home/korder/mysde/bf-sde-9.11.2/install/bin/bf-p4c")
parser.add_argument("--output", help="Output path; default is ./<profile name>/<profile name>")
parser.add_argument("--copy", help="Flag for copying files onto switch", default=True, action='store_true')
parser.add_argument("--no-copy", help="Flag for not copying files onto switch", dest="copy", action='store_false')

args = parser.parse_args()

profileName = Path(args.file).stem

compilerPath = args.compiler
outputPath = args.output
if outputPath == None:
    outputPath = os.path.abspath(os.path.join(profileName, profileName))

target = args.target

#------------
# Compile
#------------

print("Compiling...")

cmd = compilerPath
cmd += " "
cmd += str(os.path.abspath(args.file))
cmd += " -o " + outputPath
cmd += " --bf-rt-schema " + outputPath + "/bf-rt.json"

result = subprocess.run([cmd], shell=True, capture_output=True, text=True)
print(result.stdout)
print(result.stderr)

if result.returncode == 0:
    print("Compilation successful!")
else:
    print("Compilation failed!")
    exit()


#------------
# Create profile info file
#------------

infoFile = [
        "# Name\n",
        profileName + "\n",
        "# Description\n",
        "Profile for testing of loading custom switch programs\n",
        "# Eof\n"
    ]

profileInfoFilePath = os.path.join(outputPath, "profileInfo")
with open(profileInfoFilePath, "w+") as fileProfileInfo:
    fileProfileInfo.writelines(infoFile)


#------------
# Rename .conf file
#------------

confFilePath = os.path.join(outputPath, "switch.conf")
os.rename(os.path.join(outputPath, profileName + ".conf"), confFilePath)


#------------
# Modify switch.conf
#------------

import json

data = []

with open(confFilePath, 'r') as confFile:
    data = json.load(confFile)

switchWorkingDir = os.path.join("/mnt/flash/custom_profiles", profileName)

data['p4_devices'][0]['p4_programs'][0]['bfrt-config']                = os.path.join(switchWorkingDir, "bfrt.json")
data['p4_devices'][0]['p4_programs'][0]['p4_pipelines'][0]['context'] = os.path.join(switchWorkingDir, "context.json")
data['p4_devices'][0]['p4_programs'][0]['p4_pipelines'][0]['config']  = os.path.join(switchWorkingDir, "tofino.bin")
data['p4_devices'][0]['p4_programs'][0]['p4_pipelines'][0]['path']    = switchWorkingDir
data['p4_devices'][0]['p4_programs'][0]['model_json_path']            = ""

with open(confFilePath, 'w') as writeConfFile:
    writeConfFile.write(json.dumps(data, indent=4, separators=(',', ': ')))

print("Modyfing successful!")


#------------
# Copy files onto switch
#------------

if (args.copy is False):
    exit()

# create a folder which will contain all required files for the switch
outputDir = os.path.join(outputPath, profileName)
if os.path.exists(outputDir):
    shutil.rmtree(outputDir)
os.mkdir(outputDir)

shutil.copy(confFilePath, outputDir)
shutil.copy(profileInfoFilePath, outputDir)
shutil.copy(os.path.join(outputPath, "pipe/context.json"), outputDir)
shutil.copy(os.path.join(outputPath, "pipe/tofino.bin"), outputDir)
shutil.copy(os.path.join(outputPath, "bf-rt.json"), outputDir)

# scp the folder onto the switch
# NOTE: Authorization must be enabled on the switch prior to this step
# in config mode use: aaa authorization exec default local

cmd = "scp -r " + outputDir + " " + target + ":/mnt/flash/custom_profiles"

result = subprocess.run([cmd], shell=True, capture_output=True, text=True)
print(result.stdout)
print(result.stderr)

if result.returncode == 0:
    print("Files copied onto switch successfully!")
else:
    print("Copying files onto switch failed!")