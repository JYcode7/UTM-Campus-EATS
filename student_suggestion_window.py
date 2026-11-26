import tkinter as tk
from tkinter import ttk, messagebox


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

        tk.Label(form, text="From").grid(
            row=0,
            column=0,
            sticky="w",
            pady=5
        )

        tk.Label(form, text=student_name).grid(
            row=0,
            column=1,
            sticky="w",
            padx=10
        )

        tk.Label(form, text="To Restaurant").grid(
            row=1,
            column=0,
            sticky="w",
            pady=5
        )

        # Show names in the list, then use the selected restaurant's ID.
        self.restaurant_choice = ttk.Combobox(
            form,
            values=[row[1] for row in restaurants],
            state="readonly",
            width=28
        )
        self.restaurant_choice.grid(
            row=1,
            column=1,
            sticky="w",
            padx=10
        )

        tk.Label(self, text="Your Suggestion").pack(
            anchor="w",
            padx=10
        )

        self.message = tk.Text(
            self,
            height=12,
            wrap="word"
        )
        self.message.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        buttons = tk.Frame(self)
        buttons.pack(fill="x", padx=10, pady=(0, 10))

        tk.Button(
            buttons,
            text="Send",
            command=self.send_suggestion
        ).pack(side="left")

        tk.Button(
            buttons,
            text="Clear Message",
            command=self.clear_message
        ).pack(side="left", padx=10)

    def read_form(self):
        index = self.restaurant_choice.current()

        if index < 0:
            messagebox.showerror(
                "Check Input",
                "Select a restaurant.",
                parent=self
            )
            return None

        content = self.message.get("1.0", "end-1c").strip()

        # Do not send an empty message.
        if not content:
            messagebox.showerror(
                "Check Input",
                "Enter your suggestion.",
                parent=self
            )
            return None

        return self.restaurants[index][0], content

    def send_suggestion(self):
        values = self.read_form()

        if values is None:
            return

        restaurant_id, content = values

        self.data.add_suggestion(
            restaurant_id,
            self.student_id,
            self.student_name,
            content
        )

        # Clear the message only after it has been added.
        self.clear_message()

        messagebox.showinfo(
            "Suggestion",
            "Suggestion sent.",
            parent=self
        )

    def clear_message(self):
        # Keep the restaurant selected when clearing the text.
        self.message.delete("1.0", tk.END)
