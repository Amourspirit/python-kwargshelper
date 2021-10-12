.. exec::

    import glob
    import os
    r_path = os.path.join(os.path.abspath('.'), "source/kwhelp/rules")
    rules_pattern = r_path + os.sep + "Rule*.rst"
    rule_list = glob.glob(rules_pattern)
    rule_list.sort()
    print("\n")
    for rule in rule_list:
        name = os.path.basename(str(rule)[:-4])
        # print("* :py:class:`~.rules.{}`".format(name))
        print("* :doc:`{0} </source/kwhelp/rules/{0}>`".format(name))
        print("\n")