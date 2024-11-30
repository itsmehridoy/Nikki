async def all_plugins():

    from glob import glob
    from os.path import basename, dirname, isfile

    mod_paths = glob(dirname(__file__) + "/*.py")
    all_plugs = [
        basename(f)[:-3]
        for f in mod_paths
        if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")
    ]
    return sorted(all_plugs)
