# coding: utf-8
from subprocess import run

def main():
    cmd_str = 'pytest --cov=kwhelp --cov=kwhelp.rules --cov=kwhelp.helper --cov-report=html'
    res = run(cmd_str.split(' '))
    print(res.stdout)

if __name__ == '__main__':
    main()
