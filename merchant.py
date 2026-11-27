import csv
import math
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


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
    restaurant_name = restaurant_name.strip().lower().replace("’", "'")
    if not restaurant_name:
        raise ValueError("Select a restaurant first.")
    # Our CSV uses Harvey, but the shared database uses Harvey's.
    if restaurant_name == "harvey":
        restaurant_name = "harvey's"
    with open(filename, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for column in ["Restaurant", "Combo", "Price", "Discount"]:
            if not reader.fieldnames or column not in reader.fieldnames:
                raise ValueError("Missing CSV column: " + column)
        for number, row in enumerate(reader, start=2):
            restaurant = (row.get("Restaurant") or "").strip()
            combo = (row.get("Combo") or "").strip()
            price = (row.get("Price") or "").strip()
            discount = (row.get("Discount") or "").strip()
            if row.get(None):
                raise ValueError(f"Row {number}: too many columns.")
            if not any([restaurant, combo, price, discount]):
                continue
            # A blank restaurant cell uses the name from the row above.
            if restaurant:
                current_restaurant = restaurant
            if not current_restaurant:
                raise ValueError(f"Row {number}: restaurant name is missing.")
            csv_name = current_restaurant.lower().replace("’", "'")
            if csv_name == "harvey":
                csv_name = "harvey's"
            if csv_name != restaurant_name:
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
    # Return the data only after all matching rows pass the checks.
    return combos, skipped, duplicates


def make_table(parent, columns, headings):
    # Several windows need the same table and scrollbar.
    frame = tk.Frame(parent)
    frame.pack(fill="both", expand=True, padx=10, pady=10)
    tree = ttk.Treeview(frame, columns=columns, show="headings",
                        selectmode="browse", height=6)
    for index in range(len(columns)):
        column = columns[index]
        tree.heading(column, text=headings[index])
        tree.column(column, width=180)
    tree.pack(side="left", fill="both", expand=True)
    scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scroll.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scroll.set)
    return tree


class SessionData:
    def __init__(self):
        self.combos = []
        self.next_combo_id = 1

    def get_menu(self, restaurant_id):
        result = []
        for row in self.combos:
            if row[1] == restaurant_id:
                result.append((row[0], row[2], row[3], row[4]))
        return result

    def add_menu_items(self, restaurant_id, items):
        # Check the full list first so an invalid row does not leave half an import.
        checked = []
        names = set()
        for row in self.get_menu(restaurant_id):
            names.add(row[1].lower())
        for name, price, discount in items:
            item = check_combo(name, str(price), str(discount))
            if item[0].lower() in names:
                raise ValueError("This restaurant already has a combo with that name.")
            names.add(item[0].lower())
            checked.append(item)
        for name, price, discount in checked:
            self.combos.append((self.next_combo_id, restaurant_id,
                                name, price, discount))
            self.next_combo_id += 1

    def update_menu(self, restaurant_id, item_id, name, price, discount):
        name, price, discount = check_combo(name, str(price), str(discount))
        for row in self.combos:
            if (row[1] == restaurant_id and row[0] != item_id
                    and row[2].lower() == name.lower()):
                raise ValueError("This restaurant already has a combo with that name.")
        for index, row in enumerate(self.combos):
            if row[0] == item_id and row[1] == restaurant_id:
                self.combos[index] = (item_id, restaurant_id, name, price, discount)
                return True
        return False

    def delete_menu(self, restaurant_id, item_id):
        # Check both IDs so another restaurant's record is not changed.
        for index, row in enumerate(self.combos):
            if row[0] == item_id and row[1] == restaurant_id:
                self.combos.pop(index)
                return True
        return False


