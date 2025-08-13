"""setversion.py: Quickly change the version of a project"""
import argparse
import os
import sys
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
import re
from textwrap import dedent
import configparser
from typing import Iterable, Optional, Tuple, List


VERSION='1.0.1' # setversion

# If you have a file larger than this, we'll still replace version strings in the first this number of bytes
MAX_FILE_SIZE = 12 * 1025 * 1024


class BinaryFile(Exception): pass
class SourceChanged(Exception): pass
class WriteFailed(Exception): pass


@dataclass
class ProjectLine:
    file: "ProjectFile"
    src: bytes
    line_num: int
    modified: bytes = None

    def __str__(self):
        return self.text

    def __repr__(self):
        return ' '.join([
            f"ProjectLine(file='{self.file.name}', line_num={self.line_num}, ",
            f"modified={self.is_modified}, src='{self.text}')",
        ])

    @property
    def is_modified(self) -> bool:
        return self.modified is not None
    
    @property
    def text(self) -> str:
        if self.modified:
            try:
                return self.modified.decode('utf-8')
            except:
                return repr(self.modified)
        else:
            try:
                return self.src.decode('utf-8')
            except:
                return repr(self.src)


@dataclass
class ProjectFile:
    """A file in the project"""
    project: "Project"
    name: str
    path: Path
    line_changes: list[ProjectLine] = None

    LINE_SEP = b'\n' # Will not drop \r

    @property
    def has_changes(self) -> bool:
        return self.line_changes is not None and self.line_changes

    def read_lines(self) -> List[ProjectLine]:
        with self.path.open('rb') as fh:
            src = fh.read(MAX_FILE_SIZE)
            lines = [ProjectLine(file=self, src=line, line_num=i+1) for i, line in enumerate(src.split(self.LINE_SEP))]

            # Check to see if we think this is a binary file
            if max([len(line.src) for line in lines]) > self.project.max_line_length:
                raise BinaryFile(f"File {self.path} has long lines")
            if any([b'\x00' in line.src for line in lines]):
                raise BinaryFile(f"File {self.path} has NULL bytes")

            return lines

    def iterate_lines(self) -> Iterable[Tuple[ProjectLine, ProjectLine, ProjectLine]]:
        # Iterate over lines
        lines = self.read_lines()
        for i in range(len(lines)):
            prior_line = lines[i - 1] if i > 0 else None
            line = lines[i]
            next_line = lines[i + 1] if i < len(lines) - 1 else None
            yield (prior_line, line, next_line)

    def scan_for_version_changes(self, old_version: str, new_version: str) -> Iterable[ProjectLine]:
        old_version = old_version.encode('ascii')
        new_version = new_version.encode('ascii')
        self.line_changes = []
        for prior, line, nextline in self.iterate_lines():
            if old_version in line.src:
                if self.project.line_marker in line.src:
                    line.modified = line.src.replace(old_version, new_version)
                if prior and self.project.next_line_marker in prior.src:
                    line.modified = line.src.replace(old_version, new_version)
                if nextline and self.project.prior_line_marker in nextline.src:
                    line.modified = line.src.replace(old_version, new_version)
            if line.modified and line.modified != line.src:
                self.line_changes.append(line)
                yield self.line_changes[-1]

    def write_changes(self):

        # Insert changes
        lines = self.read_lines()
        for change in self.line_changes:
            if lines[change.line_num-1].src != change.src:
                raise SourceChanged(f"{self.name} changed")
            lines[change.line_num-1] = change

        # Backup target file
        bkp = self.path.parent / (self.path.name + '.setversion.tmp')
        if bkp.exists():
            bkp.unlink()
        self.path.rename(bkp)

        # Write out
        try:
            with self.path.open('wb') as fh:
                fh.write(self.LINE_SEP.join([(line.modified or line.src) for line in lines]))
        except Exception as e:
            raise WriteFailed(
                f"ERROR writing to {self.path}: {e.__class__.__name__}: {e}\nBackup at {bkp}"
            ) from e

        # Clean up
        bkp.unlink()


