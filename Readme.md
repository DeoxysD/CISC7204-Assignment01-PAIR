# PAIR 课程：数据处理流程总结

这门课（IBM Data Analysis with Python / CISC7204–CISC3015）用 **12 个 notebook** 走完同一套分析流水线。  
核心不是“换数据集”，而是反复练习：**读入 → 清洗 → 探索 → 建模 → 评估**。

---

## 1. 整体结构

课程有两条平行实验线，步骤几乎一一对应：

| 模块 | 主题 | 二手车定价 | 笔记本定价 |
|------|------|------------|------------|
| 01 | 导入数据集 | `Lab01 Importing Data Sets - Used Car Pricing` | `Lab02 Importing Data Sets - Laptop Pricing` |
| 02 | 数据清洗（Wrangling） | `Lab01 Data Wrangling - Used Car Pricing` | `Lab02 Data Wrangling - Laptop Pricing` |
| 03 | 探索性分析（EDA） | `Lab01 EDA - Used Car Pricing` | `Lab02 EDA - Laptop Pricing` |
| 04 | 模型开发 | `Lab01 Model Development - Used Car Pricing` | `Lab02 Model Development - Laptop Pricing` |
| 05 | 模型评估与改进 | `Lab01 Model Evaluation - Used Car Pricing` | `Lab02 Model Evaluation - Laptop Pricing` |

Module 06 把 01–05 **压缩进一个 notebook**，换新数据独立做一遍：

- 练习项目：医疗保险费用 `Insurance Cost`
- 期末项目：King County 房价 `House Pricing Cost`

目标变量始终是价格类连续值：`price` / `Price` / `charges`。

---

## 2. 一条通用流水线

所有 notebook 都按下面这条链走。前三段是“数据处理”，后两段是建模。

```
原始 CSV
  │
  ├─ 1. 导入：读表、加列名、看 head/tail/dtype/describe/info
  │
  ├─ 2. 清洗：? → NaN → 填缺失 / 删行 → 改类型 → 单位换算
  │         → 归一化 → 分箱 → 类别转 dummy
  │
  ├─ 3. EDA：相关、回归散点图、箱线图、分组均值、透视表、Pearson + p 值
  │         （选出真正能预测价格的特征）
  │
  ├─ 4. 建模：简单线性 → 多元线性 → 多项式 → Pipeline
  │
  └─ 5. 评估：train/test 划分 → 交叉验证 → Ridge → GridSearch
```

---

## 3. Module 01：导入数据集

**目的：** 把网上的 CSV 变成可用的 DataFrame，先看清“长什么样”，还不做深度清洗。

共同步骤：

1. `pd.read_csv(...)`  
   - 二手车 `auto.csv`、笔记本 `laptops.csv`、保险费用：**没有表头**，必须 `header=None`。  
   - 房价 `housing.csv`、以及 Module 03 之后的清洗成品：**第一行就是列名**，用默认 `header=0`。
2. 手动赋列名（无表头时）。
3. 把原始缺失标记 `"?"` 换成 `np.nan`。
4. 用 `head()` / `tail()` / `dtypes` / `describe()` / `info()` 做第一轮体检。

数据集差异：

| 数据集 | 规模与列 | 目标列 | 导入时特别注意 |
|--------|----------|--------|----------------|
| 二手车 | 约 205 行 × 26 列（symboling … price） | `price` | 无表头；价格缺失的行在导入阶段就会删掉（约剩 201 行） |
| 笔记本 | 238 行 × 12 列（Manufacturer … Price） | `Price` | 无表头；`Screen_Size_inch`、`Weight_kg` 里有 `"?"`，类型常是 object |
| 保险费用 | 2772 行 × 7 列 | `charges` | 无表头；`age`、`smoker` 有 `"?"` |
| 房价 | King County 成交数据（自带表头） | `price` | **不要** `header=None`；`bedrooms` / `bathrooms` 有缺失 |

---

## 4. Module 02：数据清洗（真正的数据处理）

