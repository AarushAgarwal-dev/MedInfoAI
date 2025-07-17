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
    Performs a Google search, handling pagination for more than 10 results.
    Returns a tuple: (list_of_results, error_message).
    Each result is a dictionary with 'snippet', 'title', and 'link'.
    On success, error_message is None. On failure, list_of_results is None.
    """
    print(f"--- Performing Google Search for: '{query}' ---")
    if not api_key or not cse_id:
        return None, "Google Search API credentials are not configured on the server."

    url = "https://www.googleapis.com/customsearch/v1"
    all_results = []
    
    # The API is limited to 10 results per request. Paginate if more are requested.
    # The API is also limited to a total of 100 results.
    num_results = min(num_results, 100)
    
    for start_index in range(1, num_results, 10):
        num_for_this_request = min(10, num_results - start_index + 1)
        
        params = {
            'q': query, 
            'key': api_key, 
            'cx': cse_id, 
            'num': num_for_this_request,
            'start': start_index
        }
        
        try:
            print(f"   - Requesting {num_for_this_request} results, starting at index {start_index}...")
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            results = response.json().get('items', [])
            
            processed_results = [
                {
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', '').replace('\n', ' '),
                    'link': item.get('link', '')
                }
                for item in results
            ]
            all_results.extend(processed_results)
            
        except requests.exceptions.HTTPError as http_err:
            error_details = http_err.response.json().get('error', {})
            error_message = error_details.get('message', 'An unknown HTTP error occurred.')
            status_code = error_details.get('code', 'N/A')
            print(f"Google Search HTTP Error for query '{query}': {status_code} - {error_message}")
            return None, f"Google API Error: {error_message}"
        except requests.exceptions.RequestException as req_err:
            print(f"Google Search Request Error for query '{query}': {req_err}")
            return None, "A network error occurred while contacting the Google Search API."
        except Exception as e:
            print(f"An unexpected error occurred during Google Search for '{query}': {e}")
            return None, "An unexpected server error occurred during the search."
            
    return all_results, None

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

# --- Main Flask Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search-page')
def search_page():
    return render_template('search.html', full_width_page=True)

@app.route('/kendra-finder-page')
def kendra_finder_page():
    return render_template('kendra_finder.html', full_width_page=True)

@app.route('/ai-assistant-page')
def ai_assistant_page():
    return render_template('ai_assistant.html', full_width_page=True)

@app.route('/blog-page')
def blog_page():
    return render_template('blog.html', full_width_page=True)

@app.route('/price-comparison-page')
def price_comparison_page():
    return render_template('price_comparison.html', full_width_page=True)

@app.route('/daily-essentials-page')
def daily_essentials_page():
    return render_template('daily_essentials.html', full_width_page=True)

@app.route('/saved-items-page')
def saved_items_page():
    return render_template('save_for_future.html', full_width_page=True)

@app.route('/about-page')
def about_page():
    return render_template('about.html')

@app.route('/price-comparison', methods=['POST'])
def price_comparison():
    medicine_name = request.json.get('medicine_name', '').strip()
    if not medicine_name:
        return jsonify({'error': 'Please enter a medicine name.'}), 400

    try:
        # Use a more generic and effective query
        query = f'buy "{medicine_name}" online price'
        search_results, error = perform_google_search(query, GOOGLE_API_KEY, GOOGLE_CSE_ID, num_results=20)

        if error:
            return jsonify({'error': error}), 500
        
        if not search_results:
            return jsonify({'medicine_name': medicine_name, 'prices': []})

        system_prompt = """
        You are a price extraction expert. From the provided web search results (a JSON list with title, snippet, and link), you must extract up to 10 price listings for the requested medication.
        For each listing, identify the online store (e.g., "1mg", "PharmEasy"), the price, and use the provided 'link' as the URL.

        CRITICAL INSTRUCTIONS:
        - Analyze the 'snippet' and 'title' for price and store information.
        - The 'link' from the input JSON object MUST be used as the 'url' for your output.
        - Prioritize results that are clearly from online pharmacies or major retailers.
        - Ignore informational links (like Wikipedia, health blogs) that are not selling the product directly.
        - If a snippet mentions a price, you MUST extract it.
        - Return a single, raw JSON object with a 'prices' key, which is a list of objects. Each object must have 'store', 'price', and 'url'.

        EXAMPLE INPUT FORMAT YOU WILL RECEIVE:
        [
          {
            "title": "Buy Paracetamol 500mg Online at Best Price - PharmEasy",
            "snippet": "Paracetamol 500mg Tablet - Strip of 15 ... at Rs.15.00. ...",
            "link": "https://pharmeasy.in/online-medicine-order/paracetamol-500mg-15-tablets-12345"
          }
        ]

        EXAMPLE OUTPUT YOU MUST GENERATE:
        {
          "prices": [
            { "store": "PharmEasy", "price": "Rs.15.00 for Strip of 15", "url": "https://pharmeasy.in/online-medicine-order/paracetamol-500mg-15-tablets-12345" }
          ]
        }
        """
        # Pass the structured results to Groq
        user_prompt = f"Extract price information for '{medicine_name}' from the following search results:\n\n{json.dumps(search_results, indent=2)}"
        
        price_data = process_with_groq(system_prompt, user_prompt)

        return jsonify({
            'medicine_name': medicine_name,
            'prices': price_data.get('prices', [])
        })

    except Exception as e:
        print(f"An unexpected server error occurred during price comparison: {e}")
        return jsonify({'error': "An unexpected server error occurred."}), 500

@app.route('/search', methods=['POST'])
def search():
    user_query = request.json.get('medicine_name', '').strip()
    if not user_query:
        return jsonify({'error': 'Please enter a medicine name.'}), 400

    try:
        # --- STAGE 1: Precise Composition Discovery ---
        print("\n--- STAGE 1: Initial AI Analysis & Composition ---")
        composition_context_list, error = perform_google_search(f'"{user_query}" composition ingredients', GOOGLE_API_KEY, GOOGLE_CSE_ID, num_results=5)
        if error:
            print(f"ERROR during composition search: {error}")
            return jsonify({'error': error}), 500

        if not composition_context_list:
            return jsonify({'error': "Could not find any composition information for this drug via web search."}), 404
        
        # Convert list of results to a single string of snippets for the AI
        composition_context_str = " ".join([item.get('snippet', '') for item in composition_context_list])

        stage1_system_prompt = """
        From the user query and web context, your only job is to identify the drug's exact chemical composition.
        Output a single, raw JSON object with one key, 'composition'.
        Example: { "composition": "Paracetamol 500mg" }
        """
        composition_result = process_with_groq(stage1_system_prompt, f"CONTEXT: {composition_context_str}\nUSER QUERY: {user_query}")
        
        composition = composition_result.get("composition")
        if not composition:
            return jsonify({'error': "AI could not determine the drug's composition from the search results."}), 404
        
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
            search_result_list, error = perform_google_search(query, GOOGLE_API_KEY, GOOGLE_CSE_ID)
            if error:
                 print(f"ERROR during super-context search for '{key}': {error}")
                 return jsonify({'error': f"A search error occurred while gathering details for '{key}'. Details: {error}"}), 500
            
            if search_result_list:
                # Convert list of results to a single string of snippets
                search_result_str = " ".join([item.get('snippet', '') for item in search_result_list])
                super_context += search_result_str

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
        print(f"An unexpected server error occurred during search: {e}")
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
        system_prompt = """
        You are a highly knowledgeable and empathetic AI Medical Assistant. Your role is to provide clear, accurate, and well-structured information to users regarding their health and medication questions.

        **CRITICAL INSTRUCTIONS:**
        1.  **Use Markdown for Formatting:** Structure your responses using Markdown for readability. Use headings (`#`, `##`), bullet points (`*` or `-`), and bold text (`**...**`) to organize information.
        2.  **Professional & Empathetic Tone:** Always maintain a professional, yet caring and empathetic tone.
        3.  **Comprehensive Answers:** Provide detailed and thorough answers. If a user asks about a medication, cover its uses, common side effects, and important warnings. If it's a general health query, provide actionable advice.
        4.  **Safety First (Disclaimer):** ALWAYS end your response with the following disclaimer, formatted exactly as below:
        
        ---
        
        ***Disclaimer:** This information is for educational purposes only and is not a substitute for professional medical advice. Always consult with a qualified healthcare provider for any health concerns or before making any decisions related to your health or treatment.*
        """
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