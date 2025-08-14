import argparse
import os,sys,re
import hipo

def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='subcommands', dest='subcommand')
    help_parser = subparsers.add_parser('help', help='show help')
    info_parser = subparsers.add_parser('info', help='show info of the package')
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    examples_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'examples'))
    mpi_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'bin/mpiexec.hydra'))
    if args.subcommand == 'help':
        print(f'''
  use 
    cp -r {examples_path} .
  to copy out a example, and use 
    python solver.py thermal1.mtx thermal1_b.mtx solver.json
  to run the example, use
    {mpi_path} -n 2 python solver.py thermal1.mtx thermal1_b.mtx solver.json
  to run the example with 2 processes.
    ''')


    if args.subcommand == 'info':
        print("Devices:")
        for it in hipo.getAllDevices():
          print(f"    {it}")
        for it, lst in hipo.getAllInstances().items():
          print(f"{it}")
          for inst in lst:
            print(f"    {inst}")
main()

