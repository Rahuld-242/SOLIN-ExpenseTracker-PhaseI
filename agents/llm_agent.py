import os
import requests
import json
import re
import unicodedata
import time

def interpret_command(user_input):
    max_retries=5
    retry_delay=3
    base_dir=os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
    system_prompt_file=os.path.join(base_dir,"prompts","system_prompts.md")
    
    if not os.path.exists(system_prompt_file):
        print("System prompt file not found. I’d love to help, but I need that first.")
        return None
        
    with open(system_prompt_file, "r", encoding="utf-8") as file:
        system_prompt=file.read()
        
    final_prompt=(
        f"{system_prompt.strip()}\n\n"
        f"Interpret the following user request and return a dictionary describing the action.\n"
        f"### User Input:\n"
        f"{user_input.strip()}"
        )

    url="http://localhost:11434/api/generate"

    payload={
        "model":"llama3:8b",
        "prompt":final_prompt,
        "stream": False
        }
    
    for attempt in range(max_retries):
        try:
            response=requests.post(url, json=payload)
            if response.status_code==200:
                break
            else:
                print(f"Attempt {attempt+1}: Ollama returned status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt+1} failed: {e}")
        time.sleep(retry_delay)
        
    else:
        print(f"Ollama could not be reached after {max_retries} attempts.")
        return None
    
    if response.status_code==200:
        json_response=response.json()
        json_output=json_response.get("response", "")
        print("Raw LLM Response:\n", json_output)
        parsed = extract_dict(json_output)
        return parsed
    else:
        print(f"Ollama returned an error code: {response.status_code}. Possibly offended by the prompt.")
        return None
    
def extract_dict(response_line)->dict:
    """
    Extracts a valid JSON dictionary from an LLM response.
    Handles markdown code blocks, extra text, and common formatting noise.
    """
    
    response_line = response_line.replace("```json", "").replace("```", "").strip()
    
    response_line = unicodedata.normalize("NFKC", response_line)
    
    start=response_line.find("{")
    if start==-1:
        print("No opening brace found.")
        return None
    
    brace_count = 0
    for i in range(start, len(response_line)):
        if response_line[i] == "{":
            brace_count+=1
        elif response_line[i] == "}":
            brace_count-=1
            if brace_count == 0:
                json_str = response_line[start:i+1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    print(f"JSON decoding failed: {e}")
                    print("Extracted (bad) block was :\n", repr(json_str))
                    return None
    print("Unmatched braces - no valid JSON object found.")
    return None

    

