# randmmutest.py
import unittest
from randmmuEXP import RandMMU
import random

class TestRandMMU(unittest.TestCase):
    def setUp(self):
        self.rand_mmu = RandMMU(5, debug=True)  # debug ON

    def test_sequence(self):
        self.rand_mmu.read_memory(1)
        self.rand_mmu.print_page_table()
        self.rand_mmu.write_memory(2)
        self.rand_mmu.print_page_table()
        self.rand_mmu.read_memory(1)
        self.rand_mmu.print_page_table()
        self.rand_mmu.read_memory(3)
        self.rand_mmu.print_page_table()
        self.rand_mmu.read_memory(4)  
        self.rand_mmu.print_page_table()
        self.rand_mmu.read_memory(6)
        self.rand_mmu.print_page_table()
        self.rand_mmu.write_memory(8)
        self.rand_mmu.print_page_table()
        self.rand_mmu.read_memory(1)
        self.rand_mmu.print_page_table()
        self.rand_mmu.read_memory(4)
        self.rand_mmu.print_page_table()
        self.rand_mmu.read_memory(4)  
        self.rand_mmu.print_page_table()

        print("\nFinal stats:")
        print("Page Faults:", self.rand_mmu.get_total_page_faults())
        print("Disk Reads:", self.rand_mmu.get_total_disk_reads())
        print("Disk Writes:", self.rand_mmu.get_total_disk_writes())

if __name__ == '__main__':
    unittest.main()