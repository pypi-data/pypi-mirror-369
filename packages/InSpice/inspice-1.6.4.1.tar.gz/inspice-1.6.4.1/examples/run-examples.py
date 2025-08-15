#! /usr/bin/env python3
# -*- Python -*-

####################################################################################################
#
# InSpice - A Spice Package for Python
# Copyright (C) 2014 Fabrice Salvaire
# Copyright (C) 2025 Innovoltive
# Modified by Innovoltive on April 18, 2025
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
####################################################################################################

####################################################################################################

from pathlib import Path
import argparse
import glob
import os
import subprocess
import sys

####################################################################################################

def run_example(file_name, no_gui=True):
    """Run a single example file with proper error handling."""
    print(f"Running {file_name}{' (GUI and plots suppressed)' if no_gui else ''}")
    
    env = os.environ.copy()
    if no_gui:
        env['MPLBACKEND'] = 'Agg'  # Non-interactive matplotlib backend
        env['InSpice_NO_DISPLAY'] = '1'  # Custom env var that can be checked in examples
    env['PYTHONUNBUFFERED'] = '1'  # Ensure output is displayed immediately
    
    try:
        result = subprocess.run(['python', file_name], env=env, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {file_name}: {e}")
        return False

# Parse command line arguments
parser = argparse.ArgumentParser(description='Run InSpice examples')
parser.add_argument('--no-gui', action='store_true', help='Run without GUI and plots')
args = parser.parse_args()

examples_path = Path(__file__).resolve().parent

successful_examples = []
failed_examples = []

for topic in os.listdir(examples_path):
    topic_path = examples_path.joinpath(topic)
    if not topic_path.is_dir() or topic.startswith('.'):
        continue
        
    python_files = glob.glob(str(topic_path.joinpath('*.py')))
    for file_name in python_files:
        
        # Run automatically if --no-gui is specified, otherwise prompt the user
        if args.no_gui:
            success = run_example(file_name, args.no_gui)
            if success:
                successful_examples.append(file_name)
            else:
                failed_examples.append(file_name)
                print("Example failed, but continuing with next example...")
        else:
            print(f'Would you like to run {file_name}? [y/N/q(uit)]')
            choice = sys.stdin.readline().strip().lower()
            
            if choice == 'q':
                print("Exiting the examples runner.")
                sys.exit(0)
            elif choice == 'y':
                success = run_example(file_name, args.no_gui)
                if success:
                    successful_examples.append(file_name)
                else:
                    failed_examples.append(file_name)
                    print("Example failed, but continuing with next example...")

# After all examples are run - always show the summary, regardless of mode
print("\n" + "="*80)
print(f"EXECUTION SUMMARY:")
print(f"Successfully executed: {len(successful_examples)} examples")

if failed_examples:
    print(f"\nFailed to execute: {len(failed_examples)} examples")
    print("Failed examples:")
    for example in failed_examples:
        print(f"  - {example}")
else:
    print("\nAll examples executed successfully!")
print("="*80)
