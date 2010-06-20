import sys

data = []
d = sys.stdin.read()
while d:
    data.append(d)
    d = sys.stdin.read()

s = "".join(data)
s = s.replace(sys.argv[1], sys.argv[2])
sys.stdout.write(s)