class Project:
    """
    Represents a project folder that the tool can be used in.

    The project will have a setversion.ini file that controls the behaviour of the tool
    for all files under the project folder.
    """

    DEFAULT_CONFIG = dedent("""\
        [default]
        current_version = 0.0.0
        ; ^setversion - Ensure this marker is set so setversion updates this version too!
    
        line_marker = setversion
        next_line_marker = setversion:
        prior_line_marker = ^setversion

        max_line_length = 1024

        [ignore]
        path = .git
    """)

    CONFIG_FILENAME = "setversion.ini"
    DEFAULT_COMPONENT = "default"

    def __init__(self, folder: Path, component: str = None):
        self.path = folder
        self.config_path = self.path / self.CONFIG_FILENAME
        self.config = configparser.ConfigParser()
        self.settings = {}
        self.ignores = []
        self.component = component or self.DEFAULT_COMPONENT

        self._load_config()

    @staticmethod
    def init_folder(path: Path, init_version: str = '0.0.0') -> "Project":
        config_path = path / Project.CONFIG_FILENAME
        if config_path.exists():
            abort(f"{config_path.absolute()} already exists")
        with config_path.open('wt') as fh:
            fh.write(Project.DEFAULT_CONFIG.replace('0.0.0', init_version))
        return Project(path)

    def _load_config(self):
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        self.config.read(self.config_path)
        if self.component not in self.config:
            raise ValueError(f"Missing [{self.component}] section in {self.config_path}")

    def _get_required_config_key(self, section: str, key: str, _type = str):
        if section not in self.config:
            abort(f"Missing [{section}] section in {self.config_path}")
        section = self.config[section]
        if key not in section or not section.get(key):
            abort(f"Missing {key}= in [{section}] section in {self.config_path}")
        try:
            return _type(section.get(key))
        except Exception as e:
            abort(f"Missing {key}= in [{section}] could not be interpreted in {self.config_path}: {e}")

    @property
    def current_version(self) -> str:
        return self._get_required_config_key(self.component, 'current_version')

    @property
    def line_marker(self) -> bytes:
        return self._get_required_config_key(self.component, 'line_marker').encode('ascii')

    @property
    def next_line_marker(self) -> bytes:
        return self._get_required_config_key(self.component, 'next_line_marker').encode('ascii')

    @property
    def prior_line_marker(self) -> bytes:
        return self._get_required_config_key(self.component, 'prior_line_marker').encode('ascii')

    @property
    def max_line_length(self) -> int:
        return int(self.config.get(self.component, 'max_line_length', fallback=1024))

    @property
    def ignore_list(self) -> Iterable[str]:
        # Check for ignore section first
        ignores = list()
        if 'ignore' in self.config:
            ignore_section = self.config['ignore']
            for key, value in ignore_section.items():
                # Support both comma and newline separated values
                ignores.extend([i.strip() for i in re.split(r'[\n,]+', value) if i.strip()])
        return list(set(ignores))

    def check_ignored(self, name: str) -> bool:
        """Check to see if file or director is ignored"""
        names = {
            name,                   # Full name
            Path(name).name,        # base name
        }
        for pat in self.ignore_list:
            for name in names:
                if fnmatch(name, pat):
                    return True
        return False

    def get_available_components(self) -> list[str]:
        """Get list of available component sections (excluding 'ignore')"""
        return [section for section in self.config.sections() if section != 'ignore']

    def find_project_files(self) -> Iterable[ProjectFile]:
        """List all project files to consider"""

        def _find_files(root: Path, root_name: Optional[str]) -> Iterable[str]:
            for child in root.iterdir():
                if root_name:
                    child_name = f"{root_name}{os.path.sep}{child.name}"
                else:
                    child_name = child.name
                if not self.check_ignored(child_name):
                    if child.is_dir():
                        yield from _find_files(child, child_name)
                    elif child.is_file():
                        yield child_name

        for name in _find_files(self.path, root_name=None):
            yield ProjectFile(project=self, name=name, path=self.path / name)


def abort(msg: str, changed: bool = False):
    print()
    print(f"ERROR: {msg}")
    if not changed:
        print("no changes made")
    sys.exit(2)


