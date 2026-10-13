import tkinter as tk
from tkinter import messagebox
import turtle
import random
import time
import pygame
from pygame import mixer
from PIL import Image, ImageTk


class GameLauncher:
    """Main launcher that connects Mastermind and Geometry Dash"""
    def __init__(self):
        self.mastermind_complete = False
        self.music_initialized = False
        self.gif_frames = []
        self.current_frame = 0
        self.bg_label = None
        
    def create_story_screen(self):
        """Create the story screen to inform the user about the story"""
        root = tk.Tk()
        root.title("Story")
        root.geometry("950x540")
        root.resizable(False, False)

        # Initialize and play music
        self.play_music_title()

        # Try to load gif, but proceed even if file doesn't exist
        try:
            gif = Image.open("title_background.gif")
            self.gif_frames = []
            i = 0
            try:
                while True:
                    gif.seek(i)
                    frame = gif.copy()
                    self.gif_frames.append(ImageTk.PhotoImage(frame))
                    i += 1
            except EOFError:
                pass
        except FileNotFoundError:
            print("title_background.gif not found - using solid background")
            self.gif_frames = []
        
        self.current_frame = 0
        self.bg_label = tk.Label(root, bg="#8B4513")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Animates the background gif
        def animate():
            if self.gif_frames:
                self.bg_label.config(image=self.gif_frames[self.current_frame])
                self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
            root.after(40, animate)
        
        animate()

        # Story Description
        story = tk.Label( 
            text="You must play 2 games\n\n"
                 "1. Mastermind\n"
                 "2. Geometry Dash\n"
                 "Once you complete Mastermind, you open the vault\n"
                 "You must escape from the police in Geometry Dash\n"
                 "Good luck!",
            font=('ArcadeClassic', 15), fg="white", bg="#1e1e1e", justify="center")
        story.pack(side="bottom", pady=20)

        # Start button
        start_btn = tk.Button(text="BEGIN HEIST", 
                             font=('ArcadeClassic', 20, 'bold'),
                             bg="#ffffff", fg="black",
                             activebackground="#ffffff",
                             relief="flat", padx=20, pady=6,
                             cursor="hand2",
                             command=lambda: self.start_mastermind(root))
        start_btn.pack(side="bottom", pady=10)

        root.mainloop()
    
    def start_mastermind(self, root):
        """Launch Mastermind game"""
        mixer.music.stop()
        mixer.quit()
        self.music_initialized = False
        root.destroy()
        
        # Create and run Mastermind
        mastermind = MastermindGame(self.on_mastermind_complete)
        mastermind.create_welcome_screen()
    
    def on_mastermind_complete(self):
        """Called when Mastermind is completed"""
        print("Mastermind complete! Starting Geometry Dash...")
        self.mastermind_complete = True
        try:
            run_intermediate_screen(self.start_geometry_dash)
        except Exception as e:
            print(f"ERROR launching Intermediate Screen: {e}")
            import traceback
            traceback.print_exc()

    def start_geometry_dash(self):
        """Launch Geometry Dash after intermediate screen"""
        try:
            geometry = GeometryDash(completion_callback=self.on_geometry_dash_complete)
            print("GeometryDash object created, calling run()...")
            geometry.run()
        except Exception as e:
            print(f"ERROR launching Geometry Dash: {e}")
            import traceback
            traceback.print_exc()

    def on_geometry_dash_complete(self):
        """Called when Geometry Dash is completed"""
        try:
            endscreen = GameEndscreen(  width=800,height=800,
background_image="cozy_cottage.gif",        music_file="21st_Century.mp3"  # Add your music file here
    )
            endscreen.run()
        except Exception as e:
            print(f"ERROR launching End Screen: {e}")
            import traceback
            traceback.print_exc()
    
    def play_music_title(self):
        """Play background music for title screen"""
        if not self.music_initialized:
            try:
                mixer.init()
                mixer.music.load("GD_MenuMusic.mp3")
                mixer.music.play(-1)
                self.music_initialized = True
            except:
                print("Could not load music file - continuing without music")


