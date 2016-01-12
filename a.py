import curses
import sys
import csv

lines = []

col = []
width = [] 
enable = []
format = []

lnum = True
header = True

first_row = 1
first_col = 0

def main(stdscr, f):

    with open(f, 'rb') as f:
        lines[:] = list(csv.reader(f))

    col[:] = lines[0]
    enable[:] = [True] * len(col)
    set_widths()
    set_formats()

    curses.use_default_colors()

    # Clear screen
    stdscr.clear()

    while True :
        draw(stdscr)
        handler(stdscr)


def set_widths() :
    k = len(col)
    width[:] = [0] * k
    for line in lines:
        width[:] = [ max(width[i], len(line[i])) for i in range(k) ]
    

def set_formats() :
    True


def handler(stdscr) :
    global first_row
    global first_col
    global lnum
    j = stdscr.getkey()
    if j == 'q' : sys.exit()
    if j == '`' : lnum = not lnum
    if j == 'h' : header = not header
    if j == 'KEY_UP' : first_row -= 3
    if j == 'KEY_DOWN' : first_row += 3
    if j == 'KEY_LEFT' : first_col = max(first_col - 1, 0)
    if j == 'KEY_RIGHT' : first_col = min(first_col + 1, len(col))
    if j in [str(i) for i in range(10)] : 
        j = int(j) - 1 if j > 0 else 9
        enable[j] = not enable[j]

def draw(stdscr) :
    # header
    start = 5 if lnum else 0
    i,j = (0,start)
    maxy, maxx = stdscr.getmaxyx()
    maxy = min(maxy, len(lines) - first_row)
    n = len(col)

    stdscr.clear()

    j = start
    stdscr.vline(i, j, curses.ACS_VLINE, maxy)
    j+=1;

    if header :
        for k in range(first_col, n):
            if not enable[k]: continue
            if j + width[k] > maxx: break
            stdscr.addstr(i, j, col[k])
            j += width[k]
            stdscr.vline(i, j, curses.ACS_VLINE, maxy)
            j += 1
        i +=  1

        stdscr.hline(i, start, curses.ACS_HLINE, j-start)

        j = start
        stdscr.addch(i, j, curses.ACS_LTEE)
        for k in range(first_col, n):
            if not enable[k]: continue
            if j + width[k] > maxx: break
            j += width[k] + 1
            stdscr.addch(i, j, curses.ACS_PLUS)
        stdscr.addch(i, j, curses.ACS_RTEE)
        i += 1

    # lines

    curr = first_row
    while i < maxy and curr < len(lines) :
        j = 0
        if lnum : 
            stdscr.addstr(i, j, '%5d' % curr)
            j += 5
        for k in range(first_col,n):
            if not enable[k]: continue
            if j + width[k] > maxx: break
            j = j + 1
            stdscr.addstr(i, j, lines[curr][k])
            j += width[k]
        i += 1
        curr += 1


    stdscr.refresh()
    return True




if __name__ == '__main__' :
    curses.wrapper(main, sys.argv[1])
