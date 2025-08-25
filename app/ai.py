from google import genai
from dotenv import load_dotenv
import os, re, json
from datetime import datetime, timezone, timedelta  

load_dotenv()
client = genai.Client(api_key=os.getenv("AI_API")) 

def clean_ai_json(raw: str) -> str:
   
    return re.sub(r"^```[a-zA-Z]*\n|\n```$", "", raw.strip())

def creat_task_json(user_input: str) -> dict:  

    current_date_iso = datetime.now(timezone.utc).date().isoformat() 
    
    
    example_date = (datetime.now(timezone.utc) + timedelta(days=2)).replace(hour=9, minute=0)
    example_date_iso = example_date.isoformat()

    prompt = f"""
### ROLE & GOAL ###
You are an expert task management assistant. Your goal is to extract structured task data from a user's informal input. Be smart and context-aware in your interpretation.

### INPUT ###
User Input: "{user_input}"

### PROCESSING INSTRUCTIONS ###
1.  **TITLE:** Create a clear, concise, and actionable title. Use verbs. (e.g., "Buy milk" instead of "milk").
2.  **due_date:**
    - Extract the date and time if mentioned. Use relative terms like "tomorrow" or "next Monday" based on the current date: {current_date_iso}.
    - If a time is not specified, default to 18:00 (end of day) for a mentioned date.
    - Output in strict ISO 8601 format (YYYY-MM-DDTHH:MM). If no date is found, use `null`.
    - if no time mentioned set the time for {current_date_iso}.
3.  **PRIORITY:** Infer from urgency keywords.
    - `High`: "urgent", "asap", "important", "critical", "!!"
    - `Medium`: "should", "need to", "follow up", "soon"
    - `Low`: Default if no urgency is detected.
4.  **DESCRIPTION:** Write a one-sentence description or note that provides more context about the task. This should be different from the title. If no extra context can be inferred, use a simple description like "Task related to [keyword from title]".

### OUTPUT FORMAT ###
You MUST respond with a valid, parsable JSON object containing exactly these fields:
{{
  "title": string,
  "due_date": string (ISO format) | null,
  "priority": "High" | "Medium" | "Low",
  "descreption": "Schedule my annual check-up and cleaning."
}}

### EXAMPLE ###
Input: "ugh i gotta finally call the dentist sometime this week to make an appointment"
Output: {{
  "title": "Call dentist to make appointment",
  "due_date": "{example_date_iso}",
  "priority": "Medium",
  "category": "Health"
}}
"""
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",   
        contents=prompt
    )

    raw_text = response.text  
    cleaned = clean_ai_json(raw_text)

    try:
       
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        
        print(f"Failed to parse the following text as JSON:\n{cleaned}")
        raise ValueError(f"AI response was not valid JSON: {e}") from e

