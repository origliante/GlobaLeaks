import hashlib
import time


m = hashlib.sha1()

f = file('100M.out')

chunk = f.read(1024)

while chunk:
    m.update(chunk)
    chunk = f.read(1024)

print 'sleep'
time.sleep(10)
print 'chunk ', m.hexdigest()


m = hashlib.sha1()
data = file('100M.out').read()
m.update(data)

print 'sleep'
time.sleep(10)

print 'whole ', m.hexdigest()

