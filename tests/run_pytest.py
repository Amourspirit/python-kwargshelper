# coding: utf-8
from subprocess import run

def main():
    cmd_str = 'pytest --cov=src.main --cov=src.error --cov=src.event_args --cov=src.helper --cov=src.rules --cov-report=html'
    res = run(cmd_str.split(' '))
    print(res.stdout)

if __name__ == '__main__':
    main()
