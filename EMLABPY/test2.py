students = {
    'ID 1':    {'Name': 'Shaun', 'Age': 35, 'City': 'Delhi'},
    'ID 2':    {'Name': 'Ritika', 'Age': 31, 'City': 'Mumbai'},
    'ID 3':    {'Name': 'Smriti', 'Age': 33, 'City': 'Sydney'},
    'ID 4':    {'Name': 'Jacob', 'Age': 23, 'City': {'perm': 'Tokyo',
                                                     'current': 'London'}},
}
def nested_dict_pairs_iterator(dict_obj):
    ''' This function accepts a nested dictionary as argument
        and iterate over all values of nested dictionaries
    '''
    # Iterate over all key-value pairs of dict argument
    for key, value in dict_obj.items():
        # Check if value is of dict type
        if isinstance(value, dict):
            # If value is dict then iterate over all its values
            for pair in  nested_dict_pairs_iterator(value):
                yield (key, *pair)
        else:
            # If value is not dict type then yield the value
            yield (key, value)
#Loop through all key-value pairs of a nested dictionary
for pair in nested_dict_pairs_iterator(students):
    print(pair)