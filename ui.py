import tkinter as tk
from tkinter import ttk, simpledialog
import time
import math
import random


class ModernDialog(tk.Toplevel):
    """A modern styled dialog with optional input field"""
    def __init__(self, parent, title="Input", message="", icon="ℹ️", is_input=False, input_type="text"):
        super().__init__(parent)
        self.title(title)
        self.configure(bg="#f0f0f0")
        self.resizable(False, False)
        
        # Set window properties
        window_width = 400
        window_height = 200 if is_input else 180
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.transient(parent)
        self.grab_set()
        
        # Add some padding
        content_frame = tk.Frame(self, bg="#f0f0f0", padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header with icon
        header_frame = tk.Frame(content_frame, bg="#f0f0f0")
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        icon_label = tk.Label(header_frame, text=icon, font=("Arial", 24), bg="#f0f0f0")
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        msg_label = tk.Label(header_frame, text=title, font=("Arial", 14, "bold"), 
                            bg="#f0f0f0", anchor="w")
        msg_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Message text
        message_label = tk.Label(content_frame, text=message, 
                               font=("Arial", 11),
                               bg="#f0f0f0", justify=tk.LEFT)
        message_label.pack(fill=tk.X, pady=(0, 15))
        
        self.result = None
        
        # Add input field if requested
        if is_input:
            input_frame = tk.Frame(content_frame, bg="#f0f0f0")
            input_frame.pack(fill=tk.X, pady=(0, 15))
            
            self.entry_var = tk.StringVar()
            
            if input_type == "number":
                vcmd = (self.register(self.validate_number), '%P')
                self.entry = tk.Entry(input_frame, textvariable=self.entry_var, 
                                    font=("Arial", 11), width=30,
                                    validate="key", validatecommand=vcmd)
            else:
                self.entry = tk.Entry(input_frame, textvariable=self.entry_var, 
                                    font=("Arial", 11), width=30)
                
            self.entry.pack(fill=tk.X)
            self.entry.focus_set()
        
        # Button frame at the bottom
        button_frame = tk.Frame(content_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Cancel button
        cancel_btn = tk.Button(button_frame, text="Cancel", 
                              command=self.cancel,
                              bg="#f2f2f2", fg="#333",
                              font=("Arial", 10),
                              padx=10, pady=5,
                              relief=tk.RAISED, bd=1)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # OK button
        ok_btn = tk.Button(button_frame, text="OK", 
                          command=self.ok,
                          bg="#4a86e8", fg="white",
                          font=("Arial", 10, "bold"),
                          padx=15, pady=5,
                          relief=tk.RAISED, bd=1)
        ok_btn.pack(side=tk.RIGHT, padx=5)
        
        # Set up key bindings
        self.bind("<Return>", lambda event: self.ok())
        self.bind("<Escape>", lambda event: self.cancel())
        
        # Wait for the window to be destroyed
        self.wait_window()
    
    def validate_number(self, value):
        if value == "":
            return True
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    def ok(self):
        if hasattr(self, 'entry_var'):
            self.result = self.entry_var.get()
        self.destroy()
    
    def cancel(self):
        self.result = None
        self.destroy()


class CustomDialog(simpledialog.Dialog):
    """Custom dialog for validating move sequences with improved styling"""
    def __init__(self, parent, prompt, validator_func, title="Input"):
        self.prompt = prompt
        self.entry_value = tk.StringVar()
        self.validator_func = validator_func
        self.result = None
        
        # Configure dialog appearance
        parent.option_add('*Dialog.msg.font', 'Arial 11')
        parent.option_add('*Dialog.msg.background', '#f5f5f7')
        
        super().__init__(parent, title)
        
    def body(self, master):
        # Set dialog background color
        self.configure(bg="#f5f5f7")
        for child in master.winfo_children():
            child.configure(bg="#f5f5f7")
        
        # Add prompt label with improved styling
        prompt_label = ttk.Label(master, text=self.prompt, style='TLabel',
                                background="#f5f5f7", wraplength=400, 
                                font=("Arial", 11))
        prompt_label.grid(row=0, pady=10, padx=10, sticky="w")
        
        # Style the entry field
        entry_frame = ttk.Frame(master, style='TFrame')
        entry_frame.grid(row=1, pady=5, padx=10, sticky="ew")
        
        entry = ttk.Entry(entry_frame, width=50, textvariable=self.entry_value)
        entry.pack(fill="x", padx=0, pady=0)
        entry.focus_set()
        
        # Add a descriptive example label
        example_label = ttk.Label(master, text="Example: A->C,A->B,C->B", 
                                 foreground="#666", background="#f5f5f7",
                                 font=("Arial", 9, "italic"))
        example_label.grid(row=2, pady=(0, 10), padx=10, sticky="w")
        
        # Error message area with improved styling
        error_frame = ttk.Frame(master, style='TFrame')
        error_frame.grid(row=3, sticky="ew", padx=10)
        
        self.error_label = ttk.Label(error_frame, text="", foreground="#e63946",
                                    background="#f5f5f7", font=("Arial", 10))
        self.error_label.pack(fill="x", pady=5)
        
        return entry
    
    def buttonbox(self):
        # Override the default button box for custom styling
        box = ttk.Frame(self)
        box.pack(fill="x", pady=10, padx=10)
        
        w = ttk.Button(box, text="OK", width=10, command=self.ok, default="active",
                      style='TButton')
        w.pack(side="right", padx=5, pady=5)
        
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel,
                      style='TButton')
        w.pack(side="right", padx=5, pady=5)
        
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
    
    def validate(self):
        value = self.entry_value.get().strip()
        validation_result = self.validator_func(value)
        
        if validation_result is True:
            self.result = value
            return True
        elif validation_result is False or validation_result is None:
            self.error_label.config(text="Invalid input format")
            return False
        else:
            # ValidationResult contains error message
            self.error_label.config(text=validation_result)
            return False


class HanoiCanvas:
    """Enhanced canvas for Tower of Hanoi game visualization"""
    def __init__(self, root, peg_click_callback):
        self.root = root
        self.frame = ttk.Frame(root)
        self.frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.frame, width=800, height=400, bg="#f0f4f8")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.pegs = {}   # Dictionary to store peg positions
        self.disks = {}  # Dictionary to store disk widgets
        self.highlighted_peg = None
        self.peg_click_callback = peg_click_callback
        self.canvas.bind("<Button-1>", self.on_click)
        
        # Animation properties
        self.animation_id = None
        self.animation_callback = None
        
        # Disk shadow and reflection effects
        self.use_effects = True
        
        # Victory effects
        self.particles = []

    def highlight_peg(self, peg_name):
        """Highlight the selected peg"""
        if peg_name in self.pegs:
            self.canvas.itemconfig(f"peg_{peg_name}", fill="#ffb700")  # Yellow color
            self.highlighted_peg = peg_name


    def draw(self, peg_state):
        """Draw the current state of the game"""
        self.canvas.delete("all")
        num_pegs = len(peg_state)
        
        # Background gradients and decorations
        self.draw_background_gradient()

        peg_width = 12
        peg_height = 200
        base_y = 350
        base_width = 120
        spacing = 800 // (num_pegs + 1)

        self.pegs = {}

        for idx, peg_name in enumerate(sorted(peg_state.keys())):
            x = spacing * (idx + 1)
            self.pegs[peg_name] = (x, base_y)
            
            # Draw peg base with shadow
            self.draw_base(x, base_y, base_width)
            
            # Draw peg
            self.canvas.create_rectangle(
                x - peg_width // 2, base_y - peg_height,
                x + peg_width // 2, base_y,
                fill="#999",
                outline="#888",
                tags=(f"peg_{peg_name}",)
            )
            
            # Draw disks on the peg (bottom to top)
            for level, disk_size in enumerate(peg_state[peg_name]):
                disk_width = 20 + disk_size * 12
                disk_height = 20
                y = base_y - disk_height * (level + 1)
                
                # Draw disk with optional effects
                self.draw_disk(x, y, disk_width, disk_height, disk_size)

            # Draw peg label with better styling
            self.canvas.create_rectangle(
                x - 30, base_y + 15,
                x + 30, base_y + 35,
                fill="#4a86e8", outline="#3a76d8",
                width=1, stipple='gray50'
            )
            self.canvas.create_text(
                x, base_y + 25, 
                text=f"Peg {peg_name}", 
                font=("Arial", 10, "bold"), 
                fill="white"
            )
        
        # Restore highlight if needed
        if self.highlighted_peg in self.pegs:
            self.highlight_peg(self.highlighted_peg)
    
    def draw_background_gradient(self):
        """Draw a gradient background"""
        width = self.canvas.winfo_width() or 800
        height = self.canvas.winfo_height() or 400
        
        # Create a subtle gradient background
        for i in range(height):
            # Calculate gradient color from top to bottom
            r = int(240 - i * 20 / height)
            g = int(244 - i * 20 / height)
            b = int(248 - i * 15 / height)
            color = f"#{r:02x}{g:02x}{b:02x}"
            
            self.canvas.create_line(0, i, width, i, fill=color, width=1)
        
        # Add some decorative elements
        for _ in range(10):
            x = random.randint(0, width)
            y = random.randint(0, height // 2)
            size = random.randint(2, 5)
            self.canvas.create_oval(
                x, y, x + size, y + size,
                fill="#e1e5eb", outline="",
                tags="decoration"
            )
    
    def draw_base(self, x, base_y, base_width):
        """Draw a peg base with shadow effect"""
        # Draw shadow
        self.canvas.create_rectangle(
            x - base_width // 2 + 5, base_y + 3,
            x + base_width // 2 + 5, base_y + 13,
            fill="#666", outline=""
        )
        
        # Draw base with 3D effect
        self.canvas.create_rectangle(
            x - base_width // 2, base_y,
            x + base_width // 2, base_y + 10,
            fill="#888", outline="#777"
        )
        
        # Add highlight to create 3D look
        self.canvas.create_line(
            x - base_width // 2, base_y,
            x + base_width // 2, base_y,
            fill="#aaa", width=1
        )
        
    def get_disk_color(self, size):
        """Return a color for a disk based on its size"""
        # Modern, vibrant color scheme
        colors = [
            "#ff595e", "#ffca3a", "#8ac926", "#1982c4", "#6a4c93",
            "#f8961e", "#43aa8b", "#4d908e", "#577590", "#f94144",
            "#bc6c25", "#f9844a", "#9d4edd", "#3a0ca3", "#2a9d8f"
    ]
        return colors[(size - 1) % len(colors)]
    
    
    
    def draw_disk(self, x, y, width, height, size):
        """Draw a disk with optional shadow and reflection effects"""
        color = self.get_disk_color(size)

        # Create disk shadow
        if self.use_effects:
            shadow_offset = 3
            self.canvas.create_rectangle(
                x - width // 2 + shadow_offset, y + shadow_offset,
                x + width // 2 + shadow_offset, y + height + shadow_offset,
                fill="#000000",  # Fixed: Removed alpha transparency
                outline="",
                tags=(f"disk_{size}_shadow", "disk_shadow")
        )

        # Create main disk
        self.canvas.create_rectangle(
            x - width // 2, y,
            x + width // 2, y + height,
            fill=color,
            outline="#000000",
            width=1,
            tags=(f"disk_{size}", "disk")
    )

        # Add reflection effect
        if self.use_effects:
            self.canvas.create_rectangle(
                x - width // 2 + 2, y + 2,
                x + width // 2 - 2, y + height // 3,
                fill="#ffffff",  # Fixed: Removed alpha transparency
                outline="",
                tags=(f"disk_{size}_reflection", "disk_reflection")
        )

            # Add disk size number
            self.canvas.create_text(
                x, y + height//2,
                text=str(size),
                font=("Arial", 8, "bold"),
                fill="#000000",
                tags=(f"disk_{size}_text", "disk_text")
        )

    def on_click(self, event):
        """Handle mouse click on the canvas"""
        for peg_name, (x, y) in self.pegs.items():
            if abs(event.x - x) < 60:
                self.peg_click_callback(peg_name)
                break

    def pulse_highlight(self, x, y, step):
        """Create a pulsing animation for the highlighted peg"""
        if self.highlighted_peg:
            # Delete previous pulse
            self.canvas.delete("pulse")

            # Calculate pulse size based on step
            size = 5 + 3 * math.sin(step / 5)

            # Draw pulsing circle
            self.canvas.create_oval(
                x - size, y - 100,
                x + size, y - 100 + size*2,
                fill="#ffb700",  # Fixed: Removed alpha transparency
                outline="",
                tags="pulse"
        )

            # Continue animation
            self.root.after(100, lambda: self.pulse_highlight(x, y, step + 1))

    
    def unhighlight_peg(self, peg_name):
        """Remove highlight from a peg"""
        if peg_name in self.pegs:
            self.canvas.itemconfig(f"peg_{peg_name}", fill="#999")  # Reset color
            self.canvas.delete("highlight")
            self.canvas.delete("pulse")
            self.highlighted_peg = None
    
    def animate_disk_move(self, from_peg, to_peg, disk_size, callback=None):
        """Animate a disk moving from one peg to another"""
        if from_peg not in self.pegs or to_peg not in self.pegs:
            if callback:
                callback()
            return
        
        # Get peg positions
        start_x, start_y = self.pegs[from_peg]
        end_x, end_y = self.pegs[to_peg]
        
        # Calculate disk position at the top of source peg
        for items in self.canvas.find_withtag(f"disk_{disk_size}"):
            self.canvas.delete(items)
        for items in self.canvas.find_withtag(f"disk_{disk_size}_shadow"):
            self.canvas.delete(items)
        for items in self.canvas.find_withtag(f"disk_{disk_size}_reflection"):
            self.canvas.delete(items)
        for items in self.canvas.find_withtag(f"disk_{disk_size}_text"):
            self.canvas.delete(items)
        
        # Get disk height
        disk_height = 20
        
        # Get number of disks on source and target pegs
        source_disks = len([tag for tag in self.canvas.gettags("disk") if f"disk_{disk_size}" in tag])
        target_disks = len([tag for tag in self.canvas.gettags("disk") if f"disk_{disk_size}" in tag and f"peg_{to_peg}" in tag])
        
        # Calculate start and end positions
        start_y = start_y - (source_disks + 1) * disk_height
        end_y = end_y - (target_disks) * disk_height
        
        # Animation parameters
        steps = 30
        height_offset = -100  # How high the disk goes during animation
        
        # Store callback for when animation completes
        self.animation_callback = callback
        
        # Start animation
        self.animate_disk_step(disk_size, start_x, start_y, end_x, end_y, height_offset, 0, steps)
    
    def animate_disk_step(self, disk_size, start_x, start_y, end_x, end_y, height_offset, step, total_steps):
        """Execute one step of the disk animation"""
        # Calculate current position
        progress = step / total_steps
        
        # Parabolic path for vertical movement (up then down)
        if progress < 0.5:
            # Going up
            vertical_progress = progress * 2  # Scale to 0-1 range
            y = start_y - height_offset * math.sin(vertical_progress * math.pi / 2)
        else:
            # Going down
            vertical_progress = (progress - 0.5) * 2  # Scale to 0-1 range
            y = (start_y - height_offset) + (end_y - (start_y - height_offset)) * math.sin(vertical_progress * math.pi / 2)
        
        # Linear interpolation for horizontal movement
        x = start_x + (end_x - start_x) * progress
        
        # Draw disk at current position
        disk_width = 20 + disk_size * 12
        disk_height = 20
        
        # Clear previous frame
        self.canvas.delete(f"animating_disk")
        
        # Draw animated disk
        self.canvas.create_rectangle(
            x - disk_width // 2, y,
            x + disk_width // 2, y + disk_height,
            fill=self.get_disk_color(disk_size),
            outline="#00000000",
            width=1,
            tags=f"animating_disk"
        )
        
        # Add reflection effect
        if self.use_effects:
            self.canvas.create_rectangle(
                x - disk_width // 2 + 2, y + 2,
                x + disk_width // 2 - 2, y + height_offset // 3,
                fill="#ffffffff", outline="", tags=f"animating_disk"
            )
            
            # Add disk size number
            self.canvas.create_text(
                x, y + disk_height//2,
                text=str(disk_size),
                font=("Arial", 8, "bold"),
                fill="#00000000",
                tags=f"animating_disk"
            )
        
        # Continue animation or finish
        if step < total_steps:
            self.animation_id = self.root.after(16, lambda: self.animate_disk_step(
                disk_size, start_x, start_y, end_x, end_y, height_offset, step + 1, total_steps
            ))
        else:
            # Animation complete
            self.canvas.delete(f"animating_disk")
            
            # Call the callback function if provided
            if self.animation_callback:
                self.animation_callback()
                self.animation_callback = None
    
    def show_victory_animation(self):
        """Display a celebration animation when player wins"""
        # Create particles
        self.particles = []
        for _ in range(50):
            x = random.randint(0, self.canvas.winfo_width())
            y = random.randint(0, self.canvas.winfo_height())
            dx = random.uniform(-2, 2)
            dy = random.uniform(-4, -1)
            color = random.choice(["#ffca3a", "#ff595e", "#8ac926", "#1982c4", "#6a4c93"])
            size = random.randint(5, 15)
            self.particles.append({
                "x": x, "y": y, "dx": dx, "dy": dy,
                "color": color, "size": size, "life": 100
            })
        
        # Start animation
        self.animate_victory()
    
    def animate_victory(self):
        """Animate victory particles"""
        if not self.particles:
            return
        
        self.canvas.delete("particle")
        
        still_active = False
        for p in self.particles:
            # Update particle position
            p["x"] += p["dx"]
            p["y"] += p["dy"]
            p["dy"] += 0.07  # Gravity
            p["life"] -= 1
            
            if p["life"] > 0:
                still_active = True
                
                # Draw particle
                alpha = int(min(255, p["life"] * 2.55))
                color = p["color"]
                
                self.canvas.create_oval(
                    p["x"] - p["size"] / 2, p["y"] - p["size"] / 2,
                    p["x"] + p["size"] / 2, p["y"] + p["size"] / 2,
                    fill=color, outline="",
                    tags="particle"
                )
        
        if still_active:
            self.root.after(16, self.animate_victory)
        else:
            self.particles = []


class AlgorithmComparisonChart:
    """Create a chart for comparing algorithm performance"""
    def __init__(self, root, times_dict):
        self.root = root
        self.top = tk.Toplevel(root)
        self.top.title("Algorithm Performance Comparison")
        self.top.geometry("700x500")
        self.top.configure(bg="#f5f5f7")
        
        self.times = times_dict
        
       # Create header frame
        header_frame = tk.Frame(self.top, bg="#4285f4", padx=10, pady=10)
        header_frame.pack(fill=tk.X)
        
        header_label = tk.Label(header_frame, text="⏱️ ALGORITHM PERFORMANCE COMPARISON ⏱️", 
                               font=("Arial", 16, "bold"), bg="#4285f4", fg="white")
        header_label.pack()
        
        # Chart area
        self.chart_frame = tk.Frame(self.top, bg="white", padx=20, pady=20)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.canvas = tk.Canvas(self.chart_frame, width=650, height=300, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw chart
        self.draw_chart()
        
        # Button frame
        button_frame = tk.Frame(self.top, bg="#f5f5f7", pady=10)
        button_frame.pack(fill=tk.X)
        
        close_btn = tk.Button(button_frame, text="Close", command=self.top.destroy,
                             bg="#f44336", fg="white", font=("Arial", 11), padx=15, pady=5)
        close_btn.pack()
        
    def draw_chart(self):
        """Draw the performance comparison chart"""
        if not self.times:
            self.canvas.create_text(
                325, 150, 
                text="No algorithm data available", 
                font=("Arial", 14, "bold"), 
                fill="#999"
            )
            return
        
        # Get canvas dimensions
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Set chart margins
        left_margin = 100
        right_margin = 50
        top_margin = 50
        bottom_margin = 80
        
        # Calculate chart area
        chart_width = width - left_margin - right_margin
        chart_height = height - top_margin - bottom_margin
        
        # Draw background grid
        for i in range(5):
            y = top_margin + i * chart_height / 4
            self.canvas.create_line(
                left_margin, y, left_margin + chart_width, y,
                fill="#e0e0e0", dash=(4, 4)
            )
        
        # Find max time value
        max_time = max(self.times.values()) if self.times else 0
        if max_time == 0:
            max_time = 0.001  # Prevent division by zero
        
        # Pad max value by 20%
        max_time *= 1.2
        
        # Draw time axis labels
        for i in range(5):
            y = top_margin + i * chart_height / 4
            value = max_time - i * max_time / 4
            self.canvas.create_text(
                left_margin - 10, y,
                text=f"{value:.6f}s",
                font=("Arial", 8),
                anchor="e",
                fill="#666"
            )
        
        # Draw algorithms
        bar_width = chart_width / (len(self.times) * 2)
        colors = {
            'recursive': "#4CAF50",
            'iterative': "#2196F3",
            'frame_stewart': "#9C27B0"
        }
        
        # Draw bars
        for i, (alg_name, time) in enumerate(self.times.items()):
            if time is None:
                continue
                
            x = left_margin + (i * 2 + 1) * bar_width
            bar_height = (time / max_time) * chart_height
            y = top_margin + chart_height - bar_height
            
            # Bar with gradient effect
            for j in range(int(bar_height)):
                # Create gradient effect
                factor = 1 - j / bar_height / 2  # Less dramatic gradient
                color = colors.get(alg_name, "#666")
                r = int(int(color[1:3], 16) * factor)
                g = int(int(color[3:5], 16) * factor)
                b = int(int(color[5:7], 16) * factor)
                bar_color = f"#{r:02x}{g:02x}{b:02x}"
                
                self.canvas.create_line(
                    x, y + j, x + bar_width, y + j,
                    fill=bar_color, width=1
                )
            
            # Draw bar outline
            self.canvas.create_rectangle(
                x, y, x + bar_width, top_margin + chart_height,
                outline="#00000044", width=1
            )
            
            # Draw time value at top of bar
            self.canvas.create_text(
                x + bar_width / 2, y - 10,
                text=f"{time:.6f}s",
                font=("Arial", 9),
                fill="#333"
            )
            
            # Draw algorithm name at bottom
            alg_display_name = {
                'recursive': "Recursive",
                'iterative': "Iterative",
                'frame_stewart': "Frame-Stewart"
            }.get(alg_name, alg_name)
            
            self.canvas.create_text(
                x + bar_width / 2, top_margin + chart_height + 15,
                text=alg_display_name,
                font=("Arial", 10, "bold"),
                fill=colors.get(alg_name, "#666")
            )
            
        # Draw chart title
        self.canvas.create_text(
            width / 2, 20,
            text="Algorithm Execution Time Comparison",
            font=("Arial", 12, "bold"),
            fill="#333"
        )
        
        # Draw y-axis title
        self.canvas.create_text(
            30, height / 2,
            text="Execution Time (seconds)",
            font=("Arial", 10),
            fill="#666",
            angle=90
        )