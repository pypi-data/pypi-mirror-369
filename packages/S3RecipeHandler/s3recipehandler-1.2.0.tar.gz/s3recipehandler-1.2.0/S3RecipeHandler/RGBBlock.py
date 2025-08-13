import struct
from .S3RGB import S3RGB

class Asset:
    def __init__(self):
        self.AssetID = bytearray(8)
        self.Models = [Model()]

class Model:
    def __init__(self):
        self.MaterialID = bytearray(8)

class RGBBlock:
    def __init__(self, BlockBytes:bytes = None, Block_json = None, RGB = None, Asset = None):

        if BlockBytes != None:
            self.RGB = S3RGB()
            self.AssetID = bytearray(8)
            self.MaterialID = bytearray(8)

            # Red
            RBytes = BlockBytes[4:8]
            self.RGB.r = struct.unpack('>f', RBytes)[0]
            # Green
            GBytes = BlockBytes[8:12]
            self.RGB.g = struct.unpack('>f', GBytes)[0]
            # Blue
            BBytes = BlockBytes[12:16]
            self.RGB.b = struct.unpack('>f', BBytes)[0]

            # Store ArenaID and Material ID that the RGB takes effect on
            self.AssetID = BlockBytes[0x1C:0x1C+8]
            self.MaterialID = BlockBytes[0x24:0x24+8]

        elif Block_json != None:
            self.from_json(Block_json)
        
        elif Asset != None:
            self.RGB = RGB
            self.AssetID = Asset.AssetID
            self.MaterialID = Asset.Models[0].MaterialID
        else:
            pass

    def get_bytes(self, index):
        RGBBlockBytes = bytearray()

        RGBBlockBytes.extend(bytearray([0, 0, 0, index]))  # RGB Block Index
        RGBBlockBytes.extend(struct.pack('>f', self.RGB.r))  # Red
        RGBBlockBytes.extend(struct.pack('>f', self.RGB.g))  # Green
        RGBBlockBytes.extend(struct.pack('>f', self.RGB.b))  # Blue
        RGBBlockBytes.extend(struct.pack('>f', self.RGB.r))  # Red
        RGBBlockBytes.extend(struct.pack('>f', self.RGB.g))  # Green
        RGBBlockBytes.extend(struct.pack('>f', self.RGB.b))  # Blue
        RGBBlockBytes.extend(self.AssetID)
        RGBBlockBytes.extend(self.MaterialID)

        return bytes(RGBBlockBytes)

    def to_json(self):
        r = float(self.RGB.r)
        g = float(self.RGB.g)
        b = float(self.RGB.b)

        data = {   
            "AssetID":self.AssetID.hex(),
            "MaterialID":self.MaterialID.hex(),
            "RGB":[r,g,b],
        }
        return data
    
    def from_json(self,json):
        self.RGB = S3RGB(R = json["RGB"][0],G = json["RGB"][1],B = json["RGB"][2])
        self.AssetID = bytearray.fromhex(json["AssetID"])
        self.MaterialID = bytearray.fromhex(json["MaterialID"])
