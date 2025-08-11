import os
from core.logger import log_command, log_error
from datetime import datetime, timedelta



from tools.system_tools import show_current_datetime, interpret_date_reference
from memory.memory_manager import (
                                   remember,
                                   recall,
                                   forget
                                   )
from tools.expense_tracker import (
                                   add_expenses,
                                   view_expenses,
                                   edit_expense,
                                   delete_expense,
                                   manage_category_deletion,
                                   expense_status,
                                   set_budget,
                                   view_budget,
                                   delete_budget_category
    )
from memory.category_manager import (
                                    expense_category_classification,
                                    extract_description,
                                    extract_amount_from_description,
                                    load_categories
                                    )
from collections import defaultdict

import functools
print = functools.partial(print, flush=True)

def safe_execute(func, action, params=None):
    try:
        if params is None:
            result = func()
        else:
            result = func(**params)
        log_command(
            user_input=action,
            action=action,
            params=params,
            output="Success!"
            )
        return result
    except Exception as e:
        log_error(
            user_input=action,
            action=action,
            params=params,
            error=str(e)
            )
        print(f"Error occurred in '{action}': {e}")
        return {"error": str(e)}
        
def print_intro_to_expense_tracker():
    print("\n" + "=" * 60)
    print("🧾  S.O.L.I.N. Expense Tracker Module — Status: ONLINE")
    print("=" * 60)
    print("Welcome back, Sir. Your financial cockpit is now active.\n")
    print("Here are your current capabilities:")
    print(" ➤  1. Add an expense")
    print(" ➤  2. View today’s expenses or any specific date")
    print(" ➤  3. Set, edit, or delete budget limits by category")
    print(" ➤  4. View your current budget utilization")
    print(" ➤  5. Edit or remove specific logged expenses\n")
    print("💡 Tip: Just say what you want to do, and I’ll handle the rest.")
    print("=" * 60)
    


ACTION_MAP ={
     'remember': remember,
     'recall': recall,
     'forget': forget,
     'start_expense_tracker': print_intro_to_expense_tracker,
     'add_expenses': add_expenses,
     'view_expenses': view_expenses,
     'edit_expense': edit_expense,
     'delete_expense': delete_expense,
     'manage_category_deletion': manage_category_deletion,
     'expense_status': expense_status,
     'set_budget': set_budget,
     'view_budget': view_budget,
     'delete_budget_category': delete_budget_category,
     'show_current_datetime': show_current_datetime,
}

EXPENSE_ACTIONS=[
    "add_expenses",
    "view_expenses",
    "edit_expense",
    "delete_expense",
    "manage_category_deletion",
    "set_budget",
    "view_budget",
    "delete_budget_category"
    ]



def is_date_recent(date_str, max_days_old=30):
    try:
        date_obj=datetime.strptime(date_str, "%Y-%m-%d")
        delta=abs((datetime.now()-date_obj).days)
        return delta <= max_days_old
    except ValueError:
        return False


