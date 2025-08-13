import argparse                                                                 # module to deal with CLI in python
import sys                                                                      # module sys to handle errors
from final_project_shopping_list.src.read_file_items import read_file_items     # function to read items from a file
from final_project_shopping_list.src.count_sort_items import count_sort_items   # function to count and sort items from a list (collectd by a given file)
from final_project_shopping_list.src.write_items_file import write_items_file   # function to write items to a file
from final_project_shopping_list.src.print_items import print_items             # function to print items to the console


# function to handle command line arguments and organize a shopping list
def main():
    """
        Objective:
            Main function to handle command line arguments and organize a shopping list
              by removing duplicates and sorting items alphabetically.
    
        Args:
            None: The function does not take any arguments directly, but uses command line arguments.

        Returns:
            None: The function does not return anything, but performs file reading, sorting, and writing.
    
        Raises:
            argparse.ArgumentError: If the command line arguments are not provided correctly.
            Exception: For any errors encountered while reading, sorting, or writing the items.
    """
  
    try:

        # create an argument parser (CLI) to handle command line arguments
        # argparse is the standard Python module used to create command line interfaces (CLI)
        parser = argparse.ArgumentParser(
            description="Organize a shopping list by removing duplicates and sorting items alphabetically."
        )

        # add arguments to the parse
        parser.add_argument("input_file", help="Text file must containing shopping list items (one per line).")
        parser.add_argument("-o", "--output", help="Output file to save the organized list (optional).")

        # parse the command line arguments
        args = parser.parse_args()

        # Read items from the input file
        items = read_file_items(args.input_file)

        # If items is None, it means there was an error reading the file or the file was not provided
        if items is None:
            # Error already printed in read_items_from_file
            sys.exit(1)

        # receiving the organized items from the function count_sort_items
        organized_items = count_sort_items(items)

        # if args.output is provided, write the organized items to the output file
        if args.output:
            write_items_file(organized_items, args.output)

        # print the items to the console
        print_items(organized_items)

    # Exceptions
    except Exception as error_message:
        print(f"An error occurred during the process: {error_message}", file=sys.stderr) # sys.stderr == print python error to standard error


# Ensures that this code only runs when executed directly,
# and not when imported as a module.
if __name__ == "__main__":
    main()


