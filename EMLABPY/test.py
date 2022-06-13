people = {1: {'Name': 'John', 'Age': '27', 'Sex': 'Male'},
          2: {'Name': 'Marie', 'Age': '22', 'Sex': 'Female'},
          3: {'Name': 'sdf', 'Age': '22', 'Sex': 'Female'}}

# for p_id, p_info in people.items():
#     print("\nPerson ID:", p_id)
#
#     for key in p_info:
#         print(key + ':', p_info[key])

def inf():
    return    [d for d in people.values() if d['Age'] == "22"]


b = inf()
print(b)