import mysql.connector
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import os as os_env

# ---------------- LOAD ENV ----------------
load_dotenv()

db_config = {
    "host": os_env.getenv("DB_HOST"),
    "port": os_env.getenv("DB_PORT"),
    "user": os_env.getenv("DB_USER"),
    "password": os_env.getenv("DB_PASS"),
    "database": os_env.getenv("DB_NAME"),
}


# ---------------- DB CONNECTION ----------------
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# ---------------- SQL QUERIES ----------------
queries = {

    "total_verification": """
        SELECT COUNT(*) FROM user_verification_journeys
        WHERE DATE(created_at)=CURDATE()
        AND status IN ('verified','failed')
    """,

    "success_verification": """
        SELECT COUNT(*) FROM user_verification_journeys
        WHERE DATE(created_at)=CURDATE()
        AND status='verified'
    """,

    "failed_verification": """
        SELECT COUNT(*) FROM user_verification_journeys
        WHERE DATE(created_at)=CURDATE()
        AND status='failed'
    """,

    "active_flow": """
        SELECT COUNT(*) FROM kyc_flow
    """,

    "basic_success": """
        SELECT COUNT(*) FROM user_verification_journeys
        WHERE DATE(created_at)=CURDATE()
        AND user_journey_flow='basic_flow'
        AND status='verified'
    """,

    "basic_failed": """
        SELECT COUNT(*) FROM user_verification_journeys
        WHERE DATE(created_at)=CURDATE()
        AND user_journey_flow='basic_flow'
        AND status='failed'
    """,

    "premium_success": """
        SELECT COUNT(*) FROM user_verification_journeys
        WHERE DATE(created_at)=CURDATE()
        AND user_journey_flow='premium_flow'
        AND status='verified'
    """,

    "premium_failed": """
        SELECT COUNT(*) FROM user_verification_journeys
        WHERE DATE(created_at)=CURDATE()
        AND user_journey_flow='premium_flow'
        AND status='failed'
    """,

    "Daily_trial_usage_basic": """
        SELECT COUNT(*) FROM free_trial_history
        WHERE DATE(created_at)=CURDATE()    
        AND flow_type='basic'    
    """,

    "Daily_trial_usage_premium": """
        SELECT COUNT(*) FROM free_trial_history
        WHERE DATE(created_at)=CURDATE()
        AND flow_type='premium'
    """,

    "daily_registrations": """
        SELECT COUNT(*) FROM client_details
        WHERE DATE(created_at)=CURDATE()
    """,

    "total_revenue": """
    SELECT
        (
            SUM(CASE 
                WHEN user_journey_flow = 'basic_flow'
                     AND status = 'verified'
                THEN 10 ELSE 0 END)
            +
            SUM(CASE 
                WHEN user_journey_flow = 'premium_flow'
                     AND status = 'verified'
                THEN 18 ELSE 0 END)
        )
    FROM user_verification_journeys
    WHERE DATE(created_at) = CURDATE()
"""

}

# ---------------- EXECUTE ----------------
results = {}

for key, query in queries.items():
    cursor.execute(query)
    results[key] = cursor.fetchone()[0]

# ---------------- DATE ----------------
today_date = datetime.now().strftime("%d-%B-%Y")

# ---------------- DATAFRAME ----------------
result_df = pd.DataFrame({
    "Date": [today_date],
    "Total Verification": [results["total_verification"]],
    "Success Verification": [results["success_verification"]],
    "Failed Verification": [results["failed_verification"]],
    "Active Flow": [results["active_flow"]],
    "Basic Success": [results["basic_success"]],
    "Basic Failed": [results["basic_failed"]],
    "Premium Success": [results["premium_success"]],
    "Premium Failed": [results["premium_failed"]],
    "Daily Registrations": [results["daily_registrations"]]
})

# ---------------- EXCEL ----------------
file_path = "kyc_daily_report.xlsx"

if os.path.exists(file_path):

    existing_df = pd.read_excel(file_path)

    if today_date not in existing_df["Date"].astype(str).values:
        updated_df = pd.concat([existing_df, result_df], ignore_index=True)
        updated_df.to_excel(file_path, index=False)

else:
    result_df.to_excel(file_path, index=False)

print("Report updated for", today_date)
