import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# LinkedIn credentials (store securely in env variables)
LINKEDIN_EMAIL = "jeffbreece@outlook.com"
LINKEDIN_PASSWORD = "Jefrobaby656#"

# LinkedIn Activity Page for Likes
ACTIVITY_URL = "https://www.linkedin.com/in/me/recent-activity/likes/"

# Initialize WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

try:
    # Step 1: Open LinkedIn login page
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)

    # Step 2: Enter email
    driver.find_element(By.ID, "username").send_keys(LINKEDIN_EMAIL)

    # Step 3: Enter password
    driver.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD, Keys.RETURN)
    time.sleep(5)  # Give some time for the page transition

    # Step 4: Wait dynamically for MFA process (up to 60 seconds)
    try:
        print("🔐 Waiting for MFA to complete...")
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.ID, "global-nav"))  # Wait for the LinkedIn main page
        )
        print("✅ MFA complete, proceeding...")
    except Exception:
        print("⚠️ MFA timeout or issue detected. Continuing...")

    # Step 5: Navigate to the Likes Activity Page
    driver.get(ACTIVITY_URL)
    time.sleep(5)

    # Step 6: Unlike all liked posts
    while True:
        like_buttons = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Unlike')]")
        if not like_buttons:
            print("✅ No more likes to remove.")
            break

        for button in like_buttons:
            try:
                driver.execute_script("arguments[0].click();", button)
                time.sleep(2)  # Wait to avoid detection
            except Exception as e:
                print("⚠️ Error clicking unlike:", e)

        # Scroll down to load more liked posts
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(3)

except Exception as e:
    print("❌ Error:", e)

finally:
    driver.quit()
    print("🔄 LinkedIn unlike process completed.")

