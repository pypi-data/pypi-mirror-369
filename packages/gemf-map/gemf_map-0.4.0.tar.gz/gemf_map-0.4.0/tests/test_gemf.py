import os

import pytest

from gemf import GEMF


PERSISTANT_TEST_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "test_output"
)


def compare_gemf(
    gemf1: GEMF, gemf2: GEMF,
    keys = ['header_info', 'source_data', 'range_data', 'range_details'],
    message: str = "GEMF1 not equal GEMF2 @ {key}",
    check_data_bytes: bool = False,
):
    gemf1_dict = gemf1.to_dict()
    gemf2_dict = gemf2.to_dict()

    for key in keys:
        assert gemf1_dict["header"][key] == gemf2_dict["header"][key], message.format(key=key)

    assert len(gemf1_dict["data"]) == len(gemf2_dict["data"]), "Data of GEMF objects not equal"

    if check_data_bytes:
        for i, (data1, data2) in enumerate(zip(gemf1.data, gemf2.data)):
            try:
                assert data1.load_bytes() == data2.load_bytes(), f"Data bytes not equal for tile {i}"
            except:
                import pdb
                pdb.set_trace()


def test_gemf(tmpdir):
    example_file = "tests/map_data.gemf"

    # tmpdir = os.path.expanduser("~/code/GEMF/dev/test_tiles")
    # os.makedirs(tmpdir, exist_ok=True)

    outdir_example_tiles = os.path.join(tmpdir, "parsed")
    outfile_rewritten = os.path.join(outdir_example_tiles, "rewritten.gemf")

    # read example file and save tiles
    gemf = GEMF.from_file(example_file, lazy=False)
    gemf_dict_in = gemf.to_dict()
    gemf.save_tiles(outdir_example_tiles)


    # rewrite gemf file
    gemf.write(outfile_rewritten)
    gemf = GEMF.from_file(outfile_rewritten, lazy=False)
    gemf_dict_out = gemf.to_dict()


    # read from tiles
    gemf = GEMF.from_tiles(outdir_example_tiles, lazy=False)
    gemf_dict_tile = gemf.to_dict()

    for key in ['header_info', 'source_data', 'range_data', 'range_details']:
        assert gemf_dict_in["header"][key] == gemf_dict_out["header"][key], f"Input .gemf does not equal rewritten .gemf @ {key}"
        assert gemf_dict_in["header"][key] == gemf_dict_tile["header"][key], f"Input .gemf does not equal .gemf from tiles @ {key}"

    assert len(gemf_dict_in["data"]) == len(gemf_dict_out["data"]), "Data @ Input .gemf does not equal rewritten .gemf."
    assert len(gemf_dict_in["data"]) == len(gemf_dict_tile["data"]), "Data @ Input .gemf does not equal .gemf from tiles."


def test_crop(tmpdir):
    example_file = "data/example_files/az_maps_2017.gemf"

    # tmpdir = PERSISTANT_TEST_DIR
    # os.makedirs(tmpdir, exist_ok=True)

    outdir_example_tiles = os.path.join(tmpdir, "parsed")
    os.makedirs(outdir_example_tiles, exist_ok=True)
    outfile_rewritten = os.path.join(outdir_example_tiles, "rewritten.gemf")

    # read example file and crop
    gemf = GEMF.from_file(example_file, lazy=False)
    gemf_crop = gemf.crop(7, 60, 62, 36, 38, lazy=False)

    # serialize original GEMF
    gemf_crop.write(outfile_rewritten)
    gemf_crop.save_tiles(outdir_example_tiles)

    # load written gemf file
    gemf_crop_load = GEMF.from_file(outfile_rewritten, lazy=False)

    # read from tiles
    gemf_crop_tile = GEMF.from_tiles(outdir_example_tiles, lazy=False)

    gemf_crop._name = "gemf_crop"
    gemf_crop_load._name = "gemf_crop_load"
    gemf_crop_tile._name = "gemf_crop_tile"

    print()
    print("gemf_crop     ", gemf_crop.data[0].__dict__)
    print("gemf_crop_load", gemf_crop_load.data[0].__dict__)
    print("gemf_crop_tile", gemf_crop_tile.data[0].__dict__)

    compare_gemf(gemf_crop, gemf_crop_load, keys=['header_info', 'source_data', 'range_data'], check_data_bytes=True)
    compare_gemf(gemf_crop, gemf_crop_tile, keys=['header_info', 'source_data', 'range_data'], check_data_bytes=True)
    compare_gemf(gemf_crop_tile, gemf_crop_tile)

    # TODO: assert range_idx, tile_idx crop vs no-crop


def test_lazy_loading():
    example_file = "data/example_files/az_maps_2017.gemf"

    # get lazy and then load
    gemf_lazy = GEMF.from_file(example_file, lazy=True)
    gemf_lazy.load_details()

    # get greedy
    gemf_greedy = GEMF.from_file(example_file, lazy=False)

    # compare
    compare_gemf(gemf_greedy, gemf_lazy)
