#!C:\Program Files\Python312\python
import random
import copy
import argparse
import time
import os
import sys
from datetime import datetime
import sys
import termios
import tty

########### UTILS ##################

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

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
# Helper Classes
REL_COORD = {
    "I":[[ 0,1], [0,0], [0,-1], [ 0,-2]],
    "J":[[ 0,1], [0,0], [0,-1], [-1,-1]],
    "L":[[ 0,1], [0,0], [0,-1], [ 1,-1]],
    "S":[[-1,0], [0,0], [0, 1], [ 1, 1]],
    "Z":[[-1,1], [0,0], [0, 1], [ 1, 0]],
    "O":[[ 1,0], [0,0], [0, 1], [ 1, 1]],
    "T":[[-1,0], [0,0], [1, 0], [ 0, 1]],
}
CARD = {
    "n": [0,1], "s": [0, -1],"e": [1,0], "w": [-1,0],
}
class Tetrimino(object):

    def __init__(self, rel_coords):
        self.rel_coords = rel_coords
        self.coords = copy.deepcopy(rel_coords)
        self.ctr = [5,16]
        self.update_coords()

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

TETRIMINO_I = Tetrimino(REL_COORD["I"])
TETRIMINO_L = Tetrimino(REL_COORD["L"])
TETRIMINO_J = Tetrimino(REL_COORD["J"])
TETRIMINO_S = Tetrimino(REL_COORD["S"])
TETRIMINO_Z = Tetrimino(REL_COORD["Z"])
TETRIMINO_O = Tetrimino(REL_COORD["O"])
TETRIMINO_T = Tetrimino(REL_COORD["T"])

LTTR = "ILJSZOT"

# Constants
OUTPUT = open("sample.txt").readlines()
SPACE = " "
ROW = [" ", " "," "," "," "," "," "," "," "," ",]
N_SPACES = len(ROW)
RANGE_SPACES = range(N_SPACES)

BLOCK = "O"
N_ROWS = 20
MATRIX = [copy.deepcopy(ROW) for x in range(N_ROWS)]

RANGE_ROWS = range(N_ROWS)

KEYS_TRANSLATIONS = {
    "a": "w",
    "s": "s",
    "d": "e",
    "w": "n",
}

KEYS_ROTATIONS = {
    "p": "cw",
    "l": "ccw"
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
        self.updated = False

    def update_coords(self, new_coords):
        self.coords += new_coords


######################################## CLASSES  ########################################
class Tetris(object):
    def __init__(self, args):
        self.automate = args.automate
        self.verbose = args.verbose
        self.matrix = copy.deepcopy(MATRIX)
        self.rows = MatrixRows()
        self.get_new_shape()
        self.update_matrix()

    def print_matrix(self):
        #os.system("cls" if os.name == "nt" else "clear")
        print(" ----------")
        for y in range(N_ROWS):
            row_str = "".join(self.matrix[N_ROWS - 1 - y])
            row_display = "|" + row_str + "|"
            print(row_display)
        print(" ----------")

    def check_shape_landed(self):
        for rc in self.rows.coords:
            for tc in self.shape.coords:
                if tc[0] == rc[0] and tc[1] == rc[1]:
                    self.move_shape("w")
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
                self.matrix[y][x] = "X"
            

        self.print_matrix()

    def get_new_shape(self):
        self.next_letter = random.choice(LTTR)
        print("INFO. ltr:", self.next_letter)
        self.shape = Tetrimino(copy.deepcopy(REL_COORD[self.next_letter]))

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
            
        self.rows.coords = new_coords
    

    def run(self):
        key = "s"
        while key != "q":
            self.move_shape(key)     
            if self.check_shape_landed():
                self.add_shape_to_rows()
                self.remove_full_rows()
                self.get_new_shape()
            self.update_matrix()
            key = getch()

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

    args = parser.parse_args()
    print(args)
    main(args)
    



    
