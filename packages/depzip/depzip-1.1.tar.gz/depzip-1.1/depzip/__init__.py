import os
import sys
from dllist import dllist
from importlib import import_module
from importlib.metadata import distribution, packages_distributions
from modulefinder import ModuleFinder
from zipfile import ZipFile, ZIP_DEFLATED


def contains(string, substrings):
    return any(s.casefold() in string.casefold() for s in substrings)


def bundle(modules=[], includes=[], excludes=[], output="bundle.zip"):
    directory = os.path.dirname(sys.executable)

    # Use ModuleFinder to track module dependencies

    finder = ModuleFinder()

    finder.import_hook("encodings", None, ["*"])

    for m in modules:
        finder.import_hook(m)

    # Collect files to bundle

    bundle = {v.__file__ for v in finder.modules.values() if v.__file__}

    # Find and collect license files for bundled modules

    packages = {k.split(".", 1)[0] for k in finder.modules.keys()}
    mapping = packages_distributions()
    licenses = {"Python": {os.path.join(directory, "LICENSE.txt")}}

    for p in packages:
        for d in mapping.get(p, []):
            licenses.setdefault(d, set()).update(
                os.path.join(r, f)
                for r, _, files in os.walk(distribution(d)._path)
                for f in files
                if contains(f, ("license", "copying"))
            )

    # Import modules to load any DLLs

    for m in modules:
        import_module(m)

    # Add DLLs to the bundle

    for dll in dllist():
        if contains(os.path.basename(dll), ("vcruntime", "msvcp")):
            continue
        if os.path.commonpath([dll, directory]) == directory:
            bundle.add(dll)

    # Include additional files and directories

    for path in includes:
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if d != "__pycache__"]
                bundle.update(os.path.join(root, f) for f in files)
        elif os.path.isfile(path):
            bundle.add(path)

    # Exclude specified files

    bundle = {f for f in bundle if not contains(f, excludes)}

    # Create the output zip file

    with ZipFile(output, mode="w", compression=ZIP_DEFLATED) as zf:
        for name, files in licenses.items():
            for f in sorted(files):
                zf.write(f, os.path.join("Licenses", name, os.path.basename(f)))
        for f in sorted(bundle):
            if os.path.isfile(f):
                zf.write(f, os.path.relpath(f, directory))
