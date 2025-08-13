import cProfile
import timeit
from os import walk
from os.path import exists, join

import libxb
from libxb.core.compress import ClapHanzHuffman, ClapHanzLZS
from libxb.core.streams import BufferStream, Endian, OpenMode

TEST_ROOT = "G:/dev/py/libxb/test_data"
TEST_GAME = "mingolonline"

IGNORE = []

DEBUG_FILE = None  # "outdir/mingol5/xbdata/course/course03/ground00.xb"

# with libxb.MNG5Archive("G:/dev/py/test_data/mRoomSel4.xb", "w") as arc:
#     arc.add(path="G:/dev/py/test_data/for_add", xb_path="../data/")


# with libxb.MNGPArchive("test_data/mRoomSel2.xb", "w") as arc:
#     arc.add(path="test_data/mRoomSel", xb_path="../")

# with open("LZ.BIN", "rb") as f:
#     lz_buf = f.read()
# with open("HUFF.BIN", "rb") as f:
#     huff_buf = f.read()


# def profiler_lz():
#     strm = BufferStream(OpenMode.READ, Endian.LITTLE, lz_buf)
#     ClapHanzLZS.decompress(strm)


# def profiler_huff():
#     strm = BufferStream(OpenMode.READ, Endian.LITTLE, huff_buf)
#     ClapHanzHuffman.decompress(strm)


# def profiler_full():
#     with libxb.MNGPArchive(f"{TEST_ROOT}/mRoomSel.xb", "r") as arc:
#         arc.extract_all(path="outdir/profiler/")


# # tm = min(timeit.repeat(profiler_huff, number=5, repeat=10000))
# # tm = min(timeit.repeat(profiler_lz, number=5, repeat=20000))
# tm = min(timeit.repeat(profiler_full, number=1, repeat=200))
# print(tm)

# cProfile.run("profiler_full()", sort="cumtime")


# exit(0)


###############################################
###############################################
###############################################


def try_extract(in_path, out_path):
    print(f"{in_path}:", end="")
    try:
        with libxb.MNGOArchive(in_path, "r") as arc:
            arc.extract_all(out_path)
    except Exception as e:
        print(f"FAIL ({e})")
        raise e

    print("OK")


started = False
print()

for wpath, wdirs, wnames in walk(f"{TEST_ROOT}/{TEST_GAME}"):
    for it in wnames:
        it = it.lower()
        if not it.endswith(".xb") and not it[:-1].endswith(".xb"):
            continue

        win = join(wpath, it).replace("\\", "/")
        wout = win.replace(TEST_ROOT, "outdir")

        if DEBUG_FILE and (wout != DEBUG_FILE and not started):
            continue

        started = True

        ignore = False
        for it in IGNORE:
            if wout.startswith(it):
                ignore = True
                break

        # print(wout)

        # if exists(wout):
        #     continue

        if ignore:
            continue

        try_extract(win, wout)

raise StopIteration("OK")

# from os import walk
# from os.path import exists, isdir, join

# import libxb

# # MGP2_ROOT = "G:/rom/psp/Hot Shots Golf - Open Tee 2 (USA) (FW3.96)/PSP_GAME/USRDIR/xbdata"
# MGP2_ROOT = "outdir"

# IGNORE = [
#     "outdir/crs/07",
#     "outdir/crs/08",
#     "outdir/crs/09",
#     "outdir/crs/10",
#     "outdir/crs/11",
#     "outdir/crs/12",
#     "outdir/tnk/result/Model/r_stand",
# ]

# DEBUG_FILE = ""


# def try_extract(in_path, out_path):
#     with libxb.MNGPArchive(in_path, "r") as arc:
#         arc.extract_all(out_path)


# def try_create(in_path, out_path):
#     with libxb.MNGPArchive(in_path + ".xb", "w") as arc:
#         arc.add(in_path, xb_path="../", recursive=True)


# started = False

# for wpath, wdirs, wnames in walk(MGP2_ROOT):
#     for it in wdirs:
#         # if not it.endswith(".xb") and not it.endswith(".xb1"):
#         #     continue

#         win = join(wpath, it).replace("\\", "/")
#         wout = win.replace(MGP2_ROOT, "outdir2")

#         if DEBUG_FILE and (wout != DEBUG_FILE and not started):
#             continue

#         started = True

#         ignore = False
#         for it in IGNORE:
#             if wout.startswith(it):
#                 ignore = True
#                 break

#         if exists(wout) or ignore:
#             continue

#         print(wout)

#         if isdir(win) and (win.endswith(".xb") or win.endswith(".xb1")):
#             try_create(win, wout)
