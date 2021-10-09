.. exec::

    import glob
    import os
    r_path = os.path.join(os.path.abspath('.'), "source/kwhelp/rules")
    rules_pattern = r_path + os.sep + "Rule*.rst"
    rule_list = glob.glob(rules_pattern)
    rule_list.sort()
    i_trim = len(r_path) + 1
    print("\n")
    for rule in rule_list:
        name = str(rule)[i_trim:-4]
        print("* :py:class:`~.rules.{}`".format(name))
        print("\n")