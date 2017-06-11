# fluffy

Know that big 3 headed puppy from the Harry Potter books/movies?
That guy is now protecting your precious source code.

This is a small tool to create or run a package containing python code.
The code is AES encrypted and can only be executed if you know the password.

## usage:

Encrypt your sources:
```bash
python fluffy.py pack <entrypoint (python) file> <output package file>
```

Run the package:
```bash
python fluffy.py run <package file>
```

## info
This is in no way safe, it's mainly playing around with python. Please do not rely on it!
