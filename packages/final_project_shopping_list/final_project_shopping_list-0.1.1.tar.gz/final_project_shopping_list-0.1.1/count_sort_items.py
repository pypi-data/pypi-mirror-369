
# function to count and sort items from a list (collectd by a given file)
def count_sort_items(items):
    """
        Objective:
            Counts the occurrences of each item in the list.
    
        Args:
            items (list): A list of items to be counted and sorted.

        Returns:
            list: A list of tuples sorted alphabetically, where each tuple contains (item_name, count).
    
        Raises:
            Exception: For any other errors encountered while reading the file.
    """
    try:    
        # Variable to hold the count of each item
        item_count = {}

        # Count occurrences of each item
        for item in items:
            # Validation if the item exists in the list item_count
            if item in item_count:
                item_count[item] += 1

            # If the item does not exist in the list item_count, add it with count 1
            else:
                item_count[item] = 1

        # Sort items alphabetically ignoring uppercase and lowercase
        # key is a function of the sort method that specifies the sorting criteria
        # lambda x: x[0] means we are sorting by the first element of each tuple (the item name)
        # x in this case is each tuple in item_count.items()
        sorted_items = sorted(item_count.items(), key=lambda x: x[0].lower())
        
        return sorted_items

    # Exceptions
    except Exception as error_message:
        print(f"An error occurred while reading the list: {error_message}")
        return None

