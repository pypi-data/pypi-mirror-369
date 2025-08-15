# ipyswiper

A reusable interactive image gallery component for Jupyter Notebooks.

This component provides an interactive image gallery with:
- Main image display with optional fade effects
- Scrollable thumbnail strip
- Keyboard navigation support
- Standalone HTML export

## Notebook example

https://nbviewer.org/github/leejjoon/ipyswiper/blob/main/notebooks/jupyter_gallery_demo.ipynb

## Install

Once you download/fork repository

    pip install .

## Command-Line Usage

`ipyswiper` can be run as a command-line tool to generate a standalone HTML gallery from a JSON file.

### Basic Usage

To generate the gallery and print the HTML to standard output:

```bash
python -m ipyswiper examples/demo.json
```

### Saving to a File

To save the gallery to an HTML file, use the `-o` or `--output` option:

```bash
python -m ipyswiper examples/demo.json -o my_gallery.html
```

### Using Custom JSON Keys

If your JSON file uses different keys for the image label and path, you can specify them with `--label-key` and `--image-key`:

```bash
python -m ipyswiper examples/custom_keys.json --label-key caption --image-key url
```

### Other Options

The command-line tool supports various options to customize the gallery's appearance and behavior. To see all available options, run:

```bash
python -m ipyswiper --help
```

## For Administrators

### How to Publish to PyPI

To publish this package to PyPI, you will need to have `flit` installed.

1.  **Install flit**

    ```bash
    pip install flit
    ```

2.  **Build the package**

    ```bash
    flit build
    ```

3.  **Publish to PyPI**

    ```bash
    flit publish
    ```

    You will be prompted for your PyPI username and password.