class MastermindGame:
    def __init__(self, completion_callback=None):
        self.colors = ["red", "blue", "green", "yellow", "black", "white"]
        self.code_length = 4
        self.max_attempts = 10
        self.secret_code = []
        self.current_attempt = 0
        self.current_guess = []
        self.screen = None
        self.pen = None
        self.gif_frames = []
        self.bg_frames = []
        self.music_initialized = False
        self.completion_callback = completion_callback
        self.game_running = True
        
    def create_welcome_screen(self):
        """Create the welcome screen with Tkinter"""
        root = tk.Tk()
        root.title("Mastermind Game")
        root.geometry("800x800")
        root.resizable(False, False)
        
        # Initialize and play music
        self.play_music_mastermind()
        
        # Try to load gif, but proceed even if file doesn't exist
        try:
            gif = Image.open("wood_background.gif")
            self.gif_frames = []
            i = 0
            try:
                while True:
                    gif.seek(i)
                    frame = gif.copy()
                    self.gif_frames.append(ImageTk.PhotoImage(frame))
                    i += 1
            except EOFError:
                pass
        except FileNotFoundError:
            print("wood_background.gif not found - using solid background")
            self.gif_frames = []
        
        self.current_frame = 0
        self.bg_label = tk.Label(root, bg="#8B4513")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        def animate():
            if self.gif_frames:
                self.bg_label.config(image=self.gif_frames[self.current_frame])
                self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
            root.after(40, animate)
        
        animate()
        
        panel = tk.Frame(root, bg="#1e1e1e")
        panel.place(relx=0.5, rely=0.5, anchor="center", width=500, height=420)
        
        # Title
        title = tk.Label(panel, text="MASTERMIND", font=('ArcadeClassic', 44, 'bold'), 
                        fg="white", bg="#1e1e1e")
        title.pack(pady=(30, 10))
        
        # Instructions
        instructions = tk.Label(panel, 
            text="Crack the secret code!\n\n"
                 "- Choose 4 colors from the palette\n"
                 "- Red peg = correct color and position\n"
                 "- Black peg = correct color, wrong position\n"
                 "- Peg order DOES NOT matter\n"
                 f"- You have {self.max_attempts} attempts",
            font=('ArcadeClassic', 16), fg="white", bg="#1e1e1e", justify="center")
        instructions.pack(pady=20)
        
        # Start button
        start_btn = tk.Button(panel, text="START GAME", 
                             font=('ArcadeClassic', 20, 'bold'),
                             bg="#ffffff", fg="black",
                             activebackground="#ffffff",
                             relief="flat", padx=40, pady=12,
                             cursor="hand2",
                             command=lambda: self.start_game(root))
        start_btn.pack(pady=20)
        
        root.mainloop()
    
    def start_game(self, root):
        root.destroy()
        self.create_game_screen()
    
    def create_game_screen(self):
        """Creates the mastermind game screen with the actual game"""
        # Screen setup
        self.screen = turtle.Screen()
        self.screen.setup(width=800, height=800)
        self.screen.title("Mastermind Game")
        self.screen.bgcolor("white")
        self.screen.tracer(0)
        
        # Load animated background
        try:
            self.bg_frames = self.load_gif_frames("wood_background.gif")
            for frame in self.bg_frames:
                self.screen.addshape(frame)
            self.animate_background()
        except FileNotFoundError:
            print("wood_background.gif not found - using solid background")
            self.screen.bgcolor("#D2B48C")
        
        # User definition
        self.pen = turtle.Turtle()
        self.pen.hideturtle()
        self.pen.speed(0)
        
        # Creates the secret code
        self.secret_code = random.choices(self.colors, k=self.code_length)
        #print(f"SECRET CODE (for testing): {self.secret_code}")
        
        self.draw_board()
        
        self.pen.penup()
        self.pen.goto(0, -380)
        self.pen.color("red")
        #self.pen.write(f"SECRET CODE: {' '.join(self.secret_code)}", align="center", font=("ArcadeClassic", 14, "bold"))
        self.screen.update()
        self.draw_clear_button()
        self.draw_submit_button()
        self.screen.update()
        
        self.screen.onclick(self.handle_click)
        self.screen.listen()
        
        # Handle window close
        try:
            self.screen.getcanvas().winfo_toplevel().protocol("WM_DELETE_WINDOW", self.on_closing)
        except:
            pass
        
        self.screen.mainloop()
    
    def on_closing(self):
        """Handle window close event"""
        self.game_running = False  # Stop background animation
        self.stop_music()
        try:
            self.screen.clearscreen()
        except:
            pass
    
    def draw_board(self):
        turt = self.pen
        turt.clear()
        turt.penup()
        turt.setheading(0)
        turt.penup()
        turt.goto(-160, 300)
        turt.pendown()
        turt.color("white")
        
        style = ("ArcadeClassic", 60, "bold")
        turt.write("Mastermind", font=style)
        turt.pensize(5)
        turt.speed(0)
        
        # Defining values for circles
        radius = 15
        start_x = -125
        start_y = 220
        gap = 50
        
        # Draw guess circles
        turt.penup()
        turt.goto(start_x, start_y)
        turt.pendown()
        
        for row in range(10):
            for col in range(4):
                turt.pendown()
                turt.circle(radius)
                turt.penup()
                turt.forward(gap)
            
            turt.backward(gap * 4)
            turt.right(90)
            turt.forward(gap)
            turt.left(90)
        
        # Draw peg holes
        turt.pensize(2)
        start_x_peg = 65
        start_y_peg = 227.5
        radius_peg = 6
        gap_peg = 25
        
        turt.penup()
        turt.goto(start_x_peg, start_y_peg)
        turt.pendown()
        
        for row in range(10):
            for col in range(4):
                turt.pendown()
                turt.circle(radius_peg)
                turt.penup()
                turt.forward(gap_peg)
            
            turt.backward(gap_peg * 4)
            turt.right(90)
            turt.forward(gap)
            turt.left(90)
        
        # Draw color palette
        colors = ["red", "blue", "green", "yellow", "black", "white"]
        turt.penup()
        turt.goto(-150, -335)
        turt.pendown()
        
        for i in range(6):
            turt.color("black", colors[i])
            turt.begin_fill()
            turt.circle(20)
            turt.end_fill()
            turt.penup()
            turt.forward(60)
            turt.pendown()
        
        turt.hideturtle()
        self.screen.update()
    
    def load_gif_frames(self, path):
        """Load GIF frames for turtle background"""
        gif = Image.open(path)
        frames = []
        i = 0
        try:
            while True:
                gif.seek(i)
                frame = gif.copy()
                frame_path = f"_wood_frame_{i}.gif"
                frame.save(frame_path)
                frames.append(frame_path)
                i += 1
        except EOFError:
            pass
        return frames
    
    def animate_background(self, index=0):
        """Animate the background GIF"""
        if not self.bg_frames or not self.game_running:
            return
        
        try:
            self.screen.bgpic(self.bg_frames[index])
            self.screen.update()
            next_index = (index + 1) % len(self.bg_frames)
            self.screen.ontimer(lambda: self.animate_background(next_index), 40)
        except:
            # Window closed or error occurred, stop animation
            pass
    
    def draw_circle(self, x, y, radius, fill_color, outline_color):
        self.pen.penup()
        self.pen.color(outline_color, fill_color)
        self.pen.goto(x, y)
        self.pen.pendown()
        self.pen.begin_fill()
        self.pen.circle(radius)
        self.pen.end_fill()
        self.pen.penup()
    
    def handle_click(self, x, y):
        
        palette_y = -315
        radius = 20
        
        for i, color in enumerate(self.colors):
            palette_x = -150 + i * 60
            dist = ((x - palette_x) ** 2 + (y - palette_y) ** 2) ** 0.5
            
            if dist <= radius:
                self.add_color_to_guess(color)
                return
        
       
        if 200 <= x <= 270 and -280 <= y <= -250:
            self.clear_row()
            return
        
        if 280 <= x <= 350 and -280 <= y <= -250:
            if len(self.current_guess) == self.code_length:
                self.check_guess()
            return
    
    def add_color_to_guess(self, color):
        """Add a color to the current guess and draw it"""
        if len(self.current_guess) < self.code_length:
            self.current_guess.append(color)
            
            # Calculate position for this color in the current row
            row_y = 220 - (self.current_attempt * 50)
            col_x = -125 + (len(self.current_guess) - 1) * 50
            
            # Draw the colored circle
            self.draw_circle(col_x, row_y, 15, color, "black")
            self.screen.update()
    
    def check_guess(self):
      
        result = []

        secret_used = [False] * self.code_length
        guess_used = [False] * self.code_length

        for i in range(self.code_length):
            if self.current_guess[i] == self.secret_code[i]:
                result.append("red")
                secret_used[i] = True
                guess_used[i] = True

     
        for i in range(self.code_length):
            if guess_used[i]:
                continue
            for j in range(self.code_length):
                if not secret_used[j] and self.current_guess[i] == self.secret_code[j]:
                    result.append("white")
                    secret_used[j] = True
                    guess_used[i] = True
                    break
        
       
        self.draw_feedback_pegs(result)
        
    
        if result.count("red") == self.code_length:
            self.game_over(True)
            return
       
        self.current_attempt += 1
        self.current_guess = []
        
       
        if self.current_attempt >= self.max_attempts:
            self.game_over(False)
        
        self.screen.update()
    
    def draw_feedback_pegs(self, result):
        """Draw the feedback pegs for the current guess matching the exact positions"""
        row_y = 227.5 - (self.current_attempt * 50)
        
        for i, peg_color in enumerate(result):
            # Place peg at position matching the guess position
            peg_x = 65 + i * 25
            
            self.draw_circle(peg_x, row_y, 6, peg_color, "black")
    
    def game_over(self, won):
        """Display the when the game is won"""
        self.pen.goto(0, -200)
        
        if won:
            self.pen.color("black")
            self.pen.write(
                f"YOU WIN! CODE CRACKED IN {self.current_attempt + 1} ATTEMPTS!",
                align="center",
                font=("ArcadeClassic", 16, "bold")
            )
            # Draw button to go to Geometry Dash
            self.draw_next_game_button()
        else:
            self.pen.color("red")
            self.pen.write(
                f"GAME OVER! The code was: {' '.join(self.secret_code)}",
                align="center",
                font=("ArcadeClassic", 16, "bold")
            )
        
        self.screen.update()
    
    def launch_next_game(self):
        """Launch Geometry Dash after Mastermind is won"""
        print("Launching Geometry Dash...")
        self.game_running = False  # Stop background animation
        self.stop_music()
        
        # Disable screen updates and remove click handler
        try:
            self.screen.onclick(None)
        except:
            pass
        
        try:
            self.screen.clearscreen()
        except:
            pass
        
        # Small delay to ensure cleanup
        time.sleep(0.5)
        
        # Call the completion callback to launch Geometry Dash
        if self.completion_callback:
            print("Calling completion callback...")
            self.completion_callback()
        else:
            print("ERROR: No completion callback found!")
    
    def draw_next_game_button(self):
        """Draw a button to proceed to Geometry Dash"""
        x, y = -100, -280
        self.pen.penup()
        self.pen.goto(x, y)
        self.pen.setheading(0)
        self.pen.pendown()
        self.pen.fillcolor("#00FF00")
        self.pen.pencolor("black")
        self.pen.pensize(4)
        self.pen.begin_fill()
        
        for _ in range(2):
            self.pen.forward(200)
            self.pen.left(90)
            self.pen.forward(40)
            self.pen.left(90)
        
        self.pen.end_fill()
        self.pen.penup()
        self.pen.pensize(1)
        self.pen.goto(0, y + 12)
        self.pen.color("black")
        self.pen.write("GO TO GEOMETRY DASH", align="center", font=("ArcadeClassic", 14, "bold"))
        
        # Update click handler to include button
        self.screen.onclick(self.handle_click_with_button)
        self.screen.update()
    
    def handle_click_with_button(self, x, y):
        """Handle clicks including the next game button"""
        # Check if clicking the "Go to Geometry Dash" button
        if -100 <= x <= 100 and -280 <= y <= -240:
            self.launch_next_game()
            return
        
        # Otherwise use normal click handler
        self.handle_click(x, y)
    
    def draw_clear_button(self):
        """Draw the clear button to clear the row the user is on"""
        x, y = 200, -280
        self.pen.penup()
        self.pen.goto(x, y)
        self.pen.setheading(0)
        self.pen.pendown()
        self.pen.fillcolor("white")
        self.pen.pencolor("black")
        self.pen.pensize(4)
        self.pen.begin_fill()
        
        for _ in range(2):
            self.pen.forward(70)
            self.pen.left(90)
            self.pen.forward(30)
            self.pen.left(90)
        
        self.pen.end_fill()
        self.pen.penup()
        self.pen.pensize(1)
        self.pen.goto(x + 35, y + 8)
        self.pen.write("Clear Row", align="center", font=("ArcadeClassic", 10, "bold"))
    
    def clear_row(self):
        """Clear the current row's guess"""
        if not self.current_guess:
            return
        
        row_y = 220 - (self.current_attempt * 50)
        
        for j in range(len(self.current_guess)):
            x = -125 + (j * 50)
            self.draw_circle(x, row_y, 15, "gray", "black")
        
        self.current_guess = []
        self.screen.update()
    
    def draw_submit_button(self):
        """Draw the submit button to submit the guess"""
        x, y = 280, -280
        self.pen.penup()
        self.pen.goto(x, y)
        self.pen.setheading(0)
        self.pen.pendown()
        self.pen.fillcolor("white")
        self.pen.pencolor("black")
        self.pen.pensize(4)
        self.pen.begin_fill()
        
        for _ in range(2):
            self.pen.forward(70)
            self.pen.left(90)
            self.pen.forward(30)
            self.pen.left(90)
        
        self.pen.end_fill()
        self.pen.penup()
        self.pen.pensize(1)
        self.pen.goto(x + 35, y + 9)
        self.pen.write("Submit", align="center", font=("ArcadeClassic", 10, "bold"))
    
    def play_music_mastermind(self):
        """Play background music for mastermind"""
        if not self.music_initialized:
            try:
                mixer.init()
                mixer.music.load("Mastermind_retro.mp3")
                mixer.music.play(-1)
                self.music_initialized = True
            except:
                print("Could not load music file - continuing without music")
    
    def stop_music(self):
        """Stop the background music"""
        if self.music_initialized:
            try:
                mixer.music.stop()
                mixer.quit()
            except:
                pass


