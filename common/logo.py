import os
import sys

if sys.platform.startswith('win'):
    from common.colors import WinColors

    c = WinColors()
else:
    from common.colors import Colors

    c = Colors()


def logo():
    clear()
    print(f'''  
  /##      /##                                                            
 | ###    /###                                                            
 | ####  /####  /######   /######   /###### / ##   /##  /######  /##   /##
 | ## ##/## ## /##__  ## /##__  ## /##_____/| ##  | ## /##__  ##| ##  | ##
 | ##  ###| ##| ########| ##  \__/| ##      | ##  | ##| ##  \__/| ##  | ## {c.GREEN}
 | ##\  # | ##| ##_____/| ##      | ##      | ##  | ##| ##      | ##  | ##
 | ## \/  | ##|  #######| ##      |  #######|  ######/| ##      |  #######
 |__/     |__/ \_______/|__/       \_______/ \______/ |__/       \____  ##
                                                                 /##  | ##
                                                                 | ######/
                                                                 \______/ {c.END}
                 {c.BLUE} Version 2.0 {c.END}\n''')


def clear():
    if sys.platform.startswith('win'):
        os.system('cls')
    else:
        os.system('clear')
    print()
