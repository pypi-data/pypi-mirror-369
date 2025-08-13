import sys                                      # module sys to handle errors

# print on the screen the alphabetical list
def print_items(items_counts):
    """
        Objective:
            Prints the sorted items with their counts to the console.
    
        Args:
            items_counts (list): A list of tuples containing item names and their counts.

        Returns:
            None: The function does not return anything, but prints to the console.
    
        Raises:
            Exception: For any errors encountered while printing the items.
    """
    try:

        # Print each item and its count to the console
        for item, count in items_counts:
            print(f"({count}x) {item}")


    # Exceptions
    except Exception as error_message:
        print(f"An error occurred while writing to the file: {error_message}", file=sys.stderr) # sys.stderr == print python error to standard error
