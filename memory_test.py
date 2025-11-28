from memory_profiler import profile

@profile
def allocate():
    x = [i for i in range(100000)]
    return x

if __name__ == "__main__":
    allocate()
