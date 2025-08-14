# Pages json generator

A terrible plugin for mkdocs to generate a `pages.json` file for sites that have a `reviewdate` field on pages

Makes a json file like

```json
[
  {
    "title": "Aqua Page 1",
    "url": "http://127.0.0.1:8000/security/aqua/aqua-page-1/",
    "review_by": "2022-01-01"
  },
  {
    "title": "Aqua Page 2",
    "url": "http://127.0.0.1:8000/security/aqua/aqua-page-2/",
    "review_by": "2022-01-01"
  },
  {
    "title": "Aqua partnership notes",
    "url": "http://127.0.0.1:8000/security/aqua/partnership-info/",
    "review_by": "2022-01-01"
  }
]
```

## Install

```shell
pip3 install git+https://github.com/userbradley/mkdocs-pages-json-plugin.git
```

This is until I can figure out how to put this on PyPi or what ever

```yaml
plugins:
  - pages-json:
        output_file: 'api/pages.json'
```

## Using

You should now be able to go to your site, and the path you chose (for example `api/pages.json`) and see the file.

An example of this in action: https://documentation.breadnet.co.uk/api/pages.json

---

Built by Bradley, with love in the UK. Licensed under MIT so you can do what ever you want with this
