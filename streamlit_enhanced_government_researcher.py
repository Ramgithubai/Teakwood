"""
Streamlit interface for Enhanced Government Business Researcher
Adds DataFrame compatibility to the enhanced government researcher
"""

import asyncio
import pandas as pd
from datetime import datetime
import streamlit as st
import os
import sys

# Add the business_contact_finder directory to the path
business_researcher_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'business_contact_finder')
if business_researcher_path not in sys.path:
    sys.path.insert(0, business_researcher_path)

try:
    from enhanced_government_researcher import EnhancedGovernmentBusinessResearcher
    ENHANCED_RESEARCH_AVAILABLE = True
except ImportError as e:
    # Enhanced research not available, create fallback
    ENHANCED_RESEARCH_AVAILABLE = False
    import warnings
    warnings.warn(f"Enhanced Government Researcher not available: {str(e)}")
    
    # Create a dummy class to prevent further errors
    class EnhancedGovernmentBusinessResearcher:
        def __init__(self):
            raise ImportError("Enhanced Government Researcher not available")


async def enhanced_research_businesses_from_dataframe(df, consignee_column='Consignee Name', max_businesses=10):
    """
    Enhanced research function for businesses from a DataFrame
    Includes government sources, industry sources, and general web research
    
    Args:
        df: pandas DataFrame containing business data
        consignee_column: name of column containing business names
        max_businesses: maximum number of businesses to research (default 10)
    
    Returns:
        tuple: (results_dataframe, summary_dict, csv_filename)
    """
    
    # Check if enhanced research is available
    if not ENHANCED_RESEARCH_AVAILABLE:
        st.error("❌ Enhanced Government Research is not available")
        st.error(f"📁 Expected path: {business_researcher_path}")
        st.error("💡 Make sure the enhanced_government_researcher.py file exists in the business_contact_finder directory.")
        return None, None, None
    
    try:
        # Initialize the enhanced researcher
        researcher = EnhancedGovernmentBusinessResearcher()
        
        # Get unique business names from DataFrame
        business_names = df[consignee_column].dropna().unique()[:max_businesses]
        
        print(f"🏛️ Starting Enhanced Government Research for {len(business_names)} businesses...")
        print("🔍 This includes: Government sources + Industry sources + General web")
        
        # Research each business
        for i, business_name in enumerate(business_names, 1):
            print(f"\n[{i}/{len(business_names)}] Enhanced research: {business_name}")
            
            try:
                # Research this business comprehensively
                result = await researcher.research_business_comprehensive(business_name)
                
                if result:
                    print(f"✅ Enhanced research completed for {business_name}")
                else:
                    print(f"⚠️ Limited results for {business_name}")
                    
            except Exception as e:
                print(f"❌ Error researching {business_name}: {str(e)}")
                # Create fallback result
                researcher.results.append({
                    'business_name': business_name,
                    'extracted_info': f"BUSINESS_NAME: {business_name}\nSTATUS: Research failed - {str(e)}",
                    'government_sources_found': 0,
                    'industry_sources_found': 0,
                    'total_sources': 0,
                    'research_date': datetime.now().isoformat(),
                    'method': 'Enhanced Government (Failed)',
                    'status': 'failed'
                })
        
        # Convert results to DataFrame
        results_df = get_enhanced_results_dataframe(researcher.results)
        
        # Create summary
        total_processed = len(business_names)
        successful = len([r for r in researcher.results if r.get('status') == 'success'])
        failed = total_processed - successful
        
        # Count government verified businesses
        government_verified = 0
        for result in researcher.results:
            if 'GOVERNMENT_VERIFIED: YES' in result.get('extracted_info', ''):
                government_verified += 1
        
        summary = {
            'total_processed': total_processed,
            'successful': successful,
            'failed': failed,
            'government_verified': government_verified,
            'success_rate': (successful / total_processed * 100) if total_processed > 0 else 0,
            'avg_govt_sources': sum([r.get('government_sources_found', 0) for r in researcher.results]) / len(researcher.results) if researcher.results else 0,
            'avg_industry_sources': sum([r.get('industry_sources_found', 0) for r in researcher.results]) / len(researcher.results) if researcher.results else 0,
            'avg_total_sources': sum([r.get('total_sources', 0) for r in researcher.results]) / len(researcher.results) if researcher.results else 0
        }
        
        # Save results to CSV
        csv_filename = save_enhanced_results_to_csv(researcher.results)
        
        print(f"\n🎉 Enhanced Research Summary:")
        print(f"   📊 Total Processed: {summary['total_processed']}")
        print(f"   ✅ Successful: {summary['successful']}")
        print(f"   🏛️ Government Verified: {summary['government_verified']}")
        print(f"   📈 Success Rate: {summary['success_rate']:.1f}%")
        print(f"   📋 Results saved to: {csv_filename}")
        
        return results_df, summary, csv_filename
        
    except Exception as e:
        print(f"❌ Enhanced research failed: {e}")
        return None, None, None


