#!C:\Program Files\Python312\python
import random
import copy
import argparse
import time
import os
import sys
from datetime import datetime
import sys

########### UTILS ##################
if os.name == "nt":
    import msvcrt
else:
    import tty
    import termios

def getch2():
    key_char = "q"
    while True:
        # Check if a keypress is waiting in the buffer
        if msvcrt.kbhit():
            # Read the key character (returns a byte string like b'a')
            key = msvcrt.getch()
            
            # Decode bytes to a string
            key_char = key.decode('utf-8', errors='ignore')
            #print(f"INFO. You pressed: {key_char} (Raw: {key})")
            break

    return key_char.lower()

def getch1():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

ALL_COORDS = [ [-1,-1], [0,-1], [1,-1], [-1,0], [0,0], [1,0], [-1,1], [0,1], [1,1], ]

ROTATE_CW = {
    (0,0):(0,0),

    ( 0, 1):( 1, 0),
    ( 1, 0):( 0,-1),
    ( 0,-1):(-1, 0),
    (-1, 0):( 0, 1),

    ( 1, 1):( 1,-1),
    ( 1,-1):(-1,-1),
    (-1,-1):(-1, 1),
    (-1, 1):( 1, 1),

    ( 0, 2):( 2, 0),
    ( 2, 0):( 0,-2),
    ( 0,-2):(-2, 0),
    (-2, 0):( 0, 2)
}
ROTATE_CCW = {ROTATE_CW[key]:key for key in ROTATE_CW.keys()}

REL_COORD = {
    "I":[[ 0,1], [0,0], [0,-1], [ 0,-2]],
    "J":[[ 0,1], [0,0], [0,-1], [-1,-1]],
    "L":[[ 0,1], [0,0], [0,-1], [ 1,-1]],
    "S":[[-1,0], [0,0], [0, 1], [ 1, 1]],
    "Z":[[-1,1], [0,0], [0, 1], [ 1, 0]],
    "O":[[ 1,0], [0,0], [0, 1], [ 1, 1]],
    "T":[[-1,0], [0,0], [1, 0], [ 0, 1]],
    "h":[[-1,-1],[1,-1],[1, 0], [-1,0]],
    "r":[[-1,-1],[0,-1],[1, 0], [ 1,1]],
    "w":[[-1,0],[0,-1],[1, -1], [ 1,0]],
    "m":[[-1,0],[0, 1],[1,  1], [ 1,0]],
}

LTTR = "IJLSZOT"
LTTR2 = list(REL_COORD.keys())

CARD = {
    "n": [0,1], "s": [0, -1],"e": [1,0], "w": [-1,0],
}
class Tetrimino(object):

    def __init__(self, rel_coords):
        self.rel_coords = rel_coords
        self.coords = copy.deepcopy(rel_coords)
        self.ctr = [5,16]
        self.update_coords()
        self.score = 0

    def update_coords(self):
        for ii, coord in enumerate(self.coords):

            self.coords[ii][0] = self.ctr[0] + self.rel_coords[ii][0]
            self.coords[ii][1] = self.ctr[1] + self.rel_coords[ii][1]

        #print("DEBUG: coords", self.coords)

    def rotate(self, _dir):
        if _dir == "cw":
            for ii, rel_coord in enumerate(self.rel_coords):
                key = tuple(self.rel_coords[ii])
                self.rel_coords[ii] = (ROTATE_CW[key][0], ROTATE_CW[key][1])
        elif _dir == "ccw":
            for ii, rel_coord in enumerate(self.rel_coords):
                key = tuple(self.rel_coords[ii])
                self.rel_coords[ii] = (ROTATE_CCW[key][0], ROTATE_CCW[key][1])

        print ("DEBUG: rel_coords", self.rel_coords)

        self.update_coords()

    def translate(self, card):
        if card in ("w", "s", "e", "n"):
            self.ctr[0] += CARD[card][0]
            self.ctr[1] += CARD[card][1]

        #print ("DEBUG: ctr", self.ctr)

        self.update_coords()



# Constants
OUTPUT = open("sample.txt").readlines()
SPACE = "."
N_SPACES = 10
RANGE_SPACES = range(N_SPACES)
ROW = [SPACE for x in RANGE_SPACES]


BLOCK = "O"
N_ROWS = 20
MATRIX = [copy.deepcopy(ROW) for x in range(N_ROWS)]

RANGE_ROWS = range(N_ROWS)

KEYS_TRANSLATIONS = {
    "a": "w",
    "s": "s",
    "d": "e",
    "e": "n",
    "w": "s",
}

KEYS_ROTATIONS = {
    "p": "ccw",
    "l": "cw",
    "f": "cw",
    "c": "ccw"
}

# Functions
def my_decorator(func):
    def wrapper(statement):
        choice = random.choice(range(len(OUTPUT)))
        line = str(statement).replace("'","").replace(",","") +" "+ OUTPUT[choice].rstrip("\n")
        func(line)
    return wrapper

@my_decorator
def my_print(statement):
    print(statement)

class MatrixRows(object):
    def __init__(self):
        self.coords =  [[x,-1] for x in RANGE_ROWS]
        self.coords += [[x, 0] for x in [0,1,2,3,5,6,7,8,9]]
        self.coords += [[x, 1] for x in [1,2,6,7,8]]
        self.updated = False

    def update_coords(self, new_coords):
        self.coords += new_coords


