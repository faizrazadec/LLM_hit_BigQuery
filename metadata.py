FEW_SHOT="""
Example 1:

Query: "List all students who have warnings and belong to the Computer Science department."

`SELECT s.Name 
FROM Students s
JOIN Departments d ON s.DepartmentID = d.DepartmentID
WHERE s.WarningCount > 0 AND d.Name = 'Computer Science';`

Example 2:

Query: "What courses are offered in the Fall 2025 semester by the Computer Science department?"

`SELECT c.CourseName, cs.Section, cs.AvailableSeats
FROM Courses_Semester cs
JOIN Courses c ON cs.CourseID = c.CourseID
JOIN Departments d ON cs.DepartmentID = d.DepartmentID
WHERE cs.Semester = 'Fall 2025' AND d.Name = 'Computer Science';`

Example 3:

Query: "Get the GPA of student John Doe in the course 'Data Structures' for the Spring 2025 semester."

`SELECT r.GPA 
FROM Registration r
JOIN Students s ON r.RollNumber = s.RollNo
JOIN Courses c ON r.CourseID = c.CourseID
WHERE s.Name = 'John Doe' AND c.CourseName = 'Data Structures' AND r.Semester = 'Spring 2025';`

Example 4:

Query: "How many seats are available for the course 'Algorithms' in the Fall 2025 semester?"

`SELECT cs.AvailableSeats
FROM Courses_Semester cs
JOIN Courses c ON cs.CourseID = c.CourseID
WHERE c.CourseName = 'Algorithms' AND cs.Semester = 'Fall 2025';`
"""