def translate_ast_to_cpp(ast):
    code = "#include <iostream>\n#include <vector>\n#include <string>\nusing namespace std;\n\n"
    functions = ""
    main_code = "int main() {\n"
    indent = "    "
    declared_vars = set()

    def declare_var_if_needed(var, expr):
        dtype = "int"
        if expr['type'] == 'string':
            dtype = "string"
        elif expr['type'] == 'list':
            dtype = "vector<int>"
        if var not in declared_vars:
            declared_vars.add(var)
            return f"{dtype} {var}"
        return var

    def translate_statement_cpp(stmt, indent):
        code = ""
        if stmt['type'] == 'assign':
            expr_code = translate_expression_cpp(stmt['expr'])
            var_name = declare_var_if_needed(stmt['var'], stmt['expr'])
            code += f"{indent}{var_name} = {expr_code};\n"
        elif stmt['type'] == 'print':
            parts = ' << '.join([translate_expression_cpp(arg) for arg in stmt['args']])
            code += f"{indent}cout << {parts} << endl;\n"
        elif stmt['type'] == 'if':
            cond = translate_expression_cpp(stmt['condition'])
            code += f"{indent}if ({cond}) {{\n"
            for s in stmt['body']:
                code += translate_statement_cpp(s, indent + "    ")
            code += indent + "}"
            if stmt.get('else'):
                code += " else {\n"
                for s in stmt['else']:
                    code += translate_statement_cpp(s, indent + "    ")
                code += indent + "}"
            code += "\n"
        elif stmt['type'] == 'while':
            cond = translate_expression_cpp(stmt['condition'])
            code += f"{indent}while ({cond}) {{\n"
            for s in stmt['body']:
                code += translate_statement_cpp(s, indent + "    ")
            code += indent + "}\n"
        elif stmt['type'] == 'for':
            code += f"{indent}for (int {stmt['var']} = 0; {stmt['var']} < {stmt['range']}; {stmt['var']}++) {{\n"
            for s in stmt['body']:
                code += translate_statement_cpp(s, indent + "    ")
            code += indent + "}\n"
        elif stmt['type'] == 'foreach':
            code += f"{indent}for (auto {stmt['var']} : {stmt['list']}) {{\n"
            for s in stmt['body']:
                code += translate_statement_cpp(s, indent + "    ")
            code += indent + "}\n"
        elif stmt['type'] == 'expr' and stmt['expr']['type'] == 'call':
            args = ', '.join(translate_expression_cpp(arg) for arg in stmt['expr']['args'])
            code += f"{indent}{stmt['expr']['name']}({args});\n"
        return code

    def translate_expression_cpp(expr):
        if expr['type'] == 'string':
            return f'"{expr["value"]}"'
        elif expr['type'] == 'number':
            return expr['value']
        elif expr['type'] == 'var':
            return expr['value']
        elif expr['type'] == 'binop':
            left = translate_expression_cpp(expr['left'])
            right = translate_expression_cpp(expr['right'])
            op = expr['op']
            return f"({left} {op} {right})"
        elif expr['type'] == 'call':
            args = ', '.join(translate_expression_cpp(arg) for arg in expr['args'])
            return f"{expr['name']}({args})"
        elif expr['type'] == 'list':
            items = ', '.join(translate_expression_cpp(el) for el in expr['elements'])
            return f"std::vector<int>{{{items}}}"
        else:
            return ""

    def translate_function_cpp(func):
        params = ', '.join([f"int {p}" for p in func['params']])
        code = f"int {func['name']}({params}) {{\n"
        for stmt in func['body']:
            if stmt['type'] == 'assign' and stmt['var'] == 'return':
                code += f"    return {translate_expression_cpp(stmt['expr'])};\n"
            else:
                code += translate_statement_cpp(stmt, "    ")
        code += "}\n\n"
        return code

    for stmt in ast:
        if stmt['type'] == 'function':
            functions += translate_function_cpp(stmt)
        else:
            main_code += translate_statement_cpp(stmt, indent)

    main_code += indent + "return 0;\n}\n"
    return code + functions + main_code
