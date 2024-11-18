import yaml
import struct

class Assembler:
    def __init__(self):
        self.instructions = []

    def parse_instruction(self, line):
        parts = line.split()
        command = parts[0]
        if command == "LOAD_CONST":
            a, b, c = 36, int(parts[1]), int(parts[2])
            self.instructions.append((a, b, c, 5))  # 5 байт для LOAD_CONST
        elif command == "READ_MEM":
            a, b, c = 55, int(parts[1]), int(parts[2])
            self.instructions.append((a, b, c, 4))  # 4 байта для READ_MEM
        elif command == "WRITE_MEM":
            a, b, c = 84, int(parts[1]), int(parts[2])
            self.instructions.append((a, b, c, 4))  # 4 байта для WRITE_MEM
        elif command == "BITREVERSE":
            a, b, c = 186, int(parts[1]), int(parts[2])
            self.instructions.append((a, b, c, 4))  # 4 байта для BITREVERSE

    def assemble(self, input_file, output_file, log_file):
        with open(input_file, 'r') as f:
            lines = f.readlines()

        binary_data = bytearray()
        log_entries = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            self.parse_instruction(line)

        for instr in self.instructions:
            a, b, c, size = instr
            if size == 5:
                # Упаковка для 5-байтовой команды: 1 байт `a`, 3 байта `b`, 1 байт `c`
                b_bytes = b.to_bytes(3, byteorder='little')
                bytes_data = bytes([a]) + b_bytes + bytes([c])
            else:
                # Упаковка для 4-байтовых команд
                # Специальная упаковка для BITREVERSE: 1 байт `a`, 2 байта `b`, 1 байт `c`
                if a == 186:  # BITREVERSE
                    bytes_data = bytes([a]) + b.to_bytes(2, byteorder='little') + bytes([c])
                else:
                    bytes_data = struct.pack("BHH", a, b, c)
            binary_data.extend(bytes_data)

            # Отладка: вывод байтов каждой команды
            print(f"Instruction: A={a}, B={b}, C={c}, Bytes: {[f'0x{byte:02X}' for byte in bytes_data]}")

            # Определение имени команды для лог-файла
            instruction_name = (
                "LOAD_CONST" if a == 36 else
                "READ_MEM" if a == 55 else
                "WRITE_MEM" if a == 84 else
                "BITREVERSE"
            )

            log_entries.append({
                'instruction': instruction_name,
                'A': a,
                'B': b,
                'C': c,
                'bytes': [f"0x{byte:02X}" for byte in bytes_data]
            })

        # Запись в бинарный файл
        with open(output_file, 'wb') as f:
            f.write(binary_data)

        # Запись лога в YAML файл
        with open(log_file, 'w') as f:
            yaml.dump(log_entries, f)

# Пример использования:
assembler = Assembler()
assembler.assemble('program.asm', 'program.bin', 'program.log')
