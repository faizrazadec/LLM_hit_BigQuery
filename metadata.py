FEW_SHOT="""
#### Example 1:
**User Query:** "Get the names of all departments."
**Schema Context:**
Table: Departments Columns:
    DepartmentID (INTEGER): A unique identifier for each department.
    Name (STRING): The name of the department.
    Abbrevation (STRING): The abbreviation of the department.
**Response:**
`SELECT Name FROM Departments;`

#### Example 2:
**User Query:** "List all students with their department names."
**Schema Context:**
Table: Students Columns:
    RollNo (STRING): Unique identifier for each student.
    Name (STRING): The name of the student.
    DepartmentID (STRING): Foreign key referencing Departments.DepartmentID.
Table: Departments Columns:
    DepartmentID (INTEGER): Unique identifier for each department.
    Name (STRING): The name of the department.
**Response:**
`SELECT Students.Name, Departments.Name AS DepartmentName FROM Students JOIN Departments ON Students.DepartmentID = Departments.DepartmentID;`

#### Example 3:
**User Query:** "Show the total dues and statuses of challans for all students in Fall 2025."
**Schema Context:**
Table: ChallanForm Columns:
    Semester (STRING): Foreign key referencing Semester.Semester.
    RollNumber (STRING): Foreign key referencing Students.RollNo.
    TotalDues (INTEGER): The total dues for the student.
    Status (STRING): The status of the challan.
Table: Semester Columns:
    Semester (STRING): The name of the semester.
**Response:**
`SELECT RollNumber, TotalDues, Status FROM ChallanForm WHERE Semester = 'Fall 2025';`

#### Example 4:
**User Query:** "Find all courses offered in Spring 2026 with available seats."
**Schema Context:**
Table: Courses_Semester Columns:
    CourseID (INTEGER): Foreign key referencing Courses.CourseID.
    Semester (STRING): Foreign key referencing Semester.Semester.
    AvailableSeats (INTEGER): Number of seats available.
Table: Semester Columns:
    Semester (STRING): Name or identifier of the semester.
**Response:**
`SELECT CourseID, AvailableSeats FROM Courses_Semester WHERE Semester = 'Spring 2026' AND AvailableSeats > 0;`

Your task is to strictly adhere to the schema context and instructions provided. Ensure no pretrained assumptions influence the SQL query generation.
"""