#!/usr/bin/python
#
# script to take sysconfig.json and produce something similar to the 4.X slotmap output
#
# TODO: make it take an argument instead of assuming ./sysconfig.json
#       put in model-specific info to break up the display further (e.g. MD1280 14 disks x 3 rows x 2 trays)
#       apparently MD3060 uses a "description" for each slot that includes the drawer/slot numbering
#
# model info Dell EN-8435A-E6EBD is MD1280
# Dlord - 05/10/2018 - "List of previously discovered disks"
# fixed issue with missing data in  "sysconfig.json" file
# pwh - 05/15/2018 changed to use name "disk.previouslyDiscovered"
#   rather than description "List of previously discovered disks"
# pwh - 08/14/2018 fixed typo of "bayid" to "bayId" when slot is empty
#
import json

valid=0

# will need to make this an argument
with open('sysconfig.json') as json_data:
    d = json.load(json_data)
    
enclosureNames = {}
diskDetails = {}


# older sysconfig.json files appear to omit the disk list
#
for item in d:
    if item['name'] == "disk.previouslyDiscovered":
        valid=1

if valid:
    for item in d:
        if item['name'] == "persist.labels":
            enclosureIdList = item['currentValue']
            if not enclosureIdList:
                print "no persisted labels"
            else:
                for encl in enclosureIdList:
                    if enclosureIdList[encl]['label'] != "retired":
                        enclosureNames[enclosureIdList[encl]['id']] = enclosureIdList[encl]['label']
                    else:
                        enclosureNames[enclosureIdList[encl]['id']] = "RETIRED"
        elif item['name'] == "enclosure.previouslyDiscovered":
            enclosureInfo = item['currentValue']
        elif item['name'] == "disk.previouslyDiscovered":
            diskInfo = item['currentValue']

    for disk in diskInfo:
        diskDetails[disk['devname']] = disk

    for encl in enclosureInfo:
        if enclosureNames and enclosureNames[encl['chassisId']] != "RETIRED":
            print "Enclosure:", enclosureNames[encl['chassisId']], encl['chassis'][0]['vendorId'], encl['chassis'][0]['productId'], encl['chassisId'] 
            for bay in encl['bays']:
                if bay['empty']:
                    print "\t%2d" % bay['bayId']
                else:
                    rawCapacity = diskDetails[bay['devname']]['capacity']
                    capacityGiB = int(rawCapacity/(1024 * 1024 * 1024))
                    print "\t%2d" % bay['bayId'], "\t", bay['description'], "\t", diskDetails[bay['devname']]['logicalDevice'], "\t", diskDetails[bay['devname']]['vendorId'], diskDetails[bay['devname']]['productId'], "\t%5d GiB" % capacityGiB, "\t", bay['devname']
            print
        elif not enclosureNames:
            print "Enclosure: (no label)", encl['chassis'][0]['vendorId'], encl['chassis'][0]['productId'], encl['chassisId'] 
            for bay in encl['bays']:
                if bay['empty']:
                    print "\t%2d" % bay['bayId']
                else:
                    rawCapacity = diskDetails[bay['devname']]['capacity']
                    capacityGiB = int(rawCapacity/(1024 * 1024 * 1024))
                    print "\t%2d" % bay['bayId'], "\t", bay['description'], "\t", diskDetails[bay['devname']]['logicalDevice'], "\t", diskDetails[bay['devname']]['vendorId'], diskDetails[bay['devname']]['productId'], "\t%5d GiB" % capacityGiB, "\t", bay['devname']
            print
else:
    print "Could not find disk list in this sysconfig.json file"
    exit 
