"""
Enhanced Business Contact Researcher with Government Sources
Includes specific searches for government business databases and official registrations
"""

import asyncio
import csv
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import openai
from tavily import TavilyClient

# Load environment variables
load_dotenv()

class EnhancedGovernmentBusinessResearcher:
    def __init__(self):
        # Load API keys
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.tavily_key = os.getenv('TAVILY_API_KEY')
        
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY not found!")
        if not self.tavily_key:
            raise ValueError("TAVILY_API_KEY not found!")
        
        # Initialize clients
        self.openai_client = openai.OpenAI(api_key=self.openai_key)
        self.tavily_client = TavilyClient(api_key=self.tavily_key)
        
        print(f"✅ OpenAI API Key: {self.openai_key[:20]}...")
        print(f"✅ Tavily API Key: {self.tavily_key[:20]}...")
        
        # Test both APIs
        self.test_apis()
        
        self.results = []
    
    def test_apis(self):
        """Test both APIs before starting research"""
        print("\n🧪 Testing APIs...")
        
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
                print("❌ OpenAI API: Empty response")
                
        except Exception as e:
            print(f"❌ OpenAI API: {e}")
        
        # Test Tavily
        try:
            response = self.tavily_client.search("test query", max_results=1)
            if response.get('results'):
                print("✅ Tavily API: Working")
            else:
                print("❌ Tavily API: No results")
                
        except Exception as e:
            print(f"❌ Tavily API: {e}")
    
    async def research_business_comprehensive(self, business_name):
        """Research business using comprehensive strategy including government sources"""
        
        print(f"\n🔍 Researching: {business_name}")
        
        # Multi-layer search strategy
        all_search_results = []
        
        # Layer 1: General business information
        print("   📊 Layer 1: General business search...")
        general_results = self.search_general_business_info(business_name)
        all_search_results.extend(general_results)
        
        # Layer 2: Government and official sources
        print("   🏛️  Layer 2: Government sources search...")
        government_results = self.search_government_sources(business_name)
        all_search_results.extend(government_results)
        
        # Layer 3: Industry-specific sources
        print("   🌲 Layer 3: Timber industry sources...")
        industry_results = self.search_industry_sources(business_name)
        all_search_results.extend(industry_results)
        
        if not all_search_results:
            print(f"❌ No search results found for {business_name}")
            return self.create_manual_fallback(business_name)
        
        # Extract contact info using OpenAI with comprehensive data
        contact_info = await self.extract_contacts_with_openai_enhanced(business_name, all_search_results)
        
        return contact_info
    
    def search_general_business_info(self, business_name):
        """Search for general business information"""
        
        search_queries = [
            f"{business_name} contact information phone email address",
            f"{business_name} official website company profile",
            f"{business_name} timber wood business details"
        ]
        
        return self.execute_search_queries(search_queries, "General")
    
    def search_government_sources(self, business_name):
        """Search specifically in government databases and official sources"""
        
        # Government and official database searches
        government_queries = [
            f'"{business_name}" site:gov.in business registration',
            f'"{business_name}" site:nic.in company details',
            f'"{business_name}" ministry commerce industry registration',
            f'"{business_name}" GST registration number',
            f'"{business_name}" ROC registrar companies',
            f'"{business_name}" DIN director identification',
            f'"{business_name}" forest department license',
            f'"{business_name}" pollution control board clearance',
            f'"{business_name}" shop establishment license',
            f'"{business_name}" trade license municipal corporation'
        ]
        
        return self.execute_search_queries(government_queries, "Government")
    
    def search_industry_sources(self, business_name):
        """Search in timber/wood industry specific sources"""
        
        industry_queries = [
            f'"{business_name}" timber traders association member',
            f'"{business_name}" wood importers exporters directory',
            f'"{business_name}" forest produce trading license',
            f'"{business_name}" timber merchants federation',
            f'"{business_name}" wood industry chamber commerce',
            f'"{business_name}" lumber dealers association',
            f'"{business_name}" plywood manufacturers association'
        ]
        
        return self.execute_search_queries(industry_queries, "Industry")
    
    def execute_search_queries(self, queries, search_type):
        """Execute a list of search queries and return results"""
        
        all_results = []
        
        for query in queries:
            try:
                print(f"      📝 {search_type}: {query[:60]}...")
                
                # Search with Tavily
                response = self.tavily_client.search(
                    query=query,
                    max_results=2,  # Reduced per query but more queries
                    search_depth="advanced",
                    include_domains=self.get_preferred_domains(search_type),
                    exclude_domains=["facebook.com", "twitter.com", "instagram.com", "linkedin.com"]
                )
                
                if response.get('results'):
                    # Tag results with search type
                    for result in response['results']:
                        result['search_type'] = search_type
                    all_results.extend(response['results'])
                    print(f"         ✅ Found {len(response['results'])} results")
                else:
                    print(f"         ❌ No results")
                    
            except Exception as e:
                print(f"         ⚠️  Error: {str(e)[:50]}")
                
        print(f"   📊 {search_type} total: {len(all_results)} results")
        return all_results
    
    def get_preferred_domains(self, search_type):
        """Get preferred domains for different search types"""
        
        domain_preferences = {
            "Government": [
                "gov.in", "nic.in", "india.gov.in", "mca.gov.in", 
                "cbic.gov.in", "incometax.gov.in", "gst.gov.in",
                "moef.gov.in", "forest.gov.in"
            ],
            "Industry": [
                "fidr.org", "plywoodassociation.org", "itpo.gov.in",
                "cii.in", "ficci.in", "assocham.org"
            ],
            "General": None  # No domain restriction for general search
        }
        
        return domain_preferences.get(search_type)
    
    async def extract_contacts_with_openai_enhanced(self, business_name, search_results):
        """Enhanced OpenAI extraction with government data analysis"""
        
        print(f"   🤖 Analyzing {len(search_results)} results with OpenAI...")
        
        # Categorize results by source type
        categorized_results = self.categorize_search_results(search_results)
        
        # Format results for OpenAI analysis
        results_text = self.format_search_results_enhanced(categorized_results)
        
        prompt = f"""
        Analyze the following comprehensive search results for the business "{business_name}" and extract contact information.
        The results include government sources, industry sources, and general business information.

        SEARCH RESULTS:
        {results_text}

        Please extract and format the following information:

        BUSINESS_NAME: {business_name}
        PHONE: [extract phone number if found, or "Not found"]
        EMAIL: [extract email address if found, or "Not found"]  
        WEBSITE: [extract official website URL if found, or "Not found"]
        ADDRESS: [extract business address if found, or "Not found"]
        REGISTRATION_NUMBER: [extract company registration/GST number if found, or "Not found"]
        LICENSE_DETAILS: [extract any business licenses mentioned, or "Not found"]
        DIRECTORS: [extract director names if found in government records, or "Not found"]
        DESCRIPTION: [brief description based on all sources, or "No description available"]
        GOVERNMENT_VERIFIED: [YES if found in government sources, NO if only general sources]
        CONFIDENCE: [rate 1-10 based on quality and number of sources]

        Rules:
        1. Prioritize information from government sources (.gov.in domains)
        2. Cross-verify information across multiple sources
        3. Only extract clearly stated information
        4. Mark confidence higher if government sources confirm the business
        5. Include registration numbers and licenses for legitimacy verification

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
                print(f"   ✅ Enhanced OpenAI extraction completed")
                
                # Create structured result
                result = {
                    'business_name': business_name,
                    'extracted_info': extracted_info,
                    'raw_search_results': search_results,
                    'government_sources_found': len([r for r in search_results if r.get('search_type') == 'Government']),
                    'industry_sources_found': len([r for r in search_results if r.get('search_type') == 'Industry']),
                    'total_sources': len(search_results),
                    'research_date': datetime.now().isoformat(),
                    'method': 'Enhanced Tavily + OpenAI + Government',
                    'status': 'success'
                }
                
                self.results.append(result)
                
                # Display results
                print(f"   📋 Enhanced Results for {business_name}:")
                print("-" * 60)
                print(extracted_info)
                print("-" * 60)
                print(f"   📊 Sources: {result['government_sources_found']} govt, {result['industry_sources_found']} industry, {result['total_sources']} total")
                
                return result
            else:
                print(f"   ❌ OpenAI returned empty response")
                return self.create_manual_fallback(business_name)
                
        except Exception as e:
            print(f"   ❌ OpenAI extraction error: {e}")
            return self.create_manual_fallback(business_name)
    
    def categorize_search_results(self, search_results):
        """Categorize results by source type"""
        
        categorized = {
            'Government': [],
            'Industry': [],
            'General': []
        }
        
        for result in search_results:
            search_type = result.get('search_type', 'General')
            categorized[search_type].append(result)
        
        return categorized
    
    def format_search_results_enhanced(self, categorized_results):
        """Format categorized search results for enhanced OpenAI analysis"""
        
        formatted_sections = []
        
        for category, results in categorized_results.items():
            if results:
                formatted_sections.append(f"\n=== {category.upper()} SOURCES ===")
                
                for i, result in enumerate(results[:5], 1):  # Top 5 per category
                    formatted_result = f"""
                    {category.upper()} RESULT {i}:
                    Title: {result.get('title', 'No title')}
                    URL: {result.get('url', 'No URL')}
                    Content: {result.get('content', 'No content')[:400]}...
                    """
                    formatted_sections.append(formatted_result)
        
        return '\n'.join(formatted_sections)
    
    def create_manual_fallback(self, business_name):
        """Enhanced fallback with government research suggestions"""
        
        fallback_info = f"""
        BUSINESS_NAME: {business_name}
        PHONE: Research required
        EMAIL: Research required
        WEBSITE: Research required  
        ADDRESS: Research required
        REGISTRATION_NUMBER: Research required
        LICENSE_DETAILS: Research required
        DIRECTORS: Research required
        DESCRIPTION: Timber/wood trading business - requires manual verification
        GOVERNMENT_VERIFIED: NO - manual verification needed
        CONFIDENCE: 1

        COMPREHENSIVE MANUAL RESEARCH NEEDED:
        
        Government Sources:
        1. MCA Portal: https://www.mca.gov.in/ (Company registration)
        2. GST Portal: https://gst.gov.in/ (GST registration details)
        3. State Forest Department websites (Timber licenses)
        4. Pollution Control Board clearances
        5. Shop & Establishment license databases
        
        Industry Sources:
        6. Timber Traders Association directories
        7. Export-Import databases (if applicable)
        8. Chamber of Commerce member lists
        
        General Sources:
        9. Google: "{business_name}" contact information
        10. LinkedIn company profiles
        11. Business directories and Yellow Pages
        """
        
        result = {
            'business_name': business_name,
            'extracted_info': fallback_info,
            'raw_search_results': [],
            'government_sources_found': 0,
            'industry_sources_found': 0,
            'total_sources': 0,
            'research_date': datetime.now().isoformat(),
            'method': 'Manual Fallback - Enhanced',
            'status': 'manual_required'
        }
        
        self.results.append(result)
        
        print(f"   ⚠️  Enhanced manual research required for {business_name}")
        print("-" * 60)
        print(fallback_info)
        print("-" * 60)
        
        return result
    
    async def research_from_csv(self, csv_file="business_names.csv", limit=None):
        """Research businesses using enhanced comprehensive approach"""
        
        # Load business names
        business_names = []
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    name = row.get('Business Name', '').strip()
                    if name:
                        business_names.append(name)
        except FileNotFoundError:
            print(f"❌ CSV file {csv_file} not found!")
            return
        
        if limit:
            business_names = business_names[:limit]
        
        print(f"\n📋 Enhanced Research: {len(business_names)} businesses")
        print("🎯 Strategy: General + Government + Industry sources")
        
        # Research each business
        successful = 0
        government_verified = 0
        manual_required = 0
        
        for i, business_name in enumerate(business_names, 1):
            print(f"\n📊 Progress: {i}/{len(business_names)}")
            
            result = await self.research_business_comprehensive(business_name)
            
            if result['status'] == 'success':
                successful += 1
                if result['government_sources_found'] > 0:
                    government_verified += 1
            elif result['status'] == 'manual_required':
                manual_required += 1
            
            # Longer delay for comprehensive search
            await asyncio.sleep(4)
        
        # Save and summarize results
        filename = self.save_enhanced_results()
        
        print(f"\n📊 ENHANCED RESEARCH SUMMARY:")
        print(f"Total businesses: {len(business_names)}")
        print(f"Successfully researched: {successful}")
        print(f"Government-verified: {government_verified}")
        print(f"Manual research required: {manual_required}")
        print(f"Success rate: {successful/len(business_names)*100:.1f}%")
        print(f"Government verification rate: {government_verified/len(business_names)*100:.1f}%")
        print(f"Results saved to: {filename}")
    
    def save_enhanced_results(self):
        """Save enhanced research results with government data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        txt_filename = f"enhanced_government_research_{timestamp}.txt"
        with open(txt_filename, 'w', encoding='utf-8') as file:
            file.write("ENHANCED BUSINESS CONTACT RESEARCH WITH GOVERNMENT SOURCES\n")
            file.write("Includes: General + Government + Industry sources\n")
            file.write("=" * 80 + "\n\n")
            
            for result in self.results:
                file.write(f"BUSINESS: {result['business_name']}\n")
                file.write(f"METHOD: {result['method']}\n")
                file.write(f"STATUS: {result['status']}\n")
                file.write(f"GOVERNMENT SOURCES: {result['government_sources_found']}\n")
                file.write(f"INDUSTRY SOURCES: {result['industry_sources_found']}\n")
                file.write(f"TOTAL SOURCES: {result['total_sources']}\n")
                file.write(f"DATE: {result['research_date']}\n")
                file.write("=" * 60 + "\n")
                file.write(result['extracted_info'])
                file.write("\n" + "=" * 80 + "\n\n")
        
        # Save enhanced CSV format
        csv_filename = f"government_verified_contacts_{timestamp}.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'business_name', 'phone', 'email', 'website', 'address', 
                'registration_number', 'license_details', 'directors',
                'description', 'government_verified', 'confidence', 
                'govt_sources_found', 'industry_sources_found', 'total_sources',
                'status', 'research_date'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self.results:
                csv_row = self.parse_enhanced_info_to_csv(result)
                writer.writerow(csv_row)
        
        print(f"\n📁 Enhanced results saved to:")
        print(f"   📄 Detailed: {txt_filename}")
        print(f"   📊 CSV: {csv_filename}")
        
        return txt_filename
    
    def parse_enhanced_info_to_csv(self, result):
        """Parse enhanced extracted info into CSV fields"""
        info = result['extracted_info']
        
        csv_row = {
            'business_name': result['business_name'],
            'phone': self.extract_field_value(info, 'PHONE:'),
            'email': self.extract_field_value(info, 'EMAIL:'),
            'website': self.extract_field_value(info, 'WEBSITE:'),
            'address': self.extract_field_value(info, 'ADDRESS:'),
            'registration_number': self.extract_field_value(info, 'REGISTRATION_NUMBER:'),
            'license_details': self.extract_field_value(info, 'LICENSE_DETAILS:'),
            'directors': self.extract_field_value(info, 'DIRECTORS:'),
            'description': self.extract_field_value(info, 'DESCRIPTION:'),
            'government_verified': self.extract_field_value(info, 'GOVERNMENT_VERIFIED:'),
            'confidence': self.extract_field_value(info, 'CONFIDENCE:'),
            'govt_sources_found': result['government_sources_found'],
            'industry_sources_found': result['industry_sources_found'],
            'total_sources': result['total_sources'],
            'status': result['status'],
            'research_date': result['research_date']
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

async def main():
    """Main function for enhanced government research"""
    
    print("🌳 ENHANCED BUSINESS CONTACT RESEARCHER")
    print("=" * 70)
    print("🏛️  Includes Government Sources + Industry Sources + General Web")
    print("🎯 Searches: Business registrations, licenses, official records")
    print("=" * 70)
    
    try:
        researcher = EnhancedGovernmentBusinessResearcher()
        
        # Ask how many to research
        limit_input = input("\nHow many businesses to research? (number or 'all'): ").strip()
        limit = None
        if limit_input.isdigit():
            limit = int(limit_input)
        
        print(f"\n⚠️  Note: Enhanced search is more thorough but takes longer per business")
        print(f"   Estimated time: ~30-60 seconds per business")
        
        confirm = input(f"Proceed with enhanced research? (y/n): ").lower()
        if confirm == 'y':
            await researcher.research_from_csv(limit=limit)
        else:
            print("Research cancelled.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nFor basic research, use: python business_researcher.py")

if __name__ == "__main__":
    asyncio.run(main())