class ComboWindow(tk.Toplevel):
    def __init__(self, parent, data, restaurant_id, restaurant_name):
        super().__init__(parent)
        self.data = data
        self.restaurant_id = restaurant_id
        self.restaurant_name = restaurant_name
        self.selected_id = None
        self.title("Combos and Discounts - " + restaurant_name)
        self.geometry("740x450")
        self.tree = make_table(self, ("combo", "price", "discount"),
                               ("Combo", "Price (CAD)", "Discount (%)"))
        self.tree.bind("<<TreeviewSelect>>", self.select_combo)
        form = tk.Frame(self)
        form.pack(fill="x", padx=10)
        # Use the same names as the CSV so the fields are easy to match.
        self.entries = []
        for column, heading in enumerate(["Combo", "Price (CAD)", "Discount (%)"]):
            tk.Label(form, text=heading).grid(row=0, column=column, sticky="w")
            entry = tk.Entry(form, width=24 if column == 0 else 16)
            entry.grid(row=1, column=column, padx=(0, 10), pady=5)
            self.entries.append(entry)
        self.entries[2].insert(0, "0")
        buttons = tk.Frame(self)
        buttons.pack(fill="x", padx=10, pady=10)
        for text, command in [
            ("Add", self.add_combo), ("Update", self.update_combo),
            ("Delete", self.delete_combo), ("Clear Form", self.clear_form),
            ("Import CSV", self.import_csv), ("Refresh", self.load_combos)
        ]:
            tk.Button(buttons, text=text, command=command).pack(
                side="left", padx=(0, 8))
        self.status = tk.Label(self, text="", anchor="w")
        self.status.pack(fill="x", padx=10, pady=(0, 10))
        self.load_combos()

    def load_combos(self):
        self.clear_form()
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item_id, combo, price, discount in self.data.get_menu(self.restaurant_id):
            self.tree.insert("", "end", iid=str(item_id),
                             values=(combo, f"{price:.2f}", f"{discount:g}"))

    def select_combo(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        self.selected_id = selection[0]
        # Keep the selected ID so Update changes the correct record.
        values = self.tree.item(self.selected_id, "values")
        for index in range(len(self.entries)):
            entry = self.entries[index]
            entry.delete(0, tk.END)
            entry.insert(0, values[index])

    def read_form(self):
        try:
            return check_combo(self.entries[0].get(), self.entries[1].get(),
                               self.entries[2].get())
        except ValueError as error:
            messagebox.showerror("Check Input", str(error), parent=self)
            return None

    def clear_form(self):
        self.selected_id = None
        for entry in self.entries:
            entry.delete(0, tk.END)
        self.entries[2].insert(0, "0")
        for selection in self.tree.selection():
            self.tree.selection_remove(selection)

    def add_combo(self):
        values = self.read_form()
        if values is None:
            return
        try:
            self.data.add_menu_items(self.restaurant_id, [values])
        except ValueError as error:
            messagebox.showerror("Add Combo", str(error), parent=self)
            return
        self.load_combos()
        self.status.config(text="Combo added.")

    def update_combo(self):
        if self.selected_id is None:
            messagebox.showinfo("Update", "Select a combo first.", parent=self)
            return
        values = self.read_form()
        if values is None:
            return
        try:
            changed = self.data.update_menu(
                self.restaurant_id, int(self.selected_id), *values)
        except ValueError as error:
            messagebox.showerror("Update Combo", str(error), parent=self)
            return
        self.load_combos()
        self.status.config(text="Combo updated." if changed
                           else "This combo no longer exists.")

    def delete_combo(self):
        if self.selected_id is None:
            messagebox.showinfo("Delete", "Select a combo first.", parent=self)
            return
        if messagebox.askyesno("Delete Combo", "Delete the selected combo?",
                              parent=self):
            changed = self.data.delete_menu(self.restaurant_id, int(self.selected_id))
            self.load_combos()
            self.status.config(text="Combo deleted." if changed
                               else "This combo no longer exists.")

    def import_csv(self):
        filename = filedialog.askopenfilename(parent=self, title="Choose Menu CSV",
                                               filetypes=[("CSV files", "*.csv")])
        if not filename:
            return
        try:
            combos, skipped, duplicates = read_menu_csv(filename, self.restaurant_name)
            existing = set()
            for row in self.data.get_menu(self.restaurant_id):
                existing.add(row[1].lower())
            new_combos = []
            for combo in combos:
                if combo[0].lower() in existing:
                    duplicates += 1
                else:
                    new_combos.append(combo)
            if not new_combos:
                self.status.config(text="No new combos for this restaurant.")
                return
            if not messagebox.askyesno(
                "Import CSV",
                f"Add {len(new_combos)} combos to {self.restaurant_name}?",
                parent=self
            ):
                return
            self.data.add_menu_items(self.restaurant_id, new_combos)
        except (OSError, UnicodeError, ValueError) as error:
            messagebox.showerror("Import CSV", str(error), parent=self)
            return
        self.load_combos()
        self.status.config(text=f"Added {len(new_combos)} combos. "
                                f"Other rows: {skipped}; duplicates: {duplicates}.")


class InboxWindow(tk.Toplevel):
    def __init__(self, parent, model, restaurant_id, restaurant_name):
        super().__init__(parent)
        self.model = model
        self.restaurant_id = restaurant_id
        self.reviews = {}
        self.title("Review Inbox - " + restaurant_name)
        self.geometry("700x500")

        self.tree = make_table(self, ("student", "rating"),
                               ("Student ID", "Average Rating"))
        self.tree.bind("<<TreeviewSelect>>", self.show_review)
        self.details = tk.Text(self, height=12, wrap="word", state="disabled")
        self.details.pack(fill="both", expand=True, padx=10, pady=5)
        tk.Button(self, text="Refresh", command=self.load_reviews).pack(pady=5)
        self.status = tk.Label(self, text="", anchor="w")
        self.status.pack(fill="x", padx=10, pady=(0, 10))
        self.load_reviews()

    def load_reviews(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.reviews.clear()
        self.details.config(state="normal")
        self.details.delete("1.0", tk.END)
        self.details.config(state="disabled")

        try:
            # Use the existing model to read only this restaurant's reviews.
            rows = self.model.get_reviews_by_restr(self.restaurant_id)
        except sqlite3.Error as error:
            self.status.config(text="Could not load reviews.")
            messagebox.showerror("Review Inbox", str(error), parent=self)
            return

        for row in rows:
            # The five ratings follow the restaurant ID in student_reviews.
            average = sum(row[3:8]) / 5
            review_id = str(row[0])
            self.tree.insert("", "end", iid=review_id,
                             values=(row[1], f"{average:.1f} / 5"))
            self.reviews[review_id] = row
        self.status.config(text=f"{len(rows)} reviews for this restaurant.")

    def show_review(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        row = self.reviews[selection[0]]
        text = (
            f"Student ID: {row[1]}\n"
            f"Taste: {row[3]} / 5\n"
            f"Serving Speed: {row[4]} / 5\n"
            f"Value for Money: {row[5]} / 5\n"
            f"Freshness: {row[6]} / 5\n"
            f"Environment: {row[7]} / 5\n\n"
            "Comment:\n" + (row[8] or "No comment provided.")
        )
        # Merchants can read reviews, but cannot change a student's review.
        self.details.config(state="normal")
        self.details.delete("1.0", tk.END)
        self.details.insert("1.0", text)
        self.details.config(state="disabled")


class MerchantWindow(tk.Toplevel):
    def __init__(self, parent, data, restaurant_id, restaurant_name, model):
        super().__init__(parent)
        self.data = data
        self.model = model
        self.restaurant_id = restaurant_id
        self.restaurant_name = restaurant_name
        self.title("Merchant - " + restaurant_name)
        self.geometry("400x230")
        tk.Label(self, text=restaurant_name, font=("Arial", 16)).pack(pady=20)
        tk.Button(self, text="Manage Combos and Discounts", width=28,
                  command=self.open_combos).pack(pady=8)
        tk.Button(self, text="Review Inbox", width=28,
                  command=self.open_inbox).pack(pady=8)

    def open_combos(self):
        ComboWindow(self, self.data, self.restaurant_id, self.restaurant_name)

    def open_inbox(self):
        InboxWindow(self, self.model, self.restaurant_id, self.restaurant_name)


if __name__ == "__main__":
    from models import SQLModel
    root = tk.Tk()
    root.withdraw()
    model = SQLModel()
    try:
        menu_data = SessionData()
        window = MerchantWindow(root, menu_data, 1, "Subway", model)
        window.protocol("WM_DELETE_WINDOW", root.destroy)
        root.mainloop()
    finally:
        model.close_database()
