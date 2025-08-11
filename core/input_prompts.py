def ask_yes_or_no(prompt: str)-> bool:
    YES_INPUTS=["y", "yes"]
    NO_INPUTS=["n", "no"]
    
    while True:
        user_input=input(prompt).strip().lower()
        if user_input in YES_INPUTS:
            return True
        elif user_input in NO_INPUTS:
            return False
        else:
            print("Enter either yes or no, thats y for yes and n for no")

