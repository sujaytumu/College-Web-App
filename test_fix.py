from database import get_all_departments

# Test departments
departments = get_all_departments()
print("Available departments:")
for dept in departments:
    print(f"  {dept['Department_ID']}: {dept['Department_Name']}")

# Test validation
try:
    from database import insert_course
    # This should raise ValueError for empty department_id
    insert_course({
        'course_name': 'Test Course',
        'instructor_id': 1,
        'credits': 3,
        'department_id': '',  # Empty string should raise error
        'max_marks': 100,
        'mid_sem_date': '2024-03-15',
        'end_sem_date': '2024-05-15'
    })
except ValueError as e:
    print(f"Validation working: {e}")
except Exception as e:
    print(f"Other error: {e}")
