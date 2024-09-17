txt = 'xxx.xxx.com/prod/none/T/r.zip'.split('/')
host = txt[:1]
filename = txt[-1:]
path = '/' + '/'.join(txt[1:-1]) + '/'
print(host)
print(filename)
print(path)
