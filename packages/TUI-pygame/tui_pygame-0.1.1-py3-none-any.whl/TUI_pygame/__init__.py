import os
import sys
import time

# Define screen dimensions
horizontal_length = 0
vertical_length = 0

# Define mouse position
mouse_position = [0, 0]
is_mouse_pressed = False

# Save screen content
screen = []

def determine_screen_size():
    print("First-time setup: Determining screen dimensions.")
    
    # Determine horizontal length
    print("Enter several block characters (e.g., Chinese characters) and press Enter to determine the horizontal length:")
    horizontal_input = input()
    global horizontal_length
    horizontal_length = len(horizontal_input)
    print(f"Horizontal length determined as: {horizontal_length} characters.")
    
    # Determine vertical length
    print("Press Enter several times, then type 'end' and press Enter to determine the vertical length:")
    vertical_lines = []
    while True:
        line = input()
        if line.strip().lower() == 'end':
            break
        vertical_lines.append(line)
    global vertical_length
    vertical_length = len(vertical_lines) + 1  # Including the 'end' line
    print(f"Vertical length determined as: {vertical_length} lines.")
    
    # Save to text file
    with open("screen_size.txt", "w") as f:
        f.write(f"Horizontal Length: {horizontal_length}\n")
        f.write(f"Vertical Length: {vertical_length}\n")
    
    print("Screen dimensions saved to screen_size.txt.")

def load_screen_size():
    global horizontal_length, vertical_length
    if not os.path.exists("screen_size.txt"):
        determine_screen_size()
    else:
        print("Screen dimensions already exist, loading from file.")
    
    with open("screen_size.txt", "r") as f:
        lines = f.readlines()
        horizontal_length = int(lines[0].split(":")[1].strip())
        vertical_length = int(lines[1].split(":")[1].strip())

def clear_screen():
    # Clear screen function
    os.system('cls' if os.name == 'nt' else 'clear')

def print_screen():
    # Print screen content
    clear_screen()
    for y in range(vertical_length):
        line = ""
        for x in range(horizontal_length):
            if [x, y] == mouse_position:
                if is_mouse_pressed:
                    line += "█"  # Solid block when mouse is pressed
                else:
                    line += "░"  # Hollow block when mouse is not pressed
            else:
                line += screen[y][x]  # Display screen content
        print(line)

def move_mouse(direction):
    global mouse_position
    if direction == 'w' and mouse_position[1] > 0:
        mouse_position[1] -= 1
    elif direction == 's' and mouse_position[1] < vertical_length - 1:
        mouse_position[1] += 1
    elif direction == 'a' and mouse_position[0] > 0:
        mouse_position[0] -= 1
    elif direction == 'd' and mouse_position[0] < horizontal_length - 1:
        mouse_position[0] += 1

def toggle_mouse_press():
    global is_mouse_pressed
    is_mouse_pressed = not is_mouse_pressed

def place_character(character, position):
    if 0 <= position[0] < horizontal_length and 0 <= position[1] < vertical_length:
        screen[position[1]][position[0]] = character

def initialize():
    global screen
    load_screen_size()
    print("Screen dimensions loaded.")
    
    # Initialize screen content
    screen = [[' ' for _ in range(horizontal_length)] for _ in range(vertical_length)]
    
    print("Use 'w', 's', 'a', 'd' keys to move the mouse.")
    print("Press Enter to confirm the position.")
    print("Enter 'place <character> <x> <y>' to place a character at a specific position.")
    print("Enter 'q' to exit the program.")

def run():
    char = sys.stdin.read(1)
    if char == 'w':  # Up
        move_mouse('w')
    elif char == 's':  # Down
        move_mouse('s')
    elif char == 'a':  # Left
        move_mouse('a')
    elif char == 'd':  # Right
        move_mouse('d')
    elif char == '\n':  # Enter key
        toggle_mouse_press()
    elif char == 'q':  # Exit
        return False
    elif char == 'p':  # Place character
        command = input("Enter command (place <character> <x> <y>): ").strip()
        if command.startswith("place"):
            parts = command.split()
            if len(parts) == 4:
                character = parts[1]
                x = int(parts[2])
                y = int(parts[3])
                place_character(character, (x, y))
    return True

def update_screen():
    print_screen()

# Automatically load screen dimensions when the module is imported
load_screen_size()
