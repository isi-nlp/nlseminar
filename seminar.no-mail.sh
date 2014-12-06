#!/bin/sh

# Set working, storage, and seminar-data directories
SEMINAR_HOME=/nfs/isd/aderi/nlseminar
SEMINAR_LIVE=/nfs/web/htdocs/division3/natural-language/nl-seminar
BACKUP=$SEMINAR_HOME/backup
DATA=$SEMINAR_HOME/data

# Set output filenames
WEBSITE=$SEMINAR_HOME/index.php
CALENDAR=$SEMINAR_HOME/nl.ics

# BACKUP
cp $SEMINAR_HOME/index.php $SEMINAR_HOME/nl.ics $BACKUP

# GENERATE DATE
python $SEMINAR_HOME/seminar.py --data $DATA \
                                        --website $WEBSITE \
                                        --ical $CALENDAR \
                                        --nomail

# COPY TO LIVE LOCATION
cp $WEBSITE $CALENDAR $SEMINAR_LIVE/
