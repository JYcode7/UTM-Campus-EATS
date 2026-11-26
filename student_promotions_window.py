import tkinter as tk
from tkinter import ttk


class StudentPromotionsWindow(tk.Toplevel):
    def __init__(self, parent, data, restaurants):
        super().__init__(parent)

        self.data = data
        self.restaurants = restaurants
        self.promotion_details = {}

        self.title("Restaurant Promotions")
        self.geometry("650x450")

        top = tk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)

        tk.Label(top, text="Restaurant").pack(side="left")

        self.restaurant_choice = ttk.Combobox(
            top,
            values=[row[1] for row in restaurants],
            state="readonly",
            width=25
        )
        self.restaurant_choice.pack(side="left", padx=10)

        if restaurants:
            self.restaurant_choice.current(0)

        self.restaurant_choice.bind(
            "<<ComboboxSelected>>",
            self.load_promotions
        )

        tk.Button(
            top,
            text="Refresh",
            command=self.load_promotions
        ).pack(side="left")

        table_frame = tk.Frame(self)
        table_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=("title",),
            show="headings",
            selectmode="browse",
            height=6
        )
        self.tree.heading("title", text="Promotion Title")
        self.tree.column("title", width=500)
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.show_promotion
        )

        tk.Label(self, text="Description").pack(
            anchor="w",
            padx=10
        )

        self.description = tk.Text(
            self,
            height=7,
            wrap="word",
            state="disabled"
        )
        self.description.pack(fill="x", padx=10, pady=10)

        self.load_promotions()

    def load_promotions(self, event=None):
        # Clear the previous restaurant's information first.
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.promotion_details.clear()

        self.description.config(state="normal")
        self.description.delete("1.0", tk.END)
        self.description.config(state="disabled")

        index = self.restaurant_choice.current()

        if index < 0:
            return

        restaurant_id = self.restaurants[index][0]

        # Read the same promotions created by the merchant.
        for promotion_id, title, content in self.data.get_promotions(
            restaurant_id
        ):
            self.tree.insert(
                "",
                "end",
                iid=str(promotion_id),
                values=(title,)
            )
            self.promotion_details[str(promotion_id)] = content

    def show_promotion(self, event):
        selection = self.tree.selection()

        if not selection:
            return

        content = self.promotion_details.get(
            selection[0], ""
        )

        # Students can read promotions but cannot edit them.
        self.description.config(state="normal")
        self.description.delete("1.0", tk.END)
        self.description.insert("1.0", content)
        self.description.config(state="disabled")
