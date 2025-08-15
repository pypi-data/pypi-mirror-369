#!/usr/bin/env python3
# NH Language - simple interpreter
# Run: nhlang <file.nh>
import sys, re, ast

# ===== Runtime env =====
vars_env = {}

class BreakSignal(Exception):
    pass

# ===== Utils =====
def is_number(s):
    try:
        float(s)
        return True
    except:
        return False

def to_python_value(tok):
    t = tok.strip()
    if t in vars_env:
        return vars_env[t]
    if t.lower() == "true":
        return True
    if t.lower() == "false":
        return False
    if t.startswith('"') and t.endswith('"'):
        return t[1:-1]
    if is_number(t):
        # int nếu không có dấu chấm
        return int(float(t)) if "." not in t else float(t)
    # default: coi như string literal (theo ví dụ ông đưa: gt, hi, idk)
    return t

# array literal: [a, b, 1, 2]
def parse_array_literal(txt):
    inner = txt.strip()
    if inner.startswith('[') and inner.endswith(']'):
        inner = inner[1:-1].strip()
    if inner == "":
        return []
    parts = [p.strip() for p in inner.split(',')]
    return [to_python_value(p) for p in parts]

# ===== Expression evaluator (safe) =====
# Hỗ trợ: tên biến, số, chuỗi "abc", + - * /, (), truy cập arr[index]
# và toán tử so sánh cho IF: ==, !=, >=, <=, >, <
ALLOWED_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div)
ALLOWED_CMPOPS = (ast.Eq, ast.NotEq, ast.Gt, ast.Lt, ast.GtE, ast.LtE)

def eval_expr(expr):
    node = ast.parse(expr, mode='eval').body
    return _eval_node(node)

def _eval_node(node):
    if isinstance(node, ast.BinOp) and isinstance(node.op, ALLOWED_BINOPS):
        return _eval_node(node.left) + _eval_node(node.right) if isinstance(node.op, ast.Add) else \
               _eval_node(node.left) - _eval_node(node.right) if isinstance(node.op, ast.Sub) else \
               _eval_node(node.left) * _eval_node(node.right) if isinstance(node.op, ast.Mult) else \
               _eval_node(node.left) / _eval_node(node.right)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        v = _eval_node(node.operand)
        return +v if isinstance(node.op, ast.UAdd) else -v
    if isinstance(node, ast.Constant):
        # strings or numbers
        return node.value
    if isinstance(node, ast.Name):
        return to_python_value(node.id)
    if isinstance(node, ast.Call):
        # Không cho phép call
        raise ValueError("Function calls not allowed")
    if isinstance(node, ast.Subscript):
        # arr[index]
        arr = _eval_node(node.value)
        slc = node.slice
        # ast.Index for <=3.8, ast.Constant/ast.Slice for >=3.9
        if isinstance(slc, ast.Slice):
            start = _eval_node(slc.lower) if slc.lower else None
            stop = _eval_node(slc.upper) if slc.upper else None
            step = _eval_node(slc.step) if slc.step else None
            return arr[slice(start, stop, step)]
        else:
            # 3.9+: slice is ast.Constant or full expression
            idx = _eval_node(slc) if not isinstance(slc, ast.Index) else _eval_node(slc.value)
            return arr[idx]
    if isinstance(node, ast.Compare):
        left = _eval_node(node.left)
        ok = True
        cur = left
        for op, comparator in zip(node.ops, node.comparators):
            right = _eval_node(comparator)
            if isinstance(op, ALLOWED_CMPOPS):
                if isinstance(op, ast.Eq): ok = cur == right
                elif isinstance(op, ast.NotEq): ok = cur != right
                elif isinstance(op, ast.Gt): ok = cur > right
                elif isinstance(op, ast.Lt): ok = cur < right
                elif isinstance(op, ast.GtE): ok = cur >= right
                elif isinstance(op, ast.LtE): ok = cur <= right
                else: ok = False
            else:
                ok = False
            if not ok: break
            cur = right
        return ok
    raise ValueError("Unsupported expression")

