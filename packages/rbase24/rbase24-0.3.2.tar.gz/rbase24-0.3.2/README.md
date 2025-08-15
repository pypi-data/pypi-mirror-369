# rbase24

A command line tool to print base16/base24 color schemes to the terminal.

Best installed using [`pipx`](https://pypi.org/project/pipx/) or your Python installer of choice.

```sh
pipx install rbase24
```

To specify the location of the color scheme files either...

1. Set the `BASE24_SCHEME_DIR` environment variable to point to the directory
   containing the scheme files.
2. Create a `config.ini` file in `$HOME/.config/rbase24` with a single entry

   ```ini
   [rbase24]
   scheme_dir = "<scheme file directory>"
   ```

Run the `rbase24` command passing an optional filespec to filter the list of
files.

The filespec will have `*` and `.yaml` added if necessary so
`gruvbox`, `gruvbox*` and `gruvbox*.yaml` will find the same schemes. Schemes are searched for in all subdirectories.

```bash
rbase24 gruvbox-li
```

Displays the following

![console output](https://github.com/sffjunkie/rbase24/raw/main/src/docs/rbase24_gruvbox.png)

- Uses the [rich](https://rich.readthedocs.io/en/latest/) library for the fancy formattting.
- Uses [typer](https://typer.tiangolo.com/) for the almost non-existent cli handling.
