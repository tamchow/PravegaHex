# PravegaHex
Hex Game for Pravega Biology

# Requirements

1. Python 3.5
2. PyGame (get it using `pip install pygame`)

# Installation

1. Ensure the `hex.py`, `cubicfive10.ttf` files and the `dna-icon.png` file are in the same folder.
 
 (you can choose to not use the icon file, in that case, comment out the line in `hex.py`'s `main` function which loads the icon)
 
2. `python hex.py` (assuming you have the environment variables correctly set up)

# Hacks

1. <kbd>L</kbd> & <kbd>R</kbd> enforce timeouts (hardcoded to 10 seconds here) on the players.
 
 This is just a proof-of-concept for the timer.
 
# Future Plans
 
 1. Migrate from hacky screen extension to a proper client-server architecture.
 
 2. Customizable player colors.
 
 3. Make the questions actually work, and put in some real questions.
 
 4. Last but not the least, migrate to Android by translating to Scala/Java as that is cheaper in terms of hardware costs.
 
 # Migration notice
 Future Plan No. 4 was completed - check the [final](https://github.com/tamchow/PravegaHex/tree/final) branch.
 This Python version (in `master`) is no longer maintained or developed.