class GeometryDash:
    def __init__(self, completion_callback=None):
        # Initialize pygame mixer
        mixer.init()
        self.music_initialized = False
        self.completion_callback = completion_callback
        
        # Game objects
        self.screen = None
        self.player = None
        self.ground = None
        self.score_display = None
        self.instructions = None
        self.finish_line_parts = []
        
        # Game variables
        self.score = 0
        self.obstacles = []
        self.gravity = -1.2
        self.jump_speed = 17
        self.obstacle_speed = 7
        self.game_running = True
        self.obstacle_timer = 0
        self.next_obstacle = random.randint(50, 61)
        self.distance_traveled = 0
        
        # Finish line variables
        self.finish_threshold = 1000
        self.finish_spawned = False
        self.level_complete = False

        # Platform variables
        self.platforms = []
        self.platform_height = 0.5
        self.platform_width = 8
        
    def cleanup(self):
        """Clean up resources when program exits"""
        try:
            if self.music_initialized:
                mixer.music.stop()
                mixer.quit()
        except:
            pass
    
    def play_music(self):
        """Initialize and play music only once"""
        if not self.music_initialized:
            try:
                mixer.music.load("StereoMadness.mp3")
                mixer.music.play(-1)
                self.music_initialized = True
            except:
                print("Music file not found or error loading music")
                self.music_initialized = True
    
    def create_game_screen(self):
        """Set up the game screen and objects"""
        # Screen setup
        self.screen = turtle.Screen()
        self.screen.title("Geometry Dash - Extreme Mode")
        self.screen.bgcolor("#287BFF")
        self.screen.setup(width=800, height=600)
        self.screen.tracer(0)
        
        # Player (cube)
        self.player = turtle.Turtle()
        self.player.shape("square")
        self.player.color("#00FF00")
        self.player.shapesize(stretch_wid=1.2, stretch_len=1.2)
        self.player.penup()
        self.player.goto(-300, -200)
        self.player.dy = 0
        self.player.is_jumping = False
        
        # Ground
        self.ground = turtle.Turtle()
        self.ground.shape("square")
        self.ground.color("#404040")
        self.ground.shapesize(stretch_wid=0.5, stretch_len=50)
        self.ground.penup()
        self.ground.goto(0, -230)
        
        # Score display
        self.score_display = turtle.Turtle()
        self.score_display.speed(0)
        self.score_display.color("white")
        self.score_display.penup()
        self.score_display.hideturtle()
        self.score_display.goto(0, 260)
        self.score_display.write(f"Progress: {self.score/self.finish_threshold*100:.2f}%", align="center", 
                                font=("ArcadeClassic", 24, "bold"))
        
        # Instructions
        self.instructions = turtle.Turtle()
        self.instructions.speed(0)
        self.instructions.color("yellow")
        self.instructions.penup()
        self.instructions.hideturtle()
        self.instructions.goto(0, 220)
        self.instructions.write("SPACE/CLICK/ARROW to Jump | EXTREME MODE", align="center", 
                               font=("ArcadeClassic", 14, "bold"))
        
        # Keyboard bindings
        self.screen.listen()
        self.screen.onkeypress(self.jump, "space")
        self.screen.onkeypress(self.restart, "r")
        self.screen.onkeypress(self.quit_game, "q")
        self.screen.onkeypress(self.jump, "Up")
        
        # Mouse bindings
        self.screen.onclick(self.mouse_jump)
    
    def jump(self):
        """Make player jump"""
        if not self.player.is_jumping:
            self.player.dy = self.jump_speed
            self.player.is_jumping = True
    
    def mouse_jump(self, x, y):
        """Make player jump (mouse click)"""
        if not self.game_running:
            return
            
        if not self.player.is_jumping:
            self.player.dy = self.jump_speed
            self.player.is_jumping = True
    
    def create_spike(self, x_position, y_position=-200, size=1.5):
        """Create a single spike"""
        spike = turtle.Turtle()
        spike.shape("triangle")
        spike.color("#FF0000")
        spike.shapesize(stretch_wid=size, stretch_len=1)
        spike.penup()
        spike.goto(x_position, y_position)
        spike.setheading(90)
        return spike

    def create_platform(self, x_position, y_position=None, length=None):
        """Create a platform the player can land on."""
        platform = turtle.Turtle()
        platform.shape("square")
        platform.color("#A0A0A0")

        if length is None:
            length = self.platform_width
        if y_position is None:
            y_position = random.choice([-150])

        platform.shapesize(self.platform_height, length, 1)
        platform.penup()
        platform.goto(x_position, y_position)
        return platform
    
    def create_finish_line(self):
        """Create an epic finish line with multiple visual elements"""
        if self.finish_spawned:
            return
        
        base_x = 450
        
        # Create checkered pattern bars (black and white alternating)
        for i in range(12):
            bar = turtle.Turtle()
            bar.shape("square")
            bar.shapesize(stretch_wid=1.5, stretch_len=0.5)
            bar.penup()
            
            # Alternate colors
            if i % 2 == 0:
                bar.color("#FFFFFF")
            else:
                bar.color("#000000")
            
            y_pos = -220 + (i * 30)
            bar.goto(base_x, y_pos)
            self.finish_line_parts.append(bar)
        
        # Create second column for checkered pattern (offset)
        for i in range(12):
            bar = turtle.Turtle()
            bar.shape("square")
            bar.shapesize(stretch_wid=1.5, stretch_len=0.5)
            bar.penup()
            
            # Alternate colors (opposite of first column)
            if i % 2 == 0:
                bar.color("#000000")
            else:
                bar.color("#FFFFFF")
            
            y_pos = -220 + (i * 30)
            bar.goto(base_x + 15, y_pos)
            self.finish_line_parts.append(bar)
        
        # Add golden border on left
        left_border = turtle.Turtle()
        left_border.shape("square")
        left_border.color("#FFD700")
        left_border.shapesize(stretch_wid=18, stretch_len=0.3)
        left_border.penup()
        left_border.goto(base_x - 10, 0)
        self.finish_line_parts.append(left_border)
        
        # Add golden border on right
        right_border = turtle.Turtle()
        right_border.shape("square")
        right_border.color("#FFD700")
        right_border.shapesize(stretch_wid=18, stretch_len=0.3)
        right_border.penup()
        right_border.goto(base_x + 25, 0)
        self.finish_line_parts.append(right_border)
        
        # Add "FINISH" text
        finish_text = turtle.Turtle()
        finish_text.speed(0)
        finish_text.color("#FFD700")
        finish_text.penup()
        finish_text.hideturtle()
        finish_text.goto(base_x + 7, 200)
        finish_text.write("FINISH", align="center", font=("ArcadeClassic", 28, "bold"))
        self.finish_line_parts.append(finish_text)
        
        # Add stars around the finish line
        star_positions = [
            (base_x - 30, 180),
            (base_x + 45, 180),
            (base_x - 30, -220),
            (base_x + 45, -220)
        ]
        
        for star_x, star_y in star_positions:
            star = turtle.Turtle()
            star.speed(0)
            star.color("#FFFF00")
            star.penup()
            star.hideturtle()
            star.goto(star_x, star_y)
            star.write("★", align="center", font=("ArcadeClassic", 36, "normal"))
            self.finish_line_parts.append(star)
        
        # Add glowing effect circles
        for i in range(3):
            glow = turtle.Turtle()
            glow.shape("circle")
            glow.color("#FFD700")
            glow.shapesize(stretch_wid=0.5 + i * 0.3, stretch_len=0.5 + i * 0.3)
            glow.penup()
            glow.goto(base_x + 7, 150 - i * 100)
            self.finish_line_parts.append(glow)
        
        self.finish_spawned = True
    
    def create_random_obstacle(self):
        """Create random single, double or triple spike obstacles"""
        base_x = 400
        spike_spacing = 28

        # chance to create platform
        if random.random() < 0.50:
            platform = self.create_platform(base_x)
            self.platforms.append(platform)
            if random.random() < 0.5:
                base_x = 430
                base_y = -140
                # Random obstacle type: 45% single, 55% double
                obstacle_type = random.choices([1, 2], weights=[45, 55])[0]
                
                if obstacle_type == 1:
                    # Single spike
                    spike = self.create_spike(base_x, base_y, size=1.5)
                    self.obstacles.append(spike)
                    
                elif obstacle_type == 2:
                    # Double spike - BIGGER
                    spike1 = self.create_spike(base_x, base_y, size=2.2)
                    spike2 = self.create_spike(base_x + spike_spacing, base_y, size=2.2)
                    self.obstacles.append(spike1)
                    self.obstacles.append(spike2)
                    
                elif obstacle_type == 3:
                    # Triple spike - BIG
                    spike1 = self.create_spike(base_x - spike_spacing, base_y, size=2.0)
                    spike2 = self.create_spike(base_x, base_y, size=2.0)
                    spike3 = self.create_spike(base_x + spike_spacing, base_y, size=2.0)
                    self.obstacles.append(spike1)
                    self.obstacles.append(spike2)
                    self.obstacles.append(spike3)

            if random.random()<0.5:
                base_x = 400
                base_y = -215
                # 5 spikes on bottom - jumping is forced
                spike1 = self.create_spike(base_x - spike_spacing * 2, base_y, size=2.0)
                spike2 = self.create_spike(base_x - spike_spacing, base_y, size=2.0)
                spike3 = self.create_spike(base_x, base_y, size=2.0)
                spike4 = self.create_spike(base_x + spike_spacing, base_y, size=2.0)
                spike5 = self.create_spike(base_x + spike_spacing * 2, base_y, size=2.0)
                self.obstacles.append(spike1)
                self.obstacles.append(spike2)
                self.obstacles.append(spike3)
                self.obstacles.append(spike4)
                self.obstacles.append(spike5)

        base_x = 400
        base_y = -215
        
        # Random obstacle type: 30% single, 45% double, 25% triple
        obstacle_type = random.choices([1, 2, 3], weights=[30, 45, 25])[0]
        
        if obstacle_type == 1:
            # Single spike
            spike = self.create_spike(base_x, base_y, size=1.5)
            self.obstacles.append(spike)
            
        elif obstacle_type == 2:
            # Double spike - BIGGER
            spike1 = self.create_spike(base_x, base_y, size=2.2)
            spike2 = self.create_spike(base_x + spike_spacing, base_y, size=2.2)
            self.obstacles.append(spike1)
            self.obstacles.append(spike2)
            
        elif obstacle_type == 3:
            # Triple spike - BIG
            spike1 = self.create_spike(base_x - spike_spacing, base_y, size=2.0)
            spike2 = self.create_spike(base_x, base_y, size=2.0)
            spike3 = self.create_spike(base_x + spike_spacing, base_y, size=2.0)
            self.obstacles.append(spike1)
            self.obstacles.append(spike2)
            self.obstacles.append(spike3)
    
    def update_score(self):
        """Update the score display"""
        self.score += 1
        self.score_display.clear()
        self.score_display.write(f"Progress: {min(self.score/self.finish_threshold*100,100):.2f}%", align="center", 
                                font=("ArcadeClassic", 24, "bold"))
        
        # Spawn finish line when score threshold is reached
        if self.score >= self.finish_threshold * 0.90 and not self.finish_spawned:
            self.create_finish_line()
    
    def check_collision(self, obstacle):
        """Check if player collides with obstacle"""
        distance = self.player.distance(obstacle)
        collision_threshold = 24
        if distance < collision_threshold:
            return True
        return False
    
    def check_finish_collision(self):
        """Check if player reached the finish line"""
        if self.finish_spawned and len(self.finish_line_parts) > 0:
            # Check position of first finish line part
            finish_x = self.finish_line_parts[0].xcor()
            player_x = self.player.xcor()
            # Check if player passed the finish line
            if player_x >= finish_x - 20:
                return True
        return False
    
    def game_over(self):
        """Display game over screen"""
        self.game_running = False
        
        game_over_text = turtle.Turtle()
        game_over_text.speed(0)
        game_over_text.color("red")
        game_over_text.penup()
        game_over_text.hideturtle()
        game_over_text.goto(0, 0)
        game_over_text.write("GAME OVER!", align="center", 
                            font=("ArcadeClassic", 36, "bold"))
        
        restart_text = turtle.Turtle()
        restart_text.speed(0)
        restart_text.color("white")
        restart_text.penup()
        restart_text.hideturtle()
        restart_text.goto(0, -50)
        
        restart_instruction = turtle.Turtle()
        restart_instruction.speed(0)
        restart_instruction.color("yellow")
        restart_instruction.penup()
        restart_instruction.hideturtle()
        restart_instruction.goto(0, -100)
        restart_instruction.write("Press 'R' to Restart or 'Q' to Quit", 
                                 align="center", font=("ArcadeClassic", 16, "normal"))
    
    def victory_screen(self):
        """Display victory screen"""
        self.game_running = False
        self.level_complete = True
        
        victory_text = turtle.Turtle()
        victory_text.speed(0)
        victory_text.color("#FFD700")
        victory_text.penup()
        victory_text.hideturtle()
        victory_text.goto(0, 50)
        victory_text.write("LEVEL COMPLETE!", align="center", 
                          font=("ArcadeClassic", 48, "bold"))
        
        stars = turtle.Turtle()
        stars.speed(0)
        stars.color("#FFFF00")
        stars.penup()
        stars.hideturtle()
        stars.goto(0, -20)
        stars.write("★ ★ ★", align="center", 
                   font=("ArcadeClassic", 60, "normal"))
        
        congrats_text = turtle.Turtle()
        congrats_text.speed(0)
        congrats_text.color("white")
        congrats_text.penup()
        congrats_text.hideturtle()
        congrats_text.goto(0, -80)
        congrats_text.write("You Beat Extreme Mode!", align="center", 
                           font=("ArcadeClassic", 24, "normal"))
        
        restart_instruction = turtle.Turtle()
        restart_instruction.speed(0)
        restart_instruction.color("yellow")
        restart_instruction.penup()
        restart_instruction.hideturtle()
        restart_instruction.goto(0, -130)
        restart_instruction.write("Press 'R' to Play Again or 'Q' to Quit", 
                                 align="center", font=("ArcadeClassic", 16, "normal"))
    
    def reset_game(self):
        """Reset all game variables and objects"""
        # Clear obstacles
        for obstacle in self.obstacles:
            obstacle.hideturtle()
        self.obstacles.clear()

        for platform in self.platforms:
            platform.hideturtle()
        self.platforms.clear()
        
        # Clear finish line parts
        for part in self.finish_line_parts:
            if hasattr(part, 'clear'):
                part.clear()
            part.hideturtle()
        self.finish_line_parts.clear()
        self.finish_spawned = False
        self.level_complete = False
        
        # Reset player
        self.player.goto(-300, -200)
        self.player.dy = 0
        self.player.is_jumping = False
        
        # Reset score
        self.score = 0
        self.distance_traveled = 0
        
        # Reset game variables
        self.obstacle_timer = 0
        self.game_running = True
        
        # Clear and recreate screen
        self.screen.clearscreen()
        self.create_game_screen()
    
    def restart(self):
        """Restart the game"""
        if not self.game_running:
            self.reset_game()
    
    def quit_game(self):
        """Quit the game"""
        self.cleanup()
        try:
            self.screen.clearscreen()
        except:
            pass
    
    def run(self):
        """Main game loop"""
        self.create_game_screen()
        self.play_music()
        
        try:
            while True:
                try:
                    self.screen.update()
                    time.sleep(0.016)  # ~60 FPS

                    if self.level_complete:
                        break
                    
                    if self.game_running:
                        # Apply gravity
                        self.player.dy += self.gravity

                        # Update player position
                        prev_y = self.player.ycor()
                        new_y = self.player.ycor() + self.player.dy

                        # Platform collision (only when falling)
                        if self.player.dy <= 0 and self.platforms:
                            player_x = self.player.xcor()
                            player_left = player_x - 10
                            player_right = player_x + 10

                            prev_bottom = prev_y - 10
                            new_bottom = new_y - 10

                            best_landing_y = None

                            for plat in self.platforms:
                                w = self.platform_width * 10
                                h = self.platform_height * 10
                                plat_left = plat.xcor() - w
                                plat_right = plat.xcor() + w
                                plat_top = plat.ycor() + h

                                x_overlaps = (player_right > plat_left) and (player_left < plat_right)
                                crosses_top = (prev_bottom >= plat_top) and (new_bottom <= plat_top)

                                if x_overlaps and crosses_top:
                                    landing_y = plat_top + 10
                                    if best_landing_y is None or landing_y > best_landing_y:
                                        best_landing_y = landing_y

                            if best_landing_y is not None:
                                new_y = best_landing_y
                                self.player.dy = 0
                                self.player.is_jumping = False
                        
                        # Ground collision
                        if new_y <= -210:
                            new_y = -210
                            self.player.dy = 0
                            self.player.is_jumping = False
                        
                        self.player.sety(new_y)
                        
                        # Check if player reached finish line
                        if self.check_finish_collision():
                            self.victory_screen()
                            continue
                        
                        # Create obstacles only if we haven't reached the finish threshold
                        if self.score < self.finish_threshold * 0.90:
                            self.obstacle_timer += 1
                            if self.obstacle_timer > self.next_obstacle:
                                self.create_random_obstacle()
                                self.distance_traveled += 1
                                self.obstacle_timer = 0
                                self.next_obstacle = random.randint(50, 61)
                        
                        # Move finish line if spawned
                        if self.finish_spawned:
                            for part in self.finish_line_parts:
                                part.setx(part.xcor() - self.obstacle_speed)
                        
                        # Move and check obstacles
                        obstacles_to_remove = []
                        for obstacle in self.obstacles:
                            obstacle.setx(obstacle.xcor() - self.obstacle_speed)
                            
                            # Check collision with spikes
                            if self.check_collision(obstacle):
                                self.game_over()
                                break
                            
                            if obstacle.xcor() < -400:
                                obstacle.hideturtle()
                                obstacles_to_remove.append(obstacle)

                        # Move and remove platforms
                        platforms_to_remove = []
                        for plat in self.platforms:
                            plat.setx(plat.xcor() - self.obstacle_speed)

                            if plat.xcor() < -450:
                                plat.hideturtle()
                                platforms_to_remove.append(plat)

                        # Remove off-screen objects
                        for obstacle in obstacles_to_remove:
                            self.obstacles.remove(obstacle)
                        for plat in platforms_to_remove:
                            self.platforms.remove(plat)

                        self.update_score()
                
                except turtle.Terminator:
                    break
        finally:
            # Always cleanup when exiting
            self.cleanup()
            try:
                if self.screen:
                    self.screen.clearscreen()
            except:
                pass
            if self.level_complete and self.completion_callback:
                self.completion_callback()


