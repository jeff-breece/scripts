import garminconnect
import json
from datetime import datetime, timedelta
import os

# Replace these with your Garmin Connect username and password
username = "jeffbreece@outlook.com"
password = "Jefrobaby656#"

def get_garmin_biometrics(start_date, end_date, output_folder):
    try:
        # Initialize the Garmin client
        client = garminconnect.Garmin(username, password)
        client.login()  # Log in to Garmin Connect

        # Create the output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Loop through the date range
        current_date = start_date
        while current_date <= end_date:
            cdate_str = current_date.strftime('%Y-%m-%d')
            print(f"Fetching data for {cdate_str}")

            # Fetch biometrics data for the current date
            try:
                biometrics = client.get_user_summary(cdate_str)

                # Save the data to a JSON file
                file_name = f"{output_folder}/{cdate_str}.json"
                with open(file_name, "w") as json_file:
                    json.dump(biometrics, json_file, indent=4)

            except Exception as e:
                print(f"Error fetching data for {cdate_str}: {str(e)}")

            # Move to the next day
            current_date += timedelta(days=1)

        print("Data export completed successfully.")

    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    # Define the date range (modify these dates as needed)
    start_date = datetime(2016, 1, 1)  # Start date (YYYY, M, D)
    end_date = datetime(2023, 12, 31)    # End date (YYYY, M, D)

    # Output folder for JSON files
    output_folder = "/home/jeff/data/raw/garmin_biometrics_data"

    # Run the function
    get_garmin_biometrics(start_date, end_date, output_folder)
