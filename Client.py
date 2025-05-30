import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading

class TermCryptApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TermCrypt")
        self.geometry("750x550")

        self.chat_proc = None
        self.chat_stop = False
        self.server_proc = None  # For multi.py server

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        # Create chat tab
        self.chat_tab = ttk.Frame(notebook)
        notebook.add(self.chat_tab, text="Chat Client")

        self.create_chat_tab()

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

        self.use_multi_server = tk.BooleanVar(value=False)
        multi_checkbox = tk.Checkbutton(self.chat_tab, text="Use Multi-client Server (multi.py)", variable=self.use_multi_server)
        multi_checkbox.grid(row=2, column=0, columnspan=3, sticky='w', pady=(5,10))

        self.chat_output = scrolledtext.ScrolledText(self.chat_tab, state='disabled', height=20)
        self.chat_output.grid(row=3, column=0, columnspan=3, sticky="nsew")

        self.chat_input = tk.Entry(self.chat_tab, width=60)
        self.chat_input.grid(row=4, column=0, columnspan=2, sticky="w")
        self.chat_input.bind("<Return>", self.send_chat)

        tk.Button(self.chat_tab, text="Send", command=self.send_chat).grid(row=4, column=2, sticky="w")
        tk.Button(self.chat_tab, text="Connect", command=self.start_chat_client).grid(row=5, column=1, sticky="w")
        tk.Button(self.chat_tab, text="Disconnect", command=self.disconnect_chat_client).grid(row=5, column=2, sticky="w")

        tk.Button(self.chat_tab, text="Start Multi-server", command=self.start_multi_server).grid(row=6, column=0, sticky='w', pady=(10,0))
        tk.Button(self.chat_tab, text="Stop Multi-server", command=self.stop_multi_server).grid(row=6, column=1, sticky='w', pady=(10,0))

        self.chat_tab.grid_rowconfigure(3, weight=1)
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

    def start_multi_server(self):
        if self.server_proc is not None:
            messagebox.showinfo("Info", "Multi-client server already running.")
            return

        cmd = ["python3", "multi.py"]
        try:
            self.server_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            threading.Thread(target=self.read_server_output, daemon=True).start()
            self.chat_append_output("[*] Multi-client server started.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start multi-client server:\n{e}")

    def read_server_output(self):
        try:
            while self.server_proc and self.server_proc.poll() is None:
                line = self.server_proc.stdout.readline()
                if line:
                    self.chat_append_output(f"[Server] {line.strip()}")
        except Exception as e:
            self.chat_append_output(f"[Server] Error reading output: {e}")

    def stop_multi_server(self):
        if self.server_proc:
            self.server_proc.terminate()
            self.server_proc = None
            self.chat_append_output("[*] Multi-client server stopped.")
        else:
            messagebox.showinfo("Info", "Multi-client server is not running.")

    def on_closing(self):
        self.disconnect_chat_client()
        self.stop_multi_server()
        self.destroy()

if __name__ == "__main__":
    app = TermCryptApp()
    app.mainloop()
