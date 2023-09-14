from classes.validation import ValidationError
import re
import datetime
import os
import pickle

class Event:
    def __init__(self, event_code, event_title):
        if self.validate_model(event_title=event_title):
            self.event_title = event_title
            self.event_code = event_code
            self.present = {}
            self.raw = []
            today = datetime.date.today()  # Gets today's date
        self.filename = f"{self.event_code}-{today.strftime('%d-%m-%Y')}"  # Formats the date as day-month-year
        self._to_storage()

    def validate_model(self, event_title):
        if self.validate_title(event_title):
            return True
        raise ValidationError("Validation failed")

    def validate_title(self, title):
        if not title:
            raise ValidationError("Event Title field cannot be empty")
        if len(title) > 100:
            raise ValidationError("title is too long")
        if not re.match(r"^[A-Za-z0-9',. -]+$", title):
            raise ValidationError("titles can only contain alphabets, hyphens, and apostrophes")
        
        # validation passed!
        return True
    
    def check_in(self, student: dict):

        try:
            if student["department"] not in self.present:
                self.present[student["department"]] = {}
                
            # Add the attendee to the self.present dictionary
            self.present[student["department"]][student["id"]] = student

            # Add to the raw
            self.raw.append(student)
        except Exception as e:
            print(str(e))

        # Trigger the update_storage variable
        self._to_storage()

    def _to_storage(self):
        # Create the directory if it doesn't exist
        if not os.path.exists('./data/events/'):
            os.makedirs('./data/events/')

        # Pickle the object and save it to the specified directory
        try:
            with open(f'./data/events/{self.filename}.evnt', 'wb') as f:
                pickle.dump(self, f)
        except pickle.PicklingError:
            # delete current event
            os.remove(f'./data/events/{self.filename}.evnt')

            with open(f'./data/events/{self.filename}.evnt', 'wb') as d:
                pickle.dump(self, d)