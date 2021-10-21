# Access 2020 Local Elections

A proof of concept to evaluate the accessibility of political campaign
digital materials.

## Background

To better understand how political campaigns make their platforms accessible to their
constituents, we are building tools to help quickly and easily evaluate their
campaign website (and potentially, any additionally linked materials --
i.e. PDFs of their plans).

For example, are political campaigns taking the time to ensure all elements of their
digital materials are accessible to low-or-no vision individuals. Are political
campaigns ensuring that their materials are available in multiple languages?

In many cases we can combine the data produced by our tools with census data
regarding disability populations and language-spoken-at-home statistics.
But we can also study correlations between web accessibility and campaign spending.

## Usage

In general, follow the instructions described in [CONTRIBUTING.md](./CONTRIBUTING.md) to
install required packages.

Once installation and setup are complete, to generate a full accessibility evaluation
report for a website, run:

```bash
make generate-report url={URL}
```

i.e.

```bash
make generate-report url="https://jacksonmaxfield.github.io/"
```

### Maintainer Usage

If you are a maintainer of this library (or of a fork of this library),
you can generate accessibility reports for any URL by using the
[Generate Report GitHub Action](https://github.com/BITS-Research/access-2020-localelections/actions/workflows/generate-report.yml).

![Screenshot of using workflow dispatch with URL parameter](https://raw.githubusercontent.com/BITS-Research/access-2020-localelections/main/docs/_static/workflow-dispatch.png)
