#!/usr/bin/env python
# seminar.py
# riesa@isi.edu (Jason Riesa)
#
# This script reads seminar data, and updates the NL Seminar website and iCal
# calendar file based on that data. Depending on the current date and time,
# it will also send email announcing upcoming seminars (see announceByEmail).
#
# It is currently set to send announcements the day of, 5 days before, and 7
# days before any scheduled seminar date. This is a natural schedule for a
# Friday seminar, since announcements will go out on Fridays and Mondays.
#
# Based on the Haskell program by Hal Daume III

import commands
import datetime
import gflags
import os
import sys
import tempfile

# Set global variable to access commandline flag arguments.
FLAGS = gflags.FLAGS

class Seminar(object):
  """ A Seminar object. We store data related to individual seminar events here.
  """
  def __init__(self):
    # Date will be a date time object.
    # Set it by calling Seminar.setDate(YYYY, MM, DD)
    self.date = None
    self.title = None
    self.abstract = ""
    self.start_time = None
    self.end_time = None
    self.location = None
    self.speaker = None
    # Reserved for extra annotation info.
    # Currently used to mark multiple same-day talks.
    self.extra = None

    self.start_hour = None
    self.end_hour = None
    self.start_min = None
    self.end_min = None

  def getAbstract(self):
    return self.abstract

  def getAbstractId(self):
    id = "abs" + self.date.strftime("%d_%b_%Y")
    if self.extra is not None:
      id += self.extra
    return id

  def getDate(self):
    return self.date.strftime("%d %b %Y")

  def getIcalString(self):
    """ Return an this event in ical format encoded as a single string. """
    end_string = (self.date.strftime("%Y%m%d") +
                 "T" + self.end_hour + self.end_min + "00")
    start_string = (self.date.strftime("%Y%m%d") +
                   "T" + self.start_hour + self.start_min + "00")

    ical = "BEGIN:VEVENT\n"
    ical += ("DESCRIPTION: " +
            self.getAbstract().replace("<p>", "\n").replace("\n", "").strip() +
            "\n\n")
    ical += "DTEND;TZID=America/Los_Angeles:" + end_string + "\n"
    ical += "DTSTART;TZID=America/Los_Angeles:" + start_string + "\n"
    ical += "LOCATION:" + self.getLocation() + "\n"
    ical += "SUMMARY:" + self.getTitle() + "\n"
    ical += "UID:" + start_string + "@NL\n"
    ical += "URL:http://www.isi.edu/natural-language/nl-seminar\n"
    ical += "END:VEVENT\n"

    return ical

  def getInfo(self):
    info = ""
    for key, value in self.__dict__.iteritems():
      info += "%s: %s\n" %( key, str(value))
    return info

  def getLocation(self):
    return self.location

  def getSpeaker(self):
    return self.speaker

  def getTime(self):
    return self.start_time + " - " + self.end_time

  def getTitle(self):
    return self.title

  def setDate(self, year, month, day):
    """ Create a new datetime date object from string representation of
    year, month, and day. """
    # We only get a 2-digit year from our data file names. Prepend the century.
    if year < 100:
      year += 2000
    try:
      self.date = datetime.date(year, month, day)
    except:
      sys.stderr.write("Error setting date with: year=%d, month=%d, day=%d\n"
                       % (year, month, day))

  def setEndTime(self, time_str):
    """ Set end time as self.start_date and self.end_date"""
    t, ampm = time_str.split()
    hour, min = t.split(":")
    if ampm == "pm" and hour != "12":
      hour = str(int(hour)+12)
    self.end_hour = hour
    self.end_min = min

  def setStartTime(self, time_str):
    """ Set start time as self.start_date and self.end_date"""
    t, ampm = time_str.split(" ")
    hour, min = t.split(":")
    if ampm == "pm" and hour != "12":
      hour = str(int(hour)+12)
    self.start_hour = hour
    self.start_min = min

