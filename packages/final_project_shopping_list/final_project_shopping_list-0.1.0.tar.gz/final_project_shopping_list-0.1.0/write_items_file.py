import sys                                      # module sys to handle errors

# function to write items to a file
def write_items_file(items_counts, output_filename):
    """
        Objective:
            Writes the sorted items with their counts to a specified output file.
    
        Args:
            items_counts (list): A list of tuples containing item names and their counts.
            output_filename (str): The path to the output file where the organized list will be saved.

        Returns:
            None: The function does not return anything, but writes to the specified file.
    
        Raises:
            Exception: For any errors encountered while writing to the file.
    """
    try:
        # Open the output file in write mode
        # 'w' mode will create the file if it does not exist or overwrite it if it does
        # 'encoding="utf-8"' ensures that the file is written in UTF-8
        with open(output_filename, "w", encoding="utf-8") as file:

            # read each item and its count from the list items_counts
            for item, count in items_counts:

                # If the count is greater than 1, write it in the format "item (count)"
                # \n to add a new line after each item
                if count > 1:
                    file.write(f"{item} ({count}x)\n")

                # If the count is 1, write it as just the item name
                # \n to add a new line after each item
                else:
                    file.write(f"{item}\n")

        # Print a message indicating the output file has been saved
        print(f"Organized list saved to: {output_filename}")

    # Exceptions
    except Exception as error_message:
        print(f"An error occurred while writing to the file: {error_message}", file=sys.stderr) # sys.stderr == print python error to standard error

