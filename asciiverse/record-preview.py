#!/usr/bin/env python3
"""Records asciiverse/froxcomposband.cast, the catalog preview, at 100x30
(hub/RECORDING.md). Runs the staged game (asciiverse/stage.sh first) with a
scratch HOME, so no save of yours is touched. It shows the title screen,
makes a character (Beginner mode, named Terminus), travels (`) to the
Weapon Smiths and looks at the wares, travels to the stairs and goes down,
then walks at the monsters of the first level and fights them (or picks
up what lies about), and saves
and quits (Ctrl-X). A simple pilot reads the screen through pyte. About
50 s. Needs pyte. Usage, from the repo root:
    sh asciiverse/build.sh && sh asciiverse/stage.sh
    python3 asciiverse/record-preview.py
TIMES=1 prints when each step happens; DUMP=1 also prints the screen."""
import os, pty, random, signal, struct, fcntl, select, shutil, tempfile, termios, time
import pyte

COLS, ROWS = 100, 30
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cast = os.path.join(root, "asciiverse", "froxcomposband.cast")
home = tempfile.mkdtemp()
env = dict(os.environ, HOME=home, TERM="xterm-256color", COLORTERM="truecolor",
           LANG="C.UTF-8")
env.pop("XDG_DATA_HOME", None)
random.seed(7)


# ncurses draws runs of one character with REP (CSI n b), which pyte lacks
class Screen(pyte.Screen):
    last = " "
    def draw(self, data):
        if data: self.last = data[-1]
        super().draw(data)
    def rep(self, n=1, *args, **kwargs):
        self.draw(self.last * max(n, 1))

class Stream(pyte.ByteStream):
    csi = dict(pyte.ByteStream.csi, b="rep")

screen = Screen(COLS, ROWS)
stream = Stream(screen)

pid, fd = pty.fork()
if pid == 0:
    os.chdir(os.path.join(root, "stage"))   # the recording shows no local paths
    os.execvpe("asciinema", ["asciinema", "rec", "--overwrite", "-q", "-i", "2",
        "--window-size", f"{COLS}x{ROWS}", "--capture-env", "TERM,COLORTERM,LANG",
        "-c", "./froxcomposband -uTerminus", cast], env)
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLS, 0, 0))

done = False
def alive():
    global done
    if not done and os.waitpid(pid, os.WNOHANG)[0]: done = True
    return not done

def stop_game():
    """Last resort: end the game under asciinema so the recording closes
    instead of running on (and writing to the cast) after we leave."""
    kids, todo = [], [pid]
    while todo:
        p = todo.pop()
        try: ch = open(f"/proc/{p}/task/{p}/children").read().split()
        except OSError: ch = []
        kids += ch; todo += [int(c) for c in ch]
    for k in reversed(kids):
        try: os.kill(int(k), signal.SIGTERM)
        except ProcessLookupError: pass

def pump(t):
    end = time.time() + t
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.01)
        if r:
            try: stream.feed(os.read(fd, 65536))
            except OSError: return

def text():
    return "\n".join(screen.display)

T0 = time.time()
def dump(tag):
    if os.environ.get("TIMES") or os.environ.get("DUMP"):
        print(f"[{time.time() - T0:5.1f}s] {tag}", flush=True)
    if os.environ.get("DUMP"):
        print("\n".join(l.rstrip() for l in screen.display), flush=True)

def key(k, wait=0.3):
    os.write(fd, k); pump(wait)

def wait_for(s, limit=10.0):
    end = time.time() + limit
    while time.time() < end and alive() and s not in text():
        pump(0.1)
    return s in text()

def more():
    """Acknowledge any -more- prompts."""
    for _ in range(10):
        if "-more-" not in text(): return
        key(b"\x1b", 0.3)

# The map is the left part of the screen below the message line; the
# sidebar starts at column 87 (LEVEL, EXP, ...).
MAP_X1, MAP_Y0, MAP_Y1 = 86, 1, ROWS - 1
STEP = {(-1, -1): b"7", (0, -1): b"8", (1, -1): b"9", (-1, 0): b"4",
        (1, 0): b"6", (-1, 1): b"1", (0, 1): b"2", (1, 1): b"3"}

def me():
    for y in range(MAP_Y0, MAP_Y1):
        x = screen.display[y].find("@", 0, MAP_X1)
        if x >= 0: return x, y
    return None

ITEMS = "|/\\!?=\"_-~([])}{$,"

def items():
    """Objects lying on the map."""
    return [(x, y) for y in range(MAP_Y0, MAP_Y1)
            for x in range(MAP_X1) if screen.display[y][x] in ITEMS]

def monsters():
    """Lone letters on the map: monsters (not words of a message)."""
    out = []
    for y in range(MAP_Y0, MAP_Y1):
        row = screen.display[y]
        for x in range(1, MAP_X1):
            if row[x].isalpha() and not row[x - 1].isalpha() and not row[x + 1].isalpha():
                out.append((x, y))
    return out

# title
wait_for("Press Any Other Key"); pump(3.0); dump("title")
key(b" ", 1.2)
key(b"\r", 1.0)                 # past the welcome
key(b"b", 1.0)                  # Beginner
pump(0.8); dump("character")     # named Terminus by -u, not after your login
key(b"\r", 1.5); dump("stats")  # stats as suggested
key(b"\r", 2.0); dump("town")   # Begin Play
key(b"\x1b", 0.5); key(b"\x1b", 1.0)   # past the welcome messages
key(b"`", 0.8); key(b"w", 0.3)  # travel to the Weapon Smiths
wait_for("Gold Remaining", 8.0); pump(4.0); dump("shop")
key(b" ", 2.5)                  # the next page of wares
key(b"\x1b", 1.0); more()
# travel to the stairs down (the cursor to them, then go); townspeople can
# stop a journey, so try the stairs and travel again until they work
for _ in range(6):
    key(b"`", 0.6); key(b">", 0.4); key(b" ", 0.3)
    pump(3.5); more(); dump("stairs?")
    key(b">", 1.2)
    if "really go into this dungeon" in text():
        key(b"y", 2.5)          # the town's stairs are a dungeon's entrance
        break
    more()
more(); dump("level 1")
end = time.time() + float(os.environ.get("PLAY_SECONDS", 17))
while time.time() < end and alive():
    if "[y/n]" in text():
        key(b"n", 0.4); continue
    if "Which stat do you want to raise" in text():
        key(b"a", 0.8); continue    # a level-up: Strength
    more()
    if "You die" in text() or "Killed by" in text(): break
    at = me()
    if not at:
        pump(0.3); continue
    near = monsters()
    if near:                    # walk at the nearest; walking into it attacks
        x, y = min(near, key=lambda m: max(abs(m[0] - at[0]), abs(m[1] - at[1])))
        d = ((x > at[0]) - (x < at[0]), (y > at[1]) - (y < at[1]))
    elif items():               # else pick up the nearest thing lying about
        x, y = min(items(), key=lambda m: max(abs(m[0] - at[0]), abs(m[1] - at[1])))
        d = ((x > at[0]) - (x < at[0]), (y > at[1]) - (y < at[1]))
        if d == (0, 0):
            key(b"g", 0.8); continue
    else:
        d = random.choice(list(STEP))
    key(STEP[d], 0.35)
pump(1.0); dump("end")
if alive():
    key(b"\x18", 2.0)           # Ctrl-X: save and quit
    more()
for _ in range(30):
    if not alive(): break
    pump(0.2)
if alive():
    stop_game(); pump(1.0)
shutil.rmtree(home, ignore_errors=True)
