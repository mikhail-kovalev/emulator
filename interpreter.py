import yaml
import struct
import sys

class Interpreter:
    def __init__(self, memory_size=1024):
        self.memory = [0] * memory_size

    def load_constant(self, b, c):
        self.memory[c] = b
        print(f"LOAD_CONST executed: memory[{c}] = {b}")

    def read_mem(self, b, c):
        self.memory[c] = self.memory[b]
        print(f"READ_MEM executed: memory[{c}] = memory[{b}] = {self.memory[b]}")

    def write_mem(self, b, c):
        self.memory[b] = self.memory[c]
        print(f"WRITE_MEM executed: memory[{b}] = {self.memory[c]}")

    def bitreverse(self, b, c):
        if b < len(self.memory) and c < len(self.memory):
            self.memory[c] = int('{:08b}'.format(self.memory[b])[::-1], 2)
            print(f"BITREVERSE executed: memory[{c}] = {self.memory[c]}")
        else:
            print(f"Error: Address {c} is out of bounds")

    def interpret(self, input_file, output_file, memory_range):
        if memory_range[1] > len(self.memory):
            print(f"Error: Memory range {memory_range} is out of bounds.")
            return

        try:
            with open(input_file, 'rb') as f:
                binary_data = f.read()
        except FileNotFoundError:
            print(f"Error: Input file '{input_file}' not found.")
            return

        i = 0
        while i < len(binary_data):
            a = binary_data[i]
            if a == 36:  # LOAD_CONST (5 байт)
                b = int.from_bytes(binary_data[i + 1:i + 4], byteorder='little')
                c = binary_data[i + 4]
                print(f"Command LOAD_CONST found: B={b}, C={c}")
                self.load_constant(b, c)
                i += 5
            elif a == 55:  # READ_MEM (4 байта)
                b, c = struct.unpack_from("HH", binary_data, i + 1)
                print(f"Command READ_MEM found: B={b}, C={c}")
                self.read_mem(b, c)
                i += 4
            elif a == 84:  # WRITE_MEM (4 байта)
                b, c = struct.unpack_from("HH", binary_data, i + 1)
                print(f"Command WRITE_MEM found: B={b}, C={c}")
                self.write_mem(b, c)
                i += 4
            elif a == 186:  # BITREVERSE (4 байта)
                # Используем 1 байт для `a`, 2 байта для `b`, и 1 байт для `c`
                b = int.from_bytes(binary_data[i + 1:i + 3], byteorder='little')
                c = binary_data[i + 3]
                print(f"Command BITREVERSE found: B={b}, C={c}")
                self.bitreverse(b, c)
                i += 4
            else:
                print(f"Unknown Command A={a} at position {i}")
                break

        result = {'memory_range': memory_range, 'values': self.memory[memory_range[0]:memory_range[1]]}
        
        try:
            with open(output_file, 'w') as f:
                yaml.dump(result, f)
            print(f"Result successfully written to {output_file}")
        except Exception as e:
            print(f"Error writing to output file '{output_file}': {e}")

# Запуск интерпретатора с аргументами командной строки
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python3 interpreter.py <input_file> <output_file> <memory_start> <memory_end>")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        memory_start = int(sys.argv[3])
        memory_end = int(sys.argv[4])
        memory_range = (memory_start, memory_end)
        
        interpreter = Interpreter()
        interpreter.interpret(input_file, output_file, memory_range)
