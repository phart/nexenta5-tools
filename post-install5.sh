#!/bin/bash
#
# post-install5.sh
#
# NexentaStor post installation script.  Applicable bits ported to 5.X
#
# Copyright (C) 2016,2018  Nexenta Systems
# William Kettler <william.kettler@nexenta.com>
# Pete Hartman <pete.hartman@nexenta.com>
#
# 2016-06-30 - Initial commit
# 2016-07-17 - Spelling fixes
# 2018-11-12 - change for 5.X specific tasks (ipadm is common between the two)
#

#
# checkpoint first
#
echo "saving system checkpoint..."
software list | grep 'before-post-install-script' > /dev/null 
CHECK=$?
if [ $CHECK -eq 1 ]; then
    software checkpoint before-post-install-script
    echo "checkpoint done..."
else
    echo 'checkpoint already exists, exiting....  verify that changes aren\'t already made'
    exit 1
fi

#
# Enable NMI
#
echo "Enabling NMI..."
echo "" >> /etc/system
echo "* Enable NMI" >> /etc/system
echo "* `date`" >> /etc/system
echo "set snooping=1" >> /etc/system
echo "set pcplusmp:apic_panic_on_nmi=1" >> /etc/system
echo "set apix:apic_panic_on_nmi = 1" >> /etc/system

#
# add tunables for 10G networking; /etc/system as previous does not work
#
echo "setting 10G tunables..."

ipadm set-prop -p send_buf=1048576 tcp
ipadm set-prop -p recv_buf=1048576 tcp
ipadm set-prop -p max_buf=16777216 tcp
ipadm set-prop -p _wscale_always=1 tcp
ipadm set-prop -p _tstamp_if_wscale=1 tcp
ipadm set-prop -p _cwnd_max=8388608 tcp

ipadm set-prop -p _conn_req_max_q0=10000 tcp
ipadm set-prop -p _conn_req_max_q=10000 tcp

#
# make sure apple extensions are set up correctly
#
echo "Adjusting Apple Extensions..."
echo "" >> /etc/system
echo "* Adjust Apple Extensions" >> /etc/system
echo "* `date`" >> /etc/system
echo "set smbsrv:smb2_aapl_extensions=1" >> /etc/system
echo "set smbsrv:smb2_aapl_server_caps=1" >> /etc/system

#
# adjust NFS buffer sizes
#
echo "adjusting NFS buffer sizes..."
echo "" >> /etc/system
echo "* Adjust NFS Buffer Sizes" >> /etc/system
echo "* `date`" >> /etc/system
echo "set nfs:nfs3_bsize = 131072" >> /etc/system
echo "set nfs:nfs4_bsize = 131072" >> /etc/system

#
# set scan_direct
# for NEW DEPLOYMENTS this should not be necessary
# but will keep it here commented out so we know about its relevance
# normally this is set in /etc/system.d/zfs
#
#echo "setting zfs_scan_direct"
#echo "" >> /etc/system
#echo "* set zfs_scan_direct" >> /etc/system
#echo "* `date`" >> /etc/system
#echo "set zfs:zfs_scan_direct = 1" >> /etc/system

#
# stop letting mouse move the cursor
#
echo "unlinking vi from the mouse"
echo "set mouse=r" >> /root/.vimrc
