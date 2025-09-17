from randmmu import RandMMU
import unittest

class TestRandMMU(unittest.TestCase):
    def setUp(self):
        self.rand_mmu = RandMMU(10)       

    def test_insert_numbers(self):
        for i in range(0, self.rand_mmu.frames):
            self.insert_number(i)
            self.print_page_table(self.rand_mmu)

    def insert_number(self, number):
        for frame in range(self.rand_mmu.frames):
            if self.rand_mmu.is_frame_empty(frame):
                if frame == 0:
                    self.rand_mmu.set_frame_content(frame, 0)
                self.rand_mmu.set_frame_content(frame, number)
                break
    def print_page_table(self, mmu):
    
        print("Page Table:")
        table = ['-'] * mmu.frames
        for page, frame in mmu.table.items():
            if frame < len(table):
                table[frame] = str(page)
        print(' '.join(table))

if __name__ == '__main__':
    unittest.main()