# Chuyển biểu thức NH (chuỗi + biến) thành Python expr:
# - Chuỗi phải là "abc"
# - Tên biến giữ nguyên (tra trong env)
# - Toán tử + - * / bình thường
# - Truy cập mảng: var[0]
def normalize_expr(s):
    # Cho phép cộng chuỗi + số -> ép str? Trong NH ta để Python xử lý: nếu bất hợp lệ, người dùng phải ép chuỗi bằng "a" + b
    return s.strip()

# ===== Parser helpers =====
def strip_comment(line):
    # cắt // comment (không xử lý trong chuỗi)
    i = line.find('//')
    if i >= 0:
        return line[:i]
    return line

def read_block(lines, i):
    # đọc các dòng cho tới '}' (không ăn dòng '}')
    block = []
    i_cur = i
    while i_cur < len(lines):
        line = lines[i_cur].strip()
        if line.startswith('}'):
            break
        block.append(lines[i_cur])
        i_cur += 1
    return block, i_cur

# ===== Statement executors =====
def exec_print(line):
    # print( <expr> );
    m = re.match(r'print\s*\((.*)\)\s*;?\s*$', line.strip())
    if not m:
        raise ValueError("Syntax error in print")
    expr = m.group(1).strip()
    # ghép các phần với + (chuỗi/biến)
    val = eval_expr(normalize_expr(expr))
    print(val)

def exec_var_decl(line):
    # <type>.<name> = <value> ;
    m = re.match(r'(int|float|str|bool|array)\s*\.\s*([A-Za-z_]\w*)\s*=\s*(.*);\s*$', line.strip())
    if not m:
        return False
    dtype, name, value_src = m.groups()
    value_src = value_src.strip()
    if dtype == 'array':
        val = parse_array_literal(value_src)
    else:
        if dtype == 'str' and value_src.startswith('[') and value_src.endswith(']'):
            # lỡ viết nhầm [] cho str -> coi như literal
            val = str(value_src)
        else:
            # Cho phép gán bằng biểu thức
            if dtype == 'str':
                # nếu không bọc quote, convert sang str theo rule to_python_value
                if value_src.startswith('"') and value_src.endswith('"'):
                    val = value_src[1:-1]
                else:
                    val = str(to_python_value(value_src))
            else:
                v = eval_expr(normalize_expr(value_src))
                if dtype == 'int':
                    if isinstance(v, bool): v = int(v)
                    val = int(v)
                elif dtype == 'float':
                    val = float(v)
                elif dtype == 'bool':
                    if isinstance(v, (int, float, str)):
                        val = bool(v)
                    else:
                        val = bool(v)
                else:
                    val = v
    vars_env[name] = val
    return True

def exec_assignment(line):
    # name = expr;
    m = re.match(r'([A-Za-z_]\w*)\s*=\s*(.*);\s*$', line.strip())
    if not m:
        return False
    name, value_src = m.groups()
    val = eval_expr(normalize_expr(value_src))
    vars_env[name] = val
    return True

def exec_input(lines, i):
    # input.name("prompt") { ... }
    head = lines[i].strip()
    m = re.match(r'input\s*\.\s*([A-Za-z_]\w*)\s*\(\s*"(.*)"\s*\)\s*\{\s*$', head)
    if not m:
        return None
    name, prompt = m.groups()
    user_in = input(prompt)
    vars_env[name] = user_in
    block, j = read_block(lines, i+1)
    try:
        exec_lines(block)
    except BreakSignal:
        pass
    return j  # index of '}' line