def existing_file(path: str) -> Path:
    path = Path(path)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"File does not exist: {path}")
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"Not a file: {path}")
    return path


def existing_folder(path: str) -> Path:
    path = Path(path)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"File does not exist: {path}")
    if not path.is_dir():
        raise argparse.ArgumentTypeError(f"Not a folder: {path}")
    return path

def existing_project_folder(path: str) -> Path:
    path = existing_folder(path)
    coinfig_path = path / Project.CONFIG_FILENAME
    if not coinfig_path.exists():
        raise argparse.ArgumentTypeError(
            f"{path} is not a project folder (no {Project.CONFIG_FILENAME}).\nUse setversion init if needed")
    return path

def encodable_str(value: str) -> bytes:
    value = value.encode()
    return value


def all_parents(from_folder: Path) -> Iterable[Path]:
    if from_folder.is_dir():
        yield from_folder
    yield from from_folder.parents


def find_project(from_folder: Path) -> Optional[Path]:
    """Find the project root folder based on setversion.ini file"""
    for folder in all_parents(from_folder):
        if (folder / Project.CONFIG_FILENAME).exists():
            return folder
    return None


def main():
    parser = argparse.ArgumentParser(
        prog='setversion.py',
        description='Quickly change the version of stack by adjusting the compose file.'
    )
    subparsers = parser.add_subparsers(dest='cmd', help='command help')

    init = subparsers.add_parser('init', help='Create settings file to prep folder for use')
    init.add_argument('path', type=existing_folder, default='.', nargs='?',
        help='Path to project folder')

    search = subparsers.add_parser('search', help='Search source files')
    search.add_argument('term', type=encodable_str, help="Search term")

    bump = subparsers.add_parser('bump', help="Bump version")
    bump.add_argument('version', nargs='?')
    bump.add_argument('--component', '-c', default='default',
        help='Component configuration section (default: default)')
    bump.add_argument('--no-prompt', action='store_true',
        help="Don't prompt to confirm")

    for cmd in (search, bump):
        cmd.add_argument('--project', type=existing_folder, default='.',
            help="Project path to look for version numbers")

    args = parser.parse_args()

    def _print_attr(title: str, detail: str):
        print(f"{title}:".ljust(13) + detail)

    def _get_project_arg():
        p = args.project or find_project(Path('.').absolute())
        if str(p) == '.':
            p = p.absolute()
        return Project(p)

    # Init project
    if args.cmd == 'init':
        project = Project.init_folder(args.path, init_version=input("Initial version: ").strip() or '0.0.0')
        print(f"Initialized {project.config_path.absolute()}")

    elif args.cmd == 'search':
        project = _get_project_arg()
        _print_attr("Project", str(project.path))

        print()
        cnt = 0
        for file in project.find_project_files():
            try:
                for line in file.read_lines():
                    if args.term in line.src:
                        print(f"{file.name}[{line.line_num}]: {line.text.strip()}")
                        cnt += 1
            except BinaryFile:
                pass

        if not cnt:
            print(f"Did not find {args.term.decode()}")

    elif args.cmd == 'bump':
        project = _get_project_arg()
        _print_attr("Project", str(project.path))
        _print_attr("Component", args.component)
        _print_attr("Current", str(project.current_version))

        # Determine new version
        version = args.version
        if not version:
            version = input("New Version: ")
        else:
            print(f"New Version: {version}")
        print()

        # Search for changes
        files = []
        for file in project.find_project_files():
            try:
                for line in file.scan_for_version_changes(str(project.current_version), version):
                    if file.name != Project.CONFIG_FILENAME:
                        print(f"{file.name}[{line.line_num}]: {line.text.strip()}")
                if file.has_changes:
                    files.append(file)
            except BinaryFile:
                pass

        if files:

            # Confirm
            if not args.no_prompt:
                print()
                if input("Continue (y/n)? ").strip().lower() not in ('y', 'yes'):
                    print("No changes made")
                    return

            # Write changes
            print()
            for file in files:
                print(f"Modifying {file.name}")
                try:
                    file.write_changes()
                except SourceChanged:
                    print(f"ERROR: {file.path} changed before writing")

            print("\nFinished")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
