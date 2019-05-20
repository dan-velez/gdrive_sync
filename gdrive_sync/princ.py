#!/usr/bin/python3
"""
princ.py - Wrapper function to print text in color.
"""

from colorama import Fore, Style

def princ(text, color):
    "Print text in color"
    color_code = ""
    if color == "green": color_code = Fore.GREEN
    elif color == "red": color_code = Fore.RED
    elif color == "blue": color_code = Fore.BLUE
    elif color == "cyan": color_code = Fore.CYAN
    print(color_code+text+Style.RESET_ALL)
