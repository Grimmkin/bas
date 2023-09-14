import os, pickle, copy
import pandas as pd

from pprint import pprint

from utilties.date_time import get_current_day_of_week

day_ext = get_current_day_of_week()

class Schedule():
    def __init__(self):
        self.schedule = {day: copy.deepcopy([]) for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]}
        pprint(self.schedule)
        self._to_storage()

    def add_to_schedule(self, course):
        for day in course.days:
            self.schedule[day].append(course.__dict__)
        self._to_storage()

    def get_courses(self):
        temp = []
        for i in list(self.schedule.values()):
            for j in i:
                temp.append(j)

        return_list = []
        for i in temp:
            if i not in return_list:
                return_list.append(i)

        return return_list
    
    def get_event_info(self, event: str):
        assert event in self.schedule[day_ext]["course_code"]
        
        index = self.schedule[day_ext]["course_code"].index(event)

        return {
            "course_code": self.schedule[day_ext]["course_code"][index],
            "course_title": self.schedule[day_ext]["course_title"][index],
        }

    def _to_storage(self):
        dir_path = f"./data/"
        file_path = f"{dir_path}/schedule.obas"
        os.makedirs(dir_path, exist_ok=True)
            
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(self, f)
        except Exception as e:
            print("An error occurred while writing to the file:", e)
        finally:
            if not f.closed:
                print("File is not closed, closing now")
                f.close()

        # dir_path = f"./data/"
        # file_path = f"{dir_path}/schedule.obas"

        # # Create the directory if it doesn't exist
        # os.makedirs(dir_path, exist_ok=True)

        # with open(file_path, 'wb') as f:
        #     pickle.dump(self, f)