这是整门课数据处理的核心。套路固定为六步。

### 4.1 识别并处理缺失值

| 变量类型 | 做法 | 例子 |
|----------|------|------|
| 连续数值 | 用该列**均值**填 | 车：`normalized-losses`, `bore`, `stroke`, `horsepower`, `peak-rpm`；笔记本：`Weight_kg`；房价：`bedrooms`, `bathrooms`；保险：`age` |
| 类别 | 用**众数**填 | 车：`num-of-doors`（多为 `"four"`）；笔记本：`Screen_Size_cm`；保险：`smoker` |
| 目标变量 | **整行删除**，不用均值填 | 二手车 `price` 缺失则 `dropna`，再 `reset_index` |

原则：预测目标不能“编造”；特征可以填，以免丢掉整行其它信息。

### 4.2 修正数据类型

`"?"` 会把数值列读成 `object`。填完缺失后 `astype(float)` / `astype(int)`，后面才能算均值、相关、回归。

### 4.3 标准化（单位统一，不是 sklearn 的 StandardScaler）

课程里的 *Standardization* 指**换成常用单位**：

- 二手车：油耗 `mpg` → `L/100km`（公式 `235 / mpg`），列名改为 `city-L/100km`、`highway-L/100km`
- 笔记本：重量 kg → 磅（× 2.205）；屏幕 cm → 英寸（÷ 2.54）

### 4.4 归一化（把量纲压到同一尺度）

简单最大值归一化：`值 / 该列最大值`，结果落在 `(0, 1]`。

- 二手车：`length` / `width` / `height`
- 笔记本：`CPU_frequency`

（建模阶段的 `StandardScaler` 是另一套：减均值除标准差，出现在 Module 04/05 的 Pipeline 里。）

### 4.5 分箱（Binning）

把连续变量切成有序档位，便于看分布、也可当类别特征：

- 二手车：`horsepower` → Low / Medium / High（直方图 3 箱）
- 笔记本：`Price` 用 `linspace` 均分成 Low / Medium / High，再画柱状图

### 4.6 指示变量（Dummy / One-hot）

类别文字列转 0/1，才能进线性回归：

- 二手车：`fuel-type`（gas/diesel）、`aspiration`（std/turbo）
- 笔记本：`Screen`（IPS Panel / Full HD）

做法：`pd.get_dummies(..., dtype=int)` → 改列名 → `concat` 拼回原表 → `drop` 原文字列。

清洗完成后，二手车线会把结果存成 `clean_df.csv`，供后续模块使用。

---

## 5. Module 03：探索性数据分析（为建模选特征）

清洗之后不再改表结构，而是回答：**哪些变量真的和价格有关？**

| 手段 | 用在什么上 | 结论怎么用 |
|------|------------|------------|
| `corr()` 相关矩阵 | 数值列 vs 价格 | 绝对值接近 1 → 线性关系强 |
| `regplot` 回归散点图 | 连续特征 | 拟合线斜、点不散 → 适合当预测变量 |
| `boxplot` 箱线图 | 类别特征 | 各组箱子分开 → 该类别能区分价格 |
| `groupby` + 透视表 + 热力图 | 两个类别的组合 | 看交互（如 GPU × CPU 核数） |
| Pearson 系数 + p 值 | 每个特征 vs 价格 | 系数看强弱，p < 0.05 看是否显著 |

各数据集里通常“有用”的信号：

- **二手车：** `engine-size`、`curb-weight`、`horsepower` 与价格强正相关；`highway-mpg` 负相关；`stroke` 几乎无关。`drive-wheels`、`body-style` 分组后平均价格差明显。
- **笔记本：** `RAM_GB`、`CPU_core`、`Storage_GB_SSD` 等配置档位区分价格更明显；屏幕尺寸、重量往往很弱。
- **保险：** `smoker` 与保费相关最强（约 0.79），其次 `age`；`bmi` 较弱。
- **房价：** 与 `price` 相关最强的通常是 `sqft_living`，其次 `grade`、`sqft_above`；海景 `waterfront` 的箱线图中位价更高。

