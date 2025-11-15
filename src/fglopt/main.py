import yaml

def launch_console():
    print("Welcome to the FGL Optimizer console.")
    print("Type 'help' for commands.")

    config = None
    while True:
        cmd = input("> ").strip()
        
        if cmd == "exit":
            break
        
        elif cmd.startswith("load"):
            _, fname = cmd.split()
            with open(fname) as f:
                config = yaml.safe_load(f)
            print(f"Config loaded from {fname}.")
            print("Loaded keys:")
            for k, v in config.items():
                print(f"    {k}: {v}")
        
        elif cmd == "run topo-opt":
            if not config:
                print("Load config first.")
            else:
                run_toplogy_optimization(config)
        
        elif cmd == "export":
            print("Exporting lattice... (stub)")
        
        elif cmd == "help":
            print("Commands: load <file>, run topo-opt, export, exit")
        
        else:
            print("Unknown command.")


def run_toplogy_optimization(config):
    print("Starting topology optimization")
    vf = config['volume_fraction']
    res = config['mesh_resolution']
    E = float(config['material']['E'])
    nu = float(config['material']['nu'])

    print(f"  Volume fraction: {vf}")
    print(f"  Mesh resolution: {res}")
    print(f"  Young's modulus: {E:.2e}")
    print(f"  Poisson's ratio: {nu}")
    print("...Optimization not implemented yet (stub)")