from datetime import datetime, timedelta
# ----------------------------------------
# System Tools
# ----------------------------------------

def show_current_datetime():
    """Returns the current date and time"""
    now = datetime.now()
    return (f"Today is: {now.strftime('%A')}, {now.strftime('%Y-%m-%d')}\n"
            f"Current time is: {now.strftime('%H:%M:%S')}")

def interpret_date_reference(date_str):
    """Interprets the date based on the string provided by the user"""
    today=datetime.now()
    weekdays={"monday":0, "tuesday":1, "wednesday":2, "thursday":3, "friday":4,
              "saturday":5, "sunday":6}
    months={"january":0, "february":1, "march":2, "april":3,
            "may":4, "june":5, "july":6, "august":7, "september":8,
            "october":9, "november":10, "december":11}
    day_of_week=date_str.lower().strip()
    
    if day_of_week in ["today", "todays"]:
        return today.strftime("%Y-%m-%d")
    
    if day_of_week=="yesterday":
        return (today-timedelta(days=1)).strftime("%Y-%m-%d")
    
    if day_of_week.startswith("last ") and day_of_week.split()[1] in weekdays:
        target_date=weekdays[day_of_week.split()[1]]
        today_date=today.weekday()
        num_days=(today_date-target_date+7)%7 or 7
        req_date=(today-timedelta(days=num_days)).strftime("%Y-%m-%d")
        return req_date
    
    if day_of_week.startswith("last ") and day_of_week.split()[1] in months:
        target_month=months[day_of_week.split()[1]]
        today_month=today.month
        num_months=(today_month-target_month+12)%12 or 12
        if target_month>today_month:
            year=today.year-1
        else:
            year=today.year
        return datetime(year, target_month, 1).strftime("%Y-%m-%d")
    
    return None
    