EDA 的产出就是后面模型用的特征名单，不是另一套清洗。

---

## 6. Module 04–05：建模与评估（数据处理的延伸）

这两步不再改原始表，但会再做一层**面向模型的变换**。

**建模（04）**

1. 简单线性回归：单特征（如 `engine-size` → `price`，`CPU_frequency` → `Price`，`smoker` → `charges`）
2. 多元线性回归：EDA 选出的多个特征一起拟合
3. 多项式：捕捉弯曲关系（阶数过高会过拟合）
4. `Pipeline`：`StandardScaler` → `PolynomialFeatures` → `LinearRegression` 串成一条链

指标：样本内 **R²**（越高越好）和 **MSE**（越低越好）。此时还在用全部数据打分，分数偏乐观。

**评估（05）**

1. `train_test_split` 留出测试集（常见 10% / 15% / 20% / 40%）
2. 交叉验证（如 `cv=4`）看分数稳不稳
3. 故意升高多项式阶数，观察测试 R² 下降 → 过拟合
4. Ridge（L2 惩罚）压系数；`GridSearchCV` 搜 `alpha`
5. 多项式变换：**只在训练集 `fit_transform`，测试集只能 `transform`**，避免泄漏

---

## 7. Module 06：把整条链压缩到一个文件

练习项目和期末项目不再分 5 个 lab，而是在同一个 notebook 里按 Module 1–5 的标题把上面流程再跑一遍。

**保险费用（练习）**

1. 无表头 CSV → 7 列命名  
2. `"?"` → NaN；`smoker` 众数填，`age` 均值填；类型改回 int；保费保留两位小数  
3. EDA：bmi 回归图、吸烟箱线图、相关矩阵  
4. 单变量（smoker）→ 全特征多元 → 标准化+2 阶多项式 Pipeline  
5. 20% 测试集 → Ridge(α=0.1) → 多项式 + Ridge  

**King County 房价（期末）**

1. 自带表头，直接读入；看 dtypes、`describe`  
2. 删掉无用列 `id`、`Unnamed: 0`；`bedrooms` / `bathrooms` 用均值填  
3. 楼层 `value_counts`、海景箱线图、`sqft_above` 回归图、数值相关  
4. `sqft_living` 简单回归 → 指定 11 特征多元回归 → 标准化+多项式 Pipeline  
5. 15% 测试集 → Ridge → 2 阶多项式 + Ridge  

房价那 11 个特征是题目给定的：  
`floors, waterfront, lat, bedrooms, sqft_basement, view, bathrooms, sqft_living15, sqft_above, grade, sqft_living`。

---

## 8. 读表时容易踩的坑（贯穿所有 notebook）

1. **有没有表头要看文件本身**  
   `auto.csv` / 原始 `laptops.csv` / 保险费用：`header=None` + 手动列名。  
   清洗后的 csv、房价数据：`header=0`。弄反会把第一行数据当成列名，或把列名当成数据。

2. **Pandas 3 的 Copy-on-Write**  
   `df["列"].replace(..., inplace=True)` 往往改不到原表。正确写法是赋回：  
   `df["列"] = df["列"].replace(...)`。

3. **缺失策略不要混用**  
   特征用均值/众数填；目标列（价格）缺失才删行。不要对已经填过的列再 `dropna`，否则会白白丢掉很多样本。

4. **Dummy 要指定 `dtype=int`**  
   新版 pandas 默认给出 True/False，实验期望 0/1。

---

## 9. 一句话记住

> 先把脏 CSV 变成类型正确、单位统一、无缺失、类别已编码的表；  
> 再用图和相关选出真正驱动价格的特征；  
> 最后才拟合模型，并用测试集/交叉验证检查有没有过拟合。

两条实验线（车 / 笔记本）和 Module 06 的两个项目，都是这条流程的重复练习。
