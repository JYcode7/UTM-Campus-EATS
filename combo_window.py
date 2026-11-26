import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from menu_csv import check_combo, read_menu_csv


class ComboWindow(tk.Toplevel):
    def __init__(self, parent, data, restaurant_id, restaurant_name):
        super().__init__(parent)

        self.data = data
        self.restaurant_id = restaurant_id
        self.restaurant_name = restaurant_name
        self.selected_id = None

        self.title("Combos - " + restaurant_name)
        self.geometry("740x450")

        table_frame = tk.Frame(self)
        table_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=("combo", "price", "discount"),
            show="headings",
            selectmode="browse",
            height=6
        )

        self.tree.heading("combo", text="Combo")
        self.tree.heading("price", text="Price (CAD)")
        self.tree.heading("discount", text="Discount (%)")

        self.tree.column("combo", width=280)
        self.tree.column("price", width=180)
        self.tree.column("discount", width=140)

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
            self.select_combo
        )

        form = tk.Frame(self)
        form.pack(fill="x", padx=10)

        # Match the form fields to the CSV columns.
        self.entries = []
        headings = ["Combo", "Price (CAD)", "Discount (%)"]

        for column, heading in enumerate(headings):
            tk.Label(form, text=heading).grid(
                row=0,
                column=column,
                sticky="w"
            )

            if column == 0:
                width = 24
            else:
                width = 16

            entry = tk.Entry(form, width=width)
            entry.grid(
                row=1,
                column=column,
                padx=(0, 10),
                pady=5
            )
            self.entries.append(entry)

        self.entries[2].insert(0, "0")

        buttons = tk.Frame(self)
        buttons.pack(fill="x", padx=10, pady=10)

        button_choices = [
            ("Add", self.add_combo),
            ("Update", self.update_combo),
            ("Delete", self.delete_combo),
            ("Clear Form", self.clear_form),
            ("Import CSV", self.import_csv),
            ("Refresh", self.load_combos)
        ]

        for text, command in button_choices:
            tk.Button(
                buttons,
                text=text,
                command=command
            ).pack(side="left", padx=(0, 8))

        self.status = tk.Label(self, text="", anchor="w")
        self.status.pack(fill="x", padx=10, pady=(0, 10))

        self.load_combos()

    def load_combos(self):
        # Reload the list after a change.
        self.clear_form()

        for row in self.tree.get_children():
            self.tree.delete(row)

        for item_id, combo, price, discount in self.data.get_menu(
            self.restaurant_id
        ):
            self.tree.insert(
                "",
                "end",
                iid=str(item_id),
                values=(
                    combo,
                    f"{price:.2f}",
                    f"{discount:g}"
                )
            )

    def select_combo(self, event):
        selection = self.tree.selection()

        if not selection:
            return

        self.selected_id = selection[0]

        # Put the selected combo back into the form.
        values = self.tree.item(self.selected_id, "values")

        for entry, value in zip(self.entries, values):
            entry.delete(0, tk.END)
            entry.insert(0, value)

    def read_form(self):
        try:
            return check_combo(
                self.entries[0].get(),
                self.entries[1].get(),
                self.entries[2].get()
            )
        except ValueError as error:
            messagebox.showerror(
                "Check Input",
                str(error),
                parent=self
            )
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
            self.data.add_menu_items(
                self.restaurant_id,
                [values]
            )
        except ValueError as error:
            messagebox.showerror(
                "Add Combo",
                str(error),
                parent=self
            )
            return

        self.load_combos()
        self.status.config(text="Combo added.")

    def update_combo(self):
        if self.selected_id is None:
            messagebox.showinfo(
                "Update",
                "Select a combo first.",
                parent=self
            )
            return

        values = self.read_form()

        if values is None:
            return

        combo, price, discount = values

        try:
            changed = self.data.update_menu(
                self.restaurant_id,
                int(self.selected_id),
                combo,
                price,
                discount
            )
        except ValueError as error:
            messagebox.showerror(
                "Update Combo",
                str(error),
                parent=self
            )
            return

        self.load_combos()

        if changed:
            self.status.config(text="Combo updated.")
        else:
            self.status.config(text="This combo no longer exists.")

    def delete_combo(self):
        if self.selected_id is None:
            messagebox.showinfo(
                "Delete",
                "Select a combo first.",
                parent=self
            )
            return

        answer = messagebox.askyesno(
            "Delete Combo",
            "Delete the selected combo?",
            parent=self
        )

        if answer:
            changed = self.data.delete_menu(
                self.restaurant_id,
                int(self.selected_id)
            )

            self.load_combos()

            if changed:
                self.status.config(text="Combo deleted.")
            else:
                self.status.config(
                    text="This combo no longer exists."
                )

    def import_csv(self):
        filename = filedialog.askopenfilename(
            parent=self,
            title="Choose Menu CSV",
            filetypes=[("CSV files", "*.csv")]
        )

        if not filename:
            return

        try:
            combos, skipped, duplicates = read_menu_csv(
                filename,
                self.restaurant_name
            )

            # Skip combos already added during this session.
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
                self.status.config(
                    text="No new combos for this restaurant."
                )
                return

            answer = messagebox.askyesno(
                "Import CSV",
                f"Add {len(new_combos)} combos to {self.restaurant_name}?",
                parent=self
            )

            if not answer:
                return

            self.data.add_menu_items(
                self.restaurant_id,
                new_combos
            )

        except (OSError, UnicodeError, ValueError) as error:
            messagebox.showerror(
                "Import CSV",
                str(error),
                parent=self
            )
            return

        self.load_combos()

        self.status.config(
            text=(
                f"Added {len(new_combos)} combos. "
                f"Other rows: {skipped}; duplicates: {duplicates}."
            )
        )
