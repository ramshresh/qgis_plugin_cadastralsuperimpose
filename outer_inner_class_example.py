class Outer(object):
    # Constructor method of outer class
    def __init__(self):  
        self.name = "Outer"
        self.inner =self.createInner()
        
    def get_outer_name(self):
        return self.name
    def set_outer_name(self, name):
        self.name = name
    def createInner(self):
        return Outer.Inner(self)

    class Inner(object):
        def __init__(self, outer_instance):
            self.outer_instance = outer_instance
            self.outer_instance.get_outer_name()
        
        def inner_method(self):
            self.outer_instance.set_outer_name("Outer-from-Inner")
o= Outer()
print (o)
print(o.inner)
print (o.name)
print (o.inner.inner_method())
print (o.name)
