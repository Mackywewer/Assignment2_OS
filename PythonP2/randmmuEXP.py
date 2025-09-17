from mmu import MMU    # keep if the skeleton expects subclassing
import random

class RandMMU(MMU):
    def __init__(self, frames, debug=False):
        # number of physical frames available
        self.frames = frames

        # page -> frame mapping (keeps compatibility with your print_page_table)
        self.table = {}       

        # frame -> page content (None if free)
        self.frame_table = [None] * frames

        # set of pages currently marked dirty
        self.dirty_pages = set()

        # statistics
        self.page_faults = 0
        self.disk_reads = 0
        self.disk_writes = 0

    def set_debug(self):
        self.debug = True

    def reset_debug(self):
        self.debug = False

    def read_memory(self, page_number):
        """Simulate a read access. Returns True if page fault occurred."""
        if page_number in self.table:  # HIT
            if self.debug:
                print(f"[HIT] Read page {page_number} (frame {self.table[page_number]})")
            return False

        # PAGE FAULT
        self.page_faults += 1
        self.disk_reads += 1

        if len(self.table) < self.frames:  # empty frame exists
            frame = len(self.table)
        else:  # need eviction
            evicted_page = random.choice(list(self.table.keys()))
            frame = self.table.pop(evicted_page)
            self.disk_writes += 1
            if self.debug:
                print(f"[EVICT] Page {evicted_page} -> replaced by page {page_number} in frame {frame}")

        self.table[page_number] = frame
        if self.debug:
            print(f"[PAGE FAULT] Loaded page {page_number} into frame {frame}")
        return True

    def write_memory(self, page_number):
        """Simulate a write access. Same as read, but marks page dirty (disk write if evicted)."""
        if page_number in self.table:  # HIT
            if self.debug:
                print(f"[HIT] Write page {page_number} (frame {self.table[page_number]})")
            return False

        # PAGE FAULT
        self.page_faults += 1
        self.disk_reads += 1

        if len(self.table) < self.frames:  # empty frame
            frame = len(self.table)
        else:  # eviction
            evicted_page = random.choice(list(self.table.keys()))
            frame = self.table.pop(evicted_page)
            self.disk_writes += 1
            if self.debug:
                print(f"[EVICT] Page {evicted_page} -> replaced by page {page_number} in frame {frame}")

        self.table[page_number] = frame
        if self.debug:
            print(f"[PAGE FAULT] Loaded page {page_number} into frame {frame}")
        return True
    # basic accessors (kept for compatibility)
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
        # map frame -> page and update table accordingly
        old = self.frame_table[frame]
        if old is not None and old in self.table:
            del self.table[old]
        self.frame_table[frame] = content
        if content is not None:
            self.table[content] = frame

    # debug toggles
    def set_debug(self):
        self.debug = True

    def reset_debug(self):
        self.debug = False

    # internal helper to find a free frame or evict randomly
    def _allocate_frame_for(self, page_number):
        # try to find a free frame first
        for idx, occupant in enumerate(self.frame_table):
            if occupant is None:
                return idx

        # no free frame: pick a random victim page
        victim_frame = random.randrange(self.frames)
        victim_page = self.frame_table[victim_frame]
        if self.set_debug:
            print(f"Evicting page {victim_page} from frame {victim_frame}")

        # if victim is dirty, write it back to disk
        if victim_page in self.dirty_pages:
            self.disk_writes += 1
            if self.set_debug:
                print(f"Writing dirty page {victim_page} to disk (disk_writes={self.disk_writes})")
            self.dirty_pages.remove(victim_page)

        # remove victim mapping
        if victim_page in self.table:
            del self.table[victim_page]

        # frame is now free for the new page
        return victim_frame

    # simulate read access
    def read_memory(self, page_number):
        if page_number in self.table:
            # hit: no disk read, no page fault
            if self.set_debug:
                print(f"Read hit: page {page_number} in frame {self.table[page_number]}")
            return False  # no page fault
        # miss -> page fault
        self.page_faults += 1
        frame = self._allocate_frame_for(page_number)
        # simulate disk read to load the page
        self.disk_reads += 1
        if self.set_debug:
            print(f"Read miss: loading page {page_number} into frame {frame} (disk_reads={self.disk_reads})")
        # install mapping
        self.table[page_number] = frame
        self.frame_table[frame] = page_number
        # reads do not make page dirty
        return True  # page fault occurred

    # simulate write access
    def write_memory(self, page_number):
        if page_number in self.table:
            # hit: mark dirty
            self.dirty_pages.add(page_number)
            if self.set_debug:
                print(f"Write hit: marked page {page_number} dirty in frame {self.table[page_number]}")
            return False
        # miss -> page fault
        self.page_faults += 1
        frame = self._allocate_frame_for(page_number)
        # simulate disk read to load the page before writing (typical assumption)
        self.disk_reads += 1
        if self.set_debug:
            print(f"Write miss: loading page {page_number} into frame {frame} (disk_reads={self.disk_reads})")
        # install mapping and mark dirty
        self.table[page_number] = frame
        self.frame_table[frame] = page_number
        self.dirty_pages.add(page_number)
        return True

    # stat getters
    def get_total_disk_reads(self):
        return self.disk_reads

    def get_total_disk_writes(self):
        return self.disk_writes

    def get_total_page_faults(self):
        return self.page_faults

    # pretty print (keeps your existing interface)
    def print_page_table(self):
        if not self.set_debug:
            return  # do nothing if debug is OFF
        
        print("Page Table:")
        table = ['-'] * self.frames
        for page, frame in self.table.items():
            if 0 <= frame < len(table):
                table[frame] = str(page)
        print(' '.join(table))
        print("-" *40)