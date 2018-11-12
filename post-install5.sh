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

#
# make sure apple extensions are set up correctly
#
echo "Adjusting Apple Extensions..."
echo "" >> /etc/system
echo "* Adjust Apple Extensions" >> /etc/system
echo "* `date`" >> /etc/system
echo "set smbsrv:smb2_aapl_extensions=1" >> /etc/system
echo "set smbsrv:smb2_aapl_server_caps=1" >> /etc/system
