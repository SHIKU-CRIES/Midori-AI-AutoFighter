import os
import importlib

class PassiveType:

    def __init__(self, name: str):
        self.name = name
        self.load_passive_implementation()

    def load_passive_implementation(self):
        """Loads the passive implementation from a Python file."""
        module_name = self.name.lower()  # Convert name to lowercase for file name
        file_path = os.path.join("passives_folder", f"{module_name}.py")  # Assuming passive files are in 'passives' directory

        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None:
                raise FileNotFoundError(f"Could not find module spec for {module_name} at {file_path}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find the class that implements the passive.  Assume the class name is the same as the passive name
            # but allow for possibility of a class naming convention
            try:
                passive_class = getattr(module, self.name)
            except AttributeError:
                try:
                    passive_class = getattr(module, f"{self.name}Passive")
                except AttributeError:
                    passive_class = getattr(module, f"{self.name.replace(' ', '')}Passive") #Try removing spaces
                except AttributeError:
                    print(f"Warning: No class named '{self.name}', '{self.name}Passive' or {self.name.replace(' ', '')}Passive' found in {file_path}.  Using base PassiveType methods.")
                    return  # Fallback to default methods
            # Create an instance of the passive class
            self.passive_instance = passive_class()
            
            # Optionally, copy methods from the loaded class to the current instance
            # This avoids the need to use self.passive_instance.method_name() everywhere.
            # Only copy methods that exist in the loaded class.
            for attr_name in dir(self.passive_instance):
                if callable(getattr(self.passive_instance, attr_name)) and not attr_name.startswith("__"):  #Check to make sure there are real methods
                    setattr(self, attr_name, getattr(self.passive_instance, attr_name))
            

        except FileNotFoundError:
            print(f"Warning: Passive implementation file '{file_path}' not found.  Using base PassiveType methods.")
        except Exception as e:
            print(f"Error loading passive implementation from '{file_path}': {e}.  Using base PassiveType methods.")

    def activate(self, gamestate) -> None:
        """Applies the passive effect."""
        return gamestate

    def do_pre_turn(self):
        pass

    def heal_damage(self, input_healing: float):
        pass

    def take_damage(self, input_damage: float):
        pass

    def deal_damage(self, input_damage_mod: float):
        pass

    def damage_mitigation(self, damage_pre: float):
        pass

    def regain_hp(self):
        pass

    def damage_over_time(self):
        pass

    def heal_over_time(self):
        pass

    def crit_damage_mod(self, damage_pre: float):
        pass

