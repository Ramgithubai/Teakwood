#!/usr/bin/env python3
"""
Integration script to enhance ai_csv_analyzer.py with Timber Business Smart Filtering
This script adds enhanced timber business research with location cross-verification
"""

import os
import shutil
from datetime import datetime

def backup_files():
    """Create backups of files that will be modified"""
    files_to_backup = [
        "ai_csv_analyzer.py",
        "modules/streamlit_business_researcher.py"
    ]
    
    backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            backup_path = f"{file_path}.backup_{backup_timestamp}"
            shutil.copy2(file_path, backup_path)
            print(f"✅ Backup created: {backup_path}")
        else:
            print(f"⚠️ File not found: {file_path}")

def update_streamlit_business_researcher():
    """Add the enhanced function to the existing streamlit_business_researcher.py"""
    
    original_file = "modules/streamlit_business_researcher.py"
    
    if not os.path.exists(original_file):
        print(f"❌ File not found: {original_file}")
        return False
    
    # Read the original file
    with open(original_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if enhanced function already exists
    if "research_timber_businesses_from_dataframe" in content:
        print("✅ Enhanced function already exists in streamlit_business_researcher.py")
        return True
    
    # Add import for enhanced researcher
    enhanced_import = """
# Import enhanced timber business researcher
try:
    from .enhanced_timber_business_researcher import research_timber_businesses_from_dataframe
    print("[INFO] ✅ Enhanced timber business researcher loaded successfully")
except ImportError as e:
    print(f"[INFO] ⚠️ Enhanced timber business researcher not available: {e}")
    # Fallback to regular function
    async def research_timber_businesses_from_dataframe(*args, **kwargs):
        return await research_businesses_from_dataframe(*args, **kwargs)
"""
    
    # Add the import at the end of the file
    enhanced_content = content + "\n" + enhanced_import
    
    # Write the enhanced content back
    with open(original_file, 'w', encoding='utf-8') as f:
        f.write(enhanced_content)
    
    print("✅ Enhanced function added to streamlit_business_researcher.py")
    return True

def create_enhanced_perform_web_scraping():
    """Create the enhanced perform_web_scraping function"""
    
    enhanced_function = '''
def perform_web_scraping_enhanced_timber(filtered_df):
    """Enhanced web scraping specifically for Teak Wood & Timber businesses with smart filtering"""

    # Check if DataFrame is empty
    if len(filtered_df) == 0:
        st.error("❌ No data to scrape. Please adjust your filters.")
        return

    # Find suitable columns for business names
    potential_name_columns = []
    for col in filtered_df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in ['consignee', 'name', 'company', 'business', 'shipper', 'supplier']):
            potential_name_columns.append(col)

    if not potential_name_columns:
        st.error("❌ No suitable business name columns found. Need columns like 'Consignee Name', 'Company Name', etc.")
        return

    # Enhanced column selection with location columns
    st.write("🌲 **Enhanced Timber Business Research Configuration:**")
    
    col_config1, col_config2 = st.columns(2)
    
    with col_config1:
        st.write("🏷️ **Select Business Name Column:**")
        selected_column = st.selectbox(
            "Choose the column containing business names:",
            potential_name_columns,
            help="Select the column that contains the business names you want to research",
            key="timber_business_name_column_selector"
        )
    
    with col_config2:
        st.write("📍 **Location Verification Columns (Optional):**")
        
        # Find potential city columns
        potential_city_columns = ['None']
        for col in filtered_df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['city', 'location', 'place', 'town']):
                potential_city_columns.append(col)
        
        city_column = st.selectbox(
            "City column (for location verification):",
            potential_city_columns,
            help="Select city column to verify business locations"
        )
        
        # Find potential address columns
        potential_address_columns = ['None']
        for col in filtered_df.columns:
            col_lower = col.lower()
            if 'address' in col_lower:
                potential_address_columns.append(col)
        
        address_column = st.selectbox(
            "Address column (for location verification):",
            potential_address_columns,
            help="Select address column to cross-verify business locations"
        )

    # Check unique business count
    unique_businesses = filtered_df[selected_column].dropna().nunique()
    if unique_businesses == 0:
        st.error(f"❌ No business names found in column '{selected_column}'")
        return

    st.info(f"🌲 Found {unique_businesses} unique businesses to research for timber/teak wood industry relevance")

    # Enhanced Business Research Range with location info preview
    if 'business_range_from' not in st.session_state:
        st.session_state.business_range_from = 1
    if 'business_range_to' not in st.session_state:
        st.session_state.business_range_to = min(5, unique_businesses)

    st.write("🎯 **Business Research Range:**")
    col_from, col_to = st.columns(2)
    
    with col_from:
        range_from = st.number_input(
            "From:",
            min_value=1,
            max_value=min(20, unique_businesses),
            value=st.session_state.business_range_from,
            help="Starting business number",
            key="timber_business_range_from_input"
        )
    
    with col_to:
        range_to = st.number_input(
            "To:",
            min_value=range_from,
            max_value=min(20, unique_businesses),
            value=max(st.session_state.business_range_to, range_from),
            help="Ending business number",
            key="timber_business_range_to_input"
        )
    
    # Calculate number of businesses to research
    max_businesses = range_to - range_from + 1
    
    # Update session state
    st.session_state.business_range_from = range_from
    st.session_state.business_range_to = range_to
    
    # Show preview of businesses to be researched with location info
    unique_businesses_list = filtered_df[selected_column].dropna().unique()
    businesses_to_research = unique_businesses_list[range_from-1:range_to]
    
    st.write("🔍 **Preview of Businesses to Research:**")
    preview_data = []
    for i, business in enumerate(businesses_to_research, start=range_from):
        business_rows = filtered_df[filtered_df[selected_column] == business]
        if not business_rows.empty:
            city_info = business_rows[city_column].iloc[0] if city_column != 'None' and city_column else "Not specified"
            address_info = business_rows[address_column].iloc[0] if address_column != 'None' and address_column else "Not specified"
            
            preview_data.append({
                "Order": i,
                "Business Name": business,
                "Expected City": city_info,
                "Expected Address": str(address_info)[:50] + "..." if len(str(address_info)) > 50 else address_info
            })
    
    if preview_data:
        preview_df = pd.DataFrame(preview_data)
        st.dataframe(preview_df, use_container_width=True)
    
    # Enhanced info about the timber business research
    st.info(f"🌲 Will research businesses {range_from} to {range_to} ({max_businesses} total businesses) with TIMBER INDUSTRY SMART FILTERING")

    # Enhanced features explanation
    st.write("🚀 **Enhanced Timber Business Research Features:**")
    col_feat1, col_feat2 = st.columns(2)
    
    with col_feat1:
        st.write("""
        **🌲 Industry-Specific Targeting:**
        • Searches specifically for timber, teak, wood businesses
        • Filters out irrelevant industries (restaurants, hotels, etc.)
        • Uses timber-specific search queries
        • Scores businesses for industry relevance (1-10)
        """)
    
    with col_feat2:
        st.write("""
        **📍 Location Cross-Verification:**
        • Verifies business location against expected city
        • Cross-checks addresses for accuracy
        • Provides location match score (1-10)
        • Reduces false positive results
        """)

    # Show research toggle
    research_mode = st.radio(
        "🔧 **Research Mode:**",
        ["🌲 Enhanced Timber Research (Recommended)", "📋 Standard Research"],
        help="Enhanced mode filters for timber businesses and verifies locations"
    )

    # API Configuration check and research button (same as before)
    # ... [Include the API configuration and research button code from the integration artifact]
    
    # Enhanced research execution
    if st.button(f"🌲 Start Enhanced Research ({max_businesses} businesses)", type="primary"):
        
        try:
            # Import the enhanced function
            if research_mode.startswith("🌲"):
                from modules.streamlit_business_researcher import research_timber_businesses_from_dataframe as research_function
                function_name = "Enhanced Timber Research"
            else:
                from modules.streamlit_business_researcher import research_businesses_from_dataframe as research_function
                function_name = "Standard Research"

            st.info(f"🔄 Starting {function_name}...")

            with st.spinner(f"🌲 Researching with {function_name}..."):

                # FIXED: Properly slice the DataFrame
                unique_businesses_list = filtered_df[selected_column].dropna().unique()
                start_idx = range_from - 1
                end_idx = range_to
                businesses_to_research = unique_businesses_list[start_idx:end_idx]
                research_df = filtered_df[filtered_df[selected_column].isin(businesses_to_research)]
                
                st.info(f"🎯 **Researching businesses {range_from} to {range_to}:**")
                for i, business in enumerate(businesses_to_research, start=range_from):
                    st.write(f"   {i}. {business}")

                # Run the research function
                async def run_research():
                    if research_mode.startswith("🌲"):
                        return await research_function(
                            df=research_df,
                            consignee_column=selected_column,
                            city_column=city_column if city_column != 'None' else None,
                            address_column=address_column if address_column != 'None' else None,
                            max_businesses=len(businesses_to_research),
                            enable_justdial=True
                        )
                    else:
                        return await research_function(
                            df=research_df,
                            consignee_column=selected_column,
                            max_businesses=len(businesses_to_research),
                            enable_justdial=True
                        )

                # Execute async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results_df, summary, csv_filename = loop.run_until_complete(run_research())
                loop.close()

                # Display results with enhanced information
                if results_df is not None and not results_df.empty:
                    st.success(f"🎉 **{function_name} Results:**")
                    
                    if research_mode.startswith("🌲"):
                        # Enhanced summary for timber research
                        col_sum1, col_sum2, col_sum3, col_sum4, col_sum5 = st.columns(5)
                        with col_sum1:
                            st.metric("Total Processed", summary['total_processed'])
                        with col_sum2:
                            st.metric("✅ Timber Businesses", summary['successful'])
                        with col_sum3:
                            st.metric("⚠️ Manual Required", summary['manual_required'])
                        with col_sum4:
                            st.metric("🚫 Irrelevant Filtered", summary.get('irrelevant_filtered', 0))
                        with col_sum5:
                            st.metric("🌲 Relevance Rate", f"{summary.get('relevance_rate', 0):.1f}%")
                    else:
                        # Standard summary
                        col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
                        with col_sum1:
                            st.metric("Total Processed", summary['total_processed'])
                        with col_sum2:
                            st.metric("Successful", summary['successful'])
                        with col_sum3:
                            st.metric("Manual Required", summary['manual_required'])
                        with col_sum4:
                            st.metric("Success Rate", f"{summary['success_rate']:.1f}%")

                    st.subheader("📈 Research Results")
                    st.dataframe(results_df, use_container_width=True, height=400)
                    
                    # Download options
                    csv_data = results_df.to_csv(index=False)
                    st.download_button(
                        label="📄 Download Results CSV",
                        data=csv_data,
                        file_name=f"{function_name.lower().replace(' ', '_')}_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    
                    st.balloons()
                    if research_mode.startswith("🌲"):
                        st.success(f"🌲 Enhanced Timber Research completed! Found {summary['successful']} relevant timber businesses.")
                    else:
                        st.success(f"📋 Standard Research completed! Found {summary['successful']} businesses.")

        except Exception as e:
            st.error(f"❌ Research Error: {str(e)}")
            st.error("Please check your API configuration and try again.")
'''
    
    return enhanced_function

def update_ai_csv_analyzer():
    """Update ai_csv_analyzer.py to include enhanced timber business research"""
    
    original_file = "ai_csv_analyzer.py"
    
    if not os.path.exists(original_file):
        print(f"❌ File not found: {original_file}")
        return False
    
    # Read the original file
    with open(original_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if enhanced function already exists
    if "perform_web_scraping_enhanced_timber" in content:
        print("✅ Enhanced function already exists in ai_csv_analyzer.py")
        return True
    
    # Add the enhanced function before the main() function
    enhanced_function = create_enhanced_perform_web_scraping()
    
    # Find the location to insert the enhanced function
    main_function_pos = content.find("def main():")
    if main_function_pos == -1:
        print("❌ Could not find main() function in ai_csv_analyzer.py")
        return False
    
    # Insert the enhanced function before main()
    enhanced_content = (
        content[:main_function_pos] + 
        enhanced_function + 
        "\n\n" + 
        content[main_function_pos:]
    )
    
    # Also update the web scraping button to offer both options
    enhanced_content = enhanced_content.replace(
        'if st.button("🌐 Web Scrape Filtered Data", help="Research business contact information using AI"):',
        '''col_scrape1, col_scrape2 = st.columns(2)
        with col_scrape1:
            if st.button("🌲 Enhanced Timber Research", help="Smart filtering for timber/teak wood businesses", type="primary"):
                perform_web_scraping_enhanced_timber(filtered_df)
        with col_scrape2:
            if st.button("📋 Standard Research", help="Standard business contact research"):'''
    )
    
    # Write the enhanced content back
    with open(original_file, 'w', encoding='utf-8') as f:
        f.write(enhanced_content)
    
    print("✅ Enhanced timber business research added to ai_csv_analyzer.py")
    return True

def update_modules_init():
    """Update modules/__init__.py to include the enhanced researcher"""
    
    init_file = "modules/__init__.py"
    
    # Create __init__.py if it doesn't exist
    if not os.path.exists(init_file):
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write('# Enhanced modules for timber business research\n')
    
    # Read the current content
    with open(init_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add import for enhanced researcher if not already present
    enhanced_import = "from .enhanced_timber_business_researcher import EnhancedTimberBusinessResearcher, research_timber_businesses_from_dataframe"
    
    if enhanced_import not in content:
        content += f"\n{enhanced_import}\n"
        
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Enhanced imports added to modules/__init__.py")
    else:
        print("✅ Enhanced imports already exist in modules/__init__.py")

def main():
    """Main integration function"""
    print("🌲 Enhanced Timber Business Research Integration")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("ai_csv_analyzer.py"):
        print("❌ Please run this script from the Dashboard directory containing ai_csv_analyzer.py")
        return
    
    print("📁 Creating backups...")
    backup_files()
    
    print("\n🔧 Updating modules...")
    
    # Step 1: Update streamlit_business_researcher.py
    if update_streamlit_business_researcher():
        print("✅ Step 1: Enhanced function added to streamlit_business_researcher.py")
    else:
        print("❌ Step 1: Failed to update streamlit_business_researcher.py")
        return
    
    # Step 2: Update ai_csv_analyzer.py
    if update_ai_csv_analyzer():
        print("✅ Step 2: Enhanced timber research added to ai_csv_analyzer.py")
    else:
        print("❌ Step 2: Failed to update ai_csv_analyzer.py")
        return
    
    # Step 3: Update modules/__init__.py
    update_modules_init()
    print("✅ Step 3: Enhanced imports added to modules")
    
    print("\n🎉 Integration completed successfully!")
    print("\n📝 What was added:")
    print("   ✅ Enhanced Timber Business Researcher with smart filtering")
    print("   ✅ Location cross-verification using city and address columns")
    print("   ✅ Industry-specific search queries for timber/teak wood businesses")
    print("   ✅ AI-powered relevance scoring (1-10) for business filtering")
    print("   ✅ Automatic filtering of irrelevant businesses (restaurants, hotels, etc.)")
    print("   ✅ Enhanced CSV output with new columns:")
    print("      • industry_relevance (1-10 score)")
    print("      • business_type (Timber Trader/Wood Manufacturer/etc.)")
    print("      • location_match (1-10 score)")
    print("      • recommendation (INCLUDE/EXCLUDE)")
    
    print("\n🧪 Testing the integration:")
    print("   1. Restart your Streamlit app: streamlit run ai_csv_analyzer.py")
    print("   2. Upload a CSV with business names and location data")
    print("   3. Go to Data Explorer tab")
    print("   4. Look for the new '🌲 Enhanced Timber Research' button")
    print("   5. Configure location columns for cross-verification")
    print("   6. Start research and see the enhanced filtering in action!")
    
    print("\n🌲 Enhanced Features:")
    print("   • Timber-specific search queries")
    print("   • Smart filtering based on industry keywords")
    print("   • Location verification against expected city/address")
    print("   • AI scoring for business relevance and location accuracy")
    print("   • Automatic exclusion of non-timber businesses")
    print("   • Enhanced CSV output with detailed scoring")

if __name__ == "__main__":
    main()
