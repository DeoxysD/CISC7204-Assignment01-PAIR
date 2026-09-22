#!/usr/bin/env python3
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures" / "crime_vs_house_price.png"
OUT = ROOT / "CISC7204-Assgn01-mc63582-PreliminaryProjectProposal.docx"


def set_run_font(run, size=11, bold=False, italic=False, name="Calibri"):
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.name = name
    r = run._element.get_or_add_rPr()
    rFonts = r.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        r.append(rFonts)
    rFonts.set(qn("w:ascii"), name)
    rFonts.set(qn("w:hAnsi"), name)
    rFonts.set(qn("w:eastAsia"), name)


def add_hyperlink(paragraph, text, url):
    part = paragraph.part
    r_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)
    new_run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "0563C1")
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), "22")
    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:ascii"), "Calibri")
    rFonts.set(qn("w:hAnsi"), "Calibri")
    rPr.extend([u, color, sz, rFonts])
    new_run.append(rPr)
    t = OxmlElement("w:t")
    t.text = text
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    new_run.append(t)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)


def add_runs(para, parts):
    for text, kwargs in parts:
        run = para.add_run(text)
        set_run_font(run, **kwargs)


def main() -> None:
    doc = Document()
    for section in doc.sections:
        section.top_margin = Cm(2.2)
        section.bottom_margin = Cm(2.2)
        section.left_margin = Cm(2.4)
        section.right_margin = Cm(2.4)

    def para(text="", size=11, bold=False, italic=False, after=8):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(after)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.line_spacing = 1.15
        if text:
            run = p.add_run(text)
            set_run_font(run, size=size, bold=bold, italic=italic)
        return p

    def heading(text, level=1):
        h = doc.add_heading(text, level=level)
        for run in h.runs:
            set_run_font(run, size=16 if level == 1 else 13, bold=True)
            run.font.color.rgb = RGBColor(0x1F, 0x1F, 0x1F)
        h.paragraph_format.space_before = Pt(14 if level == 1 else 10)
        h.paragraph_format.space_after = Pt(6)
        return h

    def bullet(parts):
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(3)
        if isinstance(parts, str):
            run = p.add_run(parts)
            set_run_font(run)
        else:
            add_runs(p, parts)
        return p

    def numbered(parts):
        p = doc.add_paragraph(style="List Number")
        p.paragraph_format.space_after = Pt(4)
        if isinstance(parts, str):
            run = p.add_run(parts)
            set_run_font(run)
        else:
            add_runs(p, parts)
        return p

    def cover_line(text, size=14, bold=False, italic=False, after=10):
        p = para(text, size=size, bold=bold, italic=italic, after=after)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        return p

    for _ in range(4):
        para("", after=6)
    cover_line("University of Macau", size=16, bold=True, after=6)
    cover_line("", after=6)
    cover_line("Assignment 01 – Preliminary Project Proposal", size=18, bold=True, after=8)
    cover_line("Crime and House Prices in London Boroughs", size=14, italic=True, after=28)

    cover_fields = [
        ("Student ID", "mc63582"),
        ("Name", "FANZIQIAN"),
        ("Course code", "CISC7204"),
        ("Course name", "Data Science and Data Visualization"),
        ("Assignment", "Assignment 01 – Preliminary Project Proposal"),
    ]
    for lab, val in cover_fields:
        p = para(after=8)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_runs(p, [(f"{lab}: ", {"bold": True, "size": 12}), (val, {"size": 12})])

    doc.add_page_break()

    heading("Project Title")
    p = para()
    add_runs(p, [("Crime and House Prices in London Boroughs", {"bold": True})])
    p = para()
    add_runs(
        p,
        [
            ("Research question: ", {"bold": True}),
            (
                "In London, United Kingdom, do administrative areas with more crime records have lower average house prices?",
                {},
            ),
        ],
    )
    para(
        "This is a judgement based on common sense (crime is commonly believed to depress house prices). "
        "This proposal aims to test whether public data at the administrative-area level actually support that claim."
    )

    heading("Region and Domain")
    bullet(
        [
            ("Region: ", {"bold": True}),
            (
                "London, United Kingdom (covering 32 London boroughs; the City of London is excluded "
                "from the 2016–2018 panel because crime or population data are incomplete).",
                {},
            ),
        ]
    )
    bullet(
        [
            ("Domain category: ", {"bold": True}),
            ("Housing and urban safety (house prices, crime records, residents’ income).", {}),
        ]
    )

    heading("Datasets (at least two public links)")
    p = numbered(
        [
            ("Housing in London (Kaggle)", {"bold": True}),
            (
                " — two CSV files available for download (monthly house prices, sales volume, and crime records; "
                "annual wages, population, and dwelling counts): ",
                {},
            ),
        ]
    )
    add_hyperlink(
        p,
        "https://www.kaggle.com/datasets/justinas/housing-in-london",
        "https://www.kaggle.com/datasets/justinas/housing-in-london",
    )

    p = numbered(
        [
            (
                "Average house prices by borough (London Datastore / GLA, based on HM Land Registry Price Paid Data)",
                {"bold": True},
            ),
            (" — official borough-level house-price tables: ", {}),
        ]
    )
    add_hyperlink(
        p,
        "https://data.london.gov.uk/dataset/average-house-prices",
        "https://data.london.gov.uk/dataset/average-house-prices",
    )

    p = para()
    add_runs(
        p,
        [
            (
                "The Kaggle data package also cites crime summaries recorded by the Metropolitan Police, hosted on the London Datastore: ",
                {},
            )
        ],
    )
    add_hyperlink(
        p,
        "https://data.london.gov.uk/dataset/mps-recorded-crime-geographic-breakdown-exy3m/",
        "https://data.london.gov.uk/dataset/mps-recorded-crime-geographic-breakdown-exy3m/",
    )

    para("Local copies used in this proposal:")
    for fname in ["data/housing_in_london_monthly.csv", "data/housing_in_london_yearly.csv"]:
        bullet([(fname, {"italic": True})])

    heading("Visualization and commentary")
    para(
        "Figure 1. London boroughs: “higher crime rates” are not associated with “lower house prices.”",
        size=10,
        italic=True,
        after=6,
    )
    pic = doc.add_paragraph()
    pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pic.paragraph_format.space_after = Pt(10)
    pic.add_run().add_picture(str(FIG), width=Inches(6.3))

    para(
        "The figure shows the scatter of 32 London boroughs. The horizontal axis is crime records per 1,000 "
        "residents; the vertical axis is average house price. Both are 2016–2018 means, to avoid interference "
        "from single-year noise. Point colour represents median resident wages from the annual data. A least-squares "
        "line is drawn only as a visual aid."
    )

    p = para()
    add_runs(
        p,
        [
            (
                "This figure is intended to answer the research question above, not to predict house prices. "
                "If the conventional view held, high-price boroughs would lie in the upper-left of the figure "
                "(low crime, high prices), or the relationship would at least slope downward. That is not the case. "
                "Spearman’s rank correlation between the crime rate and house prices is ",
                {},
            ),
            ("ρ = 0.47 (p ≈ 0.007)", {"bold": True}),
            (
                ": administrative areas with more crime records per resident tend instead to have higher prices. "
                "Westminster and Kensington and Chelsea have high house prices and similarly high crime records per "
                "resident; outer boroughs such as Bexley have lower prices and fewer crime records per resident. "
                "Wages rise together with both house prices and crime rates, so this pattern is closer to “central, "
                "higher-income areas have both higher house prices and more recorded offences” than to “crime causes "
                "house prices to fall.” It should be noted that the figure does not show that crime causes high prices; "
                "it only shows that these data contain no simple negative association of the form “higher crime, lower prices.”",
                {},
            ),
        ],
    )

    heading("Project Purpose")
    heading("Outcomes", 2)
    para(
        "This project combines the course content on statistical inquiry with a real public-data question: "
        "take a view that people already hold, find two government-derived tables related to a specified place, "
        "process and present the data, and assess whether the results support that view."
    )
    heading("Skills", 2)
    bullet(
        [
            ("Multi-source joining and aggregation: ", {"bold": True}),
            (
                "Locate and cite public tabular data (CSV / open-data portals); apply groupby + agg to the monthly "
                "and annual tables by area and year, then merge them to build a borough-level panel.",
                {},
            ),
        ]
    )
    bullet(
        [
            ("Panel construction: ", {"bold": True}),
            (
                "Aggregate monthly data to annual (prices as means, crime as sums), and use crime_months >= 10 "
                "to exclude years with incomplete crime records.",
                {},
            ),
        ]
    )
    bullet(
        [
            ("Derived measures: ", {"bold": True}),
            (
                "Construct the population-adjusted crime rate crime_per_1000, to avoid bias from using raw crime "
                "counts driven by population size.",
                {},
            ),
        ]
    )
    bullet(
        [
            ("Association analysis: ", {"bold": True}),
            (
                "Use Spearman rank correlation rather than Pearson, to accommodate non-normal distributions and "
                "non-linear but monotonic relationships; also include comparison groups (wages vs house prices, "
                "crime counts vs house prices).",
                {},
            ),
        ]
    )
    bullet(
        [
            ("Visualization design: ", {"bold": True}),
            (
                "Scatter plot + OLS guide line + colour mapping of a third variable + selective labelling of "
                "high-leverage points, balancing information density and readability.",
                {},
            ),
        ]
    )
    bullet(
        [
            ("Matching claims to evidence: ", {"bold": True}),
            (
                "Distinguish association from causation; use the ecological fallacy to explain that borough averages "
                "cannot be inferred at the household level.",
                {},
            ),
        ]
    )
    heading("Knowledge", 2)
    bullet(
        [
            ("The distinction between crime “counts” and crime “rates”: ", {"bold": True}),
            (
                "raw crime counts are affected by borough population; this analysis uses crime_per_1000 "
                "(crime count ÷ population × 1000) for population adjustment, so that boroughs can be compared.",
                {},
            ),
        ]
    )
    bullet(
        [
            ("Panel data versus cross-sectional data: ", {"bold": True}),
            (
                "using 2016–2018 three-year means rather than a single year reduces the effect of single-year noise "
                "on borough ranking; crime_months >= 10 is also used to exclude years with incomplete crime records.",
                {},
            ),
        ]
    )
    bullet(
        [
            ("Why Spearman rather than Pearson: ", {"bold": True}),
            (
                "the relationship between house prices and crime rates need not be linear; Spearman requires only a "
                "monotonic relationship and is more robust to outliers. This analysis also includes two comparison "
                "pairs (wages vs house prices; crime counts vs house prices) to prevent a single correlation from being misread.",
                {},
            ),
        ]
    )
    bullet(
        [
            ("The effect of high-leverage points on regression: ", {"bold": True}),
            (
                "Westminster has both an extremely high crime rate and extremely high house prices, and it has a "
                "marked effect on the OLS slope; this shows that borough-level association results are sensitive to "
                "individual points and should be treated separately in robustness checks.",
                {},
            ),
        ]
    )
    bullet(
        [
            ("Truncation and misleading charts: ", {"bold": True}),
            (
                "axis ranges, the colour-mapped variable, sample size, and the choice of comparison group all affect "
                "how strongly readers perceive the relationship; the OLS line on this figure is a visual aid only, "
                "not for prediction.",
                {},
            ),
        ]
    )
    bullet(
        [
            ("Ecological fallacy: ", {"bold": True}),
            (
                "relationships among borough-level averages cannot be inferred at the street or household level; "
                "this analysis describes borough-level association only, makes no causal claims, and does not describe "
                "any single street or household.",
                {},
            ),
        ]
    )

    heading("Project Tasks")
    numbered(
        [
            ("Establish the research framework: ", {"bold": True}),
            (
                "Select the region (London, United Kingdom) and the domain (housing and urban safety), and pose "
                "a statistical question that can be answered yes or no.",
                {},
            ),
        ]
    )
    numbered(
        [
            ("Obtain public data: ", {"bold": True}),
            (
                "Download the monthly and annual public tables, retain the original source links, and keep the data traceable.",
                {},
            ),
        ]
    )
    numbered(
        [
            ("Build the analysis dataset: ", {"bold": True}),
            (
                "Aggregate monthly data to annual, join annual population and wage information, and form an "
                "administrative-area panel.",
                {},
            ),
        ]
    )
    numbered(
        [
            ("Filter and clean: ", {"bold": True}),
            (
                "Restrict to years with relatively complete crime records, and take means at the borough level "
                "to reduce the effect of single-year fluctuations.",
                {},
            ),
        ]
    )
    numbered(
        [
            ("Construct the core measure: ", {"bold": True}),
            (
                "Use the population-adjusted crime rate as the main explanatory variable, to avoid population-size "
                "bias from using total crime counts.",
                {},
            ),
        ]
    )
    numbered(
        [
            ("Conduct association analysis: ", {"bold": True}),
            (
                "Compute the rank correlation between the crime rate and house prices, and include comparison groups "
                "(wages, total crime counts) to aid interpretation.",
                {},
            ),
        ]
    )
    numbered(
        [
            ("Complete the visualization: ", {"bold": True}),
            (
                "Draw one scatter plot that presents the relationship between the crime rate and house prices, "
                "and label key boroughs.",
                {},
            ),
        ]
    )
    numbered(
        [
            ("Write the commentary and planned checks: ", {"bold": True}),
            (
                "Write the figure commentary, stating association rather than causation; if the project continues, "
                "a brief robustness check may be added.",
                {},
            ),
        ]
    )
    p = para()
    add_runs(
        p,
        [
            ("Deliverables: ", {"bold": True}),
            ("this proposal, three source CSV files, one research figure, and a Python 3 notebook.", {}),
        ],
    )
    p = para()
    add_runs(
        p,
        [
            ("Guidelines followed: ", {"bold": True}),
            ("CISC7204 Project Proposal Ideation; CISC7204 Project Proposal Guideline.", {}),
        ],
    )

    heading("Criteria for Success")
    para("A completed proposal / small-scale analysis should:")
    bullet("Name both the region and the domain in the same research question")
    bullet("Provide at least two working public-data links, not local files alone")
    bullet("Include one figure whose axes correspond to the research question")
    bullet("Report a numerical association next to the figure (here Spearman’s ρ and n)")
    bullet("State clearly that the result is observational and that no causal inference is made")
    bullet("Be reproducible with Python 3 notebooks")
    bullet(
        [
            ("Form of presentation: ", {"bold": True}),
            (
                "This proposal uses a checklist as the success criterion, together with a final visual "
                "(figures/crime_vs_house_price.png), to help the reader follow the process from data collection "
                "and analysis through to interpretation.",
                {},
            ),
        ]
    )
    bullet(
        [
            ("Success is not high predictive accuracy. ", {"bold": True}),
            (
                "Success means a reader can see whether public data for London’s boroughs support the claim "
                "“more crime, cheaper housing,” and can understand why the answer is no.",
                {},
            ),
        ]
    )

    heading("Collaboration")
    para("This proposal is an individual project.")

    doc.save(OUT)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
