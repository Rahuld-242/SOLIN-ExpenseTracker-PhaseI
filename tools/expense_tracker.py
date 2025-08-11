import os
import json
from datetime import datetime
from typing import Optional




# ----------------------------------------
# Expense Management
# ----------------------------------------

def add_expenses(category, amount, description, date=None, time=None):
    """Adds daily expenses to an expense tracker file"""
    
    expense_file="memory/expenses.json"
    budgets_file="memory/budgets.json"
    
    if not os.path.exists(expense_file):
        with open(expense_file, "w") as file:
            json.dump({}, file, indent=4, ensure_ascii=False)
            expenses={}
    else:
        with open(expense_file,"r") as file:
            expenses=json.load(file)
            
    if not date:
        date=datetime.now().strftime("%Y-%m-%d")
    if not time:
        time=datetime.now().strftime("%H:%M")
    
    if category not in expenses:
        expenses[category]=[]
        
    expense={
        "amount": amount,
        "description": description,
        "date": date,
        "time": time
    }
    
    expenses[category].append(expense)
        
    with open(expense_file, "w") as file:
        json.dump(expenses, file, indent=4, ensure_ascii=False)
        
    if os.path.exists(budgets_file):
        with open(budgets_file, "r") as file:
            budgets=json.load(file)
    else:
        budgets={}
    
    categorical_expenditure=0
    tot_expenditure=0
    
    for items in expenses[category]:
        categorical_expenditure+=items.get("amount", 0)
    
    for entries in expenses.values():
        for entry in entries:
            tot_expenditure+=entry.get("amount", 0)
        
    budget_limit=budgets.get(category, 0)
    
    #print("[DEBUG] Successfully prepared result for return")
    
    return {
        "category": category,
        "amount": amount,
        "description": description,
        "date": date,
        "time": time,
        "category_total": categorical_expenditure,
        "total_expense": tot_expenditure,
        "budget_limit": budget_limit,
        "over_budget_amount":(
            categorical_expenditure-budget_limit
            if budget_limit and categorical_expenditure>budget_limit else 0),
        "budget_remaining":(
            budget_limit - categorical_expenditure
            if budget_limit and categorical_expenditure<=budget_limit else 0)}
    
def view_expenses(date: Optional[str]=None,
                  all: bool = False,
                  category: Optional[str]=None,
                  mode: str = "view"):
    
    """Displays the logged expenses in the expense tracker"""
    
    print(f"🧪 Received: date={date}, all={all}")
    
    expenses_file="memory/expenses.json"
    
    if not os.path.exists(expenses_file):
        return {
            "expenses": {},
            "total_expense": 0.0,
            "date": date or datetime.now().strftime("%Y-%m-%d")
            }
    
    with open(expenses_file, "r", encoding="utf-8") as file:
        expenses=json.load(file)
        
    if mode=="preview" and category:
        if category not in expenses:
            return {"success": False, "error": f"Category '{category}' not found."}
        
        entries=expenses[category]
        
        # Optional date filter
        if date:
            entries=[e for e in entries if e.get("date")==date]
            
        preview_list=[
            {
                "index": idx+1,
                "amount": e.get("amount"),
                "description": e.get("description"),
                "date": e.get("date"),
                "time": e.get("time")
            } for idx, e in enumerate(entries)
            ]
        
        return {
            "success": True,
            "category": category,
            "entries": preview_list,
            "filter_data": date or "ALL"
            }
                
    filtered={}
    total=0.0
    
    if not all and not date:
        all=True
        
    print(f"Final flags: date={date}, all={all}")
    
    if all:
       
        for category, entries in expenses.items():
            filtered[category]=entries
            total+=sum(e.get("amount", 0) for e in entries)
        return {
            "status": "success",
            "expenses": filtered,
            "total_expense": round(total,2),
            "date": "ALL"
            }
       
    for category, entries in expenses.items():
        matching_entries=[entry for entry in entries if entry.get("date")==date]
        if matching_entries:
            filtered[category]=matching_entries
            for entry in matching_entries:
                 total+=entry.get("amount", 0)
    return {
         "success": "success",
         "date": date,
         "expenses": filtered,
         "total_expense": round(total, 2)
         }
                
