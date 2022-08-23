import re
from typing import List, Tuple


#Step 1 clean raw text
def clean_raw_text(raw_text: str) -> str:

    #Clean adding information
    token = r"[\(-].*[\)-]"
    clean_text = re.sub(token, "", clean_text)

    #Clean phone
    phone_token = (
        r"(\(?\+?\d{2,2}\)?|0)[\s\-\.]*\d{3}[\s\-\.]*\d{3}[\s\-\.]*\d{3}\b")
    clean_text = re.sub(phone_token, "", clean_text)

    return clean_text.lower().strip()


#Step 2 get list price and food
def get_price_and_food(clean_text: str):
    ents = clean_text.split('\n')

    price_token = r"(\d\s?)+k?|(\d+\s?[\.,]+)+k?|miễn\sphí|free"

    list_price = []
    list_food = []

    for idx, ent in enumerate(ents):
        ent = ent.lower()
        if re.search(price_token, ent):
            #format price
            ent = ent.replace('o', '0').replace('k', '000')
            ent = re.sub(r'[^\d]', '', ent)
            list_price += [idx, ent]
        else:
            list_food += [idx, ent]

    return list_food, list_price


#Step 3 mapping price and food
def map(foods: list, prices: list) -> List[List[str]]:

    menu = []

    while foods[0][0] < prices[0][0]-1:
        menu.append([foods[0][1], "NO GIVEN"])
        foods.pop(0)

    n_prices = len(prices)
    i = 0
    while i < n_prices and foods:
        current_price_ent = prices[i]
        next_price_ent = prices[min(i + 1, n_prices)]

        dis_price = next_price_ent[0] - current_price_ent[0]

        #Skip current price if foods bellow this price
        if foods[0][0] < current_price_ent[0]:
            i += 1
            continue

        #Mapping by size
        if dis_price == 1:
            menu.append([foods[0][1], current_price_ent[1] + " size S"])
            menu.append([foods[0][1], next_price_ent[1] + " size M"])
            i += 2

            if i + 2 < n_prices:
                next_price_ent_1 = prices[i]
                dis_price_1 = next_price_ent_1[0] - next_price_ent[0]

                if dis_price_1 == 1:
                    menu.append([foods[0][1], next_price_ent_1[1] + " size L"])
                    i += 1

            foods.pop(0)

        #Map near
        elif dis_price == 2 or dis_price == 0:
            menu.append([foods[0][1], current_price_ent[1]])
            foods.pop(0)
            i += 1

        #Mappng group
        elif dis_price > 2:
            for j in range(dis_price):
                menu.append([foods[0][1], current_price_ent[1]])
                foods.pop(0)
            i += 1

    while foods:
        menu.append([foods[0][1], "NO GIVEN"])
        foods.pop(0)

    return menu
