from mmu import MMU

"""Use bit: was it recently accessed? set bit to 1 if yes. 
'circular list/clock': hand moves around until it finds a victim
if use bit = 0, evict that page
"""
class ClockMMU(MMU):
    def __init__(self, frames, debug=False):
        self.frames = frames
        self.debug = debug
        self.clock_hand = 0            # start the clock at frame 0
        self.use_bits = [0] * frames   # track use/reference bits per frame

        # frame -> page mapping
        self.frame_table = [None] * frames

        # page -> frame mapping
        self.table = {}

        # set of pages currently marked dirty
        self.dirty_pages = set()

        # track  recently used
        self.last_used = {}  
        self.access_counter = 0

        # stats
        self.page_faults = 0
        self.disk_reads = 0
        self.disk_writes = 0
        self.disk_accesses = 0

    def set_debug(self):
        self.debug = True

    def reset_debug(self):
        self.debug = False
    
    def get_frame(self, page_number):
        return self.table.get(page_number)

    def set_frame(self, page_number, frame):
        self.table[page_number] = frame
        self.frame_table[frame] = page_number

    def is_frame_empty(self, frame):
        return self.frame_table[frame] is None

    def get_frame_content(self, frame):
        return self.frame_table[frame]

    def set_frame_content(self, frame, content):
        old = self.frame_table[frame]
        if old is not None and old in self.table:
            del self.table[old]
        self.frame_table[frame] = content
        if content is not None:
            self.table[content] = frame
    
    def _allocate_frame_for(self, page_number):
        # 1. Check for a free frame first
        for idx, occupant in enumerate(self.frame_table):
            if occupant is None:
                self.use_bits[idx] = 1   # first access sets use bit
                return idx
        

        # 2. No free frame: apply Clock replacement
        while True:
            frame = self.clock_hand
            occupant = self.frame_table[frame]

            if self.use_bits[frame] == 0:
                # Evict this page
                if self.debug:
                    print(f"Evicting page {occupant} from frame {frame}")

                # Write back if dirty
                if occupant in self.dirty_pages:
                    self.disk_writes += 1
                    self.dirty_pages.remove(occupant)
                    if self.debug:
                        print(f"Writing dirty page {occupant} to disk (disk_writes={self.disk_writes})")

                # Remove old page mapping
                if occupant in self.table:
                    del self.table[occupant]

                # Install new page
                self.frame_table[frame] = None
                self.use_bits[frame] = 0

                # Advance clock hand for next replacement
                self.clock_hand = (self.clock_hand + 1) % self.frames
                return frame

            else:
                # Give a second chance
                self.use_bits[frame] = 0
                self.clock_hand = (self.clock_hand + 1) % self.frames


    def read_memory(self, page_number):
        """Simulate a read access. Increment counter once per call."""
        self.access_counter += 1  # only once per step

        if page_number in self.table:  # HIT
            if self.debug:
                
                print(f"Read hit: page {page_number} in frame {self.table[page_number]}")
                print("="*50 + "\n")
            self.last_used[page_number] = self.access_counter  # update LRU
            frame = self.table[page_number]
            self.use_bits[frame] = 1  # mark as recently used
            return False

        # PAGE FAULT
        self.page_faults += 1
        self.disk_reads += 1
        frame = self._allocate_frame_for(page_number)

        # install mapping
        self.frame_table[frame] = page_number
        self.table[page_number] = frame
        self.last_used[page_number] = self.access_counter  # update LRU after allocation
        self.use_bits[frame] = 1

        if self.debug:
            print(f"Read miss: loading page {page_number} into frame {frame} (disk_reads={self.disk_reads})")
            print("="*50 + "\n")

        return True

    def write_memory(self, page_number):
        """Simulate a write access. Increment counter once per call."""
        self.access_counter += 1  # only once per step

        if page_number in self.table:  # HIT
            self.dirty_pages.add(page_number)
            self.last_used[page_number] = self.access_counter  # update LRU
            frame = self.table[page_number]
            self.use_bits[frame] = 1  # mark as recently used
            if self.debug:
                print(f"Write hit: marked page {page_number} dirty in frame {self.table[page_number]}")
                print("="*50 + "\n")
            return False

        # PAGE FAULT
        self.page_faults += 1
        self.disk_reads += 1
        frame = self._allocate_frame_for(page_number)

        # install mapping and mark dirty
        self.frame_table[frame] = page_number
        self.table[page_number] = frame
        self.dirty_pages.add(page_number)
        self.last_used[page_number] = self.access_counter  # update LRU after allocation
        self.use_bits[frame] = 1

        if self.debug:
            print(f"Write miss: loading page {page_number} into frame {frame} (disk_reads={self.disk_reads})")
            print("="*50 + "\n")

        return True

    def get_total_disk_reads(self):
        return self.disk_reads

    def get_total_disk_writes(self):
        return self.disk_writes

    def get_total_page_faults(self):
        return self.page_faults
    
    def get_disk_accesses(self):
        return self.disk_accesses

    def print_page_table(self):
        if not self.debug:
            return
        table = ['-'] * self.frames
        for i, page in enumerate(self.frame_table):
            if page is not None:
                table[i] = str(page)
        print("Page Table:", " ".join(table))
        print("-" * 40)

    # -------------------------------------------------
    # Trace runner
    # -------------------------------------------------
    def run_trace_file(filename, mmu, debug=False):
        PAGE_SIZE = 4096

        if debug:
            print("\n" + "="*50)
            print(f"Running trace from {filename}")
            print("="*50 + "\n")

        with open(filename, 'r') as f:
            step_num = 1
            for line in f:
                line = line.strip()
                if not line:
                    continue
                addr, rw = line.split()
                page_number = int(addr, 16) // PAGE_SIZE
                is_write = (rw.upper() == 'W')

                if is_write:
                    pf = mmu.write_memory(page_number)
                    action = "Write"
                else:
                    pf = mmu.read_memory(page_number)
                    action = "Read"

                if debug:
                    status = "PAGE FAULT" if pf else "HIT"
                    print(f"Step {step_num}: {action} page {page_number} -> {status}")
                    mmu.print_page_table()

                step_num += 1
                mmu.disk_accesses += 1



        # Final stats
        print("\nFinal Stats:")
        print(f"Page Faults : {mmu.get_total_page_faults()}")
        print(f"Disk Reads  : {mmu.get_total_disk_reads()}")
        print(f"Disk Writes : {mmu.get_total_disk_writes()}")
        print(f"Total accesses: {mmu.get_disk_accesses()}")

        # Page Fault Rate
        if mmu.get_disk_accesses() > 0:
            rate = mmu.get_total_page_faults() / mmu.get_disk_accesses()
            print(f"Page Fault Rate: {rate:.4f}")
        else:
            print("Page Fault Rate: N/A")


        print("="*50)




    # -------------------------------------------------
    # CLI Entry
    # -------------------------------------------------
    if __name__ == "__main__":
        if len(sys.argv) != 5:
            print("Usage: python3 randmmu.py <trace_file> <num_frames> <algorithm> <mode>")
            sys.exit(1)

        trace_file = sys.argv[1]
        num_frames = int(sys.argv[2])
        algorithm = sys.argv[3].lower()
        mode = sys.argv[4].lower()
        debug = mode == "debug"

        if algorithm == "rand":
            mmu = lruMMU(num_frames, debug=debug)
        else:
            print(f"Algorithm '{algorithm}' not implemented yet.")
            sys.exit(1)

        run_trace_file(trace_file, mmu, debug=debug)