#!/usr/bin/python3
# Print list of rules for a program or stream

import sys
import psycopg2
import re
from MyUNSW_Extension.helpers import getProgram, getStream, getSubject, minMaxOutput, getCoreRequirements, getElectiveRequirements

#helper functions
def streamRules(db, code):
  #UOC
  requirements = getUOCRequirementsStream(db, code)
  printUOCRequirements(db, requirements)

  #stream (since its a stream there wont be any streams im assuming)

  # core
  requirements = getCoreRequirements(db, code, "for_stream")
  printCoreRequirements(db, requirements)

  # elective
  requirements = getElectiveRequirements(db, code, "for_stream")
  printElectiveRequirements(db, requirements)

  # gened
  requirements = getGenEdRequirements(db, code, "for_stream")
  printGenEdRequirements(db, requirements)

  # free
  requirements = getFreeRequirements(db, code, "for_stream")
  printFreeRequirements(db, requirements)
  
def programRules(db, code):
  #UOC
  requirements = getUOCRequirementsProgram(db, code)
  printUOCRequirements(db, requirements)

  #stream
  requirements = getStreamRequirementsProgram(db, code)
  printStreamRequirements(db, requirements)

  # core
  requirements = getCoreRequirements(db, code, "for_program")
  printCoreRequirements(db, requirements)

  # elective
  requirements = getElectiveRequirements(db, code, "for_program")
  printElectiveRequirements(db, requirements)

  # gened
  requirements = getGenEdRequirements(db, code, "for_program")
  printGenEdRequirements(db, requirements)
  
  # free
  requirements = getFreeRequirements(db, code, "for_program")
  printFreeRequirements(db, requirements)

def printGenEdRequirements(db, requirements):
  if requirements is None:
    return
  for requirement in requirements:
    min, max, name = requirement
    minMaxOutput(min, max)
    print(f"UOC of {name}")

def getGenEdRequirements(db, code, typeFor):
  if typeFor == "for_program":
    tableName = "Programs"
  elif typeFor == "for_stream":
    tableName = "Streams"
  query = f"""
    SELECT    r.min_req AS min,
              r.max_req AS max,
              r.name AS name
    FROM      Requirements r
    JOIN      {tableName} x ON x.id = r.{typeFor}
    WHERE     x.code = %s AND r.rtype = 'gened'
    ORDER BY  r.id
    """
  cursor = db.cursor()
  cursor.execute(query, (code,))
  info = cursor.fetchall()
  cursor.close()
  if not info:
    return None
  else:
    return info

def printFreeRequirements(db, requirements):
  if requirements is None:
    return
  for requirement in requirements:
    min, max, name = requirement
    minMaxOutput(min, max)
    print(f"UOC of {name}")

def getFreeRequirements(db, code, typeFor):
  if typeFor == "for_program":
    tableName = "Programs"
  elif typeFor == "for_stream":
    tableName = "Streams"
  query = f"""
    SELECT    r.min_req AS min,
              r.max_req AS max,
              r.name AS name
    FROM      Requirements r
    JOIN      {tableName} x ON x.id = r.{typeFor}
    WHERE     x.code = %s AND r.rtype = 'free'
    ORDER BY  r.id
    """
  cursor = db.cursor()
  cursor.execute(query, (code,))
  info = cursor.fetchall()
  cursor.close()
  if not info:
    return None
  else:
    return info

def printElectiveRequirements(db, requirements):
  if requirements is None:
    return
  for requirement in requirements:
    min, max, courses, name = requirement
    minMaxOutput(min, max)
    print(f"UOC courses from {name}")
    print(f"- {courses}")

def printCoreRequirements(db, requirements):
  if requirements is None:
    return
  for requirement in requirements:
    courses, name = requirement
    courses_list = courses.split(',')
    print(f"all courses from {name}")
    
    for subject in courses_list:
      if subject.startswith("{") and subject.endswith("}"):
        subject = subject[1:-1]
        multiple_subjects = subject.split(';')
        first_choice = True
        
        for subject1 in multiple_subjects:
          subjectInfo, = getSubject(db, subject1)
          if first_choice == True:
            print(f"- {subject1} {subjectInfo}")
            first_choice = False
          else:
            print(f"  or {subject1} {subjectInfo}")

      else:
        subjectInfo, = getSubject(db, subject)
        print(f"- {subject} {subjectInfo}")

def getStreamRequirementsProgram(db, code):
  query = """
    SELECT    r.min_req AS min,
              r.max_req AS max,
              r.name AS name,
              r.acadobjs AS streams
    FROM      Requirements r
    JOIN      Programs p ON p.id = r.for_program
    WHERE     p.code = %s AND r.rtype = 'stream'
    ORDER BY  r.id
    """
  cursor = db.cursor()
  cursor.execute(query, (code,))
  info = cursor.fetchall()
  cursor.close()
  if not info:
    return None
  else:
    return info

def printStreamRequirements(db, requirements):
  if requirements is None:
    return
  for requirement in requirements:
    min, max, name, streams = requirement
    streams_list = streams.split(',')
    minMaxOutput(min, max)
    print(f" stream from {name}")
    for code in streams_list:
      stream = getStream(db, code)
      print(f"- {code} {stream[2]}")

def printUOCRequirements(db, requirements):
  if requirements is None:
    return
  for requirement in requirements:
    print("Total UOC ", end='')
    min, max = requirement
    minMaxOutput(min, max)
    print(" UOC")

def getUOCRequirementsStream(db, code):
  query = """
    SELECT    r.min_req AS min,
              r.max_req AS max
    FROM      Requirements r
    JOIN      Streams s ON s.id = r.for_stream
    WHERE     s.code = %s AND r.rtype = 'uoc'
    ORDER BY  r.id
    """
  cursor = db.cursor()
  cursor.execute(query, (code,))
  info = cursor.fetchall()
  cursor.close()
  if not info:
    return None
  else:
    return info

def getUOCRequirementsProgram(db, code):
  query = """
    SELECT    r.min_req AS min,
              r.max_req AS max
    FROM      Requirements r
    JOIN      Programs p ON p.id = r.for_program
    WHERE     p.code = %s AND r.rtype = 'uoc'
    ORDER BY  r.id
    """
  cursor = db.cursor()
  cursor.execute(query, (code,))
  info = cursor.fetchall()
  cursor.close()
  if not info:
    return None
  else:
    return info

# global vairables
usage = f"Usage: {sys.argv[0]} (ProgramCode|StreamCode)"
db = None

# process command-line args
argc = len(sys.argv)
if argc < 2:
  print(usage)
  exit(1)
code = sys.argv[1]
if len(code) == 4:
  codeOf = "program"
elif len(code) == 6:
  codeOf = "stream"
else:
  print("Invalid code")
  exit(1)

try:
  db = psycopg2.connect("dbname=ass2")
  if codeOf == "program":
    progInfo = getProgram(db,code)
    if not progInfo:
      print(f"Invalid program code {code}")
      exit(1)
    
    print(f"{code} {progInfo[2]}")
    print("Academic Requirements:")
    programRules(db,code)

  elif codeOf == "stream":
    strmInfo = getStream(db,code)
    if not strmInfo:
      print(f"Invalid stream code {code}")
      exit(1)

    print(f"{code} {strmInfo[2]}")
    print("Academic Requirements:")
    streamRules(db,code)

except Exception as err:
  print(err)
finally:
  if db:
    db.close()
