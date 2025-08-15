import typer

app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.command()
def dev(sql: bool = typer.Option(False, "--sql", "-s")):
    """
    Develop code.
    """
    from ascend_community.lib.dev import run

    run(sql=sql)


@app.command()
def decomplect(clean: bool = typer.Option(False, "--clean")):
    """
    Decomplect the projects/ottos-expeditions/internal Project.
    """
    from ascend_community.lib.decomplect import run

    run(clean=clean)


if __name__ == "__main__":
    app()