import turtle

def run_intermediate_screen(continue_callback=None):
    screen = turtle.Screen()
    screen.setup(1000, 800)
    screen.title("Escape Game")

    message = turtle.Turtle()
    message.hideturtle()
    message.penup()

    button = turtle.Turtle()
    button.hideturtle()
    button.penup()

    end_text = turtle.Turtle()
    end_text.hideturtle()
    end_text.penup()

    def draw_main_screen():
        message.clear()
        button.clear()

        message.goto(0, 100)
        message.write("Vault unlocked! Get ready to run!",
                      align="center",
                      font=("ArcadeClassic", 40, "bold"))

        button.goto(-150, -50)
        button.pendown()
        for _ in range(2):
            button.forward(300)
            button.right(90)
            button.forward(60)
            button.right(90)
        button.penup()

        button.goto(0, -90)
        button.write("Continue to Geometry Dash",
                     align="center",
                     font=("ArcadeClassic", 20, "normal"))

    def show_end_screen():
        message.clear()
        button.clear()
        end_text.clear()

        end_text.goto(0, 0)
        end_text.write("THE END",
                       align="center",
                       font=("ArcadeClassic", 200, "bold"))

    def button_click(x, y):
        if -150 <= x <= 150 and -110 <= y <= -50:
            try:
                screen.clearscreen()
            except:
                pass
            if continue_callback:
                continue_callback()

    draw_main_screen()

    screen.onclick(button_click)

    screen.mainloop()


