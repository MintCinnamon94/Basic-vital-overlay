import tkinter as tk
from pynvml import *
import psutil
from pynput import keyboard

class GPUStats():
    def __init__(self, *args, **kwargs):
        nvmlInit()
        self.handle = nvmlDeviceGetHandleByIndex(0) # Connects with NVIDIA gpu
        self.root = tk.Tk() # Initializes the GUI
        self.root.overrideredirect(True) # Tells linux to ignore the window NO TITLE, NO X, NO MINIMIZE

        self.label = tk.Label(self.root) # Allows text inside the HUD
        self.label.pack() # Tells the GUI how big the HUD needs to be

        self.label.bind("<Button-1>", self.start_move) # Event binder for left click
        self.label.bind("<B1-Motion>", self.do_move) # Listening for left click being held

        self.root.wait_visibility(self.root) # Waits for the gui to be created to prevent crashing
        self.root.attributes('-type', 'dock')
        self.root.attributes('-alpha', 0.45) # Creates transparent box for load values

        self.listener = keyboard.Listener(on_press=self.exit_program) # Toggle to exit
        self.listener.start()

        self.update_GPU_VRAM_TEMP() # Calls the function so load bar updates

    def exit_program(self, key):
        try:
            if key.char == '0':
               self.root.destroy()
        except AttributeError:
            pass

    def start_move(self, event): # Collects x and y values or current position and where you grabbed the HUD
        self.x = event.x
        self.y = event.y

    def do_move(self, event): # Determines how far you've moved since grabbing the HUD
        delta_x = event.x - self.x
        delta_y = event.y - self.y

        new_x = self.root.winfo_rootx() + delta_x # Tells script where you have moved the HUD and does it
        new_y = self.root.winfo_rooty() + delta_y
        self.root.geometry(f'+{new_x}+{new_y}')

    def gpu_data(self):
        res = nvmlDeviceGetUtilizationRates(self.handle) # Pulls GPU %
        mem = nvmlDeviceGetMemoryInfo(self.handle) # Pulls NVIDIA VRAM %
        temp = nvmlDeviceGetTemperature(self.handle, 0) # Pulls NVIDIA GPU temp
        cpu = psutil.cpu_percent(interval=None) # Pulls cpu %
        ram = psutil.virtual_memory().percent # Pulls ram %
        mem_percent = (mem.used / mem.total) * 100 # Multiples used memory and total memory to get a % "*100"
        return res.gpu, mem_percent, temp, cpu, ram # Returns results

    def update_GPU_VRAM_TEMP(self):
        try:
            gpu_load, mem_load, temp, cpu, ram = self.gpu_data() # Pulls results from return value of gpu_data function
            self.label.config(text=f'CPU: {cpu}% | Mem: {ram}% | GPU: {gpu_load:.0f}% | VRAM: {mem_load:.0f}% | GPU: {temp}°C') # Prints load values to GUI
        except:
            self.label.config(text="GPU Error")
        self.root.after(200, self.update_GPU_VRAM_TEMP) # If unable to get load values will print 'GPU ERROR'

    def start(self): # Keeps everything in a loop so it doesnt end after 1 check
        try:
            self.root.mainloop()
        finally:
            nvmlShutdown()

if __name__ == '__main__':
     GPUStats().start()
