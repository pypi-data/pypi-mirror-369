import os
import time
import operator
from datetime import datetime
from rich_gradient.text import Text as GradientText
from typing import List, Optional, Tuple, Union
from art import text2art
from rich.console import Console, Group
from rich.table import Table
from rich.progress import Progress, track
from rich.live import Live
from rich.panel import Panel
from rich.measure import Measurement
from rich.align import Align
from rich.text import Text
from rich.layout import Layout
from rich import print
from pyfiglet import CharNotPrinted, Figlet
from rich.padding import Padding

console = Console()

version = "0.3.2"

###########
#  INPUT  #
# HANDLER #
###########

# switched from `keyboard` to `curses` for input — no admin/root needed.
# input thread ONLY reads keys and updates globals; it NEVER draws.
# this avoids flicker and conflicts with Rich's Live(screen=True).

space_pressed = False
g_pressed = False
selected_index = 0

options = ["Stopwatch", "Timer", "Profile", "Settings"]

if os.name == "nt":
    import msvcrt
    def get_key_nonblocking():
        if msvcrt.kbhit():
            return msvcrt.getch().decode("utf-8")
        return None
else:
    import termios
    import tty
    import select
    def get_key_nonblocking():
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        if dr:
            return sys.stdin.read(1)
        return None

def input_handler():
    global space_pressed
    global g_pressed
    global selected_index

    key = get_key_nonblocking()
    if not key:
        return

    if key == " ":
        space_pressed = True
    elif key == "g":
        g_pressed = True
    elif key in ("j", "\x1b[B"):
        selected_index = (selected_index + 1) % len(options)
    elif key in ("k", "\x1b[A"):
        selected_index = (selected_index - 1) % len(options)
    # add more hotkeys here if needed


##########################
#  ASCII TEXT GENERATOR  #
# USED FOR DRAW FUNCTION #
##########################

def asciiTextGenerator(
    text: str,
    font: str = "c1",
    color: str = "cyan",
    use_text2art: bool = True,
    align: bool = True,
    gradient: str = None
):
    if use_text2art == True:
        asciiText = text2art(text, font=font)
    else:
        figlet = Figlet(font='univers')
        asciiText = figlet.renderText(text)

    if gradient:
        gradient_text = GradientText(
            asciiText,
            colors=["#008dff", "#ffffff"],
            rainbow=False
        )
        renderedText = gradient_text
        FinalText = Align.center(renderedText, vertical="middle", height=console.height)
        if align:
            return FinalText
        else:
            return renderedText
    else:
        # Use regular Rich Text for solid colors
        from rich.text import Text as RichText
        renderedText = RichText(asciiText, style=color)
        FinalText = Align.center(renderedText, vertical="middle", height=console.height)
        if align:
            return FinalText
        else:
            return renderedText

#################
# DRAW FUNCTION #
#################

def draw(
    text: str,
    font: str = "c1",
    color: str = "cyan",
    use_panel: bool = False,
    use_text2art: bool = True,
    sleep_time: float = 1.0,
    live_context=None,
    message: Optional[str] = None,
) -> None:
    FinalText = asciiTextGenerator(text, font, color, use_text2art)

    if message:
        FinalText = asciiTextGenerator(text, font, color, use_text2art, align=False)
        message_text = Text(message, style="cyan")
        message_text.align(
            "center",
            Measurement.get(console, console.options, FinalText).normalize().maximum,
        )
        # NOTE: this mirrors your original behavior; not touching to avoid breaking anything
        display_text = Text.append(FinalText, message_text)
        FinalText = Align.center(display_text, vertical="middle", height=console.height)

    if use_panel == False:
        try:
            if live_context:
                live_context.update(FinalText)
                time.sleep(sleep_time)
            else:
                with Live(FinalText, refresh_per_second=4, screen=True) as live:
                    pass
        except Exception as e:
            print(f"Error: {e}")
            print("kod yarrağı yemiş durumda -ruhlar aleminden ferruh")
    else:
        print("sonra")

#########
# MODES #
#########

