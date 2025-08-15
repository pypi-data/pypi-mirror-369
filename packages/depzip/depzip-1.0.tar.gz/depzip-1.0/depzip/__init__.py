import os
import sys

import dllist
import importlib

from modulefinder import ModuleFinder

from zipfile import ZipFile, ZIP_DEFLATED


def bundle(modules=[], includes=[], excludes=[], output="bundle.zip"):
    directory = os.path.dirname(sys.executable)

    bundle = set()

    finder = ModuleFinder()

    finder.import_hook("encodings", None, ["*"])

    for m in modules:
        finder.import_hook(m)

    for name, module in finder.modules.items():
        f = getattr(module, "__file__", None)
        if f is not None:
            bundle.add(os.path.relpath(f, directory))

    for m in modules:
        importlib.import_module(m)

    for dll in dllist.dllist():
        if any(x.casefold() in dll.casefold() for x in ("VCRUNTIME", "MSVCP")):
            continue
        if os.path.commonpath([dll, directory]) == directory:
            bundle.add(os.path.relpath(dll, directory))

    for element in includes:
        if os.path.isdir(element):
            for root, dirs, files in os.walk(element):
                dirs[:] = [d for d in dirs if d != "__pycache__"]
                for f in files:
                    bundle.add(os.path.join(root, f))
        elif os.path.isfile(element):
            bundle.add(element)

    bundle -= set(excludes)

    with ZipFile(output, mode="w", compression=ZIP_DEFLATED) as zf:
        for element in sorted(bundle):
            if os.path.isfile(element):
                zf.write(element)