def dispatch_task(action, params):
    params = params or {}
    
    
    if action == "remember":
       key=params.get("key") or input("Enter the key: ")
       value=params.get("value") or input("Enter the value: ")
       safe_execute(remember, action="remember", params={"key":key, "value":value})
            
    elif action == "recall":
       key=params.get("key") or input("Enter the key you want to me to recall: ")
       safe_execute(recall, action="recall", params={"key":key})
        
    elif action == "forget":
       key=params.get("key") or input("Enter the key you want me to forget: ")
       safe_execute(forget, action="forget", params={"key":key})
            
    
    elif action == "add_expenses":
        
        raw_description = params.get("description").strip()
        
        # Ask only if description is missing or vague
        if not raw_description or raw_description.lower() in ['expense', 'payment', 'something']:
            print("No clear description detected")
            raw_description = input("Enter a description of the expense: ").strip()
            
        
        amount=params.get("amount") or extract_amount_from_description(raw_description)
        if not amount:
            try:
                amount=float(input("Couldn't detect the amount. Please enter it manually: "))
            except ValueError:
                print("Invalid amount")
                return 
            
        description=extract_description(raw_description, amount)
                
        # Semantic category classification
        classification=expense_category_classification(description)
        
        # Respect LLM suggestion if it exists
        if params.get("category"):
            category=params["category"]
        else:
            category=classification["category"]
        
        category=params.get("category") or classification["category"]
        if classification["prompt_user"]:
            print("\nI'm not confident about the category.")
            print(f"My top suggestion is '{category}' (from LLM)")
            
            categories=load_categories()
        
            print("\n Please select the correct category: ")
            for i, name in enumerate(categories.keys(),1):
                print(f"{i}. {name}")
                
            try:
                choice = int(input("Your choice (number): "))
                category=list(categories.keys())[choice - 1]
            except:
                print("Invalid input. Using best guess.")
        
        # Smart amount extraction
       
        
        # Smart date handling
        
        date=params.get("date", "")
        if date:
            interpreted=interpret_date_reference(date)
            if interpreted:
                date=interpreted
        user_input_text=params.get("user_input", "").lower()
        
        if (
                date.endswith("-01")
                and "on" not in user_input_text
                and not any(str(day) in user_input_text for day in range(1,12))
            ):
            print("\nYou mentioned a month like 'June' but no exact payment date.")
            date=input("Please enter the actual date of the expense (YYYY-MM-DD): ").strip()
        elif not date:
            date=input("Enter the date of the expense (YYYY-MM-DD) [optional]: ").strip()
        time = params.get("time") or input("Enter the time of the expense (HH:MM) [optional]: ")
        
        if amount is None:
            print("PHANTOM could not extract the amount. Please enter a valid number.")
            return {"error": "Amount extraction failed"}
    
        result = safe_execute(add_expenses, action="add_expenses", params={
            "category": category,
            "amount": amount,
            "description": description,
            "date": date or None,
            "time": time or None
            })
        
        if not result:
            print("Something went wrong while logging the expense.")
            return
        
        if "error" in result:
            print (f"PHANTOM: {result['error']}")
            return 

        print(f"\nLogged ₹{result['amount']} under '{result['category']}' for '{result['description']}'"
          f"on {result['date']} at {result['time']}.")
    
        if result["over_budget_amount"]:
            if result["over_budget_amount"]>0:
                print(f"Over budget by ₹{result['over_budget_amount']:.2f}")
        elif result['budget_remaining'] is not None:
            print(f"₹{result['budget_remaining']:.2f} remaining in budget.")
        else:
           print(f"No budget set for '{result['category']}'.")

    elif action == "view_expenses":
        date_provided=False
        if "date" in params or "date_filter" in params:
            natural_date=(params.get("date") or params.get("date_filter") or "").replace("_", " ").strip()
            resolved_date=interpret_date_reference(natural_date)
            if resolved_date:
                params["date"]=resolved_date
                date_provided=True
                
            else:
                try:
                    datetime.strptime(natural_date, "%Y-%m-%d")
                    if is_date_recent(natural_date, max_days_old=30):
                        params["date"]=natural_date
                        date_provided=True
                        
                    else:
                        raise ValueError("Too far in the past")
                    #datetime.strptime(params["date"], "%Y-%m-%d")
                    # date is valid; keep it
                except:
                    print("Invalid or hallucinated date: ", params["date"])
                    result = {
                        "status": "failed",
                        "reason": "invalid_or_hallucinated_date"
                        }
                    print(result)
                    return result
            if "date_filter" in params:
                del params["date_filter"]
        elif "days" in params:
            try:
                offset=int(params["days"])
                date_obj=datetime.now() + timedelta(days=offset)
                params["date"]=date_obj.strftime("%Y-%m-%d")
                del params["days"]
                date_provided=True
            except ValueError:
                print("Invalid days offset provided.")
                result={
                    "status":"failed",
                    "reason":"invalid_days_argument"
                    }
                print(result)
                return result
        if not date_provided:
            params["all"]=True
            
        # Clean out bad keys that break view_expenses()
        valid_keys={"date"}
        params = {k:v for k,v in params.items() if k in valid_keys}
        
        print("Final view_expenses params", params)
                
        result = safe_execute(view_expenses, action="view_expenses", params=params)
        
        if not result:
            print("No expenses logged yet.")
            result = {
                "status": "success",
                "expenses": {},
                "total_expense": 0.0
                }
            print (result)
            return result
        
        # Filtered by date - returns 'expenses' and 'total_expense'
        if isinstance(result, dict) and "expenses" in result:
            grouped=defaultdict(lambda: defaultdict(list))
            
            for category, entries in result["expenses"].items():
                for expense in entries:
                    date=expense.get("date","Unknown")
                    grouped[date][category].append(expense)
            
                
            has_entries=False
            for date in sorted(grouped.keys()):
                print(f"\nOn Date: {date}")
                for category, entries in grouped[date].items():
                    print(f"Category: {category}")
                    for expense in entries:
                        has_entries=True
                        amount=expense.get("amount", 0)
                        description = expense.get("description", "")
                        time=expense.get("time", "")
                        print(f"     - ₹{amount:.2f} | {description} @ {time}")
            if has_entries:
                total=result.get("total_expense", 0.0)
                print(f"\nTotal spent overall: ₹{total:.2f}")
                
            else:
                print("No expenses found")
            return result
        
        # No date filter - return full dict
        print("\n All logged expenses by category")
        for category, entries in result.items():
            print(f"\n {category}")
            for expense in entries:
                amount=expense.get("amount", 0)
                description=expense.get("description", "")
                date=expense.get("date", "")
                time=expense.get("time", "")
                print(f"    - ₹{amount:.2f} | {description} | {date} @ {time}")
        return {
            "status": "success",
            "expenses": result
            }
        
    elif action == "edit_expense":
        
        category = params.get("category") or input("Enter the category to edit: ").strip()
        
        preview=safe_execute(view_expenses, action="view_expenses",
                             params={"category": category, "mode": "preview"})
        
        if not preview or not preview.get("success"):
            print(f"Cannot proceed: {preview.get('error')}")
            return {"status": "failed", "reason": "preview_failed"}
        
        entries=preview["entries"]
        if not entries:
            print(f"No entries found in category '{category}'")
            return {"status": "failed", "reason": "no_entries_found"}
        
        print(f"\n Entries in category '{category}':")
        for entry in entries:
            print(f"{entry['index']}. ₹{entry['amount']} | {entry['description']} | {entry['date']} {entry['time']}")
            
        try:
            entry_choice=int(input("Which entry number would you like to edit? ").strip())
        except ValueError:
            print("That doesn't appear to be a valid number.")
            return {"status": "failed", "reason": "invalid_entry_number"}
        
        field_choice=params.get("field_choice") or input(
            "Which field would you like to edit? (amount / description / date / time/ category): ").strip().lower()
        
        valid_fields=["amount", "description", "date", "time", "category"]
            
        if field_choice not in valid_fields:
            print("Invalid field. Must be one of:", ", ".join(valid_fields))
            return {"status": "failed", "reason": "invalid_field"}
        
        current_entry=next((e for e in entries if e["index"]==entry_choice), None)
        if not current_entry:
            print("No entry found with that index.")
            return {"status": "failed", "reason": "entry_not_found"}
        
        print(f"Current value for {field_choice}: {current_entry.get(field_choice)}")
        new_value=params.get("new_value") or input(f"Enter new value for {field_choice}: ").strip()
        
        result = safe_execute(edit_expense, action="edit_expense",
                              params={
                                  "category":category,
                                  "entry_choice": entry_choice,
                                  "field_choice": field_choice,
                                  "new_value": new_value
                                  }
                              )
        
        if result and result.get("success"):
            print(f"{field_choice.title()} for entry {entry_choice} updated to: {new_value}")
            return {"status": "success", "action": "edit_expense"}
        else:
            print(f"Edit failed: {result.get('error')}")
            return {"status": "failed", "reason": result.get("error", "unknown")}
    
    elif action == "delete_expense":
        cat_choice = params.get("cat_choice") or input("Enter the category to delete from: ").strip()
        try:
            entry_choice = int(params.get("entry_choice") or input("Which entry number would you like to delete? ").strip())
        except ValueError:
            print("That doesn't appear to be a valid number.")
            return
        
        confirm = params.get("confirm")
        if confirm is None:
            confirm_input=input("Are you sure you want to delete this entry? (yes/no): ").strip().lower()
            if confirm_input=="yes":
                confirm = True
            else:
                confirm = False
                
        result = safe_execute(delete_expense, action="delete_expense", params={
            "cat_choice": cat_choice,
            "entry_choice": entry_choice,
            "confirm": confirm
            })
        
        if result.get("success"):
            deleted=result["deleted_entry"]
            print(f"Entry {entry_choice} from '{cat_choice}' has been deleted: ₹{deleted['amount']} | {deleted['description']}")
        elif result.get("confirmation_required"):
            print("Deletion not confirmed. Action cancelled.")
        else:
            print(f"Delete failed: {result.get('error')}")  
            
    elif action == "manage_category_deletion":
        cat_choice = params.get("cat_choice") or input("Enter the category you want to manage: ").strip()
        print("Do you want to clear all entries or delete the entire category?")
        action_choice = params.get("action_choice") or input("Type 'clear' or 'delete': ").strip().lower()
        
        result = safe_execute(manage_category_deletion, action="manage_category_deletion", params={
            "cat_choice": cat_choice,
            "action": action_choice
            })
        
        if result.get("success"):
            print(f"Category '{result['cat_choice']}' has been {result['action']}.")
        else:
            print(f"Action failed: {result.get('error')}")
            
    elif action == "expense_status":
        result=expense_status()
        if result.get("success"):
            print("\nExpense Tracker Status:")
            print(f"Last Entry Date: {result['last_entry_date']}")
            print(f"Categories: {result['total_categories']}")
            print(f"Entries: {result['total_entries']}")
            print(f"Total Spent: ₹{result['total_amount_spent']}")
        else:
            print("No expenses found yet")
            
    elif action == "set_budget":
        categories = load_categories()
        print ("Here are the categories")
        for i, cat in enumerate(categories.keys(),1):
            print(f"{i}. {cat}")
            
        category = params.get("category") or input("Enter the category you want to set the budget for: ")
        try:
            budget = params.get("budget") or float(input("Enter the budget amount: "))
        except ValueError:
            print("That doesn't appear to be a valid number.")
            return
        
        result = safe_execute(set_budget, action="set_budget", params={"category": category, "budget": budget})
        
        if not result:
            return "Something went wrong while setting the budget."
            
        
        if "error" in result:
            return f"PHANTOM: {result['error']}"
            
        
        print(f"✅ Budget {result['action']} for '{result['category']}': ₹{result['budget']:.2f}")
        return f"✅ Budget {result['action']} for '{result['category']}': ₹{result['budget']:.2f}"
            
    elif action == "view_budget":
        mode=params.get("mode") or input("View all budgets or a specific category? (all/specific): ").strip().lower()
        category=None
        if mode=="specific":
            category=params.get("category") or input("Which category?: ").strip()
            
        result = safe_execute(view_budget, action="view_budget", params={
            "mode": mode,
            "category": category
            })
        
        if not result:
            print("Failed to retrieve budget information.")
        elif "error" in result:
            print(result["error"])
        elif result["mode"] == "all":
            print("\nHere are your allocated budgets:\n")
            print("Category".ljust(20) + "| " + "Budget".rjust(12))
            print("-" * 35)
            for cat, amt in result["budgets"].items():
                print(f"{cat.title().ljust(20)}| ₹{amt:>11.2f}")
            print("-" * 35)
            print(f"Total categories: {result['total_categories']}\n")
        elif result["mode"] == "specific":
            print(f"Budget for '{result['category']}': ₹{result['budget']:,.2f}")
            
    elif action == "delete_budget_category":
        cat_choice=params.get("cat_choice") or input("Enter the budget category you want to delete: ").strip()
        
        confirm = params.get("confirm")
        if confirm is None:
            confirm_input = input(f"Are you sure you want to delete the budget for '{cat_choice}'? (yes/no): ").strip().lower()
            if confirm_input == "yes":
                confirm = True
            else:
                confirm = False
                
        result = safe_execute(delete_budget_category, action = "delete_budget_category", params={
            "cat_choice": cat_choice,
            "confirm": confirm
            })
        
        if result.get("success"):
            print(f"Deleted budget for '{result['deleted_category']}' (₹{result['deleted_budget']:.2f})")
        elif result.get("confirmation_required"):
            print("Deletion aborted — no confirmation given.")
        else:
            print(f"Failed to delete budget: {result.get('error')}")
            
    elif action in ACTION_MAP:
       result=safe_execute(ACTION_MAP[action], action=action, params=params)
       if result is not None:
           print(f"P.H.A.N.T.O.M.: {result}")
       
    elif action == "help":
       print("\nSir, here are my available capabilities:\n")
    
       for action_name in ACTION_MAP:
           print(f"- {action_name}")

       print("\nSir, simply type the action name to invoke a capability.\n")
    
    else:
       print("Sir, despite my repeated requests, you haven't created an appropriate tool for this action!")
