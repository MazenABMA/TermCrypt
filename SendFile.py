import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import subprocess
import threading

class TermCryptApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TermCrypt - File Transfer")
        self.geometry("700x500")

        self.receiver_process = None

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        # File Transfer Tab
        self.file_tab = ttk.Frame(notebook)
        notebook.add(self.file_tab, text="File Transfer")

        self.create_file_tab()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ========== FILE TAB ==========
    def create_file_tab(self):
        tk.Label(self.file_tab, text="Server IP:").grid(row=0, column=0, sticky="e")
        self.file_ip = tk.Entry(self.file_tab)
        self.file_ip.insert(0, "127.0.0.1")
        self.file_ip.grid(row=0, column=1, sticky="w")

        tk.Label(self.file_tab, text="Port:").grid(row=1, column=0, sticky="e")
        self.file_port = tk.Entry(self.file_tab)
        self.file_port.insert(0, "5555")
        self.file_port.grid(row=1, column=1, sticky="w")

        tk.Label(self.file_tab, text="Password:").grid(row=2, column=0, sticky="e")
        self.file_password = tk.Entry(self.file_tab, show="*")
        self.file_password.grid(row=2, column=1, sticky="w")

        tk.Label(self.file_tab, text="File:").grid(row=3, column=0, sticky="e")
        self.file_path_var = tk.StringVar()
        self.file_entry = tk.Entry(self.file_tab, textvariable=self.file_path_var, width=40)
        self.file_entry.grid(row=3, column=1, sticky="w")
        tk.Button(self.file_tab, text="Browse", command=self.browse_file).grid(row=3, column=2)

        tk.Button(self.file_tab, text="Send File", command=self.send_file).grid(row=4, column=1, sticky="w")
        tk.Button(self.file_tab, text="Start Receiver", command=self.start_receiver).grid(row=4, column=2, sticky="w")
        self.finish_button = tk.Button(self.file_tab, text="Finish", command=self.stop_receiver, state='disabled')
        self.finish_button.grid(row=4, column=3, sticky="w")

        self.file_output = scrolledtext.ScrolledText(self.file_tab, state='disabled', height=15)
        self.file_output.grid(row=5, column=0, columnspan=4, sticky="nsew")

        self.file_tab.grid_rowconfigure(5, weight=1)
        self.file_tab.grid_columnconfigure(1, weight=1)

    def browse_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.file_path_var.set(filename)

    def file_append_output(self, text):
        self.file_output.configure(state='normal')
        self.file_output.insert(tk.END, text + "\n")
        self.file_output.see(tk.END)
        self.file_output.configure(state='disabled')

    def send_file(self):
        ip = self.file_ip.get()
        port = self.file_port.get()
        password = self.file_password.get()
        file_path = self.file_path_var.get()

        if not ip or not password or not file_path:
            messagebox.showerror("Error", "Please fill all fields.")
            return

        cmd = ["./file_send.sh", ip, port, file_path, password]

        def run_send():
            self.file_append_output(f"[*] Sending {file_path} to {ip}:{port} ...")
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                self.file_append_output(line.strip())
            proc.wait()
            self.file_append_output("[*] Send finished.")

        threading.Thread(target=run_send, daemon=True).start()

    def start_receiver(self):
        port = self.file_port.get()
        password = self.file_password.get()

        if not password:
            messagebox.showerror("Error", "Enter password.")
            return

        if self.receiver_process:
            messagebox.showinfo("Info", "Receiver already running.")
            return

        cmd = ["./file_recv.sh", port, password]

        def run_receiver():
            self.file_append_output(f"[*] Starting receiver on port {port} ...")
            self.receiver_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            self.finish_button.config(state='normal')
            for line in self.receiver_process.stdout:
                self.file_append_output(line.strip())
            self.file_append_output("[*] Receiver stopped.")
            self.receiver_process = None
            self.finish_button.config(state='disabled')

        threading.Thread(target=run_receiver, daemon=True).start()

    def stop_receiver(self):
        if self.receiver_process:
            self.file_append_output("[*] Finishing receiver ...")
            self.receiver_process.terminate()
            self.finish_button.config(state='disabled')
        else:
            messagebox.showinfo("Info", "Receiver is not running.")

    def on_closing(self):
        if self.receiver_process:
            try:
                self.receiver_process.terminate()
            except:
                pass
        self.destroy()


if __name__ == "__main__":
    app = TermCryptApp()
    app.mainloop()
