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
# pwh - 06/13/2019 fix to deal with situation where some enclosures are labelled and others are not
#                  also call out drives that show up as "LEGACY_SAS" instead of in an enclosure
# EHarmer - 04/21/2020 fix to cope with NVME drives in "LEGACY_NVME"
#                      Also modify so that it'll take a path argument instead of always assuming it's in the same dir as sysconfig.json
#
import json, os, sys

from operator import itemgetter

valid=0


def process_sysconfig(sysconfig_file):
	# will need to make this an argument
	with open(sysconfig_file) as json_data:
		d = json.load(json_data)

	enclosureNames = {}
	diskDetails = {}
	unmappedDisks = {}

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
			if (disk['enclosure'] == 'LEGACY_SAS'):
				unmappedDisks[disk['devname']] = disk
				disk_type=disk['enclosure']
				NVME_DRIVES=False
			elif (disk['enclosure'] == 'LEGACY_NVME'):
				unmappedDisks[disk['devname']] = disk
				disk_type=disk['enclosure']
				NVME_DRIVES=True


		for encl in enclosureInfo:
			# it is possible for us to have an un-retired but not labelled chassis, even when other chassis are labelled
			# ensure that encl['chassisId'] really shows up in the label list before referencing it so we don't blow up
			if enclosureNames and (encl['chassisId'] in enclosureNames) and enclosureNames[encl['chassisId']] != "RETIRED":
				print "Enclosure:", enclosureNames[encl['chassisId']], encl['chassis'][0]['vendorId'], encl['chassis'][0]['productId'], encl['chassisId']
				for bay in encl['bays']:
					if bay['empty']:
						print "\t%2d" % bay['bayId']
					else:
						rawCapacity = diskDetails[bay['devname']]['capacity']
						capacityGiB = int(rawCapacity/(1024 * 1024 * 1024))
						print "\t%2d" % bay['bayId'], "\t", bay['description'], "\t", diskDetails[bay['devname']]['logicalDevice'], "\t", diskDetails[bay['devname']]['vendorId'], diskDetails[bay['devname']]['productId'], "\t%5d GiB" % capacityGiB, "\t", bay['devname']
				print
			elif not enclosureNames or not (encl['chassisId'] in enclosureNames):
				print "Enclosure: (no label)", encl['chassis'][0]['vendorId'], encl['chassis'][0]['productId'], encl['chassisId']
				for bay in encl['bays']:
					if bay['empty']:
						print "\t%2d" % bay['bayId']
					else:
						rawCapacity = diskDetails[bay['devname']]['capacity']
						capacityGiB = int(rawCapacity/(1024 * 1024 * 1024))
						print "\t%2d" % bay['bayId'], "\t", bay['description'], "\t", diskDetails[bay['devname']]['logicalDevice'], "\t", diskDetails[bay['devname']]['vendorId'], diskDetails[bay['devname']]['productId'], "\t%5d GiB" % capacityGiB, "\t", bay['devname']
		if unmappedDisks:
			print "\nThe following devices are not mapped to any enclosure (they show up as " + disk_type + "):\n"
			if NVME_DRIVES:
				print "THESE ARE NVME DRIVES - please check HCL as we currently only support certain models of Seagate NYTRO drives\n"
			for disk in sorted(unmappedDisks.values(), key=itemgetter('bay')):
				rawCapacity = disk['capacity']
				capacityGiB = int(rawCapacity/(1024 * 1024 * 1024))
				print "\t%2d" % disk['bay'], "\t\t\t", disk['logicalDevice'], "\t", disk['vendorId'], disk['productId'], "\t%5d GiB" % capacityGiB, "\t", disk['devname']
	else:
		print "Could not find disk list in this sysconfig.json file"
		exit

def slotmap5_help ():
	help_output = """
Usage: slotmap5.py [sysconfig.json_file]

Can be run in the same directory as sysconfig.json file without any argument
     # slotmap5.py

Can provide a path to the sysconfig.json file
     # slotmap5.py ./nef/sysconfig.json

"""
	print help_output

######################
#
# run section
#
######

if len(sys.argv) == 1:
	sysconfig_file = "sysconfig.json"
if len(sys.argv) == 2:
	sysconfig_file = sys.argv[1]

if os.path.isfile(sysconfig_file):
	process_sysconfig(sysconfig_file)
else:
	print
	print "Error ==> " + sysconfig_file + " does not exist"
	slotmap5_help()