######################################## CLASSES  ########################################
class Tetris(object):
    def __init__(self, args):
        self.automate = args.automate
        self.verbose = args.verbose
        self.shapes_type = args.shapes_type
        self.matrix = copy.deepcopy(MATRIX)
        self.rows = MatrixRows()
        self.complete_row = []
        self.score = 0
        if self.shapes_type == "r":
            self.next_letter = "R" 
        elif self.shapes_type == "a":
            self.next_letter = random.choice(LTTR2)
        else:
            self.next_letter = random.choice(LTTR)
        self.get_new_shape()
        self.update_matrix()
        

    def print_matrix(self):
        #os.system("cls" if os.name == "nt" else "clear")
        #my_print(" ----------")
        for y in range(N_ROWS):
            row_str = "".join(self.matrix[N_ROWS - 1 - y])
            row_display = row_str
            my_print(row_display)
        #my_print(" ----------")

    def check_shape_landed(self):
        for rc in self.rows.coords:
            for tc in self.shape.coords:
                if tc[0] == rc[0] and tc[1] == rc[1]:
                    self.move_shape("e")
                    return True
                    break
        

    def update_matrix(self):
        self.matrix = copy.deepcopy(MATRIX)
         
        for coord in self.shape.coords:
            #print("DEBUG: t coords", coord)
            x = coord[0]
            y = coord[1]
            if x in RANGE_SPACES and y in RANGE_ROWS:
                self.matrix[y][x] = "O"

        for coord in self.rows.coords:
            #print("DEBUG: row coord", coord)
            x = coord[0]
            y = coord[1]
            if x in RANGE_SPACES and y in RANGE_ROWS:
                self.matrix[y][x] = "H"

        for coord in self.complete_row:
            #print("DEBUG: row coord", coord)
            x = coord[0]
            y = coord[1]
            if x in RANGE_SPACES and y in RANGE_ROWS:
                self.matrix[y][x] = "+"
            
        self.score += 1
        self.print_matrix()

    def get_new_shape(self):
        if self.shapes_type == "r":
            rel_coord = random.sample(ALL_COORDS, 4)
            self.shape = Tetrimino(rel_coord)
        elif self.shapes_type == "a":
            self.shape = Tetrimino(copy.deepcopy(REL_COORD[self.next_letter]))
            self.next_letter = random.choice(LTTR2)
        else:
            self.shape = Tetrimino(copy.deepcopy(REL_COORD[self.next_letter]))
            self.next_letter = random.choice(LTTR)
            
        

    def move_shape(self, key):
        if key in KEYS_TRANSLATIONS.keys():
            move = KEYS_TRANSLATIONS[key]
            self.shape.translate(move)
        elif key in KEYS_ROTATIONS.keys():
            move = KEYS_ROTATIONS[key]
            print("DEBUG: move", move)
            self.shape.rotate(move)

    def add_shape_to_rows(self):
        self.rows.update_coords(self.shape.coords)

    def remove_full_rows(self):
        rows_dict = {}
        self.complete_row = []
        for coord in self.rows.coords:
            if coord[1] < 0:
                continue
            if coord[1] not in rows_dict.keys():
                rows_dict[coord[1]] = []
            rows_dict[coord[1]].append(coord)

        new_coords = [[x,-1] for x in RANGE_ROWS]
        skeys = sorted(rows_dict.keys())
        new_y = min(skeys)
        for y in skeys:
            if y < 0 or len(rows_dict[y]) < 10:
                for ii in range(len(rows_dict[y])):
                    rows_dict[y][ii][1] = new_y
                new_coords += rows_dict[y]
                new_y += 1
            else:
                self.complete_row += rows_dict[y]
                
                self.score += 1

        if len(self.complete_row) > 0:
            print("INFO: line(s) removed!")
            self.update_matrix()
            time.sleep(0.5)
            self.complete_row = []
            
    
        self.rows.coords = new_coords
    

    def run(self):
        key = "s"
        while key != "q":
            print("Score:", self.score,"Next:", self.next_letter)
            self.move_shape(key)    
            if self.check_shape_landed():
                self.add_shape_to_rows()
                self.remove_full_rows()
                self.get_new_shape()
                key = "e"
            
            self.update_matrix()
            
            if key != "w":
                if os.name == "nt":
                    key = getch2()
                else:
                    key = getch1()
        print("".join(["\n" for x in RANGE_ROWS]))

# Tests
def test(args):
    self = Tetris(args)
    self.run()
    
# Main Function
def main(args):
    if args.test == True:
        test(args)
    else:
        ch = Tetris(args)
        ch.run()

# Command-line Execution
if __name__=="__main__":
    #args
    parser = argparse.ArgumentParser(description="ch")
    parser.add_argument("-a", "--automate", action="store_true", help="automate")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose")
    parser.add_argument("-t", "--test", action="store_true", help="test")
    parser.add_argument("-s", "--shapes_type", default = "n", type=str, help="shapes_types. n:normal, a:additional,r:random")

    args = parser.parse_args()
    print(args)
    main(args)
    



    
