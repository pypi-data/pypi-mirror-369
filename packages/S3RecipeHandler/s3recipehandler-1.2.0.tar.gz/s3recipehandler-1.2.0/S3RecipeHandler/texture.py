import struct
from .Helpers import Helpers

class Texture:
    def __init__(self, texture_block_bytes=None, texture_block_json=None, texture_channel="", texture_name=None):
        if texture_block_bytes != None:
            self.texture_channel = texture_block_bytes[4:4 + texture_block_bytes[3]].decode('ascii')
            self.texture_name = texture_block_bytes[4 + texture_block_bytes[3]:4 + texture_block_bytes[3] + 8]
        elif texture_block_json != None:
            pass
        else:
            self.texture_channel = texture_channel
            self.texture_name = texture_name if texture_name is not None else bytearray(8)

    @staticmethod
    def file_name_to_bytes(texture_name):
        return texture_name.encode('ascii')

    def get_bytes(self):
        texture_block_bytes = bytearray()
        texture_length = len(self.texture_channel)
        texture_block_bytes.extend(struct.pack('>I', texture_length))
        texture_block_bytes.extend(self.texture_channel.encode('ascii'))
        texture_block_bytes.extend(self.texture_name)
        return bytes(texture_block_bytes)

    def to_json(self) -> dict:
        dictionary = {
            "texture_channel":self.texture_channel,
            "texture_file":Helpers.file_name_bytes_to_string(self.texture_name)
        }
        return dictionary
    
    def from_json(self,json):
        self.texture_channel = json["texture_channel"]
        self.texture_name = Helpers.file_name_to_bytes(json["texture_file"])
