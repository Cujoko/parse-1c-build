# -*- coding: utf-8 -*-
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any

from commons import SettingsException
from commons_1c import get_last_1c_exe_file_path
from parse_1c_build.base import Processor


class Parser(Processor):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        # 1C
        if '1c' in kwargs:
            self.last_1c_exe_file_path = Path(kwargs['1c'])
        else:
            self.last_1c_exe_file_path = None
            if '1c' in self.settings:
                self.last_1c_exe_file_path = Path(self.settings['1c'])

        if self.last_1c_exe_file_path is None or not self.last_1c_exe_file_path.is_file():
            self.last_1c_exe_file_path = get_last_1c_exe_file_path()
            if self.last_1c_exe_file_path is None:
                raise Exception('Couldn\'t find 1C:Enterprise 8!')

        # IB
        if 'ib' in kwargs:
            self.ib_dir_path = Path(kwargs['ib'])
        else:
            if 'ib' not in self.settings:
                raise SettingsException('There is no service information base in settings!')
            self.ib_dir_path = Path(self.settings['ib'])

        if not self.ib_dir_path.is_dir():
            raise Exception('Service information base does not exist!')

        # V8Reader
        if 'v8reader' in kwargs:
            self.v8_reader_file_path = Path(kwargs['v8reader'])
        else:
            if 'v8reader' not in self.settings:
                raise SettingsException('There is no V8Reader in settings!')
            self.v8_reader_file_path = Path(self.settings['v8reader'])

        if not self.v8_reader_file_path.is_file():
            raise Exception('V8Reader does not exist!')

    def run(self, input_file_path: Path, output_dir_path: Path) -> None:
        with tempfile.NamedTemporaryFile('w', encoding='cp866', suffix='.bat', delete=False) as bat_file:
            bat_file.write('@echo off\n')
            input_file_path_suffix_lower = input_file_path.suffix.lower()
            if input_file_path_suffix_lower in ['.epf', '.erf']:
                bat_file.write('"{}" /F"{}" /DisableStartupMessages /Execute"{}" {}'.format(
                    str(self.last_1c_exe_file_path),
                    str(self.ib_dir_path),
                    str(self.v8_reader_file_path),
                    '/C"decompile;pathtocf;{};pathout;{};shutdown;convert-mxl2txt;"'.format(
                        str(input_file_path),
                        str(output_dir_path)
                    )
                ))
            elif input_file_path_suffix_lower in ['.ert', '.md']:
                input_file_path_ = input_file_path

                # fixme Тут что-то непонятное и скорее всего неработоспособное
                if input_file_path_suffix_lower == '.md':
                    temp_dir_name = tempfile.mkdtemp()
                    input_file_path_ = Path(shutil.copy(str(input_file_path_), temp_dir_name))

                bat_file.write('"{}" -d -F "{}" -DD "{}"'.format(
                    str(self.gcomp_file_path),
                    str(input_file_path_),
                    str(output_dir_path)
                ))

        exit_code = subprocess.check_call(['cmd.exe', '/C', str(bat_file.name)])
        if not exit_code == 0:
            raise Exception('Parsing \'{}\' is failed!'.format(str(input_file_path)))

        Path(bat_file.name).unlink()


def run(args: Any) -> None:
    processor = Parser()

    # Args
    input_file_path = Path(args.input[0])

    if args.output is None:
        output_dir_path = input_file_path.stem + '_' + input_file_path.suffix[1:] + '_src'
    else:
        output_dir_path = Path(args.output)

    processor.run(input_file_path, output_dir_path)


def add_subparser(subparsers: Any) -> None:
    desc = 'Parse 1C:Enterprise file in a directory'
    subparser = subparsers.add_parser(
        Path(__file__).stem,
        help=desc,
        description=desc,
        add_help=False)

    subparser.set_defaults(func=run)

    subparser.add_argument(
        '-h', '--help',
        action='help',
        help='Show this help message and exit')

    subparser.add_argument(
        'input',
        nargs=1)  # todo Добавить help

    subparser.add_argument(
        'output',
        nargs='?')  # todo Добавить help