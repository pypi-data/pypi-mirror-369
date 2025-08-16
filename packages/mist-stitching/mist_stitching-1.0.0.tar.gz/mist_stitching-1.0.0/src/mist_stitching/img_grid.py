import argparse
import os
import re
import numpy as np
import skimage.io
import logging

# local imports
import img_tile




class TileGrid():
    timePattern = "(.*)(\\{[t]+\\})(.*)"

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.img_height = None
        self.img_width = None

        if 'grid_width' in vars(args) and 'grid_height' in vars(args):
            # init a 2d list to hold Tiles
            self.tiles = [[None for _ in range(self.args.grid_width)] for _ in range(self.args.grid_height)]
            self.height = self.args.grid_height
            self.width = self.args.grid_width
        else:
            self.tiles = None
            self.height = None
            self.width = None

    def load_images_into_memory(self):
        for r in range(self.args.grid_height):
            for c in range(self.args.grid_width):
                t = self.get_tile(r, c)
                if t is not None:
                    t.get_image()  # loads the image into memory

    def get_tile(self, r: int, c: int) -> img_tile.Tile:
        if r >= 0 and c >= 0 and r < self.args.grid_height and c < self.args.grid_width:
            return self.tiles[r][c]
        else:
            # tile request is invalid
            return None

    def get_image_shape(self) -> tuple[int, int]:
        if self.img_height is None or self.img_width is None:
            for r in range(self.args.grid_height):
                for c in range(self.args.grid_width):
                    t = self.get_tile(r, c)
                    if t is not None:
                        if t.exists():  # if the file exists
                            s = t.get_image().shape
                            self.img_height = s[0]
                            self.img_width = s[1]

        return self.img_height, self.img_width

    def get_image_size_per_direction(self, direction) -> int:
        img_shape = self.get_image_shape()
        if direction == 'HORIZONTAL':
            return img_shape[1]
        elif direction == 'VERTICAL':
            return img_shape[0]
        else:
            raise ValueError("Invalid direction: {}".format(direction))

    def get_num_valid_tiles(self):
        count = 0
        for r in range(self.args.grid_height):
            for c in range(self.args.grid_width):
                if self.get_tile(r, c) is not None:
                    count += 1
        return count

    def print_names(self):
        str = "Tile grid:"
        for r in range(self.args.grid_height):
            str += "\n"
            for c in range(self.args.grid_width):
                if self.tiles[r][c] is None:
                    str += "None\t"
                else:
                    str += self.tiles[r][c].name + "\t"
        logging.info(str)

    def print_peaks(self, dir: str, key: str):
        assert dir in ['north', 'west']
        assert key in ['ncc', 'x', 'y', 'abs_x', 'abs_y']

        str = "{} {} matrix:".format(dir, key)
        for r in range(self.args.grid_height):
            str += "\n"
            for c in range(self.args.grid_width):
                tile = self.get_tile(r, c)
                if tile is None:
                    str += "None\t"
                    continue

                t = tile.west_translation if dir == 'west' else tile.north_translation
                if t is not None:
                    val = getattr(t, key)
                    if np.isnan(val):
                        str += "nan \t"  # print nan with a trailing space to make it the same size as the rest of the values
                    else:
                        str += "{:0.2f}\t".format(val)
                else:
                    str += "None\t"
        logging.info(str)

    def write_translations_to_file(self, output_filepath: str):
        with open(output_filepath, 'w') as f:
            for r in range(self.args.grid_height):
                for c in range(self.args.grid_width):
                    tile = self.get_tile(r, c)
                    if tile is None:
                        continue
                    west = self.get_tile(r, c - 1)
                    north = self.get_tile(r - 1, c)

                    if west is not None:
                        t = tile.west_translation
                        if t is not None:
                                f.write("west, {}, {}, {:0.10f}, {:d}, {:d}\n".format(tile.name, west.name, t.ncc, t.x, t.y))

                    if north is not None:
                        t = tile.north_translation
                        if t is not None:
                                f.write("north, {}, {}, {:0.10f}, {:d}, {:d}\n".format(tile.name, north.name, t.ncc, t.x, t.y))

    def write_global_positions_to_file(self, output_filepath: str):
        with open(output_filepath, 'w') as f:
            for r in range(self.args.grid_height):
                for c in range(self.args.grid_width):
                    tile = self.get_tile(r, c)
                    if tile is None:
                        continue

                    ncc = tile.get_max_translation_ncc()
                    if np.isnan(ncc):
                        ncc = -1.0

                    f.write("file: {}; corr: {:0.10f}; position: ({:d}, {:d}); grid: ({:d}, {:d});\n".format(tile.name, ncc, tile.abs_x, tile.abs_y, c, r))


