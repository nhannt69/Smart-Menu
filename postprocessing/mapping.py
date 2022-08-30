import re
from typing import List, Tuple


# Step 1 clean raw text
def clean_raw_text(raw_text: str) -> str:
    clean_text = raw_text.lower()

    # Remove anything in parentheses
    token = r"\([^)]*\)"
    clean_text = re.sub(token, "", raw_text)

    # Remove hyperlink
    clean_text = re.sub(
        r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""",
        " ",
        clean_text,
    )

    # Clean phone
    phone_token = r"(\(?\+?\d{2,2}\)?|0)[\s\-\.]*\d{3}[\s\-\.]*\d{3}[\s\-\.]*\d{3}\b"
    clean_text = re.sub(phone_token, "", clean_text)

    # Remove time entities
    token = r"\d{1,2}\s?(h|giờ|phút)\s?\d{0,2}\s?(phút|minutes?)?}"
    clean_text = re.sub(token, "", clean_text)

    # Split ent between foods and prices
    token = r"(\D+\s*)(\s)([\d\,\.\w]{2,})"
    clean_text = re.sub(token, r"\g<1>\n\g<3>", clean_text)

    # Remove size entities
    token = r"size|\s+x{0,2}[lms][\.\s:-]+|(nhỏ|vừa|lớn|bự|to|small|medium|big|large):?"
    clean_text = re.sub(token, "\n", clean_text)



    return clean_text.strip()


# Step 2 get list price and food
def get_price_and_food(ents):
    # price_token = r"(\d\s?){2,}k?|(\d\s?[\.,]+)+k?|miễn\sphí|free"
    price_token = r"\d{4,}|\d+k|[\d.,]{5,}|miễn\sphí|free"

    list_price = []
    list_food = [""] * len(ents)

    for idx, ent in enumerate(ents):
        ent = ent.lower()

        # check if current token is price
        price_ent = re.search(price_token, ent)
        if price_ent:
            # format price
            price_ent = price_ent.group(0)
            price_ent = price_ent.replace("o", "0").replace("k", "000")
            price_ent = re.sub(r"[^\d]", "", price_ent)
            list_price.append([idx, price_ent])
        else:
            if ent:
                list_food[idx] = ent

    return [list_food, list_price]


def get_current_food(foods: List, current_price_idx: int):
    current_food = foods[current_price_idx - 1]

    price_token = r"\d{4,}|\d+k|[\d.,]{5,}"
    i = current_price_idx - 1
    while foods[i] != None and not re.search(price_token, foods[i]):
        current_food = foods[i] + " " + current_food
        i -= 1

    return current_food

def get_size(text):
    text = text.lower()
    size_token = r"\s+s|nhỏ|small"

    quantity_token = r"size|set"

    size = re.findall(size_token, text)
    quantity = re.findall(quantity_token,text)

    if not size:
        return ["S", "M", "L"]

    size = size[0]
    quantity = quantity[0] if quantity else 'size'
    if re.match(r"\s+s", size):
        return [quantity + ' s', quantity + ' m', quantity + ' l']
    if re.match(r'small', size):
        return [quantity + ' small', quantity + ' medium', quantity + ' large']
    if re.match(r'nhỏ', size):
        return [quantity + ' nhỏ', quantity + ' vừa', quantity + ' lớn']

# Step 3 mapping price and food
def map(foods: list, prices: list, sizes:list) -> List[List[str]]:
    menu = []

    n_prices = len(prices)

    #check if list price is null
    if not prices:
        return [[f, 'NOT GIVEN'] for f in foods if f]


    #Clean header content
    for idx, f in enumerate(foods):
        if idx < prices[0][0] - 1:
            foods[idx] = ''
        else:
            break

    # If only has one price on image, mapping all the food to this price
    if n_prices == 1:
        for idx, f in enumerate(foods[:-5]):
            if idx >= prices[0][0] - 1 and f:
                menu.append([f, prices[0][1]])
                foods[idx] = ""
        return menu

    i = 0
    while i < n_prices:
        current_price_ent = prices[i]
        current_price_ent_idx = current_price_ent[0]
        next_price_ent = prices[min(i + 1, n_prices - 1)]

        dis_price = next_price_ent[0] - current_price_ent_idx

        # Mapping by size
        if dis_price == 1:
            current_food = foods[current_price_ent_idx - 1]

            menu.append([current_food + sizes[0], current_price_ent[1]])
            menu.append([current_food + sizes[1], next_price_ent[1]])
            i += 2

            if i + 2 < n_prices:
                next_price_ent_1 = prices[i]
                dis_price_1 = next_price_ent_1[0] - next_price_ent[0]

                if dis_price_1 == 1:
                    menu.append([current_food + sizes[2], next_price_ent_1[1]])
                    i += 1

            foods[current_price_ent_idx - 1] = ""

        # Map near
        elif dis_price == 2 or dis_price == 0 or dis_price == 3:
            menu.append([foods[current_price_ent_idx - 1], current_price_ent[1]])
            foods[current_price_ent_idx - 1] = ""
            i += 1

        # Mapping group
        elif dis_price > 2:
            if i == n_prices - 1:
                for idx in range(current_price_ent_idx - 1, len(foods)):
                    food = foods[idx]
                    if food:
                        menu.append([food, current_price_ent[1]])
                        foods[idx] = ""
            else:
                for idx in range(
                    current_price_ent_idx - 1, current_price_ent_idx + dis_price
                ):
                    food = foods[idx]
                    if food:
                        menu.append([food, current_price_ent[1]])
                        foods[idx] = ""
            i += 1

    return menu
