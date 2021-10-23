# Understanding the Produced Results
This document will explain how to interpret the results of a website accessibility test that was run against your campaign website. 

## Report
Our tool analyzes any link that is self-referencing to your own website and generates
an accessibility report [^1]. As a simple example - If the starting page is `www.a.com` and on that page there are links to
`www.a.com/subsection` and `www.b.com`, our tool will create an accessibility evaluation
for both `www.a.com` and `www.a.com/subsection` but will skip-over `www.b.com`
as it is not the same website.

Using our prior example, the produced report for `www.a.com`
would include:

```
www.a.com/
├── accessibility-violations-summarized.csv
├── aggregated-accessibility-violations-summarized.csv
├── email.txt
├── full-axe-results.json
└── subsection
    ├── accessibility-violations-summarized.csv
    └── full-axe-results.json
```

Notice that `subsection` is now a child folder in the parent `www.a.com` folder.

This structure should mirror your website's page layout. This structure also makes it possible to
quickly check the accessibility evaluation that we have run for each individual page on your site.

## Basic Contents
Each directory, regardless of it is the starting page or a found page,
will contain the following files:

-   `accessibility-violations-summarized.csv`
-   `full-axe-results.json`

### Accessibility Violations Summarized

This is a CSV file that summarizes the violations found for that page
("that page" meaning the full directory path, i.e. `www.a.com/subsection` is the
folder name and the webpage).

This CSV has six fields:

-   `id`: the id, shortname, or general classification of the
    violation ("color-contrast", "heading-order", etc.)
-   `impact`: the severity of the violation in plain text
-   `impact_score`: the severity of the violation as an integer (useful for sorting)
-   `reason`: the short description of why this is a violation
-   `number_of_elements_in_violation`: the number of HTML elements
    affected by this violation for this page
-   `help_url`: a link to the specific
    [Deque University rule that was violated](https://dequeuniversity.com/rules/axe/3.1/)
    for more details

### Full Axe Results

This is a JSON file containing the full resulting output from running the
axe accessibility evaluation tool for the page.

We utilize the `"violations"` section of this document which looks like the following:

```
"violations": [
    {
        "description": "Ensures the contrast between foreground and background colors meets WCAG 2 AA contrast ratio thresholds",
        "help": "Elements must have sufficient color contrast",
        "helpUrl": "https://dequeuniversity.com/rules/axe/3.1/color-contrast?application=axeAPI",
        "id": "color-contrast",
        "impact": "serious",
        "nodes": [
            ...
        ]
    },
]
```

This may already start to look a bit familiar, as this is where we are pulling our
aggregated data from.

The `"nodes"` subsection of `"violations"` is where you can find all the HTML elements
or nodes that are in violation of the specified rule.

A single node section looks something like the following:

```
{
    "all": [],
    "any": [
        {
            "data": {
                "bgColor": "#f9f4ec",
                "contrastRatio": 2.93,
                "expectedContrastRatio": "4.5:1",
                "fgColor": "#ff4f5e",
                "fontSize": "14.4pt",
                "fontWeight": "normal",
                "missingData": null
            },
            "id": "color-contrast",
            "impact": "serious",
            "message": "Element has insufficient color contrast of 2.93 (foreground color: #ff4f5e, background color: #f9f4ec, font size: 14.4pt, font weight: normal). Expected contrast ratio of 4.5:1",
            "relatedNodes": [
                {
                    "html": "<body>",
                    "target": [
                        "body"
                    ]
                }
            ]
        }
    ],
    "failureSummary": "Fix any of the following:\n  Element has insufficient color contrast of 2.93 (foreground color: #ff4f5e, background color: #f9f4ec, font size: 14.4pt, font weight: normal). Expected contrast ratio of 4.5:1",
    "html": "<a href=\"#public-interest-technology\">Public Interest Technology</a>",
    "impact": "serious",
    "none": [],
    "target": [
        "li:nth-child(1) > a[href=\"#public-interest-technology\"]"
    ]
}
```

Breaking this down, we can see exactly which element(s) was reported in violation
from the `"html"` and `"target"` fields:

```
"html": "<a href=\"#public-interest-technology\">Public Interest Technology</a>",
...
"target": [
    "li:nth-child(1) > a[href=\"#public-interest-technology\"]"
]
```

In this case, it looks like the website has a link to a page called
"Public Interest Technology" however if you need more specifics the `"target"`
field details that it is the 1st list item that contains
an anchor element (`li:nth-child(1) > a`).

Additionally, `axe` reports _why_ these elements were marked
as a violation in the `"failureSummary"` field.

> Fix any of the following:\n Element has insufficient color contrast of 2.93
> (foreground color: #ff4f5e, background color: #f9f4ec, font size: 14.4pt,
> font weight: normal). Expected contrast ratio of 4.5:1

We can see that this particular link's font color does not
contrast enough from the background color.

### Aggregated Accessibility Violations Summarized
This file will always live at the top of the report and
stores the violation results from aggregating each child
[Accessibility Violations Summarized](#accessibility-violations-summarized).

The only additional field added to this CSV over each
`accessibility-violations-summarized.csv` is:

-   `number_of_pages_affected`: which is the count of the number of pages in
    your website affected by this violation

### Pages Not Included

Pages on your website may not be picked up by our tool for a variety of reasons
however the most common would be:

-   The webpage that is missing from the report was not linked to by
    any of the found webpages.
-   The webpage was a document. It is very common to store policy proposals
    on a website as a PDF or similar static file however our tools
    do not currently parse such files or pages.
-   Something went wrong during processing of an individual webpage.

---

If you have any questions or would like clarification on this documentation
please simply respond to our original email. We are happy to work with you to improve your site's accessibility to all voters. 

[^1]: This report is generated with support from the [axe](https://www.deque.com/axe/) toolset.
