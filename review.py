#This part was edited by Jerred Yuan
import tkinter as tk
from tkinter import messagebox
class Application(tk.Tk): 
    def __init__(self): 
        super().__init__() 
        self.title("UTM Campus EATS") 
        self._build_widgets() 
    def _build_widgets(self): 
        tk.Label(self, text="Students Review").grid(row=0, column=0)#use grid to place the label in the first row

        tk.Label(self, text="Restaurant").grid(row=1, column=0)
        self.restaurant = tk.IntVar()#create an IntVar to store the value of the selected restaurant
        Restaurant_frame = tk.Frame(self)#Nesting restaurant options
        Restaurant_frame.grid(row=1, column=1, columnspan=4, sticky="w")
        tk.Radiobutton(self, text="Subway", value=1, variable=self.restaurant).grid(row=1, column=1)#first restaurant option
        tk.Radiobutton(self, text="Tim Hortons", value=2, variable=self.restaurant).grid(row=1, column=2)#second restaurant option
        tk.Radiobutton(self, text="Harveys", value=3, variable=self.restaurant).grid(row=1, column=3)#third restaurant option
       
        tk.Label(self, text="TasteRating").grid(row=2, column=0)#Create a label for the rating
        self.rating = tk.IntVar()#create an IntVar to store the value of the selected rating
        rating_frame = tk.Frame(self)#Nesting rating options
        rating_frame.grid(row=2, column=1, columnspan=4, sticky="w")
        tk.Radiobutton(rating_frame, text="1", value=1, variable=self.rating).grid(row=0, column=0)
        tk.Radiobutton(rating_frame, text="2", value=2, variable=self.rating).grid(row=0, column=1)
        tk.Radiobutton(rating_frame, text="3", value=3, variable=self.rating).grid(row=0, column=2)
        tk.Radiobutton(rating_frame, text="4", value=4, variable=self.rating).grid(row=0, column=3)
        tk.Radiobutton(rating_frame, text="5", value=5, variable=self.rating).grid(row=0, column=4)

        tk.Label(self, text="Serving Speed").grid(row=3, column=0)#Create a label for the serving speed
        self.serving_speed = tk.IntVar()#create an IntVar to store the value of the selected serving speed
        serving_speed_frame = tk.Frame(self)#Nesting serving speed options  
        serving_speed_frame.grid(row=3, column=1, columnspan=4, sticky="w")
        tk.Radiobutton(serving_speed_frame, text="1", value=1, variable=self.serving_speed).grid(row=0, column=0)
        tk.Radiobutton(serving_speed_frame, text="2", value=2, variable=self.serving_speed).grid(row=0, column=1)
        tk.Radiobutton(serving_speed_frame, text="3", value=3, variable=self.serving_speed).grid(row=0, column=2)
        tk.Radiobutton(serving_speed_frame, text="4", value=4, variable=self.serving_speed).grid(row=0, column=3)
        tk.Radiobutton(serving_speed_frame, text="5", value=5, variable=self.serving_speed).grid(row=0, column=4)

        tk.Label(self, text="Value for Money").grid (row=4, column=0)#Create a label for the value for money
        self.value_for_money = tk.IntVar()#create an IntVar to store the value of the selected value for money
        value_for_money_frame = tk.Frame(self)#Nesting value for money options
        value_for_money_frame.grid(row=4, column=1, columnspan=4, sticky="w")
        tk.Radiobutton(value_for_money_frame, text="1", value=1, variable=self.value_for_money).grid(row=0, column=0)
        tk.Radiobutton(value_for_money_frame, text="2", value=2, variable=self.value_for_money).grid(row=0, column=1)
        tk.Radiobutton(value_for_money_frame, text="3", value=3, variable=self.value_for_money).grid(row=0, column=2)
        tk.Radiobutton(value_for_money_frame, text="4", value=4, variable=self.value_for_money).grid(row=0, column=3)
        tk.Radiobutton(value_for_money_frame, text="5", value=5, variable=self.value_for_money).grid(row=0, column=4)

        tk.Label(self, text="Freshness").grid(row=5, column=0)#Create a label for the freshness
        self.freshness = tk.IntVar()#create an IntVar to store the value of the selected freshness
        freshness_frame = tk.Frame(self)#Nesting freshness options
        freshness_frame.grid(row=5, column=1, columnspan=4, sticky="w")
        tk.Radiobutton(freshness_frame, text="1", value=1, variable=self.freshness).grid(row=0, column=0)
        tk.Radiobutton(freshness_frame, text="2", value=2, variable=self.freshness).grid(row=0, column=1)
        tk.Radiobutton(freshness_frame, text="3", value=3, variable=self.freshness).grid(row=0, column=2)
        tk.Radiobutton(freshness_frame, text="4", value=4, variable=self.freshness).grid(row=0, column=3)
        tk.Radiobutton(freshness_frame, text="5", value=5, variable=self.freshness).grid(row=0, column=4)

        tk.Label(self, text="Environment").grid(row=6, column=0)#Create a label for the environment
        self.environment = tk.IntVar()#create an IntVar to store the value of the selected environment
        environment_frame = tk.Frame(self)#Nesting environment options
        environment_frame.grid(row=6, column=1, columnspan=4, sticky="w")
        tk.Radiobutton(environment_frame, text="1", value=1, variable=self.environment).grid(row=0, column=0)
        tk.Radiobutton(environment_frame, text="2", value=2, variable=self.environment).grid(row=0, column=1)
        tk.Radiobutton(environment_frame, text="3", value=3, variable=self.environment).grid(row=0, column=2)
        tk.Radiobutton(environment_frame, text="4", value=4, variable=self.environment).grid(row=0, column=3)
        tk.Radiobutton(environment_frame, text="5", value=5, variable=self.environment).grid(row=0, column=4)

        tk.Label(self, text="Comments（Optional）").grid(row=7, column=0, sticky="nw")#Create a label for the comments
        self.comments = tk.Text(self)
        self.comments.config(height=3, width=20)
        self.comments.grid(row=7, column=1, columnspan=4, sticky="w")

        tk.Button(self, text="Save", command=self.check_review).grid(row=8, column=1)#Create a save button
    
    def check_review(self):
        restaurant = self.restaurant.get()
        if not restaurant:
            messagebox.showerror("Error", "Please select a restaurant.")
        elif not self.rating.get():
            messagebox.showerror("Missing information", "Please select a taste rating")
        elif not self.freshness.get():
            messagebox.showerror("Missing information", "Please select a freshness rating")
        elif not self.environment.get():
            messagebox.showerror("Missing information", "Please select an environment rating")
        else:
            messagebox.showinfo("Success", "Review submitted successfully.")
  

Application().mainloop()