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
(venv) python main.py $CONFIGURATION_FILE_PATH $ROM_FILE_PATH $OUTPUT_DIRECTORY_PATH
```

## Configuration file reference

### Palettes

```yaml
palettes:
  - [$BGR15_COLOR_1, $BGR15_COLOR_2, $BGR15_COLOR_3, $BGR15_COLOR_4]
```

#### Palette

Type: List.

List of 4 colors, encoded in BGR15.

### Tiles

```yaml
tiles:
- id: $ID
  offset: $OFFSET
  palette: $PALETTE
  has_alpha: $HAS_ALPHA
```

#### Tile

##### Tile.id

Type: String.

Tile unique identifier, used to generate the tile file name.

##### Tile.offset

Type: Integer.

Tile byte offset in the ROM file.

##### Tile.palette

Type: Palette.

The palette to apply on the tile.

##### Tile.has_alpha

Type: Boolean, default: `false`.

If `true` the first color of the palette is considered has transparent.

### Sprites

```yaml
sprites:
  - id: $ID
    sprite_tiles:
    - tile: $TILE_1
      x_flip: $X_FLIP_TILE_1
      y_flip: $Y_FLIP_TILE_1
    - tile: $TILE_2
      x_flip: $X_FLIP_TILE_2
      y_flip: $Y_FLIP_TILE_2
    - tile: $TILE_3
      x_flip: $X_FLIP_TILE_3
      y_flip: $Y_FLIP_TILE_3
    - tile: $TILE_4
      x_flip: $X_FLIP_TILE_4
      y_flip: $Y_FLIP_TILE_4
```

#### Sprite

##### Sprite.id

Type: String.

Sprite unique identifier, used to generate the tile file name.

##### Sprite.sprite_tiles.tile

Type: Tile.

Tile composing a 4-tiles sprite.
Tile order is: top-left, bottom-left, top-right, bottom-right.

##### Sprite.sprite_tiles.x_flip, Sprite.sprite_tiles.y_flip

Type: Boolean, default: `false`.

If `true` the tile will be flipped horizontally or vertically.

### Spritesheets

```yaml
spritesheets:
- id: $ID
  spritesheet_sprites:
    - sprite: $SPRITE_1
    - sprite: $SPRITE_2
```

#### Spritesheet

##### Spritesheet.id

Type: String.

Spritesheet unique identifier, used to generate the tile file name.

##### Spritesheet.spritesheet_sprites.sprite

Type: Sprite.

Sprite composing a spritesheet.
Sprites are added from left to right on the spritesheet, without limitation on the number of sprites to use.
