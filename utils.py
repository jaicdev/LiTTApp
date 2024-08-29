from tkinter import messagebox, filedialog

def export_to_latex(papers):
    if not papers:
        messagebox.showerror("Error", "No papers to export!")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".tex", filetypes=[("LaTeX files", "*.tex")])
    if not file_path:
        return

    try:
        with open(file_path, "w") as f:
            f.write("\\documentclass{article}\n\\begin{document}\n\\title{Literature Review}\n\\maketitle\n")
            for paper in papers:
                f.write(f"\\section*{{{paper['title']}}}\n")
                f.write(f"\\textbf{{Authors:}} {paper['authors']} \\\\ \n")
                f.write(f"\\textbf{{Year:}} {paper['year']} \\\\ \n")
                f.write(f"\\textbf{{DOI:}} {paper['doi']} \\\\ \n")
                f.write(f"\\textbf{{Categories:}} {', '.join(paper['categories'])} \\\\ \n")
                f.write(f"\\textbf{{Tags:}} {', '.join(paper['tags'])} \\\\ \n")
                f.write(f"\\textbf{{Summary:}} \n{paper['summary']} \\\\ \n")
                f.write(f"\\textbf{{Notes:}} \n{paper['notes']} \\\\ \n")
            f.write("\\end{document}")
        messagebox.showinfo("Success", f"Papers exported to {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export papers: {str(e)}")

