# COMP3311 21T3 Ass2 ... Python helper functions
# add here any functions to share between Python scripts 
# you must submit this even if you add nothing

def minMaxOutput(min, max):
  if min is None and max is None:
    # both min and max are null
    # nothing to be displayed
    pass
  elif min is not None and max is None:
    #min is not null, max is null
    print(f"at least {min}", end='')
  elif min is None and max is not None:
    #min is null, max is not null
    print(f"up to {max}", end='')
  elif min is not None and max is not None:
    if min < max:
      #both are not null and min < max
      print(f"between {min} and {max}", end='')
    elif min == max:
      # both are nt null and min = max
      print(f"{min}", end='')

def getProgram(db,code):
  cursor = db.cursor()
  cursor.execute("select * from Programs where code = %s",[code])
  info = cursor.fetchone()
  cursor.close()
  if not info:
    return None
  else:
    return info

def getSubject(db, subject):
  cursor = db.cursor()
  query = """
      SELECT  title AS course_name
      FROM    Subjects s
      WHERE   s.code = %s
      """
  cursor.execute(query, (subject,))
  info = cursor.fetchone()
  cursor.close()
  if not info:
    return None
  else:
    return info

def getSubjectUoc(db, subject):
  cursor = db.cursor()
  query = """
      SELECT  uoc AS uoc
      FROM    Subjects s
      WHERE   s.code = %s
      """
  cursor.execute(query, (subject,))
  info = cursor.fetchone()
  cursor.close()
  if not info:
    return None
  else:
    return info

def getStream(db,code):
  cursor = db.cursor()
  cursor.execute("select * from Streams where code = %s",[code])
  info = cursor.fetchone()
  cursor.close()
  if not info:
    return None
  else:
    return info

def getStudent(db,zid):
  cursor = db.cursor()
  qry = """
  select p.*
  from   People p
         join Students s on s.id = p.id
  where  p.zid = %s
  """
  cursor.execute(qry,[zid])
  info = cursor.fetchone()
  cursor.close()
  if not info:
    return None
  else:
    return info

def getMostRecentEnrolement(db,zid):
  cursor = db.cursor()
  qry = """
  SELECT    program.code AS p_code,
            stream.code AS s_code,
            program.name AS name
  FROM      Program_enrolments pe
  JOIN      Terms t ON pe.term = t.id
  JOIN      Students s ON s.id = pe.student
  JOIN      People p ON p.id = s.id
  JOIN      Programs program ON program.id = pe.program
  JOIN      Stream_enrolments se ON se.part_of = pe.id
  JOIN      Streams stream ON se.stream = stream.id
  WHERE     p.zid = %s
  ORDER BY  CAST(SUBSTRING(t.code, 1, 2) AS INT) DESC, 
            CAST(SUBSTRING(t.code, 4, 1) AS INT) DESC
  LIMIT 1;
  """
  cursor.execute(qry,[zid])
  info = cursor.fetchone()
  cursor.close()
  if not info:
    return None
  else:
    return info

def getTranscriptData(db, zid):
  cursor = db.cursor()
  qry = """
  SELECT    s.code AS course_code,
            t.code AS term,
            s.title AS subject_title,
            ce.mark AS mark,
            ce.grade AS grade,
            s.uoc AS uoc
  FROM      Course_enrolments ce
  JOIN      Courses c ON ce.course = c.id
  JOIN      Terms t ON t.id = c.term
  JOIN      Subjects s ON s.id = c.subject
  JOIN      Students st ON st.id = ce.student
  JOIN      People p ON p.id = st.id
  WHERE     p.zid = %s
  ORDER BY  CAST(SUBSTRING(t.code, 1, 2) AS INT), 
            CAST(SUBSTRING(t.code, 4, 1) AS INT),
            SUBSTRING(s.code, 1, 4),
            CAST(SUBSTRING(s.code, 5, 4) AS INT);
  """
  cursor.execute(qry,[zid])
  info = cursor.fetchall()
  cursor.close()
  if not info:
    return None
  else:
    return info

def getCoreRequirements(db, code, typeFor):
  if typeFor == "for_program":
    tableName = "Programs"
  elif typeFor == "for_stream":
    tableName = "Streams"
  query = f"""
    SELECT    r.acadobjs AS courses,
              r.name AS name
    FROM      Requirements r
    JOIN      {tableName} x ON x.id = r.{typeFor}
    WHERE     x.code = %s AND r.rtype = 'core'
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

def getElectiveRequirements(db, code, typeFor):
  if typeFor == "for_program":
    tableName = "Programs"
  elif typeFor == "for_stream":
    tableName = "Streams"
  query = f"""
    SELECT    r.min_req AS min,
              r.max_req AS max,
              r.acadobjs AS courses,
              r.name AS name
    FROM      Requirements r
    JOIN      {tableName} x ON x.id = r.{typeFor}
    WHERE     x.code = %s AND r.rtype = 'elective'
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

def weightedMarkSumCalc(grade, mark, uoc):
  valid_grades = {'HD', 'DN', 'CR', 'PS', 'FL', 'UF', 'E', 'F'}
  if mark is None:
    return 0
  elif grade in valid_grades:
    return (uoc*mark)
  else:
    return 0

def totalAttemptedUocCalc(grade, uoc, mark):
  valid_grades = {'HD', 'DN', 'CR', 'PS', 'AF', 'FL', 'UF', 'E', 'F'}
  if grade in valid_grades:
    return uoc
  else:
    return 0 # this inlcudes the AF case where mark is null

def totalAchievedUocCalc(grade, uoc):
  valid_grades = {'A', 'B', 'C', 'D', 'A+', 'B+', 'C+', 'D+','A-', 'B-', 'C-', 'D-','HD', 'DN', 'CR', 'PS', 'XE', 'T', 'SY', 'EC', 'RC'}
  if grade in valid_grades:
    return uoc
  else:
    return 0

def format_string(s):
    # Truncate if longer than 32 characters
    if len(s) > 31:
        return s[:31]
    
    # Pad with spaces if shorter than 32 characters
    return s.ljust(31)
  
def markOutput(grade, mark):
  # valid_grades = {'HD', 'DN', 'CR', 'PS', 'FL', 'UF', 'E', 'F'}
  if mark is None and grade != 'AF':
    return "-"
  elif mark is None and grade == 'AF':
    return "0"
  else:
    return f"{mark}" # still print the mark even if its not valid, it just doesnt go towards wam i think

def gradeOutput(grade):
  if grade is None:
    return "-"
  else:
    return grade

def uocOutput(grade, uoc):
  valid_grades = {'A', 'B', 'C', 'D', 'A+', 'B+', 'C+', 'D+','A-', 'B-', 'C-', 'D-', 'HD', 'DN', 'CR', 'PS', 'XE', 'T', 'SY', 'EC', 'RC'}
  fail_grades = {'AF', 'FL', 'UF', 'E', 'F'}
  unresolved_grades = {'AS', 'AW', 'PW', 'NA', 'RD', 'NF', 'NC', 'LE', 'PE', 'WD', 'WJ'}
  if grade in valid_grades:
    return f"{uoc:2d}uoc"
  elif grade in fail_grades:
    return " fail"
  elif grade in unresolved_grades:
    return " unrs"
  elif grade is None:
    return "     "
  else:
    return "     "


