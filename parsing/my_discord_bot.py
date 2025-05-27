import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException



driver = webdriver.Chrome()

driver.get("https://www.reg.uci.edu/perl/WebSoc")

url = driver.current_url

driver.implicitly_wait(3)


SELECT_XPATH = '/html/body/form/table/tbody/tr[4]/td[3]/select'
SEARCH_XPATH = '/html/body/form/p[2]/input[1]'
BOOKMARK_XPATH='/html/body/dl[1]/dd[4]/a'
URL_XPATH='/html/body/dl[1]/dd[5]/a'

wait = WebDriverWait(driver, 10)

# Cache the visible labels once so we know how many choices exist
dropdown   = Select(driver.find_element(By.XPATH, SELECT_XPATH))
labels = [opt.text.strip()
          for opt in dropdown.options
          if not opt.text.startswith("Include All")]

for label in labels:
    # 1️⃣  Re-find a fresh <select> and wrap it
    dropdown = Select(driver.find_element(By.XPATH, SELECT_XPATH))  
    dropdown.select_by_visible_text(label)           # pick current dept

    #print(f"Selected: {label.split(' .')[0]}")
    
    # 2️⃣  Click Search
    driver.find_element(By.XPATH, SEARCH_XPATH).click()

    
    # … scrape / process results here …
    #driver.find_element(By.XPATH, BOOKMARK_XPATH).click()
    #time.sleep(1)

    # locate the <a> element

    #edge case, if there are no courses matched for your search criteria
    try:


        bookmark_el = driver.find_element(By.LINK_TEXT, "MyWebSocResults")

# pull out the URL it points to
        href = bookmark_el.get_attribute("href")               # real URL string
        #print("href:", href)                                   # sanity-check

# --- QUICK way ---
        dept = href.split("Dept=")[1]
        print(f'"{label.split(' .')[0]}" : "{dept}",')                 # works if Dept= is always there
        #print(dept)

    
    # 3️⃣  Go back to the non-unique page
    #driver.back()

        
    except NoSuchElementException:
        print("") 
          
        
    finally:
        driver.back() #go back to form page
    # 4️⃣  Wait until the form page is really back before looping
        wait.until(
            EC.presence_of_element_located((By.XPATH, SELECT_XPATH))
        )
    #print("Success")


driver.quit()