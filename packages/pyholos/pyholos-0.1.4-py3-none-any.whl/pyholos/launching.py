import subprocess
from pathlib import Path, PureWindowsPath

from pyholos.config import PATH_HOLOS_CLI
from pyholos.utils import print_holos_msg


def set_cmd(
        path_dir_farms: Path,
        path_dir_outputs: Path = None,
        name_farm_json: str = None,
        name_dir_farms_json: str = None,
        name_settings: str = None,
        id_slc_polygon: int = None,
) -> list[str]:
    cmd = [
        'cmd', '/c',
        str(PureWindowsPath(PATH_HOLOS_CLI)),
        str(PureWindowsPath(path_dir_farms)),
        '-u',
        'metric'
    ]

    if path_dir_outputs is not None:
        cmd += ['-o', path_dir_outputs]

    if name_farm_json is not None:
        cmd += ['-i', name_farm_json]

    if name_dir_farms_json is not None:
        cmd += ['-f', name_dir_farms_json]

    if name_settings is not None:
        if any([name_farm_json is not None, name_dir_farms_json is not None]):
            cmd += ['-s', name_settings]

    if id_slc_polygon is not None:
        cmd += ['-p', str(int(id_slc_polygon))]

    return cmd


def launch_holos(
        path_dir_farms: Path,
        path_dir_outputs: Path = None,
        name_farm_json: str = None,
        name_dir_farms_json: str = None,
        name_settings: str = None,
        id_slc_polygon: int = None,
        is_print_holos_messages: bool = False
) -> None:
    cmd = set_cmd(
        path_dir_farms=path_dir_farms,
        path_dir_outputs=path_dir_outputs,
        name_farm_json=name_farm_json,
        name_dir_farms_json=name_dir_farms_json,
        name_settings=name_settings,
        id_slc_polygon=id_slc_polygon
    )

    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True)

    for msg in _get_cli_messages(p=process):
        print_holos_msg(is_print_message=is_print_holos_messages, holos_message=msg)

        if msg.startswith("Do you have farms that you would like to import from the Holos GUI? (yes/no)"):
            process.stdin.write('no\n')
            process.stdin.flush()
        if "press enter to exit" in msg:
            process.stdin.write('\n')
            process.stdin.flush()
    pass


def _get_cli_messages(p: subprocess.Popen) -> str:
    while True:
        # returns None while subprocess is running
        return_code = p.poll()
        yield p.stdout.readline()
        if return_code is not None:
            break
