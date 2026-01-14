import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from services import StudentManager
from models import Student

# --- Color Palette ---
BG_COLOR = "#f4f6f9"       # Light Grey Blue Background
SIDEBAR_COLOR = "#2c3e50"  # Dark Blue/Grey
ACCENT_COLOR = "#3498db"   # Bright Blue
TEXT_COLOR = "#34495e"     # Dark Grey Text
WHITE = "#ffffff"

class StudentManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Tracking System")
        self.root.geometry("1100x700")
        self.root.configure(bg=BG_COLOR)
        
        self.manager = StudentManager()
        
        self.configure_styles()
        self.create_widgets()
        self.refresh_list()

    def configure_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # General Defaults
        self.style.configure(".", 
                             background=BG_COLOR, 
                             foreground=TEXT_COLOR, 
                             font=("Segoe UI", 10))
        
        # Treeview (Table)
        self.style.configure("Treeview",
                             background=WHITE,
                             fieldbackground=WHITE,
                             foreground=TEXT_COLOR,
                             rowheight=30,
                             font=("Segoe UI", 10),
                             borderwidth=0)
        self.style.configure("Treeview.Heading",
                             background=SIDEBAR_COLOR,
                             foreground=WHITE,
                             font=("Segoe UI", 11, "bold"),
                             padding=10)
        self.style.map("Treeview", 
                       background=[('selected', ACCENT_COLOR)], 
                       foreground=[('selected', WHITE)])

        # Buttons
        self.style.configure("Accent.TButton",
                             background=ACCENT_COLOR,
                             foreground=WHITE,
                             font=("Segoe UI", 10, "bold"),
                             padding=(10, 5),
                             borderwidth=0)
        self.style.map("Accent.TButton",
                       background=[('active', "#2980b9")]) # Darker blue on hover
                       
        self.style.configure("Danger.TButton",
                             background="#e74c3c", # Red
                             foreground=WHITE,
                             font=("Segoe UI", 10, "bold"),
                             padding=(10, 5),
                             borderwidth=0)
        self.style.map("Danger.TButton",
                       background=[('active', "#c0392b")])

        # Frames & Labels
        self.style.configure("Card.TFrame", background=WHITE, relief="flat")
        self.style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), background=BG_COLOR, foreground=SIDEBAR_COLOR)
        self.style.configure("SubHeader.TLabel", font=("Segoe UI", 12, "bold"), background=WHITE, foreground=SIDEBAR_COLOR)

    def create_widgets(self):
        # --- Header ---
        header_frame = ttk.Frame(self.root, padding=(20, 20))
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        title_label = ttk.Label(header_frame, text="Student Tracking Dashboard", style="Header.TLabel")
        title_label.pack(side=tk.LEFT)

        # --- Main Content Area ---
        content_frame = ttk.Frame(self.root, padding=(20, 0, 20, 20))
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 1. Action Toolbar (Top of Content)
        toolbar_frame = ttk.Frame(content_frame, padding=(0, 0, 0, 10))
        toolbar_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Left side actions
        ttk.Button(toolbar_frame, text="+ Add Student", style="Accent.TButton", command=self.add_student).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(toolbar_frame, text="Edit", command=self.edit_student).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar_frame, text="Delete", style="Danger.TButton", command=self.delete_student).pack(side=tk.LEFT, padx=5)
        
        # Right side actions (Search)
        search_container = ttk.Frame(toolbar_frame)
        search_container.pack(side=tk.RIGHT)
        
        ttk.Label(search_container, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda name, index, mode: self.refresh_list())
        search_entry = ttk.Entry(search_container, textvariable=self.search_var, width=25)
        search_entry.pack(side=tk.LEFT)

        # 2. Data Table (Treeview) inside a 'Card'
        table_card = ttk.Frame(content_frame, style="Card.TFrame", padding=1) # 1px padding for border effect if needed
        table_card.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        columns = ("id", "name", "surname", "class", "absence", "average")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")
        
        # Configure columns
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("surname", text="Surname")
        self.tree.heading("class", text="Class")
        self.tree.heading("absence", text="Absence")
        self.tree.heading("average", text="GPA")
        
        self.tree.column("id", width=0, stretch=tk.NO)
        self.tree.column("name", width=200, anchor=tk.W)
        self.tree.column("surname", width=200, anchor=tk.W)
        self.tree.column("class", width=100, anchor=tk.CENTER)
        self.tree.column("absence", width=100, anchor=tk.CENTER)
        self.tree.column("average", width=100, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(table_card, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<Double-1>", lambda event: self.view_details())

        # 3. Footer / Secondary Actions
        footer_frame = ttk.Frame(self.root, padding=20)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        ttk.Button(footer_frame, text="View Details / Grades", command=self.view_details).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(footer_frame, text="Manage Attendance", command=self.manage_attendance).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(footer_frame, text="Export CSV", command=self.export_csv).pack(side=tk.RIGHT, padx=5)
        ttk.Button(footer_frame, text="Backup Data", command=self.backup_data).pack(side=tk.RIGHT, padx=5)

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        search_term = self.search_var.get().lower()
        students = self.manager.list_students()
        
        # Apply striped row tags
        self.tree.tag_configure('odd', background=WHITE)
        self.tree.tag_configure('even', background="#f8f9fa")

        count = 0
        for s in students:
            if search_term and (search_term not in s.name.lower() and 
                                search_term not in s.surname.lower()):
                continue
                
            avg = self.manager.calculate_average(s.id)
            tag = 'even' if count % 2 == 0 else 'odd'
            self.tree.insert("", tk.END, values=(s.id, s.name, s.surname, s.class_name, s.absence_count, f"{avg:.2f}"), tags=(tag,))
            count += 1

    def get_selected_id(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Required", "Please select a student from the list.")
            return None
        return self.tree.item(selected_item[0])['values'][0]

    def _create_popup_window(self, title, width=400, height=450):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry(f"{width}x{height}")
        window.configure(bg=WHITE)
        return window

    def add_student(self):
        popup = self._create_popup_window("Add New Student", 350, 400)
        
        content = ttk.Frame(popup, padding=20, style="Card.TFrame")
        content.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(content, text="Student Details", style="SubHeader.TLabel").pack(pady=(0, 20))
        
        ttk.Label(content, text="Name").pack(anchor=tk.W)
        name_entry = ttk.Entry(content)
        name_entry.pack(fill=tk.X, pady=(5, 15))
        
        ttk.Label(content, text="Surname").pack(anchor=tk.W)
        surname_entry = ttk.Entry(content)
        surname_entry.pack(fill=tk.X, pady=(5, 15))
        
        ttk.Label(content, text="Class").pack(anchor=tk.W)
        class_entry = ttk.Entry(content)
        class_entry.pack(fill=tk.X, pady=(5, 20))
        
        def save():
            name = name_entry.get().strip()
            surname = surname_entry.get().strip()
            cls = class_entry.get().strip()
            
            if name and surname and cls:
                self.manager.add_student(name, surname, cls)
                self.refresh_list()
                popup.destroy()
            else:
                messagebox.showerror("Error", "All fields are required.")
                
        ttk.Button(content, text="Save Student", style="Accent.TButton", command=save).pack(fill=tk.X, pady=10)

    def edit_student(self):
        s_id = self.get_selected_id()
        if not s_id: return
        
        student = self.manager.get_student(s_id)
        if not student: return
        
        popup = self._create_popup_window("Edit Student", 350, 400)
        content = ttk.Frame(popup, padding=20, style="Card.TFrame")
        content.pack(fill=tk.BOTH, expand=True)

        ttk.Label(content, text="Edit Details", style="SubHeader.TLabel").pack(pady=(0, 20))
        
        ttk.Label(content, text="Name").pack(anchor=tk.W)
        name_entry = ttk.Entry(content)
        name_entry.insert(0, student.name)
        name_entry.pack(fill=tk.X, pady=(5, 15))
        
        ttk.Label(content, text="Surname").pack(anchor=tk.W)
        surname_entry = ttk.Entry(content)
        surname_entry.insert(0, student.surname)
        surname_entry.pack(fill=tk.X, pady=(5, 15))
        
        ttk.Label(content, text="Class").pack(anchor=tk.W)
        class_entry = ttk.Entry(content)
        class_entry.insert(0, student.class_name)
        class_entry.pack(fill=tk.X, pady=(5, 20))
        
        def save():
            self.manager.update_student(s_id, name_entry.get(), surname_entry.get(), class_entry.get())
            self.refresh_list()
            popup.destroy()
            
        ttk.Button(content, text="Update Student", style="Accent.TButton", command=save).pack(fill=tk.X, pady=10)

    def delete_student(self):
        s_id = self.get_selected_id()
        if not s_id: return
        
        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this student?\nThis action cannot be undone."):
            self.manager.delete_student(s_id)
            self.refresh_list()

    def view_details(self):
        s_id = self.get_selected_id()
        if not s_id: return
        
        student = self.manager.get_student(s_id)
        
        popup = self._create_popup_window(f"Student Profile: {student.name}", 500, 600)
        
        # Main container with padding
        main_container = ttk.Frame(popup, padding=20, style="Card.TFrame")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header Info
        info_frame = ttk.Frame(main_container, style="Card.TFrame")
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(info_frame, text=f"{student.name} {student.surname}", font=("Segoe UI", 16, "bold"), background=WHITE).pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Class: {student.class_name}  |  Absence: {student.absence_count}", foreground="#7f8c8d", background=WHITE).pack(anchor=tk.W, pady=(5, 0))

        # Grades Section
        ttk.Label(main_container, text="Academic Grades", style="SubHeader.TLabel").pack(anchor=tk.W, pady=(0, 10))
        
        grades_frame = ttk.Frame(main_container, style="Card.TFrame")
        grades_frame.pack(fill=tk.BOTH, expand=True)

        # Uses a Treeview for grades instead of plain text for better look
        columns = ("lesson", "grades")
        grades_tree = ttk.Treeview(grades_frame, columns=columns, show="headings", height=8)
        grades_tree.heading("lesson", text="Lesson")
        grades_tree.heading("grades", text="Grades")
        grades_tree.column("lesson", width=150)
        grades_tree.column("grades", width=250)
        grades_tree.pack(fill=tk.BOTH, expand=True)

        def refresh_grades():
            for item in grades_tree.get_children():
                grades_tree.delete(item)
            for lesson, grades in student.grades.items():
                grades_str = ", ".join(map(str, grades))
                grades_tree.insert("", tk.END, values=(lesson, grades_str))

        refresh_grades()
        
        # Add Grade Section
        add_frame = ttk.LabelFrame(main_container, text="Add New Grade", padding=15)
        add_frame.pack(fill=tk.X, pady=20)
        
        input_row = ttk.Frame(add_frame)
        input_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_row, text="Lesson:").pack(side=tk.LEFT)
        lesson_entry = ttk.Entry(input_row, width=15)
        lesson_entry.pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(input_row, text="Score:").pack(side=tk.LEFT)
        grade_entry = ttk.Entry(input_row, width=8)
        grade_entry.pack(side=tk.LEFT, padx=5)
        
        def add_grade():
            try:
                lesson = lesson_entry.get().strip()
                grade = int(grade_entry.get().strip())
                if 0 <= grade <= 100:
                    self.manager.add_grade(s_id, lesson, grade)
                    refresh_grades()
                    lesson_entry.delete(0, tk.END)
                    grade_entry.delete(0, tk.END)
                    self.refresh_list()
                else:
                    messagebox.showerror("Error", "Grade must be between 0 and 100.")
            except ValueError:
                messagebox.showerror("Error", "Invalid numeric input.")
        
        ttk.Button(input_row, text="Add", style="Accent.TButton", command=add_grade).pack(side=tk.LEFT, padx=15)

    def manage_attendance(self):
        s_id = self.get_selected_id()
        if not s_id: return
        
        student = self.manager.get_student(s_id)
        
        # Custom Dialog for nicer look
        popup = self._create_popup_window("Attendance", 300, 250)
        content = ttk.Frame(popup, padding=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(content, text=f"Update Absence", style="SubHeader.TLabel").pack(pady=(0, 10))
        ttk.Label(content, text=f"Current Total: {student.absence_count}", foreground="#7f8c8d").pack(pady=(0, 20))
        
        val_frame = ttk.Frame(content)
        val_frame.pack()
        
        days_var = tk.StringVar(value="1")
        spinbox = ttk.Spinbox(val_frame, from_=-20, to=20, textvariable=days_var, width=10)
        spinbox.pack(pady=5)
        ttk.Label(val_frame, text="(Use negative to reduce)").pack(pady=(0, 15), font=("Segoe UI", 8))
        
        def commit():
            try:
                amount = int(days_var.get())
                if self.manager.update_attendance(s_id, amount):
                    self.refresh_list()
                    popup.destroy()
                else:
                    messagebox.showerror("Error", "Result cannot be negative.")
            except ValueError:
                messagebox.showerror("Error", "Invalid number.")

        ttk.Button(content, text="Save", style="Accent.TButton", command=commit).pack(fill=tk.X)

    def backup_data(self):
        res = self.manager.backup_data()
        messagebox.showinfo("Backup Status", res)

    def export_csv(self):
        res = self.manager.export_csv()
        messagebox.showinfo("Export Status", res)

if __name__ == "__main__":
    root = tk.Tk()
    # Attempt to set High DPI awareness on Windows if applicable
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
        
    app = StudentManagerApp(root)
    root.mainloop()
