#!/usr/bin/python3
# Progression check for a given student

import sys
import psycopg2
import re
from MyUNSW_Extension.helpers import getStudent, getSubjectUoc, getSubject, getProgram, getStream, getMostRecentEnrolement, getTranscriptData, uocOutput, gradeOutput, markOutput, format_string, totalAchievedUocCalc, totalAttemptedUocCalc, weightedMarkSumCalc

#linked list classes
class RequirementNode:
  def __init__(self, rid, for_program, rtype, name, min_req, max_req, acadobjs):
    self.rid = rid
    self.for_program = for_program
    self.rtype = rtype
    self.name = name
    if rtype == "free":
      if min_req is None:
        min_req = max_req
      if max_req is None:
        max_req = min_req
    self.min_req = min_req
    self.max_req = max_req
    self.current_uoc = 0
    self.satisfied = False
    courses_list = acadobjs.split(',')
    self.acadobjs = courses_list
    self.next = None

class LinkedList:
  def __init__(self):
    self.head = None

  def append(self, rid, for_program, rtype, name, min_req, max_req, acadobjs):
    if not self.head:
      self.head = RequirementNode(rid, for_program, rtype, name, min_req, max_req, acadobjs)
      return
    last_node = self.head
    while last_node.next:
      last_node = last_node.next
    last_node.next = RequirementNode(rid, for_program, rtype, name, min_req, max_req, acadobjs)

  def display(self):
    current_node = self.head
    while current_node:
      print(f"Name: {current_node.name}, For_program: {current_node.for_program}, Rtype: {current_node.rtype}, Min: {current_node.min_req}, Max: {current_node.max_req}, Current UOC: {current_node.current_uoc}, Satistfied: {current_node.satisfied}, AcadObjs: {current_node.acadobjs}")
      current_node = current_node.next

  def sort(self):
    # Map rtype to a numeric value for sorting
    rtype_order = {'core': 0, 'elective': 1, 'gened': 2, 'free': 3}

    swapped = True
    while swapped:
      swapped = False
      current = self.head
      prev = None

      while current and current.next:
        next_node = current.next
        # Compare current node with next node
        if (rtype_order.get(current.rtype, 4) > rtype_order.get(next_node.rtype, 4)) or \
          (current.rtype == next_node.rtype and current.for_program and not next_node.for_program) or \
          (current.rtype == next_node.rtype and current.for_program == next_node.for_program and current.rid > next_node.rid):

          # Swap nodes
          if prev:
            prev.next = next_node
          else:
            self.head = next_node
          current.next = next_node.next
          next_node.next = current

          swapped = True
          prev = next_node
        else:
          prev = current
          current = current.next

  def __iter__(self):
    node = self.head
    while node is not None:
      yield node
      node = node.next

# helper functions
def getAllRequirements(progCode, strmCode, allRequirements):
  query = f"""
    SELECT    *
    FROM      Requirements r
    JOIN      Programs p ON p.id = r.for_program
    WHERE     p.code = %s AND r.rtype != 'stream' AND r.rtype != 'uoc'
    """
  cursor = db.cursor()
  cursor.execute(query, (progCode,))
  info = cursor.fetchall()
  for requirement in info:
    rid = requirement[0]
    name = requirement[1]
    rtype = requirement[2]
    min_req = requirement[3]
    max_req = requirement[4]
    acadobjs = requirement[5]
    for_program = True
    allRequirements.append(rid, for_program, rtype, name, min_req, max_req, acadobjs)

  query = f"""
    SELECT    *
    FROM      Requirements r
    JOIN      Streams s ON s.id = r.for_stream
    WHERE     s.code = %s AND r.rtype != 'stream' AND r.rtype != 'uoc'
    """
  cursor.execute(query, (strmCode,))
  info = cursor.fetchall()
  for requirement in info:
    rid = requirement[0]
    name = requirement[1]
    rtype = requirement[2]
    min_req = requirement[3]
    max_req = requirement[4]
    acadobjs = requirement[5]
    for_program = False
    allRequirements.append(rid, for_program, rtype, name, min_req, max_req, acadobjs)
  
  cursor.close()

