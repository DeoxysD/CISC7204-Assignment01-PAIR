#!/usr/bin/env python3
"""Build the Chinese Word proposal."""
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures" / "crime_vs_house_price.png"
OUT = ROOT / "CISC7204-Assgn01-mc63582-PreliminaryProjectProposal-zh.docx"
CN = "Songti SC"
EN = "Calibri"


def set_run_font(run, size=11, bold=False, italic=False, name=EN):
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.name = name
    r = run._element.get_or_add_rPr()
    rFonts = r.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        r.append(rFonts)
    rFonts.set(qn("w:ascii"), EN)
    rFonts.set(qn("w:hAnsi"), EN)
    rFonts.set(qn("w:eastAsia"), CN)


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
    rFonts.set(qn("w:ascii"), EN)
    rFonts.set(qn("w:hAnsi"), EN)
    rFonts.set(qn("w:eastAsia"), CN)
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
    cover_line("澳门大学", size=16, bold=True, after=6)
    cover_line("科技学院", size=13, after=28)
    cover_line("作业一：初步项目提案", size=18, bold=True, after=8)
    cover_line("伦敦各区的犯罪与房价", size=14, italic=True, after=28)

    cover_fields = [
        ("学号", "mc63582"),
        ("姓名", "FANZIQIAN"),
        ("课程代码", "CISC7204"),
        ("课程名称", "Data Science and Data Visualization"),
        ("作业名称", "Assignment 01 – Preliminary Project Proposal"),
    ]
    for lab, val in cover_fields:
        p = para(after=8)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_runs(p, [(f"{lab}：", {"bold": True, "size": 12}), (val, {"size": 12})])

    doc.add_page_break()

    heading("项目标题")
    p = para()
    add_runs(p, [("伦敦各区的犯罪与房价", {"bold": True})])
    p = para()
    add_runs(
        p,
        [
            ("研究问题：", {"bold": True}),
            ("在英国伦敦，立案犯罪更多的行政区，平均房价是否更低？", {}),
        ],
    )
    para(
        "这是一道常识题（人们通常认为犯罪会压低房价）。本提案检验行政区尺度的公开数据表是否真的支持这一说法。"
    )

    heading("地区与领域")
    bullet(
        [
            ("地区：", {"bold": True}),
            (
                "英国伦敦（32 个伦敦行政区；因 2016–2018 年犯罪或人口记录不完整，未纳入伦敦城 City of London）。",
                {},
            ),
        ]
    )
    bullet(
        [
            ("领域类别：", {"bold": True}),
            ("住房与城市安全（房价、立案犯罪、居民收入）。", {}),
        ]
    )

    heading("数据集（至少两个公开链接）")
    p = numbered(
        [
            ("Housing in London（Kaggle）", {"bold": True}),
            (
                "——两份可下载 CSV（月度房价、成交量与立案犯罪；年度工资、人口与住房套数）：",
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
                "各行政区平均房价（伦敦数据商店 / 大伦敦政府，来源为英国土地登记处成交价）",
                {"bold": True},
            ),
            ("——官方行政区房价表：", {}),
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
        [("Kaggle 数据包还引用了伦敦数据商店上的大都会警察局立案犯罪汇总：", {})],
    )
    add_hyperlink(
        p,
        "https://data.london.gov.uk/dataset/mps-recorded-crime-geographic-breakdown-exy3m/",
        "https://data.london.gov.uk/dataset/mps-recorded-crime-geographic-breakdown-exy3m/",
    )

    para("本提案使用的本地副本：")
    for fname in ["data/housing_in_london_monthly.csv", "data/housing_in_london_yearly.csv"]:
        bullet([(fname, {"italic": True})])

    heading("可视化及说明")
    para(
        "图。伦敦各区：犯罪更高并不对应更便宜的住房。",
        size=10,
        italic=True,
        after=6,
    )
    pic = doc.add_paragraph()
    pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pic.paragraph_format.space_after = Pt(10)
    pic.add_run().add_picture(str(FIG), width=Inches(6.3))

    para(
        "图中是 32 个伦敦行政区的散点。横轴为每千名居民立案犯罪数，纵轴为平均房价，二者均为 2016–2018 年均值，"
        "以免被单一年份噪声带偏。点的颜色来自年度表中的居民工资中位数。最小二乘直线只作读图辅助，不是因果模型。"
    )

    p = para()
    add_runs(
        p,
        [
            (
                "这张图用来回答上述研究问题，而不是预测房价。若常识成立，高房价行政区应落在右下方（高犯罪、低房价），"
                "或至少呈现向下的斜率。实际并非如此。犯罪率与房价的 Spearman 等级相关为 ",
                {},
            ),
            ("ρ = 0.47（p ≈ 0.007）", {"bold": True}),
            (
                "：人均立案更多的行政区，房价往往更高。Westminster、Kensington and Chelsea 既贵、人均立案也高；"
                "Bexley 等外围行政区更便宜，人均立案也更少。工资与这两个变量都同向升高，因此格局更接近「中心、高收入地区"
                "既有高房价，也有更多立案」，而不是「犯罪让住房变便宜」。图",
                {},
            ),
            ("并不", {"italic": True}),
            (
                "表明犯罪导致高房价，只表明这些表里不存在「犯罪高则房价低」的简单负向关系。",
                {},
            ),
        ],
    )

    heading("项目目的")
    heading("成果", 2)
    para(
        "本项目把课程中的统计探究接到一个真实的公开数据问题上：先取人们已有的信念，再为明确地点找到两张相关的"
        "政府来源表，清洗并拼接，然后判断数字是否支持该信念。这比刷 Kaggle 排行榜更接近日后的实证工作"
        "（政策简报、城市分析、应用统计）。"
    )
    heading("技能", 2)
    for s in [
        "查找并引用公开表格数据（CSV / 开放数据门户）",
        "按行政区与年份拼接月度表与年度表",
        "处理犯罪月份缺失，并构造按人口调整的犯罪率",
        "等级相关，以及非建模者也能读懂的散点图",
        "写与证据匹配的论断（相关，而非因果）",
    ]:
        bullet(s)
    heading("知识", 2)
    for s in [
        "犯罪次数与犯罪率的差别",
        "截断坐标或过度堆叠为何会误导，以及轴、样本量、对照变量（工资）为何应出现在图上",
        "生态学谬误：行政区平均值不是住户层面的效应",
    ]:
        bullet(s)

    heading("项目任务")
    for s in [
        "写明地区、领域，以及可用是否回答的统计问题（本文）。",
        "下载月度与年度 CSV，并保留原始网址。",
        "只保留 borough_flag = 1。将月度房价取均值、犯罪取合计，汇总到日历年。再拼接年度 population_size 与 median_salary。",
        "限定犯罪月份较完整的年份（2016–2018），并在行政区内再取平均。",
        "计算犯罪率与房价的 Spearman ρ（并以工资与房价的相关作对照）。",
        "绘制散点图，并在 notebooks/01_eda.ipynb 中复现。",
        "撰写上面 1–2 段图注说明；若项目继续，再做简要稳健性检查（去掉 Westminster；改用犯罪次数而非犯罪率）。",
    ]:
        numbered(s)
    p = para()
    add_runs(
        p,
        [
            ("交付物：", {"bold": True}),
            ("本提案、两份源 CSV、一张研究图、一份 Python 3 notebook。", {}),
        ],
    )
    p = para()
    add_runs(
        p,
        [
            ("依据指南：", {"bold": True}),
            ("CISC7204 Project Proposal Ideation；CISC7204 Project Proposal Guideline。", {}),
        ],
    )

    heading("成功标准")
    para("一份完成的提案 / 小型分析应当：")
    for s in [
        "在同一句研究问题中点明地区与领域",
        "提供至少两个可打开的公开数据链接，而不仅是本地文件",
        "给出一张坐标轴对应研究问题中那些量的图",
        "在图旁报告数值关联（此处为 Spearman ρ 与 n）",
        "明确说明结果是观察性的",
        "可用 Python 3 从 notebooks/01_eda.ipynb 复现",
    ]:
        bullet(s)
    p = para()
    add_runs(
        p,
        [
            ("成功不是很高的预测 AUC。", {"italic": True}),
            (
                "成功是：读者能看出伦敦各区的公开表是否支持「犯罪更多、住房更便宜」，以及为什么答案是否定的。",
                {},
            ),
        ],
    )

    heading("协作")
    p = para()
    add_runs(
        p,
        [
            ("本提案按", {}),
            ("个人", {"bold": True}),
            ("项目准备。若课程后续要求组队，拟定分工如下：", {}),
        ],
    )

    table = doc.add_table(rows=5, cols=2)
    table.style = "Table Grid"
    rows = [
        ("角色", "职责"),
        ("项目协调人", "问题、时间表、论断的最终措辞"),
        ("文书", "提案正文与图注"),
        ("进度跟踪", "notebook 可复现性与上面的清单"),
        ("对外联络", "数据引用，以及与教师的后续沟通"),
    ]
    for i, (a, b) in enumerate(rows):
        table.rows[i].cells[0].text = a
        table.rows[i].cells[1].text = b
        for cell in table.rows[i].cells:
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(2)
                for run in paragraph.runs:
                    set_run_font(run, size=10, bold=(i == 0))
    for cell in table.rows[0].cells:
        tcPr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:fill"), "E7E6E6")
        shd.set(qn("w:val"), "clear")
        tcPr.append(shd)

    para("")
    para(
        "组队守则：不得悄悄覆盖提案正文；文中每个数字都必须能从 notebook 重新跑出；"
        "不得用 Kaggle kernel 替代引用伦敦数据商店的原始来源。"
    )

    doc.save(OUT)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
