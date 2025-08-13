from .graphic_vector import graphic_vector


class graphic_vector_list():
    def __init__(self, vector_list_bytes = None, vector_list_json = None):
        self.list_order = ["shirt", "upper", "lower", "board", "hat"]
        self.list = {}

        if vector_list_bytes != None:
            for index, vector_name in enumerate(self.list_order):

                self.list[vector_name] = graphic_vector(vector_bytes=vector_list_bytes[(index)*0x10:(index+1)*0x10])
        elif vector_list_json != None:
            self.from_json(vector_list_json)
        
        else:
            # default constructer
            for vector_name in self.list_order:
                self.list[vector_name] = graphic_vector()

    
    def get_bytes(self):
        vector_bytes = []

        for vector_name in self.list_order:
            vector_bytes.extend(self.list[vector_name].get_bytes())
        
        return vector_bytes

    def from_json(self,json):
        for vector_name in self.list_order:
            self.list[vector_name] = graphic_vector(vector_json=json[vector_name])

    def to_json(self):
        data = {}
        for vector_name in self.list_order:
            data[vector_name] = self.list[vector_name].to_json()
        return data