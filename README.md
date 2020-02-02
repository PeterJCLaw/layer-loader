# Layer-Loader

[![CircleCI](https://circleci.com/gh/PeterJCLaw/layer-loader.svg?style=svg)](https://circleci.com/gh/PeterJCLaw/layer-loader)

Layer-loader is a Python library designed to allow easy composition of configuration files.

This project was inspired by [hiera][puppet-hiera], though intends to be somewhat simpler.

[puppet-hiera]: https://puppet.com/docs/puppet/latest/hiera_intro.html

## Usage

The primary interface is a Python API:

``` python
import json
import layer_loader

data = layer_loader.load_files(
    ['dev.json', 'main.json'],
    loader=json.load,
)
```

This will load the data from `dev.json` and `main.json`, interpreting it as JSON,
combine it into a single object and then any placeholders are expanded.

For convenience you can also run `layer_loader` as a module:

```shell
$ cat dev.json
{
    "url": "http://localhost:8000"
}
$ cat main.json
{
    "endpoints": [
        "{url}/abc",
        "{url}/def",
        "{url}/ghi"
    ],
    "url": "https://production.system"
}
$ python -m layer_loader --loader=json.load dev.json main.json
{
    "endpoints": [
        "http://localhost:8000/abc",
        "http://localhost:8000/def",
        "http://localhost:8000/ghi"
    ],
    "url": "http://localhost:8000"
}
```

## Layers

Layers are specified in order from most important (top) to least important (bottom).
When combining layers, layer-loader uses the following rules:

* Mappings can be _merged_, combining the entries from several layers
* Scalar values and lists _replace_ entries in the lower layers
* Keys in more important layers override those in lower layers
* Where keys are present in multiple layers, it is an error for those
  keys to have values of different types. The exception to this is
  that keys can explicitly be set to `null` in a higher layer in order
  to remove a value set in a lower layer.

## Placeholders

Placeholders are specified similarly to python format strings and may appear
anywhere inside a string value, for example `'foo {place.holder} bar'`.
Placeholders may *not* appear in keys.

Placeholders are expanded by walking the flattened data structure, using dots in
the placeholder to separate names at each level of nesting.

There is no mechanism to specify which layer a placeholder should be looked up
within -- all placeholder expansion happens after the layers have been
flattened.
