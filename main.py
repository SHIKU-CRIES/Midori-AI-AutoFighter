import os
import colorama
import cProfile

from gamestates import main

try:
    os.remove("auto.pick")
except Exception as e:
    pass


if __name__ == "__main__":
    try:
        main(1)
    except Exception as error:
        print(f"A error: {str(error)}")
        os.remove("Player.dat")
    #cProfile.run('main(1)', filename='profiling_results.prof')
