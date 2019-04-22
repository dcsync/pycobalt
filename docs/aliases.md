
# pycobalt.aliases

For registering beacon console aliasess

Regular example:

    def test_alias(args):
        print(args)
    aliases.register('test_alias', test_alias)

Decorator example:

    @aliases.alias('test_alias')
    def test_alias(args):
        print(args)

## register
```python
register(name,
         callback,
         short_help=None,
         long_help=None,
         quote_replacement=None)
```

Register an alias

Regarding the quote_replacement argument: Cobalt Strike's Beacon console
uses double quotes to enclose arguments with spaces in them. There's no way
to escape double quotes within those quotes though. Set quote_replacement
to a string and PyCobalt will replace it with " in each argument.

**Arguments**:

- `name`: Name of alias
- `callback`: Callback for alias
- `short_help`: Short version of help, shown when running `help` with no
                   arguments
- `long_help`: Long version of help, shown when running `help <alias>`.
                  By default this is generated based on the short help and syntax of the
                  Python callback.
- `quote_replacement`: Replace this string with " in each
                          argument.

## alias
```python
alias(name, short_help=None, long_help=None, quote_replacement=None)
```

Decorator for alias registration
