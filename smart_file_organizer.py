import os
import shutil
import pandas as pd
from datetime import datetime
from collections import Counter
import customtkinter as ctk
from tkinter import filedialog, messagebox

# ============ CONFIG ============ #
CATEGORY_MAP = {
    'pdf': 'Documents', 'docx': 'Documents', 'txt': 'Documents', 'csv': 'Documents',
    'jpg': 'Images', 'jpeg': 'Images', 'png': 'Images', 'gif': 'Images',
    'mp4': 'Videos', 'mkv': 'Videos', 'mov': 'Videos',
    'zip': 'Archives', 'rar': 'Archives', '7z': 'Archives', 'tar': 'Archives',
    'py': 'Code', 'cpp': 'Code', 'java': 'Code', 'js': 'Code', 'html': 'Code', 'css': 'Code'
}


# ============ CORE FUNCTIONS ============ #
def get_category(file_name):
    _, ext = os.path.splitext(file_name)
    return CATEGORY_MAP.get(ext[1:].lower(), "Others")


def organize_files(src_folder, dest_folder, dry_run=True):
    os.makedirs(dest_folder, exist_ok=True)
    for cat in set(CATEGORY_MAP.values()):
        os.makedirs(os.path.join(dest_folder, cat), exist_ok=True)
    os.makedirs(os.path.join(dest_folder, "Others"), exist_ok=True)

    records = []
    for file_name in os.listdir(src_folder):
        file_path = os.path.join(src_folder, file_name)
        if not os.path.isfile(file_path):
            continue

        category = get_category(file_name)
        dest_cat_folder = os.path.join(dest_folder, category)
        dest_path = os.path.join(dest_cat_folder, file_name)

        # Handle duplicates
        name, ext = os.path.splitext(file_name)
        counter = 1
        while os.path.exists(dest_path):
            dest_path = os.path.join(dest_cat_folder, f"{name}({counter}){ext}")
            counter += 1

        size_kb = round(os.path.getsize(file_path) / 1024, 2)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not dry_run:
            shutil.move(file_path, dest_path)
            action = "Moved"
        else:
            action = "Preview"

        records.append({
            "File Name": file_name,
            "Old Path": file_path,
            "New Path": dest_path,
            "Category": category,
            "Size (KB)": size_kb,
            "Date": timestamp,
            "Action": action
        })
    return records


def save_report(records, dest_folder):
    if not records:
        return None
    df = pd.DataFrame(records)
    report_path = os.path.join(dest_folder, "organizer_report.csv")
    df.to_csv(report_path, index=False)
    return report_path


def get_summary(records):
    summary = Counter([r["Category"] for r in records if r["Action"] == "Moved"])
    return "\n".join([f"{cat}: {count} files" for cat, count in summary.items()]) or "No files moved."


# ============ GUI ============ #
class SmartFileOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Smart File Organizer + CSV Report")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Variables
        self.src_folder = ctk.StringVar()
        self.dest_folder = ctk.StringVar()
        self.dry_run = ctk.BooleanVar(value=True)

        # Layout
        self.create_widgets()

    def create_widgets(self):
        title = ctk.CTkLabel(self, text="📁 Smart File Organizer", font=("Helvetica", 24, "bold"))
        title.pack(pady=20)

        src_frame = ctk.CTkFrame(self)
        src_frame.pack(pady=10)
        ctk.CTkLabel(src_frame, text="Source Folder:").pack(side="left", padx=10)
        ctk.CTkEntry(src_frame, textvariable=self.src_folder, width=400).pack(side="left")
        ctk.CTkButton(src_frame, text="Browse", command=self.browse_src).pack(side="left", padx=5)

        dest_frame = ctk.CTkFrame(self)
        dest_frame.pack(pady=10)
        ctk.CTkLabel(dest_frame, text="Destination Folder:").pack(side="left", padx=10)
        ctk.CTkEntry(dest_frame, textvariable=self.dest_folder, width=400).pack(side="left")
        ctk.CTkButton(dest_frame, text="Browse", command=self.browse_dest).pack(side="left", padx=5)

        ctk.CTkCheckBox(self, text="Dry Run (Preview Only)", variable=self.dry_run).pack(pady=10)

        ctk.CTkButton(self, text="Organize Files", command=self.run_organizer, width=200, height=40).pack(pady=20)

        self.output_box = ctk.CTkTextbox(self, width=700, height=300, corner_radius=10)
        self.output_box.pack(pady=10)

    def browse_src(self):
        folder = filedialog.askdirectory()
        if folder:
            self.src_folder.set(folder)

    def browse_dest(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dest_folder.set(folder)

    def run_organizer(self):
        src = self.src_folder.get()
        dest = self.dest_folder.get()
        dry = self.dry_run.get()

        if not src:
            messagebox.showerror("Error", "Please select a source folder.")
            return

        # ✅ If no destination selected, auto-create one inside source folder
        if not dest:
            dest = os.path.join(src, "Organized Files")
            os.makedirs(dest, exist_ok=True)
            self.dest_folder.set(dest)

        self.output_box.delete("1.0", "end")
        self.output_box.insert("end", "Processing...\n")

        records = organize_files(src, dest, dry_run=dry)
        report_path = save_report(records, dest)
        summary = get_summary(records)

        for r in records:
            self.output_box.insert("end", f"{r['Action']}: {r['File Name']} -> {r['Category']}\n")

        self.output_box.insert("end", "\n--- Summary ---\n" + summary + "\n")

        if report_path:
            self.output_box.insert("end", f"\nReport saved at:\n{report_path}\n")

        messagebox.showinfo("Done", "Operation completed successfully!")


# ============ RUN APP ============ #
if __name__ == "__main__":
    app = SmartFileOrganizerApp()
    app.mainloop()
