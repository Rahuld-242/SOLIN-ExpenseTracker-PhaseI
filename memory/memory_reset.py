import os
from datetime import datetime
from tools.expense_tracker import reset_monthly_expense

def check_and_reset_monthly_expense():
    """Checks if a new month has started and resets the monthly expense if necessary."""
    reset_file= "memory/expense_reset.txt"
    current_month= datetime.now().strftime("%Y-%m")
    if not os.path.exists(reset_file):
        with open(reset_file, "w") as file:
            file.write(current_month)
        
        reset_monthly_expense()
        
        result = reset_monthly_expense()
        
        return {
            "triggered": True,
            "first_time": True,
            "result": result
        }
        
    with open(reset_file, "r") as file:
        last_reset_month = file.read().strip()
            
    if last_reset_month != current_month:
        result=reset_monthly_expense()
        with open(reset_file, "w") as file:
            file.write(f"{current_month}")
        return {
            "triggered": True,
            "first_time": False,
            "result": result
            }
    
    return {
        "triggered": False,
        "message": "Reset already performed for this month."
    }

    
        