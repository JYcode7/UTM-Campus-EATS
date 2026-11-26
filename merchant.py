import csv
import math
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
    restaurant_name = restaurant_name.strip().lower()
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
            csv_name = current_restaurant.lower()
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
    tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse", height=6)
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
        # All windows share these lists. Closing the app clears them.
        # 接入 SQLite 后，替换这个类的读写方法，窗口继续调用同样的方法。
        # Match the IDs and names in setup_database.py.
        self.restaurants = [(1, "Subway"), (2, "Tim Hortons"), (3, "Harvey's")]
        self.combos = []
        self.promotions = []
        self.suggestions = []
        self.next_combo_id = 1
        self.next_promotion_id = 1
        self.next_message_id = 1

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
            self.combos.append((self.next_combo_id, restaurant_id, name, price, discount))
            self.next_combo_id += 1

    def update_menu(self, restaurant_id, item_id, name, price, discount):
        name, price, discount = check_combo(name, str(price), str(discount))
        for row in self.combos:
            if row[1] == restaurant_id and row[0] != item_id and row[2].lower() == name.lower():
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

    def get_promotions(self, restaurant_id):
        result = []
        for row in self.promotions:
            if row[1] == restaurant_id:
                result.append((row[0], row[2], row[3]))
        return result

    def add_promotion(self, restaurant_id, title, content):
        self.promotions.append((self.next_promotion_id, restaurant_id, title, content))
        self.next_promotion_id += 1

    def update_promotion(self, restaurant_id, promotion_id, title, content):
        for index, row in enumerate(self.promotions):
            if row[0] == promotion_id and row[1] == restaurant_id:
                self.promotions[index] = (promotion_id, restaurant_id, title, content)
                return True
        return False

    def delete_promotion(self, restaurant_id, promotion_id):
        for index, row in enumerate(self.promotions):
            if row[0] == promotion_id and row[1] == restaurant_id:
                self.promotions.pop(index)
                return True
        return False

    def add_suggestion(self, restaurant_id, student_id, student_name, content):
        self.suggestions.append((self.next_message_id, restaurant_id, student_id, student_name, content))
        self.next_message_id += 1

    def get_suggestions(self, restaurant_id):
        result = []
        for row in self.suggestions:
            if row[1] == restaurant_id:
                result.append((row[0], row[3], row[4]))
        return result


class ComboWindow(tk.Toplevel):
    def __init__(self, parent, data, restaurant_id, restaurant_name):
        super().__init__(parent)
        self.data = data
        self.restaurant_id = restaurant_id
        self.restaurant_name = restaurant_name
        self.selected_id = None
        self.title("Combos - " + restaurant_name)
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
        for text, command in [("Add", self.add_combo), ("Update", self.update_combo),
                              ("Delete", self.delete_combo), ("Clear Form", self.clear_form),
                              ("Import CSV", self.import_csv), ("Refresh", self.load_combos)]:
            tk.Button(buttons, text=text, command=command).pack(side="left", padx=(0, 8))
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
            return check_combo(self.entries[0].get(), self.entries[1].get(), self.entries[2].get())
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
            changed = self.data.update_menu(self.restaurant_id, int(self.selected_id), *values)
        except ValueError as error:
            messagebox.showerror("Update Combo", str(error), parent=self)
            return
        self.load_combos()
        self.status.config(text="Combo updated." if changed else "This combo no longer exists.")

    def delete_combo(self):
        if self.selected_id is None:
            messagebox.showinfo("Delete", "Select a combo first.", parent=self)
            return
        if messagebox.askyesno("Delete Combo", "Delete the selected combo?", parent=self):
            changed = self.data.delete_menu(self.restaurant_id, int(self.selected_id))
            self.load_combos()
            self.status.config(text="Combo deleted." if changed else "This combo no longer exists.")

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
            if not messagebox.askyesno("Import CSV",
                    f"Add {len(new_combos)} combos to {self.restaurant_name}?", parent=self):
                return
            self.data.add_menu_items(self.restaurant_id, new_combos)
        except (OSError, UnicodeError, ValueError) as error:
            messagebox.showerror("Import CSV", str(error), parent=self)
            return
        self.load_combos()
        self.status.config(text=f"Added {len(new_combos)} combos. "
                                f"Other rows: {skipped}; duplicates: {duplicates}.")


