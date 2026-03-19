import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import sys
import os

class NIST_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NIST Statistical Test Suite GUI - by erkangkang")
        self.root.geometry("800x680")
        
        # Author Info
        author_label = tk.Label(root, text="Author: erkangkang", font=("Arial", 10, "italic"), fg="gray")
        author_label.pack(side="bottom", pady=5)
        
        # Generator Selection
        self.gen_var = tk.StringVar(value="0")
        gen_frame = tk.LabelFrame(root, text="Generator Selection")
        gen_frame.pack(fill="x", padx=10, pady=5)
        
        generators = [
            ("0: Input File", "0"), ("1: Linear Congruential", "1"),
            ("2: Quadratic Congruential I", "2"), ("3: Quadratic Congruential II", "3"),
            ("4: Cubic Congruential", "4"), ("5: XOR", "5"),
            ("6: Modular Exponentiation", "6"), ("7: Blum-Blum-Shub", "7"),
            ("8: Micali-Schnorr", "8"), ("9: G Using SHA-1", "9")
        ]
        
        for i, (text, val) in enumerate(generators):
            r = ttk.Radiobutton(gen_frame, text=text, value=val, variable=self.gen_var, command=self.on_gen_change)
            r.grid(row=i//3, column=i%3, sticky="w", padx=5, pady=2)
            
        # File Selection
        self.file_frame = tk.Frame(root)
        self.file_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(self.file_frame, text="Input File:").pack(side="left")
        self.file_entry = tk.Entry(self.file_frame, width=50)
        self.file_entry.pack(side="left", padx=5)
        self.file_btn = tk.Button(self.file_frame, text="Browse...", command=self.browse_file)
        self.file_btn.pack(side="left")
        
        # General Settings
        settings_frame = tk.LabelFrame(root, text="General Settings")
        settings_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(settings_frame, text="Stream Length:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.stream_len = tk.Entry(settings_frame)
        self.stream_len.insert(0, "1000000")
        self.stream_len.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        tk.Label(settings_frame, text="Bitstreams Count:").grid(row=0, column=2, sticky="e", padx=5, pady=2)
        self.bitstreams = tk.Entry(settings_frame)
        self.bitstreams.insert(0, "1")
        self.bitstreams.grid(row=0, column=3, sticky="w", padx=5, pady=2)
        
        tk.Label(settings_frame, text="File Format:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.format_var = tk.StringVar(value="0")
        ttk.Radiobutton(settings_frame, text="ASCII", value="0", variable=self.format_var).grid(row=1, column=1, sticky="w", padx=5)
        ttk.Radiobutton(settings_frame, text="Binary", value="1", variable=self.format_var).grid(row=1, column=2, sticky="w", padx=5)
        
        # Tests Selection
        tests_frame = tk.LabelFrame(root, text="Statistical Tests")
        tests_frame.pack(fill="x", padx=10, pady=5)
        
        self.test_vars = []
        test_names = [
            "Frequency", "Block Frequency", "Cumulative Sums", "Runs", "Longest Run of Ones",
            "Rank", "Discrete Fourier Transform", "Nonperiodic Template Matchings",
            "Overlapping Template Matchings", "Universal Statistical", "Approximate Entropy",
            "Random Excursions", "Random Excursions Variant", "Serial", "Linear Complexity"
        ]
        for i, name in enumerate(test_names):
            var = tk.IntVar(value=1)
            self.test_vars.append(var)
            cb = ttk.Checkbutton(tests_frame, text=f"[{i+1:02d}] {name}", variable=var)
            cb.grid(row=i//3, column=i%3, sticky="w", padx=5, pady=2)
            
        # Parameter Adjustments
        params_frame = tk.LabelFrame(root, text="Parameter Adjustments")
        params_frame.pack(fill="x", padx=10, pady=5)
        
        self.param_vars = {}
        params_info = [
            (1, "Block Frequency - block length (M):", "128"),
            (2, "NonOverlapping Template - block length (m):", "9"),
            (3, "Overlapping Template - block length (m):", "9"),
            (4, "Approximate Entropy - block length (m):", "10"),
            (5, "Serial - block length (m):", "16"),
            (6, "Linear Complexity - block length (M):", "500")
        ]
        
        for i, (num, text, default) in enumerate(params_info):
            tk.Label(params_frame, text=text).grid(row=i//2, column=(i%2)*2, sticky="e", padx=5, pady=2)
            var = tk.StringVar(value=default)
            self.param_vars[num] = var
            tk.Entry(params_frame, textvariable=var, width=10).grid(row=i//2, column=(i%2)*2+1, sticky="w", padx=5, pady=2)
            
        # Run Button
        self.run_btn = tk.Button(root, text="Run Tests", command=self.run_tests, bg="green", fg="white", font=("Arial", 12, "bold"))
        self.run_btn.pack(pady=10)
        
        # Output Log
        self.log_text = tk.Text(root, height=10)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)
        
    def on_gen_change(self):
        if self.gen_var.get() == "0":
            self.file_entry.config(state="normal")
            self.file_btn.config(state="normal")
        else:
            self.file_entry.config(state="disabled")
            self.file_btn.config(state="disabled")
            
    def browse_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)
            
    def log(self, message):
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        
    def run_tests(self):
        length = self.stream_len.get()
        if not length.isdigit():
            messagebox.showerror("Error", "Stream length must be an integer.")
            return
            
        gen = self.gen_var.get()
        filepath = self.file_entry.get()
        if gen == "0" and not filepath:
            messagebox.showerror("Error", "Please select an input file.")
            return
            
        # Construct input sequence
        inputs = []
        inputs.append(gen)
        if gen == "0":
            inputs.append(filepath)
            
        # Tests to apply
        all_tests = all(v.get() == 1 for v in self.test_vars)
        if all_tests:
            inputs.append("1")
        else:
            inputs.append("0")
            test_str = "".join(str(v.get()) for v in self.test_vars)
            inputs.append(test_str)
            
        # Parameters (check if modified)
        defaults = {1: "128", 2: "9", 3: "9", 4: "10", 5: "16", 6: "500"}
        for num, var in self.param_vars.items():
            val = var.get()
            if val != defaults[num]:
                inputs.append(str(num))
                inputs.append(val)
        inputs.append("0") # 0 to continue
        
        inputs.append(self.bitstreams.get())
        inputs.append(self.format_var.get())
        
        input_str = "\n".join(inputs) + "\n"
        
        self.run_btn.config(state="disabled")
        self.log_text.delete(1.0, tk.END)
        self.log("Starting NIST Statistical Test Suite...\n")
        self.log(f"Command: assess.exe {length}\n")
        
        threading.Thread(target=self.execute_process, args=(length, input_str), daemon=True).start()
        
    def execute_process(self, length, input_str):
        # Determine base path for PyInstaller
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            # If frozen, we need to create the required directories in the current working directory
            cwd = os.path.dirname(sys.executable)
        else:
            base_path = os.path.abspath(os.path.dirname(__file__))
            cwd = base_path
            
        exe_path = os.path.join(base_path, "assess.exe")
        
        # NIST STS requires these specific folders to exist where it's executed
        experiments_dir = os.path.join(cwd, "experiments")
        algo_dir = os.path.join(experiments_dir, "AlgorithmTesting")
        if not os.path.exists(experiments_dir):
            os.makedirs(experiments_dir, exist_ok=True)
        if not os.path.exists(algo_dir):
            os.makedirs(algo_dir, exist_ok=True)
            
        # The tool also needs subdirectories for each test
        test_dirs = [
            "Frequency", "BlockFrequency", "CumulativeSums", "Runs", "LongestRun",
            "Rank", "FFT", "NonOverlappingTemplate", "OverlappingTemplate", "Universal",
            "ApproximateEntropy", "RandomExcursions", "RandomExcursionsVariant",
            "Serial", "LinearComplexity"
        ]
        for td in test_dirs:
            td_path = os.path.join(algo_dir, td)
            if not os.path.exists(td_path):
                os.makedirs(td_path, exist_ok=True)
                
        # Also we need to make sure the templates folder is available
        templates_dir = os.path.join(cwd, "templates")
        if not os.path.exists(templates_dir):
            import shutil
            bundled_templates = os.path.join(base_path, "templates")
            if os.path.exists(bundled_templates):
                shutil.copytree(bundled_templates, templates_dir)
            
        try:
            process = subprocess.Popen(
                [exe_path, length],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=cwd
            )
            
            # Write inputs
            process.stdin.write(input_str)
            process.stdin.flush()
            process.stdin.close()
            
            # Read output interactively
            for line in process.stdout:
                self.root.after(0, self.log, line)
                
            process.wait()
            self.root.after(0, self.log, f"\nProcess exited with code {process.returncode}\n")
            self.root.after(0, self.log, f"Results are saved in the '{os.path.join(cwd, 'experiments')}' folder.\n")
            
        except Exception as e:
            self.root.after(0, self.log, f"\nError: {str(e)}\n")
        finally:
            self.root.after(0, lambda: self.run_btn.config(state="normal"))

if __name__ == "__main__":
    root = tk.Tk()
    app = NIST_GUI(root)
    root.mainloop()