def edit_expense(category, entry_choice, field_choice, new_value):
    """Lets the user edit his logged expenses"""
    expense_file="memory/expenses.json"
    
    if not os.path.exists(expense_file):
        return {"success": False, "error": "No expenses logged yet."}
    
    with open(expense_file, "r") as file:
        expenses=json.load(file)
        
    matched_category=None
    for existing_category in expenses:
        if existing_category.lower()==category.lower():
            matched_category=existing_category
            break
    
    if not matched_category:
        print(f"Cannot proceed: Category '{category}' not found.")
        return
    
    category=matched_category
    
    if entry_choice<1 or entry_choice>len(expenses[category]):
        return {"success": False, "error": "Invalid entry choice"}
    
    valid_fields=["amount", "description", "date", "time", "category"]
    if field_choice not in valid_fields:
        return {"success": False, "error": "Invalid field choice"}
        
    entry = expenses[category][entry_choice-1]
    
    if field_choice == "amount":
        try:
            new_value = float(new_value)
        except ValueError:
            return {"success": False, "error": "Invalid amount entered."}
        entry["amount"]=new_value
        
    elif field_choice == "category":
        new_category = new_value.strip()
        # Remove entry from current category
        moved_entry = expenses[category].pop(entry_choice-1)
        
        # Add entry to new category
        if new_category not in expenses:
            expenses[new_category] = []
        expenses[new_category].append(moved_entry)
        
    else:
        entry[field_choice]=new_value
        
    # If old category becomes empty, optionally keep or clean it (your choice)
    # Example: if not expenses[category]: del expenses[category]
    
    with open(expense_file, "w") as file:
        json.dump(expenses, file, indent=4)
        
    return {
        "success": True,
        "category": category,
        "entry_choice": entry_choice,
        "field_choice": field_choice,
        "new_value": new_value
        }
    
def delete_expense(cat_choice, entry_choice, confirm=False):
    """Deletes a specific expense entry"""
    expense_file="memory/expenses.json"
    
    if not os.path.exists(expense_file):
        return {"success": False, "error": "No expenses logged yet."}
    
    with open(expense_file, "r") as file:
        expenses=json.load(file)
    
    if cat_choice not in expenses:
        return {"success": False, "error": f"Category '{cat_choice}' not found."}
    print(f"Sir, here are the logged expenses under '{cat_choice}':")
    
    if entry_choice < 1 or entry_choice > len(expenses[cat_choice]):
        return {"success": False, "error": "Invalid entry index."}
    
    if not confirm:
        return {"success": False, "confirmation_required": True}
        
    deleted_entry=expenses[cat_choice].pop(entry_choice-1)
    
    with open(expense_file, "w") as file:
        json.dump(expenses, file, indent=4)
        
    return {
         "success": True,
         "deleted_entry": deleted_entry,
         "cat_choice": cat_choice,
         "entry_choice": entry_choice
        }
    
def manage_category_deletion(cat_choice, action):
    """Manages the deletion of a category from the expense tracker"""
    
    expense_file="memory/expenses.json"
    
    if not os.path.exists(expense_file):
        return {"success": False, "error": "No expenses logged yet."}
    
    with open(expense_file, "r") as file:
        expenses=json.load(file)
        
    if cat_choice not in expenses:
        return {"success": False, "error": f"Category '{cat_choice}' not found."}
    
    if action == "clear":
        if not expenses[cat_choice]:
            return {"success": False, "error": f"Category '{cat_choice}' is already empty."}
        expenses[cat_choice] = []
        action_taken = "cleared"
        
    elif action == "delete":
        del expenses[cat_choice]
        action_taken = "deleted"
    else:
        return {"success": False, "error": "Invalid action. Must be 'clear' or 'delete'."}
    
    with open(expense_file, "w") as file:
        json.dump(expenses, file, indent=4)
        
    return {
        "success": True,
        "cat_choice": cat_choice,
        "action": action_taken
        }
        
def expense_status():
    """Returns a status summary of all expense logs"""
    expense_file = "memory/expenses.json"
    
    if not os.path.exists(expense_file):
        return {"success": False, "message": "No expenses found."}
    
    with open(expense_file, "r") as file:
        expenses=json.load(file)
        
    total_entries=0
    total_categories=len(expenses)
    total_amount_spent=0.0
    latest_date=None
    
    for entries in expenses.values():
        for entry in entries:
            total_entries+=1
            total_amount_spent+=entry.get("amount",0.0)
            entry_date=entry.get("date")
            if entry_date:
                if not latest_date or entry_date>latest_date:
                    latest_date=entry_date
    return {
        "success": True,
        "last_entry_date": latest_date,
        "total_entries": total_entries,
        "total_categories": total_categories,
        "total_amount_spent": round(total_amount_spent, 2)
        }
    
    
# ----------------------------------------
# Budget Management
# ----------------------------------------
        
