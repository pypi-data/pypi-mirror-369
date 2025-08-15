# TODO: update these to share SQL strings, default to local `ascendlake/` directory, and more


def python_repl() -> None:
    import os  # noqa
    from importlib import reload  # noqa

    import IPython
    from rich import console

    import ascend_community as ac  # noqa

    # rich configuration
    console = console.Console()
    print = console.print  # noqa

    # print banner
    banner = """
▓█████▄ ▓█████ ██▒   █▓
▒██▀ ██▌▓█   ▀▓██░   █▒
░██   █▌▒███   ▓██  █▒░
░▓█▄   ▌▒▓█  ▄  ▒██ █░░
░▒████▓ ░▒████▒  ▒▀█░
 ▒▒▓  ▒ ░░ ▒░ ░  ░ ▐░
 ░ ▒  ▒  ░ ░  ░  ░ ░░
 ░ ░  ░    ░       ░░
   ░       ░  ░     ░
 ░                 ░
     """.strip()
    console.print(banner, style="bold purple")

    # create IPython shell
    IPython.embed(
        banner1="",
        banner2="",
        display_banner=False,
        exit_msg="",
        colors="linux",
        theming="monokai",
    )


def sql_repl() -> None:
    import subprocess

    bash_script = """
#!/usr/bin/env bash

set -euo pipefail

if [ -z "${LAKE:-}" ]; then
    LAKE="$HOME/lake"
    mkdir -p "$LAKE"
fi

duckdb -cmd "$(cat <<EOF
install ducklake;
install sqlite;

create secret (
    type ducklake,
    metadata_path 'sqlite:$LAKE/metadata.sqlite',
    data_path '$LAKE/data'
);

attach 'sqlite:$LAKE/metadata.sqlite' as metadata;
attach 'ducklake:' as data;

use data;

EOF
)"
"""
    subprocess.run(["bash", "-c", bash_script])


def run(sql: bool = False) -> None:
    if sql:
        sql_repl()
    else:
        python_repl()
