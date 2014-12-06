#!/bin/sh

# Add backup and data subdirectories to
# the current working directory

if [ ! -d backup ] ; then
 mkdir backup
fi

if [ ! -d data ] ; then
 mkdir data
fi