def announceByEmail(today_talks, upcoming_talks):
  for talk in today_talks + upcoming_talks:
    subject = "NL Seminar " + talk.getDate() + " - " + talk.getTitle()
    # Special subject if talk is today.
    if talk.date == datetime.date.today():
      subject = "Reminder: TODAY! - " + talk.getTitle()

    """
    # Old policy: Send email announcement the day of, 4 days before, and 7 days before.
    if (talk.date - datetime.date.today() == datetime.timedelta(0) or
        talk.date - datetime.date.today() == datetime.timedelta(4) or
        talk.date - datetime.date.today() == datetime.timedelta(7)):
    """
    # New policy: Send email announcement the day of, 7 days before, and the Monday of.
    if (talk.date - datetime.date.today() == datetime.timedelta(0) or
        talk.date - datetime.date.today() == datetime.timedelta(7) or
        (datetime.date.today().weekday() == 0 and talk.date - datetime.date.today() < datetime.timedelta(7))):
      body = "*********** " + FLAGS.seminar_name + " Announcement ***********\n\n"
      body += " Speaker: " + talk.getSpeaker() + "\n"
      body += "    Date: " + talk.getDate() + "\n"
      body += "    Time: " + talk.start_time + " - " + talk.end_time + "\n"
      body += "Location: " + talk.getLocation() + "\n"
      body += "\n"
      body += ("    Note: Outside visitors should go to the tenth floor lobby where\n"
             + "          they will be met and escorted to the appropriate location\n"
             + "          five minutes before the talk.\n\n")
      body += "   Title: " + talk.getTitle() + "\n"
      body += "\n"
      body += "Abstract:\n\n"
      body += talk.getAbstract().replace("<p>", "") + "\n"
      body += "\n"
      body += "***********************************************\n\n"
      body += "Remember, future seminars can be found at:\n"
      body += "  " + FLAGS.public_url + "\n"

      sender_name_str = " ".join(FLAGS.sender_name)
      recipients_str = ", ".join(FLAGS.recipient)
      email = "From: " + sender_name_str + " "
      email += "<" + FLAGS.sender_email + ">\n"
      email += "To: " + recipients_str + "\n"
      email += "Subject: " + subject + "\n"
      email += "\n"
      email += body

      # Send the mail
      tmp_email_file = open("announce.eml", 'w')
      tmp_email_file.write(email)
      tmp_email_file.close()
      commands.getstatusoutput(FLAGS.mailer+" -t < announce.eml")

def findEarliestTalk(talks):
  """ Remove earliest talk from a list of talks. Return that talk."""
  earliest_talk = talks[0]
  earliest_talk_date = talks[0].date
  for talk in talks:
    if talk.date <= earliest_talk_date:
      earliest_talk = talk
      earliest_talk_date = talk.date

  talks.remove(earliest_talk)
  return earliest_talk

def findLatestTalk(talks):
  """ Remove earliest talk from a list of talks. Return that talk."""
  latest_talk = talks[0]
  latest_talk_date = talks[0].date
  for talk in talks:
    if talk.date >= latest_talk_date:
      latest_talk = talk
      latest_talk_date = talk.date
  talks.remove(latest_talk)
  return latest_talk

