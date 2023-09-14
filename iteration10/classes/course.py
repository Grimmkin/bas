from classes.validation import ValidationError
import re
import datetime
import os

class Course:
    def __init__(self, course_code, course_title, days = []):
        if self.validate_model(course_title=course_title, days=days):
            self.course_title = course_title
            self.course_code = course_code
            self.present = {}
            self.days = days
            today = datetime.date.today()  # Gets today's date
        self.filename = f"{self.course_code}-{today.strftime('%d-%m-%Y')}"  # Formats the date as day-month-year

    def validate_model(self, course_title, days):
        if self.validate_title(course_title):
            if self.validate_days(days):
                return True
        raise ValidationError("Validation failed")
    
    def validate_days(self, days):
        if len(days) == 0:
            raise ValidationError("Course is not held on any day")
        
        # validation passed!
        return True
    
    def validate_title(self, title):
        if not title:
            raise ValidationError("Course Title field cannot be empty")
        if len(title) > 100:
            raise ValidationError("title is too long")
        if not re.match(r"^[A-Za-z0-9',. -]+$", title):
            raise ValidationError("titles can only contain alphabets, hyphens, and apostrophes")
        
        # validation passed!
        return True
