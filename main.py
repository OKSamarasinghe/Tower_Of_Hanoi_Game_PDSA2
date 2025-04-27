import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import threading
import time
import random
import pygame
from hanoi_algorithms import recursive_hanoi, iterative_hanoi, frame_stewart
from ui import HanoiCanvas, CustomDialog, ModernDialog
from database import Database


class TowerOfHanoiGame:
    def __init__(self, root):
        self.root = root
        self.root.title("\U0001F9E0 Tower Of Hanoi – Interactive Puzzle Game")
        self.root.geometry("950x700")
        self.root.config(bg="#f5f5f7")
        
        # Set theme for ttk widgets
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('TFrame', background='#f5f5f7')
        style.configure('TButton', font=('Arial', 11), background='#4a86e8', foreground='white', borderwidth=0)
        style.map('TButton', background=[('active', '#3a76d8'), ('pressed', '#2a66c8')])
        
        style.configure('Info.TLabel', font=('Arial', 14, 'bold'), background='#f5f5f7', foreground='#333')
        style.configure('Timer.TLabel', font=('Arial', 12), background='#f5f5f7', foreground='#e63946')
        style.configure('Header.TLabel', font=('Arial', 18, 'bold'), background='#f5f5f7', foreground='#2a66c8')
        
        self.db = Database()
        self.username = ""
        self.num_pegs = 3
        self.num_disks = 0
        self.pegs = {}
        self.selected_peg = None
        self.user_move_count = 0
        self.user_move_sequence = ""
        self.actual_move_sequence = []
        self.actual_move_counter = 0
        self.solution_path = []
        self.current_hint_index = 0
        self.canvas = None
        self.start_time = None
        self.timer_label = None
        self.timer_running = False
        self.is_game_active = False
        self.algorithm_times = {}
        self.auto_play_sequence = None
        self.min_moves = 0
        self.animation_in_progress = False

        pygame.mixer.init()
        self.setup_ui()

    def setup_ui(self):
        # Create a header frame
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.pack(fill=tk.X, pady=(15, 5))
        
        header_label = ttk.Label(header_frame, text="🧠 Tower of Hanoi 🧠", style='Header.TLabel')
        header_label.pack()
        
        # Add a separator
        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill=tk.X, padx=20, pady=5)

        # Main content frame
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Info frame with gradient background
        info_frame = tk.Frame(main_frame, bg="#e9ecef", relief=tk.GROOVE, bd=1)
        info_frame.pack(fill=tk.X, pady=10, ipady=5)

        self.info_label = ttk.Label(info_frame, text="Welcome to Tower of Hanoi", style='Info.TLabel', background="#e9ecef")
        self.info_label.pack(side=tk.LEFT, padx=15)

        self.timer_label = ttk.Label(info_frame, text="Time: 0s", style='Timer.TLabel', background="#e9ecef")
        self.timer_label.pack(side=tk.RIGHT, padx=15)

        # Canvas frame with border
        canvas_frame = tk.Frame(main_frame, bg="white", relief=tk.RIDGE, bd=2)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.canvas = HanoiCanvas(canvas_frame, self.handle_peg_click)

        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        # Game controls frame
        game_controls = ttk.Frame(control_frame)
        game_controls.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create button frame for start and hint
        btn_frame1 = ttk.Frame(game_controls)
        btn_frame1.pack(side=tk.LEFT, padx=5)
        
        start_btn = tk.Button(btn_frame1, text="🎮 Start New Game", 
                              command=self.setup_game, 
                              bg="#4CAF50", fg="white",
                              font=("Arial", 11), 
                              relief=tk.RAISED,
                              padx=15, pady=5)
        start_btn.pack(side=tk.LEFT, padx=5)

        hint_btn = tk.Button(btn_frame1, text="💡 Hint", 
                            command=self.show_hint, 
                            bg="#FFC107", fg="black",
                            font=("Arial", 11), 
                            relief=tk.RAISED,
                            padx=15, pady=5)
        hint_btn.pack(side=tk.LEFT, padx=5)
        
        # Create button frame for leaderboard and compare
        btn_frame2 = ttk.Frame(game_controls)
        btn_frame2.pack(side=tk.LEFT, padx=5)
        
        leaderboard_btn = tk.Button(btn_frame2, text="🏆 Leaderboard", 
                                    command=self.show_leaderboard, 
                                    bg="#2196F3", fg="white",
                                    font=("Arial", 11), 
                                    relief=tk.RAISED,
                                    padx=15, pady=5)
        leaderboard_btn.pack(side=tk.LEFT, padx=5)

        compare_btn = tk.Button(btn_frame2, text="📊 Compare Algorithms", 
                               command=self.show_algorithm_comparison, 
                               bg="#9C27B0", fg="white",
                               font=("Arial", 11), 
                               relief=tk.RAISED,
                               padx=15, pady=5)
        compare_btn.pack(side=tk.LEFT, padx=5)

        # Quit button in a separate frame
        quit_frame = ttk.Frame(control_frame)
        quit_frame.pack(side=tk.RIGHT)
        
        quit_btn = tk.Button(quit_frame, text="❌ Quit", 
                            command=self.root.quit, 
                            bg="#F44336", fg="white",
                            font=("Arial", 11), 
                            relief=tk.RAISED,
                            padx=15, pady=5)
        quit_btn.pack(side=tk.RIGHT, padx=5)

        # Status frame at the bottom
        status_frame = tk.Frame(self.root, bg="#e0e0e0", height=25)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        status_label = tk.Label(status_frame, text="Ready to play!", bg="#e0e0e0", fg="#333", anchor=tk.W, padx=10)
        status_label.pack(side=tk.LEFT)
        
        # Schedule game setup after UI is rendered
        self.root.after(500, self.setup_game)

    def setup_game(self):
        try:
            self.stop_timer()
            self.is_game_active = False
            self.actual_move_sequence = []
            self.actual_move_counter = 0
            self.solution_path = []
            self.current_hint_index = 0
            self.auto_play_sequence = None

            if not self.username:
                self.username = self.get_valid_username()
                if not self.username:
                    return

            peg_choice = self.get_valid_peg_count()
            if not peg_choice:
                return

            self.num_pegs = peg_choice
            self.num_disks = random.randint(5, 10)

            self.pegs = {}
            for i in range(self.num_pegs):
                peg_label = chr(65 + i)
                self.pegs[peg_label] = list(reversed(range(1, self.num_disks + 1))) if peg_label == 'A' else []

            self.canvas.draw(self.pegs)
            self.min_moves = self.get_min_moves(self.num_disks, self.num_pegs)

            if self.num_pegs == 3:
                self.solution_path = recursive_hanoi(self.num_disks, 'A', chr(65 + self.num_pegs - 1), 'B')
            else:
                pegs_list = [chr(65 + i) for i in range(4)]
                self.solution_path = frame_stewart(self.num_disks, pegs_list, 'A', 'D')

            # Updated styling for the game information display
            self.info_label.config(text=f"Game with {self.num_disks} disks on {self.num_pegs} pegs • Min moves: {self.min_moves}")
            
            # Custom dialog box with enhanced styling
            messagebox.showinfo("Game Started", 
                               f"Move all {self.num_disks} disks from Peg A to Peg {chr(65 + self.num_pegs - 1)}.\n\n"
                               f"Minimum moves needed: {self.min_moves}\n\n"
                               f"Rules:\n"
                               f"1. Move only one disk at a time\n"
                               f"2. A larger disk cannot be placed on a smaller disk")

            self.get_user_predictions()
            
            # Check if the user provided a sequence and if it's valid
            if self.user_move_sequence and self.validate_move_sequence(self.user_move_sequence) is True:
                self.auto_play_sequence = [tuple(move.strip().split('->')) for move in self.user_move_sequence.split(',')]
            
            self.start_time = time.time()
            self.timer_running = True
            self.is_game_active = True
            self.update_timer()
            
            # If there's a valid sequence to auto-play, start playing it
            if self.auto_play_sequence:
                self.root.after(500, self.auto_play_next_move)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def auto_play_next_move(self):
        """Process the next move in the auto-play sequence instantly (no animation)"""
        if not self.auto_play_sequence or not self.is_game_active:
            return

        source, target = self.auto_play_sequence.pop(0)

        if not self.pegs[source]:
            messagebox.showwarning("Invalid Move", f"Invalid move: {source}->{target}, source peg is empty")
            self.selected_peg = None
            self.auto_play_sequence = None
            return

        if self.pegs[target] and self.pegs[source][-1] > self.pegs[target][-1]:
            messagebox.showwarning("Invalid Move", f"Invalid move: {source}->{target}, larger disk on smaller disk")
            self.selected_peg = None
            self.auto_play_sequence = None
            return

        # Directly move the disk (no animation)
        disk = self.pegs[source].pop()
        self.pegs[target].append(disk)

        self.actual_move_sequence.append(f"{source}->{target}")
        self.actual_move_counter += 1

        self.canvas.draw(self.pegs)
        self.play_sound("sounds/move.wav")

        if self.check_win():
            if self.actual_move_counter <= self.min_moves:
                self.game_won()
            else:
                self.show_loss_message()
            return

        if self.auto_play_sequence:
            self.root.after(500, self.auto_play_next_move)


    def finish_auto_play_move(self, disk, target):
        """Complete the auto-play move after animation"""
        self.pegs[target].append(disk)
        self.actual_move_sequence.append(f"{self.selected_peg}->{target}")
        self.actual_move_counter += 1
        self.canvas.unhighlight_peg(self.selected_peg)
        self.selected_peg = None
        self.canvas.draw(self.pegs)
        self.play_sound("sounds/move.wav")
        self.animation_in_progress = False
        
        # Check if the game is won
        if self.check_win():
            if self.actual_move_counter <= self.min_moves:
                self.game_won()
            else:
                self.show_loss_message()
            return
            
        # Continue with next move after a delay
        if self.auto_play_sequence:
            self.root.after(500, self.auto_play_next_move)

    def show_hint(self):
        if not self.is_game_active:
            messagebox.showinfo("Hint", "Start a game first to get hints!")
            return
            
        if self.current_hint_index < len(self.solution_path):
            move = self.solution_path[self.current_hint_index]
            
            # Show hint with improved styling
            hint_dialog = ModernDialog(self.root, 
                                      title="Hint",
                                      message=f"Try this move: {move[0]} → {move[1]}",
                                      icon="💡")
            
            self.current_hint_index += 1
        else:
            messagebox.showinfo("Hint", "No more hints available!")

    def show_loss_message(self):
        self.stop_timer()
        self.is_game_active = False
        
        # Enhanced loss message
        result = messagebox.showwarning("Game Over", 
                                       f"You used {self.actual_move_counter} moves, but the minimum is {self.min_moves}.\n\nWould you like to try again?",
                                       type=messagebox.YESNO)
        
        if result == 'yes':
            self.setup_game()

    def handle_peg_click(self, peg_name):
        if not self.is_game_active or self.auto_play_sequence:
            # Prevent manual clicks during auto-play
            return

        if self.selected_peg is None:
            if self.pegs[peg_name]:
                self.selected_peg = peg_name
                self.canvas.highlight_peg(peg_name)
            else:
                self.play_sound("sounds/error.wav")
        else:
            if self.selected_peg != peg_name:
                if not self.pegs[peg_name] or self.pegs[self.selected_peg][-1] < self.pegs[peg_name][-1]:
                    disk = self.pegs[self.selected_peg].pop()
                    self.pegs[peg_name].append(disk)
                    self.actual_move_sequence.append(f"{self.selected_peg}->{peg_name}")
                    self.actual_move_counter += 1
                    self.canvas.draw(self.pegs)
                    self.play_sound("sounds/move.wav")
                    if self.check_win():
                        if self.actual_move_counter <= self.min_moves:
                            self.game_won()
                        else:
                            self.show_loss_message()
                else:
                    messagebox.showwarning("Invalid Move", "Cannot place larger disk on smaller disk.")
                    self.play_sound("sounds/error.wav")
            self.canvas.unhighlight_peg(self.selected_peg)
            self.selected_peg = None


    def finish_manual_move(self, disk, target_peg, source_peg):
        """Complete manual move after animation"""
        self.pegs[target_peg].append(disk)
        self.actual_move_sequence.append(f"{source_peg}->{target_peg}")
        self.actual_move_counter += 1
        self.canvas.draw(self.pegs)
        self.play_sound("sounds/move.wav")
        
        # Check win condition
        if self.check_win():
            if self.actual_move_counter <= self.min_moves:
                self.game_won()
            else:
                self.show_loss_message()
        
        self.canvas.unhighlight_peg(self.selected_peg)
        self.selected_peg = None
        self.animation_in_progress = False

    def get_valid_username(self):
        """Get valid username with improved dialog"""
        dialog = ModernDialog(self.root, 
                             title="Welcome!",
                             message="Please enter your name:",
                             icon="👋",
                             is_input=True)
        
        if dialog.result is None:
            return None
            
        username = dialog.result.strip()
        
        if not username:
            messagebox.showerror("Invalid Input", "Name cannot be empty.")
            return self.get_valid_username()
        elif len(username) > 50:
            messagebox.showerror("Invalid Input", "Name too long.")
            return self.get_valid_username()
            
        return username

    def get_valid_peg_count(self):
        """Get valid peg count with improved dialog"""
        dialog = ModernDialog(self.root, 
                            title="Game Setup",
                            message="Enter number of pegs (3 or 4):",
                            icon="🔢",
                            is_input=True,
                            input_type="number")
        
        if dialog.result is None:
            return None
            
        try:
            peg_choice = int(dialog.result)
            if peg_choice not in [3, 4]:
                messagebox.showerror("Invalid Input", "Only 3 or 4 pegs allowed.")
                return self.get_valid_peg_count()
            return peg_choice
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a number.")
            return self.get_valid_peg_count()

    def get_user_predictions(self):
        """Get user move predictions with improved dialog"""
        # Ask for move count prediction
        dialog = ModernDialog(self.root, 
                            title="Your Prediction",
                            message=f"How many moves do you think are needed for {self.num_disks} disks on {self.num_pegs} pegs?",
                            icon="🤔",
                            is_input=True,
                            input_type="number")
        
        if dialog.result is None:
            self.user_move_count = 0
        else:
            try:
                count = int(dialog.result)
                if count < 1:
                    messagebox.showerror("Invalid Input", "Please enter a positive number.")
                    self.user_move_count = 0
                else:
                    self.user_move_count = count
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number.")
                self.user_move_count = 0

        # Ask for move sequence
        dialog = CustomDialog(self.root, 
                            f"Enter your sequence of moves for {self.num_disks} disks on {self.num_pegs} pegs\n(e.g., A->C,A->B,C->B)", 
                            self.validate_move_sequence)
        self.user_move_sequence = dialog.result if dialog.result else ""

    def validate_move_sequence(self, sequence):
        if not sequence:
            return True
        moves = sequence.split(',')
        for move in moves:
            move = move.strip()
            if not move:
                return "Move sequence contains empty moves"
            parts = move.split('->')
            if len(parts) != 2:
                return f"Invalid move format: {move}. Use format 'A->B'"
            source, target = parts[0].strip(), parts[1].strip()
            if source not in self.pegs or target not in self.pegs:
                return f"Invalid peg '{source}' or '{target}'"
            if source == target:
                return f"Invalid move {move}: same source and target"
        return True

    def get_min_moves(self, n, pegs):
        if pegs == 3:
            return 2 ** n - 1
        else:
            return min([2 * self.get_min_moves(k, pegs) + 2 ** (n - k) - 1 for k in range(1, n)]) if n > 1 else 1

    def check_win(self):
        target_peg = chr(65 + self.num_pegs - 1)
        return len(self.pegs[target_peg]) == self.num_disks

    def game_won(self):
        self.stop_timer()
        self.is_game_active = False
        self.play_sound("sounds/win.wav")
        elapsed_time = int(time.time() - self.start_time)
        
        # Show victory animation
        self.canvas.show_victory_animation()
        
        if self.auto_play_sequence is not None and len(self.auto_play_sequence) == 0:
            # Game was won using user's sequence
            messagebox.showinfo("🎉 Congratulations! 🎉", 
                               f"Your sequence of moves successfully solved the puzzle!\n\n"
                               f"⏱️ Time: {elapsed_time} seconds\n"
                               f"🔢 Predicted moves: {self.user_move_count}\n"
                               f"🎮 Actual moves: {self.actual_move_counter}\n"
                               f"✅ Minimum moves: {self.min_moves}")
        else:
            messagebox.showinfo("🎉 Congratulations! 🎉", 
                               f"You solved the puzzle!\n\n"
                               f"⏱️ Time: {elapsed_time} seconds\n"
                               f"✅ Minimum moves: {self.min_moves}\n"
                               f"🎮 Your moves: {self.actual_move_counter}")
        
        threading.Thread(target=self.run_algorithms, args=(elapsed_time,)).start()

    def validate_user_solution(self):
        if not self.user_move_sequence:
            return False, []
        if self.num_pegs == 3:
            correct_moves = recursive_hanoi(self.num_disks, 'A', chr(65 + self.num_pegs - 1), 'B')
        else:
            pegs_list = [chr(65 + i) for i in range(4)]
            correct_moves = frame_stewart(self.num_disks, pegs_list, 'A', 'D')
        try:
            user_sequence = [tuple(move.strip().split("->")) for move in self.user_move_sequence.split(",")]
        except Exception:
            return False, []
        is_correct = (len(user_sequence) == self.min_moves) and all(u == c for u, c in zip(user_sequence, correct_moves))
        return is_correct, user_sequence

    def run_algorithms(self, elapsed_time):
        self.algorithm_times = {}
        start = time.time()
        recursive_moves = recursive_hanoi(self.num_disks, 'A', chr(65 + self.num_pegs - 1), 'B')
        self.algorithm_times['recursive'] = time.time() - start

        start = time.time()
        iterative_moves = iterative_hanoi(self.num_disks, 'A', chr(65 + self.num_pegs - 1), 'B')
        self.algorithm_times['iterative'] = time.time() - start

        if self.num_pegs == 4:
            start = time.time()
            pegs_list = [chr(65 + i) for i in range(4)]
            frame_stewart_moves = frame_stewart(self.num_disks, pegs_list, 'A', 'D')
            self.algorithm_times['frame_stewart'] = time.time() - start
            if len(recursive_moves) > len(frame_stewart_moves):
                efficiency_note = f"4-peg solution is more efficient ({len(frame_stewart_moves)} vs {len(recursive_moves)})"
            else:
                efficiency_note = f"3-peg solution matches 4-peg efficiency ({len(recursive_moves)} moves)"
        else:
            self.algorithm_times['frame_stewart'] = None
            efficiency_note = "3-peg solution used"

        is_correct, parsed_moves = self.validate_user_solution()
        user_moves_str = ','.join([f"{a}->{b}" for a, b in parsed_moves]) if parsed_moves else ""
        actual_moves_str = ','.join(self.actual_move_sequence)

        # Save result with min_moves included
        self.db.save_result(
            self.username, self.num_disks, self.num_pegs,
            True, self.algorithm_times, elapsed_time,
            user_moves_str, is_correct,
            efficiency_note,
            actual_moves=actual_moves_str,
            min_moves=self.min_moves
        )

        self.show_algorithm_comparison()

    def update_timer(self):
        if self.timer_running and self.start_time:
            elapsed = int(time.time() - self.start_time)
            self.timer_label.config(text=f"⏱️ Time: {elapsed}s")
            self.root.after(1000, self.update_timer)

    def stop_timer(self):
        self.timer_running = False

    def play_sound(self, filename):
        try:
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error playing sound: {e}")

    def show_leaderboard(self):
        top_scores = self.db.get_top_scores()
        if not top_scores:
            messagebox.showinfo("Leaderboard", "No scores recorded yet!")
            return
            
        # Create a custom leaderboard window
        leaderboard_window = tk.Toplevel(self.root)
        leaderboard_window.title("🏆 Leaderboard 🏆")
        leaderboard_window.geometry("500x400")
        leaderboard_window.configure(bg="#f0f0f0")
        
        # Create a header
        header_frame = tk.Frame(leaderboard_window, bg="#4285f4", padx=10, pady=10)
        header_frame.pack(fill=tk.X)
        
        header_label = tk.Label(header_frame, text="🏆 TOWER OF HANOI LEADERBOARD 🏆", 
                               font=("Arial", 16, "bold"), bg="#4285f4", fg="white")
        header_label.pack()
        
        # Create the leaderboard table
        table_frame = tk.Frame(leaderboard_window, bg="white", padx=15, pady=15)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Table header
        header_bg = "#e0e0e0"
        tk.Label(table_frame, text="Rank", font=("Arial", 12, "bold"), bg=header_bg, width=5).grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        tk.Label(table_frame, text="Player", font=("Arial", 12, "bold"), bg=header_bg, width=15).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        tk.Label(table_frame, text="Time", font=("Arial", 12, "bold"), bg=header_bg, width=8).grid(row=0, column=2, sticky="ew", padx=5, pady=5)
        tk.Label(table_frame, text="Disks", font=("Arial", 12, "bold"), bg=header_bg, width=5).grid(row=0, column=3, sticky="ew", padx=5, pady=5)
        tk.Label(table_frame, text="Pegs", font=("Arial", 12, "bold"), bg=header_bg, width=5).grid(row=0, column=4, sticky="ew", padx=5, pady=5)
        
        # Table data
        for idx, (username, time_taken, disks, pegs) in enumerate(top_scores, start=1):
            # Alternating row colors
            row_bg = "#f9f9f9" if idx % 2 == 0 else "white"
            
            # Add medal emoji for top 3
            rank_text = f"{idx}"
            if idx == 1:
                rank_text = "🥇"
            elif idx == 2:
                rank_text = "🥈"
            elif idx == 3:
                rank_text = "🥉"
                
            tk.Label(table_frame, text=rank_text, font=("Arial", 12), bg=row_bg).grid(row=idx, column=0, sticky="ew", padx=5, pady=5)
            tk.Label(table_frame, text=username, font=("Arial", 12), bg=row_bg).grid(row=idx, column=1, sticky="w", padx=5, pady=5)
            tk.Label(table_frame, text=f"{time_taken}s", font=("Arial", 12), bg=row_bg).grid(row=idx, column=2, sticky="ew", padx=5, pady=5)
            tk.Label(table_frame, text=str(disks), font=("Arial", 12), bg=row_bg).grid(row=idx, column=3, sticky="ew", padx=5, pady=5)
            tk.Label(table_frame, text=str(pegs), font=("Arial", 12), bg=row_bg).grid(row=idx, column=4, sticky="ew", padx=5, pady=5)
        
        # Close button
        btn_frame = tk.Frame(leaderboard_window, bg="#f0f0f0", pady=10)
        btn_frame.pack(fill=tk.X)
        
        close_btn = tk.Button(btn_frame, text="Close", command=leaderboard_window.destroy,
                             bg="#f44336", fg="white", font=("Arial", 11), padx=15, pady=5)
        close_btn.pack()

    def show_algorithm_comparison(self):
        if not self.algorithm_times:
            messagebox.showinfo("Algorithm Comparison", "No algorithm data available yet!")
            return
        
            # Create a custom algorithm comparison window
        comparison_window = tk.Toplevel(self.root)
        comparison_window.title("📊 Algorithm Performance Comparison")
        comparison_window.geometry("650x500")
        comparison_window.configure(bg="#f5f5f7")
    
        # Create a header
        header_frame = tk.Frame(comparison_window, bg="#4285f4", padx=10, pady=10)
        header_frame.pack(fill=tk.X)
    
        header_label = tk.Label(header_frame, text="⏱️ ALGORITHM PERFORMANCE ANALYSIS ⏱️", 
                           font=("Arial", 16, "bold"), bg="#4285f4", fg="white")
        header_label.pack()
    
        # Create the comparison content frame
        content_frame = tk.Frame(comparison_window, bg="white", padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
        # Add test info
        info_text = f"Test configuration: {self.num_disks} disks on {self.num_pegs} pegs"
        tk.Label(content_frame, text=info_text, font=("Arial", 12, "bold"), 
            bg="white").pack(pady=(0, 15))
    
        # Results frame
        results_frame = tk.Frame(content_frame, bg="white")
        results_frame.pack(fill=tk.X, pady=10)
    
        # Algorithm results with visual indicators
        algorithms = [
        ("Recursive Algorithm", self.algorithm_times['recursive'], "#4CAF50"),
        ("Iterative Algorithm", self.algorithm_times['iterative'], "#2196F3")
    ]
    
        if self.algorithm_times['frame_stewart'] is not None:
            algorithms.append(("Frame-Stewart Algorithm", self.algorithm_times['frame_stewart'], "#9C27B0"))
    
        # Find the fastest algorithm
        fastest_time = min([time for _, time, _ in algorithms if time is not None])
    
        for algo_name, time, color in algorithms:
            algo_frame = tk.Frame(results_frame, bg="white", pady=10)
            algo_frame.pack(fill=tk.X)
        
        # Add a visual speed indicator
        indicator_width = int(400 * (fastest_time / time)) if time > 0 else 400
        indicator = tk.Frame(algo_frame, bg=color, width=indicator_width, height=15)
        indicator.pack(side=tk.LEFT, padx=10)
        
        # Add time text
        time_text = f"{algo_name}: {time:.6f} seconds"
        if time == fastest_time:
            time_text += " (Fastest! ⚡)"
        
        tk.Label(algo_frame, text=time_text, font=("Arial", 11), 
                bg="white", anchor="w").pack(side=tk.LEFT, padx=5)
    
        # Add average stats if available
        stats = self.db.get_algorithm_stats()
        if stats:
            separator = ttk.Separator(content_frame, orient='horizontal')
            separator.pack(fill=tk.X, pady=15)
        
            tk.Label(content_frame, text="Average Performance (All Games)", 
                font=("Arial", 12, "bold"), bg="white").pack(pady=(5, 10))
            
            for alg, avg_time in stats.items():
                stat_text = f"{alg}: {avg_time:.6f} seconds"
                tk.Label(content_frame, text=stat_text, font=("Arial", 11), 
                    bg="white").pack(anchor="w", pady=2)
    
        # User performance frame
        user_frame = tk.Frame(content_frame, bg="#f9f9f9", padx=15, pady=15)
        user_frame.pack(fill=tk.X, pady=(20, 10))
    
        user_label = tk.Label(user_frame, text=f"Your performance: {self.actual_move_counter} moves in {int(time.time() - self.start_time) if self.start_time else 0} seconds", 
                         font=("Arial", 11, "bold"), bg="#f9f9f9")
        user_label.pack(anchor="w")
    
        # Close button
        btn_frame = tk.Frame(comparison_window, bg="#f5f5f7", pady=10)
        btn_frame.pack(fill=tk.X)
    
        close_btn = tk.Button(btn_frame, text="Close", command=comparison_window.destroy,
                         bg="#f44336", fg="white", font=("Arial", 11), padx=15, pady=5)
        close_btn.pack()


if __name__ == "__main__":
    root = tk.Tk()
    app = TowerOfHanoiGame(root)
    root.mainloop()