def set_budget(category, budget):
    """Sets a budget for the specified category"""
    categories_file="memory/categories.json"
    budget_file="memory/budgets.json"
    
    # Load category keys
    if not os.path.exists(categories_file):
        return {"success": False, "error": "No categories defined. Please add categories first."}
    
    with open(categories_file, "r") as file:
        categories=json.load(file)
        
    budget_categories=set(categories.keys())
    
    if category not in categories:
        return {"success": False,
                "error": f"'{category}' is not a valid category. Valid categories are: {', '.join(budget_categories)}"
               }
    
    # if budgets.json is missing    
    if not os.path.exists(budget_file):
        budgets={cat: 0 for cat in budget_categories}
        with open(budget_file, "w") as file:
            json.dump(budgets, file, indent=4)
    else:
        with open(budget_file, "r") as file:
            budgets=json.load(file)
    
    action = "updated" if category in budgets and budgets[category]!=0 else "set"
    budgets[category] = budget
    
    with open(budget_file, "w") as file:
        json.dump(budgets, file, indent=4)
        
    return {
        "success": True,
        "category": category,
        "budget": budget,
        "action": action,
        "message": f"Budget {action} for '{category}': ₹{budget:.2f}"
        }
    
def view_budget(mode="all", category=None):
    """Returns budget data for all or a specific category, based on mode."""
    budget_file="memory/budgets.json"
    
    if not os.path.exists(budget_file):
        return {"error": "No budgets have been set yet."}
        
    with open(budget_file, "r") as file:
        budgets=json.load(file)
    
    if mode=="all":
        total_categories = len(budgets)
        return {
            "mode": "all",
            "budgets": budgets,
            "total_categories": total_categories
            }
    
    elif mode=="specific":
        if category in budgets:
            return {
                "mode": "specific",
                "category": category,
                "budget": budgets[category]
                }
        else:
            return {
                "error": f"No budget found for category '{category}'."
                }
    
    else:
        return {"error": "Invalid mode. Use 'all' or 'specific'."}
    
def delete_budget_category(cat_choice, confirm=False):
    """Deletes a budget category if it exists and confirmation is True."""
    budget_file="memory/budgets.json"
    
    if not os.path.exists(budget_file):
        return {"success": False, "error": "No budgets have been set yet."}
    
    with open(budget_file, "r") as file:
        budgets=json.load(file)
        
    if cat_choice not in budgets:
        return {"success": False, "error": f"Category '{cat_choice}' not found in your budgets."}
        
    if not confirm:
        return {"success": False, "confirmation_required": True}
    
    deleted_value = budgets.pop(cat_choice)
    
    with open(budget_file, "w") as file:
        json.dump(budgets, file, indent=4)
        
    return {
        "success": True,
        "deleted_category": cat_choice,
        "deleted_budget": deleted_value
    }
    
# ----------------------------------------
# Monthly Reset and Archival
# ----------------------------------------
    
def reset_monthly_expense():
    """Resets the expense every month"""
    expense_file="memory/expenses.json"
    
    if not os.path.exists(expense_file):
        return {
            "success": False,
            "error": "No expenses logged yet."
        }
    
    with open(expense_file, "r") as file:
        expenses=json.load(file)
        
    monthly_archives={}
    
    for categories, entries in expenses.items():
        for entry in entries:
            date=entry.get("date", "")
            year_month=datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")
            
            if year_month not in monthly_archives:
                monthly_archives[year_month] = {}
                
            if categories not in monthly_archives[year_month]:
                monthly_archives[year_month][categories] = []
                
            monthly_archives[year_month][categories].append(entry)
    
    current_month=datetime.now().strftime("%Y-%m")
    archived_files = []
            
    for date in monthly_archives:
               
        if date==current_month:
            continue
        
        archive_file=f"memory/archives/expenses_{date}.json"
        
        if not os.path.exists(os.path.dirname(archive_file)):
            os.makedirs(os.path.dirname(archive_file))
        
        with open(archive_file, "w") as file:
            json.dump(monthly_archives[date], file, indent=4)
            archived_files.append(archive_file)
            
    for category in expenses:
        current_month_entries=[]
        for entry in expenses[category]:
            entry_date=entry.get("date", "")[:7]
            if entry_date == current_month:
                current_month_entries.append(entry)
        expenses[category]=current_month_entries
                
    with open(expense_file, "w") as file:
        json.dump(expenses, file, indent=4)
        
    return {
        "success": True,
        "archived_months": [f.split("_")[-1][:-5] for f in archived_files],
        "archived_files": archived_files,
        "retained_month": current_month
    }


