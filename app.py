from tkinter import *
import sqlite3
from PIL import Image, ImageTk

class ToDoList(Tk):
    
    def __init__(self):
        super().__init__()
        self.minsize(460, 700)  # Set minimum window size
        self.config(bg='#fde100')  # Set background color
        self.resizable(False, False)  # Prevent resizing the window
        
        self.conn = sqlite3.connect('todos.db')  # Connect to SQLite database
        self.cursor = self.conn.cursor()
        
        # Create todos table if it does not exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                todo TEXT NOT NULL,
                is_finished BOOLEAN NOT NULL
            )
        ''')

        self.image_sizes = (40, 40)  # Define image size for icons
        self.photo_images = []  # List to store images
        
        # Frame for adding new todos
        self.add_frame = Frame(self, width=440, height=50, bg='#fde100')
        self.add_frame.pack(anchor='center', padx=10, pady=15)
        
        self.add_label = Label(self.add_frame, text='Add a new ToDo', bg='#fde100', font=('Arial'))
        self.add_label.pack(padx=5, pady=5, anchor='center')
        
        self.entry = Entry(self.add_frame, font=('Arial', 17))
        self.entry.config(width=50)
        self.entry.bind('<Return>', self.add_to_list)  # Bind Enter key to add_to_list method
        
        self.entry.pack(padx=5, pady=5, anchor='center')       
        
        # Frame to display todos
        self.todo_frame = Frame(self, bg='white', width=440, height=50)
        self.todo_frame.config(bg='#fde100')
        self.todo_frame.pack_propagate(False)
        
        self.show_all_todos()  # Display all todos on initialization
        
        # Label and button to clear all todos
        self.clear_everything = Label(self, text='Delete Everything', bg='#fde100', font=('Arial'))
        self.clear_everything.pack(padx=5, pady=5, anchor='center')
        
        image = Image.open('clear.png')  # Load clear button image
        resized_image = image.resize(self.image_sizes, Image.LANCZOS)
        photo = ImageTk.PhotoImage(resized_image)
        
        self.photo_images.append(photo)  # Add image to list
        photo_image_label = Label(self, image=photo, justify='center')
        
        self.clear_button = Button(self, image=photo, borderwidth=0, command=self.clear_all_todos)  # Button to clear all todos
        self.clear_button.config(bg='#fde100')
        self.clear_button.pack(padx=10, pady=10)
        
        self.mainloop()  # Start the main loop
        self.conn.close()  # Close the database connection
        
    def add_to_list(self, event):
        entered_text = self.entry.get()  # Get text from entry widget
        if entered_text:
            self.cursor.execute('INSERT INTO todos (todo, is_finished) VALUES (?, ?)', (entered_text, 0)) # Add todo to database
            self.conn.commit()
        self.entry.delete(0, END)  # Clear the entry widget
        self.show_all_todos()  # Refresh the todo list
        
    def show_all_todos(self):
        # Clear previous todos
        for widget in self.todo_frame.winfo_children():
            widget.destroy()
        
        # Fetch all todos from database
        self.cursor.execute("""SELECT * FROM todos""")
        todos = self.cursor.fetchall()
        
        # Display the todo_frame if not already displayed
        if not self.todo_frame.winfo_ismapped():
            self.todo_frame.pack(anchor='center', padx=50, pady=10, fill='both', expand=True)

        row_number = 0  # Initialize row number
        
        for row in todos:
            todo_text = row[1]  # Get todo text
            is_finished = row[2]  # Get todo completion status
            
            # Load and resize delete button image
            delete_image = Image.open('delete.png')
            resized_delete_image = delete_image.resize(self.image_sizes, Image.LANCZOS)
            photo = ImageTk.PhotoImage(resized_delete_image)
            
            self.photo_images.append(photo)  # Add image to list
            delete_image_label = Label(self.todo_frame, image=photo, justify='left')
            
            delete_button = Button(self.todo_frame, image=photo, borderwidth=0, command=lambda todo=todo_text: self.delete_a_todo(todo))  # Button to delete todo
            delete_button.config(bg='#fde100')
            delete_button.grid(row=row_number, column=0, padx=10, pady=10, sticky='w')
            
            # Load and resize completion status image
            if is_finished:
                image = Image.open('finished.png')
            else:
                image = Image.open('empty.webp')
            
            resized_image = image.resize(self.image_sizes, Image.LANCZOS)
            photo = ImageTk.PhotoImage(resized_image)
            
            # Create button for marking todo as finished/not finished
            button = Button(self.todo_frame, image=photo, borderwidth=0, command=lambda todo=todo_text, finished=row[2]: self.mark_a_todo(todo, finished))
            button.grid(row=row_number, column=1, padx=10, pady=10, sticky='w')
            
            image_label = Label(self.todo_frame, image=photo, justify='left')
            image_label.image = photo  # Keep a reference to avoid garbage collection
            
            # Create label for displaying todo text
            text_label = Label(self.todo_frame, text=todo_text, bg='white', font=('Arial', 17), wraplength=550)
            text_label.config(bg='#fde100')
            if row[2]:
                text_label.config(font=('Arial', 17, 'overstrike'))  # Strike-through if completed
            text_label.grid(row=row_number, column=2, padx=10, pady=10, sticky='w')
            
            row_number += 1  # Move to the next row

    def mark_a_todo(self, todo_value, current_val):
        if todo_value:
            # Update todo status in the database
            if current_val:
                self.cursor.execute("UPDATE todos SET is_finished = ? WHERE todo = ?", (0, todo_value,))
            else:
                self.cursor.execute("UPDATE todos SET is_finished = ? WHERE todo = ?", (1, todo_value,))
            
            self.conn.commit()
        self.show_all_todos()  # Refresh the todo list
    
    def delete_a_todo(self, value_to_delete):
        # Delete a specific todo from the database
        self.cursor.execute("DELETE FROM todos WHERE todo = ?", (value_to_delete,))
        self.conn.commit()
        self.show_all_todos()  # Refresh the todo list

    def clear_all_todos(self):
        # Delete all todos from the database
        self.cursor.execute("DELETE FROM todos")
        self.conn.commit()
        
        self.clear_button.config(bg='#fde100')  # Reset clear button appearance
        self.show_all_todos()  # Refresh the todo list
