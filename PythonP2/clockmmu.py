from mmu import MMU


class ClockMMU(MMU):
    def __init__(self, frames):
        self.frames = frames
        self.frames_table = [None] * frames

        self.reference_bits = [0] * frames

        self.dirty_bits = [0] * frames

        self.page_to_frame = {}

        self.clock_hand = 0
        self.page_faults = 0
        self.disk_reads = 0
        self.disk_writes = 0
        self.debug = False

    def set_debug(self):
        self.debug = True

    def reset_debug(self):
        self.debug = False

    def read_memory(self, page_number):
        if page_number in self.page_to_frame:
            frame_index = self.page_to_frame[page_number]
            self.reference_bits[frame_index] = 1
            if self.debug:
                print(f"Read hit: Page {page_number} found in frame {frame_index}.")
            return False
        
        self.page_faults += 1
        self.disk_reads += 1
        frame = self._allocate_frame_for(page_number, is_write=False)

        self.frames_table[frame] = page_number
        self.page_to_frame[page_number] = frame
        self.reference_bits[frame] = 1
        self.dirty_bits[frame] = 0

        if self.debug:
            print(f"Read miss: loading page {page_number} into frame {frame} (disk reads={self.disk_reads}).")
        return True

    def write_memory(self, page_number):
        if page_number in self.page_to_frame:
            frame_index = self.page_to_frame[page_number]
            self.reference_bits[frame] = 1
            self.dirty_bits[frame] = 1
            if self.debug:
                print(f"Write hit: marked page {page_number} dirty in frame {frame}.")
            return False
        self.page_faults += 1
        self.disk_reads += 1
        frame = self._allocate_frame_for(page_number, is_write=True)
        self.frames_table[frame] = page_number
        self.page_to_frame[page_number] = frame
        self.reference_bits[frame] = 1
        self.dirty_bits[frame] = 1
        if self.debug:
            print(f"Write miss: loading page {page_number} into frame {frame} (disk reads={self.disk_reads}).")
        return True
    
    def _allocate_frame_for(self, page_number, is_write):
        for i in range(self.frames):
            if self.frames_table[i] is None:
                if self.debug:
                    print(f"Allocating free frame {i} for page {new_page}.")
                return i
        
        victim = self._clock_select(prefer_dirty=False)
        if victim is None:
            victim = self._clock_select(prefer_dirty=True)
        victim_page = self.frames_table[victim]
        if self.dirty_bits[victim] == 1:
            self.disk_writes += 1
            if self.debug:
                print(f"Writing dirty page {victim_page} to disk {victim} (disk writes={self.disk_writes}).")
        else:
            if self.debug:
                print(f"Evicting clean page {victim_page} from frame {victim}.")

        if victim_page in self.page_to_frame:
            del self.page_to_frame[victim_page]
        
        return victim
    
    def _clock_select(self, prefer_dirty):
        target_dirty = 1 if prefer_dirty else 0
        scanned = 0
        frames = self.frames

        while scanned < frames:
            idx  = self.clock_hand
            R = self.reference_bits[idx]
            D = self.dirty_bits[idx]

            if R == 0 and D == target_dirty:
                chosen = idx
                self.clock_hand = (self.clock_hand + 1) % frames
                return chosen
            
            if R == 1:
                self.reference_bits[idx] = 0
            
            self.clock_hand = (self.clock_hand + 1) % frames
            scanned += 1
        return None

    def get_total_disk_reads(self):
        return self.disk_reads

    def get_total_disk_writes(self):
        return self.disk_writes

    def get_total_page_faults(self):
        return self.page_faults
