import csv
import math


def check_combo(combo, price_text, discount_text):
    combo = combo.strip()

    if not combo:
        raise ValueError("Enter a combo name.")

    # Accept the percentage sign used in our CSV.
    discount_text = discount_text.strip()

    if discount_text.endswith("%"):
        discount_text = discount_text[:-1].strip()

    try:
        price = float(price_text)
        discount = float(discount_text or "0")
    except ValueError:
        raise ValueError("Price and discount must be numbers.")

    if not math.isfinite(price) or price < 0:
        raise ValueError("Enter a valid price of zero or more.")

    if not math.isfinite(discount) or not 0 <= discount <= 100:
        raise ValueError("Discount must be between 0 and 100.")

    return combo, round(price, 2), discount


def read_menu_csv(filename, restaurant_name):
    combos = []
    current_restaurant = ""
    seen_names = set()

    skipped = 0
    duplicates = 0

    restaurant_name = restaurant_name.strip()

    if not restaurant_name:
        raise ValueError("Select a restaurant first.")

    with open(
        filename,
        newline="",
        encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)

        required_columns = [
            "Restaurant",
            "Combo",
            "Price",
            "Discount"
        ]

        for column in required_columns:
            if not reader.fieldnames or column not in reader.fieldnames:
                raise ValueError("Missing CSV column: " + column)

        for number, row in enumerate(reader, start=2):
            restaurant = (row.get("Restaurant") or "").strip()
            combo = (row.get("Combo") or "").strip()
            price = (row.get("Price") or "").strip()
            discount = (row.get("Discount") or "").strip()

            if row.get(None):
                raise ValueError(
                    f"Row {number}: too many columns."
                )

            if not any([restaurant, combo, price, discount]):
                continue

            # A blank restaurant cell uses the name above it.
            if restaurant:
                current_restaurant = restaurant

            if not current_restaurant:
                raise ValueError(
                    f"Row {number}: restaurant name is missing."
                )

            # Only read combos for the selected restaurant.
            if current_restaurant.lower() != restaurant_name.lower():
                skipped += 1
                continue

            try:
                item = check_combo(combo, price, discount)
            except ValueError as error:
                raise ValueError(f"Row {number}: {error}")

            if item[0].lower() in seen_names:
                duplicates += 1
                continue

            seen_names.add(item[0].lower())
            combos.append(item)

    # Return the data after checking all matching rows.
    return combos, skipped, duplicates
