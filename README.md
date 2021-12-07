
## 📣 This is an old repository. New website is at https://github.com/isi-nlp/nl-seminar 

------
02 Feb 2012
riesa@isi.edu (Jason Riesa)
modified: Qing Dou (qdou@isi.edu)
		  Yang Gao (yanggao@isi.edu), Jul 26 2013, Apr 11 2014
		  Aliya Deri(aderi@isi.edu), June 4 2014

How to use the ISI Seminar tool
===============================

0. Note: This document assumes you have write access to the ISI NL Seminar webspace.
	/nfs/web/htdocs/division3/natural-language/nl-seminar

	If you don't yet have it (and you probably don't), contact Action.

	It also assumes that you can run the "sendmail" command, if not, install "ssmtp".
	Here is a command to use in ubuntu if you have sudo authority: sudo apt-get install ssmtp

1. Unpack this archive to an accessible location and run setup.sh:
	$ ./setup.sh

	This creates two subdirectories:
	backup/
	data/

2. Change organizer's name and email in:
	/nfs/web/htdocs/division3/natural-language/nl-seminar/includes/about.php 

3. Edit seminar.sh with appropriate pathnames for your setup and environment:
	(a) Set the SEMINAR_HOME variable to the location where you unpacked this archive. # must
	(b) Edit the --sender_name argument with your full name. (Line 24) # must
	(c) Edit the --sender_email argument with your email address. (Line 25) # must

4. Set seminar.sh to run each day at 5am.
	(a) Edit SEMINAR_CRON with the path to your seminar.sh file. # must
	(b) Set a new cronjob for this program: # must type crontab -l to see current jobs, crontab -r will delete jobs
		$ crontab SEMINAR_CRON

5. Varieties of seminar.sh:
	- For sanity check, try sending email to your self by editing and run seminar.self.sh
	- To just update information on website, run seminar.no-mail.sh

6. Create your own meeting schedule on Google Docs, or use an existing one. Example: http://goo.gl/pgSD4j.

7. Misc:
	-in templates/ invitation.txt from Qing Dou and Aliya Deri and thankyou.txt from Peter Zamar
	-remember to commit and push to git, so you're safeguarded against any accidental deletes
	