class PromotionWindow(tk.Toplevel):
    def __init__(self, parent, data, restaurant_id, restaurant_name):
        super().__init__(parent)
        self.data = data
        self.restaurant_id = restaurant_id
        self.selected_id = None
        self.promotion_details = {}
        self.title("Promotions - " + restaurant_name)
        self.geometry("650x460")
        self.tree = make_table(self, ("title",), ("Promotion Title",))
        self.tree.bind("<<TreeviewSelect>>", self.select_promotion)
        tk.Label(self, text="Title").pack(anchor="w", padx=10)
        self.title_entry = tk.Entry(self)
        self.title_entry.pack(fill="x", padx=10)
        tk.Label(self, text="Description").pack(anchor="w", padx=10, pady=(10, 0))
        self.content = tk.Text(self, height=6, wrap="word")
        self.content.pack(fill="x", padx=10)
        buttons = tk.Frame(self)
        buttons.pack(fill="x", padx=10, pady=10)
        for text, command in [("Publish", self.publish), ("Update", self.update_promotion),
                              ("Delete", self.delete_promotion), ("Clear Form", self.clear_form), ("Refresh", self.load_promotions)]:
            tk.Button(buttons, text=text, command=command).pack(side="left", padx=(0, 8))
        self.load_promotions()

    def load_promotions(self):
        self.clear_form()
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.promotion_details.clear()
        for promotion_id, title, content in self.data.get_promotions(self.restaurant_id):
            self.tree.insert("", "end", iid=str(promotion_id), values=(title,))
            self.promotion_details[str(promotion_id)] = content

    def select_promotion(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        self.selected_id = selection[0]
        title = self.tree.item(self.selected_id, "values")[0]
        content = self.promotion_details.get(self.selected_id, "")
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, title)
        self.content.delete("1.0", tk.END)
        self.content.insert("1.0", content)

    def read_form(self):
        title = self.title_entry.get().strip()
        content = self.content.get("1.0", "end-1c").strip()
        if not title or not content:
            messagebox.showerror("Check Input", "Enter a title and description.", parent=self)
            return None
        return title, content

    def clear_form(self):
        self.selected_id = None
        self.title_entry.delete(0, tk.END)
        self.content.delete("1.0", tk.END)
        for selection in self.tree.selection():
            self.tree.selection_remove(selection)

    def publish(self):
        values = self.read_form()
        if values is None:
            return
        self.data.add_promotion(self.restaurant_id, values[0], values[1])
        self.load_promotions()

    def update_promotion(self):
        if self.selected_id is None:
            messagebox.showinfo("Update", "Select a promotion first.", parent=self)
            return
        values = self.read_form()
        if values is None:
            return
        changed = self.data.update_promotion(self.restaurant_id, int(self.selected_id), *values)
        self.load_promotions()
        if not changed:
            messagebox.showinfo("Update", "This promotion no longer exists.", parent=self)

    def delete_promotion(self):
        if self.selected_id is None:
            messagebox.showinfo("Delete", "Select a promotion first.", parent=self)
            return
        if messagebox.askyesno("Delete Promotion", "Delete the selected promotion?", parent=self):
            self.data.delete_promotion(self.restaurant_id, int(self.selected_id))
            self.load_promotions()


