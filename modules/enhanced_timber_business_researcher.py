"""
Enhanced Streamlit Business Researcher specifically for Teak Wood & Timber Business
Includes smart filtering, location cross-verification, and industry-specific targeting
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

class EnhancedTimberBusinessResearcher:
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
        self.irrelevant_businesses = []  # Track filtered out businesses
    
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
        
        return True, "All APIs working"
    
    async def research_business_with_location_verification(self, business_name, expected_city="", expected_address=""):
        """Enhanced research with location cross-verification for timber businesses"""
        
        print(f"🌲 Enhanced timber business research for: {business_name}")
        if expected_city:
            print(f"🏙️ Expected location: {expected_city}")
        
        try:
            # Step 1: Search with timber-specific queries
            search_results = self.search_timber_business(business_name, expected_city)
            
            if not search_results:
                print(f"❌ No search results found for {business_name}")
                return self.create_manual_fallback(business_name)
            
            # Step 2: Extract and verify contact info using enhanced AI
            contact_info = await self.extract_timber_business_contacts(business_name, search_results, expected_city, expected_address)
            
            # Step 3: JustDial research for WhatsApp phone number
            await self.get_justdial_contact(business_name, expected_city)
            
            return contact_info
            
        except Exception as e:
            error_str = str(e).lower()
            if "billing" in error_str or "quota" in error_str or "insufficient" in error_str:
                print(f"💳 API Billing Error for {business_name}: {e}")
                return self.create_billing_error_result(business_name)
            else:
                print(f"❌ Error researching {business_name}: {e}")
                return self.create_manual_fallback(business_name)
    
    def search_timber_business(self, business_name, city=""):
        """Search specifically for timber/teak wood businesses with enhanced queries"""
        
        print(f"   🌲 Searching for timber business: {business_name}")
        
        try:
            # Timber-specific search queries with location
            location_part = f" {city}" if city else ""
            
            search_queries = [
                f"{business_name}{location_part} timber wood contact phone email",
                f"{business_name}{location_part} teak wood supplier trader",
                f"{business_name}{location_part} lumber wooden furniture manufacturer",
                f"{business_name}{location_part} forest products timber trading",
                f"{business_name}{location_part} wood processing company address",
                f"{business_name} wooden products supplier contact details"
            ]
            
            all_results = []
            
            for query in search_queries:
                print(f"      🔍 Query: {query}")
                
                response = self.tavily_client.search(
                    query=query,
                    max_results=4,
                    search_depth="advanced",
                    include_domains=None,
                    exclude_domains=[
                        "facebook.com", "twitter.com", "instagram.com", 
                        "youtube.com", "linkedin.com", "pinterest.com"
                    ]
                )
                
                if response.get('results'):
                    # Filter for timber-related content
                    timber_results = self.filter_timber_relevant_results(response['results'])
                    all_results.extend(timber_results)
                    print(f"      ✅ Found {len(timber_results)} timber-relevant results")
                else:
                    print(f"      ❌ No results for this query")
            
            print(f"   📊 Total timber-relevant results: {len(all_results)}")
            return all_results
            
        except Exception as e:
            error_str = str(e).lower()
            if "billing" in error_str or "quota" in error_str or "insufficient" in error_str or "limit" in error_str:
                print(f"💳 Tavily Billing Error: {e}")
                raise Exception(f"Tavily API billing issue: {e}")
            else:
                print(f"   ❌ Tavily search error: {e}")
                return []
    
    def filter_timber_relevant_results(self, results):
        """Filter search results to keep only timber/wood industry relevant ones"""
        
        timber_keywords = [
            'timber', 'teak', 'wood', 'lumber', 'forest', 'wooden', 'hardwood', 'softwood',
            'plywood', 'furniture', 'sawmill', 'log', 'tree', 'plantation', 'forestry',
            'woodwork', 'carpentry', 'joinery', 'board', 'panel', 'veneer', 'export',
            'import', 'trading', 'supplier', 'manufacturer', 'processor'
        ]
        
        irrelevant_keywords = [
            'restaurant', 'hotel', 'food', 'catering', 'textile', 'clothing', 'medicine',
            'pharmacy', 'software', 'technology', 'digital', 'marketing', 'advertising',
            'insurance', 'banking', 'finance', 'real estate', 'construction materials',
            'cement', 'steel', 'metal', 'plastic', 'electronic', 'automotive'
        ]
        
        relevant_results = []
        
        for result in results:
            content = f"{result.get('title', '')} {result.get('content', '')}".lower()
            
            # Check for timber-related keywords
            timber_score = sum(1 for keyword in timber_keywords if keyword in content)
            
            # Check for irrelevant keywords
            irrelevant_score = sum(1 for keyword in irrelevant_keywords if keyword in content)
            
            # Include if timber score is higher than irrelevant score and has at least 1 timber keyword
            if timber_score > 0 and timber_score > irrelevant_score:
                relevant_results.append(result)
                print(f"      ✅ Relevant: {result.get('title', 'No title')[:60]}...")
            else:
                print(f"      ❌ Filtered out: {result.get('title', 'No title')[:60]}...")
        
        return relevant_results
    
    async def extract_timber_business_contacts(self, business_name, search_results, expected_city="", expected_address=""):
        """Use enhanced AI prompt to extract contact information for timber businesses with location verification"""
        
        print(f"   🤖 Analyzing timber business results with AI...")
        
        # Prepare search results text for OpenAI
        results_text = self.format_search_results(search_results)
        
        # Enhanced prompt specifically for timber businesses with location verification
        prompt = f"""
        You are a specialized business intelligence analyst focused on the TIMBER, TEAK WOOD, and WOODEN PRODUCTS industry.

        Analyze the following web search results for the business "{business_name}" and determine if this is a legitimate timber/wood industry business.

        BUSINESS TO ANALYZE: {business_name}
        EXPECTED LOCATION: {expected_city} {expected_address}

        SEARCH RESULTS:
        {results_text}

        EXTRACTION RULES:
        1. ONLY extract information if this business is clearly involved in timber, teak wood, lumber, wooden products, forest products, or related wood industry activities
        2. VERIFY the location matches or is near the expected location: {expected_city}
        3. EXCLUDE businesses in: restaurants, hotels, textiles, software, finance, or other non-wood industries
        4. Prefer official company websites over directory listings
        5. Cross-verify phone numbers and addresses with the expected location

        TIMBER INDUSTRY KEYWORDS TO LOOK FOR:
        - Timber, teak, wood, lumber, hardwood, softwood
        - Plywood, furniture, wooden products, sawmill
        - Forest products, plantation, forestry, woodwork
        - Wood export/import, timber trading, wood supplier
        - Carpentry, joinery, wood processing, veneer

        Please extract and format the following information:

        BUSINESS_NAME: {business_name}
        INDUSTRY_RELEVANCE: [Rate 1-10 how relevant this business is to timber/wood industry, 0 if completely irrelevant]
        BUSINESS_TYPE: [Specify: Timber Trader/Wood Manufacturer/Furniture Maker/Sawmill/Plantation/Export-Import/Other Wood Business/NOT TIMBER RELATED]
        PHONE: [extract phone number if found, prioritize numbers from {expected_city} area, or "Not found"]
        EMAIL: [extract email address if found, or "Not found"]  
        WEBSITE: [extract official website URL if found, or "Not found"]
        ADDRESS: [extract business address if found, verify it matches expected location {expected_city}, or "Not found"]
        LOCATION_MATCH: [Rate 1-10 how well the found address matches expected location: {expected_city}]
        DESCRIPTION: [brief description focusing on timber/wood business activities, or "Non-timber business" if irrelevant]
        CONFIDENCE: [rate 1-10 how confident you are this is the correct timber business]
        RECOMMENDATION: [INCLUDE/EXCLUDE - Include only if INDUSTRY_RELEVANCE >= 6 AND CONFIDENCE >= 5]

        CRITICAL: If INDUSTRY_RELEVANCE is less than 6, mark as EXCLUDE and set all contact fields to "Irrelevant business"

        Format your response exactly as shown above with the field names.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.1
            )
            
            if response.choices[0].message.content:
                extracted_info = response.choices[0].message.content
                print(f"   ✅ Enhanced AI extraction completed")
                
                # Check if business should be excluded
                if "RECOMMENDATION: EXCLUDE" in extracted_info or "Irrelevant business" in extracted_info:
                    print(f"   ❌ Business excluded as irrelevant to timber industry")
                    self.irrelevant_businesses.append(business_name)
                    return self.create_irrelevant_business_result(business_name, extracted_info)
                
                result = {
                    'business_name': business_name,
                    'extracted_info': extracted_info,
                    'raw_search_results': search_results,
                    'research_date': datetime.now().isoformat(),
                    'method': 'Enhanced Timber Research',
                    'status': 'success'
                }
                
                self.results.append(result)
                
                # Display results
                print(f"   📋 Timber business results for {business_name}:")
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
    
    async def get_justdial_contact(self, business_name, city=""):
        """Get JustDial contact with timber business filtering"""
        
        justdial_phone = None
        if JUSTDIAL_AVAILABLE and self.groq_key:
            try:
                print(f"📱 JustDial timber business search for: {business_name}")
                
                # Use JustDial researcher to get phone number
                justdial_researcher = JustDialStreamlitResearcher(
                    groq_api_key=self.groq_key,
                    use_existing_chrome=True,
                    headless=False
                )
                
                # Search with timber-specific terms
                search_terms = f"{business_name} timber wood"
                justdial_result = justdial_researcher.research_single_business(search_terms, city)
                
                if justdial_result and justdial_result.get('status') == 'success':
                    justdial_phone = justdial_result.get('justdial_phone')
                    print(f"✅ JustDial contact found: {justdial_phone}")
                else:
                    print(f"⚠️ JustDial search failed")
                    justdial_phone = "Not found"
                    
            except Exception as e:
                print(f"❌ JustDial error: {e}")
                justdial_phone = "Research failed"
        else:
            justdial_phone = "Not available"
            
        # Store JustDial result
        self.justdial_results[business_name] = justdial_phone
    
    def format_search_results(self, search_results):
        """Format Tavily search results for OpenAI analysis"""
        
        formatted_results = []
        
        for i, result in enumerate(search_results[:8], 1):  # Limit to 8 results for better focus
            formatted_result = f"""
            RESULT {i}:
            Title: {result.get('title', 'No title')}
            URL: {result.get('url', 'No URL')}
            Content: {result.get('content', 'No content')[:600]}...
            """
            formatted_results.append(formatted_result)
        
        return '\n'.join(formatted_results)
    
    def create_irrelevant_business_result(self, business_name, extracted_info):
        """Create result for businesses that are not timber-related"""
        
        result = {
            'business_name': business_name,
            'extracted_info': extracted_info,
            'raw_search_results': [],
            'research_date': datetime.now().isoformat(),
            'method': 'Filtered Out - Irrelevant',
            'status': 'irrelevant'
        }
        
        print(f"   🚫 Irrelevant business filtered out: {business_name}")
        
        return result
    
    def create_manual_fallback(self, business_name):
        """Create fallback result when automated research fails"""
        
        fallback_info = f"""
        BUSINESS_NAME: {business_name}
        INDUSTRY_RELEVANCE: Manual verification required
        BUSINESS_TYPE: Unknown - Manual verification needed
        PHONE: Research required
        EMAIL: Research required
        WEBSITE: Research required  
        ADDRESS: Research required
        LOCATION_MATCH: Unknown
        DESCRIPTION: Potential timber/wood business - requires manual verification
        CONFIDENCE: 1
        RECOMMENDATION: MANUAL RESEARCH

        MANUAL RESEARCH STEPS:
        1. Google search: "{business_name} timber wood contact information"
        2. Verify business is involved in timber/teak wood industry
        3. Check local timber trade directories and associations
        4. Search for company in wood export/import databases
        5. Verify location and contact details manually
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
        INDUSTRY_RELEVANCE: 0
        BUSINESS_TYPE: Unknown - Billing Error
        PHONE: API billing error
        EMAIL: API billing error
        WEBSITE: API billing error  
        ADDRESS: API billing error
        LOCATION_MATCH: 0
        DESCRIPTION: Research stopped due to API billing/quota issue
        CONFIDENCE: 0
        RECOMMENDATION: BILLING ERROR

        API BILLING ERROR:
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
    
    async def research_from_dataframe_enhanced(self, df, consignee_column='Consignee Name', city_column=None, address_column=None, max_businesses=None, enable_justdial=True):
        """Enhanced research with location cross-verification"""
        
        # Validate consignee column
        if consignee_column not in df.columns:
            available_cols = [col for col in df.columns if 'consignee' in col.lower() or 'name' in col.lower()]
            if available_cols:
                consignee_column = available_cols[0]
                print(f"⚠️  Using '{consignee_column}' instead.")
            else:
                raise ValueError(f"No business name column found. Available: {list(df.columns)}")
        
        # Auto-detect city column
        if not city_column:
            for col in df.columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in ['city', 'location', 'place']):
                    city_column = col
                    break
        
        # Auto-detect address column
        if not address_column:
            for col in df.columns:
                col_lower = col.lower()
                if 'address' in col_lower:
                    address_column = col
                    break
        
        print(f"🏢 Business column: {consignee_column}")
        print(f"🏙️ City column: {city_column}")
        print(f"📍 Address column: {address_column}")
        
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
        
        # Research each business with location verification
        successful = 0
        manual_required = 0
        billing_errors = 0
        irrelevant_count = 0
        
        for i, business_name in enumerate(business_names, 1):
            print(f"\n📊 Progress: {i}/{total_businesses}")
            print(f"🌲 Timber Business: {business_name}")
            
            # Get location info for this business
            expected_city = ""
            expected_address = ""
            
            business_rows = df[df[consignee_column] == business_name]
            if not business_rows.empty:
                if city_column and pd.notna(business_rows[city_column].iloc[0]):
                    expected_city = str(business_rows[city_column].iloc[0]).strip()
                
                if address_column and pd.notna(business_rows[address_column].iloc[0]):
                    expected_address = str(business_rows[address_column].iloc[0]).strip()
            
            if expected_city:
                print(f"📍 Expected location: {expected_city}")
            
            try:
                result = await self.research_business_with_location_verification(
                    business_name, expected_city, expected_address
                )
                
                if result['status'] == 'success':
                    successful += 1
                elif result['status'] == 'manual_required':
                    manual_required += 1
                elif result['status'] == 'billing_error':
                    billing_errors += 1
                    print("💳 Stopping research due to billing error.")
                    break
                elif result['status'] == 'irrelevant':
                    irrelevant_count += 1
                
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
        
        # Return enhanced summary
        total_processed = len(self.results)
        summary = {
            'total_processed': total_processed,
            'successful': successful,
            'manual_required': manual_required,
            'billing_errors': billing_errors,
            'irrelevant_filtered': irrelevant_count,
            'success_rate': successful/total_processed*100 if total_processed else 0,
            'relevance_rate': (successful + manual_required)/(total_processed)*100 if total_processed else 0
        }
        
        print(f"\n🎯 TIMBER BUSINESS RESEARCH SUMMARY:")
        print(f"   📊 Total processed: {total_processed}")
        print(f"   ✅ Successful: {successful}")
        print(f"   ⚠️  Manual required: {manual_required}")
        print(f"   🚫 Irrelevant filtered: {irrelevant_count}")
        print(f"   💳 Billing errors: {billing_errors}")
        print(f"   📈 Success rate: {summary['success_rate']:.1f}%")
        print(f"   🌲 Timber relevance rate: {summary['relevance_rate']:.1f}%")
        
        return summary
    
    def parse_extracted_info_to_csv_enhanced(self, result):
        """Parse extracted info with enhanced timber business fields"""
        info = result['extracted_info']
        business_name = result['business_name']
        
        # Get JustDial phone number for this business
        justdial_whatsapp_number = self.justdial_results.get(business_name, "Not found")
        
        csv_row = {
            'business_name': business_name,
            'industry_relevance': self.extract_field_value(info, 'INDUSTRY_RELEVANCE:'),
            'business_type': self.extract_field_value(info, 'BUSINESS_TYPE:'),
            'phone': self.extract_field_value(info, 'PHONE:'),
            'email': self.extract_field_value(info, 'EMAIL:'),
            'website': self.extract_field_value(info, 'WEBSITE:'),
            'address': self.extract_field_value(info, 'ADDRESS:'),
            'location_match': self.extract_field_value(info, 'LOCATION_MATCH:'),
            'description': self.extract_field_value(info, 'DESCRIPTION:'),
            'confidence': self.extract_field_value(info, 'CONFIDENCE:'),
            'recommendation': self.extract_field_value(info, 'RECOMMENDATION:'),
            'justdial_whatsapp_number': justdial_whatsapp_number,
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
    
    def get_results_dataframe(self):
        """Convert results to DataFrame with enhanced timber business fields"""
        
        if not self.results:
            return pd.DataFrame()
        
        csv_data = []
        for result in self.results:
            csv_row = self.parse_extracted_info_to_csv_enhanced(result)
            csv_data.append(csv_row)
        
        return pd.DataFrame(csv_data)
    
    def save_csv_results(self, filename=None):
        """Save enhanced timber business research results to CSV"""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"timber_business_contacts_{timestamp}.csv"
        
        results_df = self.get_results_dataframe()
        results_df.to_csv(filename, index=False)
        
        print(f"📁 Enhanced timber business results saved to: {filename}")
        return filename

# Enhanced function to replace the original research function
async def research_timber_businesses_from_dataframe(df, consignee_column='Consignee Name', city_column=None, address_column=None, max_businesses=10, enable_justdial=True):
    """
    Enhanced function to research TIMBER BUSINESSES from DataFrame with smart filtering and location verification
    
    Args:
        df: pandas DataFrame containing business data
        consignee_column: name of column containing business names
        city_column: name of column containing city information (auto-detected if None)
        address_column: name of column containing address information (auto-detected if None)
        max_businesses: maximum number of businesses to research (default 10)
        enable_justdial: whether to enable JustDial WhatsApp number extraction (default True)
    
    Returns:
        tuple: (results_dataframe, summary_dict, csv_filename)
    """
    
    try:
        researcher = EnhancedTimberBusinessResearcher()
        
        # Test APIs first
        api_ok, api_message = researcher.test_apis()
        if not api_ok:
            raise Exception(f"API Test Failed: {api_message}")
        
        # Research timber businesses with enhanced filtering
        summary = await researcher.research_from_dataframe_enhanced(
            df, 
            consignee_column=consignee_column,
            city_column=city_column,
            address_column=address_column,
            max_businesses=max_businesses,
            enable_justdial=enable_justdial
        )
        
        # Get results with enhanced timber business data
        results_df = researcher.get_results_dataframe()
        
        # Save to CSV with enhanced format
        csv_filename = researcher.save_csv_results()
        
        return results_df, summary, csv_filename
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None, None