def stopwatch():
    global g_pressed
    messagestate = True
    console.clear()
    start_time = time.time()
    try:
        with Live(screen=True, refresh_per_second=4) as live:
            while True:
                input_handler()
                elapsed = int(time.time() - start_time)
                minutes = elapsed // 60
                seconds = elapsed % 60
                time_str = f"{minutes:02}:{seconds:02}"

                if g_pressed:
                    g_pressed = False
                    messagestate = not messagestate
                    
                if messagestate:
                    draw(
                        text=time_str,
                        message="'h' to view help menu // 'g' to hide this",
                        color="cyan",
                        sleep_time=0.25,
                        live_context=live
                    )
                else:
                    draw(
                        text=time_str,
                        color="cyan",
                        sleep_time=0.25,
                        live_context=live
                    )

    except KeyboardInterrupt:
        console.clear()
        with Live(screen=True, refresh_per_second=4) as live:
            draw(
                text="STOPPED",
                color="red",
                sleep_time=3
            )
        time.sleep(3)
        main()

def timer(input_time):
    console.clear()
    start_time = time.time()
    total_time = input_time
    remaining_time = total_time
    try:
        with Live(screen=True, refresh_per_second=4) as live:
            while remaining_time >= 0:
                elapsed = int(time.time() - start_time)
                remaining_time = int(total_time - elapsed)
                minutes = remaining_time // 60
                seconds = remaining_time % 60
                time_str = f"{minutes:02}:{seconds:02}"

                draw(
                    text=time_str,
                    color="cyan",
                    sleep_time=0.25,
                    live_context=live,
                )

            draw(
                text="TIMER COMPLETE",
                color="red",
                sleep_time=3
            )
            main()
    except KeyboardInterrupt:
        console.clear()
        draw(
            text="STOPPED",
            color="red",
            sleep_time=3
        )
        time.sleep(3)
        main()

#################
# MENU FUNCTION #
#################

def menu():
    global space_pressed, selected_index
    layout = Layout()
    layout.split_column(
        Layout(name="header"),
        Layout(name="upper"),
        Layout(name="lower")
    )
    layout["header"].split_row(
        Layout(name="UpperLeft"),
        Layout(name="UpperCenter"),
        Layout(name="UpperRight")
    )
    layout["lower"].split_row(Layout(name="left"), Layout(name="right"))

    layout["header"].size = 3
    layout["UpperCenter"].update(
        Align.center(GradientText("studr", colors=["#008dff", "#80a5d0"]), style="bold", vertical="middle")
    )
    layout["UpperLeft"].update(
        Align.center(version, style="white bold", vertical="middle")
    )

    def render_options():
        global space_pressed, selected_index
        text = Text()
        for i, opt in enumerate(options):
            prefix = f"{i+1} - "
            if i == selected_index:
                text.append(prefix, style="black on white bold")
                text.append(opt, style="black on white bold")
            else:
                text.append(prefix, style="white bold")
                text.append(opt, style="cyan bold")
            text.append("\n")
        return Align.center(text, vertical="middle")

    with Live(layout, refresh_per_second=16, screen=True):
        while True:
            input_handler()
            timestr = datetime.now().ctime().replace(":", "[blink]:[/]")
            layout["UpperRight"].update(
                Align.center(
                    GradientText(timestr, colors=["#ffffff", "#ffffff"]),
                    style="bold", vertical="middle"
                )
            )
            layout["upper"].update(render_options())
            time.sleep(0.05)

            # read by input thread; we just react to the flag here
            if space_pressed:
                space_pressed = False
                return

def run_selection(index):
    time.sleep(0.1)
    console.clear()
    if index == 0:
        stopwatch()
    elif index == 1:
        timer(10)
    elif index == 2:
        print("Opening Profile...")
        time.sleep(1)
    elif index == 3:
        print("Opening Settings...")
        time.sleep(1)

#################
# MAIN FUNCTION #
#################

def main():
    # menu waits until space is pressed (set by input thread)
    console.clear()
    menu()
    run_selection(selected_index)

if __name__ == "__main__":
    main()
