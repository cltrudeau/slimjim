# slimjim

Absolute hack for injecting pretend typing into an application when recording
screen casts.

Requires command-line tool [sendkeys](https://github.com/socsieng/sendkeys)
installed to do the typing injection.

Two commands:

* `slimfile` takes a file and uses it as a source for content to inject
* `slimspec` takes a content specification containing instruction fields and
    injectable content


# Install

`pip install slimjim`

Commands will be in your path


## Warning

This project ships with a copy of an unreleased version of a widget from 
[asciimatics](https://asciimatics.readthedocs.io/en/stable/index.html) in
order to take advantage of features that haven't been released yet.
