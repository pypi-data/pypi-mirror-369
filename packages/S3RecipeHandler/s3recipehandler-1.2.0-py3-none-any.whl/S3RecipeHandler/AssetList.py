import struct
from .Asset import Asset

class AssetList:
    def __init__(self, asset_header=None, asset_json=None, asset_folder_name=None):
        self.asset_folder_name = ""
        self.assets = []

        if asset_header != None:
            self.asset_folder_name = asset_header[4:4 + asset_header[3]].decode('ascii')
        
        if asset_json != None:
            self.from_json(asset_json)

        elif asset_folder_name is not None:
            self.asset_folder_name = asset_folder_name

    def get_bytes(self):
        asset_header_bytes = bytearray()

        asset_folder_name_length = len(self.asset_folder_name)
        asset_header_bytes.extend(struct.pack('>I', asset_folder_name_length))
        asset_header_bytes.extend(self.asset_folder_name.encode('ascii'))
        asset_header_bytes.extend(b'\x00\x00\x00' + bytes([len(self.assets)]))

        for asset in self.assets:
            asset_header_bytes.extend(asset.get_bytes())

        return bytes(asset_header_bytes)

    def to_json(self):
        assets = []
        for asset in self.assets:
            assets.append(asset.to_json())
        
        data = {
            "asset_folder_name":self.asset_folder_name,
            "assets":assets
        }
        return data
    
    def from_json(self,json):
        self.asset_folder_name = json["asset_folder_name"]
        self.assets = []
        for asset in json["assets"]:
            a = Asset()
            a.from_json(asset)
            self.assets.append(a)