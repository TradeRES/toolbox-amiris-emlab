class Parent:
    def __init__(self, name, reps):
        self.name = name
        self.reps = reps

    def getName(self):
        return self.name


class Child(Parent):
    def __init__(self, reps):
        super().__init__("Child", reps)
        self.age = 2


    def getAge(self):
        return self.age


class Grandchild(Child):
    def __init__(self, reps):
        #Parent().__init__("Ingrid", reps)
        self.location = 3


    def getLocation(self):
        return self.location

#gc = Child("reps")
#print(gc.getName(), gc.getAge(), gc.reps)
gc = Grandchild("reps")
print(gc.getName(), gc.getAge(), gc.getLocation(), gc.reps)
