from ReadWriteMem import ReadWriteMemory
import ctypes
from time import sleep

def read_dmc_concentration():
    rwm = ReadWriteMemory()
    # Create Process Instance
    process = rwm.get_process_by_name('DevilMayCry5.exe')
    process.open()

    # Base Offset
    base_offset = 0X7E61B90

    module_addr = int(str(process.base_addr), 0) + int(str(base_offset), 0)
    concentration_ptr = process.get_pointer(lp_base_address=module_addr, offsets=[0x78, 0x1B50])
    print('Pointer Address:',hex(concentration_ptr))
    c = process.read_float(concentration_ptr)
    print("Concentration val:", c)
    process.close()

def write_dmc_concentration():
    rwm = ReadWriteMemory()
    # Create Process Instance
    process = rwm.get_process_by_name('DevilMayCry5.exe')
    process.open()

    # Base Offset
    base_offset = 0X7E61B90

    module_addr = int(str(process.base_addr), 0) + int(str(base_offset), 0)
    concentration_ptr = process.get_pointer(lp_base_address=module_addr, offsets=[0x78, 0x1B50])
    print('Pointer Address:', hex(concentration_ptr))
    state = process.write(concentration_ptr, 220)

    print(state)

if __name__ == '__main__':
    read_dmc_concentration()
    write_dmc_concentration();