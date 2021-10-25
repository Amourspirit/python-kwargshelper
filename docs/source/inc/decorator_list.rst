.. exec::

    import glob
    import os
    r_path = os.path.join(os.path.abspath('.'), "source/kwhelp/decorator")
    rules_pattern = r_path + os.sep + "*.rst"
    dec_list = [n for n in glob.glob(rules_pattern) if not n.endswith('index.rst')]
    dec_list.sort()
    print("\n")
    for dec in dec_list:
        name = os.path.basename(str(dec)[:-4])
        print("* :doc:`{0} </source/kwhelp/decorator/{0}>`".format(name))
        print("\n")