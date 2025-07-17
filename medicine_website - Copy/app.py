import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from groq import Groq

# --- Initialization ---
load_dotenv()
app = Flask(__name__)

try:
    groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    GOOGLE_CSE_ID = os.environ.get("GOOGLE_CSE_ID")
except Exception as e:
    print(f"Error initializing API clients: {e}")
    groq_client = None

# --- API Helper Functions ---

def perform_google_search(query, api_key, cse_id, num_results=10):
    """
    Performs a single targeted Google search and returns a string of snippets.
    """
    print(f"--- Performing Google Search for: '{query}' ---")
    if not api_key or not cse_id:
        print("WARNING: Google Search API credentials not configured.")
        return ""
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {'q': query, 'key': api_key, 'cx': cse_id, 'num': num_results}
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        results = response.json().get('items', [])
        return " ".join([item.get('snippet', '').replace('\n', ' ') for item in results])
    except Exception as e:
        print(f"Google Search API Error for query '{query}': {e}")
        return ""

def get_medicine_image_url(medicine_name, api_key, cse_id):
    """
    Gets the URL of the first relevant image result for a medicine.
    """
    print(f"--- Searching for image of: {medicine_name} ---")
    if not api_key or not cse_id: return None
    url = "https://www.googleapis.com/customsearch/v1"
    # A more specific query to get clean product shots
    query = f'{medicine_name} tablet strip box'
    params = {'q': query, 'key': api_key, 'cx': cse_id, 'searchType': 'image', 'num': 1, 'imgSize': 'medium'}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        items = response.json().get('items', [])
        return items[0]['link'] if items else None
    except Exception as e:
        print(f"Google Image Search Error: {e}")
        return None

def process_with_groq(system_prompt, user_prompt):
    """
    A generic function to call the Groq AI with specified prompts.
    """
    if not groq_client: raise ConnectionError("Groq client not initialized.")
    try:
        completion = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        response_text = completion.choices[0].message.content
        return json.loads(response_text)
    except Exception as e:
        print(f"Groq API Error: {e}")
        return {"error": "The AI service encountered an error during processing."}

# --- Main Flask Route ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    user_query = request.json.get('medicine_name', '').strip()
    if not user_query:
        return jsonify({'error': 'Please enter a medicine name.'}), 400

    try:
        # --- STAGE 1: Precise Composition Discovery ---
        print("\n--- STAGE 1: Initial AI Analysis & Composition ---")
        composition_context = perform_google_search(f'"{user_query}" composition ingredients', GOOGLE_API_KEY, GOOGLE_CSE_ID, num_results=5)
        if not composition_context:
            return jsonify({'error': "Could not retrieve composition info for this drug."}), 404
        
        stage1_system_prompt = """
        From the user query and web context, your only job is to identify the drug's exact chemical composition.
        Output a single, raw JSON object with one key, 'composition'.
        Example: { "composition": "Paracetamol 500mg" }
        """
        composition_result = process_with_groq(stage1_system_prompt, f"CONTEXT: {composition_context}\nUSER QUERY: {user_query}")
        
        composition = composition_result.get("composition")
        if not composition:
            return jsonify({'error': "AI could not determine the drug's composition."}), 404
        
        generic_name = composition.split(' ')[0]

        # --- STAGE 2: Massive Information Gathering ---
        print(f"\n--- STAGE 2: Building Super-Context for '{composition}' ---")
        queries = {
            "uses": f'"{composition}" detailed uses and indications',
            "side_effects": f'"{composition}" common and rare side effects professional',
            "warnings": f'"{composition}" contraindications and warnings',
            "alternatives": f'"{composition}" brand names and manufacturers in india',
            "generic_info": f'what is "{generic_name}" medicine class and mechanism of action'
        }
        
        super_context = ""
        for key, query in queries.items():
            super_context += f"\n\n--- CONTEXT FOR {key.upper()} ---\n"
            super_context += perform_google_search(query, GOOGLE_API_KEY, GOOGLE_CSE_ID)

        # --- STAGE 3: Final, Comprehensive Synthesis ---
        print("\n--- STAGE 3: Final AI Synthesis ---")
        stage3_system_prompt = """
        You are a Drug Information Synthesizer. Your job is to meticulously analyze the provided, pre-categorized web search contexts and create a single, comprehensive JSON report.

        CRITICAL RULES:
        - For each section (uses, side_effects, etc.), create a long, detailed, and thorough bulleted list based ONLY on its corresponding context.
        - For 'alternatives', create a list of objects, each containing the 'brand_name' and 'manufacturer'. If a manufacturer is not clearly associated with a brand, omit that brand. Find as many as you can.
        - For 'generic_info_paragraph', write a detailed, professional summary of the drug's class and how it works, based on its context.
        - The output must be a single, raw JSON object.

        JSON OUTPUT STRUCTURE:
        {
          "generic_info_paragraph": "A detailed paragraph about the generic drug.",
          "summary": {
              "uses": ["A long, detailed list of key uses."],
              "side_effects": ["A long, detailed list of common and rare side effects."],
              "warnings": ["A long, detailed list of important warnings."]
          },
          "alternatives": [
            { "brand_name": "Brand Name 1", "manufacturer": "Manufacturer 1" },
            { "brand_name": "Brand Name 2", "manufacturer": "Manufacturer 2" }
          ]
        }
        """
        final_summary = process_with_groq(stage3_system_prompt, f"CONTEXTS:\n{super_context}\n\nUSER QUERY: Create a full report for a drug with composition: {composition}")

        # --- STAGE 4: Assemble the Final Response ---
        print("\n--- STAGE 4: Assembling Final Response ---")
        final_response = {
            "identified_medicine": user_query.title(),
            "composition": composition,
            "generic_name": generic_name,
            "image_url": get_medicine_image_url(user_query, GOOGLE_API_KEY, GOOGLE_CSE_ID),
            **final_summary
        }

        print(f"✅ Final report generated with {len(final_response.get('alternatives', []))} unique alternatives.")
        return jsonify(final_response)

    except Exception as e:
        print(f"An unexpected server error occurred: {e}")
        return jsonify({'error': "An unexpected server error occurred."}), 500

@app.route('/ai-assistant', methods=['POST'])
def ai_assistant():
    data = request.get_json()
    user_message = data.get('message', '').strip() if data else ''
    if not user_message:
        return jsonify({'reply': 'Please enter a message.'}), 400
    if not groq_client:
        return jsonify({'reply': 'AI service is not available.'}), 503
    try:
        system_prompt = "You are a helpful, professional medical assistant. Answer user questions clearly and concisely. If the question is about a medicine, provide relevant information. If it is a general health question, answer helpfully."
        completion = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        ai_reply = completion.choices[0].message.content.strip()
        return jsonify({'reply': ai_reply})
    except Exception as e:
        print(f"Groq AI Assistant Error: {e}")
        return jsonify({'reply': 'Sorry, there was an error processing your request.'}), 500

if __name__ == '__main__':
    app.run(debug=True)