class TileGridRowCol(TileGrid):
    colPattern = "(.*)(\\{[c]+\\})(.*)"
    rowPattern = "(.*)(\\{[r]+\\})(.*)"

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)

        if self.args.grid_origin == 'UL':
            start_row = 0
            start_col = 0
            row_incrementer = 1
            col_incrementer = 1
        elif self.args.grid_origin == 'UR':
            start_row = 0
            start_col = self.args.grid_width - 1
            row_incrementer = 1
            col_incrementer = -1
        elif self.args.grid_origin == 'LL':
            start_row = self.args.grid_height - 1
            start_col = 0
            row_incrementer = -1
            col_incrementer = 1
        elif self.args.grid_origin == 'LR':
            start_row = self.args.grid_height - 1
            start_col = self.args.grid_width - 1
            row_incrementer = -1
            col_incrementer = -1
        else:
            raise RuntimeError("Unknown grid origin: {}".format(self.args.grid_origin))

        filename_pattern = self.args.filename_pattern
        time_matcher = re.compile(self.timePattern)
        time_match = time_matcher.match(filename_pattern)
        if time_match is not None:
            if self.args.time_slice is None:
                raise RuntimeError("Filename pattern has a time component \"{t+}\", so a time slice is required.")
            fmt_str = "{:0" + str(len(time_match.group(2)) - 2) + "d}"
            filename_pattern = "{}{}{}".format(time_match.group(1), fmt_str.format(self.args.time_slice), time_match.group(3))

        row_matcher = re.compile(self.rowPattern)
        col_matcher = re.compile(self.colPattern)

        grid_row = start_row
        for row in range(0, self.args.grid_height):
            fn = filename_pattern
            row_match = row_matcher.match(fn)
            fmt_str = "{:0" + str(len(row_match.group(2)) - 2) + "d}"
            fn_row = "{}{}{}".format(row_match.group(1), fmt_str.format(row + self.args.start_row), row_match.group(3))

            grid_col = start_col
            for col in range(0, self.args.grid_width):
                col_match = col_matcher.match(fn_row)
                fmt_str = "{:0" + str(len(col_match.group(2)) - 2) + "d}"
                fn = "{}{}{}".format(col_match.group(1), fmt_str.format(col + self.args.start_col), col_match.group(3))

                if os.path.exists(os.path.join(self.args.image_dirpath, fn)):
                    t = img_tile.Tile(grid_row, grid_col, os.path.join(self.args.image_dirpath, fn), disable_cache=self.args.disable_mem_cache)
                    self.tiles[grid_row][grid_col] = t
                grid_col += col_incrementer
            grid_row += row_incrementer


