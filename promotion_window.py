import tkinter as tk
from tkinter import ttk, messagebox


class PromotionWindow(tk.Toplevel):
    def __init__(self, parent, data, restaurant_id, restaurant_name):
        super().__init__(parent)

        self.data = data
        self.restaurant_id = restaurant_id
        self.selected_id = None
        self.promotion_details = {}

        self.title("Promotions - " + restaurant_name)
        self.geometry("650x460")

        table_frame = tk.Frame(self)
        table_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # Show titles in the list and full content in the form.
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
            self.select_promotion
        )

        tk.Label(self, text="Title").pack(
            anchor="w",
            padx=10
        )

        self.title_entry = tk.Entry(self)
        self.title_entry.pack(fill="x", padx=10)

        tk.Label(self, text="Description").pack(
            anchor="w",
            padx=10,
            pady=(10, 0)
        )

        self.content = tk.Text(
            self,
            height=6,
            wrap="word"
        )
        self.content.pack(fill="x", padx=10)

        buttons = tk.Frame(self)
        buttons.pack(fill="x", padx=10, pady=10)

        button_choices = [
            ("Publish", self.publish),
            ("Update", self.update_promotion),
            ("Delete", self.delete_promotion),
            ("Clear Form", self.clear_form),
            ("Refresh", self.load_promotions)
        ]

        for text, command in button_choices:
            tk.Button(
                buttons,
                text=text,
                command=command
            ).pack(side="left", padx=(0, 8))

        self.load_promotions()

    def load_promotions(self):
        self.clear_form()

        for row in self.tree.get_children():
            self.tree.delete(row)

        self.promotion_details.clear()

        for promotion_id, title, content in self.data.get_promotions(
            self.restaurant_id
        ):
            self.tree.insert(
                "",
                "end",
                iid=str(promotion_id),
                values=(title,)
            )
            self.promotion_details[str(promotion_id)] = content

    def select_promotion(self, event):
        selection = self.tree.selection()

        if not selection:
            return

        self.selected_id = selection[0]

        title = self.tree.item(self.selected_id, "values")[0]
        content = self.promotion_details.get(
            self.selected_id, ""
        )

        # Bring the selected promotion into the form.
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, title)

        self.content.delete("1.0", tk.END)
        self.content.insert("1.0", content)

    def read_form(self):
        title = self.title_entry.get().strip()
        content = self.content.get("1.0", "end-1c").strip()

        if not title or not content:
            messagebox.showerror(
                "Check Input",
                "Enter a title and description.",
                parent=self
            )
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

        title, content = values

        self.data.add_promotion(
            self.restaurant_id,
            title,
            content
        )

        self.load_promotions()

    def update_promotion(self):
        if self.selected_id is None:
            messagebox.showinfo(
                "Update",
                "Select a promotion first.",
                parent=self
            )
            return

        values = self.read_form()

        if values is None:
            return

        title, content = values

        changed = self.data.update_promotion(
            self.restaurant_id,
            int(self.selected_id),
            title,
            content
        )

        self.load_promotions()

        if not changed:
            messagebox.showinfo(
                "Update",
                "This promotion no longer exists.",
                parent=self
            )

    def delete_promotion(self):
        if self.selected_id is None:
            messagebox.showinfo(
                "Delete",
                "Select a promotion first.",
                parent=self
            )
            return

        answer = messagebox.askyesno(
            "Delete Promotion",
            "Delete the selected promotion?",
            parent=self
        )

        if answer:
            self.data.delete_promotion(
                self.restaurant_id,
                int(self.selected_id)
            )
            self.load_promotions()
