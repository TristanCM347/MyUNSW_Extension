#!/usr/bin/python3
# Track proportion of overseas students

import sys
import psycopg2
import re

#helper functions
def get_student_counts(cursor, TermCode):
  query = """
    SELECT 
            SUM(CASE WHEN distinct_students_of_term_code.status = 'INTL' THEN 1 ELSE 0 END) AS Internationals,
            SUM(CASE WHEN distinct_students_of_term_code.status != 'INTL' THEN 1 ELSE 0 END) AS Locals
    FROM 
            (SELECT DISTINCT s.id, s.status
            FROM Program_enrolments pe
            JOIN Students s ON pe.student = s.id
            JOIN Terms t ON pe.term = t.id
            WHERE t.code = %s) AS distinct_students_of_term_code
    """
  cursor.execute(query, (TermCode,))
  result = cursor.fetchone()
  return result

# global vairables
db = None

try:
  db = psycopg2.connect("dbname=ass2")
  cursor = db.cursor()

  # the header
  print("Term  #Locl  #Intl Proportion")

  terms = [f"{year}T{term}" for year in range(19, 24) for term in range(4) if not (year == 19 and term == 0)]

  for TermCode in terms:
    Internationals, Locals = get_student_counts(cursor, TermCode)
    Proportion = Locals / Internationals
    print(f"{TermCode} {Locals:6d} {Internationals:6d} {Proportion:6.1f}")

except Exception as err:
  print(err)
finally:
  if db:
    db.close()
