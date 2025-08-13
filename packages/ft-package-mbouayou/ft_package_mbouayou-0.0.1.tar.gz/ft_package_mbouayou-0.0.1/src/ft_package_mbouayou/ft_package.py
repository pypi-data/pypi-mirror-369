
def ft_function():
    """A simple function that prints a message."""
    print("This is a function from the ft_package_mbouayou package.")

def count_in_list(lst, value):
    """Counts the occurrences of 'value' in 'lst'."""
    if not isinstance(lst, list):
        raise TypeError("The first argument must be a list.")
    return lst.count(value)



