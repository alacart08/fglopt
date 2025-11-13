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
        elif cmd == "run topo-opt":
            if not config:
                print("Load config first.")
            else:
                print("Running topology optimization... (stub)")
        elif cmd == "export":
            print("Exporting lattice... (stub)")
        elif cmd == "help":
            print("Commands: load <file>, run topo-opt, export, exit")
        else:
            print("Unknown command.")