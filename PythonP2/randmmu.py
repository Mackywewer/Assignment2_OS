from mmu import MMU

class RandMMU(MMU):
    def __init__(self, frames):
        self.frames = frames
        self.table = {}
    def get_frame(self, page_number):
        return self.table.get(page_number)

    def set_frame(self, page_number, frame):
        self.table[page_number] = frame

    def is_frame_empty(self, frame): 
        return frame not in self.table
    
    def get_frame_content(self, frame):
        return self.table[frame]
    
    def set_frame_content(self, frame, content):
        self.table[frame] = content
                  
    def set_debug(self):
        # TODO: Implement the method to set debug mode
        pass

    def reset_debug(self):
        # TODO: Implement the method to reset debug mode
        pass

    def read_memory(self, page_number):
        # TODO: Implement the method to read memory
        pass

    def write_memory(self, page_number):
        # TODO: Implement the method to write memory
        pass

    def get_total_disk_reads(self):
        # TODO: Implement the method to get total disk reads
        return -1

    def get_total_disk_writes(self):
        # TODO: Implement the method to get total disk writes
        return -1

    def get_total_page_faults(self):
        # TODO: Implement the method to get total page faults
        return -1