class TileGridSequential(TileGrid):

    positionPattern = "(.*)(\\{[p]+\\})(.*)"

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)

        self._filename_pattern = self.args.filename_pattern
        time_matcher = re.compile(self.timePattern)
        time_match = time_matcher.match(self._filename_pattern)
        if time_match is not None:
            if self.args.time_slice is None:
                raise RuntimeError("Filename pattern has a time component \"{t+}\", so a time slice is required.")
            fmt_str = "{:0" + str(len(time_match.group(2)) - 2) + "d}"
            self._filename_pattern = "{}{}{}".format(time_match.group(1), fmt_str.format(self.args.time_slice), time_match.group(3))

        self._sequential_matcher = re.compile(self.positionPattern)

        if self.args.numbering_pattern == 'HORIZONTALCOMBING':
            self._fill_numbering_by_row()
        elif self.args.numbering_pattern == 'HORIZONTALCONTINUOUS':
            self._fill_numbering_by_row_chained()
        elif self.args.numbering_pattern == 'VERTICALCOMBING':
            self._fill_numbering_by_col()
        elif self.args.numbering_pattern == 'VERTICALCONTINUOUS':
            self._fill_numbering_by_col_chained()
        else:
            raise RuntimeError("Unknown grid origin: {}".format(self.args.numbering_pattern))

        if self.args.grid_origin == 'UL':
            pass
        elif self.args.grid_origin == 'UR':
            self._reflect_numbering_vertical()
        elif self.args.grid_origin == 'LL':
            self._reflect_numbering_horizontal()
        elif self.args.grid_origin == 'LR':
            self._reflect_numbering_vertical()
            self._reflect_numbering_horizontal()
        else:
            raise RuntimeError("Unknown grid origin: {}".format(self.args.grid_origin))


    def _init_tile(self, r, c, index):
        seq_match = self._sequential_matcher.match(self._filename_pattern)
        fmt_str = "{:0" + str(len(seq_match.group(2)) - 2) + "d}"
        fn = "{}{}{}".format(seq_match.group(1), fmt_str.format(index), seq_match.group(3))
        if os.path.exists(os.path.join(self.args.image_dirpath, fn)):
            t = img_tile.Tile(r, c, os.path.join(self.args.image_dirpath, fn), disable_cache=self.args.disable_mem_cache)
            self.tiles[r][c] = t

    def _fill_numbering_by_row(self):
        index = self.args.start_tile
        for r in range(self.args.grid_height):
            for c in range(self.args.grid_width):
                self._init_tile(r, c, index)
                index += 1

    def _fill_numbering_by_row_chained(self):
        index = self.args.start_tile
        for r in range(self.args.grid_height):
            if r % 2 == 0:
                for c in range(self.args.grid_width):
                    self._init_tile(r, c, index)
                    index += 1
            else:
                for c in range(self.args.grid_width - 1, -1, -1):
                    self._init_tile(r, c, index)
                    index += 1

    def _fill_numbering_by_col(self):
        index = self.args.start_tile
        for c in range(self.args.grid_width):
            for r in range(self.args.grid_height):
                self._init_tile(r, c, index)
                index += 1

    def _fill_numbering_by_col_chained(self):
        index = self.args.start_tile
        for c in range(self.args.grid_width):
            if c % 2 == 0:
                for r in range(self.args.grid_height):
                    self._init_tile(r, c, index)
                    index += 1
            else:
                for r in range(self.args.grid_height - 1, -1, -1):
                    self._init_tile(r, c, index)
                    index += 1

    def _reflect_numbering_vertical(self):
        """
        reflect the grid numbering around the vertical axis
        """
        for r in range(self.height):
            for c in range(int(self.width / 2)):
                col_offset = self.width - c - 1
                tile = self.tiles[r][c]
                other = self.tiles[r][col_offset]
                if tile is not None and other is not None:
                    tmp_fp = tile.filepath
                    tmp_fn = tile.name
                    tile.name = other.name
                    tile.filepath = other.filepath
                    other.name = tmp_fn
                    other.filepath = tmp_fp
                if tile is not None and other is None:
                    self.tiles[r][col_offset] = tile
                    tile.c = col_offset
                    self.tiles[r][c] = None
                if tile is None and other is not None:
                    self.tiles[r][c] = other
                    other.c = c
                    self.tiles[r][col_offset] = None

    def _reflect_numbering_horizontal(self):
        """
        reflect the grid numbering around the vertical axis
        """
        for r in range(int(self.height / 2)):
            row_offset = self.height - r - 1
            for c in range(self.width):
                tile = self.tiles[r][c]
                other = self.tiles[row_offset][c]
                if tile is not None and other is not None:
                    tmp_fp = tile.filepath
                    tmp_fn = tile.name
                    tile.name = other.name
                    tile.filepath = other.filepath
                    other.name = tmp_fn
                    other.filepath = tmp_fp
                if tile is not None and other is None:
                    self.tiles[row_offset][c] = tile
                    tile.r = row_offset
                    self.tiles[r][c] = None
                if tile is None and other is not None:
                    self.tiles[r][c] = other
                    other.r = r
                    self.tiles[row_offset][c] = None



class TileGridFromCsv(TileGrid):

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)

        if not os.path.exists(self.args.grid_csv_filepath):
            raise RuntimeError("Grid csv file does not exist: {}".format(self.args.grid_csv_filepath))

        self.tiles = list()
        import pandas as pd
        df = pd.read_csv(self.args.grid_csv_filepath, header=None)
        self.height = df.shape[0]
        self.width = df.shape[1]
        # add grid size to args namespace
        self.args.grid_height = self.height
        self.args.grid_width = self.width


        # init a 2d list to hold Tiles
        self.tiles = [[None for _ in range(self.width)] for _ in range(self.height)]
        for row in range(self.height):
            for col in range(self.width):
                fn = df.iloc[row, col]
                if not isinstance(fn, str):
                    continue
                fn = fn.strip()
                if len(fn) == 0:
                    continue
                if os.path.exists(os.path.join(self.args.image_dirpath, fn)):
                    t = img_tile.Tile(row, col, os.path.join(self.args.image_dirpath, fn), disable_cache=self.args.disable_mem_cache)
                    self.tiles[row][col] = t