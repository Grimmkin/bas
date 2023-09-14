import os, pickle, re, glob
from classes.validation import ValidationError
from utilties.capitalizer import capitalize_non_function_words

class Department:
    def __init__(self, name=None, code=None, level=None, faculty=None, password=None):
        if self.validate_model(name=name, code=code, level=level, faculty=faculty):
            self.name = capitalize_non_function_words(name)
            self.code = code
            self.level = level
            self.faculty = capitalize_non_function_words(faculty)
            self.students = {}
            self.staff = {}
            self.database = f"{self.code.upper()}-{self.level}"
            self.password = password
            self._to_storage()

    def validate_model(self, name, code, level, faculty):
        if self.validate_name(name):
            if self.validate_department_code(code):
                if self.validate_department_faculty(faculty):
                    if self.validate_filename(code, level):
                        return True
        raise ValidationError("Validation failed")
    
    def validate_filename(self, code, level):
        database_filename = f"{code.upper()}-{level}"
        instances = glob.glob(f"./data/department/{database_filename}.dpt")
        if len(instances) > 0:
            raise ValidationError("This department already exists!")
        else:
            return True

    def validate_name(self, name):
        if not name:
            raise ValidationError("Department name field cannot be empty")
        if len(name) > 200:
            raise ValidationError("Department name is too long")
        if not re.match(r"^[A-Za-z0-9',. -]+$", name):
            raise ValidationError("Department Names can only contain alphabets, hyphens, and apostrophes")
        
        # validation passed!
        return True

    def validate_department_code(self, code):
        if not code:
            raise ValidationError("Code field cannot be empty")
        
        regex = r'^[A-Z]{2,4}$'
        if not re.match(regex, code):
            raise ValidationError("enter a valid department code")
        else:
            return True

    def validate_department_faculty(self, faculty_name):
        if not faculty_name:
            raise ValidationError("Faculty field cannot be empty")
        
        if len(faculty_name) > 200:
            raise ValidationError("Faculty name is too long")
        
        regex = r'^[A-Za-z ,\'-]+$'
        if not re.match(regex, faculty_name):
            raise ValidationError("Invalid faculty name")
        else:
            return True
        
    def update_info(self, dictionary):
        try:
            if self.validate_model(
                dictionary["name"], 
                dictionary["code"],
                dictionary["level"],
                dictionary["faculty"]
            ):
                self.__dict__.update(dictionary)

                dir_path = f"./data/departments"
                file_path = f"{dir_path}/{self.database}.dpt"
                os.remove(file_path)
                self.database = f"{self.code.upper()}-{self.level}"
                self._to_storage()
                return True
        except ValidationError as e:
            return False

    def get_students(self):
        return self.students
    
    def get_no_of_students(self):
        return len(self.students)

    def add_student(self, student, edit = False):
        try:
            exists = self.students[student["device_id"]]
            if edit:
                # an edit is being made
                self.students[student["device_id"]] = student
                return True
            raise ValidationError("id already exists in database")
        except KeyError:
            # Safe to add student to database
            self.students[student["device_id"]] = student
            self._to_storage()
            return True
        
    def add_staff(self, staff, edit = False):
        try:
            exists = self.staff[staff["device_id"]]
            if edit:
                # an edit is being made
                self.staff[staff["device_id"]] = staff
                return True
            raise ValidationError("id already exists in database")
        except KeyError:
            # Safe to add student to database
            self.staff[staff["device_id"]] = staff.to_dict()
            self._to_storage()
            return True

    def delete_student(self, student: dict):
        try:
            self.students.pop(student.device_id)
            self._to_storage()
            return True
        except KeyError:
            return False

    def _to_storage(self):
        dir_path = f"./data/departments"
        file_path = f"{dir_path}/{self.database}.dpt"

        # Create the directory if it doesn't exist
        os.makedirs(dir_path, exist_ok=True)

        # Write the instance of the class to the .dpt file
        with open(file_path, 'wb') as f:
            pickle.dump(self, f)