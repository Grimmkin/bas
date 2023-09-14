import re
from classes.validation import ValidationError

class StudentModel:
    def __init__(self, first_name, last_name, id, device_id, sex):
        if self.validate_model(first_name = first_name, last_name = last_name, id = id, device_id=device_id):
            self.first_name = first_name
            self.last_name = last_name
            self.id = int(id)
            self.device_id = device_id
            self.sex = sex

    def validate_model(self, first_name, last_name, id, device_id):
        if self.validate_device_id(device_id):
            if self.validate_first_name(first_name):
                if self.validate_last_name(last_name):
                    if self.validate_id(id):
                        return True
        raise ValidationError("Validation failed")
    
    def validate_device_id(self, device_id):
        if device_id == None or device_id == "?" or device_id == "" or device_id == " ":
            raise ValidationError("Fingerprint has not been enrolled")
        return True
    
    def validate_first_name(self, name):
        if not name:
            raise ValidationError("First name field cannot be empty")
        if len(name) > 100:
            raise ValidationError("First name is too long")
        if not re.match(r"^[A-Za-z'-]+$", name):
            raise ValidationError("Names can only contain alphabets, hyphens, and apostrophes")
        
        # validation passed!
        return True
    
    def validate_last_name(self, name):
        if not name:
            raise ValidationError("Last name field cannot be empty")
        if len(name) > 50:
            raise ValidationError("Last name is too long")
        if not re.match(r"^[A-Za-z'-]+$", name):
            raise ValidationError("Names can only contain alphabets, hyphens, and apostrophes")
        
        # validation passed!
        return True
    
    def validate_id(self, id):
        try:
            id = int(id)
        except ValueError:
            raise ValidationError("Matriculation number has to be a number")
        if id < 0:
            raise ValidationError("Matriculation number cannot be negative")
        if not id:
            raise ValidationError("Matriculation number field cannot be 0")
        # check database to make sure number is unique
        if not 1 <= id <= 999:
            raise ValidationError("Matriculation number must be between 1 and 999")
        
        return True

    def to_dict(self):
        # or just use .__dict__ ;)
        return self.__dict__