def readSeminarData(today_talks, upcoming_talks, past_talks):
  """ For each file in the data directory, parse and assign data to a
  seminar object """
  today = datetime.date.today()
  months_str_to_int = {"Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5, "Jun":6,
                       "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}

  for file in os.listdir(FLAGS.data):

    if file[0] == "." or file[-1] == "~":
      # Ignore special swap and emacs files.
      if FLAGS.debug:
        sys.stderr.write("Ignoring special file: "+file)
      continue
    try:
      year, month, day = file.split("_")
    except:
       # Ignore anything else we can't parse or recognize, but return a warning.
       sys.stderr.write("Error parsing filename: "+file+"\n")
       sys.stderr.write("Format is YY_MMM_DD, e.g.: for a talk on ")
       sys.stderr.write("October 4, 2011, use: 11_Oct_04\n")
       continue
    talk = Seminar()
    # If there is more than one talk today, we append a letter to the filename
    # e.g. We might have 11_Oct_04 and 11_Oct_04b
    # Remove and record the letter here.
    try:
      int(day[-1])
    except:
      talk.extra = day[-1]
      day = day[:-1]

    talk.setDate(int(year), months_str_to_int[month], int(day))
    parseDataFile(file, talk)

    zero_delta = datetime.timedelta(0)

    if talk.date - today == zero_delta:
      if FLAGS.debug:
        sys.stderr.write("Talk is TODAY!\n")
      today_talks.append(talk)
    elif talk.date - today > zero_delta:
      if FLAGS.debug:
        sys.stderr.write("Upcoming talk.\n")
      upcoming_talks.append(talk)
    elif talk.date - today < zero_delta:
      if FLAGS.debug:
        sys.stderr.write("Past talk.\n")
      past_talks.append(talk)
    else:
      sys.stderr.write("Error reading date for seminar file: "+file)


def parseDataFile(filename, talk):
  """ Parse a seminar data file.
  Format is:

  SPEAKER     # Line 1
  TITLE       # Line 2
  START_TIME - END_TIME   # Line 3
  LOCATION    # Line 4
  EMPTY LINE  # Line 5
  ABSTRACT    # Rest of lines in data file make up the abstract.
              # Replace blank lines with <p>\n

  """
  f = open(FLAGS.data+"/"+filename, 'r')
  for line_number, line in enumerate(f):
    line = line.strip()
    if FLAGS.debug:
      sys.stderr.write("Reading line [%d]: <<%s>>\n" %(line_number, line))
    parse_error = False
    if line_number == 0:
      # Author line
      if line != "":
        talk.speaker = line
      else:
        parse_error = True
    elif line_number == 1:
      if line != "":
        talk.title = line
      else:
        parse_error = True
    elif line_number == 2:
      if line != "":
        start_time, end_time = line.split(" - ")
        if len(start_time) <= 0 or len(end_time) <= 0:
          parse_error = True
        talk.start_time = start_time
        talk.end_time = end_time
        talk.setStartTime(talk.start_time)
        talk.setEndTime(talk.end_time)
      else:
        parse_error = True
    elif line_number == 3:
      if line != "":
        talk.location = line
      else:
        parse_error = True
    elif line_number == 4:
      continue
    else: # Line number > 4
      if line == "":
        line = "<p>"
      talk.abstract += (line + "\n")

    if parse_error:
      sys.stderr.write("FATAL: " +
                       "Unable to parse data file: "+filename+"\n")
      sys.stderr.write(talk.getInfo())
      sys.exit(1)

def writeSeminarToWebsite(f, talk):
  # Div id name has format abs[YY_MMM_DD]
  # For example, abs11_Oct_04
  div_id_name = talk.getAbstractId()
  seminar = []
  seminar.append("<tr class=\"speakerItem\" border=0 >")
  # Seminar date
  seminar.append("<td align=left valign=top>" + talk.getDate() + "</td>")
  # Seminar speaker
  seminar.append("<td align=left valign=top>" + talk.getSpeaker() +"</td>")
  # Seminar title, time, location and abstract
  seminar.append("<td align=left valign=top>")
  seminar.append("<a onMouseOver=\"window.status='View abstract'; " +
                 "return true\" onMouseOut=\"window.status=' '; " +
                 "return true\" href=\"javascript:exp_coll('" + div_id_name +
                 "');\">")
  seminar.append(talk.getTitle())
  seminar.append("</a><br>")
  seminar.append("<span id="+div_id_name+" style=\"display:none;\">")
  seminar.append("<font size=-1>")
  seminar.append("<b>Time:</b> " + talk.getTime() + "<br>")
  seminar.append("<b>Location:</b> " + talk.getLocation() + "<br>")
  seminar.append("<b>Abstract:</b> " + talk.getAbstract() + "<br>")
  seminar.append("</font>")
  seminar.append("</span>")
  seminar.append("</td></tr>")
  f.write("\n".join(seminar))

def writeWebsiteEpilogue(f):
  """ Write a timestamp and closing HTML tags. """
  # Compute human-readable date string
  # In the format of: Mon Oct 3 11:29:26 PDT 2011
  now = datetime.datetime.now()
  date_string = now.strftime("%a %b %d %H:%M:%S %Y")
  lines = []
  lines.append("<div align=\"center\">" +
               "<font face=\"Verdana, Arial, Helvetica, sans-serif\" "+
               "size=\"1\">")
  lines.append("This web page was last generated on " + date_string + ".<br>")
  lines.append("</font></div>")
  lines.append("</body></html>")
  f.write("\n".join(lines)+"\n")

def writeWebsiteHeader(f):
  """ Write invariant header portion to file f """
  header = []
  header.append("<html>")
  header.append("<head>")
  header.append("<meta http-equiv=\"Content-Type\" content=\"text/html; " +
                "charset=UTF-8\" />")
  header.append("<link rel=\"stylesheet\" " +
                "type=\"text/css\" href=\"css/NLGSite.css\" /> " +
                "<style type=\"text/css\">")
  header.append("<!--")
  header.append("  A:link    { text-decoration: none; color: #000099}")
  header.append("  A:active  { text-decoration: none; color: #000099}")
  header.append("  A:visited { text-decoration: none; color: #000099}")
  header.append("  A:hover   { text-decoration: underline; color: #990099}")
  header.append("//-->")
  header.append("</style>")
  header.append("")
  header.append("<script type=\"text/javascript\">")
  header.append("<!--")
  header.append("function exp_coll(ind) {")
  header.append("  s = document.getElementById(ind);")
  header.append("")
  header.append("  if (s.style.display == 'none') {")
  header.append("    s.style.display = 'block';")
  header.append("  } else if (s.style.display == 'block') {")
  header.append("    s.style.display = 'none';")
  header.append("  }")
  header.append("}")
  header.append("-->")
  header.append("</script>")
  header.append("")
  header.append("<title>NL Seminar</title>")
  header.append("")
  header.append("  </head>")
  header.append("<body text=\"#000033\" link=\"#000099\" vlink=\"#000099\"" +
                " alink=\"#000099\">")
  header.append("<?php include('includes/usc-header.php'); ?>" +
                "<br><center><h2><b>USC/ISI NL Seminar</b></h2></center>")
  header.append("<?php include('includes/about.php'); ?>")

  f.writelines("\n".join(header))

def writePastTalks(f, past_talks):
  """ Write past talks to website """
  # Set up past talks table
  lines = []
  lines.append(" <div class=\"nlheader\"><h3>Past talks:</h3></div>")

  lines.append("<table width=90% border=0 cellspacing=1 cellpadding=4 " +
               "bgcolor=\"#FFFFFF\" align=center>")
  lines.append("<tr class=\"seminarTableHeader\"><td align=left width=14%>")
  lines.append("  <b>Date</b>")
  lines.append("</td><td align=left width=25%>")
  lines.append("    <b>Speaker</b>")
  lines.append("  </td><td align=left>")
  lines.append("    <b>Title</b>")
  lines.append("  </td></tr>")
  f.write("\n".join(lines)+"\n")
  # Write talks
  while(len(past_talks) > 0):
    talk = findLatestTalk(past_talks)
    writeSeminarToWebsite(f, talk)

  # Write ending for past talks table
  f.write("</table><br><br>\n")

def writeTodayTalks(f, today_talks):
  """ Write talks happening today. """
  # Set up  upcoming talks table
  lines = []
  lines.append("  <div class=\"nlheader\"><h2><b>Today:</b></h2></div>")
  lines.append("<table width=90% border=0 cellspacing=1 cellpadding=4 " +
                "bgcolor=\"#FFFFFF\" align=center>")
  lines.append("<tr class=\"seminarTableHeader\"><td align=left width=14%>")
  # Main three headings
  lines.append("    <b>Date</b>")
  lines.append("  </td><td align=left width=25%>")
  lines.append("    <b>Speaker</b>")
  lines.append("  </td><td align=left>")
  lines.append("    <b>Title</b>")
  lines.append("  </td></tr>")
  f.write("\n".join(lines)+"\n")

  # Write talks
  while(len(today_talks) > 0):
    talk = findEarliestTalk(today_talks)
    writeSeminarToWebsite(f, talk)

  # Write ending for upcoming talks table
  f.write("</table><br><br>\n")

def writeUpcomingTalks(f, upcoming_talks):
  """ Write upcoming talks to website"""
  # Set up  upcoming talks table
  lines = []
  lines.append("  <div class=\"nlheader\"><h3>Upcoming talks:</h3></div>")
  lines.append("<table width=90% border=0 cellspacing=1 cellpadding=4 " +
                "bgcolor=\"#FFFFFF\" align=center>")
  lines.append("<tr class=\"seminarTableHeader\"><td align=left width=14%>")
  # Main three headings
  lines.append("    <b>Date</b>")
  lines.append("  </td><td align=left width=25%>")
  lines.append("    <b>Speaker</b>")
  lines.append("  </td><td align=left>")
  lines.append("    <b>Title</b>")
  lines.append("  </td></tr>")
  f.write("\n".join(lines)+"\n")

  # Write talks
  while(len(upcoming_talks) > 0):
    talk = findEarliestTalk(upcoming_talks)
    writeSeminarToWebsite(f, talk)

  # Write ending for upcoming talks table
  f.write("</table><br><br>\n")


def writeTalks(f, today_talks, upcoming_talks, past_talks):
  """ Write talk items to website if necessary."""

  if len(today_talks) > 0:
    writeTodayTalks(f, list(today_talks))

  if len(upcoming_talks) > 0:
    writeUpcomingTalks(f, list(upcoming_talks))

  if len(past_talks) > 0:
    writePastTalks(f, list(past_talks))

def getTimeZone():
  return "BEGIN:VTIMEZONE\n" + \
  "TZID:America/Los_Angeles\n" + \
  "X-LIC-LOCATION:America/Los_Angeles\n" + \
  "BEGIN:DAYLIGHT\n" + \
  "TZOFFSETFROM:-0800\n" + \
  "TZOFFSETTO:-0700\n" + \
  "TZNAME:PDT\n" + \
  "DTSTART:19700308T020000\n" + \
  "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU\n" + \
  "END:DAYLIGHT\n" + \
  "BEGIN:STANDARD\n" + \
  "TZOFFSETFROM:-0700\n" + \
  "TZOFFSETTO:-0800\n" + \
  "TZNAME:PST\n" + \
  "DTSTART:19701101T020000\n" + \
  "RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU\n" + \
  "END:STANDARD\n" + \
  "END:VTIMEZONE\n"

def writeIcal(f, today_talks, upcoming_talks, past_talks):
  """ Write talks to ical format """
  # Header info
  f.write("BEGIN:VCALENDAR\n")
  f.write("CALSTYLE:GREGORIAN\n")
  f.write("PRODID:-//NL//Seminar Calendar//EN\n")
  f.write("VERSION:2.0\n")
  f.write("X-WR-CALNAME:NL\n")
  # f.write("X-WR-TIMEZONE:America/Los_Angeles\n")
  f.write(getTimeZone())


  for talk in today_talks + upcoming_talks + past_talks:
    f.write(talk.getIcalString())

  # Epilogue
  f.write("END:VCALENDAR\n")

def writeWebsite(f, today_talks, upcoming_talks, past_talks):

  writeWebsiteHeader(f)
  writeTalks(f, today_talks, upcoming_talks, past_talks)
  writeWebsiteEpilogue(f)

if __name__ == '__main__':
  gflags.DEFINE_string("mailer", "/usr/sbin/sendmail", "Path to mail program")
  gflags.DEFINE_string("data",
                       "/nfs/amber/riesa/nl-seminar/data",
                       "Path to NL Seminar data files")
  gflags.DEFINE_string("website", None, "Path to website file")
  gflags.DEFINE_string("ical", None, "Path to ical file.")
  gflags.DEFINE_boolean("debug", False, "Print verbose debugging messages.")
  gflags.DEFINE_string("seminar_name", "NL Seminar", "Name of Seminar")
  gflags.DEFINE_boolean("mail", True, "Send broadcast mail for upcoming seminars")
  gflags.DEFINE_spaceseplist("sender_name", "NL Seminar", "Name of the organizer of this seminar.")
  gflags.DEFINE_string("sender_email", "nlseminar@isi.edu", "E-mail of the organizer of this seminar.")
  gflags.DEFINE_multistring("recipient", "nlg-seminar@isi.edu", "Recipient of announcements of this semianr. Usually a mailing list.")
  gflags.DEFINE_string("public_url", "http://www.isi.edu/natural-language/nl-seminar/", "URL to include at bottom of announcements")
  argv = FLAGS(sys.argv)

  if FLAGS.website is None or FLAGS.ical is None:
    sys.stderr.write("SYNTAX: %s --data DATA "
                     "--website WEBSITE --ical ICAL --mailer MAILER" %(argv[0]))
    sys.exit(1)

  # Parse data and write website and ical
  today_talks = []
  upcoming_talks = []
  past_talks = []
  readSeminarData(today_talks, upcoming_talks, past_talks)
  site_filehandle = open(FLAGS.website, 'w')
  ical_filehandle = open(FLAGS.ical, 'w')

  writeWebsite(site_filehandle, today_talks, upcoming_talks, past_talks)
  writeIcal(ical_filehandle, today_talks, upcoming_talks, past_talks)

  site_filehandle.close()
  ical_filehandle.close()

  if FLAGS.mail:
    announceByEmail(today_talks, upcoming_talks)