def hasPattern(code):
  return "#" in code

def satisfiesRequirement(grade):
  valid_grades = {'A', 'B', 'C', 'D', 'A+', 'B+', 'C+', 'D+','A-', 'B-', 'C-', 'D-', 'HD', 'DN', 'CR', 'PS', 'XE', 'T', 'SY', 'EC', 'RC'}
  if grade in valid_grades:
    return True
  return False

def stringsMatchPattern(str1, str2):
  # both strings are same length
  # Iterate through each character
  for char1, char2 in zip(str1, str2):
    if char1 != char2 and char1 != '#' and char2 != '#':
      return False
  return True

def assign_requirements(transcript, assignment_of_reqs, allRequirements):
  index = 0
  for subject in transcript:
    course_code, term, subject_title, mark, grade, uoc = subject
    for requirement_node in allRequirements:
      # check what type of node
      if requirement_node.rtype == "core":
        for s in range(len(requirement_node.acadobjs) - 1, -1, -1):
          course = requirement_node.acadobjs[s]

          if course.startswith("{") and course.endswith("}"):
            course = course[1:-1]
            multiple_courses = course.split(';')
            # loop through mulitple courses

            found = False
            for s1 in range(len(multiple_courses) - 1, -1, -1):
              course1 = multiple_courses[s1]
              if stringsMatchPattern(course_code, course1) and satisfiesRequirement(grade):
                found = True
                break
        
            if found == True:
              del requirement_node.acadobjs[s]
              assignment_of_reqs[index] = requirement_node.name
              break

          elif stringsMatchPattern(course_code, course) and satisfiesRequirement(grade):
              del requirement_node.acadobjs[s]
              assignment_of_reqs[index] = requirement_node.name
              break

        # update if core courses have been fulfilled
        if requirement_node.acadobjs == []:
          requirement_node.satisfied = True

      elif requirement_node.rtype == "elective":
        # loop thoruhg all of the courses
        for s in range(len(requirement_node.acadobjs) - 1, -1, -1):
          course = requirement_node.acadobjs[s]
          if stringsMatchPattern(course_code, course) and satisfiesRequirement(grade):
            # check if course will fulfil requirement or already fulfilled 
            if not isValidAmountOfUoc(requirement_node.min_req, requirement_node.max_req, requirement_node.current_uoc, uoc):
              # we cant use the course
              continue

            if not hasPattern(course):
              del requirement_node.acadobjs[s]
            requirement_node.current_uoc = requirement_node.current_uoc + uoc
            assignment_of_reqs[index] = requirement_node.name
            break
      
      elif requirement_node.rtype == "gened":
        course = "########"
        if stringsMatchPattern(course_code, course) and satisfiesRequirement(grade):
          # check if course will fulfil requirement or already fulfilled 
          if not isValidAmountOfUoc(requirement_node.min_req, requirement_node.max_req, requirement_node.current_uoc, uoc):
            # we cant use the course
            continue

          requirement_node.current_uoc = requirement_node.current_uoc + uoc
          assignment_of_reqs[index] = requirement_node.name
          break
      
      elif requirement_node.rtype == "free":
        course = "########"
        if stringsMatchPattern(course_code, course) and satisfiesRequirement(grade):
          # check if course will fulfil requirement or already fulfilled 
          if not isValidAmountOfUoc(requirement_node.min_req, requirement_node.max_req, requirement_node.current_uoc, uoc):
            # we cant use the course
            continue

          requirement_node.current_uoc = requirement_node.current_uoc + uoc
          assignment_of_reqs[index] = requirement_node.name
          break
      
      # check if we assigned a requirement
      if assignment_of_reqs[index] != '':
        break
   
    if assignment_of_reqs[index] == '' and satisfiesRequirement(grade):
      assignment_of_reqs[index] = "Could not be allocated"
    
    index += 1

def isValidAmountOfUoc(min_req, max_req, current_uoc, uoc):
  if min_req is None:
    return False
  elif max_req is None:
    if current_uoc < min_req:
      return True
    else:
      return False
  else:
    if current_uoc < min_req and current_uoc + uoc <= max_req:
      return True
    else:
      return False

