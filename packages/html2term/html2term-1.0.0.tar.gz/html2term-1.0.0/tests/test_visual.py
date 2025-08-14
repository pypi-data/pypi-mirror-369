from html2term.core import printc

def print_header(title: str):
    """Prints a styled header to the console."""
    printc(f"\n<b><yellow>--- {title.upper()} ---</yellow></b>")

def main():
    """Runs the visual demonstration."""
    printc("<b><green>html2term Visual Test Suite</green></b>")
    printc("<i>Running a visual demonstration of all features...</i>")

    print_header("Basic Text Styles")
    printc("This is default text.")
    printc("<b>This text should be bold.</b>")
    printc("<strong>This text should also be bold (strong tag).</strong>")
    printc("<i>This text should be italic.</i>")
    printc("<em>This text should also be italic (em tag).</em>")
    printc("<u>This text should be underlined.</u>")
    printc("<strike>This text should be struck through.</strike>")
    printc("<blink>This text should be blinking (if supported by your terminal).</blink>")

    print_header("16 Standard Colors (Foreground)")
    printc("<black>Black</black> <red>Red</red> <green>Green</green> <yellow>Yellow</yellow> "
           "<blue>Blue</blue> <magenta>Magenta</magenta> <cyan>Cyan</cyan> <white>White</white>")

    print_header("16 Standard Colors (Background)")
    printc("<bg-black> Black BG </bg-black> <bg-red> Red BG </bg-red> <bg-green> Green BG </bg-green> "
           "<bg-yellow> Yellow BG </bg-yellow>")
    printc("<bg-blue> Blue BG </bg-blue> <bg-magenta> Magenta BG </bg-magenta> "
           "<bg-cyan> Cyan BG </bg-cyan> <bg-white><black> White BG </black></bg-white>")

    print_header("Truecolor (Hex) Support")
    printc("You can use any hex code, like <#ff00ff>magenta</#ff00ff> or <#00ffff>cyan</#00ffff>.")
    printc("Backgrounds work too: <bg-#5f00d7>  </bg-#5f00d7> <bg-#ff8700>  </bg-#ff8700> <bg-#00afaf>  </bg-#00afaf>")
    
    printc("\n<i>Foreground Gradient (Red to Blue):</i>")
    for i in range(40):
        r = int(255 - (i * 255 / 39))
        b = int(i * 255 / 39)
        hex_code = f"#{r:02x}00{b:02x}"
        printc(f"<{hex_code}>█</{hex_code}>", end="")
    
    printc("\n<i>Background Gradient (Yellow to Cyan):</i>")
    for i in range(40):
        r = int(255 - (i * 255 / 39))
        g = 255
        b = int(i * 255 / 39)
        hex_code = f"#{r:02x}{g:02x}{b:02x}"
        printc(f"<bg-{hex_code}> </bg-{hex_code}>", end="")
    print()

    print_header("Layout Tags")
    printc("This is the first line.<br/>This is the second line (after a br tag).")
    printc("Column 1<tab/>Column 2<tab/>Column 3 (separated by tab tags)")

    print_header("Nested Tag Support")
    printc("You can <b><blue>nest styles</blue></b> easily.")
    printc("<u>This is underlined, but <i>this part is also italic</i>, and this is back to just underlined.</u>")
    printc("<bg-cyan><black><b>This is bold black text on a cyan background.</b></black></bg-cyan>")
    printc("<b><#ff7f50>This is bold and coral colored.</#ff7f50></b>")
    
    print_header("Graceful Handling of Malformed Tags")
    printc("An <unclosed-tag> is treated as literal text.")
    printc("A </mismatched-closing-tag> is also literal text.")
    printc("An invalid hex code like <#12345>invalid</#12345> is also treated as literal text.")

    print_header("Putting It All Together. EXAMPLE:")
    printc("<b><green>SUCCESS:</green></b> Package build completed.<br/>"
           "<tab/><i>Log file written to <#808080>/var/logs/app.log</#808080></i><br/>"
           "<tab/><b><red>WARNING:</red></b> <strike>1 deprecation</strike> <u>0 deprecations</u> found.")

if __name__ == "__main__":
    main()
