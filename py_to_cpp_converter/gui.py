import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from py_ast_parser import Parser
from translator import translate_ast_to_cpp

# Convert Python to C++
def convert_code():
    python_code = input_text.get("1.0", tk.END)
    try:
        parser = Parser(python_code)
        ast = parser.parse()
        cpp_code = translate_ast_to_cpp(ast)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, cpp_code)
    except Exception as e:
        messagebox.showerror("Error", f"Parsing or translation failed:\n{e}")

# Clear both input and output
def clear_all():
    input_text.delete("1.0", tk.END)
    output_text.delete("1.0", tk.END)

# Save C++ code to file
def save_cpp_file():
    cpp_code = output_text.get("1.0", tk.END).strip()
    if not cpp_code:
        messagebox.showwarning("Warning", "No C++ code to save!")
        return
    file_path = filedialog.asksaveasfilename(
        defaultextension=".cpp",
        filetypes=[("C++ files", "*.cpp"), ("All files", "*.*")]
    )
    if file_path:
        with open(file_path, "w") as f:
            f.write(cpp_code)
        messagebox.showinfo("Saved", f"File saved at:\n{file_path}")

# GUI Setup
root = tk.Tk()
root.title("Python to C++ Converter")
root.geometry("900x700")
root.resizable(False, False)

# Input Section
input_label = tk.Label(root, text="Enter Python Code", font=("Arial", 12, "bold"))
input_label.pack()

input_text = scrolledtext.ScrolledText(root, height=15, width=100, font=("Consolas", 11))
input_text.pack(pady=5)

# Button Section
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

convert_button = tk.Button(button_frame, text="Convert to C++", width=20, command=convert_code)
convert_button.grid(row=0, column=0, padx=10)

clear_button = tk.Button(button_frame, text="Clear", width=20, command=clear_all)
clear_button.grid(row=0, column=1, padx=10)

save_button = tk.Button(button_frame, text="Save as .cpp", width=20, command=save_cpp_file)
save_button.grid(row=0, column=2, padx=10)

# Output Section
output_label = tk.Label(root, text="Converted C++ Code", font=("Arial", 12, "bold"))
output_label.pack()

output_text = scrolledtext.ScrolledText(root, height=15, width=100, font=("Consolas", 11))
output_text.pack(pady=5)

# Start GUI
root.mainloop()