def checkingProgression(db, progCode, strmCode, zid):
  allRequirements = LinkedList()
  getAllRequirements(progCode, strmCode, allRequirements)
  allRequirements.sort()
  # loop through transcript
  # get transcript
  transcript = getTranscriptData(db, zid)
  assignment_of_reqs = [''] * len(transcript)

  assign_requirements(transcript, assignment_of_reqs, allRequirements)

  # now print new transcript with requirements
  total_achieved_uoc = 0
  total_attempted_uoc = 0
  weighted_mark_sum = 0

  index = 0
  for subject in transcript:
    course_code, term, subject_title, mark, grade, uoc = subject
    displaying_uoc = uoc
    if assignment_of_reqs[index] == "Could not be allocated":
      displaying_uoc = 0
    print(f"{course_code} {term} {format_string(subject_title)} {markOutput(grade, mark):>3} {gradeOutput(grade):>2s}  {uocOutput(grade, displaying_uoc)}  {assignment_of_reqs[index]}")
    
    total_achieved_uoc += totalAchievedUocCalc(grade, displaying_uoc)

    total_attempted_uoc += totalAttemptedUocCalc(grade, uoc, mark)
    weighted_mark_sum += weightedMarkSumCalc(grade, mark, uoc)
    index += 1
  
  print(f"UOC = {total_achieved_uoc}, WAM = {(weighted_mark_sum/total_attempted_uoc):.1f}")
  printUnsatisfiedRequirements(db, allRequirements)

  # print to be completed list -> already in correct order

def printUnsatisfiedRequirements(db, allRequirements):
  stillUnSatisfiedRequirements = False
  for requirement_node in allRequirements:
    if requirement_node.rtype == "core":
      if not requirement_node.satisfied:
        stillUnSatisfiedRequirements = True
        # loop through courses in acadobjs and count how many left
        uoc_left = 0
        for course in requirement_node.acadobjs:
          subject = course
          if course.startswith("{") and course.endswith("}"):
            subject = course[1:9] 
          
          course_info, = getSubjectUoc(db, subject)
          uoc_left += course_info
          uoc_left

        print(f"Need {uoc_left} more UOC for {requirement_node.name}")
        
        for subject in requirement_node.acadobjs:
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

    elif requirement_node.current_uoc < requirement_node.min_req:
      stillUnSatisfiedRequirements = True
      uoc_left = requirement_node.min_req - requirement_node.current_uoc
      print(f"Need {uoc_left} more UOC for {requirement_node.name}")

  if stillUnSatisfiedRequirements == False:
    print("Eligible to graduate")

# global variables
usage = f"Usage: {sys.argv[0]} zID [Program Stream]"
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
  print("Invalid student ID")
  exit(1)

progCode = None
strmCode = None

if argc == 4:
  progCode = sys.argv[2]
  strmCode = sys.argv[3]

try:
  db = psycopg2.connect("dbname=ass2")

  stuInfo = getStudent(db,zid)
  if not stuInfo:
    print(f"Invalid student id {zid}")
    exit(1)
  print(f"{stuInfo[1]} {stuInfo[2]}, {stuInfo[3]}")

  if progCode and argc == 4:
    progInfo = getProgram(db,progCode)
    if not progInfo:
      print(f"Invalid program code {progCode}")
      exit(1)

  if strmCode and argc == 4:
    strmInfo = getStream(db,strmCode)
    if not strmInfo:
      print(f"Invalid program code {strmCode}")
      exit(1)
    
  # The script already checks the validity of the command-line arguments
  # Therefore assume that supplied stream is part of the supplied program

  if argc == 4:
    # use supplied program
    print(f"{progCode} {strmCode} {progInfo[2]}")
    checkingProgression(db, progCode, strmCode, zid)
  else:
    #use most recent program
    enrolementInfo = getMostRecentEnrolement(db,zid)
    print(f"{enrolementInfo[0]} {enrolementInfo[1]} {enrolementInfo[2]}")
    checkingProgression(db, enrolementInfo[0], enrolementInfo[1], zid)


except Exception as err:
  print("DB error: ", err)
finally:
  if db:
    db.close()

