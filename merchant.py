import tkinter as tk
from tkinter import ttk

from menu_csv import check_combo
from combo_window import ComboWindow
from promotion_window import PromotionWindow
from inbox_window import InboxWindow
from student_promotions_window import StudentPromotionsWindow
from student_suggestion_window import StudentSuggestionWindow


class SessionData:
    def __init__(self):
        # Keep the data here so all windows use the same lists.
        self.restaurants = [
            (1, "Subway"),
            (2, "Tim Hortons"),
            (3, "Harvey")
        ]

        self.combos = []
        self.promotions = []
        self.suggestions = []

        self.next_combo_id = 1
        self.next_promotion_id = 1
        self.next_message_id = 1

    def get_menu(self, restaurant_id):
        # Only return combos belonging to this restaurant.
        result = []

        for row in self.combos:
            if row[1] == restaurant_id:
                result.append((row[0], row[2], row[3], row[4]))

        return result

    def add_menu_items(self, restaurant_id, items):
        checked = []
        names = set()

        for row in self.get_menu(restaurant_id):
            names.add(row[1].lower())

        # Check every item before adding anything.
        for name, price, discount in items:
            item = check_combo(name, str(price), str(discount))

            if item[0].lower() in names:
                raise ValueError(
                    "This restaurant already has a combo with that name."
                )

            names.add(item[0].lower())
            checked.append(item)

        for name, price, discount in checked:
            self.combos.append((
                self.next_combo_id,
                restaurant_id,
                name,
                price,
                discount
            ))
            self.next_combo_id += 1

    def update_menu(self, restaurant_id, item_id, name, price, discount):
        name, price, discount = check_combo(
            name, str(price), str(discount)
        )

        # Another combo in this restaurant should not use the same name.
        for row in self.combos:
            if (
                row[1] == restaurant_id
                and row[0] != item_id
                and row[2].lower() == name.lower()
            ):
                raise ValueError(
                    "This restaurant already has a combo with that name."
                )

        for index, row in enumerate(self.combos):
            if row[0] == item_id and row[1] == restaurant_id:
                self.combos[index] = (
                    item_id,
                    restaurant_id,
                    name,
                    price,
                    discount
                )
                return True

        return False

    def delete_menu(self, restaurant_id, item_id):
        # Check both IDs before deleting a record.
        for index, row in enumerate(self.combos):
            if row[0] == item_id and row[1] == restaurant_id:
                self.combos.pop(index)
                return True

        return False

    def get_promotions(self, restaurant_id):
        result = []

        for row in self.promotions:
            if row[1] == restaurant_id:
                result.append((row[0], row[2], row[3]))

        return result

    def add_promotion(self, restaurant_id, title, content):
        self.promotions.append((
            self.next_promotion_id,
            restaurant_id,
            title,
            content
        ))
        self.next_promotion_id += 1

    def update_promotion(self, restaurant_id, promotion_id, title, content):
        for index, row in enumerate(self.promotions):
            if row[0] == promotion_id and row[1] == restaurant_id:
                self.promotions[index] = (
                    promotion_id,
                    restaurant_id,
                    title,
                    content
                )
                return True

        return False

    def delete_promotion(self, restaurant_id, promotion_id):
        for index, row in enumerate(self.promotions):
            if row[0] == promotion_id and row[1] == restaurant_id:
                self.promotions.pop(index)
                return True

        return False

    def add_suggestion(self, restaurant_id, student_id, student_name, content):
        self.suggestions.append((
            self.next_message_id,
            restaurant_id,
            student_id,
            student_name,
            content
        ))
        self.next_message_id += 1

    def get_suggestions(self, restaurant_id):
        result = []

        # Messages for other restaurants are not included.
        for row in self.suggestions:
            if row[1] == restaurant_id:
                result.append((row[0], row[3], row[4]))

        return result


class MerchantWindow(tk.Toplevel):
    def __init__(self, parent, data, restaurant_id, restaurant_name):
        super().__init__(parent)

        self.data = data
        self.restaurant_id = restaurant_id
        self.restaurant_name = restaurant_name

        self.title("Merchant - " + restaurant_name)
        self.geometry("400x280")

        tk.Label(
            self,
            text=restaurant_name,
            font=("Arial", 16)
        ).pack(pady=20)

        # Open a separate window for each task.
        tk.Button(
            self,
            text="Manage Combos",
            width=25,
            command=self.open_combos
        ).pack(pady=8)

        tk.Button(
            self,
            text="Manage Promotions",
            width=25,
            command=self.open_promotions
        ).pack(pady=8)

        tk.Button(
            self,
            text="Suggestion Inbox",
            width=25,
            command=self.open_inbox
        ).pack(pady=8)

    def open_combos(self):
        ComboWindow(
            self,
            self.data,
            self.restaurant_id,
            self.restaurant_name
        )

    def open_promotions(self):
        PromotionWindow(
            self,
            self.data,
            self.restaurant_id,
            self.restaurant_name
        )

    def open_inbox(self):
        InboxWindow(
            self,
            self.data,
            self.restaurant_id,
            self.restaurant_name
        )


class MerchantPreview(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("UTM Campus EATS")
        self.geometry("450x330")

        # Pass this same object to every window.
        self.data = SessionData()

        tk.Label(
            self,
            text="Choose a restaurant to manage:"
        ).pack(pady=(20, 5))

        self.choice = ttk.Combobox(
            self,
            values=[row[1] for row in self.data.restaurants],
            state="readonly"
        )
        self.choice.pack(pady=8)
        self.choice.current(0)

        tk.Button(
            self,
            text="Open Merchant Window",
            command=self.open_merchant
        ).pack(pady=8)

        tk.Button(
            self,
            text="Browse Promotions as Student",
            command=self.open_promotions
        ).pack(pady=8)

        tk.Button(
            self,
            text="Send Suggestion as Student",
            command=self.open_suggestion
        ).pack(pady=8)

    def open_merchant(self):
        restaurant_id, restaurant_name = (
            self.data.restaurants[self.choice.current()]
        )

        MerchantWindow(
            self,
            self.data,
            restaurant_id,
            restaurant_name
        )

    def open_promotions(self):
        StudentPromotionsWindow(
            self,
            self.data,
            self.data.restaurants
        )

    def open_suggestion(self):
        # Use a sample student until the main program supplies a student.
        StudentSuggestionWindow(
            self,
            self.data,
            1,
            "Sample Student",
            self.data.restaurants
        )


# Importing this file should not open a window.
if __name__ == "__main__":
    MerchantPreview().mainloop()
