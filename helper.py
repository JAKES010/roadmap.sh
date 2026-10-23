import json
import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError


load_dotenv()

def create_ticket(title, description):
    ticket_id = int(time.time_ns())  
    new_ticket = {
        "id": ticket_id,
        "title": title.strip(),
        "Description": description.strip()
    }
    return new_ticket

def save_ticket(ticket, filename='tickets.json'):
    if os.path.exists(filename) and os.path.getsize(len(filename) > 0):
        with open(filename, 'r') as file:
            tickets = json.load(file)
    else:
        tickets = []

    tickets.append(ticket)

    with open(filename, 'w') as file:
        json.dump(tickets, file)

def get_ai_suggestions(description):
    """Sends the ticket description to Gemini and returns troubleshooting suggestions."""
    if not os.getenv("GEMINI_API_KEY"):
        return "Error: GEMINI_API_KEY is missing from your environment variables or .env file."

    try:
        client = genai.Client()
        
        prompt = (
            f"You are a helpful campus IT support assistant. A student or staff member reported this issue:\n"
            f"\"{description}\"\n\n"
            f"Provide 3 to 4 short, numbered, practical troubleshooting steps or investigation suggestions "
            f"on how to fix or diagnose this problem."
        )
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
        )
        return response.text

    except APIError as e:
        if "503" in str(e) or "UNAVAILABLE" in str(e):
            return "The AI model is currently experiencing high demand. Please try creating your ticket again in a moment!"
        return f"API Error: Failed to communicate with the AI model ({e})."
    except Exception as e:
        return f"An unexpected error occurred while fetching AI suggestions: {e}"