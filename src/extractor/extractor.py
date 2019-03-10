import argparse
import os
from io import TextIOWrapper, BufferedReader
from math import floor

import ruamel.yaml
from PIL import Image
from PIL.Image import FLIP_LEFT_RIGHT, FLIP_TOP_BOTTOM


class Configuration:
    class Palette:
        def __init__(self, id: str, colors: list, is_obj: bool):
            self.id = id
            self.colors = colors
            self.is_obj = is_obj

        @staticmethod
        def from_yaml(yaml_palette) -> 'Configuration.Palette':
            return Configuration.Palette(
                yaml_palette.anchor.value,
                yaml_palette['colors'],
                yaml_palette['is_obj']
            )

    class Tile:
        def __init__(self, id: str, address: int, palette: 'Configuration.Palette'):
            self.id = id
            self.address = address
            self.palette = palette

        @staticmethod
        def from_yaml(yaml_tile) -> 'Configuration.Tile':
            return Configuration.Tile(
                yaml_tile.anchor.value,
                yaml_tile['address'],
                Configuration.Palette.from_yaml(yaml_tile['palette'])
            )

    class Tiles:
        def __init__(self, yaml_tiles):
            self.tiles = {}
            for yaml_tile in yaml_tiles:
                self.tiles[yaml_tile.anchor.value] = Configuration.Tile.from_yaml(yaml_tile)

    class SpriteTile:
        def __init__(self, tile: 'Configuration.Tile', x_flip: bool, y_flip: bool):
            self.tile = tile
            self.x_flip = x_flip
            self.y_flip = y_flip

        @staticmethod
        def from_yaml(yaml_sprite_tile) -> 'Configuration.SpriteTile':
            return Configuration.SpriteTile(
                Configuration.Tile.from_yaml(yaml_sprite_tile['tile']),
                yaml_sprite_tile['x_flip'] if 'x_flip' in yaml_sprite_tile else False,
                yaml_sprite_tile['y_flip'] if 'y_flip' in yaml_sprite_tile else False
            )

    class Sprite:
        def __init__(self, id: str, sprite_tiles: list):
            self.id = id
            self.sprite_tiles = sprite_tiles

        @staticmethod
        def from_yaml(yaml_sprite) -> 'Configuration.Sprite':
            return Configuration.Sprite(
                yaml_sprite.anchor.value,
                [Configuration.SpriteTile.from_yaml(yaml_sprite_tile) for yaml_sprite_tile in yaml_sprite['sprite_tiles']]
            )

    class Sprites:
        def __init__(self, yaml_sprites):
            self.sprites = {}
            for yaml_sprite in yaml_sprites:
                self.sprites[yaml_sprite.anchor.value] = Configuration.Sprite.from_yaml(yaml_sprite)

    class SpritesheetSprite:
        def __init__(self, sprite: 'Configuration.Sprite'):
            self.sprite = sprite

        @staticmethod
        def from_yaml(yaml_spritesheet_sprite) -> 'Configuration.SpritesheetSprite':
            return Configuration.SpritesheetSprite(
                Configuration.Sprite.from_yaml(yaml_spritesheet_sprite['sprite']),
            )

    class Spritesheet:
        def __init__(self, id: str, spritesheet_sprites: list):
            self.id = id
            self.spritesheet_sprites = spritesheet_sprites

        @staticmethod
        def from_yaml(yaml_spritesheet) -> 'Configuration.Spritesheet':
            return Configuration.Spritesheet(
                yaml_spritesheet.anchor.value,
                [Configuration.SpritesheetSprite.from_yaml(spritesheet_sprite) for spritesheet_sprite in yaml_spritesheet['spritesheet_sprites']]
            )

    class Spritesheets:
        def __init__(self, yaml_spritesheets):
            self.spritesheets = {}
            for yaml_spritesheet in yaml_spritesheets:
                self.spritesheets[yaml_spritesheet.anchor.value] = Configuration.Spritesheet.from_yaml(yaml_spritesheet)

    def __init__(self, stream: TextIOWrapper):
        self.stream = stream
        yaml = ruamel.yaml.YAML()
        yaml_document = yaml.load(self.stream)
        self.tiles = Configuration.Tiles(yaml_document['tiles'])
        self.sprites = Configuration.Sprites(yaml_document['sprites'])
        self.spritesheets = Configuration.Spritesheets(yaml_document['spritesheets'])


