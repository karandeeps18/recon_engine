import sys 
from recon_engine.config_loader import load_config
from recon_engine.reader import read_system_a, read_system_b


def main():
    """_summary_
    This is the main entry point for the reconciliation engine 
    This will orchestrate the loading, fetching, caching, reconciliation, and Output 
    """
    # Load config.json 
    config = load_config("config.json")
    # load system a and system b 
    # later need to add the file handling using glob 
    print(config)
    sys_a = read_system_a(config['system_a_file'])
    sys_b = read_system_b(config['system_b_file'])
    print(sys_a.head())
    print(sys_b.head())
    return sys_a, sys_b, config

if __name__ == "__main__":
    main()