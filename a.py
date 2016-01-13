import curses
import sys
import csv

from decimal import Decimal

lines = []

col = []
width = [] 
enable = []

lnum = True
header = True

first_row = 1
first_col = 0


def tuptoString(x, left=5, right=2) :
    nleft = len(x.digits) + x.exponent
    dleft = left - nleft - x.sign
    dright = right + x.exponent
    return '%s%s%s.%s%s' % (
                " " * (dleft) , 
                ["","-"][x.sign],
                "".join(map(str, x.digits[:nleft])),
                "".join(map(str, x.digits[nleft:])),
                " " * (dright) , 
    )

def digitReducer(x,y):
    return [max(x[0], len(y.digits)+y.exponent+y.sign), max(x[1], -y.exponent)]

def main(stdscr, f):

    with open(f, 'rb') as f:
        lines[:] = list(csv.reader(f))

    col[:] = lines[0]
    enable[:] = [True] * len(col)
    set_widths()

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
    



def handler(stdscr) :
    global first_row
    global first_col
    global lnum
    global header
    j = stdscr.getkey()
    if j == 'q' : sys.exit()
    if j == '`' : lnum = not lnum
    if j == '~' : header = not header
    if j == 'KEY_UP' : first_row -= 3
    if j == 'KEY_DOWN' : first_row += 3
    if j == 'KEY_LEFT' : first_col = max(first_col - 1, 0)
    if j == 'KEY_RIGHT' : first_col = min(first_col + 1, len(col))

    i = 0
    while j in [str(x) for x in range(10)] : 
        i = i * 10 + int(str(j))
        stdscr.addstr(0, 0, str(i))
        j = stdscr.getkey()

    if j == 'g':
        first_row = i

    i = i - 1

    if j == 's' :
        for line in lines[1:]: line[i] = line[i].strip()
#        width[i] = reduce(max, [len(line[i]) for line in lines])
    if j == 'i' :
        for line in lines[1:]: line[i] = ('%%%dd' % width[i]) % int(line[i])
    if j == 'f' :
        for line in lines[1:]: line[i] = Decimal(line[i]).as_tuple()
        digits = reduce(digitReducer, [ line[i] for line in lines[1:] ], (0,0))               
        digits[0] = max(digits[0], len(lines[0][i]) - digits[1] - 1)
        width[i] = digits[0] + digits[1] + 1
        for line in lines[1:]: line[i] = tuptoString(line[i], digits[0], digits[1])
    if j == 'x' :
        enable[i] = not enable[i]

def draw(stdscr) :
    # header
    start = 5 if lnum else 0
    i,j = (0,start)
    maxy, maxx = stdscr.getmaxyx()
    maxy = min(maxy, len(lines) - first_row)
    n = len(col)

    stdscr.clear()

    if lnum or header :
        j = start
        stdscr.vline(i, j, curses.ACS_VLINE, maxy)
        j+=1;

    if header :
        for k in range(first_col, n):
            if not enable[k]: continue
            if j + width[k] > maxx: break
            stdscr.addstr(i, j, col[k] if first_row % 2 else str(k+1))
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
#            stdscr.addstr(i, j, format[k] % lines[curr][k])
            stdscr.addstr(i, j, lines[curr][k])
            j += width[k]
        i += 1
        curr += 1

    #footer
    if header and curr < len(lines) :
        stdscr.hline(i, start, curses.ACS_HLINE, j-start)
        j = start
        stdscr.addch(i, j, curses.ACS_LLCORNER)
        for k in range(first_col, n):
            if not enable[k]: continue
            if j + width[k] > maxx: break
            j += width[k] + 1
            stdscr.addch(i, j, curses.ACS_BTEE)
        stdscr.addch(i, j, curses.ACS_LRCORNER)



    stdscr.refresh()
    return True




if __name__ == '__main__' :
    curses.wrapper(main, sys.argv[1])
