import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading

class CANApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CAN Interface")
        
        # Variables
        self.ip = tk.StringVar()
        self.port = tk.IntVar(value=1234)
        self.speed = tk.StringVar()
        self.filter_acr = tk.StringVar()
        self.filter_amr = tk.StringVar()
        self.can_id = tk.StringVar()
        self.dlc = tk.StringVar()
        self.data = tk.StringVar()
        self.log = tk.StringVar()
        self.extd = tk.BooleanVar()

        self.sock = None
        
        # Create widgets
        self.create_widgets()
        
    def create_widgets(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="ESP32 IP:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.ip).grid(row=0, column=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text="Port:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.port).grid(row=1, column=1, sticky=(tk.W, tk.E))

        ttk.Button(frame, text="Connect", command=self.connect).grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))

        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        ttk.Label(frame, text="Speed:").grid(row=4, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.speed).grid(row=4, column=1, sticky=(tk.W, tk.E))
        ttk.Button(frame, text="Set Speed", command=self.set_speed).grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))

        ttk.Label(frame, text="Filter ACR:").grid(row=6, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.filter_acr).grid(row=6, column=1, sticky=(tk.W, tk.E))
        ttk.Label(frame, text="Filter AMR:").grid(row=7, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.filter_amr).grid(row=7, column=1, sticky=(tk.W, tk.E))
        ttk.Button(frame, text="Set Filter", command=self.set_filter).grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E))

        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=9, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        ttk.Label(frame, text="CAN ID:").grid(row=10, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.can_id).grid(row=10, column=1, sticky=(tk.W, tk.E))
        ttk.Label(frame, text="DLC:").grid(row=11, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.dlc).grid(row=11, column=1, sticky=(tk.W, tk.E))
        ttk.Label(frame, text="Data:").grid(row=12, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.data).grid(row=12, column=1, sticky=(tk.W, tk.E))
        ttk.Checkbutton(frame, text="Extended ID", variable=self.extd).grid(row=13, column=0, columnspan=2, sticky=tk.W)
        ttk.Button(frame, text="Send CAN Frame", command=self.send_can_frame).grid(row=14, column=0, columnspan=2, sticky=(tk.W, tk.E))

        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=15, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        self.log_text = tk.Text(frame, height=10, width=50)
        self.log_text.grid(row=16, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.ip.get(), self.port.get()))
            self.log_message("Connected to ESP32")
            threading.Thread(target=self.receive_data).start()
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
        
    def set_speed(self):
        try:
            speed_command = f"AT+SPEED={self.speed.get()}\r\n"
            self.sock.sendall(speed_command.encode())
            self.log_message("Speed set to " + self.speed.get())
        except Exception as e:
            messagebox.showerror("Set Speed Error", str(e))
        
    def set_filter(self):
        try:
            filter_command = f"AT+FILTER={self.filter_acr.get()},{self.filter_amr.get()},1\r\n"
            self.sock.sendall(filter_command.encode())
            self.log_message("Filter set: ACR=" + self.filter_acr.get() + ", AMR=" + self.filter_amr.get())
        except Exception as e:
            messagebox.showerror("Set Filter Error", str(e))
        
    def send_can_frame(self):
        try:
            extd = 1 if self.extd.get() else 0
            send_command = f"AT+SEND={self.can_id.get()},{self.dlc.get()},{extd},{self.data.get()}\r\n"
            self.sock.sendall(send_command.encode())
            self.log_message("Sent CAN Frame: ID=" + self.can_id.get() + ", DLC=" + self.dlc.get() + ", Data=" + self.data.get())
        except Exception as e:
            messagebox.showerror("Send CAN Frame Error", str(e))
        
    def receive_data(self):
        try:
            while True:
                data = self.sock.recv(1024)
                if data:
                    self.log_message(data.decode())
        except Exception as e:
            self.log_message("Receive Error: " + str(e))
        
    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

def main():
    root = tk.Tk()
    app = CANApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
