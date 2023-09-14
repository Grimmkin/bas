import os, pickle, datetime

class Events:
    def __init__(self):
        self.events = {}
        self._to_storage()

    def add_event(self, event):
        now = datetime.datetime.now().strftime("%m/%d/%Y")
        
        if event.code not in self.events:
            self.events[event.code] = {}

        if now not in self.events[event.code]:
            self.events[event.code][now] = []

        self.events[event.code][now].append(event.__dict__)
        self._to_storage()
        return True
    
    def get_number_of_events(self):
        return len(self.events)
    
    def get_total_median(self):
        # List to store all median values
        medians = []

        # Iterate over all events
        for event_code in self.events:
            for date in self.events[event_code]:
                for event in self.events[event_code][date]:
                    # Append the median value of the event to the list
                    medians.append(event['median'])

        # Calculate and return the average of the medians
        if medians:
            total_median = sum(medians) / len(medians)
            return total_median
        else:
            return 0


    def _to_storage(self):
        dir_path = f"./data/"
        file_path = f"{dir_path}/events.obas"
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