#!/bin/bash
#
# upgradecd.sh
#
# Script to mount a NS5 Upgrade ISO and to 
# create the publishers and run a dry-run upgrade
#
# Copyright (C) 2019  Nexenta Systems
# Marc Molleman <marc.molleman@nexenta.com>
# Version 1.2
#

#isofile="NS_UpgradeCD_5.2.1_CP1.iso"


# DO NOT CHANGE ANYTHING BELOW THIS LINE

isodir="./"
isofile="$1"


if [ $1 = "restorepublisher" ] ;
then
echo "Destroying publishers"
publisher destroy nexenta ; publisher destroy HighAvailability
echo "Restoring saved publishers"
publisher create nexenta https://prodpkg.nexenta.com/nstor/pkg5/ ; publisher create HighAvailability https://prodpkg.nexenta.com/thirdparty/HAC/rsf/pkg5/
echo "Listing restored publishers"
publisher list 
sleep 5
echo
else

echo "Creating checkpoint pre-$isofile"
software checkpoint pre-$isofile
cd $isodir
echo "Creating Upgrade Repo Mountpoint"
mkdir -p /media/NS_UpgradeCD 
echo "Mounting Upgrade ISO"
mount -F hsfs -o ro `lofiadm -a $isodir$isofile` /media/NS_UpgradeCD 
	# lofiadm -a $isodir$isofile /dev/lofi/1
	# mount -F hsfs -o ro /dev/lofi/1 /media/NS_UpgradeCD
echo "Discovering new publishers"
publisher discover 
echo
sleep 1
echo "Saving current publisher list to publisher.out"
publisher list > ./publisher.out
echo "Destroying old publishers"
publisher destroy nexenta
publisher destroy HighAvailability
sleep 1
echo "Creating new publishers"
publisher create nexenta /media/NS_UpgradeCD/nexenta
publisher create HighAvailability /media/NS_UpgradeCD/rsf
echo "Listing new publishers"
publisher list 
echo
echo "Run '# ./upgradecd.sh restorepublisher' to restore the saved publishers"
sleep 5
echo
echo "Running dry-run software upgrade"
software upgrade -n
echo "Now run '# software upgrade' to perform the upgrade using $isofile"
echo

fi
exit
