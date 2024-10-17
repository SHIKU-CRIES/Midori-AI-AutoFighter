import os

from gamestates import main

try:
    os.remove("auto.pick")
except Exception as e:
    pass


if __name__ == "__main__":
    main(1)
