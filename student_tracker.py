import sqlite3
import tkinter as tk
from tkinter import messagebox


class Student:
    """Represent one student's result for a subject."""

    def __init__(self, student_name, subject, mark):
        # Store the information supplied for this student.
        self.student_name = student_name
        self.subject = subject
        self.mark = float(mark)

    def get_grade(self):
        # Convert the numeric mark into the required letter grade.
        if 75 <= self.mark <= 100:
            return "D"
        elif 60 <= self.mark < 75:
            return "M"
        elif 50 <= self.mark < 60:
            return "P"
        return "F"

    def is_passing(self):
        # A mark of 50 or higher is a pass.
        return self.mark >= 50

    def __str__(self):
        # Return the display format required by the assessment.
        return (
            f"Student: {self.student_name} | Subject: {self.subject} | "
            f"Mark: {self.mark:g} | Grade: {self.get_grade()}"
        )


class StudentTrackerApp:
    """Manage the Tkinter interface and SQLite student records."""

    def __init__(self, root):
        # Prepare the database before creating and populating the interface.
        self.root = root
        self.record_ids = []
        self.setup_database()
        self.build_gui()
        self.load_records()

    def setup_database(self):
        # Create the database and required table if they do not exist.
        connection = None
        try:
            connection = sqlite3.connect("tracker.db")
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_name TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    mark REAL NOT NULL,
                    grade TEXT
                )
            """)
            connection.commit()
        except sqlite3.Error as error:
            messagebox.showerror("Database Error", str(error))
        finally:
            if connection is not None:
                connection.close()

    def build_gui(self):
        # Create and arrange all required labels, entries and buttons.
        self.root.title("Student Performance Tracker")
        self.root.geometry("780x520")
        self.root.resizable(False, False)

        form = tk.Frame(self.root, padx=15, pady=15)
        form.pack(fill="x")

        tk.Label(form, text="Student Name").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = tk.Entry(form, width=35)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form, text="Subject").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.subject_entry = tk.Entry(form, width=35)
        self.subject_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form, text="Mark").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.mark_entry = tk.Entry(form, width=35)
        self.mark_entry.grid(row=2, column=1, padx=5, pady=5)

        buttons = tk.Frame(self.root, pady=5)
        buttons.pack()
        tk.Button(buttons, text="Add Record", command=self.add_record).grid(row=0, column=0, padx=8)
        tk.Button(buttons, text="Delete Selected", command=self.delete_record).grid(row=0, column=1, padx=8)
        tk.Button(buttons, text="Clear Fields", command=self.clear_fields).grid(row=0, column=2, padx=8)

        list_frame = tk.Frame(self.root, padx=15, pady=10)
        list_frame.pack(fill="both", expand=True)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.records_listbox = tk.Listbox(
            list_frame, width=105, height=16,
            yscrollcommand=scrollbar.set
        )
        self.records_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.records_listbox.yview)

        self.name_entry.focus_set()

    def add_record(self):
        # Validate the entries, create a Student object and save its details.
        student_name = self.name_entry.get().strip()
        subject = self.subject_entry.get().strip()
        mark_text = self.mark_entry.get().strip()

        if not student_name or not subject or not mark_text:
            messagebox.showwarning("Missing Information", "Please complete all three fields.")
            return

        try:
            mark = float(mark_text)
            if not 0 <= mark <= 100:
                messagebox.showerror("Invalid Mark", "Enter a mark between 0 and 100.")
                return

            student = Student(student_name, subject, mark)
            grade = student.get_grade()

            connection = sqlite3.connect("tracker.db")
            try:
                cursor = connection.cursor()
                cursor.execute(
                    """INSERT INTO results (student_name, subject, mark, grade)
                       VALUES (?, ?, ?, ?)""",
                    (student.student_name, student.subject, student.mark, grade)
                )
                connection.commit()
            finally:
                connection.close()

            self.load_records()
            self.clear_fields()
            messagebox.showinfo("Success", "Student record added successfully.")
        except ValueError:
            messagebox.showerror("Invalid Mark", "The mark must be a number.")
        except sqlite3.Error as error:
            messagebox.showerror("Database Error", str(error))

    def load_records(self):
        # Retrieve records alphabetically and display each Student object.
        self.records_listbox.delete(0, tk.END)
        self.record_ids = []
        connection = None
        try:
            connection = sqlite3.connect("tracker.db")
            cursor = connection.cursor()
            cursor.execute("""
                SELECT id, student_name, subject, mark
                FROM results
                ORDER BY student_name ASC
            """)
            for record_id, student_name, subject, mark in cursor.fetchall():
                student = Student(student_name, subject, mark)
                self.records_listbox.insert(tk.END, str(student))
                self.record_ids.append(record_id)
        except sqlite3.Error as error:
            messagebox.showerror("Database Error", str(error))
        finally:
            if connection is not None:
                connection.close()

    def delete_record(self):
        # Use the selected row's ID and parsed name to delete that exact record.
        selection = self.records_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a student record to delete.")
            return

        selected_index = selection[0]
        selected_text = self.records_listbox.get(selected_index)
        student_name = selected_text.split(" | ")[0].replace("Student: ", "", 1)
        record_id = self.record_ids[selected_index]

        connection = None
        try:
            connection = sqlite3.connect("tracker.db")
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM results WHERE id = ? AND student_name = ?",
                (record_id, student_name)
            )
            connection.commit()
            self.load_records()
            messagebox.showinfo("Success", "Selected record deleted successfully.")
        except sqlite3.Error as error:
            messagebox.showerror("Database Error", str(error))
        finally:
            if connection is not None:
                connection.close()

    def clear_fields(self):
        # Empty all entry widgets and return the cursor to Student Name.
        self.name_entry.delete(0, tk.END)
        self.subject_entry.delete(0, tk.END)
        self.mark_entry.delete(0, tk.END)
        self.name_entry.focus_set()


if __name__ == "__main__":
    # Start the Student Performance Tracker application.
    root = tk.Tk()
    app = StudentTrackerApp(root)
    root.mainloop()
