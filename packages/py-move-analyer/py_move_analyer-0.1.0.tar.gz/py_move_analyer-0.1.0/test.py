from py_move_analyer import parse

file = """
module my_addr::main_model;

fun init() {}
"""
a = parse(file)
print(a)