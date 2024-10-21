import os
import colorama
import cProfile

from gamestates import main

try:
    os.remove("auto.pick")
except Exception as e:
    pass


if __name__ == "__main__":
    main(1)
    #cProfile.run('main(1)', filename='profiling_results.prof')
