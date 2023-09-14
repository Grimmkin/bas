import random
import datetime

first_names = ["Daniel", "Dele", "Folasade", "Victor", "Segun", "Festus", "Marvellous", "Simbi", "Ikechukwu", "David", "Timilehin", "Michael", "Abolaji", "Faruq", "Bolu", "Mark", "Matthew", "Chinedu", "Feranmi"]
last_names = ["Ogunsola", "Adedokun", "Madueke", "Momodu", "Fasesin", "Oti", "Saliu-Aina", "Ojo", "Akinyemi", "Aderounmu", "Erinoso"]
departments = ["Computer Science and Mathematics", "Computer Science and Engineering", "Computer Science and Economics", "Electrical and Electronic Engineering", "Material and Metallurgical Science", "Philosophy"]

def random_student():
    student = {}
    student["first_name"] = random.choice(first_names)
    student["last_name"] = random.choice(last_names)
    student["id"] = random.randint(1,30)
    student["department"] = random.choice(departments)
    
    # Use the current time as the check in time
    current_time = datetime.datetime.now().time()

    # Format the time as a string in the format "hours:minutes:seconds"
    time_in_after_event_starts = current_time.strftime("%H:%M")

    # Add the time_in_after_event_starts to the attendee's info
    student['check in'] = time_in_after_event_starts

    student["check out"] = "--:--"

    if random.choice([1,0,0]):
        student["check out"] = "check out"

    student['type'] = random.choice(["Student", "Staff"])

    return student