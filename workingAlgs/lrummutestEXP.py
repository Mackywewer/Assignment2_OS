import unittest
from lrummuEXP import lruMMU  # make sure this file is in the same folder or PYTHONPATH

class TestLruMMU(unittest.TestCase):
    def setUp(self):
        frames = 3
        debug = True
        self.mmu = lruMMU(frames, debug=debug)  # consistent attribute

    def test_sequence(self):
        # Define a sequence of (page_number, is_write) accesses
        sequence = [
            (1, False),
            (2, True),
            (1, False),
            (3, False),
            (4, False),
            (6, False),
            (8, True),
            (1, False),
            (4, False),
            (4, False)
        ]

        for page_number, is_write in sequence:
            if is_write:
                pf = self.mmu.write_memory(page_number)
                action = "Write"
            else:
                pf = self.mmu.read_memory(page_number)
                action = "Read"

            status = "PAGE FAULT" if pf else "HIT"
            print(f"{action} page {page_number} -> {status}")
            self.mmu.print_page_table()

        # Final stats
        print("\nFinal Stats:")
        print(f"Page Faults : {self.mmu.get_total_page_faults()}")
        print(f"Disk Reads  : {self.mmu.get_total_disk_reads()}")
        print(f"Disk Writes : {self.mmu.get_total_disk_writes()}")
        pf_rate = self.mmu.get_total_page_faults() / len(sequence)
        print(f"Page Fault Rate: {pf_rate:.4f}")

if __name__ == "__main__":
    unittest.main()