def exec_loop(lines, i):
    # loop.var(count, value) { ... }
    head = lines[i].strip()
    m = re.match(r'loop\s*\.\s*([A-Za-z_]\w*)\s*\(\s*(.+)\s*,\s*(.+)\s*\)\s*\{\s*$', head)
    if not m:
        return None
    name, count_src, value_src = m.groups()
    count = int(eval_expr(normalize_expr(count_src)))
    # value có thể là chuỗi/biến/số
    val = None
    if value_src.strip().startswith('[') and value_src.strip().endswith(']'):
        val = parse_array_literal(value_src)
    else:
        # Cho phép expr (ví dụ: "hi " + num)
        try:
            val = eval_expr(normalize_expr(value_src))
        except Exception:
            val = to_python_value(value_src)
    block, j = read_block(lines, i+1)
    for _ in range(count):
        vars_env[name] = val
        try:
            exec_lines(block)
        except BreakSignal:
            break
    return j  # index of '}' line

def exec_if_chain(lines, i):
    # if.var <op> <expr> { ... }
    # elseif.var <op> <expr> { ... }
    # else { ... }
    head = lines[i].strip()
    m = re.match(r'if\s*\.\s*([A-Za-z_]\w*)\s*(==|>=|<=|>|<)\s*(.+)\s*\{\s*$', head)
    if not m:
        return None
    varname, op, rhs = m.groups()
    cond_expr = f"{varname} {op} ({rhs})"
    first_block, j = read_block(lines, i+1)
    chosen_executed = False
    if bool(eval_expr(normalize_expr(cond_expr))):
        try:
            exec_lines(first_block)
        except BreakSignal:
            pass
        chosen_executed = True

    k = j + 1
    while k < len(lines):
        line = lines[k].strip()
        # elseif
        m2 = re.match(r'elseif\s*\.\s*([A-Za-z_]\w*)\s*(==|>=|<=|>|<)\s*(.+)\s*\{\s*$', line)
        if m2:
            name2, op2, rhs2 = m2.groups()
            block2, j2 = read_block(lines, k+1)
            if not chosen_executed and bool(eval_expr(normalize_expr(f"{name2} {op2} ({rhs2})"))):
                try:
                    exec_lines(block2)
                except BreakSignal:
                    pass
                chosen_executed = True
            k = j2 + 1
            continue
        # else
        m3 = re.match(r'else\s*\{\s*$', line)
        if m3:
            block3, j3 = read_block(lines, k+1)
            if not chosen_executed:
                try:
                    exec_lines(block3)
                except BreakSignal:
                    pass
            k = j3 + 1
            break
        # không còn elseif/else
        break
    return k - 1  # trả về index của dòng cuối cùng đã xử lý (thường là } của if/elseif/else cuối)

def exec_break(line):
    if re.match(r'break\s*;\s*$', line.strip()):
        raise BreakSignal()

# ===== Main executor =====
def exec_lines(lines):
    i = 0
    while i < len(lines):
        raw = strip_comment(lines[i].rstrip('\n'))
        line = raw.strip()
        if line == "":
            i += 1
            continue
        # single-line block end
        if line == "}":
            return

        # break
        if exec_break(line) is not None:
            # exec_break raises exception; this is never reached
            pass

        # print
        if line.startswith("print("):
            exec_print(line)
            i += 1
            continue

        # input
        j = exec_input(lines, i)
        if j is not None:
            i = j + 1
            continue

        # loop
        j = exec_loop(lines, i)
        if j is not None:
            i = j + 1
            continue

        # if / elseif / else chain
        j = exec_if_chain(lines, i)
        if j is not None:
            i = j + 1
            continue

        # var decl
        if exec_var_decl(line):
            i += 1
            continue

        # assignment
        if exec_assignment(line):
            i += 1
            continue

        raise ValueError(f"Syntax error: {line}")
    return

def run_file(path):
    with open(path, "r", encoding="utf-8") as f:
        # giữ nguyên dòng để block reader hoạt động
        lines = f.readlines()
    exec_lines(lines)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: nhlang <file.nh>")
        sys.exit(1)
    run_file(sys.argv[1])

def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: nhlang <file.nh>")
        sys.exit(1)
    run_file(sys.argv[1])
