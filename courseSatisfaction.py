#!/usr/bin/python3
# Track satisfaction in a given subject

import sys
import psycopg2
import re
from MyUNSW_Extension.helpers import getSubject

#helper functions
def getCourseSatisfactionInfo(db, TermCode, subject):
  cursor = db.cursor()
  query = """
    SELECT
              c.satisfact AS Satisfaction,
              c.nresponses AS Responses,
              COUNT(DISTINCT ce.student) AS Students,
              p.full_name AS Convenor
    FROM      Subjects subjects
    JOIN      Courses c ON c.subject = subjects.id
    JOIN      Terms t ON t.id = c.term
    LEFT JOIN Course_enrolments ce ON ce.course = c.id
    JOIN      Staff staff ON c.convenor = staff.id
    JOIN      People p ON p.id = staff.id
    WHERE     t.code = %s AND subjects.code = %s
    GROUP BY  c.satisfact, c.nresponses, p.full_name
    """
  cursor.execute(query, (TermCode, subject))
  info = cursor.fetchone()
  cursor.close()
  if not info:
    return None
  else:
    return info

#global varibales
usage = f"Usage: {sys.argv[0]} SubjectCode"
db = None

#process command-line args
argc = len(sys.argv)
if argc < 2:
  print(usage)
  exit(1)
subject = sys.argv[1]
check = re.compile("^[A-Z]{4}[0-9]{4}$")
if not check.match(subject):
  print("Invalid subject code")
  exit(1)

try:
  db = psycopg2.connect("dbname=ass2")

  subjectInfo, = getSubject(db, subject)
  
  # check if subject exists and returns its info
  if not subjectInfo:
    print(f"Invalid subject code {subject}")
    exit(1)
  print(f"{subject} {subjectInfo}")

  # header
  print("Term  Satis  #resp   #stu  Convenor")

  terms = [f"{year}T{term}" for year in range(19, 24) for term in range(4) if not (year == 19 and term == 0)]

  for TermCode in terms:
    courseSatisfactionInfo = getCourseSatisfactionInfo(db, TermCode, subject)
    # If a course wasn't offered in a particular term, don't print any line for that term.
    if not courseSatisfactionInfo:
      continue
    
    Satisfaction, Responses, Students, Convenor = courseSatisfactionInfo
    # If any of the attributes have a NULL value, use a "?" instead of the number or convenor name (and in this case you will need to use a different format string).
    Satisfaction_str = "     ?" if Satisfaction is None else f"{Satisfaction:6d}"
    Responses_str = "     ?" if Responses is None else f"{Responses:6d}"
    Students_str = "     ?" if Students is None else f"{Students:6d}"
    Convenor_str = "?" if Convenor is None else Convenor

    print(f"{TermCode} {Satisfaction_str} {Responses_str} {Students_str} {Convenor_str}")

except Exception as err:
  print(err)
finally:
  if db:
    db.close()
