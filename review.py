#This part was edited by Jerred Yuan
import tkinter as tk
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
       
        tk.Label(self, text="Rating").grid(row=2, column=0)#Create a label for the rating
        self.rating = tk.IntVar()#create an IntVar to store the value of the selected rating
        rating_frame = tk.Frame(self)#Nesting rating options
        rating_frame.grid(row=2, column=1, columnspan=4, sticky="w")
        tk.Radiobutton(rating_frame, text="1", value=1, variable=self.rating).grid(row=0, column=0)#first rating option
        tk.Radiobutton(rating_frame, text="2", value=2, variable=self.rating).grid(row=0, column=1)#second rating option
        tk.Radiobutton(rating_frame, text="3", value=3, variable=self.rating).grid(row=0, column=2)#third rating option
        tk.Radiobutton(rating_frame, text="4", value=4, variable=self.rating).grid(row=0, column=3)#fourth rating option
        tk.Radiobutton(rating_frame, text="5", value=5, variable=self.rating).grid(row=0, column=4)#fifth rating option

        tk.Label(self, text="Serving Speed")
        self.serving_speed = tk.IntVar()#create an IntVar to store the value of the selected serving speed
        serving_speed_frame = tk.Frame(self)#Nesting serving speed options  
        serving_speed_frame.grid(row=3, column=1, columnspan=4, sticky="w")
        tk.Radiobutton(serving_speed_frame, text="1", value=1, variable=self.serving_speed).grid(row=0, column=0)#first serving speed option
        tk.Radiobutton(serving_speed_frame, text="2", value=2, variable=self.serving_speed).grid(row=0, column=1)#second serving speed option
        tk.Radiobutton(serving_speed_frame, text="3", value=3, variable=self.serving_speed).grid(row=0, column=2)#third serving speed option
        tk.Radiobutton(serving_speed_frame, text="4", value=4, variable=self.serving_speed).grid(row=0, column=3)#fourth serving speed option
        tk.Radiobutton(serving_speed_frame, text="5", value=5, variable=self.serving_speed).grid(row=0, column=4)#fifth serving speed option
Application().mainloop()