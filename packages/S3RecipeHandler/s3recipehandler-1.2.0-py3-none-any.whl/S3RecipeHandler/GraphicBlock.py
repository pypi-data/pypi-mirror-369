import struct

class GraphicBlock:
    def __init__(self, BlockBytes=None, Block_json=None, URL=None, Asset=None):
        if BlockBytes is not None: 
            self.URL = BlockBytes[4:4 + BlockBytes[3]].decode('ascii')
            self.AssetID = BlockBytes[4 + len(self.URL):12 + len(self.URL)]
            self.MaterialID = BlockBytes[12 + len(self.URL):20 + len(self.URL)]
        elif Block_json != None:
            self.from_json(Block_json)
        elif URL is not None and Asset is not None:
            self.URL = URL
            self.AssetID = Asset.AssetID
            self.MaterialID = Asset.Models[0].MaterialID
        else:
            self.URL = ""
            self.AssetID = bytearray(8)
            self.MaterialID = bytearray(8)

    def get_bytes(self, index):
        GraphicBlockBytes = bytearray()
        url_length = len(self.URL)
        
        GraphicBlockBytes.extend(struct.pack('>I', url_length))
        GraphicBlockBytes.extend(self.URL.encode('ascii'))
        GraphicBlockBytes.extend(self.AssetID)
        GraphicBlockBytes.extend(self.MaterialID)
        GraphicBlockBytes.extend(bytearray(8))
        GraphicBlockBytes.append(1 if "http" in self.URL else 0)
        return bytes(GraphicBlockBytes)

    def to_json(self):
        data = {
            "AssetID":self.AssetID.hex(),
            "MaterialID":self.MaterialID.hex(),
            "URL":self.URL
        }
        return data
    
    def from_json(self,json):
        self.AssetID = bytearray.fromhex(json["AssetID"])
        self.MaterialID = bytearray.fromhex(json["MaterialID"])
        self.URL = json["URL"]

