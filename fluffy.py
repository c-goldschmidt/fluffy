import json
import os
import argparse
from getpass import getpass

from lib.aes import AESCipher
from lib.file_tree import FileTree
from lib.statics import Statics


def merge_files(entry_file):
    entry_file = os.path.abspath(entry_file)

    tree = FileTree(entry_file, os.path.dirname(entry_file))
    needed = [imp for imp, val in Statics.RESOLVED_IMPORTS.items() if val is None]

    lib_imports = ''
    for imp in needed:
        lib_imports += imp + '\n'

    tree_dict = tree.get_dict()
    tree_dict['__main__'] = lib_imports + tree_dict['__main__']
    return json.dumps(tree_dict)


def pack(args):
    content = AESCipher(args.passwd).encrypt(merge_files(args.file))
    with(open(args.out, 'wb')) as f:
        f.write(content)

    print('packing done.')


def run(args):
    with(open(args.file, 'rb')) as f:
        content = f.read()

    content = AESCipher(args.passwd).decrypt(content)
    content = json.loads(content)

    def resolve(dst, module, *args):
        if module not in scopes:
            scopes[module] = {
                '__file__':  __file__,
                '__fluffy__': resolve,
                '__name__': module,
            }

        exec(content[module], scopes[module])
        for arg in args:
            scopes[dst][arg] = scopes[module][arg]

    scopes = {
        '__main__': {
            '__file__': __file__,
            '__fluffy__': resolve,
            '__name__': '__main__',
        }
    }

    exec(content['__main__'], scopes['__main__'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    sp = parser.add_subparsers()

    sp_run = sp.add_parser('run')
    sp_pack = sp.add_parser('pack')

    sp_run.set_defaults(func=run)
    sp_pack.set_defaults(func=pack)

    sp_run.add_argument(
        'file',
        type=str,
    )
    sp_pack.add_argument(
        'file',
        type=str,
    )
    sp_pack.add_argument(
        'out',
        type=str,
    )

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.passwd = getpass('Password: ')
        args.func(args)
    else:
        parser.print_help()


