def remove_duplicates(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 使用集合(set)来去除重复行
    unique_lines = set(lines)

    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(unique_lines)


# 示例：去除重复行并保存到新文件
remove_duplicates('unsaved_line_id.txt', 'output.txt')
