"""
CSV Merger Script for JustDial Integration
This script merges existing business_contacts_*.csv files with justdial_research_*.csv files
to add the justdial_whatsapp_number column to existing business contacts data.
"""

import pandas as pd
import os
import glob
from datetime import datetime

def find_csv_files(pattern):
    """Find CSV files matching a pattern"""
    files = glob.glob(pattern)
    return sorted(files, key=os.path.getmtime, reverse=True)  # Sort by modification time, newest first

def merge_business_contacts_with_justdial(business_contacts_file, justdial_research_file, output_file=None):
    """
    Merge a business contacts CSV with JustDial research CSV
    
    Args:
        business_contacts_file: Path to business_contacts_*.csv file
        justdial_research_file: Path to justdial_research_*.csv file  
        output_file: Optional output file path (if None, will create enhanced_business_contacts_*.csv)
    
    Returns:
        str: Path to the created merged file
    """
    
    print(f"📄 Loading business contacts: {business_contacts_file}")
    try:
        business_df = pd.read_csv(business_contacts_file)
        print(f"   ✅ Loaded {len(business_df)} business contact records")
    except Exception as e:
        print(f"   ❌ Error loading business contacts: {e}")
        return None
    
    print(f"📱 Loading JustDial research: {justdial_research_file}")
    try:
        justdial_df = pd.read_csv(justdial_research_file)
        print(f"   ✅ Loaded {len(justdial_df)} JustDial research records")
    except Exception as e:
        print(f"   ❌ Error loading JustDial research: {e}")
        return None
    
    # Check if justdial_whatsapp_number column already exists
    if 'justdial_whatsapp_number' in business_df.columns:
        print("   ⚠️ justdial_whatsapp_number column already exists in business contacts")
        return business_contacts_file
    
    # Check required columns
    if 'business_name' not in business_df.columns:
        print("   ❌ business_name column not found in business contacts file")
        return None
        
    if 'business_name' not in justdial_df.columns:
        print("   ❌ business_name column not found in JustDial research file")
        return None
        
    if 'justdial_phone' not in justdial_df.columns:
        print("   ❌ justdial_phone column not found in JustDial research file")
        return None
    
    # Create a mapping from JustDial data (business_name -> justdial_phone)
    # Rename justdial_phone to justdial_whatsapp_number
    justdial_mapping = justdial_df.set_index('business_name')['justdial_phone'].to_dict()
    
    print(f"🔗 Merging data...")
    print(f"   📊 Found {len(justdial_mapping)} JustDial phone mappings")
    
    # Add the justdial_whatsapp_number column to business contacts
    enhanced_df = business_df.copy()
    enhanced_df['justdial_whatsapp_number'] = enhanced_df['business_name'].map(justdial_mapping).fillna("Not found")
    
    # Count successful matches
    successful_matches = sum(1 for x in enhanced_df['justdial_whatsapp_number'] if x != "Not found")
    print(f"   ✅ Successfully matched {successful_matches} businesses with JustDial phone numbers")
    
    # Generate output filename if not provided
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(business_contacts_file))[0]
        output_file = f"enhanced_{base_name}_{timestamp}.csv"
    
    # Save the enhanced file
    try:
        enhanced_df.to_csv(output_file, index=False)
        print(f"💾 Enhanced file saved: {output_file}")
        print(f"   📊 Total records: {len(enhanced_df)}")
        print(f"   📱 With JustDial numbers: {successful_matches}")
        return output_file
    except Exception as e:
        print(f"   ❌ Error saving enhanced file: {e}")
        return None

def auto_merge_latest_files():
    """
    Automatically find and merge the latest business_contacts_*.csv with the latest justdial_research_*.csv
    """
    
    print("🔍 Auto-detecting latest CSV files...")
    
    # Find latest business contacts file
    business_files = find_csv_files("business_contacts_*.csv")
    if not business_files:
        print("❌ No business_contacts_*.csv files found")
        return None
    
    latest_business_file = business_files[0]
    print(f"📄 Latest business contacts: {latest_business_file}")
    
    # Find latest JustDial research file
    justdial_files = find_csv_files("justdial_research_*.csv")
    if not justdial_files:
        print("❌ No justdial_research_*.csv files found")
        return None
    
    latest_justdial_file = justdial_files[0]
    print(f"📱 Latest JustDial research: {latest_justdial_file}")
    
    # Merge the files
    return merge_business_contacts_with_justdial(latest_business_file, latest_justdial_file)

