# xmlist

`xmlist` is a module for generating XML, which it represents by lists and
tuples.

## using xmlist

    doc = ['html',
        ('xmlns', 'http://www.w3.org/1999/xhtml'),
        ['head', ['title', 'Hello, world!']],
        ['body',
            ['h1', 'Hello, world!'],
            ['p', 'xmlist is a module for generating XML']]]
    xml = xmlist.serialize(doc)

## hacking on xmlist

Create a venv and install the package with the `-e`/`--editable` flag. The
`dev` extra  pulls in requirements for  setuptools and tox; and the `test`
extra for various pytest packages.

    python -m venv env
    env/bin/python -m pip install -e .[dev,test]

## testing xmlist

Running the tests for your current Python:

    env/bin/python -m pytest -v

Running the tests in other Pythons:

    env/bin/python -m tox
