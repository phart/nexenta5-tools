#!/usr/bin/python2
#
# script to correct Nexenta-side ACLs so that files do not inherit the execute flag from parent directories
#
import os
import sys
import subprocess
import re


# check argument count
if len(sys.argv) != 2:
    print ("incorrect number of arguments\nusage: fix-perms.py DIRNAME")
    sys.exit(-1)

# grab first (only) argument
dirname = sys.argv[1]

# is it really a directory?
if not (os.path.isdir(dirname) and not os.path.islink(dirname)):
    print ("%s is not a directory" % dirname)
    sys.exit(-1)

# ok, we're good
ls_output = subprocess.check_output(["ls", "-lvd", dirname]).split("\n")
in_acl = False
acl_number = None
owner_acls = {}
for line in ls_output:
    if not in_acl:
        mymatch = re.search("^\s+(\d+):owner@:(.*)$", line)
        if mymatch:
            in_acl = True
            if acl_number != None:
                owner_acls[acl_number] = acl_entry
            acl_number = mymatch.group(1)
            acl_entry = mymatch.group(2)
    else:
        mymatch = re.search("^\s+(/.*)$", line)
        if mymatch:
            acl_entry += mymatch.group(1)
        else:
            mymatch = re.search("^\s+(\d+):owner@:(.*)$", line)
            if mymatch:
                # save previous entire entry
                owner_acls[acl_number] = acl_entry
                # start new match
                acl_number = mymatch.group(1)
                acl_entry = mymatch.group(2)
            else:
                mymatch = re.search("^\s+\d+:", line)
                if mymatch:     # a non-owner@ ACE
                    # save previous entire entry
                    owner_acls[acl_number] = acl_entry
                    in_acl = False
                    acl_number = None
                    acl_entry = None
            # ignore all other entries (e.g. group@ etc)

if acl_number:
    owner_acls[acl_number] = acl_entry

for entry in owner_acls:
    # does it have a file_inherit flag?
    mymatch = re.search("^(.*):file_inherit/?(.*)$", owner_acls[entry])
    if mymatch:
        # print ("A%s:%s" % (entry, owner_acls[entry]))
        # print ("-------------")
        print("executing chmod A%s=owner@:%s:%s %s" % (entry, mymatch.group(1), mymatch.group(2), dirname))
        if subprocess.call(["chmod","A%s=owner@:%s:%s" % (entry, mymatch.group(1), mymatch.group(2)), dirname]) != 0:
            print ("CHMOD FAILED")
            sys.exit(-1)
