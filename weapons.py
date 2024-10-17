import random

class WeaponType:
    def __init__(self, name, damage, accuracy, critical_chance, game_str):
        self.name = name
        self.damage = damage
        self.accuracy = accuracy
        self.critical_chance = critical_chance
        self.game_obj = game_str
        self.position = (0, 0)
    
def get_weapon(name):
    """Returns a WeaponType object with the given name."""

    random_vector = [random.randint(0, 100) for i in range(10)]
    random_string = ''.join(random.choice("abcdefghijklmnopqrstuvwxyz") for i in range(10))

    # Python terms
    game_bit = WeaponType("game_bit", 10, 0.8, 0.05, f"{random.getrandbits(1)}")
    game_byte = WeaponType("game_byte", 20, 0.7, 0.1, f"{random.choice([True, False])}")
    game_str = WeaponType("game_str", 30, 0.6, 0.15, f"{random.choice("Hello World")}")
    game_integer = WeaponType("game_integer", 40, 0.5, 0.2, f"{random.randint(0, 9)}")

    # C terms
    game_char = WeaponType("game_char", 10, 0.8, 0.05, f"{random.choice('abcdefghijklmnopqrstuvwxyz')}")
    game_short = WeaponType("game_short", 20, 0.7, 0.1, f"{random.randint(-32768, 32767)}")
    game_int = WeaponType("game_int", 30, 0.6, 0.15, f"{random.randint(0, 9)}")
    game_long = WeaponType("game_long", 40, 0.5, 0.2, f"{random.getrandbits(64)}")

    # C++ terms
    game_bool = WeaponType("game_bool", 10, 0.8, 0.05, f"{random.choice([True, False])}")
    game_wchar_t = WeaponType("game_wchar_t", 20, 0.7, 0.1, f"{random.choice('abcdefghijklmnopqrstuvwxyz')}")
    game_string = WeaponType("game_string", 30, 0.6, 0.15, f"{random_string}")
    game_vector = WeaponType("game_vector", 40, 0.5, 0.2, f"{random_vector}")

    # C# terms
    game_object = WeaponType("game_object", 10, 0.8, 0.05, "object")
    game_class = WeaponType("game_class", 20, 0.7, 0.1, "class")
    game_struct = WeaponType("game_struct", 30, 0.6, 0.15, "struct")
    game_enum = WeaponType("game_enum", 40, 0.5, 0.2, "enum")

    # Java terms
    game_void = WeaponType("game_void", 10, 0.8, 0.05, "void")
    game_main = WeaponType("game_main", 20, 0.7, 0.1, "main")
    game_system = WeaponType("game_system", 30, 0.6, 0.15, "system")
    game_out = WeaponType("game_out", 40, 0.5, 0.2, "out")

    # Ruby terms
    game_nil = WeaponType("game_nil", 10, 0.8, 0.05, "nil")
    game_true = WeaponType("game_true", 20, 0.7, 0.1, "true")
    game_false = WeaponType("game_false", 30, 0.6, 0.15, "false")
    game_array = WeaponType("game_array", 40, 0.5, 0.2, "array")

    # Go terms
    game_interface = WeaponType("game_interface", 10, 0.8, 0.05, "interface")
    game_map = WeaponType("game_map", 20, 0.7, 0.1, "map")
    game_channel = WeaponType("game_channel", 30, 0.6, 0.15, "channel")
    game_goroutine = WeaponType("game_goroutine", 40, 0.5, 0.2, "goroutine")

    # Rust terms
    game_trait = WeaponType("game_trait", 10, 0.8, 0.05, "pub trait Animal")
    game_impl = WeaponType("game_impl", 20, 0.7, 0.1, "impl Animal")
    game_enum = WeaponType("game_enum", 30, 0.6, 0.15, "#[derive(Debug)]")
    game_struct = WeaponType("game_struct", 40, 0.5, 0.2, "#[derive(Debug)]")

    weapons = {
        "game_bit": game_bit,
        "game_byte": game_byte,
        "game_str": game_str,
        "game_integer": game_integer,
        "game_char": game_char,
        "game_short": game_short,
        "game_int": game_int,
        "game_long": game_long,
        "game_bool": game_bool,
        "game_wchar_t": game_wchar_t,
        "game_string": game_string,
        "game_vector": game_vector,
        "game_object": game_object,
        "game_class": game_class,
        "game_struct": game_struct,
        "game_enum": game_enum,
        "game_void": game_void,
        "game_main": game_main,
        "game_system": game_system,
        "game_out": game_out,
        "game_nil": game_nil,
        "game_true": game_true,
        "game_false": game_false,
        "game_array": game_array,
        "game_interface": game_interface,
        "game_map": game_map,
        "game_channel": game_channel,
        "game_goroutine": game_goroutine,
        "game_trait": game_trait,
        "game_impl": game_impl,
        "game_enum": game_enum,
        "game_struct": game_struct
    }

    if name not in weapons:
        raise ValueError("Invalid weapon name")

    return weapons[name]

def get_random_weapon():
    """Returns a random WeaponType object."""

    weapons = [
        "game_bit",
        "game_byte",
        "game_str",
        "game_integer",
        "game_char",
        "game_short",
        "game_int",
        "game_long",
        "game_bool",
        "game_wchar_t",
        "game_string",
        "game_vector",
        "game_object",
        "game_class",
        "game_struct",
        "game_enum",
        "game_void",
        "game_main",
        "game_system",
        "game_out",
        "game_nil",
        "game_true",
        "game_false",
        "game_array",
        "game_interface",
        "game_map",
        "game_channel",
        "game_goroutine",
        "game_trait",
        "game_impl"]
    
    random_index = random.randint(0, len(weapons) - 1)
    return weapons[random_index]

