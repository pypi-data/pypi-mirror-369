# odoc - OpenDocument Spreadsheet Generator

A lightweight spreadsheet generator, which targets LibreOffice.

Aims to provide an easy and painless way to create spreadsheets, without having to dive into the
details of the OpenDocument format.

Limitations:
- odoc is for the creation of documents only.  It does not read them, nor does it allow
  to interact with them, or edit them programatically.
- Charts are not supported (yet).
- The documentation sucks - as there is non. But, there are example files, which
  cover all aspects of odoc.
- No macro support.

Capabilities:
- Supports most styling options
- Named cells and ranges
- Conditional formating
- Images
- Cell comments
- Merged cells
- Array-formulas

## Installation

```shell
python3 -m pip install odoc
```

## Example
```python
from odoc import Calc

doc = Calc()
sheet = doc['Sheet1']

sheet[0,0] = 'Apples'
sheet[0,1] = 5

sheet[1,0] = 'Oranges'
sheet[1,1] = 7

sheet[2,0] = 'Total'
sheet[2,1] = f'=sum({sheet[0:1,1].address()})'

doc.save('sample.ods')
```

## Requirements

Python >= 3.11

## License

The project uses the [MIT](https://mit-license.org/) license.
