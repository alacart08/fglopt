from src.fglopt.utils.config_loader import ConfigLoader

def launch_console():
    print("Welcome to the FGL Optimizer console.")
    print("Type 'help' for commands.")

    config = None
    while True:
        cmd = input("> ").strip()
        
        if cmd == "exit":
            break
        
        # Load the configuration files
        elif cmd.startswith("load"):
            parts = cmd.split(maxsplit=1)
            if len(parts) != 2:
                print('Usage: load <config_file>')
                continue

            fname = parts[1]
            try:
                config = ConfigLoader(fname)
                print(f'Config loaded from {fname}.')
                print(f'Loaded keys:')
                for k, v in config.to_dict().items():
                    print(f'    {k}: {v}')
            except Exception as e:
                print(f'Error loaded config file: {e}')
                config = None

        elif cmd == "plot mesh":
            
            if config is None:
                print("Load config first.")
            else:
                from fglopt.mesh.domain_mesh import DomainMesh

                nx = config.get("mesh_resolution")
                ny = config.get("mesh_height", nx)
                lx = config.get("length_x", 1.0)
                ly = config.get("length_y", 1.0)

                mesh = DomainMesh(nx=nx, ny=ny, lx=lx, ly=ly)
                mesh.plot()


        # Run the optimization loop
        elif cmd == "run topo-opt":
            if not config:
                print("Load config first.")
            else:
                run_toplogy_optimization(config)
        
        # Show the help information
        elif cmd == "help":
            print("Commands:")
            print("  load <file>       Load a YAML config file")
            print("  run topo-opt      Run topology optimization (stub)")
            print("  plot mesh         Plot the mesh")
            print("  export <file>     Export lattice to STL (stub)")
            print("  exit              Quit")
            
        
        elif cmd == "help":
            print("Commands: load <file>, run topo-opt, export, exit")
        
        else:
            print("Unknown command.")


def run_toplogy_optimization(config: ConfigLoader):
    print("Starting topology optimization")

    vf = config.get('volume_fraction')
    res = config.get('mesh_resolution')
    E = config.get_nested('material','E')
    nu = config.get_nested('material','nu')

    print(f"  Volume fraction: {vf}")
    print(f"  Mesh resolution: {res}")
    print(f"  Young's modulus: {E:.2}")
    print(f"  Poisson's ratio: {nu}")
    print("...Optimization not implemented yet (stub)")