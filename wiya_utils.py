
# Helper function for decoding
def str_it(value):
    if isinstance(value, bytes):
        return value.decode('utf-8')
    else:
        return value