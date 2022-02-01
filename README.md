# Campaign Website Accessibility Evaluation

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

## Recreating Analysis

To recreate our analysis of our preliminary 2021 study:

1. Clone the repo
2. In a terminal navigate to the cloned repo
3. In the repo directory run

```bash
pip install .
analyze-access-eval-2021-dataset
```

This will generate all of the plots used in our paper and place them
in a directory called `plots/`. It will also create a file called `stats.json`
which contains the statistics used in our paper (generated from t-tests, ANOVA, etc.)

## aXe Scraper Usage

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

### Maintainer GitHub Action

If you are a maintainer of this library (or of a fork of this library),
you can generate accessibility reports for any URL by using the
[Generate Report GitHub Action](https://github.com/BITS-Research/campaign-access-eval/actions/workflows/generate-report.yml).

![Screenshot of using workflow dispatch with URL parameter](https://raw.githubusercontent.com/BITS-Research/campaign-access-eval/main/docs/_static/workflow-dispatch.png)
