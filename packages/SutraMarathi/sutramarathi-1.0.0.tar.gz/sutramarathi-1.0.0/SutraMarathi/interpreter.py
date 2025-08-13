import sys
import re
import os

# Marathi to Python keyword mapping
marathi_to_python = {
    # Basic I/O
    "sanga": "print",
    "vichara": "input",

    # Boolean
    "khare": "True",
    "chukiche": "False",

    # Conditions
    "jar": "if",
    "terjar": "elif",
    "naiter": "else",
    "sod": "pass",

    # Logical
    "aani": "and",
    "kimva": "or",
    "nako": "not",

    # Loops
    "pratek": "for",
    "joparyant": "while",
    "madhe": "in",
    "thamb": "break",
    "pudhe": "continue",

    # Functions
    "karya": "def",
    "parat_dya": "return",

    # Error Handling
    "prayatna": "try",
    "pakad": "except",
    "shevti": "finally",

    # Modules
    "aana": "import",
    "kadhun": "from",
    "navane": "as",

    # Classes
    "rachana": "class",
    "swayam": "self",
    "suruvat": "__init__",

    # File I/O
    "ughad": "open",
    "vacha": "read",
    "liha": "write",
    "band_kara": "close",
}

# Variable declarations
def handle_declarations(code: str) -> str:
    lines = code.splitlines()
    new_lines = []
    for line in lines:
        match = re.match(r'^\s*(ank|shabda|dashansh)\s+(\w+)\s*=\s*(.+)$', line)
        if match:
            variable = match.group(2)
            value = match.group(3)
            new_lines.append(f"{variable} = {value}")
        else:
            new_lines.append(line)
    return "\n".join(new_lines)

# Comment handling
def handle_comments(code: str) -> str:
    code = re.sub(r"#>(.*)", r"# \1", code)
    code = re.sub(r"#>\s*(.*?)\s*<#", r'"""\1"""', code, flags=re.DOTALL)
    return code

# Replace Marathi keywords
def replace_keywords(code: str) -> str:
    for marathi, python in marathi_to_python.items():
        code = re.sub(rf"\b{marathi}\b", python, code)
    return code

# Convert to Python
def convert_to_python(code: str) -> str:
    code = handle_comments(code)
    code = handle_declarations(code)
    code = replace_keywords(code)
    return code

# Run sutra file
def run_sutra_file(file_path: str):
    file_path = os.path.abspath(file_path)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            marathi_code = f.read()
    except FileNotFoundError:
        print(f"❌ फाईल सापडली नाही: {file_path}")
        return

    python_code = convert_to_python(marathi_code)

    print("\n🎉 congratulations bhava 🎉\n")
   
    try:
        exec(python_code, {})
    except Exception as e:
        print("❌ त्रुटी आली आहे:", e)
