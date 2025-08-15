#!/usr/bin/env python3
"""
Wrapper for the original Exe.py functionality.
This makes the Exe.py logic available as an importable module.
"""

import sys
import os

# Add the src directory to the Python path - handle different execution contexts
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))  # Go up from src/jahn_teller_dynamics to project root
src_dir = os.path.join(project_root, 'src')

if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

try:
    import jahn_teller_dynamics.io.JT_config_file_parsing as  JT_cfg    
    import jahn_teller_dynamics.io.user_workflow as uw
except ImportError:
    # Fallback for test environments
    sys.path.insert(0, os.path.join(current_dir, '..', '..'))
    import jahn_teller_dynamics.io.JT_config_file_parsing as  JT_cfg    
    import jahn_teller_dynamics.io.user_workflow as uw


def main():
    """Main function that replicates the original Exe.py behavior."""
    arguments = sys.argv[1:]
    
    if not arguments:
        print("Error: No configuration file specified.")
        print("Usage: Exe <config_file>")
        sys.exit(1)
    
    config_file_name = arguments[0]
    
    
    JT_config_parser = JT_cfg.Jahn_Teller_config_parser(config_file_name)
    print('Run an Exe calculation')
    if JT_config_parser.is_ZPL_calculation():
        uw.ZPL_procedure(JT_config_parser)
    elif JT_config_parser.is_single_case():
        section_to_look_for = JT_cfg.single_case_section
        uw.spin_orbit_JT_procedure_general(JT_config_parser, section_to_look_for, complex_trf=True)
    else:
        print("Error: Could not determine calculation type from config file.")
        sys.exit(1)
            

    


if __name__ == "__main__":
    main() 