
import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
import re

# Premium Theme Colors
COLOR_BG_PRIMARY = "#f0f2f5"  # Slightly darker gray for background contrast
COLOR_HEADER = "#ffffff"
COLOR_NAV_TEXT = "#4b6584"
COLOR_NAV_ACTIVE = "#3867d6"
COLOR_CARD_BG = "#ffffff"
COLOR_ACCENT = "#3867d6"
COLOR_SUCCESS = "#20bf6b"
COLOR_DANGER = "#eb3b5a"
COLOR_BORDER = "#d1d8e0"
COLOR_CARD_SHADOW = "#cbd3da" # Simulation for shadow

# Fonts
FONT_HEADER = ("Helvetica", 18, "bold")
FONT_TAB = ("Helvetica", 9, "bold")
FONT_TITLE = ("Helvetica", 13, "bold")
FONT_LABEL = ("Helvetica", 10, "bold") # More punchy labels
FONT_ENTRY = ("Helvetica", 11)
FONT_CARD_DATA = ("Helvetica", 10)

class RecordSystemApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RMS Mobile")
        # Standard mobile aspect ratio
        self.geometry("400x700")
        self.configure(bg=COLOR_BG_PRIMARY)
        
        # Main Layout: Header, Content, Footer
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # --- Header ---
        self.header = tk.Frame(self, bg=COLOR_HEADER, height=60, bd=0, highlightthickness=1, highlightbackground=COLOR_BORDER)
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)
        
        self.lbl_header = tk.Label(self.header, text="Records", bg=COLOR_HEADER, fg=COLOR_NAV_TEXT, font=FONT_HEADER)
        self.lbl_header.pack(expand=True)
        
        # --- Body (Content Area) ---
        self.container = tk.Frame(self, bg=COLOR_BG_PRIMARY)
        self.container.grid(row=1, column=0, sticky="nsew")
        
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # --- Footer (Navigation) ---
        self.footer = tk.Frame(self, bg=COLOR_HEADER, height=70, highlightthickness=1, highlightbackground=COLOR_BORDER)
        self.footer.grid(row=2, column=0, sticky="ew")
        self.footer.grid_propagate(False)
        
        self.nav_buttons = {}
        # Nav Buttons in Footer
        self.footer.grid_columnconfigure(0, weight=1)
        self.footer.grid_columnconfigure(1, weight=1)
        
        self.btn_view = self.create_nav_btn("View", 0, lambda: self.show_frame("ViewRecordsScreen"))
        self.btn_add = self.create_nav_btn("Add", 1, lambda: self.show_frame("AddRecordScreen"))
        
        self.frames = {}
        for F in (ViewRecordsScreen, AddRecordScreen):
            name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("ViewRecordsScreen")

    def create_nav_btn(self, text, col, cmd):
        btn_frame = tk.Frame(self.footer, bg=COLOR_HEADER)
        btn_frame.grid(row=0, column=col, sticky="nsew")
        
        btn = tk.Button(btn_frame, text=text, font=FONT_TAB, fg=COLOR_NAV_TEXT, bg=COLOR_HEADER, 
                        bd=0, activebackground=COLOR_HEADER, cursor="hand2", command=cmd)
        btn.pack(expand=True, fill="both", pady=10)
        
        self.nav_buttons[text] = btn
        return btn

    def show_frame(self, name):
        frame = self.frames[name]
        self.lbl_header.config(text="Add Record" if name == "AddRecordScreen" else "Records")
        
        # Update Nav Styles
        for text, btn in self.nav_buttons.items():
            if (text == "View" and name == "ViewRecordsScreen") or (text == "Add" and name == "AddRecordScreen"):
                btn.config(fg=COLOR_NAV_ACTIVE)
            else:
                btn.config(fg=COLOR_NAV_TEXT)
        
        if hasattr(frame, 'on_show'):
            frame.on_show()
        frame.tkraise()

    def validate_contact(self, P):
        # P is the value if the change is allowed
        if len(P) > 11:
            return False
        if P == "" or P.isdigit():
            return True
        return False

    def validate_age(self, P):
        if len(P) > 3: # Reasonable age limit digits
            return False
        if P == "" or P.isdigit():
            return True
        return False

class ViewRecordsScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BG_PRIMARY)
        self.controller = controller
        
        # --- Search Bar ---
        search_frame = tk.Frame(self, bg=COLOR_BG_PRIMARY, padx=15, pady=5)
        search_frame.pack(fill="x")
        
        self.search_ent = tk.Entry(search_frame, font=FONT_ENTRY, bg="#ffffff", bd=1, relief="flat",
                                   highlightthickness=1, highlightbackground=COLOR_BORDER)
        self.search_ent.pack(fill="x", ipady=8)
        self.search_ent.insert(0, "Search records...")
        self.search_ent.bind("<FocusIn>", self._clear_search_placeholder)
        self.search_ent.bind("<FocusOut>", self._restore_search_placeholder)
        self.search_ent.bind("<KeyRelease>", lambda e: self.load_records())

        # List of Records (Using a Frame to hold Canvas + Scrollbar)
        list_container = tk.Frame(self, bg=COLOR_BG_PRIMARY)
        list_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Use tk.Scrollbar for better control/visibility
        self.scrollbar = tk.Scrollbar(list_container, orient="vertical", bg=COLOR_BG_PRIMARY, width=16)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas = tk.Canvas(list_container, bg=COLOR_BG_PRIMARY, highlightthickness=0, yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.scrollbar.config(command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas, bg=COLOR_BG_PRIMARY)
        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Sync width of scrollable frame on canvas resize
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Bind mouse wheel for scrolling when mouse enters the scrollable area
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if not self.canvas.winfo_exists():
            return
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def _clear_search_placeholder(self, event):
        if self.search_ent.get() == "Search records...":
            self.search_ent.delete(0, tk.END)
            self.search_ent.config(fg="black")

    def _restore_search_placeholder(self, event):
        if not self.search_ent.get():
            self.search_ent.insert(0, "Search records...")
            self.search_ent.config(fg="gray")
        
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.window_id, width=event.width)

    def on_show(self):
        self.load_records()

    def load_records(self):
        # Clear frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        try:
            query = self.search_ent.get()
            if query == "Search records...":
                query = None
                
            records = Database().get_records(query)
            if not records:
                msg = "No results found" if query else "No records yet"
                tk.Label(self.scrollable_frame, text=msg, bg=COLOR_BG_PRIMARY, font=FONT_LABEL).pack(pady=50)
                return
                
            for rec in records:
                # rec: (id, name, age, address, contact, email)
                self.create_card(rec)
                
            # Reset scroll to top on reload
            self.canvas.yview_moveto(0)
            
            # Use a tiny delay (after items are drawn) to update scrollbox
            self.scrollable_frame.after(100, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_card(self, rec):
        # Card Container (Shadow Simulation Layer)
        shadow_frame = tk.Frame(self.scrollable_frame, bg=COLOR_CARD_SHADOW, pady=0, padx=0)
        shadow_frame.pack(fill="x", pady=(5, 12), padx=8)
        
        # Main Card Body
        card = tk.Frame(shadow_frame, bg=COLOR_CARD_BG, pady=18, padx=18, 
                        highlightthickness=1, highlightbackground=COLOR_BORDER)
        card.pack(fill="x", pady=(0, 2), padx=(0, 0)) # Offset to show shadow
        
        # Content
        title_lbl = tk.Label(card, text=rec[1].upper(), font=FONT_TITLE, bg=COLOR_CARD_BG, fg=COLOR_NAV_TEXT, anchor="w")
        title_lbl.pack(fill="x")
        
        # Divider Line
        divider = tk.Frame(card, bg=COLOR_BG_PRIMARY, height=1)
        divider.pack(fill="x", pady=10)
        
        details_frame = tk.Frame(card, bg=COLOR_CARD_BG)
        details_frame.pack(fill="x")
        
        def add_info(lbl, val):
            row = tk.Frame(details_frame, bg=COLOR_CARD_BG)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=lbl, font=("Helvetica", 8, "bold"), bg=COLOR_CARD_BG, fg="#a5b1c2", width=8, anchor="w").pack(side="left")
            tk.Label(row, text=val, font=FONT_CARD_DATA, bg=COLOR_CARD_BG, fg="#4b6584").pack(side="left")

        add_info("ID:", rec[6])
        add_info("AGE:", rec[2])
        add_info("COURSE:", rec[7])
        add_info("SEC:", rec[8])
        add_info("PHONE:", rec[4])
        add_info("EMAIL:", rec[5])
        add_info("ADDR:", rec[3])
        
        # Actions bar
        actions = tk.Frame(card, bg=COLOR_CARD_BG)
        actions.pack(fill="x", pady=(15, 0))
        
        edit_btn = tk.Button(actions, text="EDIT DETAILS", font=FONT_TAB, fg=COLOR_NAV_ACTIVE, bg="#f1f2f6", bd=0, 
                             activeforeground=COLOR_NAV_ACTIVE, cursor="hand2", command=lambda r=rec: self.edit_rec(r),
                             padx=10, pady=5)
        edit_btn.pack(side="left", padx=(0, 10))
        
        del_btn = tk.Button(actions, text="DELETE", font=FONT_TAB, fg=COLOR_DANGER, bg="#fff5f5", bd=0, 
                            activeforeground=COLOR_DANGER, cursor="hand2", command=lambda r=rec: self.delete_rec(r[0]),
                            padx=10, pady=5)
        del_btn.pack(side="left")

    def delete_rec(self, rid):
        if messagebox.askyesno("Confirm", "Delete this record?"):
            Database().delete_record(rid)
            self.load_records()

    def edit_rec(self, rec):
        EditSheet(self, rec, self.load_records)

class AddRecordScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BG_PRIMARY)
        self.controller = controller
        
        # Scrollable setup for AddRecordScreen
        # Use tk.Scrollbar for better control/visibility
        self.scrollbar = tk.Scrollbar(self, orient="vertical", bg=COLOR_BG_PRIMARY, width=16)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas = tk.Canvas(self, bg=COLOR_BG_PRIMARY, highlightthickness=0, yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.scrollbar.config(command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas, bg=COLOR_BG_PRIMARY)
        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Sync width of inner frame to canvas width
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Bind mouse wheel for scrolling when mouse enters the scrollable area
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

        # --- Form Content ---
        self.form_container = tk.Frame(self.scrollable_frame, bg=COLOR_BG_PRIMARY, padx=30, pady=30)
        self.form_container.pack(fill="both", expand=True)
        
        # Elevation layer for form
        shadow = tk.Frame(self.form_container, bg=COLOR_CARD_SHADOW)
        shadow.pack(fill="both", expand=True)
        
        inner_form = tk.Frame(shadow, bg=COLOR_CARD_BG, padx=20, pady=20, highlightthickness=1, highlightbackground=COLOR_BORDER)
        inner_form.pack(fill="both", expand=True, pady=(0, 3))

        self.entries = {}
        fields = ["Name", "Age", "Course", "Section", "Address", "Contact", "Email"]
        
        vcmd_contact = (self.register(self.controller.validate_contact), '%P')
        vcmd_age = (self.register(self.controller.validate_age), '%P')
        
        for field in fields:
            tk.Label(inner_form, text=field.upper(), bg=COLOR_CARD_BG, font=FONT_LABEL, fg="#a5b1c2").pack(anchor="w", pady=(10, 2))
            if field == "Contact":
                ent = tk.Entry(inner_form, font=FONT_ENTRY, bg="#f8f9fa", bd=1, relief="flat", 
                               highlightthickness=1, highlightbackground=COLOR_BORDER,
                               validate='key', validatecommand=vcmd_contact)
            elif field == "Age":
                ent = tk.Entry(inner_form, font=FONT_ENTRY, bg="#f8f9fa", bd=1, relief="flat", 
                               highlightthickness=1, highlightbackground=COLOR_BORDER,
                               validate='key', validatecommand=vcmd_age)
            else:
                ent = tk.Entry(inner_form, font=FONT_ENTRY, bg="#f8f9fa", bd=1, relief="flat", 
                               highlightthickness=1, highlightbackground=COLOR_BORDER)
            ent.pack(fill="x", ipady=10)
            self.entries[field] = ent
            
        # Submit Button
        self.btn_submit = tk.Button(inner_form, text="SAVE NEW RECORD", bg=COLOR_ACCENT, fg="white", 
                                    font=FONT_TITLE, bd=0, activebackground="#2980b9", activeforeground="white", 
                                    cursor="hand2", command=self.save, pady=15)
        self.btn_submit.pack(fill="x", pady=(30, 10))

        # Explicitly update scrollregion after layout with a tiny delay
        self.scrollable_frame.after(100, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.window_id, width=event.width)

    def _on_mousewheel(self, event):
        if not self.canvas.winfo_exists():
            return
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def save(self):
        data = {k: v.get().strip() for k, v in self.entries.items()}
        name = data["Name"]
        age = data["Age"]
        course = data["Course"]
        section = data["Section"]
        address = data["Address"]
        contact = data["Contact"]
        email = data["Email"]

        if not all(data.values()):
            messagebox.showerror("Validation", "Please fill all fields")
            return
        
        # Validations
        if not age.isdigit() or int(age) <= 0:
            messagebox.showerror("Validation", "Age must be a positive number")
            return

        if not contact.isdigit():
            messagebox.showerror("Validation", "Contact must contain only numbers (no letters)")
            return

        if len(contact) != 11:
            messagebox.showerror("Validation", "Contact number must be exactly 11 digits")
            return

        if "@" not in email:
            messagebox.showerror("Validation", "Invalid Email: Must contain '@'")
            return
        
        if "'" in email or '"' in email:
            messagebox.showerror("Validation", "Email cannot contain quotation marks")
            return
            
        # Basic Email Regex for better assurance
        if not re.match(r"[^@\"']+\@[^@\"']+\.[^@\"']+", email):
            messagebox.showerror("Validation", "Invalid Email format (e.g. user@example.com) and no quotes allowed")
            return
            
        try:
            db = Database()
            # Check for duplicates (Name or Email) - Student ID is auto-generated
            # Email uniqueness is now enforced both in logic and DB
            if not db.verify_not_exists(None, name, email):
                messagebox.showerror("Duplicate Found", "This Name or Email is already registered to another student. Please use a unique Email.")
                return

            db.add_record(name, int(age), course, section, address, contact, email)
            self.clear()
            self.controller.show_frame("ViewRecordsScreen")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear(self):
        for e in self.entries.values():
            e.delete(0, tk.END)


class EditSheet(tk.Toplevel):
    def __init__(self, parent, rec, callback):
        super().__init__(parent)
        self.callback = callback
        self.rid = rec[0]
        self.title("Update Entry")
        self.geometry("400x600")
        self.configure(bg=COLOR_BG_PRIMARY)
        
        # Scrollable setup for EditSheet
        sheet_container = tk.Frame(self, bg=COLOR_BG_PRIMARY)
        sheet_container.pack(fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(sheet_container, orient="vertical", width=16)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas = tk.Canvas(sheet_container, bg=COLOR_BG_PRIMARY, highlightthickness=0, yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.scrollbar.config(command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas, bg=COLOR_BG_PRIMARY)
        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Sync width
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Mousewheel binding (Robust enter/leave)
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

        self.container = tk.Frame(self.scrollable_frame, bg=COLOR_BG_PRIMARY, padx=20, pady=20)
        self.container.pack(fill="both", expand=True)
        
        tk.Label(self.container, text="Update Record", font=FONT_TITLE, bg=COLOR_BG_PRIMARY, fg=COLOR_NAV_TEXT).pack(pady=(0, 20))
        
        self.entries = {}
        fields = ["Student ID", "Name", "Age", "Course", "Section", "Address", "Contact", "Email"]
        current = [rec[6], rec[1], rec[2], rec[7], rec[8], rec[3], rec[4], rec[5]]
        
        vcmd_contact = (self.register(parent.controller.validate_contact), '%P')
        vcmd_age = (self.register(parent.controller.validate_age), '%P')
        
        for i, field in enumerate(fields):
            tk.Label(self.container, text=field, bg=COLOR_BG_PRIMARY, font=FONT_LABEL).pack(anchor="w", pady=(10, 2))
            if field == "Student ID":
                ent = tk.Entry(self.container, font=FONT_ENTRY, bg="#f1f2f6", bd=1, relief="flat", 
                               highlightthickness=1, highlightbackground=COLOR_BORDER)
                ent.insert(0, str(current[i]))
                ent.config(state="readonly")
            elif field == "Contact":
                ent = tk.Entry(self.container, font=FONT_ENTRY, bg="#ffffff", bd=1, relief="flat", 
                               highlightthickness=1, highlightbackground=COLOR_BORDER,
                               validate='key', validatecommand=vcmd_contact)
            elif field == "Age":
                ent = tk.Entry(self.container, font=FONT_ENTRY, bg="#ffffff", bd=1, relief="flat", 
                               highlightthickness=1, highlightbackground=COLOR_BORDER,
                               validate='key', validatecommand=vcmd_age)
            else:
                ent = tk.Entry(self.container, font=FONT_ENTRY, bg="#ffffff", bd=1, relief="flat", 
                               highlightthickness=1, highlightbackground=COLOR_BORDER)
            ent.insert(0, str(current[i]))
            ent.pack(fill="x", ipady=8)
            self.entries[field] = ent
            
        tk.Button(self.container, text="Confirm Changes", bg=COLOR_ACCENT, fg="white", 
                  font=FONT_TITLE, bd=0, cursor="hand2", command=self.save, pady=12).pack(fill="x", pady=30)

        # Explicitly update scrollregion after layout with a tiny delay
        self.scrollable_frame.after(100, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.window_id, width=event.width)

    def _on_mousewheel(self, event):
        if not self.canvas.winfo_exists():
            return
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def save(self):
        data = {k: v.get().strip() for k, v in self.entries.items()}
        student_id = data["Student ID"]
        name = data["Name"]
        age = data["Age"]
        course = data["Course"]
        section = data["Section"]
        address = data["Address"]
        contact = data["Contact"]
        email = data["Email"]

        if not all(data.values()):
            messagebox.showerror("Error", "Required fields empty.")
            return

        if not age.isdigit() or int(age) <= 0:
            messagebox.showerror("Validation", "Age must be a positive number")
            return

        if not contact.isdigit():
            messagebox.showerror("Validation", "Contact must contain only numbers (no letters)")
            return

        if len(contact) != 11:
            messagebox.showerror("Validation", "Contact number must be exactly 11 digits")
            return

        if "@" not in email:
            messagebox.showerror("Validation", "Invalid Email: Must contain '@'")
            return
            
        if "'" in email or '"' in email:
            messagebox.showerror("Validation", "Email cannot contain quotation marks")
            return
            
        if not re.match(r"[^@\"']+\@[^@\"']+\.[^@\"']+", email):
            messagebox.showerror("Validation", "Invalid Email format and no quotes allowed")
            return

        try:
             db = Database()
             # Check for duplicates excluding current record
             if not db.verify_not_exists(student_id, name, email, exclude_id=self.rid):
                 messagebox.showerror("Duplicate Found", "Another record with this ID, Name or Email already exists. Please ensure the Name and Email are unique.")
                 return

             db.update_record(self.rid, student_id, name, int(age), course, section, address, contact, email)
             self.callback()
             self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = RecordSystemApp()
    app.mainloop()
