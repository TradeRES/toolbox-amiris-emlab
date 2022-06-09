class Employee:

    def __init__(self, name):
        self.name = name
        self.amount = None
        self.price = None

    def adding_new_attr(self, attr, value):
        setattr(self, attr, value)


a = Employee("Juan")
names = [("amount", "1"),("price", "2")]

# for i in names:
#     a.__setattr__(i[0], i[1])
for i in names:
    a.adding_new_attr(i[0], i[1])
print(a)