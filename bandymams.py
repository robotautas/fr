import os

result = list(os.walk('./static/known'))[0][2]

print(result)