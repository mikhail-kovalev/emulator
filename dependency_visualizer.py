import argparse
import subprocess
import os

def get_dependencies(package_name, max_depth):
    # Функция рекурсивно определяет зависимости пакета
    dependencies = {}

    def fetch_deps(pkg, current_depth):
        if current_depth > max_depth:
            return
        if pkg in dependencies:  # Проверяем, если пакет уже обработан
            return
        try:
            result = subprocess.run(
                ['pip', 'show', pkg],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.split('\n'):
                if line.startswith('Requires'):
                    deps = line.split(':')[1].strip().split(', ')
                    dependencies[pkg] = [dep.strip() for dep in deps if dep.strip()]
                    print(f"Dependencies for {pkg}: {dependencies[pkg]}")  # Отладочный вывод
                    for dep in dependencies[pkg]:
                        fetch_deps(dep.strip(), current_depth + 1)
                elif line.startswith('Name'):
                    if pkg not in dependencies:
                        dependencies[pkg] = []  # Установленный пакет без зависимостей
                    print(f"{pkg} has no dependencies.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to fetch dependencies for {pkg}: {e}")  # Отладочный вывод


    fetch_deps(package_name, 0)
    if not dependencies:
        print(f"No dependencies found for {package_name}.")  # Отладочный вывод
    return dependencies


def create_mermaid_graph(dependencies):
    # Создаем описание графа в формате Mermaid
    lines = ['graph TD']
    for pkg, deps in dependencies.items():
        for dep in deps:
            lines.append(f'    {pkg} --> {dep}')  # Убираем лишние пробелы
    return '\n'.join(lines)

def save_mermaid_graph(graph_description, output_file, path_to_visualizer):
    # Сохраняем граф в файл .mmd
    mermaid_file = 'graph.mmd'
    with open(mermaid_file, 'w') as f:
        f.write(graph_description)

    # Используем Mermaid CLI для создания изображения PNG
    try:
        subprocess.run([path_to_visualizer, '-i', mermaid_file, '-o', output_file], check=True)
        print(f"Graph successfully saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while generating the graph: {e}")
        raise 
    finally:
        os.remove(mermaid_file)


def main():
    parser = argparse.ArgumentParser(description="Python package dependency visualizer")
    parser.add_argument('--path-to-visualizer', required=True, help="Path to the mmdc executable")
    parser.add_argument('--package-name', required=True, help="Name of the package to analyze")
    parser.add_argument('--output-file', required=True, help="Output file for the dependency graph (PNG)")
    parser.add_argument('--max-depth', type=int, default=3, help="Maximum depth of dependency analysis")
    args = parser.parse_args()

    dependencies = get_dependencies(args.package_name, args.max_depth)
    graph_description = create_mermaid_graph(dependencies)
    print("Graph description:")
    print(graph_description)  # Отладочный вывод
    if not graph_description.strip():  # Проверка на пустой граф
        print("Graph description is empty. No graph will be created.")
        return
    save_mermaid_graph(graph_description, args.output_file, args.path_to_visualizer)

if __name__ == '__main__':
    main()
