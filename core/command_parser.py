from agents.llm_agent import llm_understand

def parse_command(user_input):
    user_input=user_input.lower()
    
    if "create file" in user_input:
        return "create_file"
    
    elif "open browser" in user_input:
        return "open_browser"
    
    elif "calculate my income tax" in user_input:
        return "calculate_income_tax"
    
    elif any(phrase in user_input for phrase in [
            "start expense tracker",
            "open expense tracker",
            "launch expense tracker",
            "begin expense tracker",
            "start my expense tracker",
            "get started with expense tracker",
            "start the expense tracker"]):
        return {
            "action": "start_expense_tracker",
            "params":{}
            }
    
    # Fallback to LLM interpretation
    action = llm_understand(user_input)
    return action
    
        

