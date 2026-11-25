import tkinter as tk

from combo_window import ComboWindow
from promotion_window import PromotionWindow
from inbox_window import InboxWindow


class MerchantWindow(tk.Toplevel):
    def __init__(self, parent, restaurant_id, restaurant_name):
        super().__init__(parent)

        # Get the selected restaurant from the main program.
        # Pass the same restaurant details to the other windows.
        self.restaurant_id = restaurant_id
        self.restaurant_name = restaurant_name

        self.title("Merchant - " + restaurant_name)
        self.geometry("400x280")

        tk.Label(
            self,
            text=restaurant_name,
            font=("Arial", 16)
        ).pack(pady=20)

        # Keep the three tasks separate to avoid a crowded window.
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
            self.restaurant_id,
            self.restaurant_name
        )

    def open_promotions(self):
        PromotionWindow(
            self,
            self.restaurant_id,
            self.restaurant_name
        )

    def open_inbox(self):
        InboxWindow(
            self,
            self.restaurant_id,
            self.restaurant_name
        )