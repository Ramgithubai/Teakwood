"""
Enhanced Streamlit Business Researcher with JustDial Integration
Modified to include justdial_whatsapp_number in business_contacts_*.csv files
"""

import asyncio
import csv
import os
import json
import tempfile
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import openai
from tavily import TavilyClient

# Import JustDial researcher
try:
    from .justdial_researcher import JustDialStreamlitResearcher
    JUSTDIAL_AVAILABLE = True
    print("[INFO] ✅ JustDial researcher loaded successfully")
except ImportError as e:
    JUSTDIAL_AVAILABLE = False
    print(f"[INFO] ⚠️ JustDial researcher not available: {e}")

# Load environment variables
load_dotenv()

class StreamlitBusinessResearcher:
    def __init__(self):
        # Load API keys
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.tavily_key = os.getenv('TAVILY_API_KEY')
        self.groq_key = os.getenv('GROQ_API_KEY')  # For JustDial research
        
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY not found in .env file!")
        if not self.tavily_key:
            raise ValueError("TAVILY_API_KEY not found in .env file!")
        
        # Initialize clients
        self.openai_client = openai.OpenAI(api_key=self.openai_key)
        self.tavily_client = TavilyClient(api_key=self.tavily_key)
        
        self.results = []
        self.justdial_results = {}  # Store JustDial results by business name
    
    def test_apis(self):
        """Test all APIs before starting research"""
        print("🧪 Testing APIs...")
        
        # Test OpenAI
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say 'OpenAI working'"}],
                max_tokens=10
            )
            if response.choices[0].message.content:
                print("✅ OpenAI API: Working")
            else:
                return False, "OpenAI API: Empty response"
                
        except openai.RateLimitError as e:
            error_msg = f"OpenAI API: Rate limit exceeded - {e}"
            print(f"❌ {error_msg}")
            return False, error_msg
        except openai.AuthenticationError as e:
            error_msg = f"OpenAI API: Authentication failed - {e}"
            print(f"❌ {error_msg}")
            return False, error_msg
        except Exception as e:
            error_str = str(e).lower()
            if "billing" in error_str or "quota" in error_str or "insufficient" in error_str:
                error_msg = f"OpenAI API: Billing/Quota Issue - {e}"
                print(f"💳 {error_msg}")
                return False, error_msg
            else:
                error_msg = f"OpenAI API: {e}"
                print(f"❌ {error_msg}")
                return False, error_msg
        
        # Test Tavily
        try:
            response = self.tavily_client.search("test query", max_results=1)
            if response.get('results'):
                print("✅ Tavily API: Working")
            else:
                return False, "Tavily API: No results"
                
        except Exception as e:
            error_str = str(e).lower()
            if "billing" in error_str or "quota" in error_str or "insufficient" in error_str or "limit" in error_str:
                error_msg = f"Tavily API: Billing/Quota Issue - {e}"
                print(f"💳 {error_msg}")
                return False, error_msg
            else:
                error_msg = f"Tavily API: {e}"
                print(f"❌ {error_msg}")
                return False, error_msg
        
        # Test JustDial availability
        if JUSTDIAL_AVAILABLE and self.groq_key:
            print("✅ JustDial API: Available")
        else:
            print("⚠️ JustDial API: Not available")
            
        return True, "All APIs working"
    
    async def research_business_with_justdial(self, business_name, city=""):
        """Enhanced research that combines regular research with JustDial phone extraction"""
        
        print(f"🔍 Enhanced research for: {business_name}")
        
        # Step 1: Regular business research (Tavily + OpenAI)
        regular_result = await self.research_business_direct(business_name)
        
        # Step 2: JustDial research for WhatsApp phone number
        justdial_phone = None
        if JUSTDIAL_AVAILABLE and self.groq_key:
            try:
                print(f"📱 Starting JustDial research for: {business_name}")
                
                # Use JustDial researcher to get phone number
                justdial_researcher = JustDialStreamlitResearcher(
                    groq_api_key=self.groq_key,
                    use_existing_chrome=True,
                    headless=False
                )
                
                justdial_result = justdial_researcher.research_single_business(business_name, city)
                
                if justdial_result and justdial_result.get('status') == 'success':
                    justdial_phone = justdial_result.get('justdial_phone')
                    print(f"✅ JustDial phone found: {justdial_phone}")
                else:
                    print(f"⚠️ JustDial research failed: {justdial_result.get('status', 'unknown')}")
                    justdial_phone = "Not found"
                    
            except Exception as e:
                print(f"❌ JustDial research error: {e}")
                justdial_phone = "Research failed"
        else:
            justdial_phone = "Not available"
            
        # Step 3: Store JustDial result
        self.justdial_results[business_name] = justdial_phone
        
        return regular_result
    
    async def research_business_direct(self, business_name):
        """Research business using Tavily + OpenAI directly"""
        
        print(f"🔍 Researching: {business_name}")
        
        try:
            # Step 1: Search with Tavily
            search_results = self.search_with_tavily(business_name)
            
            if not search_results:
                print(f"❌ No search results found for {business_name}")
                return self.create_manual_fallback(business_name)
            
            # Step 2: Extract contact info using OpenAI
            contact_info = await self.extract_contacts_with_openai(business_name, search_results)
            
            return contact_info
            
        except Exception as e:
            error_str = str(e).lower()
            if "billing" in error_str or "quota" in error_str or "insufficient" in error_str:
                print(f"💳 API Billing Error for {business_name}: {e}")
                return self.create_billing_error_result(business_name)
            else:
                print(f"❌ Error researching {business_name}: {e}")
                return self.create_manual_fallback(business_name)
    
    def search_with_tavily(self, business_name):
        """Search for business information using Tavily API"""
        
        print(f"   🌐 Searching Tavily for: {business_name}")
        
        try:
            # Multiple search queries for better coverage
            search_queries = [
                f"{business_name} contact information phone email",
                f"{business_name} timber wood business address",
                f"{business_name} company website official"
            ]
            
            all_results = []
            
            for query in search_queries:
                print(f"      📝 Query: {query}")
                
                response = self.tavily_client.search(
                    query=query,
                    max_results=3,
                    search_depth="advanced",
                    include_domains=None,
                    exclude_domains=["facebook.com", "twitter.com", "instagram.com"]
                )
                
                if response.get('results'):
                    all_results.extend(response['results'])
                    print(f"      ✅ Found {len(response['results'])} results")
                else:
                    print(f"      ❌ No results for this query")
            
            print(f"   📊 Total search results: {len(all_results)}")
            return all_results
            
        except Exception as e:
            error_str = str(e).lower()
            if "billing" in error_str or "quota" in error_str or "insufficient" in error_str or "limit" in error_str:
                print(f"💳 Tavily Billing Error: {e}")
                raise Exception(f"Tavily API billing issue: {e}")
            else:
                print(f"   ❌ Tavily search error: {e}")
                return []
    
    async def extract_contacts_with_openai(self, business_name, search_results):
        """Use OpenAI to extract contact information"""
        
        print(f"   🤖 Analyzing results with OpenAI...")
        
        # Prepare search results text for OpenAI
        results_text = self.format_search_results(search_results)
        
        prompt = f"""
        Analyze the following web search results for the business "{business_name}" and extract contact information.

        SEARCH RESULTS:
        {results_text}

        Please extract and format the following information:

        BUSINESS_NAME: {business_name}
        PHONE: [extract phone number if found, or "Not found"]
        EMAIL: [extract email address if found, or "Not found"]  
        WEBSITE: [extract official website URL if found, or "Not found"]
        ADDRESS: [extract business address if found, or "Not found"]
        DESCRIPTION: [brief description of business based on search results, or "No description available"]
        CONFIDENCE: [rate 1-10 how confident you are this is the correct business]

        Rules:
        1. Only extract information that is clearly present in the search results
        2. Don't make up or assume any contact details
        3. Prefer official websites over directory listings
        4. If multiple phone numbers found, choose the main business number
        5. If no specific info found, write "Not found" for that field

        Format your response exactly as shown above with the field names.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.1
            )
            
            if response.choices[0].message.content:
                extracted_info = response.choices[0].message.content
                print(f"   ✅ OpenAI extraction completed")
                
                result = {
                    'business_name': business_name,
                    'extracted_info': extracted_info,
                    'raw_search_results': search_results,
                    'research_date': datetime.now().isoformat(),
                    'method': 'Tavily + OpenAI',
                    'status': 'success'
                }
                
                self.results.append(result)
                
                # Display results
                print(f"   📋 Results for {business_name}:")
                print("-" * 50)
                print(extracted_info)
                print("-" * 50)
                
                return result
            else:
                print(f"   ❌ OpenAI returned empty response")
                return self.create_manual_fallback(business_name)
                
        except Exception as e:
            error_str = str(e).lower()
            if "billing" in error_str or "quota" in error_str or "insufficient" in error_str:
                print(f"💳 OpenAI Billing Error: {e}")
                raise Exception(f"OpenAI API billing issue: {e}")
            else:
                print(f"   ❌ OpenAI extraction error: {e}")
                return self.create_manual_fallback(business_name)
    
    def format_search_results(self, search_results):
        """Format Tavily search results for OpenAI analysis"""
        
        formatted_results = []
        
        for i, result in enumerate(search_results[:10], 1):
            formatted_result = f"""
            RESULT {i}:
            Title: {result.get('title', 'No title')}
            URL: {result.get('url', 'No URL')}
            Content: {result.get('content', 'No content')[:500]}...
            """
            formatted_results.append(formatted_result)
        
        return '\n'.join(formatted_results)
    
    def create_manual_fallback(self, business_name):
        """Create fallback result when automated research fails"""
        
        fallback_info = f"""
        BUSINESS_NAME: {business_name}
        PHONE: Research required
        EMAIL: Research required
        WEBSITE: Research required  
        ADDRESS: Research required
        DESCRIPTION: Timber/wood trading business - requires manual verification
        CONFIDENCE: 1

        MANUAL RESEARCH NEEDED:
        1. Google search: "{business_name}" contact information
        2. Check local business directories and Yellow Pages
        3. Search LinkedIn for company profile
        4. Look for timber trade association listings
        5. Check government business registration databases
        """
        
        result = {
            'business_name': business_name,
            'extracted_info': fallback_info,
            'raw_search_results': [],
            'research_date': datetime.now().isoformat(),
            'method': 'Manual Fallback',
            'status': 'manual_required'
        }
        
        self.results.append(result)
        
        print(f"   ⚠️  Manual research required for {business_name}")
        
        return result
    
    def create_billing_error_result(self, business_name):
        """Create result for billing error cases"""
        
        billing_info = f"""
        BUSINESS_NAME: {business_name}
        PHONE: API billing error
        EMAIL: API billing error
        WEBSITE: API billing error  
        ADDRESS: API billing error
        DESCRIPTION: Research stopped due to API billing/quota issue
        CONFIDENCE: 0

        BILLING ERROR OCCURRED:
        Research was stopped due to API billing or quota limits.
        Please resolve billing issues and restart the research process.
        """
        
        result = {
            'business_name': business_name,
            'extracted_info': billing_info,
            'raw_search_results': [],
            'research_date': datetime.now().isoformat(),
            'method': 'Billing Error',
            'status': 'billing_error'
        }
        
        self.results.append(result)
        
        print(f"   💳 Billing error occurred for {business_name}")
        
        return result
    
    async def research_from_dataframe(self, df, consignee_column='Consignee Name', max_businesses=None, enable_justdial=True):
        """Enhanced research businesses from DataFrame with JustDial integration"""
        
        # Extract business names from the specified column
        if consignee_column not in df.columns:
            available_cols = [col for col in df.columns if 'consignee' in col.lower() or 'name' in col.lower()]
            if available_cols:
                consignee_column = available_cols[0]
                print(f"⚠️  Column '{consignee_column}' not found. Using '{consignee_column}' instead.")
            else:
                raise ValueError(f"Column '{consignee_column}' not found in DataFrame. Available columns: {list(df.columns)}")
        
        # Get unique business names
        business_names = df[consignee_column].dropna().unique().tolist()
        business_names = [name.strip() for name in business_names if name.strip()]
        
        if not business_names:
            raise ValueError(f"No business names found in column '{consignee_column}'")
        
        # Limit number of businesses if specified
        if max_businesses and max_businesses < len(business_names):
            business_names = business_names[:max_businesses]
            print(f"🎯 Limited to first {max_businesses} businesses")
        
        total_businesses = len(business_names)
        print(f"📋 Found {total_businesses} unique businesses to research")
        
        # Extract cities from DataFrame if available
        city_column = None
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['city', 'location', 'place', 'address']):
                city_column = col
                break
        
        print(f"🏙️ City column detected: {city_column}")
        
        # Research each business
        successful = 0
        manual_required = 0
        billing_errors = 0
        
        for i, business_name in enumerate(business_names, 1):
            print(f"\n📊 Progress: {i}/{total_businesses}")
            print(f"🏢 Business: {business_name}")
            
            # Get city for this business
            city = ""
            if city_column:
                business_rows = df[df[consignee_column] == business_name]
                if not business_rows.empty:
                    city = business_rows[city_column].iloc[0] if pd.notna(business_rows[city_column].iloc[0]) else ""
            
            try:
                if enable_justdial:
                    result = await self.research_business_with_justdial(business_name, city)
                else:
                    result = await self.research_business_direct(business_name)
                
                if result['status'] == 'success':
                    successful += 1
                elif result['status'] == 'manual_required':
                    manual_required += 1
                elif result['status'] == 'billing_error':
                    billing_errors += 1
                    print("💳 Stopping research due to billing error.")
                    break
                
                # Delay between requests
                await asyncio.sleep(3)
                
            except Exception as e:
                error_str = str(e).lower()
                if "billing" in error_str or "quota" in error_str:
                    print(f"💳 BILLING ERROR: {e}")
                    billing_errors += 1
                    break
                else:
                    print(f"❌ Unexpected error: {e}")
                    manual_required += 1
        
        # Return summary
        summary = {
            'total_processed': len(self.results),
            'successful': successful,
            'manual_required': manual_required,
            'billing_errors': billing_errors,
            'success_rate': successful/len(self.results)*100 if self.results else 0
        }
        
        return summary
    
    def get_results_dataframe(self):
        """Convert results to DataFrame with JustDial integration"""
        
        if not self.results:
            return pd.DataFrame()
        
        csv_data = []
        for result in self.results:
            csv_row = self.parse_extracted_info_to_csv_enhanced(result)
            csv_data.append(csv_row)
        
        return pd.DataFrame(csv_data)
    
    def save_csv_results(self, filename=None):
        """Save enhanced research results to CSV file with JustDial data"""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"business_contacts_{timestamp}.csv"
        
        results_df = self.get_results_dataframe()
        results_df.to_csv(filename, index=False)
        
        print(f"📁 Enhanced results saved to: {filename}")
        return filename
    
    def parse_extracted_info_to_csv_enhanced(self, result):
        """Parse extracted info text into CSV fields with JustDial integration"""
        info = result['extracted_info']
        business_name = result['business_name']
        
        # Get JustDial phone number for this business (renamed to justdial_whatsapp_number)
        justdial_whatsapp_number = self.justdial_results.get(business_name, "Not found")
        
        csv_row = {
            'business_name': business_name,
            'phone': self.extract_field_value(info, 'PHONE:'),
            'email': self.extract_field_value(info, 'EMAIL:'),
            'website': self.extract_field_value(info, 'WEBSITE:'),
            'address': self.extract_field_value(info, 'ADDRESS:'),
            'description': self.extract_field_value(info, 'DESCRIPTION:'),
            'confidence': self.extract_field_value(info, 'CONFIDENCE:'),
            'justdial_whatsapp_number': justdial_whatsapp_number,  # NEW COLUMN (renamed from justdial_phone)
            'status': result['status'],
            'research_date': result['research_date'],
            'method': result['method']
        }
        
        return csv_row
    
    def extract_field_value(self, text, field_name):
        """Extract field value from formatted text"""
        try:
            lines = text.split('\n')
            for line in lines:
                if line.strip().startswith(field_name):
                    value = line.replace(field_name, '').strip()
                    return value if value and value != "Not found" else ""
            return ""
        except:
            return ""

async def research_businesses_from_dataframe(df, consignee_column='Consignee Name', max_businesses=10, enable_justdial=True):
    """
    Enhanced function to research businesses from a DataFrame with JustDial integration
    
    Args:
        df: pandas DataFrame containing business data
        consignee_column: name of column containing business names
        max_businesses: maximum number of businesses to research (default 10)
        enable_justdial: whether to enable JustDial WhatsApp number extraction (default True)
    
    Returns:
        tuple: (results_dataframe, summary_dict, csv_filename)
    """
    
    try:
        researcher = StreamlitBusinessResearcher()
        
        # Test APIs first
        api_ok, api_message = researcher.test_apis()
        if not api_ok:
            raise Exception(f"API Test Failed: {api_message}")
        
        # Research businesses with JustDial integration
        summary = await researcher.research_from_dataframe(
            df, 
            consignee_column=consignee_column, 
            max_businesses=max_businesses,
            enable_justdial=enable_justdial
        )
        
        # Get results with JustDial data
        results_df = researcher.get_results_dataframe()
        
        # Save to CSV with enhanced format
        csv_filename = researcher.save_csv_results()
        
        return results_df, summary, csv_filename
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None, None

# Import enhanced timber business researcher
try:
    from .enhanced_timber_business_researcher import research_timber_businesses_from_dataframe
    print("[INFO] ✅ Enhanced timber business researcher loaded successfully")
except ImportError as e:
    print(f"[INFO] ⚠️ Enhanced timber business researcher not available: {e}")
    # Fallback to regular function
    async def research_timber_businesses_from_dataframe(*args, **kwargs):
        return await research_businesses_from_dataframe(*args, **kwargs)
