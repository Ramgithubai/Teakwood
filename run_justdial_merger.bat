@echo off
echo ========================================
echo    JustDial CSV Merger Tool
echo ========================================
echo.
echo This will merge your business_contacts_*.csv files
echo with justdial_research_*.csv files to add the
echo justdial_whatsapp_number column.
echo.

echo Testing current setup...
python test_csv_merge.py

echo.
echo ========================================
echo If the test passed, the merger is ready!
echo.
echo Available commands:
echo 1. python merge_justdial_csv.py - Run the merger
echo 2. python test_csv_merge.py - Test the setup
echo ========================================
pause
