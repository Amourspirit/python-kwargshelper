# coding: utf-8
from subprocess import run
TEST_MODULES = ['kwhelp', 'kwhelp.rules', 'kwhelp.helper']
# kwhelp.method
def get_modules():
    global TEST_MODULES
    result = ''
    if len(TEST_MODULES) > 0:
        result = ' --cov=' + ' --cov='.join(TEST_MODULES)
    return result
def main():
    cov_mod = get_modules()
    # see: https://stackoverflow.com/questions/41748464/pytest-cannot-import-module-while-python-can
    cmd_str = f"python -m pytest{cov_mod} --cov-report=html"
    res = run(cmd_str.split(' '))
    print(res.stdout)
    print(cmd_str)

if __name__ == '__main__':
    main()
