#!/usr/bin/python3

import io

output = io.StringIO()
output.write('First line.\n')
print('Second line.', file=output)

# Retrieve file contents -- this will be
# 'First line.\nSecond line.\n'
contents = output.getvalue()

f = open('workfile', 'w')
f.write(contents)
f.close()

print(contents)

# Close object and discard memory buffer --
# .getvalue() will now raise an exception.
output.close()
