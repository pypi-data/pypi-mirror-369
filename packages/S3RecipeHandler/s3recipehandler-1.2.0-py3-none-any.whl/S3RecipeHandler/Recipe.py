
import struct
from enum import Enum
from typing import List
from .AssetList import AssetList
from .Asset import Asset
from .Model import Model
from .texture import Texture
from .RGBBlock import RGBBlock
from .GraphicBlock import GraphicBlock
from .BodyModBlock import body_mod_blocks
from .graphic_vector_list import graphic_vector_list

class Gender(Enum):
    MALE = 1
    FEMALE = 0

class RecipeTypes(Enum):
    MARQUEE = 0
    LIVINGWORLD = 1
    VEHICLE = 2
    CREATEACHARACTER = 3
    UNDEFINED = 4
    TEST = 5

class Recipe:
    def __init__(self, recipe_bytes=None, Recipe_Json:dict=None, recipe_name="", recipe_type=RecipeTypes.MARQUEE):
        """
        Serialized instance of a recipe class
            recipe_bytes = bytes/bytearray of a recipe
            Recipe_Json = dict of recipe
            recipe_name = recipe name eg. cas_db
            recipe_type = recipe type specifies what folder to read from
        """
        
        self.recipe_name = ""
        self.gender = Gender.MALE
        self.recipe_type = RecipeTypes.MARQUEE
        self._only_load_model_textures = True
        self.asset_lists = []
        self.rgb_blocks = []
        self.graphic_blocks = []
        self.body_mods = body_mod_blocks()
        self.graphic_vectors = graphic_vector_list()
        
        if recipe_bytes != None:
            # Constructor with byte array parsing
            self._parse_recipe_bytes(recipe_bytes)
        
        elif Recipe_Json != None:
            self.from_json(Recipe_Json)
        
        else:
            # Constructor with name and type
            self.recipe_name = recipe_name
            self.recipe_type = recipe_type

    def _parse_recipe_bytes(self, recipe_bytes):
        """Parse recipe from byte array - exact translation of original constructor logic"""
        # Store Recipe Name
        name_length = recipe_bytes[7]
        self.recipe_name = recipe_bytes[8:8 + name_length].decode('ascii')

        # Store Recipe Type (marquee, createacharacter, etc.)
        self.recipe_type = RecipeTypes(recipe_bytes[0x0B + recipe_bytes[7]])

        if recipe_bytes[0x13 + recipe_bytes[7]] == 2:
            self._only_load_model_textures = False

        # Get the index where assets start
        index = 0x18 + recipe_bytes[7]

        # Get the amount of assets in Recipe file and loop through them
        amount_of_asset_lists = recipe_bytes[index - 1]
        for i in range(amount_of_asset_lists):
            start_index = index
            index += 8 + recipe_bytes[index + 3]
            self.asset_lists.append(AssetList(recipe_bytes[start_index:index]))

            # Get amount of assets in asset list and loop through them
            amount_of_assets = recipe_bytes[index - 1]
            for a in range(amount_of_assets):
                start_index = index
                index += 0x0C
                self.asset_lists[-1].assets.append(Asset(recipe_bytes[start_index:start_index + 0x0C]))
                amount_of_models = recipe_bytes[index - 1]
                for k in range(amount_of_models):

                    self.asset_lists[-1].assets[-1].Models.append(Model(recipe_bytes[index:index + 0x25]))
                    index += 0x25

                    # Unknown why this happens on female Rostrals, gotta parse through them
                    texture_loops = recipe_bytes[index - 0x11]

                    amount_of_textures = recipe_bytes[index - 1]
                    for b in range(amount_of_textures):
                        start_index = index
                        index += 12 + recipe_bytes[index + 3]
                        self.asset_lists[-1].assets[-1].Models[-1].Textures.append(
                            Texture(recipe_bytes[start_index:index])
                        )

                    for b in range(texture_loops - 1):
                        index += 0x10
                        amount_of_textures = recipe_bytes[index - 1]

                        for d in range(amount_of_textures):
                            index += 12 + recipe_bytes[index + 3]

        if not self._only_load_model_textures:
            # After parsing assets, parse gender and RGB blocks
            index += 5  # Skip through the unnecessary 01 00 00 00 06
            self.gender = Gender(recipe_bytes[index])
            index += 9  # Jump to first RGB Block

            # Get amount of RGB Blocks and loop through them and make RGBBlock objects
            amount_of_rgb_blocks = recipe_bytes[index - 1]
            for i in range(amount_of_rgb_blocks):
                start_index = index
                index += 0x2C
                self.rgb_blocks.append(RGBBlock(recipe_bytes[start_index:index]))

            # Go through blocks
            index += 8
            amount_of_graphics = recipe_bytes[index - 1]
            for i in range(amount_of_graphics):
                start_index = index
                index += 5 + (8 * 3) + recipe_bytes[index + 3]
                self.graphic_blocks.append(GraphicBlock(recipe_bytes[start_index:index]))
                index += 1

            start_index = index + 4
            index = start_index + 76

            print(start_index)
            print(index)

            self.body_mods = body_mod_blocks(asset_bytes=recipe_bytes[start_index:index])

            start_index = index+20
            index = start_index + 80

            self.graphic_vectors = graphic_vector_list(vector_list_bytes=recipe_bytes[start_index:index])

            #self._bytes_after.extend(recipe_bytes[index:index + 500])

    def remove_low_lod_models(self):
        """Remove low LOD models from assets"""
        for asset_list in self.asset_lists:
            for asset in asset_list.assets:
                if len(asset.Models) > 1:
                    asset.Models.pop(1)

    def get_bytes(self):
        """Convert recipe back to byte array"""
        recipe_bytes:bytearray = []

        # Add Unknown bytes in Recipe header
        recipe_bytes.extend([0, 0, 0, 7])

        # Recipe name length
        recipe_bytes.extend(struct.pack('>I', len(self.recipe_name)))

        recipe_bytes.extend(self.recipe_name.encode('ascii'))

        # Write recipe type (createacharacter, marquee, etc.)
        recipe_bytes.extend(struct.pack('>I', self.recipe_type.value))

        # Add more unknown bytes
        recipe_bytes.extend([0, 0, 0, 0x0F, 0, 0, 0, 2])

        # Add assets count to recipe
        recipe_bytes.extend(struct.pack('>I', len(self.asset_lists)))

        # Loop through AssetLists and add their bytes
        for asset_list in self.asset_lists:
            recipe_bytes.extend(asset_list.get_bytes())

        # Not documented what this byte array is for but it's in every recipe
        recipe_bytes.extend([1, 0, 0, 0, 6])

        # Add gender bytes
        recipe_bytes.append(self.gender.value)

        # Loop through RGB blocks and add them
        recipe_bytes.extend(struct.pack('>I', len(self.rgb_blocks)))
        recipe_bytes.extend(struct.pack('>I', len(self.rgb_blocks)))
        for i in range(len(self.rgb_blocks)):
            recipe_bytes.extend(self.rgb_blocks[i].get_bytes(i))

        # Loop through graphic blocks and add them
        recipe_bytes.extend(struct.pack('>I', 5))  # Not sure what this 5 is for but it's in every single recipe file
        amount_of_graphics = struct.pack('<I', len(self.graphic_blocks))
        amount_of_graphics_reversed = amount_of_graphics[::-1]
        recipe_bytes.extend(amount_of_graphics_reversed)
        for i in range(len(self.graphic_blocks)):
            recipe_bytes.extend(self.graphic_blocks[i].get_bytes(i))
            recipe_bytes.append(i)

        recipe_bytes.extend([0,0,0,0x13])
        recipe_bytes.extend(self.body_mods.get_bytes())

        recipe_bytes.extend([0] * 20)
        recipe_bytes.extend(self.graphic_vectors.get_bytes())
        recipe_bytes.extend([00, 00, 00, 00, 00, 0x0F, 0x58])

        #recipe_bytes.extend(self._bytes_after)

        return bytes(recipe_bytes)

    def to_json(self) -> dict:
        """
        converts serialized recipe to a dict format for easy serialized
        """

        asset_list = []
        for asset in self.asset_lists:
            asset_list.append(asset.to_json())


        graphics_list = []
        for graphic_block in self.graphic_blocks:
            graphics_list.append(graphic_block.to_json())

        rgb_blocks = []
        for rgb_block in self.rgb_blocks:
            rgb_blocks.append(rgb_block.to_json())
    

        data = {
            "recipe_name":self.recipe_name,
            "gender":self.gender.name.lower(),
            "recipe_type":self.recipe_type.name.lower(),
            "only_load_model_textures":self._only_load_model_textures,
            "asset_list":asset_list,
            "graphic_blocks":graphics_list,
            "rgb_blocks":rgb_blocks,
            "body_mods":self.body_mods.to_json(),
            "graphic_vectors":self.graphic_vectors.to_json()
        }
        
        return data
    
    def from_json(self,json:dict):
        """
        loads a recipe from json format
        json = dict pre serialized json
        """

        self.recipe_name = json["recipe_name"]
        
        gender_map = {"female": Gender.FEMALE, "male": Gender.MALE}
        self.gender = gender_map[json["gender"]]
        
        RecipeType_map = {"marquee":RecipeTypes.MARQUEE, "livingworld":RecipeTypes.LIVINGWORLD, "vehicle":RecipeTypes.VEHICLE, "createacharacter":RecipeTypes.CREATEACHARACTER, "undefined":RecipeTypes.UNDEFINED, "test":RecipeTypes.TEST}
        self.recipe_type = RecipeType_map[json["recipe_type"]]

        self._only_load_model_textures = (json["only_load_model_textures"] == "true")

        self.asset_lists = []
        for asset in json["asset_list"]:
            al = AssetList(asset_json=asset)
            self.asset_lists.append(al)

        self.rgb_blocks = []

        for rgb_blocks in json["rgb_blocks"]:
            rgb = RGBBlock(Block_json=rgb_blocks)
            self.rgb_blocks.append(rgb)
        
        self.graphic_blocks = []

        for graphic_block in json["graphic_blocks"]:
            g = GraphicBlock(Block_json=graphic_block)
            self.graphic_blocks.append(g)

        self.body_mods = body_mod_blocks(Asset_json=json["body_mods"])
        self.graphic_vectors = graphic_vector_list(vector_list_json=json["graphic_vectors"])