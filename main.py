def run_solin():
    from agents.llm_agent import interpret_command
    from core.task_dispatcher import dispatch_task, print_intro_to_expense_tracker
    from datetime import datetime
    from memory.memory_reset import check_and_reset_monthly_expense


    # Startup banner
    import time

    print("Initializing S.O.L.I.N.", end="")
    for _ in range(3):
        time.sleep(0.4)
        print(".", end="")
    print("\nAI assistant is now active. Ready for your command.\n")


    # Time-based greeting
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    print("🔆 S.O.L.I.N. — Self-Organizing Language Intelligence Node")
    print("Brilliance on demand.")
    print(f"{greeting}, Sir!")
    
    print_intro_to_expense_tracker()

    reset_status = check_and_reset_monthly_expense()

    if reset_status.get("triggered"):
        result = reset_status["result"]
        if result.get("success"):
            print("Monthly expense reset completed.")
            print(f"Archived: {', '.join(result['archived_months'])}")
        else:
            print(f"Reset failed: {result.get('error')}")

    while True:
        user_input=input("You: ")
        if user_input.strip().lower() in ["exit", "quit", "escape","bye"]:
            print("Goodbye, Until next time.")
            break
            
        response_line=interpret_command(user_input)
        if response_line:
            action=response_line.get("action")
            params=response_line.get("params",{})
            print(f"\nS.O.L.I.N.: Executing '{action}' with parameters {params}")
            dispatch_task(action, params)
        else:
            print("\nS.O.L.I.N.: Unable to process your request.")


if __name__=="__main__":
    run_solin()
    