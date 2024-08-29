import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import csv
from collections import Counter
import webbrowser
import atexit

from utils import export_to_latex

class LiteratureReviewApp:
    def __init__(self, master):
        self.master = master
        self.master.title("LiTTApp")
        self.master.geometry("800x600")

        self.papers = []
        self.undo_stack = []
        self.redo_stack = []

        # Create and set up the notebook
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Create tabs
        self.add_paper_tab = ttk.Frame(self.notebook)
        self.view_papers_tab = ttk.Frame(self.notebook)
        self.statistics_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.add_paper_tab, text="Add Paper")
        self.notebook.add(self.view_papers_tab, text="View Papers")
        self.notebook.add(self.statistics_tab, text="Statistics")

        self.setup_add_paper_tab()
        self.setup_view_papers_tab()
        self.setup_statistics_tab()

        # Set up menu
        self.setup_menu()

        # Auto-load data and state
        self.auto_load()

        # Register auto-save on exit
        atexit.register(self.auto_save)

        # Setup keyboard shortcuts
        self.setup_shortcuts()

        # Initialize style for dark mode
        self.style = ttk.Style(self.master)
        self.dark_mode = False  # Track whether dark mode is active

    def setup_menu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save", command=self.save_to_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Load", command=self.load_from_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Export as CSV", command=self.export_csv)
        file_menu.add_command(label="Export to Word", command=lambda: export_to_word(self.papers))
        file_menu.add_command(label="Export to LaTeX", command=lambda: export_to_latex(self.papers))
        file_menu.add_command(label="Backup", command=self.backup_data)
        file_menu.add_command(label="Restore", command=self.restore_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit, accelerator="Ctrl+Q")

        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")

        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Advanced Search", command=self.setup_advanced_search, accelerator="Ctrl+F")
        tools_menu.add_command(label="Set Reminder", command=self.set_reminder)

        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode, accelerator="Ctrl+D")

    def setup_add_paper_tab(self):
        # Compact layout for "Add Paper" tab
        fields = [("Title:", "title"), ("Authors:", "authors"), ("Year:", "year"), 
                  ("DOI:", "doi"), ("Categories:", "categories"), ("Tags:", "tags")]
        
        for i, (label, attr) in enumerate(fields):
            tk.Label(self.add_paper_tab, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = tk.Entry(self.add_paper_tab, width=50)
            if attr == "year":
                entry.insert(0, tk.StringVar(value="2024").get())  # Default to current year
            entry.grid(row=i, column=1, columnspan=2, padx=5, pady=5)
            setattr(self, f"{attr}_entry", entry)

        # Summary
        tk.Label(self.add_paper_tab, text="Summary:").grid(row=len(fields), column=0, sticky="ne", padx=5, pady=5)
        self.summary_text = tk.Text(self.add_paper_tab, width=50, height=5)
        self.summary_text.grid(row=len(fields), column=1, columnspan=2, padx=5, pady=5)

        # Notes
        tk.Label(self.add_paper_tab, text="Notes:").grid(row=len(fields)+1, column=0, sticky="ne", padx=5, pady=5)
        self.notes_text = tk.Text(self.add_paper_tab, width=50, height=5)
        self.notes_text.grid(row=len(fields)+1, column=1, columnspan=2, padx=5, pady=5)

        # Add Paper Button
        self.add_button = tk.Button(self.add_paper_tab, text="Add Paper", command=self.add_paper)
        self.add_button.grid(row=len(fields)+2, column=1, sticky="e", padx=5, pady=10)

    def setup_view_papers_tab(self):
        # Integrated Search and Filter Bar
        search_frame = ttk.Frame(self.view_papers_tab)
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="Search:").pack(side="left")
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.filter_papers)

        tk.Label(search_frame, text="Category:").pack(side="left", padx=(20, 5))
        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(search_frame, textvariable=self.category_var)
        self.category_combobox.pack(side="left")
        self.category_combobox.bind("<<ComboboxSelected>>", self.filter_papers)

        tk.Label(search_frame, text="Tag:").pack(side="left", padx=(20, 5))
        self.tag_var = tk.StringVar()
        self.tag_combobox = ttk.Combobox(search_frame, textvariable=self.tag_var)
        self.tag_combobox.pack(side="left")
        self.tag_combobox.bind("<<ComboboxSelected>>", self.filter_papers)

        # Treeview
        self.tree = ttk.Treeview(self.view_papers_tab, columns=("Title", "Authors", "Year", "Tags"), show="headings")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Authors", text="Authors")
        self.tree.heading("Year", text="Year")
        self.tree.heading("Tags", text="Tags")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Contextual actions via right-click menu
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Buttons
        button_frame = ttk.Frame(self.view_papers_tab)
        button_frame.pack(fill="x", padx=10, pady=5)

        buttons = [
            ("View Details", self.view_paper_details),
            ("Edit Paper", self.edit_paper),
            ("Delete Paper", self.delete_paper),
            ("Open DOI", self.open_doi)
        ]

        for text, command in buttons:
            ttk.Button(button_frame, text=text, command=command).pack(side="left", padx=5)

    def show_context_menu(self, event):
        menu = tk.Menu(self.master, tearoff=0)
        menu.add_command(label="View Details", command=self.view_paper_details)
        menu.add_command(label="Edit Paper", command=self.edit_paper)
        menu.add_command(label="Delete Paper", command=self.delete_paper)
        menu.add_command(label="Open DOI", command=self.open_doi)
        menu.tk_popup(event.x_root, event.y_root)

    def setup_statistics_tab(self):
        self.stats_text = tk.Text(self.statistics_tab, wrap=tk.WORD, width=70, height=20)
        self.stats_text.pack(expand=True, fill="both", padx=10, pady=10)
        self.update_statistics()

    def setup_shortcuts(self):
        self.master.bind("<Control-s>", lambda event: self.save_to_file())
        self.master.bind("<Control-o>", lambda event: self.load_from_file())
        self.master.bind("<Control-q>", lambda event: self.master.quit())
        self.master.bind("<Control-f>", lambda event: self.setup_advanced_search())
        self.master.bind("<Control-z>", lambda event: self.undo())
        self.master.bind("<Control-y>", lambda event: self.redo())
        self.master.bind("<Control-d>", lambda event: self.toggle_dark_mode())

    def add_paper(self):
        title = self.title_entry.get()
        authors = self.authors_entry.get()
        year = self.year_entry.get()
        doi = self.doi_entry.get()
        categories = [cat.strip() for cat in self.categories_entry.get().split(',')]
        tags = [tag.strip() for tag in self.tags_entry.get().split(',')]
        summary = self.summary_text.get("1.0", tk.END).strip()
        notes = self.notes_text.get("1.0", tk.END).strip()

        if not all([title, authors, year]):
            messagebox.showerror("Error", "Title, Authors, and Year are required!")
            return

        paper = {
            "title": title,
            "authors": authors,
            "year": year,
            "doi": doi,
            "categories": categories,
            "tags": tags,
            "summary": summary,
            "notes": notes
        }

        self.undo_stack.append((self.papers.copy(), "Add Paper"))
        self.redo_stack.clear()

        self.papers.append(paper)
        self.tree.insert("", tk.END, values=(title, authors, year, ", ".join(tags)))
        self.clear_fields()
        self.update_statistics()
        self.update_category_filter()
        self.update_tag_filter()

        messagebox.showinfo("Success", "Paper added successfully!")

    def clear_fields(self):
        for widget in self.add_paper_tab.winfo_children():
            if isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)
            elif isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)

    def view_paper_details(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a paper to view details.")
            return

        index = self.tree.index(selected_item)
        paper = self.papers[index]

        details_window = tk.Toplevel(self.master)
        details_window.title("Paper Details")
        details_window.geometry("500x400")

        for key, value in paper.items():
            if key in ['summary', 'notes']:
                tk.Label(details_window, text=f"{key.capitalize()}:").pack(anchor="w", padx=10, pady=5)
                text = tk.Text(details_window, wrap=tk.WORD, width=60, height=5)
                text.insert(tk.END, value)
                text.config(state=tk.DISABLED)
                text.pack(padx=10, pady=5)
            else:
                tk.Label(details_window, text=f"{key.capitalize()}: {value}").pack(anchor="w", padx=10, pady=5)

    def edit_paper(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a paper to edit.")
            return

        index = self.tree.index(selected_item)
        paper = self.papers[index]

        # Pre-fill the fields with the selected paper's details
        self.title_entry.insert(0, paper['title'])
        self.authors_entry.insert(0, paper['authors'])
        self.year_entry.insert(0, paper['year'])
        self.doi_entry.insert(0, paper['doi'])
        self.categories_entry.insert(0, ', '.join(paper['categories']))
        self.tags_entry.insert(0, ', '.join(paper['tags']))
        self.summary_text.insert(tk.END, paper['summary'])
        self.notes_text.insert(tk.END, paper['notes'])

        # Change the Add Paper button to Update Paper
        self.add_button.config(text="Update Paper", command=lambda: self.update_paper(index))

        # Switch to the Add Paper tab
        self.notebook.select(self.add_paper_tab)

    def update_paper(self, index):
        paper = self.papers[index]
        paper['title'] = self.title_entry.get()
        paper['authors'] = self.authors_entry.get()
        paper['year'] = self.year_entry.get()
        paper['doi'] = self.doi_entry.get()
        paper['categories'] = [cat.strip() for cat in self.categories_entry.get().split(',')]
        paper['tags'] = [tag.strip() for tag in self.tags_entry.get().split(',')]
        paper['summary'] = self.summary_text.get("1.0", tk.END).strip()
        paper['notes'] = self.notes_text.get("1.0", tk.END).strip()

        self.undo_stack.append((self.papers.copy(), "Edit Paper"))
        self.redo_stack.clear()

        self.tree.item(self.tree.get_children()[index], values=(paper['title'], paper['authors'], paper['year'], ", ".join(paper['tags'])))
        self.clear_fields()
        self.update_statistics()
        self.update_category_filter()
        self.update_tag_filter()

        # Reset the Add Paper button
        self.add_button.config(text="Add Paper", command=self.add_paper)

        messagebox.showinfo("Success", "Paper updated successfully!")

    def delete_paper(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a paper to delete.")
            return

        index = self.tree.index(selected_item)
        self.undo_stack.append((self.papers.copy(), "Delete Paper"))
        self.redo_stack.clear()

        del self.papers[index]
        self.tree.delete(selected_item)
        self.update_statistics()
        self.update_category_filter()
        self.update_tag_filter()

        messagebox.showinfo("Success", "Paper deleted successfully!")

    def open_doi(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a paper to open its DOI.")
            return

        index = self.tree.index(selected_item)
        paper = self.papers[index]
        doi = paper.get('doi')

        if doi:
            webbrowser.open(f"https://doi.org/{doi}")
        else:
            messagebox.showinfo("Info", "This paper does not have a DOI.")

    def save_to_file(self):
        if not self.papers:
            messagebox.showerror("Error", "No papers to save!")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not file_path:
            return

        with open(file_path, "w") as f:
            json.dump(self.papers, f, indent=2)

        messagebox.showinfo("Success", f"Papers saved to {file_path}")

    def load_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not file_path:
            return

        try:
            with open(file_path, "r") as f:
                self.papers = json.load(f)

            self.tree.delete(*self.tree.get_children())

            for paper in self.papers:
                self.tree.insert("", tk.END, values=(paper["title"], paper["authors"], paper["year"], ", ".join(paper["tags"])))

            self.update_statistics()
            self.update_category_filter()
            self.update_tag_filter()
            messagebox.showinfo("Success", f"Papers loaded from {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load papers: {str(e)}")

    def filter_papers(self, event=None):
        search_query = self.search_entry.get().lower()
        category_filter = self.category_var.get()
        tag_filter = self.tag_var.get()

        self.tree.delete(*self.tree.get_children())

        for paper in self.papers:
            if all([
                search_query in paper["title"].lower() or search_query in paper["authors"].lower() or search_query in paper["year"],
                not category_filter or category_filter in paper["categories"],
                not tag_filter or tag_filter in paper["tags"]
            ]):
                self.tree.insert("", tk.END, values=(paper["title"], paper["authors"], paper["year"], ", ".join(paper["tags"])))

    def update_statistics(self):
        if not self.papers:
            self.stats_text.delete("1.0", tk.END)
            self.stats_text.insert(tk.END, "No papers available.")
            return

        years = [int(paper['year']) for paper in self.papers]
        year_counter = Counter(years)

        categories = [cat for paper in self.papers for cat in paper['categories']]
        category_counter = Counter(categories)

        tags = [tag for paper in self.papers for tag in paper['tags']]
        tag_counter = Counter(tags)

        stats_summary = (
            f"Total Papers: {len(self.papers)}\n"
            f"Year Distribution:\n"
            + "\n".join([f"{year}: {count}" for year, count in year_counter.items()]) + "\n\n"
            f"Category Distribution:\n"
            + "\n".join([f"{category}: {count}" for category, count in category_counter.items()]) + "\n\n"
            f"Tag Distribution:\n"
            + "\n".join([f"{tag}: {count}" for tag, count in tag_counter.items()])
        )

        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert(tk.END, stats_summary)

    def update_category_filter(self):
        categories = sorted(set(cat for paper in self.papers for cat in paper['categories']))
        self.category_combobox['values'] = [""] + categories

    def update_tag_filter(self):
        tags = sorted(set(tag for paper in self.papers for tag in paper['tags']))
        self.tag_combobox['values'] = [""] + tags

    def export_csv(self):
        if not self.papers:
            messagebox.showerror("Error", "No papers to export!")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        try:
            with open(file_path, "w", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["title", "authors", "year", "doi", "categories", "tags", "summary", "notes"])
                writer.writeheader()
                for paper in self.papers:
                    paper_copy = paper.copy()
                    paper_copy["categories"] = ", ".join(paper_copy["categories"])
                    paper_copy["tags"] = ", ".join(paper_copy["tags"])
                    writer.writerow(paper_copy)
            messagebox.showinfo("Success", f"Papers exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export papers: {str(e)}")

    def undo(self):
        if self.undo_stack:
            last_action = self.undo_stack.pop()
            self.redo_stack.append((self.papers.copy(), last_action[1]))
            self.papers = last_action[0]
            self.tree.delete(*self.tree.get_children())
            for paper in self.papers:
                self.tree.insert("", tk.END, values=(paper["title"], paper["authors"], paper["year"], ", ".join(paper["tags"])))
            self.update_statistics()
            self.update_category_filter()
            self.update_tag_filter()

    def redo(self):
        if self.redo_stack:
            next_action = self.redo_stack.pop()
            self.undo_stack.append((self.papers.copy(), next_action[1]))
            self.papers = next_action[0]
            self.tree.delete(*self.tree.get_children())
            for paper in self.papers:
                self.tree.insert("", tk.END, values=(paper["title"], paper["authors"], paper["year"], ", ".join(paper["tags"])))
            self.update_statistics()
            self.update_category_filter()
            self.update_tag_filter()

    def set_reminder(self):
        reminder_time = simpledialog.askstring("Set Reminder", "Enter reminder time (e.g., '2024-08-29 10:00')")
        if reminder_time:
            messagebox.showinfo("Reminder Set", f"Reminder set for {reminder_time}")

    def toggle_dark_mode(self):
        if not self.dark_mode:
            self.style.theme_use("clam")
            self.master.config(bg="black")
            self.add_paper_tab.config(bg="black")
            self.view_papers_tab.config(bg="black")
            self.statistics_tab.config(bg="black")
            self.stats_text.config(bg="black", fg="white")
            self.dark_mode = True
        else:
            self.style.theme_use("default")
            self.master.config(bg="SystemButtonFace")
            self.add_paper_tab.config(bg="SystemButtonFace")
            self.view_papers_tab.config(bg="SystemButtonFace")
            self.statistics_tab.config(bg="SystemButtonFace")
            self.stats_text.config(bg="SystemButtonFace", fg="black")
            self.dark_mode = False

    def auto_save(self):
        with open("autosave.json", "w") as f:
            json.dump(self.papers, f, indent=2)

    def auto_load(self):
        try:
            with open("autosave.json", "r") as f:
                self.papers = json.load(f)
                for paper in self.papers:
                    self.tree.insert("", tk.END, values=(paper["title"], paper["authors"], paper["year"], ", ".join(paper["tags"])))
                self.update_statistics()
                self.update_category_filter()
                self.update_tag_filter()
        except FileNotFoundError:
            pass

    # Missing Methods Implementation

    def backup_data(self):
        """Create a backup of the current data."""
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not file_path:
            return
        try:
            with open(file_path, "w") as f:
                json.dump(self.papers, f, indent=2)
            messagebox.showinfo("Success", "Backup created successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create backup: {str(e)}")

    def restore_data(self):
        """Restore data from a backup."""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not file_path:
            return
        try:
            with open(file_path, "r") as f:
                self.papers = json.load(f)
                self.tree.delete(*self.tree.get_children())
                for paper in self.papers:
                    self.tree.insert("", tk.END, values=(paper["title"], paper["authors"], paper["year"], ", ".join(paper["tags"])))
                self.update_statistics()
                self.update_category_filter()
                self.update_tag_filter()
                messagebox.showinfo("Success", "Data restored successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restore data: {str(e)}")

    def setup_advanced_search(self):
        """Setup and perform an advanced search."""
        search_window = tk.Toplevel(self.master)
        search_window.title("Advanced Search")
        search_window.geometry("400x300")

        # Add search fields
        tk.Label(search_window, text="Title:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        title_entry = tk.Entry(search_window, width=30)
        title_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(search_window, text="Authors:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        authors_entry = tk.Entry(search_window, width=30)
        authors_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(search_window, text="Year:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        year_entry = tk.Entry(search_window, width=10)
        year_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(search_window, text="Category:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        category_entry = tk.Entry(search_window, width=30)
        category_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(search_window, text="Tag:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        tag_entry = tk.Entry(search_window, width=30)
        tag_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Button(search_window, text="Search", command=lambda: self.perform_advanced_search(
            title_entry.get(), authors_entry.get(), year_entry.get(), category_entry.get(), tag_entry.get()
        )).grid(row=5, column=1, pady=10)

    def perform_advanced_search(self, title, authors, year, category, tag):
        """Perform advanced search with given parameters."""
        self.tree.delete(*self.tree.get_children())

        for paper in self.papers:
            if all([
                title.lower() in paper["title"].lower(),
                authors.lower() in paper["authors"].lower(),
                year in paper["year"],
                category.lower() in (', '.join(paper['categories'])).lower(),
                tag.lower() in (', '.join(paper['tags'])).lower()
            ]):
                self.tree.insert("", tk.END, values=(paper["title"], paper["authors"], paper["year"], ", ".join(paper["tags"])))

