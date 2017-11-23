import importlib
import inspect

class Loadable(object):
    """An object that can be written to and loaded from json config files
    """
    def __init__(self, name):
        """
        Args:
            name (str): Name of Loadable.
        """
        self.name = name

    def add(self, name, obj):
        """
        Add a parameters to the Loadable
        """
        setattr(self, name, obj)

    def to_json(self):
        """
        Return a json representation of the object that can be re-loaded.
        """
        json = {"name": self.name,
                "type": {"class": self.__class__.__name__,
                         "module": self.__module__},
                "properties": {}}
        for key in self.__dict__.keys():
            val = getattr(self, key)
            if hasattr(val, "to_json"):
                json["properties"][key] = val.to_json()
            else:
                json["properties"][key] = val
        return json
    
    @staticmethod
    def from_json(json):
        """
        Generate a class instance from a json representation of a Loadable
        """
        # For now this directs the base implemetation to the correct
        # class implementation
        module = importlib.import_module(json["type"]["module"])
        classname = json["type"]["class"]
        data = json["properties"]
        cls = getattr(module, classname)
        # Use inspect to get the signature
        sig = inspect.signature(cls)
        # Use the json data to bind arguments to the signature
        ba = sig.bind(*[data[key] for key in sig.parameters.keys()])
        # Use the bound args to instantiate the object
        return cls(*ba.args, **ba.kwargs)

    @staticmethod
    def from_json(json):
        # Get the class of the object
        module = importlib.import_module(json["type"]["module"])
        classname = json["type"]["class"]
        data = json["properties"]
        cls = getattr(module, classname)
        sig = inspect.signature(cls)
        # Make the object
        data = json["properties"] # can i do this w/o assuming keys?
        ba = sig.bind(*[data[key] for key in sig.parameters.keys()])
        obj = cls(*ba.args, **ba.kwargs)
        # Set parameters not set in init
        for key in data.keys():
            # If it has a "type" key, it's a loadable
            if hasattr(data[key], "keys"):
                if "type" in data[key].keys():
                    sub_obj = Loadable.from_json(data[key])
                    obj.add(sub_obj)
                else:
                    setattr(obj, key, data[key])
            else:
                setattr(obj, key, data[key])
        return obj

    


    
            
            
        
