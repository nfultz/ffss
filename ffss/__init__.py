import curses
import sys
import csv
import re
import os
from decimal import Decimal

lines = []

col = []
orig_width = []
width = []
enable = []
last = []
format = []

lnum = True
header = True

first_row = 1
first_col = 0

def getWidth(k):
    return width[k] if format[k][1] else orig_width[k]

def tuptoString(s, left=5, right=2) :
    x = Decimal(s).as_tuple()
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

def main(stdscr):
    
    if "DIALECT" in os.environ:
        dialect = eval(os.environ["DIALECT"])
    else:
        dialect = csv.excel

    if len(sys.argv) > 1 :
        with open(sys.argv[1]) as f:
            lines[:] = list(csv.reader(f, dialect))
    else :
        lines[:] = list(csv.reader(sys.stdin, dialect))
        tty = open('/dev/tty', 'r')
        os.dup2(tty.fileno(), sys.stdin.fileno())

    col[:] = lines[0]
    enable[:] = [True] * len(col)
    orig_width[:] = map(lambda col: reduce(max, [len(s) for s in col]), zip(*lines))
    format[:] = [(lambda x:x) if w < 20 else (lambda x: x[:20]) for w in orig_width]
    width[:] = map(min, orig_width, [20]*len(col))

    irxp = re.compile('^-?[0-9]+$')
    frxp = re.compile('^-?[0-9]*[.]?[0-9]*$')
    for i in range(len(col)):
        if all(irxp.match(x[i]) for x in lines[1:]):
            format[i] = (lambda f: (lambda x: f % int(x)) )('%%%dd' % width[i])
        elif all(frxp.match(x[i]) for x in lines[1:]):
            digits = [Decimal(line[i]).as_tuple() for line in lines[1:]]
            digits = reduce(digitReducer, digits, [0,0])
            digits[0] = max(digits[0], len(lines[0][i]) - digits[1] - 1)
            width[i] = digits[0] + digits[1] + 1
            format[i] = (lambda d0, d1: lambda x: tuptoString(x, d0, d1))(digits[0], digits[1])
#            for line in lines[1:]: line[i] = tuptoString(line[i], digits[0], digits[1])

    format[:] = [(f,True) for f in format]

    curses.use_default_colors()

    # Clear screen
    stdscr.clear()

    while True :
        draw(stdscr)
        handler(stdscr)



def scroll(delta) :
    global first_row
    n = len(lines)-1
    first_row = max(-n, min(n, first_row + delta))

def pan(delta, d=1) :
    global first_col
    while delta > 0:
        if first_col + d not in xrange(len(col)) : return
        first_col += d
        if enable[first_col]: delta -= 1

#    first_col = max(0, min(len(col)-1, first_col + delta))


def handler(stdscr) :
    global first_row
    global first_col
    global lnum
    global header

    i = 0
    j = stdscr.getkey()

    if j == '.' : i,j = last
    if j == 'Z' : sys.exit()
    if j == '`' : lnum = not lnum
    if j == '~' : header = not header
    if j == 'X' : enable[:] = [True] * len(col)
    if j == 'KEY_UP' : scroll(-15)
    if j == 'KEY_DOWN' : scroll(15)
    if j == 'KEY_LEFT' : pan(5, -1)
    if j == 'KEY_RIGHT' : pan(5, 1)
    if j == ' ' : scroll(stdscr.getmaxyx()[0] - 2* header)

    while j in [str(x) for x in range(10)] :
        i = i * 10 + int(str(j))
        stdscr.addstr(0, 0, str(i))
        j = stdscr.getkey()

    last[:] = (i,j)

    if j == 'x' :
        i = i - 1 if i > 0 else first_col
        enable[i] = not enable[i]
        while not enable[first_col] or first_col == len(col) : pan(1)

    if i == 0 : i = 1

    if j == 'g' : first_row = i
    if j == 'G' : first_row = len(lines) - (stdscr.getmaxyx()[0] - 2*header)
    if j == 'h' : pan(i,-1)
    if j == 'l' : pan(i,1)
    if j == 'k' : scroll(-i)
    if j == 'j' : scroll(i)



def draw(stdscr) :
    # header
    start = 5 if lnum else 0
    endln = 3 if header else 0
    i,j = (0,start)
    maxy, maxx = stdscr.getmaxyx()
    endln = min(maxy, len(lines) - first_row + endln)
    n = len(col)

    stdscr.clear()

    if lnum or header :
        j = start
        stdscr.vline(i, j, curses.ACS_VLINE, endln)
        j+=1;

    if header :
        for k in range(first_col, n):
            if not enable[k]: continue
            if j + getWidth(k) > maxx: break
            stdscr.addstr(i, j, col[k] if first_row % 2 else str(k+1))
            j += getWidth(k)
            stdscr.vline(i, j, curses.ACS_VLINE, endln)
            j += 1
        i +=  1

        stdscr.hline(i, start, curses.ACS_HLINE, j-start)

        j = start
        stdscr.addch(i, j, curses.ACS_LTEE)
        for k in range(first_col, n):
            if not enable[k]: continue
            if j + getWidth(k) > maxx: break
            j += getWidth(k) + 1
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
            if j + getWidth(k) > maxx: break
            j = j + 1
            t = lines[curr][k]
            if curr != 0 and format[k][1] :
                t = format[k][0](lines[curr][k])
#            stdscr.addstr(i, j, format[k] % lines[curr][k])
            stdscr.addstr(i, j, t)
#            stdscr.addstr(i, j, lines[curr][k])
            j += getWidth(k)
        i += 1
        curr += 1

    #footer
    if header and i < maxy :
        stdscr.hline(i, start, curses.ACS_HLINE, j-start)
        j = start
        stdscr.addch(i, j, curses.ACS_LLCORNER)
        for k in range(first_col, n):
            if not enable[k]: continue
            if j + getWidth(k) > maxx: break
            j += getWidth(k) + 1
            stdscr.addch(i, j, curses.ACS_BTEE)
        stdscr.addch(i, j, curses.ACS_LRCORNER)

    stdscr.refresh()
    return True

