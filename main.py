import argparse
import logging
import os
from math import floor

import yaml
from PIL import Image
from PIL.Image import FLIP_LEFT_RIGHT, FLIP_TOP_BOTTOM


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('configuration_file_path', metavar='configuration-file-path', type=argparse.FileType('r'))
    parser.add_argument('rom_file_path', metavar='rom-file-path', type=argparse.FileType('rb'))
    parser.add_argument('output_directory_path', metavar='output-directory-path', type=is_directory_path)
    parser.add_argument('--log-level', choices=['CRITICAL', 'FATAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'])

    return parser


def is_directory_path(path) -> bool:
    if not os.path.isdir(path):
        raise NotADirectoryError(path)

    return path


def load_configuration(configuration_file, logger):
    configuration = yaml.load(configuration_file)

    logger.debug('Read configuration: {}'.format(configuration))
    return configuration


def load_tile_image(rom_file, tile, logger):
    offset = tile['offset']
    palette = tile['palette']
    has_alpha = tile['has_alpha'] if 'has_alpha' in tile else False

    rom_bytes = read_rom_bytes(rom_file, offset, 16, logger)
    indexed_colors = convert_rom_bytes_to_indexed_colors(rom_bytes, logger)
    rgba32_bytes = convert_indexed_colors_to_rgba32_bytes(indexed_colors, palette, has_alpha, logger)
    image = Image.frombytes('RGBA', (8, 8), rgba32_bytes)

    return image


def read_rom_bytes(rom_file, offset, size, logger):
    rom_file.seek(offset)
    bytes = rom_file.read(size)

    logger.debug('Read bytes: {}'.format(bytes))
    return bytes


def convert_rom_bytes_to_indexed_colors(bytes, logger):
    """
    In 2bpp, a pair of bytes represents a tile line.
    See: http://www.huderlem.com/demos/gameboy2bpp.html.

    Example:
    [x07, x00] -> x00 = 0 0 0 0 0 0 0 0 -> [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 1], [0, 1], [0, 1] -> [0, 0, 0, 0, 0, 1, 1, 1].
                  x07 = 0 0 0 0 0 1 1 1
    """
    indexed_colors = []

    pairs = [[bytes[i], bytes[i + 1]] for i in range(0, len(bytes), 2)]
    for pair in pairs:
        low_byte = pair[0]
        high_byte = pair[1]
        indexed_colors.extend([((high_byte >> i & 1) << 1) | (low_byte >> i & 1) for i in range(8 - 1, -1, -1)])

    logger.debug('Read indexed colors: {}'.format(indexed_colors))
    return indexed_colors


def convert_indexed_colors_to_rgba32_bytes(indexed_colors, palette, has_alpha, logger):
    """
    Palettes are specified in BGR15.
    """
    bytes = []

    for indexed_color in indexed_colors:
        bytes.append(convert_bgr15_to_rgba32_bytes(indexed_color, palette, has_alpha))
    bytes = b''.join(bytes)

    logger.debug('Converted into RGBA32: {}'.format(bytes))
    return bytes


def convert_bgr15_to_rgba32_bytes(index, palette, has_alpha):
    """
    BGR15 is represented in 15 bits and has a value range of [0-31].
    RGB24 is represented in 24 bits and has a value range of [0-255].
    """
    if has_alpha and 0 == index:
        rgba32_bytes = int.to_bytes(0xFFFFFF00, 4, 'big')
    else:
        bgr15_bytes = palette[index]
        r = floor((bgr15_bytes & 0x1F) / 31 * 255)
        g = floor((bgr15_bytes >> 5 & 0x1F) / 31 * 255)
        b = floor((bgr15_bytes >> 10 & 0x1F) / 31 * 255)
        rgba32_bytes = int.to_bytes(r << 24 | g << 16 | b << 8 | 0xFF, 4, 'big')

    return rgba32_bytes


def load_sprite_image(rom_file, sprite, logger):
    tile_images = []
    for sprite_tile in sprite['sprite_tiles']:
        tile_image = load_tile_image(rom_file, sprite_tile['tile'], logger)
        if 'x_flip' in sprite_tile and sprite_tile['x_flip']:
            tile_image = tile_image.transpose(FLIP_LEFT_RIGHT)
        if 'y_flip' in sprite_tile and sprite_tile['y_flip']:
            tile_image = tile_image.transpose(FLIP_TOP_BOTTOM)
        tile_images.append(tile_image)

    sprite_image = Image.new('RGBA', (16, 16))
    for index, tile_image in enumerate(tile_images):
        sprite_image.paste(tile_image, (0 if index in [0, 1] else 8, 0 if index in [0, 2] else 8))

    return sprite_image


def load_spritesheet_image(rom_file, spritesheet, logger):
    sprite_images = []
    for spritesheet_sprite in spritesheet['spritesheet_sprites']:
        sprite_image = load_sprite_image(rom_file, spritesheet_sprite['sprite'], logger)
        sprite_images.append(sprite_image)

    spritesheet_image = Image.new('RGBA', (len(sprite_images) * 16, 16))
    for index, sprite_image in enumerate(sprite_images):
        spritesheet_image.paste(sprite_image, (index * 16, 0))

    return spritesheet_image


def main():
    logger = logging.getLogger(__name__)

    parser = build_argument_parser()
    args = parser.parse_args()
    configuration_file = args.configuration_file_path
    rom_file = args.rom_file_path
    output_directory_path = args.output_directory_path
    logging.basicConfig(level=args.log_level)

    # Configuration.
    configuration = load_configuration(configuration_file, logger)

    # Tiles.
    tiles = configuration['tiles']
    for tile in tiles:
        tile_image = load_tile_image(rom_file, tile, logger)
        tile_image.save(output_directory_path + '/' + tile['id'] + '.png')

    # Sprites.
    sprites = configuration['sprites']
    for sprite in sprites:
        sprite_image = load_sprite_image(rom_file, sprite, logger)
        sprite_image.save(output_directory_path + '/' + sprite['id'] + '.png')

    # Spritesheets.
    spritesheets = configuration['spritesheets']
    for spritesheet in spritesheets:
        spritesheet_image = load_spritesheet_image(rom_file, spritesheet, logger)
        spritesheet_image.save(output_directory_path + '/' + spritesheet['id'] + '.png')


if __name__ == '__main__':
    main()
