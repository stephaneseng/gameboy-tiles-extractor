# gameboy-tiles-extractor

The main goal of this tool is to programmatically extract tiles data contained in a GameBoy (Color) ROM.

## Installation

### 0. Requirements

* [Python (tested with version 3.6)](https://www.python.org)

### 1. Install

```bash
(venv) make install
```

## Usage

```bash
(venv) python ./src/extractor/extractor.py $CONFIGURATION_FILE_PATH $ROM_FILE_PATH $OUTPUT_DIRECTORY_PATH
```

## Development

### Run the tests

```bash
(venv) python -m unittest discover
```

## Configuration file reference

### Palettes

```yaml
palettes:
- &palette-id
  colors: [0x1, 0x2, 0x3, 0x4]
  is_obj: true
```

* Palette.anchor:
  * Type: String
  * Palette unique identifier
* Palette.colors:
  * Type: List of Integers
  * List of 4 colors, encoded in BGR15
* Palette.is_obj:
  * Type: Boolean
  * If `true` the first color in the palette will be considered as transparent

### Tiles

```yaml
tiles:
- &tile-id
  address: 0x1
  palette: *palette-id
```

* Tile.anchor:
  * Type: String
  * Tile unique identifier, used to generate the tile file name 
* Tile.address:
  * Type: Integer 
  * Tile byte offset in the ROM file
* Tile.palette:
  * Type: Palette
  * The palette to apply on the tile 

### Sprites

```yaml
sprites:
- &sprite-id
  sprite_tiles:
  - tile: *tile-id-1
    x_flip: true
    y_flip: true
  - tile: *tile-id-2
    x_flip: true
    y_flip: true
  - tile: *tile-id-3
    x_flip: true
    y_flip: true
  - tile: *tile-id-4
    x_flip: true
    y_flip: true
```

* Sprite.anchor:
  * Type: String
  * Sprite unique identifier, used to generate the sprite file name
* Sprite.sprite_tiles:
  * Type: List of SpriteTiles
* Sprite.sprite_tiles.tile
  * Type: Tile
  * Tile composing a 4-tiles sprite
  * Tile order is: top-left, bottom-left, top-right, bottom-right
* Sprite.sprite_tiles.x_flip, Sprite.sprite_tiles.y_flip:
  * Type: Boolean, default: `false`
  * If `true` the tile will be flipped horizontally or vertically

### Spritesheets

```yaml
spritesheets:
- &spritesheet-id
  spritesheet_sprites:
  - sprite: *sprite-id-1
  - sprite: *sprite-id-2
```

* Spritesheet.anchor:
  * Type: String
  * Spritesheet unique identifier, used to generate the spritesheet file name
* Spritesheet.spritesheet_sprites:
  * Type: List of SpritesheetSprites
* Spritesheet.spritesheet_sprites.sprite:
  * Type: Sprite
  * Sprite composing a spritesheet
  * Sprites are added from left to right on the spritesheet, without limitation on the number of sprites to use
