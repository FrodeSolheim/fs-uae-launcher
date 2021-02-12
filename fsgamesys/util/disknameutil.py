import os
import re
import unittest

from fsgamesys.util.gamenameutil import GameNameUtil


class DiskNameUtil(object):
    @classmethod
    def find_disks(
        cls, path, base_names=None, script=None, file_list=None, black_list={}
    ):
        disks = [path]
        print("")
        print("FIRST DISK", path)
        print("")
        # disks = []
        if script:
            use_name = script.rename_file(os.path.basename(path))
        else:
            use_name = os.path.basename(path)
        number = GameNameUtil.find_number(use_name)
        disk_count = GameNameUtil.find_disk_count(use_name)
        first_without_number = GameNameUtil.strip_number(use_name)
        first_without_flags = GameNameUtil.strip_flags(first_without_number)
        if number is None:
            # only this disk
            return disks
        base_name = GameNameUtil.find_base_name(path)
        dir = os.path.dirname(path)
        candidates = {}
        items = []
        if base_names:
            items = base_names[base_name]
        else:
            if file_list:
                all_items = file_list
            else:
                all_items = os.listdir(dir)
            for item in all_items:
                b = GameNameUtil.find_base_name(item)
                if base_name == b:
                    items.append(item)
        # print("items is", items)
        for item in items:
            if script:
                use_name = script.rename_file(item)
            else:
                use_name = item
            # print(item)
            if GameNameUtil.is_bad_dump(use_name):
                continue
            if GameNameUtil.find_disk_count(use_name) != disk_count:
                continue
            n = GameNameUtil.find_number(use_name)
            if n == 0:
                n = 99
            if n:
                candidates.setdefault(n, []).append(
                    (use_name, os.path.join(dir, item))
                )
        # print(candidates)
        for n, items in candidates.items():
            if n == 1:
                # already added first floppy
                continue
            print("")
            print("Candidates:")
            for item in items:
                print(item[0])
            print("")
            print("FIND FLOPPY NUMBER", n)
            print("")
            matches = []
            for use_name, p in items:
                without_number = GameNameUtil.strip_number(use_name)
                print(without_number, "vs", first_without_number)
                if without_number == first_without_number:
                    # print("perfect match:", p)
                    # disks.append(p)
                    matches.append((-1000, p))
                    continue
                    # break
                without_flags = GameNameUtil.strip_flags(without_number)
                if without_flags == first_without_flags:

                    flags_1 = extract_flags(first_without_number)
                    cr_flag_1 = ""
                    for flag in flags_1:
                        if flag.startswith("cr"):
                            cr_flag_1 = flag

                    flags_n = extract_flags(without_number)
                    cr_flag_n = ""
                    for flag in flags_n:
                        if flag.startswith("cr"):
                            cr_flag_n = flag

                    score = 0

                    # if cr_flag_n and cr_flag_1 != cr_flag_n:
                    if cr_flag_1 and cr_flag_n and cr_flag_1 != cr_flag_n:
                        # not same cracker
                        score += 10000

                    if "[o" in without_number:
                        score += 20000

                    flag_set_1 = set(flags_1)
                    flag_set_n = set(flags_n)

                    extra_flags_in_1 = flag_set_1.difference(flag_set_n)
                    extra_flags_in_n = flag_set_n.difference(flag_set_1)

                    # score += len(extra_flags_in_1)
                    print(extra_flags_in_1)
                    for flag in extra_flags_in_1:
                        score += 10 - flags_1.index(flag)
                    score += len(extra_flags_in_n) * 100
                    print(score, p)
                    matches.append((score, p))

                    # if without_flags == without_number:
                    #     # there were no flags on this floppy
                    #     matches.append((1, p))
                    # else:
                    #     # slightly worse score since there were flags
                    #     # not matching floppy 1
                    #     matches.append((100, p))

            if len(matches) == 0:
                # raise Exception("no candidates for floppy " + num)
                # print("WARNING: choosing partial matching floppy", p,
                #         "for floppy number", n)
                # disks.append(p)
                print("Did not find good match for floppy", n)
                print("candidates:")
                for item in items:
                    print("  ", item)
                raise Exception(
                    "Did not find good match for floppy {0}".format(n)
                )
            matches.sort()

            print("")
            print("Matches:")
            for match in matches:
                print(match[0], match[1])
            print("")
            score, p = matches[0]
            # if score == 2:
            disks.append(p)
            # TOSEC (x of y) disk number labelling format
            if " of {0})".format(n) in path:
                # found the correct number of disks
                break
        print("")
        print("Result:")
        for disk in disks:
            print(disk)
        print("")
        return disks


flags_pattern = re.compile("\[([^\]]+)\]")


def extract_flags(name):
    matches = flags_pattern.findall(name)
    return [x.strip() for x in matches]


class TestGameDiskUtil(unittest.TestCase):
    def set_disks(self, s):
        self.all_disks = [x.strip() for x in s.split("\n") if x.strip()]

    def find_disks(self, name):
        return DiskNameUtil.find_disks(name, file_list=self.all_disks)

    def test_batman_the_movie(self):
        self.set_disks(BATMAN_THE_MOVIE)
        disks = self.find_disks(
            "Batman - The Movie (1989)(Ocean)(PAL)"
            "(Disk 1 of 2)[cr Black Monks].adf"
        )
        print(disks)

    def test_batman_the_movie_cr_qtx(self):
        self.set_disks(BATMAN_THE_MOVIE)
        disks = self.find_disks(
            "Batman - The Movie (1989)(Ocean)(PAL)(Disk 1 of 2)[cr QTX].adf"
        )
        self.assertEqual(
            disks,
            [
                "Batman - The Movie (1989)(Ocean)(PAL)(Disk 1 of 2)[cr QTX].adf",
                "Batman - The Movie (1989)(Ocean)(PAL)(Disk 2 of 2)[cr QTX].adf",
            ],
        )


BATMAN_THE_MOVIE = """
Batman - The Movie (1989)(Data East)(US)[cr].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 1 of 2)[cr Band][t +4 Band].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 1 of 2)[cr Band][t +4 Band][a].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 1 of 2)[cr Black Monks].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 1 of 2)[cr Dragons].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 1 of 2)[cr QTX].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 1 of 2)[cr QTX][a2].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 1 of 2)[cr QTX][a3].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 1 of 2)[cr QTX][a].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 1 of 2)[cr QTX][f NTSC QTX].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 1 of 2)[cr QTX][f NTSC].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 1 of 2)[cr QTX][h Phantasie - Bandidos].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 1 of 2)[cr QTX][h Phantasie].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 1 of 2)[cr QTX][h TFS].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 1 of 2)[cr QTX][t +4 Band].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 1 of 2)[cr QTX][t +4 Band][a].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 2 of 2)[cr Band][t +4 Band].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 2 of 2)[cr Band][t +4 Band][a].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 2 of 2)[cr Dragons].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 2 of 2)[cr QTX].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 2 of 2)[cr QTX][a bootblock].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 2 of 2)[cr QTX][a2 bootblock].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 2 of 2)[cr QTX][a3].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 2 of 2)[cr QTX][a4].adf
Batman - The Movie (1989)(Ocean)(PAL)(Disk 2 of 2)[cr QTX][a5].adf
Batman - The Movie (1989)(Ocean)(PAL)[cr][a][one disk version].adf
Batman - The Movie (1989)(Ocean)(PAL)[cr][one disk version].adf
Batman - The Movie (1991)(Hit Squad, The)(PAL).adf
"""

if __name__ == "__main__":
    unittest.main()
