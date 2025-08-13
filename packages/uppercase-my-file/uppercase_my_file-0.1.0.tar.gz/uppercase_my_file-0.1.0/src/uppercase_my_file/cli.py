
import sys

def how_to_use():
    print("This is a simple command line program that converts all the text on your file to UPPERCASE.")
    print("How to use this program:")
    print("Run it using two filename. The first file is the file you want to convert to uppercase, and the second file is the output file where the result will be saved.")
    print("Example: python cli.py input.txt output.txt")
    print("Need help? Use --help option to see how to use this program.")

def start():
    args = sys.argv
    if len(args) != 3 or args[1] == "--help": # check if the number of arguments not equal to 3 or if the user asks for help
        how_to_use()                          # if so, print how to use the program by calling how_to_use function
        return
    
    input_file = args[1]  # the first argument is the input file
    output_file = args[2]  # the second argument is the output file
    #args[0] is the name of the script. 

    try:
        with open(input_file, 'r') as infile:  # open the input file in read mode, infile holds the opened file. 
            lines = infile.readlines() # read all lines from the input file and store them in a list called lines
    except FileNotFoundError: 
        print(f"Error: The file '{input_file}' was not found.") # if the file is not found, print this error message
        return
    except Exception as e:
        print(f"An error occurred while reading '{input_file}': {e}")
        return


    uppercase_lines = [line.upper() for line in lines]  # convert each line to uppercase and store the result in uppercase_lines

    try:
        with open(output_file, 'w') as outfile:  # open the output file in write mode, this is where the result will be saved
            outfile.writelines(uppercase_lines)  # write the uppercase lines to the output file
    except Exception as e:
        print(f"An error occurred while writing to '{output_file}': {e}")
        return
      

if __name__ == "__main__":
    start()