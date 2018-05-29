import psutil, os

r=list(range(10000000))

process = psutil.Process(os.getpid())
mem = process.memory_info().rss / 1000
print("Used this much memory: " + str(mem) + ' kb')