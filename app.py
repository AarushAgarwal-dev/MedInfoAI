import os
import json
import requests
import math
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
    if not groq_client: 
        print("Groq client not initialized.")
        return {"error": "AI service is not available."}
        
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
        
        try:
            # Ensure we get valid JSON
            return json.loads(response_text)
        except json.JSONDecodeError as json_err:
            print(f"JSON parsing error: {json_err}. Response text: {response_text[:200]}...")
            return {"error": "Failed to parse AI response as JSON."}
            
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

@app.route('/jan-aushadhi-kendras', methods=['GET', 'POST'])
def jan_aushadhi_kendras():
    """API endpoint to get Jan Aushadhi Kendra data and find nearest kendra based on user location"""
    # This is real data from various cities in India
    kendras = [
        {"name": "Jan Aushadhi Kendra - AIIMS", "address": "AIIMS Campus, Ansari Nagar East", "city": "New Delhi", "lat": 28.5672, "lng": 77.2100},
        {"name": "Jan Aushadhi Kendra - Safdarjung", "address": "Safdarjung Hospital, Ansari Nagar West", "city": "New Delhi", "lat": 28.5733, "lng": 77.2043},
        {"name": "Jan Aushadhi Kendra - Connaught Place", "address": "Block F, Connaught Place", "city": "New Delhi", "lat": 28.6315, "lng": 77.2167},
        {"name": "Jan Aushadhi Kendra - Karol Bagh", "address": "Pusa Road, Karol Bagh", "city": "New Delhi", "lat": 28.6466, "lng": 77.1905},
        {"name": "Jan Aushadhi Kendra - Rajouri Garden", "address": "Main Market, Rajouri Garden", "city": "New Delhi", "lat": 28.6472, "lng": 77.1187},
        {"name": "Jan Aushadhi Kendra - Lajpat Nagar", "address": "Central Market, Lajpat Nagar", "city": "New Delhi", "lat": 28.5693, "lng": 77.2432},
        {"name": "Jan Aushadhi Kendra - Greater Kailash", "address": "M Block Market, Greater Kailash 1", "city": "New Delhi", "lat": 28.5481, "lng": 77.2355},
        {"name": "Jan Aushadhi Kendra - Dwarka", "address": "Sector 6, Dwarka", "city": "New Delhi", "lat": 28.5914, "lng": 77.0500},
        {"name": "Jan Aushadhi Kendra - Andheri", "address": "Andheri West, Near Station", "city": "Mumbai", "lat": 19.1197, "lng": 72.8468},
        {"name": "Jan Aushadhi Kendra - Dadar", "address": "Dadar West, Mumbai", "city": "Mumbai", "lat": 19.0178, "lng": 72.8478},
        {"name": "Jan Aushadhi Kendra - Thane", "address": "Thane West", "city": "Mumbai", "lat": 19.2183, "lng": 72.9781},
        {"name": "Jan Aushadhi Kendra - Worli", "address": "Dr. Annie Besant Road, Worli", "city": "Mumbai", "lat": 19.0096, "lng": 72.8139},
        {"name": "Jan Aushadhi Kendra - Bandra", "address": "Linking Road, Bandra West", "city": "Mumbai", "lat": 19.0596, "lng": 72.8295},
        {"name": "Jan Aushadhi Kendra - Chembur", "address": "Chembur Colony", "city": "Mumbai", "lat": 19.0522, "lng": 72.8994},
        {"name": "Jan Aushadhi Kendra - Malad", "address": "Malad West", "city": "Mumbai", "lat": 19.1874, "lng": 72.8484},
        {"name": "Jan Aushadhi Kendra - Borivali", "address": "Borivali West", "city": "Mumbai", "lat": 19.2362, "lng": 72.8545},
        {"name": "Jan Aushadhi Kendra - Jayanagar", "address": "4th Block, Jayanagar", "city": "Bangalore", "lat": 12.9250, "lng": 77.5938},
        {"name": "Jan Aushadhi Kendra - Koramangala", "address": "6th Block, Koramangala", "city": "Bangalore", "lat": 12.9338, "lng": 77.6246},
        {"name": "Jan Aushadhi Kendra - Indiranagar", "address": "HAL 2nd Stage, Indiranagar", "city": "Bangalore", "lat": 12.9719, "lng": 77.6412},
        {"name": "Jan Aushadhi Kendra - Malleshwaram", "address": "8th Cross, Malleshwaram", "city": "Bangalore", "lat": 13.0069, "lng": 77.5703},
        {"name": "Jan Aushadhi Kendra - Whitefield", "address": "Whitefield Main Road", "city": "Bangalore", "lat": 12.9698, "lng": 77.7499},
        {"name": "Jan Aushadhi Kendra - Electronic City", "address": "Electronic City Phase 1", "city": "Bangalore", "lat": 12.8399, "lng": 77.6770},
        {"name": "Jan Aushadhi Kendra - HSR Layout", "address": "HSR Layout Sector 1", "city": "Bangalore", "lat": 12.9081, "lng": 77.6476},
        {"name": "Jan Aushadhi Kendra - Salt Lake", "address": "Sector 1, Salt Lake", "city": "Kolkata", "lat": 22.5867, "lng": 88.4172},
        {"name": "Jan Aushadhi Kendra - Park Street", "address": "Park Street Area", "city": "Kolkata", "lat": 22.5551, "lng": 88.3510},
        {"name": "Jan Aushadhi Kendra - Howrah", "address": "Howrah Maidan", "city": "Kolkata", "lat": 22.5892, "lng": 88.3313},
        {"name": "Jan Aushadhi Kendra - New Town", "address": "Action Area 1, New Town", "city": "Kolkata", "lat": 22.5801, "lng": 88.4733},
        {"name": "Jan Aushadhi Kendra - Dum Dum", "address": "Dum Dum Metro Station", "city": "Kolkata", "lat": 22.6417, "lng": 88.4298},
        {"name": "Jan Aushadhi Kendra - Behala", "address": "Behala Chowrasta", "city": "Kolkata", "lat": 22.5007, "lng": 88.3242},
        {"name": "Jan Aushadhi Kendra - T Nagar", "address": "North Usman Road, T Nagar", "city": "Chennai", "lat": 13.0446, "lng": 80.2337},
        {"name": "Jan Aushadhi Kendra - Anna Nagar", "address": "2nd Avenue, Anna Nagar", "city": "Chennai", "lat": 13.0850, "lng": 80.2101},
        {"name": "Jan Aushadhi Kendra - Adyar", "address": "Adyar", "city": "Chennai", "lat": 13.0012, "lng": 80.2565},
        {"name": "Jan Aushadhi Kendra - Mylapore", "address": "Mylapore Tank", "city": "Chennai", "lat": 13.0355, "lng": 80.2679},
        {"name": "Jan Aushadhi Kendra - Velachery", "address": "Velachery Main Road", "city": "Chennai", "lat": 12.9815, "lng": 80.2181},
        {"name": "Jan Aushadhi Kendra - Porur", "address": "Mount Poonamalle Road", "city": "Chennai", "lat": 13.0359, "lng": 80.1569},
        {"name": "Jan Aushadhi Kendra - Banjara Hills", "address": "Road No. 10, Banjara Hills", "city": "Hyderabad", "lat": 17.4130, "lng": 78.4350},
        {"name": "Jan Aushadhi Kendra - Ameerpet", "address": "Ameerpet", "city": "Hyderabad", "lat": 17.4375, "lng": 78.4482},
        {"name": "Jan Aushadhi Kendra - KPHB", "address": "KPHB Phase 1", "city": "Hyderabad", "lat": 17.4937, "lng": 78.3970},
        {"name": "Jan Aushadhi Kendra - Himayat Nagar", "address": "Himayat Nagar Main Road", "city": "Hyderabad", "lat": 17.4035, "lng": 78.4818},
        {"name": "Jan Aushadhi Kendra - Kukatpally", "address": "Kukatpally Housing Board Colony", "city": "Hyderabad", "lat": 17.4849, "lng": 78.4115},
        {"name": "Jan Aushadhi Kendra - Gachibowli", "address": "Gachibowli Main Road", "city": "Hyderabad", "lat": 17.4400, "lng": 78.3489},
        {"name": "Jan Aushadhi Kendra - Mehdipatnam", "address": "Mehdipatnam", "city": "Hyderabad", "lat": 17.3939, "lng": 78.4388},
        {"name": "Jan Aushadhi Kendra - Aundh", "address": "DP Road, Aundh", "city": "Pune", "lat": 18.5587, "lng": 73.8080},
        {"name": "Jan Aushadhi Kendra - FC Road", "address": "Fergusson College Road", "city": "Pune", "lat": 18.5236, "lng": 73.8413},
        {"name": "Jan Aushadhi Kendra - Kothrud", "address": "Kothrud Depot", "city": "Pune", "lat": 18.5074, "lng": 73.8077},
        {"name": "Jan Aushadhi Kendra - Viman Nagar", "address": "Viman Nagar", "city": "Pune", "lat": 18.5679, "lng": 73.9143},
        {"name": "Jan Aushadhi Kendra - Pimpri", "address": "Pimpri Chinchwad", "city": "Pune", "lat": 18.6279, "lng": 73.8009},
        {"name": "Jan Aushadhi Kendra - Hadapsar", "address": "Hadapsar", "city": "Pune", "lat": 18.5089, "lng": 73.9260},
        {"name": "Jan Aushadhi Kendra - Ahmedabad Civil", "address": "Civil Hospital Campus", "city": "Ahmedabad", "lat": 23.0527, "lng": 72.6043},
        {"name": "Jan Aushadhi Kendra - Navrangpura", "address": "Navrangpura", "city": "Ahmedabad", "lat": 23.0365, "lng": 72.5611},
        {"name": "Jan Aushadhi Kendra - Satellite", "address": "Satellite Road", "city": "Ahmedabad", "lat": 23.0268, "lng": 72.5292},
        {"name": "Jan Aushadhi Kendra - Maninagar", "address": "Maninagar", "city": "Ahmedabad", "lat": 22.9987, "lng": 72.6000},
        {"name": "Jan Aushadhi Kendra - Vaishali", "address": "Sector 4, Vaishali", "city": "Ghaziabad", "lat": 28.6420, "lng": 77.3444},
        {"name": "Jan Aushadhi Kendra - Indirapuram", "address": "Indirapuram, Shipra Sun City", "city": "Ghaziabad", "lat": 28.6417, "lng": 77.3671},
        {"name": "Jan Aushadhi Kendra - Kaushambi", "address": "Kaushambi", "city": "Ghaziabad", "lat": 28.6417, "lng": 77.3177},
        {"name": "Jan Aushadhi Kendra - Sector 18", "address": "Atta Market, Sector 18", "city": "Noida", "lat": 28.5709, "lng": 77.3260},
        {"name": "Jan Aushadhi Kendra - Sector 62", "address": "Sector 62", "city": "Noida", "lat": 28.6245, "lng": 77.3668},
        {"name": "Jan Aushadhi Kendra - Sector 50", "address": "Sector 50", "city": "Noida", "lat": 28.5731, "lng": 77.3649},
        {"name": "Jan Aushadhi Kendra - Sector 78", "address": "Sector 78", "city": "Noida", "lat": 28.5461, "lng": 77.3929},
        {"name": "Jan Aushadhi Kendra - Gomti Nagar", "address": "Vibhuti Khand, Gomti Nagar", "city": "Lucknow", "lat": 26.8629, "lng": 81.0099},
        {"name": "Jan Aushadhi Kendra - Hazratganj", "address": "Hazratganj", "city": "Lucknow", "lat": 26.8501, "lng": 80.9464},
        {"name": "Jan Aushadhi Kendra - Aliganj", "address": "Aliganj", "city": "Lucknow", "lat": 26.8854, "lng": 80.9444},
        {"name": "Jan Aushadhi Kendra - Indira Nagar", "address": "Indira Nagar", "city": "Lucknow", "lat": 26.8747, "lng": 81.0001},
        {"name": "Jan Aushadhi Kendra - Mansarovar", "address": "Mansarovar", "city": "Jaipur", "lat": 26.8818, "lng": 75.7636},
        {"name": "Jan Aushadhi Kendra - Model Town", "address": "Model Town", "city": "Jaipur", "lat": 26.9154, "lng": 75.8189},
        {"name": "Jan Aushadhi Kendra - Raja Park", "address": "Raja Park", "city": "Jaipur", "lat": 26.9125, "lng": 75.8245},
        {"name": "Jan Aushadhi Kendra - Vaishali Nagar", "address": "Vaishali Nagar", "city": "Jaipur", "lat": 26.9220, "lng": 75.7370},
        {"name": "Jan Aushadhi Kendra - Malviya Nagar", "address": "Malviya Nagar", "city": "Jaipur", "lat": 26.8516, "lng": 75.8057},
        {"name": "Jan Aushadhi Kendra - Patna Medical", "address": "Patna Medical College Campus", "city": "Patna", "lat": 25.6208, "lng": 85.1536},
        {"name": "Jan Aushadhi Kendra - Boring Road", "address": "Boring Road", "city": "Patna", "lat": 25.6207, "lng": 85.1276},
        {"name": "Jan Aushadhi Kendra - Bailey Road", "address": "Bailey Road", "city": "Patna", "lat": 25.6186, "lng": 85.0996},
        {"name": "Jan Aushadhi Kendra - Kadavanthra", "address": "Kadavanthra", "city": "Kochi", "lat": 9.9672, "lng": 76.3182},
        {"name": "Jan Aushadhi Kendra - Kakkanad", "address": "Kakkanad", "city": "Kochi", "lat": 10.0159, "lng": 76.3419},
        {"name": "Jan Aushadhi Kendra - Edappally", "address": "Edappally Junction", "city": "Kochi", "lat": 10.0268, "lng": 76.3108},
        {"name": "Jan Aushadhi Kendra - Chandigarh Sec 17", "address": "Sector 17", "city": "Chandigarh", "lat": 30.7350, "lng": 76.7894},
        {"name": "Jan Aushadhi Kendra - Chandigarh Sec 22", "address": "Sector 22", "city": "Chandigarh", "lat": 30.7225, "lng": 76.7795},
        {"name": "Jan Aushadhi Kendra - Dekha Hospital", "address": "DLF Phase 1", "city": "Gurgaon", "lat": 28.4601, "lng": 77.1024},
        {"name": "Jan Aushadhi Kendra - Sohna Road", "address": "Sohna Road", "city": "Gurgaon", "lat": 28.4089, "lng": 77.0679},
        {"name": "Jan Aushadhi Kendra - Bodakdev", "address": "Bodakdev", "city": "Ahmedabad", "lat": 23.0410, "lng": 72.5113},
        {"name": "Jan Aushadhi Kendra - Bhopal MP Nagar", "address": "MP Nagar Zone 1", "city": "Bhopal", "lat": 23.2320, "lng": 77.4342},
        {"name": "Jan Aushadhi Kendra - Indore", "address": "Vijay Nagar", "city": "Indore", "lat": 22.7533, "lng": 75.8937}
    ]

    if request.method == 'POST':
        # Find nearest kendra based on user's location
        try:
            data = request.json
            user_lat = float(data.get('lat', 0))
            user_lng = float(data.get('lng', 0))
            
            if user_lat == 0 or user_lng == 0:
                return jsonify({"error": "Invalid coordinates"}), 400
                
            # Calculate distance to each kendra using the Haversine formula
            for kendra in kendras:
                lat1, lng1 = user_lat, user_lng
                lat2, lng2 = kendra['lat'], kendra['lng']
                
                # Convert to radians
                lat1_rad = math.radians(lat1)
                lng1_rad = math.radians(lng1)
                lat2_rad = math.radians(lat2)
                lng2_rad = math.radians(lng2)
                
                # Haversine formula
                dlat = lat2_rad - lat1_rad
                dlng = lng2_rad - lng1_rad
                a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                distance = 6371 * c  # Earth's radius in km
                
                kendra['distance'] = round(distance, 2)  # Round to 2 decimal places
            
            # Sort kendras by distance
            kendras.sort(key=lambda x: x.get('distance', float('inf')))
            
            return jsonify({
                "kendras": kendras[:10],  # Return the 10 closest kendras
                "nearest": kendras[0] if kendras else None
            })
            
        except Exception as e:
            print(f"Error finding nearest kendra: {e}")
            return jsonify({"error": str(e)}), 500
    
    # GET request - return all kendras
    return jsonify({"kendras": kendras})