import turtle
import pygame
from pygame import mixer
from PIL import Image


class GameEndscreen:
    def __init__(self, width=800, height=800, background_image=None, music_file=None):
        # Setup screen
        self.screen = turtle.Screen()
        self.screen.setup(width=width, height=height)
        self.screen.title("Game Endscreen")
        
        # Setup pygame mixer for music
        mixer.init()
        self.music_file = music_file
        
        # Resize and set background image
        if background_image:
            self.set_fullscreen_background(background_image, width, height)
        
        # Setup turtle
        self.t = turtle.Turtle()
        self.t.speed(0)
        self.t.hideturtle()
        self.t.color("white")
        
        # Font styles
        self.title_style = ("ArcadeClassic", 100, "bold")
        self.subtitle_style = ("ArcadeClassic", 30)
        self.instruction_style = ("ArcadeClassic", 20, "bold")
        
    def set_fullscreen_background(self, image_path, width, height):
        """Resize image to fit screen and set as background"""
        try:
            # Open and resize image
            img = Image.open(image_path)
            img_resized = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Save as temporary GIF (turtle only supports GIF)
            temp_gif = "temp_background.gif"
            img_resized.save(temp_gif)
            
            # Set as background
            self.screen.bgpic(temp_gif)
        except Exception as e:
            print(f"Could not load background image: {e}")
            self.screen.bgcolor("black")
    
    def play_music(self):
        """Play the background music"""
        if self.music_file:
            try:
                pygame.mixer.music.load(self.music_file)
                pygame.mixer.music.play(-1)  # -1 means loop indefinitely
            except pygame.error as e:
                print(f"Could not load music file: {e}")
    
    def stop_music(self):
        """Stop the background music"""
        pygame.mixer.music.stop()
        
    def draw_initial_screen(self):
        """Draw the initial end screen"""
        # Draw "The End"
        self.t.penup()
        self.t.goto(-180, 100)
        self.t.write("The End", font=self.title_style, align="left")
        
        # Draw "Congratulations!"
        self.t.goto(-150, 0)
        self.t.write("Congratulations!", font=self.subtitle_style, align="left")
        
        # Draw "Click Anywhere To Continue"
        self.t.goto(0, -250)
        self.t.write("Click Anywhere To Continue", font=self.instruction_style, align="center")
    
    def on_click(self, x, y):
        """Handle click event"""
        # Clear the screen
        self.t.clear()
        
        # Show victory message
        self.t.goto(0, 0)
        self.t.write("You have beat the game!", font=self.subtitle_style, align="center")
      
    
    def run(self):
        """Run the endscreen"""
        self.play_music()
        self.draw_initial_screen()
        self.screen.onclick(self.on_click)
        turtle.done()


# Create and run the endscreen
if __name__ == "__main__" and False:
    endscreen = GameEndscreen(  width=800,height=800,
background_image="cozy_cottage.gif",        music_file="21st_Century.mp3"
    )
    endscreen.run()


if __name__ == "__main__":
    launcher = GameLauncher()
    launcher.create_story_screen()
