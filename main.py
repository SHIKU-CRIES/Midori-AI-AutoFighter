import os
import getpass

from gamestates import main

try:
    os.remove("auto.pick")
except Exception as e:
    pass

if __name__ == "__main__":
    try:
        if getpass.getuser() == "lunamidori":
            import cProfile
            cProfile.run('main(1)', filename='profiling_results.prof')
        else:
            main(1)
    except Exception as error:
        print(f"A error: {str(error)}")