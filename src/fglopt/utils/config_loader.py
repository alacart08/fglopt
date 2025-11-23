import yaml

class ConfigLoader:
    """
    Load and provide access to configuration values from a YAML file.
    """

    def __init__(self, path:str):
        """
        Args:
            path: Path to a YAML config file.
        """
        self.path = path
        self.data = self._load()
        self.validate()

    
    def _load(self) -> dict:
        """Read and parse the YAML file."""
        try:
            with open(self.path, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            raise FileNotFoundError(f'Config file not found at {self.path}')
        except yaml.YAMLError as e:
            raise ValueError(f'Error parsing the YAML config file at {self.path}: {e}')
    

    def validate(self) -> None:
        """
        Basic sanity checks on required keys.
        Extend this over time as the app grows.
        """

        required_top = ["input_stl", "mesh_resolution", "volume_fraction", "material"]
        missing = [k for k in required_top if k not in self.data]
        if missing:
            raise ValueError(f'Missing required configuration data: {missing}')
        
        mat = self.data.get('material', {})
        for k in ['E', 'nu']:
            if k not in mat:
                raise ValueError(f'Missing material properties: {k}')
            
        
    def get(self, key:str, default=None):
        """Get a top-level config value."""
        return self.data.get(key, default)
    

    def get_nested(self, *keys, default=None):
        """
        Safely get nested config values, e.g. ("material", "E").
        """
        val = self.data
        for k in keys:
            if not isinstance(val, dict) or k not in val:
                return default
            val = val[k]
        return val
    

    def to_dict(self) -> dict:
        """Return the raw config dictionary."""
        return self.data
    
