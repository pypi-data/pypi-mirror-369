import sys                                      # module sys to handle errors

# reading the items in a file
def read_file_items(filename):
    """
        Objective:
            Function to return a list of items from a given file.
    
        Args:
            filename (str): The path to the file containing shopping list items.

        Returns:
            list: A list of items read from the file, with whitespace removed and empty lines ignored.
    
        Raises:
            FileNotFoundError: If the specified file does not exist.
            Exception: For any other errors encountered while reading the file.
    """
    try:
        # Open the file and read its contents
        with open(filename, "r", encoding="utf-8") as file:
            
            # Read all lines, remove whitespace and ignore empty lines
            items = [line.strip() for line in file if line.strip()]
        
        return items
    
    # File not found
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.", file=sys.stderr)  # sys.stderr == print python error to standard error
        return None
    
    # Other exceptions
    except Exception as error_message:
        print(f"An error occurred while reading the file: {error_message}", file=sys.stderr) # sys.stderr == print python error to standard error
        return None