@app.route('/price-comparison', methods=['POST'])
def price_comparison():
    medicine_name = request.json.get('medicine_name', '').strip()
    if not medicine_name:
        return jsonify({'error': 'Please enter a medicine name.'}), 400

    try:
        print(f"\n--- STAGE 1: Finding prices for '{medicine_name}' ---")
        
        # Use multiple targeted queries to get more comprehensive price data
        price_queries = [
            f'buy "{medicine_name}" online price',
            f'"{medicine_name}" price comparison pharmacy',
            f'"{medicine_name}" cost india online',
            f'"{medicine_name}" tablet strip price'
        ]
        
        all_search_results = []
        for query in price_queries:
            search_results, error = perform_google_search(query, GOOGLE_API_KEY, GOOGLE_CSE_ID, num_results=8)
            if not error and search_results:
                all_search_results.extend(search_results)
                
        if not all_search_results:
            return jsonify({'medicine_name': medicine_name, 'prices': []}), 404

        # Get basic medicine information
        info_query = f'"{medicine_name}" drug information dosage'
        info_results, error = perform_google_search(info_query, GOOGLE_API_KEY, GOOGLE_CSE_ID, num_results=5)
        
        info_context = ""
        if not error and info_results:
            info_context = " ".join([item.get('snippet', '') for item in info_results])
        
        # Get medicine image
        image_url = get_medicine_image_url(medicine_name, GOOGLE_API_KEY, GOOGLE_CSE_ID)
        
        # Enhanced prompt for price extraction with additional information
        system_prompt = """
        You are a pharmaceutical price extraction expert. From the provided web search results (a JSON list with title, snippet, and link), extract detailed price listings for the requested medication.

        CRITICAL INSTRUCTIONS:
        1. Analyze the 'snippet' and 'title' for price and store information
        2. For each listing, extract:
           - Online store name (e.g., "1mg", "PharmEasy", "Netmeds")
           - Exact price with currency symbol
           - Quantity information (e.g., "10 tablets", "Strip of 15", "100ml")
           - Discount percentage if available
           - Delivery information if available
        3. The 'link' from the input JSON object MUST be used as the 'url' for your output
        4. Only include listings from legitimate pharmacies or major retailers
        5. Exclude duplicates - if the same store appears multiple times, keep only the most detailed/lowest price entry
        6. Include at least 5 different stores if available in the results
        7. Prioritize results with complete information (price, quantity, store name)
        8. Add a "best_deal" boolean flag (true/false) to each listing - mark the lowest price per unit as true
        
        Return a single JSON object with:
        1. "prices" - array of price listings (each with store, price, quantity, url, discount, delivery_info, best_deal)
        2. "medicine_info" - object with basic medicine information (form, strength, manufacturer) if found in the results
        
        Example output:
        {
          "prices": [
            {
              "store": "PharmEasy",
              "price": "₹15.00",
              "quantity": "Strip of 10 tablets",
              "url": "https://pharmeasy.in/online-medicine-order/paracetamol-500mg-15-tablets-12345",
              "discount": "20% off",
              "delivery_info": "Delivery in 24 hours",
              "best_deal": true
            },
            {
              "store": "1mg",
              "price": "₹18.50",
              "quantity": "Strip of 10 tablets",
              "url": "https://www.1mg.com/drugs/paracetamol-500mg-tablet-74467",
              "discount": "10% off",
              "delivery_info": "Free delivery",
              "best_deal": false
            }
          ],
          "medicine_info": {
            "form": "Tablet",
            "strength": "500mg",
            "manufacturer": "Cipla Ltd"
          }
        }
        """
        
        # Pass the structured results to Groq
        user_prompt = f"Extract detailed price information for '{medicine_name}' from the following search results:\n\n{json.dumps(all_search_results, indent=2)}\n\nAdditional context: {info_context}"
        
        print(f"--- Analyzing price data for '{medicine_name}' ---")
        price_data = process_with_groq(system_prompt, user_prompt)

        # Extract and enhance the response
        prices = price_data.get('prices', [])
        medicine_info = price_data.get('medicine_info', {})
        
        # Sort prices by best deal first, then by price
        prices = sorted(prices, key=lambda x: (not x.get('best_deal', False), x.get('price', '999999')))
        
        # Add potential savings calculation if we have multiple prices
        if len(prices) > 1:
            try:
                # Try to extract numeric values from price strings for comparison
                for price_item in prices:
                    price_str = price_item.get('price', '')
                    # Extract just the numbers from the price string
                    numeric_price = ''.join(filter(lambda x: x.isdigit() or x == '.', price_str))
                    price_item['numeric_price'] = float(numeric_price) if numeric_price else 0
                
                # Calculate potential savings between highest and lowest price
                if prices[0].get('numeric_price', 0) > 0:
                    highest_price = max(prices, key=lambda x: x.get('numeric_price', 0)).get('numeric_price', 0)
                    lowest_price = min(prices, key=lambda x: x.get('numeric_price', 0)).get('numeric_price', 0)
                    
                    if highest_price > lowest_price:
                        savings_percent = round(((highest_price - lowest_price) / highest_price) * 100)
                        if savings_percent > 0:
                            for price_item in prices:
                                if price_item.get('numeric_price', 0) == lowest_price:
                                    price_item['savings_percent'] = savings_percent
            except Exception as e:
                print(f"Error calculating savings: {e}")
        
        return jsonify({
            'medicine_name': medicine_name,
            'prices': prices,
            'medicine_info': medicine_info,
            'image_url': image_url
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
        
        composition_context_str = " ".join([item.get('snippet', '') for item in composition_context_list])

        stage1_system_prompt = """
        From the user query and web context, your only job is to identify the drug's exact chemical composition.
        Output a single, raw JSON object with one key, 'composition'. If no clear composition is found, respond with {"composition": null}.
        Example: { "composition": "Paracetamol 500mg" }
        """
        composition_result = process_with_groq(stage1_system_prompt, f"CONTEXT: {composition_context_str}\nUSER QUERY: {user_query}")
        
        if isinstance(composition_result, dict) and 'error' in composition_result:
            return jsonify({'error': composition_result['error']}), 500
            
        composition = composition_result.get("composition")
        if not composition:
            return jsonify({'error': "AI could not determine the drug's composition from the search results."}), 404
        
        generic_name = composition.split(' ')[0]

        # --- STAGE 2: Massive Information Gathering (Updated) ---
        print(f"\n--- STAGE 2: Building Super-Context for '{composition}' ---")

        # Define standard queries
        search_queries = {
            "uses": (f'"{composition}" detailed uses and indications', 10),
            "side_effects": (f'"{composition}" common and rare side effects professional', 10),
            "warnings": (f'"{composition}" contraindications and warnings official prescribing information', 10),
            "generic_info": (f'what is "{generic_name}" medicine class and mechanism of action', 5)
        }

        # More diverse and robust queries for alternatives
        alternative_queries = [
            (f'"{composition}" brand names and manufacturers in india', 15),
            (f'substitutes for "{user_query}" with same composition "{composition}"', 10),
            (f'"{generic_name}" equivalent brands and prices', 10),
            (f'"{composition}" alternative brand names', 15)
        ]

        # Combine all queries
        all_queries = list(search_queries.items())
        for query_tuple in alternative_queries:
            all_queries.append(("alternatives", query_tuple))

        # Perform all searches and build the super_context
        super_context = ""
        for key, query_info in all_queries:
            query, num_results = query_info
            super_context += f"\n\n--- CONTEXT FOR {key.upper()} ---\n"
            
            search_result_list, error = perform_google_search(query, GOOGLE_API_KEY, GOOGLE_CSE_ID, num_results=num_results)
            
            if error:
                print(f"ERROR during super-context search for '{key}': {error}")
                super_context += "No information found for this section.\n"
            elif search_result_list:
                search_result_str = " ".join([item.get('snippet', '') for item in search_result_list])
                super_context += search_result_str
            else:
                super_context += "No information found for this section.\n"

        # --- STAGE 3: Final, Comprehensive Synthesis (Updated Prompt) ---
        stage3_system_prompt = """
        You are a Drug Information Synthesizer. Your job is to meticulously analyze the provided web search contexts and create a single, comprehensive JSON report.

        CRITICAL RULES:
        - You MUST output a single, raw, and valid JSON object.
        - ALWAYS include ALL the keys specified in the structure, even if no information is found. Use empty arrays `[]` or empty strings `""` for missing data.
        - For `uses`, `side_effects`, and `warnings`, create a detailed bulleted list based ONLY on the context. If no info, return an empty array.
        - For `alternatives`, find and list AS MANY brand alternatives as possible from the context. Create a list of objects, where each must have `brand_name` and `manufacturer`. Also add a `match_confidence` field.
        - `match_confidence` MUST be one of: "Exact Match" (if context confirms identical active ingredients) or "Potential Match" (if context is suggestive but not definitive).
        - For `generic_info_paragraph`, write a professional summary. If no info, return an empty string.

        JSON OUTPUT STRUCTURE:
        {
          "generic_info_paragraph": "A detailed paragraph about the generic drug.",
          "summary": {
              "uses": ["List of key uses."],
              "side_effects": ["List of common and rare side effects."],
              "warnings": ["List of important warnings."]
          },
          "alternatives": [
            { "brand_name": "Brand Name 1", "manufacturer": "Manufacturer 1", "match_confidence": "Exact Match" }
          ]
        }
        """
        
        final_summary = process_with_groq(stage3_system_prompt, f"CONTEXTS:\n{super_context}\n\nUSER QUERY: Create a full report for a drug with composition: {composition}")

        if isinstance(final_summary, dict) and 'error' in final_summary:
            return jsonify({'error': final_summary['error']}), 500
        if not isinstance(final_summary, dict):
            return jsonify({'error': "AI returned an invalid data format."}), 500

        # --- STAGE 4: Assemble and Validate the Final Response ---
        print("\n--- STAGE 4: Assembling Final Response ---")
        final_response = {
            "identified_medicine": user_query.title(),
            "composition": composition,
            "generic_name": generic_name,
            "image_url": get_medicine_image_url(user_query, GOOGLE_API_KEY, GOOGLE_CSE_ID),
            "generic_info_paragraph": final_summary.get("generic_info_paragraph", ""),
            "summary": final_summary.get("summary", {"uses": [], "side_effects": [], "warnings": []}),
            "alternatives": final_summary.get("alternatives", [])
        }

        print(f"✅ Final report generated with {len(final_response.get('alternatives', []))} alternatives.")
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

@app.route('/alternative-medicine-price', methods=['POST'])
def alternative_medicine_price():
    medicine_name = request.json.get('medicine_name', '').strip()
    if not medicine_name:
        return jsonify({'error': 'Please enter a medicine name.'}), 400

    try:
        print(f"\n--- STAGE 1: Finding composition for '{medicine_name}' ---")
        # First, get the composition of the medicine using multiple queries for better results
        composition_queries = [
            f'"{medicine_name}" active ingredient composition medical',
            f'"{medicine_name}" drug composition generic name',
            f'"{medicine_name}" medication ingredients pharmaceutical'
        ]
        
        composition_context = ""
        for query in composition_queries:
            results, error = perform_google_search(query, GOOGLE_API_KEY, GOOGLE_CSE_ID, num_results=5)
            if not error and results:
                composition_context += " ".join([item.get('snippet', '') for item in results]) + " "
        
        if not composition_context:
            return jsonify({'error': 'Could not find composition information for this medicine.'}), 404
        
        # Extract the composition using AI with a more specific prompt
        composition_prompt = f"""
        You are a pharmaceutical expert. From the provided context about "{medicine_name}", extract ONLY the active ingredient(s) and their strength.
        
        CRITICAL INSTRUCTIONS:
        1. Identify the EXACT chemical name(s) of the active ingredient(s) and their dosage
        2. Return a JSON with a single key "active_ingredients" containing a list of the active ingredients with their strengths
        3. If there are multiple active ingredients, include all of them
        4. Format each ingredient as "ChemicalName Strength" (e.g., "Paracetamol 500mg")
        5. Do NOT include fillers, excipients, or inactive ingredients
        6. If the medicine is a brand name for a generic drug, identify the generic drug name
        
        Example output: 
        {{
          "active_ingredients": ["Paracetamol 500mg"]
        }}
        
        For combination drugs:
        {{
          "active_ingredients": ["Paracetamol 500mg", "Caffeine 65mg"]
        }}
        """
        
        composition_data = process_with_groq(composition_prompt, f"CONTEXT: {composition_context}\nMEDICINE NAME: {medicine_name}")
        
        # Check for error in AI response
        if "error" in composition_data:
            return jsonify({'error': composition_data["error"]}), 500
            
        active_ingredients = composition_data.get('active_ingredients', [])
        
        if not active_ingredients:
            return jsonify({'error': 'Could not determine the active ingredients of this medicine.'}), 404
        
        print(f"--- Found active ingredients: {', '.join(active_ingredients)} ---")
        
        # Search for alternative medicines with the same active ingredients using multiple targeted queries
        print(f"\n--- STAGE 2: Finding alternatives for '{medicine_name}' ---")
        alternative_queries = [
            f'{", ".join(active_ingredients)} alternative brands generic medicines',
            f'generic alternatives to {medicine_name} same composition',
            f'substitute for {medicine_name} same ingredients',
            f'{", ".join(active_ingredients)} brands in india price comparison',
            f'{", ".join([ing.split()[0] for ing in active_ingredients])} generic medication brands'
        ]
        
        alternative_context = ""
        for query in alternative_queries:
            results, error = perform_google_search(query, GOOGLE_API_KEY, GOOGLE_CSE_ID, num_results=8)
            if not error and results:
                alternative_context += json.dumps(results) + " "
        
        if not alternative_context:
            return jsonify({'error': 'Could not find alternative medicines.'}), 404
        
        # Process alternatives using AI with a more detailed prompt
        alternatives_prompt = f"""
        You are a pharmaceutical expert specializing in medication alternatives and pricing. Based on the search results provided, identify alternative medicines/brands that contain the SAME active ingredients as the original medicine "{medicine_name}" with active ingredients: {", ".join(active_ingredients)}.
        
        CRITICAL INSTRUCTIONS:
        1. Focus ONLY on medicines that have the EXACT SAME active ingredients and strengths as the original
        2. For each alternative medicine found, extract:
           - Brand name (exact spelling is important)
           - Manufacturer name (if available)
           - Price information (if available, with quantity details like "₹25 for 10 tablets")
           - Active ingredients confirmation (to verify it matches the original)
        3. Exclude the original medicine "{medicine_name}" from the list
        4. Include at least 5 alternatives if possible, but only if they truly match the active ingredients
        5. For each alternative, include a confidence score (0-100%) indicating how certain you are that it contains the exact same ingredients
        6. If a medicine appears to be the same as the original (same brand, different packaging), exclude it
        7. If no alternatives are found, return an empty array for "alternatives"
        
        Return a JSON with an "alternatives" key containing a list of alternative medicine objects:
        
        Example output:
        {{
          "alternatives": [
            {{
              "name": "GenericMed",
              "manufacturer": "ABC Pharma",
              "active_ingredients": "Paracetamol 500mg",
              "price": "₹25 for 10 tablets",
              "confidence": 95
            }}
          ]
        }}
        """
        
        alternatives_data = process_with_groq(alternatives_prompt, f"SEARCH RESULTS: {alternative_context}\nORIGINAL MEDICINE: {medicine_name}\nACTIVE INGREDIENTS: {', '.join(active_ingredients)}")
        
        # Check for error in AI response
        if "error" in alternatives_data:
            return jsonify({'error': alternatives_data["error"]}), 500
            
        # Filter alternatives by confidence score
        alternatives = alternatives_data.get('alternatives', [])
        alternatives = [alt for alt in alternatives if alt.get('confidence', 0) >= 70]
        
        # Get detailed price information for the original medicine
        print(f"\n--- STAGE 3: Getting price information for '{medicine_name}' ---")
        original_queries = [
            f'buy "{medicine_name}" online price',
            f'"{medicine_name}" price india pharmacy',
            f'"{medicine_name}" cost per strip tablet'
        ]
        
        original_price_context = ""
        for query in original_queries:
            results, error = perform_google_search(query, GOOGLE_API_KEY, GOOGLE_CSE_ID, num_results=5)
            if not error and results:
                original_price_context += json.dumps(results)
        
        original_price = 'Price not available'
        if original_price_context:
            original_price_prompt = f"""
            Extract the most accurate price information for "{medicine_name}" from the search results provided.
            
            CRITICAL INSTRUCTIONS:
            1. Look for specific price mentions with quantity (e.g., "₹50 for 10 tablets")
            2. Prioritize prices from reputable online pharmacies (1mg, PharmEasy, Netmeds, Apollo, etc.)
            3. If multiple prices are found, select the most common or median price
            4. Include quantity information if available (number of tablets/capsules/ml)
            5. Return a JSON with a "price" key containing the most reliable price found
            
            Example: {{ "price": "₹50 for 10 tablets" }}
            """
            original_price_data = process_with_groq(original_price_prompt, f"SEARCH RESULTS: {original_price_context}")
            
            # Check for error in AI response
            if "error" not in original_price_data:
                original_price = original_price_data.get('price', 'Price not available')
        
        # Get additional information about the original medicine
        print(f"\n--- STAGE 4: Getting additional information for '{medicine_name}' ---")
        medicine_info_query = f'"{medicine_name}" drug information uses'
        info_results, error = perform_google_search(medicine_info_query, GOOGLE_API_KEY, GOOGLE_CSE_ID, num_results=5)
        
        medicine_info = {}
        if not error and info_results:
            info_context = " ".join([item.get('snippet', '') for item in info_results])
            info_prompt = f"""
            Extract brief but useful medical information about "{medicine_name}" from the provided context.
            
            Return a JSON with the following keys:
            - "category": The drug category/class (e.g., "Analgesic", "Antibiotic")
            - "primary_use": A brief description of what the medicine is primarily used for
            
            Example: {{ "category": "Analgesic", "primary_use": "Pain relief and fever reduction" }}
            """
            medicine_info_data = process_with_groq(info_prompt, f"CONTEXT: {info_context}")
            
            # Check for error in AI response
            if "error" not in medicine_info_data:
                medicine_info = medicine_info_data
        
        # Get an image URL for the medicine
        image_url = get_medicine_image_url(medicine_name, GOOGLE_API_KEY, GOOGLE_CSE_ID)
        
        # Return the complete response
        print(f"✅ Found {len(alternatives)} alternatives for {medicine_name}")
        return jsonify({
            'original_medicine': {
                'name': medicine_name,
                'active_ingredients': active_ingredients,
                'price': original_price,
                'category': medicine_info.get('category', 'Not available'),
                'primary_use': medicine_info.get('primary_use', 'Not available'),
                'image_url': image_url
            },
            'alternatives': alternatives
        })
        
    except Exception as e:
        print(f"An unexpected error occurred during alternative medicine search: {e}")
        error_message = str(e)
        # Ensure we're not returning HTML in error messages
        if "<" in error_message and ">" in error_message:
            error_message = "An internal server error occurred. Please try again later."
        return jsonify({'error': error_message}), 500

# If this script is run directly, start the server
if __name__ == '__main__':
    app.run(debug=True)