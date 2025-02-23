import garminconnect
import json
from datetime import datetime, timedelta
import os
import hvac

# ---------------------------
# Vault Configuration
# ---------------------------
VAULT_ADDR = "http://127.0.0.1:8200"
VAULT_TOKEN = os.getenv("VAULT_TOKEN", "your-token-here")
client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)

# Fetch Garmin credentials from Vault
try:
    vault_secrets = client.secrets.kv.v2.read_secret_version(
        path="automation_keys",
        raise_on_deleted_version=True
    )["data"]["data"]
    username = vault_secrets["GARMIN_USER_ID"]
    password = vault_secrets["GARMIN_USER_PASSWORD"]
except Exception as e:
    print(f"Error accessing Vault for Garmin credentials: {e}")
    exit(1)

# ---------------------------
# Garmin Data Export Function
# ---------------------------
def get_garmin_biometrics(start_date, end_date, output_folder):
    try:
        # Initialize the Garmin client
        client = garminconnect.Garmin(username, password)
        client.login()  # Log in to Garmin Connect

        # Create the output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

        # Loop through the date range
        current_date = start_date
        while current_date <= end_date:
            cdate_str = current_date.strftime('%Y-%m-%d')
            print(f"Fetching data for {cdate_str}")

            try:
                # Fetch biometrics data for the current date
                biometrics = client.get_user_summary(cdate_str)

                # Save the data to a JSON file
                file_name = f"{output_folder}/{cdate_str}.json"
                with open(file_name, "w") as json_file:
                    json.dump(biometrics, json_file, indent=4)

            except Exception as e:
                print(f"Error fetching data for {cdate_str}: {str(e)}")

            # Move to the next day
            current_date += timedelta(days=1)

        print("✅ Data export completed successfully.")

    except Exception as e:
        print(f"🚨 Error initializing Garmin client: {str(e)}")

# ---------------------------
# Main Execution
# ---------------------------
if __name__ == "__main__":
    try:
        # Prompt user for date range
        start_date_input = input("Enter start date (YYYY-MM-DD): ")
        end_date_input = input("Enter end date (YYYY-MM-DD): ")

        # Convert input to datetime objects
        start_date = datetime.strptime(start_date_input, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_input, "%Y-%m-%d")

        # Validate date range
        if end_date < start_date:
            print("🚨 End date cannot be before start date.")
            exit(1)

        # Output folder for JSON files
        output_folder = "/home/jeff/data/raw/garmin_biometrics_data"

        # Run the function
        get_garmin_biometrics(start_date, end_date, output_folder)

    except ValueError as ve:
        print(f"🚨 Invalid date format: {ve}")
    except Exception as e:
        print(f"🚨 An unexpected error occurred: {e}")