class InboxWindow(tk.Toplevel):
    def __init__(self, parent, data, restaurant_id, restaurant_name):
        super().__init__(parent)
        self.data = data
        self.restaurant_id = restaurant_id
        self.suggestion_details = {}
        self.title("Suggestion Inbox - " + restaurant_name)
        self.geometry("650x400")
        tk.Label(self, text="Select a suggestion to read it.").pack(anchor="w", padx=10, pady=10)
        self.tree = make_table(self, ("student",), ("From",))
        self.tree.bind("<<TreeviewSelect>>", self.read_suggestion)
        # A restaurant should not be able to edit the student's message.
        self.message = tk.Text(self, height=7, wrap="word", state="disabled")
        self.message.pack(fill="x", padx=10, pady=10)
        tk.Button(self, text="Refresh", command=self.load_suggestions).pack(pady=(0, 10))
        self.load_suggestions()

    def load_suggestions(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.suggestion_details.clear()
        self.message.config(state="normal")
        self.message.delete("1.0", tk.END)
        self.message.config(state="disabled")
        # Only show messages addressed to this restaurant.
        for message_id, student_name, content in self.data.get_suggestions(self.restaurant_id):
            self.tree.insert("", "end", iid=str(message_id), values=(student_name,))
            self.suggestion_details[str(message_id)] = content

    def read_suggestion(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        content = self.suggestion_details.get(selection[0], "")
        self.message.config(state="normal")
        self.message.delete("1.0", tk.END)
        self.message.insert("1.0", content)
        self.message.config(state="disabled")


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
        restaurant_names = []
        for restaurant in restaurants:
            restaurant_names.append(restaurant[1])
        self.restaurant_choice = ttk.Combobox(top, values=restaurant_names,
                                               state="readonly", width=25)
        self.restaurant_choice.pack(side="left", padx=10)
        if restaurants:
            self.restaurant_choice.current(0)
        self.restaurant_choice.bind("<<ComboboxSelected>>", self.load_promotions)
        tk.Button(top, text="Refresh", command=self.load_promotions).pack(side="left")
        self.tree = make_table(self, ("title",), ("Promotion Title",))
        self.tree.bind("<<TreeviewSelect>>", self.show_promotion)
        tk.Label(self, text="Description").pack(anchor="w", padx=10)
        self.description = tk.Text(self, height=7, wrap="word", state="disabled")
        self.description.pack(fill="x", padx=10, pady=10)
        self.load_promotions()

    def load_promotions(self, event=None):
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
        # Read the same promotions that the merchant creates.
        for promotion_id, title, content in self.data.get_promotions(restaurant_id):
            self.tree.insert("", "end", iid=str(promotion_id), values=(title,))
            self.promotion_details[str(promotion_id)] = content

    def show_promotion(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        content = self.promotion_details.get(selection[0], "")
        # Students can read promotions, but cannot edit them.
        self.description.config(state="normal")
        self.description.delete("1.0", tk.END)
        self.description.insert("1.0", content)
        self.description.config(state="disabled")


class StudentSuggestionWindow(tk.Toplevel):
    def __init__(self, parent, data, student_id, student_name, restaurants):
        super().__init__(parent)
        self.data = data
        self.student_id = student_id
        self.student_name = student_name
        self.restaurants = restaurants
        self.title("Send a Suggestion")
        self.geometry("600x420")
        form = tk.Frame(self)
        form.pack(fill="x", padx=10, pady=10)
        tk.Label(form, text="From").grid(row=0, column=0, sticky="w", pady=5)
        tk.Label(form, text=student_name).grid(row=0, column=1, sticky="w", padx=10)
        tk.Label(form, text="To Restaurant").grid(row=1, column=0, sticky="w", pady=5)
        # Use the ID for sending, since restaurant names can change.
        restaurant_names = []
        for restaurant in restaurants:
            restaurant_names.append(restaurant[1])
        self.restaurant_choice = ttk.Combobox(form, values=restaurant_names,
                                               state="readonly", width=28)
        self.restaurant_choice.grid(row=1, column=1, sticky="w", padx=10)
        tk.Label(self, text="Your Suggestion").pack(anchor="w", padx=10)
        self.message = tk.Text(self, height=12, wrap="word")
        self.message.pack(fill="both", expand=True, padx=10, pady=10)
        buttons = tk.Frame(self)
        buttons.pack(fill="x", padx=10, pady=(0, 10))
        tk.Button(buttons, text="Send", command=self.send_suggestion).pack(side="left")
        tk.Button(buttons, text="Clear Message", command=self.clear_message).pack(side="left", padx=10)

    def read_form(self):
        index = self.restaurant_choice.current()
        if index < 0:
            messagebox.showerror("Check Input", "Select a restaurant.", parent=self)
            return None
        content = self.message.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showerror("Check Input", "Enter your suggestion.", parent=self)
            return None
        return self.restaurants[index][0], content

    def send_suggestion(self):
        values = self.read_form()
        if values is None:
            return
        restaurant_id, content = values
        self.data.add_suggestion(restaurant_id, self.student_id, self.student_name, content)
        self.clear_message()
        messagebox.showinfo("Suggestion", "Suggestion sent.", parent=self)

    def clear_message(self):
        self.message.delete("1.0", tk.END)


class MerchantWindow(tk.Toplevel):
    def __init__(self, parent, data, restaurant_id, restaurant_name):
        super().__init__(parent)
        self.data = data
        self.restaurant_id = restaurant_id
        self.restaurant_name = restaurant_name
        self.title("Merchant - " + restaurant_name)
        self.geometry("400x280")
        tk.Label(self, text=restaurant_name, font=("Arial", 16)).pack(pady=20)
        tk.Button(self, text="Manage Combos", width=25, command=self.open_combos).pack(pady=8)
        tk.Button(self, text="Manage Promotions", width=25, command=self.open_promotions).pack(pady=8)
        tk.Button(self, text="Suggestion Inbox", width=25, command=self.open_inbox).pack(pady=8)

    def open_combos(self):
        ComboWindow(self, self.data, self.restaurant_id, self.restaurant_name)

    def open_promotions(self):
        PromotionWindow(self, self.data, self.restaurant_id, self.restaurant_name)

    def open_inbox(self):
        InboxWindow(self, self.data, self.restaurant_id, self.restaurant_name)


class MerchantPreview(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Campus Eats")
        self.geometry("450x300")
        # All windows share this object so they see the same session data.
        self.data = SessionData()
        tk.Label(self, text="Choose a restaurant to manage:").pack(pady=(20, 0))
        restaurant_names = []
        for restaurant in self.data.restaurants:
            restaurant_names.append(restaurant[1])
        self.choice = ttk.Combobox(self, values=restaurant_names, state="readonly")
        self.choice.pack(pady=8)
        self.choice.current(0)
        tk.Button(self, text="Open Merchant Window", command=self.open_merchant).pack(pady=8)
        tk.Button(self, text="Browse Promotions as Student", command=self.open_promotions).pack(pady=8)
        tk.Button(self, text="Send Suggestion as Student", command=self.open_suggestion).pack(pady=8)

    def open_merchant(self):
        restaurant_id, restaurant_name = self.data.restaurants[self.choice.current()]
        MerchantWindow(self, self.data, restaurant_id, restaurant_name)

    def open_promotions(self):
        StudentPromotionsWindow(self, self.data, self.data.restaurants)

    def open_suggestion(self):
        # 整合的时候，从主程序传入学生编号和姓名
        StudentSuggestionWindow(self, self.data, None, "Student",
                                self.data.restaurants)


if __name__ == "__main__":
    MerchantPreview().mainloop()