def merge_all_available_files():
    """
    Merge all available business_contacts_*.csv files with their corresponding justdial_research_*.csv files
    """
    
    print("🔄 Merging all available files...")
    
    business_files = find_csv_files("business_contacts_*.csv")
    justdial_files = find_csv_files("justdial_research_*.csv")
    
    if not business_files:
        print("❌ No business_contacts_*.csv files found")
        return []
    
    if not justdial_files:
        print("❌ No justdial_research_*.csv files found")
        return []
    
    merged_files = []
    
    for business_file in business_files:
        # Extract timestamp from business file to find matching JustDial file
        business_basename = os.path.splitext(os.path.basename(business_file))[0]
        
        # Try to find a JustDial file from the same day or the closest one
        best_justdial_file = justdial_files[0]  # Default to latest
        
        for justdial_file in justdial_files:
            justdial_basename = os.path.splitext(os.path.basename(justdial_file))[0]
            
            # Extract dates from filenames
            business_date = business_basename.split('_')[-2] if '_' in business_basename else ""
            justdial_date = justdial_basename.split('_')[-2] if '_' in justdial_basename else ""
            
            # If dates match, use this JustDial file
            if business_date == justdial_date:
                best_justdial_file = justdial_file
                break
        
        print(f"\n🔗 Merging:")
        print(f"   📄 Business: {business_file}")
        print(f"   📱 JustDial: {best_justdial_file}")
        
        merged_file = merge_business_contacts_with_justdial(business_file, best_justdial_file)
        if merged_file:
            merged_files.append(merged_file)
    
    return merged_files

def show_csv_summary(csv_file):
    """Show a summary of a CSV file"""
    try:
        df = pd.read_csv(csv_file)
        print(f"\n📊 Summary of {csv_file}:")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {len(df.columns)}")
        print(f"   Column names: {', '.join(df.columns.tolist())}")
        
        if 'justdial_whatsapp_number' in df.columns:
            non_empty = sum(1 for x in df['justdial_whatsapp_number'] if pd.notna(x) and x != "Not found" and x.strip())
            print(f"   JustDial WhatsApp numbers: {non_empty} out of {len(df)} ({non_empty/len(df)*100:.1f}%)")
        
    except Exception as e:
        print(f"   ❌ Error reading {csv_file}: {e}")

if __name__ == "__main__":
    print("🚀 JustDial CSV Merger Tool")
    print("="*50)
    
    # Show available files
    print("\n📁 Available files:")
    business_files = find_csv_files("business_contacts_*.csv")
    justdial_files = find_csv_files("justdial_research_*.csv")
    
    print(f"   Business contacts files: {len(business_files)}")
    for f in business_files[:3]:  # Show first 3
        print(f"     • {f}")
    if len(business_files) > 3:
        print(f"     ... and {len(business_files) - 3} more")
    
    print(f"   JustDial research files: {len(justdial_files)}")
    for f in justdial_files[:3]:  # Show first 3
        print(f"     • {f}")
    if len(justdial_files) > 3:
        print(f"     ... and {len(justdial_files) - 3} more")
    
    if not business_files or not justdial_files:
        print("\n❌ Cannot proceed: Missing required CSV files")
        exit(1)
    
    # Auto-merge latest files
    print(f"\n🔄 Auto-merging latest files...")
    merged_file = auto_merge_latest_files()
    
    if merged_file:
        print(f"\n✅ Merge completed successfully!")
        show_csv_summary(merged_file)
        
        # Show before and after comparison
        latest_business_file = find_csv_files("business_contacts_*.csv")[0]
        print(f"\n📊 Comparison:")
        print(f"   BEFORE (original business_contacts):")
        show_csv_summary(latest_business_file)
        print(f"   AFTER (enhanced with JustDial):")
        show_csv_summary(merged_file)
        
    else:
        print(f"\n❌ Merge failed")
