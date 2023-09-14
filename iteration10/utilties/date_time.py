from datetime import datetime

today = datetime.today()

# returns the date in this format
def get_date(): 
    current_date = today.strftime("%d %B %Y")
    return current_date

def get_current_day_of_week():
    return today.strftime('%A')