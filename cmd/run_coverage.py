# coding: utf-8
from subprocess import run, call

def main():
    cmd_str = 'coverage run --source=kwhelp -m unittest discover tests'
    res = run(cmd_str.split(' '))
    run(['coverage', 'report'])

if __name__ == '__main__':
    main()
