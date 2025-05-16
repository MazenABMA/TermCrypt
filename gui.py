import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import subprocess
import threading
import os

class TermCryptApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TermCrypt")
        self.geometry("750x550")

        self.chat_proc = None
        self.chat_stop = False
        self.receiver_process = None

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        # Create chat tab
        self.chat_tab = ttk.Frame(notebook)
        notebook.add(self.chat_tab, text="Chat Client")

        # Create file tab
        self.file_tab = ttk.Frame(notebook)
        notebook.add(self.file_tab, text="File Transfer")

        self.create_chat_tab()
        self.create_file_tab()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ========== CHAT TAB ==========
    def create_chat_tab(self):
        tk.Label(self.chat_tab, text="Server IP:").grid(row=0, column=0, sticky="e")
        self.chat_ip = tk.Entry(self.chat_tab)
        self.chat_ip.insert(0, "127.0.0.1")
        self.chat_ip.grid(row=0, column=1, sticky="w")

        tk.Label(self.chat_tab, text="Port:").grid(row=1, column=0, sticky="e")
        self.chat_port = tk.Entry(self.chat_tab)
        self.chat_port.insert(0, "4443")
        self.chat_port.grid(row=1, column=1, sticky="w")

        self.chat_output = scrolledtext.ScrolledText(self.chat_tab, state='disabled', height=20)
        self.chat_output.grid(row=2, column=0, columnspan=3, sticky="nsew")

        self.chat_input = tk.Entry(self.chat_tab, width=60)
        self.chat_input.grid(row=3, column=0, columnspan=2, sticky="w")
        self.chat_input.bind("<Return>", self.send_chat)

        tk.Button(self.chat_tab, text="Send", command=self.send_chat).grid(row=3, column=2, sticky="w")
        tk.Button(self.chat_tab, text="Connect", command=self.start_chat_client).grid(row=4, column=1, sticky="w")
        tk.Button(self.chat_tab, text="Disconnect", command=self.disconnect_chat_client).grid(row=4, column=2, sticky="w")

        self.chat_tab.grid_rowconfigure(2, weight=1)
        self.chat_tab.grid_columnconfigure(1, weight=1)

    def chat_append_output(self, text):
        self.chat_output.configure(state='normal')
        self.chat_output.insert(tk.END, text + "\n")
        self.chat_output.see(tk.END)
        self.chat_output.configure(state='disabled')

    def start_chat_client(self):
        if self.chat_proc is not None:
            messagebox.showinfo("Info", "Already connected.")
            return

        ip = self.chat_ip.get()
        port = self.chat_port.get()
        if not ip:
            messagebox.showerror("Error", "Please enter server IP.")
            return

        cmd = ["bash", "./chat_client.sh", ip, port]
        self.chat_proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        self.chat_stop = False
        threading.Thread(target=self.read_chat_output, daemon=True).start()
        self.chat_append_output(f"[*] Connecting to {ip}:{port} ...")

    def read_chat_output(self):
        try:
            while not self.chat_stop:
                line = self.chat_proc.stdout.readline()
                if line == '' and self.chat_proc.poll() is not None:
                    break
                if line:
                    self.chat_append_output(line.rstrip())
        except Exception as e:
            self.chat_append_output(f"[!] Error: {e}")

        self.chat_append_output("[*] Disconnected.")
        self.chat_proc = None

    def send_chat(self, event=None):
        if self.chat_proc is None:
            messagebox.showerror("Error", "Not connected.")
            return

        msg = self.chat_input.get().strip()
        if not msg:
            return

        try:
            self.chat_proc.stdin.write(msg + "\n")
            self.chat_proc.stdin.flush()
            self.chat_append_output(f"[You] {msg}")
            self.chat_input.delete(0, tk.END)
        except Exception as e:
            self.chat_append_output(f"[!] Error sending message: {e}")

    def disconnect_chat_client(self):
        if self.chat_proc is None:
            messagebox.showinfo("Info", "Not connected.")
            return

        try:
            self.chat_stop = True
            self.chat_proc.stdin.write("/exit\n")
            self.chat_proc.stdin.flush()
            self.chat_proc.terminate()
        except Exception:
            pass
        self.chat_proc = None
        self.chat_append_output("[*] Disconnected.")

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
        if self.chat_proc:
            self.disconnect_chat_client()
        if self.receiver_process:
            self.receiver_process.terminate()
        self.destroy()

if __name__ == "__main__":
    app = TermCryptApp()
    app.mainloop()
