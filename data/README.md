# LaTeX user template and guide

To compile user guide:

1. `pdflatex sample-DL26`
2. `bibtex sample-DL26`
3. `pdflatex sample-DL26`
4. `pdflatex sample-DL26`

use the makefile:

`make`


For the "minted" versions:

1. `pdflatex -shell-escape sample-DL26+minted`
2. `pdflatex -shell-escape sample-DL26+minted`


