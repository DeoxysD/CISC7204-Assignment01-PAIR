# CISC7204 — Crime and House Prices in London Boroughs

课堂 proposal 用的小项目，不是 Kaggle 竞赛刷榜。

**问题：** In London, United Kingdom, do boroughs with higher recorded crime have lower average house prices?

**结论（描述性）：** 2016–2018 年 32 个 borough 上，犯罪率与均价的 Spearman ρ = **0.47**（p ≈ 0.007），方向与「犯罪高则房价低」相反。

## 交作业时主要用这些

| 文件 | 用途 |
|---|---|
| **`CISC7204-Assgn01-mc63582-PreliminaryProjectProposal.docx`** | **英文 Word（课程提交）** |
| **`CISC7204-Assgn01-mc63582-PreliminaryProjectProposal-zh.docx`** | **中文 Word** |
| `PROPOSAL.md` | 英文 Markdown 底稿 |
| `PROPOSAL_zh.md` | 中文 Markdown 底稿 |
| `figures/crime_vs_house_price.png` | 可选上传的图 |
| `notebooks/01_eda.ipynb` | 可选的 Python 3 notebook |
| `data/housing_in_london_monthly.csv` | 月度房价 / 成交 / 犯罪 |
| `data/housing_in_london_yearly.csv` | 年度工资 / 人口 |

## 运行 notebook

```bash
# conda env mew, 或任何有 pandas / matplotlib / scipy 的 Python 3
jupyter notebook notebooks/01_eda.ipynb
```

数据链接见 `PROPOSAL.md`。
