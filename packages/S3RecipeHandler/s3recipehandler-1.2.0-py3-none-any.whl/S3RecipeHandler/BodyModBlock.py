import struct
import json


class body_mod_blocks():
    def __init__(self, asset_bytes=None, Asset_json=None):

        if asset_bytes != None:

            self.skinniness =     struct.unpack(">f", asset_bytes[ 0+(4*0) : 0+(4*1)])[0]
            self.fatness =        struct.unpack(">f", asset_bytes[ 0+(4*1) : 0+(4*2)])[0]
            
            self.brow_rotation =  struct.unpack(">f", asset_bytes[ 0+(4*2) : 0+(4*3)])[0]
            self.brow_height =    struct.unpack(">f", asset_bytes[ 0+(4*3) : 0+(4*4)])[0]
            self.brow_profile =   struct.unpack(">f", asset_bytes[ 0+(4*4) : 0+(4*5)])[0]
            
            self.nose_curve =     struct.unpack(">f", asset_bytes[ 0+(4*5) : 0+(4*6)])[0]
            self.nose_width =     struct.unpack(">f", asset_bytes[ 0+(4*6) : 0+(4*7)])[0]
            self.nose_length =    struct.unpack(">f", asset_bytes[ 0+(4*7) : 0+(4*8)])[0]
            self.nose_height =    struct.unpack(">f", asset_bytes[ 0+(4*8) : 0+(4*9)])[0]
            
            self.mouth_width =    struct.unpack(">f", asset_bytes[ 0+(4*9) : 0+(4*10)])[0]
            self.mouth_smile =    struct.unpack(">f", asset_bytes[ 0+(4*10) : 0+(4*11)])[0]
            self.mouth_fullness = struct.unpack(">f", asset_bytes[ 0+(4*11) : 0+(4*12)])[0]
            
            self.UKNOWN_BLOCK =   struct.unpack(">f", asset_bytes[ 0+(4*12) : 0+(4*13)])[0]

            if self.UKNOWN_BLOCK != self.UKNOWN_BLOCK: # this is checking if the UKNOWN BLOCK is nan as json doesnt support it (this is the best way...python moment)
                self.UKNOWN_BLOCK = 0.25
            
            self.chin_length =    struct.unpack(">f", asset_bytes[ 0+(4*13) : 0+(4*14)])[0]
            self.jaw_definition = struct.unpack(">f", asset_bytes[ 0+(4*14) : 0+(4*15)])[0]
            self.jaw_roundness =  struct.unpack(">f", asset_bytes[ 0+(4*15) : 0+(4*16)])[0]
            self.eye_width =      struct.unpack(">f", asset_bytes[ 0+(4*16) : 0+(4*17)])[0]
            self.eye_height =     struct.unpack(">f", asset_bytes[ 0+(4*17) : 0+(4*18)])[0]
            self.eye_rotation =   struct.unpack(">f", asset_bytes[ 0+(4*18) : 0+(4*19)])[0]

        
        elif Asset_json != None:
            self.from_json(Asset_json)

        else:
            self.skinniness = 0.25
            self.fatness = 0.25
            self.brow_rotation = 0.25
            self.brow_height = 0.25
            self.brow_profile = 0.25
            self.nose_curve = 0.25
            self.nose_width = 0.25
            self.nose_length = 0.25
            self.nose_height = 0.25
            self.mouth_width = 0.25
            self.mouth_smile = 0.25
            self.mouth_fullness = 0.25
            self.UKNOWN_BLOCK = 0.25
            self.chin_length = 0.25
            self.jaw_definition = 0.25
            self.jaw_roundness = 0.25
            self.eye_width = 0.25
            self.eye_height = 0.25
            self.eye_rotation = 0.25

    def get_bytes(self):
        bodyModBlockBytes = []

        bodyModBlockBytes.extend(struct.pack(">f",self.skinniness))
        bodyModBlockBytes.extend(struct.pack(">f",self.fatness))
        bodyModBlockBytes.extend(struct.pack(">f",self.brow_rotation))
        bodyModBlockBytes.extend(struct.pack(">f",self.brow_height))
        bodyModBlockBytes.extend(struct.pack(">f",self.brow_profile))
        bodyModBlockBytes.extend(struct.pack(">f",self.nose_curve))
        bodyModBlockBytes.extend(struct.pack(">f",self.nose_width))
        bodyModBlockBytes.extend(struct.pack(">f",self.nose_length))
        bodyModBlockBytes.extend(struct.pack(">f",self.nose_height))
        bodyModBlockBytes.extend(struct.pack(">f",self.mouth_width))
        bodyModBlockBytes.extend(struct.pack(">f",self.mouth_smile))
        bodyModBlockBytes.extend(struct.pack(">f",self.mouth_fullness))
        bodyModBlockBytes.extend(struct.pack(">f",self.UKNOWN_BLOCK))
        bodyModBlockBytes.extend(struct.pack(">f",self.chin_length))
        bodyModBlockBytes.extend(struct.pack(">f",self.jaw_definition))
        bodyModBlockBytes.extend(struct.pack(">f",self.jaw_roundness))
        bodyModBlockBytes.extend(struct.pack(">f",self.eye_width))
        bodyModBlockBytes.extend(struct.pack(">f",self.eye_height))
        bodyModBlockBytes.extend(struct.pack(">f",self.eye_rotation))

        return bodyModBlockBytes

    def to_json(self):
        data = {
        "skinniness":self.skinniness,
        "fatness":self.fatness,
        "brow_rotation":self.brow_rotation,
        "brow_height":self.brow_height,
        "brow_profile":self.brow_profile,
        "nose_curve":self.nose_curve,
        "nose_width":self.nose_width,
        "nose_length":self.nose_length,
        "nose_height":self.nose_height,
        "mouth_width":self.mouth_width,
        "mouth_smile":self.mouth_smile,
        "mouth_fullness":self.mouth_fullness,
        "UKNOWN_BLOCK":self.UKNOWN_BLOCK,
        "chin_length":self.chin_length,
        "jaw_definition":self.jaw_definition,
        "jaw_roundness":self.jaw_roundness,
        "eye_width":self.eye_width,
        "eye_height":self.eye_height,
        "eye_rotation":self.eye_rotation 
        }

        return data

    def from_json(self,json):
        self.skinniness = float(json["skinniness"])
        self.fatness = float(json["fatness"])
        self.brow_rotation = float(json["brow_rotation"])
        self.brow_height = float(json["brow_height"])
        self.brow_profile = float(json["brow_profile"])
        self.nose_curve = float(json["nose_curve"])
        self.nose_width = float(json["nose_width"])
        self.nose_length = float(json["nose_length"])
        self.nose_height = float(json["nose_height"])
        self.mouth_width = float(json["mouth_width"])
        self.mouth_smile = float(json["mouth_smile"])
        self.mouth_fullness = float(json["mouth_fullness"])
        self.UKNOWN_BLOCK = float(json["UKNOWN_BLOCK"])
        self.chin_length = float(json["chin_length"])
        self.jaw_definition = float(json["jaw_definition"])
        self.jaw_roundness = float(json["jaw_roundness"])
        self.eye_width = float(json["eye_width"])
        self.eye_height = float(json["eye_height"])
        self.eye_rotation = float(json["eye_rotation"])
