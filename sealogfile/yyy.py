import ast

log_string = "([11], [], {'Cwrd1': 512, 'SymblOfst': 933, 'AccssTyp': 2, 'timeout': 20, 'ParmCtrl': 2})"

# Convert string back to Python variable using ast.literal_eval
converted_variable = ast.literal_eval(log_string)

# Access the dictionary
dictionary_part = converted_variable[2]
print(converted_variable[0][0])
print(converted_variable[1])
print(dictionary_part)