from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import re
recipes = {}
items = {}


driver = webdriver.Chrome()
driver.get('https://mouseypounds.github.io/stardew-checkup/')
driver.implicitly_wait(5)

# uploads the save file to the website
sys_user = input("Enter your system username (the one that shows up in your path): ")
save_name = input("Enter the name of your save file: ")
upload_file = driver.find_element(By.ID, 'file_select')
upload_file.send_keys(r'C:\Users\\' + sys_user+ '\AppData\Roaming\StardewValley\Saves\\' + save_name + '\\' + save_name)

show_craft_details = driver.find_element(By.ID, 'toggle_Crafting_details')
show_craft_details.click()

hide_summary = driver.find_element(By.ID, 'toggle_Crafting_summary')
hide_summary.click()

unfiltered = driver.find_elements(By.CLASS_NAME, 'need')

# filters out only the "Left to craft:" list
for element in unfiltered:
    soup = BeautifulSoup(element.get_attribute('innerHTML'), 'lxml')
    if soup.html.body.p.text == 'Left to craft:':
        filtered = element

filtered = BeautifulSoup(filtered.get_attribute('innerHTML'), 'lxml')
left_to_craft = filtered.find_all('a')

# traversing through all the links in the list and extraction of the ingredients
for item in left_to_craft:
    url = driver.find_element(By.LINK_TEXT, item.text)
    url.click()
    title = driver.find_element(By.CLASS_NAME, 'firstHeading')
    greendivs = driver.find_elements(By.TAG_NAME, 'tr')

    # iterates through all the <tr> elements until it finds thhe ingredients row
    for div in greendivs:
        soup = BeautifulSoup(div.get_attribute('innerHTML'), 'lxml')
        try:
            items_required = []
            if soup.html.body.td.text == "Ingredients":
                # finds all items needed to craft in the 'Ingredients' row
                ingredients = soup.find_all('span', class_ = 'nametemplate')

                for ticker, item in enumerate(ingredients):
                    links = soup.find_all('a')
                    quantity = re.search('\d+', item.text).group()
                    ingr = [links[ticker].text, quantity, 'https://stardewvalleywiki.com'+links[ticker]['href']]
                    items_required.append(ingr)
                
                """
                Adds every item in the 'Left to craft:' list in the recipes dictionary with their ingredients
                the format:
                item_name: [[ingredient1_name, ingredient1_quantity, ingredient1_link], [ingredient2_name, ingredient2_quantity, ingredient2_link]]
                """
                recipes[title.get_attribute('innerHTML')] = items_required
        except (AttributeError):
            continue
    driver.back()

"""
makes another dictionary called 'items' which gives the total quantity of each ingredient you need to craft all the remaining items
format:
ingredient_name: quantity
"""
for key, value in recipes.items():
    for ingredient in value:
        if ingredient[0] in items:
            items[ingredient[0]] = str(int(items[ingredient[0]]) + int(ingredient[1]))
        else:
            items[ingredient[0]] = ingredient[1]

# writes the item dictionary into a text file called 'items.txt' in the cwd
with open('items.txt', mode='w') as fp:
    for keys, values in items.items():
        fp.writelines(f"{keys} : {values}\n")
    print("All ingredients listed in 'items.txt' file in your current directory!")

time.sleep(100)