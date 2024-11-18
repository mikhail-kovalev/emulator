import json
import re
import sys

class ConfigTranslator:
    def __init__(self):
        self.constants = {}

    def validate_name(self, name):
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', name):
            raise ValueError(f"Invalid name format: {name}")
        return name

    def parse_constant(self, name, value):
        name = self.validate_name(name)  # Validate the name format
        if isinstance(value, int) or isinstance(value, str):
            self.constants[name] = value
        elif isinstance(value, list):
            self.constants[name] = self.parse_list(value)
        else:
            raise ValueError(f"Unsupported constant value: {value}")

    def parse_list(self, items):
        parsed_items = [self.parse_value(item) for item in items]
        return f"list({', '.join(parsed_items)})"

    def parse_value(self, value):
        if isinstance(value, int):
            return str(value)
        elif isinstance(value, str):
            return f"[[{value}]]"
        elif isinstance(value, list):
            return self.parse_list(value)
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")

    def concat(self, *args):
        return ''.join(str(self.constants.get(arg, arg)) for arg in args)

    def ord_func(self, arg):
        value = self.constants.get(arg, arg)
        if isinstance(value, str) and len(value) > 0:
            return ord(value[0])
        raise ValueError(f"ord() requires a non-empty string, got: {value}")

    def parse_expression(self, expr):
        # Скорректируем регулярное выражение для поддержки пробелов и операторов
        match = re.match(r'\$\{([+\-*]|concat|ord)\s+([^\}]+)\}', expr)
        if not match:
            raise ValueError(f"Invalid expression format: {expr}")

        op, args = match.groups()
        args = args.split()
    
        if op == '+':
            return int(self.constants.get(args[0], args[0])) + int(self.constants.get(args[1], args[1]))
        elif op == '-':
            return int(self.constants.get(args[0], args[0])) - int(self.constants.get(args[1], args[1]))
        elif op == '*':
            return int(self.constants.get(args[0], args[0])) * int(self.constants.get(args[1], args[1]))
        elif op == "concat":
            return self.concat(*args)
        elif op == "ord":
            return self.ord_func(args[0])
        else:
            raise ValueError(f"Unsupported operation: {op}")



    def translate(self, json_data):
        output_lines = []
        for key, value in json_data.items():
            if key == "const":
                for const_name, const_value in value.items():
                    self.parse_constant(const_name, const_value)
                    output_lines.append(f"const {const_name} = {self.parse_value(const_value)}")
            elif key == "expression":
                result = self.parse_expression(value)
                output_lines.append(f"expression result = {result}")
            elif key == "comment":
                if isinstance(value, str):
                    output_lines.append(f"|| {value}")
                elif isinstance(value, list) and len(value) == 2:
                    output_lines.append(f"=begin\n{value[0]}\n=cut")
            else:
                output_lines.append(f"{key} = {self.parse_value(value)}")
        return "\n".join(output_lines)

def main():
    input_data = json.load(sys.stdin)
    output_path = sys.argv[1] if len(sys.argv) > 1 else "output.txt"

    translator = ConfigTranslator()
    translated_text = translator.translate(input_data)

    with open(output_path, 'w') as output_file:
        output_file.write(translated_text)
        print(f"Configuration saved to {output_path}")

if __name__ == "__main__":
    main()
