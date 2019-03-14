import unittest
from io import StringIO

from src.extractor.extractor import Configuration, Rom


class TestConfiguration(unittest.TestCase):

    def test___init__(self):
        configuration = Configuration(StringIO("""
            palettes:
            - &palette-id
              colors: [0x1, 0x2, 0x3, 0x4]
              is_obj: true

            tiles:
            - &tile-id
              address: 0x1
              palette: *palette-id

            sprites:
            - &sprite-id
              sprite_tiles:
              - tile: *tile-id
                x_flip: true
                y_flip: true
              - tile: *tile-id
                x_flip: true
                y_flip: true
              - tile: *tile-id
                x_flip: true
                y_flip: true
              - tile: *tile-id
                x_flip: true
                y_flip: true

            spritesheets:
            - &spritesheet-id
              spritesheet_sprites:
              - sprite: *sprite-id
              - sprite: *sprite-id
        """))

        self.assertEqual(1, configuration.tiles.tiles.__len__())
        self.assertEqual('tile-id', configuration.tiles.tiles.get('tile-id').id)
        self.assertEqual('palette-id', configuration.tiles.tiles.get('tile-id').palette.id)
        self.assertEqual([0x1, 0x2, 0x3, 0x4], configuration.tiles.tiles.get('tile-id').palette.colors)
        self.assertEqual(True, configuration.tiles.tiles.get('tile-id').palette.is_obj)

        self.assertEqual(1, configuration.sprites.sprites.__len__())
        self.assertEqual('sprite-id', configuration.sprites.sprites.get('sprite-id').id)
        self.assertEqual(4, configuration.sprites.sprites.get('sprite-id').sprite_tiles.__len__())
        self.assertEqual('tile-id', configuration.sprites.sprites.get('sprite-id').sprite_tiles[0].tile.id)
        self.assertEqual(True, configuration.sprites.sprites.get('sprite-id').sprite_tiles[0].x_flip)
        self.assertEqual(True, configuration.sprites.sprites.get('sprite-id').sprite_tiles[0].y_flip)

        self.assertEqual(1, configuration.spritesheets.spritesheets.__len__())
        self.assertEqual('spritesheet-id', configuration.spritesheets.spritesheets.get('spritesheet-id').id)
        self.assertEqual(2, configuration.spritesheets.spritesheets.get('spritesheet-id').spritesheet_sprites.__len__())
        self.assertEqual('sprite-id', configuration.spritesheets.spritesheets.get('spritesheet-id').spritesheet_sprites[0].sprite.id)


class TestRom(unittest.TestCase):

    def setUp(self):
        self.rom = Rom(None)

    def test_convert_rom_2bpp_bytes_to_indexed_pixels(self):
        rom_2bpp_bytes = bytearray.fromhex('0700 0b07 1b04 3f13 3f14 3f10 2718 1f0d')
        actual = self.rom.convert_rom_2bpp_bytes_to_indexed_pixels(rom_2bpp_bytes)
        expected = [
            0, 0, 0, 0, 0, 1, 1, 1,  # 0700 = 00000111 00000000 -[DECODE 2BPP]-> 00000111
            0, 0, 0, 0, 1, 2, 3, 3,  # 0b07 = 00001011 00000111 -[DECODE 2BPP]-> 00001233
            0, 0, 0, 1, 1, 2, 1, 1,
            0, 0, 1, 3, 1, 1, 3, 3,
            0, 0, 1, 3, 1, 3, 1, 1,
            0, 0, 1, 3, 1, 1, 1, 1,
            0, 0, 1, 2, 2, 1, 1, 1,
            0, 0, 0, 1, 3, 3, 1, 3
        ]
        self.assertEqual(expected, actual)

    def test_convert_bgr15_color_to_rgba32_bytes(self):
        bgr15_color = 0x22a2
        actual = self.rom.convert_bgr15_color_to_rgba32_bytes(bgr15_color, 255)
        expected = int.to_bytes(
            16 << 24  # 22a2 -> 00100010 10100010 -[AND 00011111]-> 00010 = 2 -[SCALE 31 -> 255]-> 16 = 0001 0000 = 10
            | 172 << 16  # 22a2 -> 00100010 10100010 -[SHIFT RIGHT 5 + AND 00011111] -> 10101 = 21 -[SCALE 31 -> 255]-> 172 = 1010 1100 = ac
            | 65 << 8  # 22a2 -> 00100010 10100010 -[SHIFT RIGHT 10 + AND 00011111] -> 01000 = 8 -[SCALE 31 -> 255]-> 65 = 0100 0001
            | 255
            , 4, 'big')
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
