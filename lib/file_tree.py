import os
import re
import copy
import zlib

from lib.statics import Statics


class FileTree(object):
    RX_IMPORTS = r'(from (?P<from>.+?) )?import ?((?P<imports_single>[^()]+?)$|\((?P<imports_multi>.+?)\))'

    def __init__(self, filename, root):
        self.filename = filename
        self.dirname = os.path.dirname(self.filename)
        self.root = root

        self.content = None
        self.imports = []
        self.to_remove = []
        self.module = '__main__'

        self.read_file()
        self.read_imports()

    def read_file(self):
        with open(self.filename, 'r+') as f:
            self.content = f.read()

    def path_from_module(self, match):
        path_split = match.group('from').split('.')

        filename = path_split[-1] + '.py'
        path_split = path_split[:-1]

        if not path_split:
            return os.path.join(self.dirname, filename)
        elif path_split[0] == '':
            return os.path.join(self.dirname, *path_split[1:], filename)
        elif os.path.isdir(os.path.join(self.root, path_split[0])):
            return os.path.join(self.root, *path_split, filename)
        else:
            return os.path.join(self.dirname, *path_split, filename)

    def absolute_module_path(self, filename):
        rel_path = os.path.relpath(os.path.dirname(filename), self.root)
        f_name = os.path.basename(filename)
        rel_path += '/' + f_name.replace('.py', '')

        return re.sub(r'[/\\]', '.', rel_path)

    def resolve(self, match):
        if match.group('from'):
            filename = self.path_from_module(match)
            module = self.absolute_module_path(filename)

            init_file = filename.replace('.py', '/__init__.py')
            if os.path.isfile(init_file) and init_file not in Statics.RESOLVED_IMPORTS:
                node = FileTree(init_file, self.root)
                node.module = module
                self.imports.append(node)
                Statics.RESOLVED_IMPORTS[init_file] = node
                Statics.CODE_BY_MODULE[module].append(node)

            if os.path.isfile(filename):
                if filename not in Statics.RESOLVED_IMPORTS:
                    node = FileTree(filename, self.root)
                    node.module = module
                    self.imports.append(node)
                    Statics.RESOLVED_IMPORTS[filename] = node
                    Statics.CODE_BY_MODULE[module].append(node)

            elif os.path.isfile(filename.replace('.py', '/__init__.py')):
                pass
            else:
                print('import from outside project (lib): {}'.format(match.group(0)))
                Statics.RESOLVED_IMPORTS[match.group(0)] = None

        else:
            print('single import: {}'.format(match.group(0)))
            Statics.RESOLVED_IMPORTS[match.group(0)] = None

    def read_imports(self):
        matches = re.finditer(self.RX_IMPORTS, self.content, re.MULTILINE | re.DOTALL)

        if not matches:
            print('no imports found in {}'.format(self.filename))

        for match in matches:
            self.to_remove.append(match)
            self.resolve(match)

    def print_files(self):
        for imp in self.imports:
            imp.print_files()
        print(self.filename)

    def get_copy_list(self, match):
        single = match.group('imports_single')
        multi = match.group('imports_multi')

        imps = single if single else multi
        if not imps:
            return ''
        else:
            return '\',\''.join([m.group(0) for m in re.finditer(r'\w+', imps)])

    def clean_imports(self):
        content = copy.copy(self.content)

        if self.module == '__main__':
            new_import = '__fluffy__(\'{}\', \'{}\', \'{}\')\n'.format(
                self.module,
                '__fluffy_crc__',
                '__fluffy_crc'
            )
            content = new_import + '__fluffy_crc()\n' + content

        for rem in self.to_remove:
            module = None
            if rem.group('from'):
                filename = self.path_from_module(rem)
                module = self.absolute_module_path(filename)

            if module and module in Statics.CODE_BY_MODULE:
                new_import = '__fluffy__(\'{}\', \'{}\', \'{}\')\n'.format(
                    self.module,
                    module,
                    self.get_copy_list(rem),
                )
                content = content.replace(rem.group(0), new_import, 1)
            else:
                content = content.replace(rem.group(0), '', 1)

        return content

    def merge_it(self):
        content = ''

        for imp in self.imports:
            content += imp.merge_it()

        content += self.clean_imports() + '\n'
        return content

    @staticmethod
    def _get_crc(filename):
        prev = 0
        for eachLine in open(filename, 'rb'):
            prev = zlib.crc32(eachLine, prev)
        return '%X' % (prev & 0xFFFFFFFF)

    def get_dict(self):
        code_dict = {}

        if self.module == '__main__':
            with open('lib/fluffy_crc.py', 'r') as f:
                code_dict['__fluffy_crc__'] = f.read().format(
                    self._get_crc('fluffy.py'),
                    self._get_crc('lib/aes.py')
                )

        for imp in self.imports:
            code_dict.update(imp.get_dict())

        code_dict[self.module] = self.clean_imports()
        return code_dict
