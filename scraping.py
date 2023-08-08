from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#setup chrome options
chrome_options = Options()
chrome_options.add_argument("--headless") # Ensure GUI is off
chrome_options.add_argument("--no-sandbox")
chrome_service = ChromeService('~/workspace/mg_cedh_analysis/chromedriver/chrome-linux64/chrome')

driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

driver.get("https://www.mtgtop8.com/format?f=cEDH")

#making sure that page is fully rendered by locating table
elem = WebDriverWait(driver,5).until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div/table/tbody/tr/td[1]/div[6]/div[2]/div[3]/div/div[2]/a"))).get_attribute('href')

#storing urls of commander archetypes (table, left side)
commander_archetype_elements = driver.find_elements(By.XPATH, '//a[contains(@href,"archetype")]')

cedh_cards = {}

for commander_archetype in commander_archetype_elements:
    
    commander_archetype_link = commander_archetype.get_attribute('href')
    driver_commander_archetype_link = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver_commander_archetype_link.get(commander_archetype_link)
    archetype_specific_deck_elements = driver_commander_archetype_link.find_elements(By.XPATH, '//a[contains(@href,"event")]')

    correct_archetype_specific_deck_links = []
    for single_deck in archetype_specific_deck_elements:
        correct_archetype_specific_deck_links.append(single_deck.get_attribute('href'))
    correct_archetype_specific_deck_links = correct_archetype_specific_deck_links[1::2]
    
    for unique_deck_link in correct_archetype_specific_deck_links:

        driver_unique_deck_link = webdriver.Chrome(service=chrome_service, options=chrome_options)
        driver_unique_deck_link.get(unique_deck_link)
        
        card_elements = driver_unique_deck_link.find_elements(By.XPATH, "//div[@class='deck_line hover_tr']")

        #data cleaning for commander format
        #To-do: additional if excluding str "Mountain", "Forest" etc.
        for card in card_elements:
            crd = card.text.strip("1 ")
            if crd.split(" ")[0].isnumeric() == False:
                cedh_cards[crd] = cedh_cards.get(crd,0)+1
        driver_unique_deck_link.close()
          
    driver_commander_archetype_link.close()
    
driver.quit()

#sorting by frequency in descending order
cedh_cards_sorted = dict(sorted(cedh_cards.items(), key=lambda x: x[1], reverse=True))

#writing analysis to output file
with open('cedh_meta_analysis', 'w') as file:
    for k, v in cedh_cards_sorted.items():
        file.write(str(k) + ": " + str(v) + '\n')
file.close() 