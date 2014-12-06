#!/usr/bin/env python

import sys
from distutils.core import setup
from googlecalsync import __version__

setup(name='googlecalendarsync',
      version=__version__,
      description="Google Calendar Synchronizer",
      long_description="""\
googlecalendarsync is a tool written in python to bidirectional synchronize a
local iCal (.ics) file with Google Calendar
""",
      author="Andrea Righi",
      author_email="righiandr@users.sf.net",
      url='http://googlecalendarsync.googlecode.com',
      license='GPL',
      platforms='Any',
      scripts=['googlecalsync.py'],
      packages=None
      )
