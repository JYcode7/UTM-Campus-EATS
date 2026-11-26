import tkinter as tk
from tkinter import ttk


class InboxWindow(tk.Toplevel):
    def __init__(self, parent, data, restaurant_id, restaurant_name):
        super().__init__(parent)

        self.data = data
        self.restaurant_id = restaurant_id
        self.suggestion_details = {}

        self.title("Suggestion Inbox - " + restaurant_name)
        self.geometry("650x400")

        tk.Label(
            self,
            text="Select a suggestion to read it."
        ).pack(anchor="w", padx=10, pady=10)

        table_frame = tk.Frame(self)
        table_frame.pack(
            fill="both",
            expand=True,
            padx=10
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=("student",),
            show="headings",
            selectmode="browse",
            height=6
        )
        self.tree.heading("student", text="From")
        self.tree.column("student", width=500)
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
            self.read_suggestion
        )

        # The restaurant can read messages but cannot edit them.
        self.message = tk.Text(
            self,
            height=7,
            wrap="word",
            state="disabled"
        )
        self.message.pack(fill="x", padx=10, pady=10)

        tk.Button(
            self,
            text="Refresh",
            command=self.load_suggestions
        ).pack(pady=(0, 10))

        self.load_suggestions()

    def load_suggestions(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.suggestion_details.clear()

        self.message.config(state="normal")
        self.message.delete("1.0", tk.END)
        self.message.config(state="disabled")

        # Only load suggestions sent to this restaurant.
        for message_id, student_name, content in self.data.get_suggestions(
            self.restaurant_id
        ):
            self.tree.insert(
                "",
                "end",
                iid=str(message_id),
                values=(student_name,)
            )
            self.suggestion_details[str(message_id)] = content

    def read_suggestion(self, event):
        selection = self.tree.selection()

        if not selection:
            return

        content = self.suggestion_details.get(
            selection[0], ""
        )

        self.message.config(state="normal")
        self.message.delete("1.0", tk.END)
        self.message.insert("1.0", content)
        self.message.config(state="disabled")