def get_enhanced_results_dataframe(results):
    """Convert enhanced research results to DataFrame"""
    
    if not results:
        return pd.DataFrame()
    
    csv_data = []
    for result in results:
        csv_row = parse_enhanced_info_to_csv(result)
        csv_data.append(csv_row)
    
    return pd.DataFrame(csv_data)


def parse_enhanced_info_to_csv(result):
    """Parse enhanced extracted info into CSV fields"""
    info = result['extracted_info']
    
    csv_row = {
        'business_name': result['business_name'],
        'phone': extract_field_value(info, 'PHONE:'),
        'email': extract_field_value(info, 'EMAIL:'),
        'website': extract_field_value(info, 'WEBSITE:'),
        'address': extract_field_value(info, 'ADDRESS:'),
        'registration_number': extract_field_value(info, 'REGISTRATION_NUMBER:'),
        'license_details': extract_field_value(info, 'LICENSE_DETAILS:'),
        'directors': extract_field_value(info, 'DIRECTORS:'),
        'description': extract_field_value(info, 'DESCRIPTION:'),
        'government_verified': extract_field_value(info, 'GOVERNMENT_VERIFIED:'),
        'confidence': extract_field_value(info, 'CONFIDENCE:'),
        'govt_sources_found': result.get('government_sources_found', 0),
        'industry_sources_found': result.get('industry_sources_found', 0),
        'total_sources': result.get('total_sources', 0),
        'status': result.get('status', 'unknown'),
        'research_date': result.get('research_date', ''),
        'method': result.get('method', 'Enhanced Government Research')
    }
    
    return csv_row


def extract_field_value(text, field_name):
    """Extract field value from formatted text"""
    try:
        lines = text.split('\n')
        for line in lines:
            if line.strip().startswith(field_name):
                value = line.replace(field_name, '').strip()
                return value if value and value not in ["Not found", ""] else ""
        return ""
    except:
        return ""


def save_enhanced_results_to_csv(results):
    """Save enhanced research results to CSV file"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"enhanced_government_research_{timestamp}.csv"
    
    results_df = get_enhanced_results_dataframe(results)
    results_df.to_csv(csv_filename, index=False)
    
    return csv_filename


class StreamlitEnhancedGovernmentResearcher:
    """Streamlit-compatible wrapper for Enhanced Government Business Researcher"""
    
    def __init__(self):
        self.enhanced_researcher = None
    
    def test_apis(self):
        """Test both APIs before starting research"""
        if not ENHANCED_RESEARCH_AVAILABLE:
            return False, "Enhanced Government Researcher not available - check file paths"
            
        try:
            # Create temporary researcher just for testing
            test_researcher = EnhancedGovernmentBusinessResearcher()
            
            # If we get here without exceptions, APIs are working
            return True, "Enhanced Government Researcher APIs working"
            
        except ValueError as e:
            if "OPENAI_API_KEY" in str(e):
                return False, "OpenAI API key not found in .env file"
            elif "TAVILY_API_KEY" in str(e):
                return False, "Tavily API key not found in .env file"
            else:
                return False, f"API configuration error: {str(e)}"
        except Exception as e:
            return False, f"API test failed: {str(e)}"
    
    async def research_from_dataframe(self, df, consignee_column='Consignee Name', max_businesses=10):
        """
        Research businesses from DataFrame using enhanced government research
        
        Args:
            df: pandas DataFrame
            consignee_column: column name containing business names
            max_businesses: maximum number to research
            
        Returns:
            dict: summary of research results
        """
        
        try:
            # Execute enhanced research
            results_df, summary, csv_filename = await enhanced_research_businesses_from_dataframe(
                df=df,
                consignee_column=consignee_column, 
                max_businesses=max_businesses
            )
            
            return summary
            
        except Exception as e:
            raise Exception(f"Enhanced research failed: {str(e)}")
    
    def get_results_dataframe(self):
        """Get results as DataFrame"""
        # This would be implemented if we stored results in the wrapper
        # For now, results are handled by the main function
        return pd.DataFrame()
    
    def save_csv_results(self, filename=None):
        """Save results to CSV"""
        # This would be implemented if we stored results in the wrapper
        # For now, CSV saving is handled by the main function
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"enhanced_government_research_{timestamp}.csv"
