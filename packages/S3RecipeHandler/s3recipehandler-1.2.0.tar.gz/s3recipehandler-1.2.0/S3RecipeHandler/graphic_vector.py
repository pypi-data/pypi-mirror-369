import struct


class graphic_vector():
    def __init__(self, vector_bytes = None, vector_json = None):

        if vector_bytes != None:

            self.rotation = ((struct.unpack(">f",vector_bytes[0:4])[0])/6.3)*360 #makes it equal to 360.00 being a full rotation

            self.scale = struct.unpack(">f",vector_bytes[4:8])[0]
            self.x = struct.unpack(">f",vector_bytes[8:12])[0]
            self.y = struct.unpack(">f",vector_bytes[12:16])[0]

        elif vector_json != None:
            self.from_json(vector_json)
        
        else:
            self.rotation = 0.00
            self.scale = 5.00
            self.x = -0.25
            self.y = 0.25
        
    def get_bytes(self):
        vector_bytes = []

        vector_bytes.extend( struct.pack(">f", (self.rotation/360)*6.3) )
        vector_bytes.extend(struct.pack(">f", self.scale))
        vector_bytes.extend(struct.pack(">f", self.x))
        vector_bytes.extend(struct.pack(">f", self.y))

        return vector_bytes
    
    def to_json(self):
        data = {
            "rotation":self.rotation,
            "scale":self.scale,
            "x":self.x,
            "y":self.y
        }
        return data
    
    def from_json(self, json):

        self.rotation = float(json["rotation"])
        self.scale = float(json["scale"])
        self.x = float(json["x"])
        self.y = float(json["y"])