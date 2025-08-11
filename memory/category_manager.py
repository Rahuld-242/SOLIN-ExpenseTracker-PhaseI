import json
import os
import re
import requests
import spacy
nlp = spacy.load("en_core_web_sm")

default_categories = {
    "Food": "Meals, snacks, restaurants, cafes, delivery, Swiggy, Zomato",
    "Transport": "Cabs, Uber, Ola, bus, train, fuel, metro, autorickshaw, flights",
    "Bills": "Electricity, water, gas, broadband, mobile, DTH, rent",
    "Groceries": "Vegetables, fruits, rice, supermarket, Big Bazaar, daily items",
    "Health": "Medicines, pharmacy, doctor visits, clinic, hospital",
    "Education": "Tuition, coaching, online courses, Udemy, textbooks, school fees",
    "Investment": "Mutual funds, SIPs, stocks, equity, Zerodha, trading",
    "Insurance": "LIC, premiums, life insurance, health cover, vehicle insurance",
    "Shopping": "Amazon, Flipkart, clothes, shoes, electronics, accessories",
    "Social": "Gifts, donations, parties, family functions, celebrations",
    "Entertainment": "Netflix, cinema, games, YouTube Premium, Spotify, events",
    "EMI": "Loan EMI, home loan, bike loan, car installment, credit card EMI",
    "Savings": "Deposits, recurring savings, piggy bank, bank transfer to savings"
}

category_file="memory/categories.json"


def load_categories():
    if not os.path.exists(category_file):
        print("S.O.L.I.N.: Sir, categories.json is missing. I’ve restored default categories.")
        save_categories(default_categories)
        return default_categories
    
    with open(category_file, "r") as file:
        return json.load(file)
    
def save_categories(categories):
    with open(category_file, "w") as file:
        json.dump(categories, file, indent=4)
        
def rephrase_description(desc):
    desc = desc.lower().strip()
    replacements = {
        "swiggy": "Swiggy food delivery",
        "zomato": "Zomato meal order",
        "breakfast": "meal for breakfast",
        "lunch": "meal for lunch",
        "dinner": "meal for dinner",
        "ipad": "Apple tablet iPad",
        "iphone": "Apple mobile phone iPhone",
        "uber": "Uber cab ride",
        "ola": "Ola auto ride",
        "recharge": "mobile recharge payment",
        "netflix": "Netflix subscription",
        "amazon": "shopping on Amazon",
        "flipkart": "shopping on Flipkart",
        "mutual fund": "investment in mutual funds",
        "rent": "monthly house rent"
    }
    for key, val in replacements.items():
        if key in desc:
            desc = desc.replace(key, val)
    return f"This expense is about {desc}."
        
def expense_category_classification(description):
    categories=load_categories()
    if not categories:
        print("No categories found.")
        return {"category": None, "prompt_user": True, "confidence": 0.0}
    
    category_names=list(categories.keys())
    category_list = ", ".join(category_names)
    
    prompt = f"""
    Categorize the following expense into one of the predefined categories.
    Categories: [{category_list}]

    User Input: "{description}"

    Respond with only the category name as a plain text line.
    """
    try:
        response=requests.post(
            "http://localhost:11434/api/generate",
            json={"model":"llama3:8b", "prompt": prompt, "stream": False, "stop":["\n"]},
            timeout=30
            )
        raw=response.json()
        response_text=raw.get("response", "").strip()
        print("LLM Raw Response: ", repr(response_text))
        
        #Match exactly against categories
        if response_text in category_list:
            return {
                "category": response_text,
                "confidence":1.0,
                "prompt_user": False
                }
        else:
            print()
        category=response.text.strip()
        print(f"SOLIN LLM Classifier: {description} -> {category}")
        
        if category in category_names:
            return {"category": category, "confidence": 1.0, "prompt_user": False}
        else:
            raise ValueError("LLM response not in category list.")
            return None
        
    except Exception as e:
        print(f"LLM Categorization failed: {e}")
        # Fallback to manual prompt
        print("\n Available categories: ")
        for i, cat in enumerate(category_names, 1):
            print(f"{i}. {cat}")
        while True:
            choice = input("Please choose a category: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(category_names):
                selected=category_names[int(choice)-1]
                return {"category": selected, "confidence": 1.0, "prompt_user": False}
            else:
                print("Invalid selection. Please enter a valid number")        
    
def extract_amount_from_description(text):
    """
    Extracts the first numeric amount from the given expense description
    Supports formats like ₹48000, 48,000, or plain 48000
    """
    match = re.search(r"(?:₹)?\s?(\d+(?:,\d{3})*(?:\.\d+)?|\d+)", text)
    if match:
        amt=match.group(1).replace(",","")
        return float(amt)
    return None

def extract_description(user_prompt, amount):
    """
    Extracts a clean, user-style description from an expense sentence.
    e.g. "I paid ₹300 for cab ride to office" -> "Cab ride to office"
    """
    
    # Remove ₹ or numeric amount
    pattern=rf"(₹\s*{int(amount)}(?:\.00)?)|\b{int(amount)}(?:\.00)?\b"
    text=re.sub(pattern, '', user_prompt, flags=re.IGNORECASE)
    
    # Parse with SpaCy
    doc=nlp(text)
    
    # Try to return the longest noun phrase
    noun_chunks=[chunk.text.strip() for chunk in doc.noun_chunks if len(chunk.text.strip())>2]
    if noun_chunks:
        return noun_chunks[-1].capitalize()
    
    # Fallback: remove filter verbs, prepositions
    text=re.sub(r'\b(i\s+)?(paid|spent|gave|used|added|bought|towards|for|on|as|in|from|to|at|my|the|a|an)\b', '', text, flags=re.IGNORECASE)
    text=re.sub(r'\s+', ' ', text).strip()
    return text.capitalize()
    
    
    
    
    
