import random
import struct
from .Model import Model

class Asset:
    def __init__(self, asset_bytes=None, Asset_json=None):
        self.Models = []
        self.AssetID = bytearray(8)

        if asset_bytes != None:
            self.AssetID = asset_bytes[:8]
        elif Asset_json != None:
            self.from_json(Asset_json)
        else:
            # Generate random Asset ID
            for i in range(8):
                self.AssetID[i] = random.randint(0, 255)

    def change_textures(self, new_texture_bytes, texture_channel):
        for model in self.Models:
            found_texture = None
            for texture in model.textures:
                if texture.texture_channel == texture_channel:
                    found_texture = texture
                    break
            if found_texture:
                found_texture.texture_name = new_texture_bytes

    def get_bytes(self):
        asset_block_bytes = bytearray()

        asset_block_bytes.extend(self.AssetID)
        asset_block_bytes.extend(struct.pack('>I', len(self.Models)))  # Big-endian

        for i, model in enumerate(self.Models):
            lod_index = 0 if i == 0 else 2
            asset_block_bytes.extend(model.get_bytes(lod_index))

        return bytes(asset_block_bytes)
    
    def to_json(self):
        Models = []
        for model in self.Models:
            Models.append(model.to_json())
        
        data = {
            "AssetID":self.AssetID.hex(),
            "Models":Models
        }
        return data
    
    def from_json(self,json):
        self.AssetID = bytearray.fromhex(json["AssetID"])
        self.Models = []
        for models in json["Models"]:
            m = Model()
            m.from_json(models)

            self.Models.append(m)


