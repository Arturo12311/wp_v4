# Import Ghidra modules
from ghidra.app.script import GhidraScript
from ghidra.program.model.listing import Program
from ghidra.program.model.address import Address
from ghidra.program.model.symbol import SymbolTable
from ghidra.program.model.mem import Memory

class MyGhidraScript(GhidraScript):

    def run(self):
        # This is the main entry point for the script
        print("Starting my Ghidra script...")

        # Get the current program
        program = getCurrentProgram()
        if program is None:
            print("No program loaded. Please load a program before running this script.")
            return

        # Get the memory of the program
        memory = program.getMemory()

        # Get the symbol table
        symbolTable = program.getSymbolTable()

        # Get the listing (contains instructions, data, etc.)
        listing = program.getListing()

        # Your analysis code goes here
        # For example, let's print the program name and its base address
        print("Program Name:", program.getName())
        print("Base Address:", program.getImageBase())

        print("Script completed.")

# Run the script
if __name__ == '__main__':
    MyGhidraScript().run()
