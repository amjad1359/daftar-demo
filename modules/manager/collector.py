import os

def collect_all_codes(root_dir, output_file):
    ignored_dirs = {'__pycache__', '.git', 'venv', 'env', 'python_packages', 'uploads', 'file_upload'}
    # پسوندهای مجاز برای جمع‌آوری
    allowed_extensions = ('.py', '.html', '.js', '.css', '.json', '.xml', '.yaml', '.yml', '.md')

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in ignored_dirs]
            for file in files:
                # فایل خود اسکریپت را رد کن
                if file == os.path.basename(__file__):
                    continue
                if file.endswith(allowed_extensions):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, root_dir)
                    outfile.write(f"\n{'='*80}\n")
                    outfile.write(f" FILE: {relative_path}\n")
                    outfile.write(f"{'='*80}\n\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                    except Exception as e:
                        outfile.write(f"Error reading file: {e}")
                    outfile.write("\n\n")

if __name__ == "__main__":
    current_directory = os.getcwd()
    output_filename = "all_project_codes.txt"
    print(f"در حال جمع‌آوری کدها از: {current_directory}")
    collect_all_codes(current_directory, output_filename)
    print(f"تمامی کدها با موفقیت در فایل {output_filename} ذخیره شدند.")