class Rom:
    def __init__(self, stream: BufferedReader):
        self.stream = stream

    def __read_rom_bytes(self, address: int, size: int) -> bytes:
        self.stream.seek(address)
        return self.stream.read(size)

    def __convert_rom_2bpp_bytes_to_indexed_pixels(self, rom_2bpp_bytes: bytes) -> list:
        indexed_pixels = []
        for pair in [[rom_2bpp_bytes[i], rom_2bpp_bytes[i + 1]] for i in range(0, len(rom_2bpp_bytes), 2)]:
            low_byte = pair[0]
            high_byte = pair[1]
            indexed_pixels.extend([((high_byte >> i & 1) << 1) | (low_byte >> i & 1) for i in range(8 - 1, -1, -1)])
        return indexed_pixels

    def __convert_bgr15_color_to_rgba32_bytes(self, bgr15_color: int, alpha: int) -> bytes:
        red = floor((bgr15_color & 0x1f) / 31 * 255)
        green = floor((bgr15_color >> 5 & 0x1f) / 31 * 255)
        blue = floor((bgr15_color >> 10 & 0x1f) / 31 * 255)
        return int.to_bytes(red << 24 | green << 16 | blue << 8 | alpha, 4, 'big')

    def __convert_indexed_pixels_to_image(self, indexed_pixels: list, palette: 'Configuration.Palette') -> Image:
        image_bytes = bytearray()
        for indexed_pixel in indexed_pixels:
            alphas = [0, 255, 255, 255] if palette.is_obj else [255, 255, 255, 255]
            image_bytes.extend(bytearray(
                self.__convert_bgr15_color_to_rgba32_bytes(palette.colors[indexed_pixel], alphas[indexed_pixel])))
        return Image.frombytes('RGBA', (8, 8), bytes(image_bytes))

    def read_tile(self, configuration_tile: 'Configuration.Tile') -> Image:
        rom_2bpp_bytes = self.__read_rom_bytes(configuration_tile.address, 16)
        indexed_pixels = self.__convert_rom_2bpp_bytes_to_indexed_pixels(rom_2bpp_bytes)
        return self.__convert_indexed_pixels_to_image(indexed_pixels, configuration_tile.palette)

    def read_sprite(self, configuration_sprite: 'Configuration.Sprite') -> Image:
        tile_images = []
        for sprite_tile in configuration_sprite.sprite_tiles:
            tile_image = self.read_tile(sprite_tile.tile)
            if sprite_tile.x_flip:
                tile_image = tile_image.transpose(FLIP_LEFT_RIGHT)
            if sprite_tile.y_flip:
                tile_image = tile_image.transpose(FLIP_TOP_BOTTOM)
            tile_images.append(tile_image)
        sprite_image = Image.new('RGBA', (16, 16))
        for index, tile_image in enumerate(tile_images):
            sprite_image.paste(tile_image, (0 if index in [0, 1] else 8, 0 if index in [0, 2] else 8))
        return sprite_image

    def read_spritesheet(self, configuration_spritesheet: 'Configuration.Spritesheet') -> Image:
        sprite_images = []
        for spritesheet_sprite in configuration_spritesheet.spritesheet_sprites:
            sprite_image = self.read_sprite(spritesheet_sprite.sprite)
            sprite_images.append(sprite_image)
        spritesheet_image = Image.new('RGBA', (len(sprite_images) * 16, 16))
        for index, sprite_image in enumerate(sprite_images):
            spritesheet_image.paste(sprite_image, (index * 16, 0))
        return spritesheet_image


def is_directory_path(path) -> bool:
    if not os.path.isdir(path):
        raise NotADirectoryError(path)
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('configuration_file_path', metavar='configuration-file-path', type=argparse.FileType('r'))
    parser.add_argument('rom_file_path', metavar='rom-file-path', type=argparse.FileType('rb'))
    parser.add_argument('output_directory_path', metavar='output-directory-path', type=is_directory_path)
    args = parser.parse_args()

    configuration = Configuration(args.configuration_file_path)
    rom = Rom(args.rom_file_path)

    for configuration_tile in configuration.tiles.tiles.values():
        image = rom.read_tile(configuration_tile)
        image.save('{0}/{1}.png'.format(args.output_directory_path, configuration_tile.id))
    for configuration_sprite in configuration.sprites.sprites.values():
        image = rom.read_sprite(configuration_sprite)
        image.save('{0}/{1}.png'.format(args.output_directory_path, configuration_sprite.id))
    for configuration_spritesheet in configuration.spritesheets.spritesheets.values():
        image = rom.read_spritesheet(configuration_spritesheet)
        image.save('{0}/{1}.png'.format(args.output_directory_path, configuration_spritesheet.id))


if __name__ == '__main__':
    main()
