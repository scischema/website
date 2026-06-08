# SciSchema.org

Repository for the SciSchema.org website and machine-readable scientific process schemas.

This repository contains:

* JSON Schema representations of scientific processes.
* Metadata and auto-generation scripts used to build the schema catalog.
* Source files for the SciSchema.org website.

Website: https://scischema.org

## Repository Structure for Scientific Schema Storage

```text
auto-gen/
    schema-json/
    schema-metadata.csv
    generate_schema_pages.py

schemas/
    <domain>/<schema>/
        index.html
        master-schema.json
```

## Contributing

SciSchema is a community-driven collection of machine-readable scientific process schemas. Contributions from researchers and domain experts are welcome.

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed instructions on adding new schemas and submitting pull requests.

## License

Unless otherwise noted, the schemas and documentation in this repository are licensed under the Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0).

This license permits commercial use, distribution, and adaptation, provided that attribution is given and derivative works are distributed under the same license.
