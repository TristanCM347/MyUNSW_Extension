#!/usr/bin/python3
# Print a transcript for a given student

import sys
import psycopg2
import re
from MyUNSW_Extension.helpers import getStudent, getMostRecentEnrolement, getTranscriptData, uocOutput, gradeOutput, markOutput, format_string, totalAchievedUocCalc, totalAttemptedUocCalc, weightedMarkSumCalc

# global vairables
usage = f"Usage: {sys.argv[0]} zID"
db = None

# process command-line args
argc = len(sys.argv)
if argc < 2:
  print(usage)
  exit(1)
zid = sys.argv[1]
if zid[0] == 'z':
  zid = zid[1:8]
digits = re.compile("^\d{7}$")
if not digits.match(zid):
  print(f"Invalid student ID {zid}")
  exit(1)

try:
  db = psycopg2.connect("dbname=ass2")
  stuInfo = getStudent(db,zid)
  if not stuInfo:
    print(f"Invalid student ID {zid}")
    exit(1)
  
  print(f"{stuInfo[1]} {stuInfo[2]}, {stuInfo[3]}")
  
  # The program and stream should be the ones most recently enrolled by the student.
  enrolementInfo = getMostRecentEnrolement(db,zid)
  print(f"{enrolementInfo[0]} {enrolementInfo[1]} {enrolementInfo[2]}")

  # loop thoruhg all the courses for each term
  transcriptInfo = getTranscriptData(db,zid)

  total_achieved_uoc = 0
  total_attempted_uoc = 0
  weighted_mark_sum = 0

  for subject in transcriptInfo:
    course_code, term, subject_title, mark, grade, uoc = subject
    print(f"{course_code} {term} {format_string(subject_title)} {markOutput(grade, mark):>3} {gradeOutput(grade):>2s}  {uocOutput(grade, uoc)}")
    
    total_achieved_uoc += totalAchievedUocCalc(grade, uoc)
    total_attempted_uoc += totalAttemptedUocCalc(grade, uoc, mark)
    weighted_mark_sum += weightedMarkSumCalc(grade, mark, uoc)

  print(f"UOC = {total_achieved_uoc}, WAM = {(weighted_mark_sum/total_attempted_uoc):.1f}")

except Exception as err:
  print("DB error: ", err)
finally:
  if db:
    db.close()
