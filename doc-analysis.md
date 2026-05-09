# CatSim 文档分析报告

> 分析对象：`User manual-EN.doc` 与 `Modelling Technical Manual-EN-Mark.doc`  
> 分析日期：2026-05-09  
> 说明：两个源文件均为 Microsoft Word 旧版二进制 `.doc`（OLE Compound File）格式。本报告基于从 Word 文本流中提取出的正文、目录、标题层级、公式片段与表格文字进行分析；嵌入的 Visio 图、Excel 对象、公式对象和图片未做视觉/OCR 级别解析。

## 1. 总体结论

这两个文档共同描述了 **CatSim v4**，一个面向 FCC（Fluid Catalytic Cracking，流化催化裂化）装置的 Excel/模型系统：

- `User manual-EN.doc` 是**用户操作手册**，目标读者是模型使用者、工艺工程师和需要通过 Excel 界面完成安装、校准、预测、故障排查的人员。它强调“如何使用 CatSim”。
- `Modelling Technical Manual-EN-Mark.doc` 是**建模技术手册**，目标读者是模型维护者、算法开发者、模型验证人员或需要理解公式逻辑的高级用户。它强调“CatSim 如何计算”。
- 两个文档内容高度互补：用户手册第 3 章和附录 A 对技术原理做概要说明，而技术手册将这些模块展开为更完整的变量、常数、计算步骤和经验关联式。
- 从内容看，CatSim v4 的核心能力包括：热平衡、标准收率预测、工厂产品收率与分馏预测、产品性质预测、循环物流预测、催化剂管理、元素/物料衡算、蒸馏曲线转换以及物性换算。
- 文档年代较早：用户手册标注最后修改日期为 **2003-12-10**，其中包含 Windows/Excel、许可证管理、共享服务器路径、BP/UOP 帮助台等历史部署信息。若用于现代化维护，应优先校验安装、授权、依赖组件和组织路径是否仍然有效。

## 2. 源文档概览

| 文件 | 文档定位 | 主要内容 | 适合读者 | 分析重点 |
|---|---|---|---|---|
| `User manual-EN.doc` | CatSim v4 用户手册 | 安装授权、快速开始、界面说明、校准/预测流程、故障排查、技术附录 | 一线模型用户、工艺工程师、支持人员 | 工作流、界面、使用方式、常见问题 |
| `Modelling Technical Manual-EN-Mark.doc` | FCC/CatSim 建模技术手册 | 热平衡、反应器与再生器计算、标准收率、分馏、性质预测、循环、催化剂、物性与蒸馏换算 | 模型开发/维护人员、验证人员、高级工程师 | 公式、模块边界、输入输出、算法依赖 |

## 3. 两份文档的关系

### 3.1 主题上的对应关系

| 用户手册主题 | 技术手册对应模块 | 关系说明 |
|---|---|---|
| Operational Modes：Calibrate / Predict | Base Case / Predict Case 各类计算 | 用户手册解释两种运行模式，技术手册给出基础工况与预测工况的公式实现。 |
| Heat Balance Module | Heat Balance | 用户手册说明热平衡在系统中的作用，技术手册细化为单级/两级再生器、反应器、WHSV、预热等计算。 |
| Reactor Yield and Product Quality Modules | Prediction of Standard Yields、Product Quality Prediction | 用户手册说明模块功能，技术手册给出标准收率、产品性质、单元因子等计算逻辑。 |
| TLP prediction and Fractionation Module | Fractionation & Prediction of Plant Yields | 用户手册描述 TLP 与分馏模块，技术手册展开 TLP 曲线、完美/非完美分馏、有效切割点与产品收率。 |
| Feed Characterisation | Physical Property / Distillation Conversion | 用户手册强调输入 feed 性质，技术手册提供蒸馏曲线转换、特征沸点和物性换算。 |
| Catalyst Management | Catalyst Management Calculations、CatCalc Add-in | 用户手册介绍催化剂活性、金属、选择性等输入/校准概念，技术手册进一步描述催化剂管理和 CatCalc 插件。 |
| Troubleshooting | 技术公式与模块约束 | 用户手册列出使用错误、打开文件、Predict 不等于 Base、金属/活性输入、Excel 崩溃等问题；技术手册可用于追溯根因。 |

### 3.2 内容重叠与差异

- **重叠部分**：用户手册附录 A 的技术议题与技术手册主体章节基本一致，例如热平衡、标准收率、分馏、产品质量、循环、催化剂、元素衡算、蒸馏转换和物性换算。
- **差异部分**：
  - 用户手册更关注操作顺序、Excel sheet、输入单元格/颜色、用户格式、校准与预测按钮、故障处理。
  - 技术手册更关注公式、变量名、常数、条件分支、计算顺序、经验关联式和插件算法。
- **建议用法**：培训新用户时先读用户手册；调试模型、迁移代码、验证结果或重构算法时，以技术手册为主，并用用户手册核对界面行为。

## 4. `User manual-EN.doc` 分析

### 4.1 文档定位

该文档标题为 **CatSim v4 User Manual**，发布主体为 UOP LLC，最后修改日期为 **2003-12-10**。它面向 CatSim 的日常使用，重点是帮助用户完成：

1. 了解 CatSim 的基本建模思想；
2. 安装与授权；
3. 打开 Excel 模型并进行快速校准/预测；
4. 理解主要 worksheet 的作用；
5. 处理测试运行数据、校准模型、执行预测和使用 Feed Blender；
6. 排查常见错误。

### 4.2 主要章节结构

用户手册包含以下主线：

1. **Introduction**
   - 介绍 CatSim 的背景、用途和 v4 变化。
   - 模型以 feed properties、catalyst properties、FCC operating variables 为输入，预测稳态收率、产品性质和依赖操作条件。
   - 明确 CatSim 有两个核心模式：**Calibrate** 与 **Predict**。

2. **Installation and Licensing**
   - 描述授权申请、安装前依赖处理、安装文件位置、License Manager、启动模型和 `xldiscon` 等内容。
   - 该部分强依赖 2003 年左右的 IT 环境和组织流程，现代复用时需要重点复核。

3. **Catsim: Getting Started**
   - 概述 CatSim 软件组成与快速开始流程。
   - 指导用户打开模型、进行校准、运行预测。

4. **Technical Basis and Structure**
   - 从用户视角解释模型模块：热平衡、收率、产品性质、TLP/分馏、feed 表征、设计参数、循环、催化剂管理、汽油 PIANO、湿气计算、迭代循环。

5. **Spreadsheet Navigation**
   - 解释固定格式和用户格式。
   - 说明主要 sheet：Unit Monitoring、CatSim、Gasoline Composition、Property Distributions、Feed Blender、Step Out、Forward Predict。

6. **Calculation Options / How to Use CatSim**
   - 描述测试运行数据处理、校准、预测、Feed Blender 等关键操作。

7. **Troubleshooting**
   - 覆盖错误/警告、打开 spreadsheet 问题、Predict 与 Base 不一致、金属/活性输入问题、Excel 崩溃。

8. **Technical Appendices**
   - 附录 A 汇总更多技术议题。
   - 附录 B 讨论关键参数变化时的模型响应。

### 4.3 关键概念

#### Calibrate / Predict 双模式

- **Calibrate**：以已知装置数据 `(x, y)` 为基础工况，调整模型参数或单元因子，使模型贴合特定装置。
- **Predict**：沿用校准得到的参数，对 feed、催化剂、操作变量或设计参数变化后的新工况进行预测。
- 这种设计说明 CatSim 不是纯机理模型，而是机理、经验关联式和装置校准因子的组合。

#### Excel 界面作为核心交互层

用户手册大量篇幅围绕 spreadsheet 使用展开，说明 CatSim v4 很大程度上是通过 Excel workbook 暴露输入、输出、按钮和插件功能的。其优势是便于工程师操作；风险是依赖 Excel 版本、宏、安全设置、外部加载项和历史路径。

#### 模型应用场景

用户手册提到的典型应用包括：

- 工艺监控；
- 日常优化；
- 长期优化，例如 feed selection、催化剂 reformulation；
- de-bottlenecking study；
- 设计参数变化评估；
- 装置改造研究；
- FCC LP representation 生成。

### 4.4 用户手册中的风险点

- **年代和环境依赖**：安装、API Databook、BP help desk、UOP/BP shared server 等内容可能已失效。
- **Excel 依赖**：Excel 崩溃、旧 API Databook 不兼容、模型打开失败等问题提示系统稳定性高度依赖桌面环境。
- **输入质量敏感**：测试运行数据、金属/活性、feed 表征、产品切割点等输入会影响校准质量和预测可靠性。
- **Predict 与 Base 不一致**：用户手册专门列出该问题，表明模型中存在迭代、单位、输入完整性或校准状态导致的复现风险。

## 5. `Modelling Technical Manual-EN-Mark.doc` 分析

### 5.1 文档定位

该文档标题为 **FCC Technical Manual**，是对 CatSim/FCC 模型计算逻辑的技术展开。它以工程计算模块为主线，给出大量变量、常数、单位、公式与条件分支。

它适合用于：

- 将旧 Excel/宏模型迁移到现代代码；
- 对模型输出做回归测试和公式核对；
- 解释 CatSim 输出结果的来源；
- 审计经验关联式、常数和单位；
- 训练高级用户理解模型边界。

### 5.2 主要章节结构

技术手册包括以下核心模块：

1. **Calculation Flow Diagrams**
   - 包含 Calibration 与 Predict 流程图，但原始文档中为嵌入 Visio 对象，本次文本分析仅识别到对象占位。

2. **Heat Balance**
   - 单级再生器基础工况热平衡；
   - 两级再生器基础工况热平衡；
   - 反应器热平衡；
   - WHSV 计算；
   - 预测工况下单级/两级再生器热平衡；
   - feed preheat calculation。

3. **Prediction of Standard Yields**
   - 从 plant data 计算标准收率；
   - 标准收率预测；
   - 当前催化剂因子；
   - Yield Unit Factors。

4. **Fractionation & Prediction of Plant Yields**
   - 构造 TLP 曲线；
   - 完美分馏与非完美分馏；
   - Fractionation indices 与 effective cut points；
   - 产品收率预测；
   - 文档中还出现一行中文注释，说明某些 TLP 点按顺序计算。

5. **Product Quality Prediction**
   - 标准产品质量预测；
   - 工厂产品性质预测；
   - 覆盖 specific gravity、sulphur、LCO cloud/pour point、cetane index、gasoline RVP/RON/MON、viscosity、concarbon、basic nitrogen、molecular weight curve、gasoline composition 等。

6. **Product Recycle Prediction**
   - 描述循环物流预测及相关校准逻辑。

7. **Catalyst Management Calculations**
   - 涉及催化剂活性、金属、选择性、平衡催化剂/新鲜催化剂等影响。

8. **Elemental Balances**
   - 至少包含 sulphur balance 与 hydrogen balance。

9. **Cubic Spline Functions**
   - 用于曲线插值/平滑，支撑 TLP、蒸馏曲线或性质分布相关计算。

10. **Distillation Conversion Methods**
    - D1160、TBP、D86、Simdis(D2887) 之间的转换；
    - 压力换算；
    - D1160 @ 760 mmHg 到 D86/Simdis 的换算。

11. **Physical Property Calculations and Conversions**
    - 生成特征沸点；
    - CA 计算；
    - MAT 与 RMA 换算；
    - Conradson Carbon 与 Ramsbottom carbon 换算；
    - MeABP、VABP、ABP 换算。

12. **Appendices**
    - Quench Add-in；
    - CatCalc Add-in；
    - Model Input/Output；
    - Molecular Weight Constants。

### 5.3 热平衡模块分析

热平衡是技术手册中最庞大的模块。其关键特点包括：

- 同时支持 **single stage regenerator** 与 **two stage regenerator**。
- 基础工况中，根据用户输入可以选择：
  - 已知 air rate 与 flue gas analysis，计算 coke yield；
  - 已知 coke yield 与 flue gas analysis，计算 air rate；
  - 已知 coke make、burn ratio 与 coke composition，计算再生相关量。
- 预测工况下，支持用 coke make、air rate、flue gas composition 或 burn ratio/coke composition 等不同输入组合求解。
- 计算中显式使用：空气组成、O₂ 富集、flue gas CO/CO₂/O₂、torch oil、coke H/S、催化剂冷却器、反应器温度、再生床温度、热损失、coke desorption heat 等变量。
- 反应器热平衡和 WHSV 计算与 feed vaporization、steam/lift gas、catalyst circulation、反应热、riser outlet temperature 等强相关。

该模块体现出 CatSim 的工程属性：它不是只预测收率，还要闭合操作条件和能量约束。

### 5.4 收率、分馏与产品性质模块分析

#### 标准收率

技术手册将 plant data 转换为标准收率，例如：

- C5 and lighter；
- C5-221°C gasoline；
- 221-350°C LCO；
- 350°C+ DCO；
- coke。

这些标准收率再结合经验关联式、催化剂因子和 unit factors 进行预测。

#### TLP 与分馏

TLP（Total Liquid Product）曲线是从标准收率走向实际产品切割的桥梁。技术手册区分：

- **Perfect Fractionation**：理想切割；
- **Imperfect Fractionation**：考虑实际分馏夹带、重叠、fractionation indices、effective cut points；
- 产品 distillation quality calibration；
- plant yield prediction。

#### 产品性质

产品性质预测覆盖范围较广，既包括标准产品，也包括工厂实际产品：

- 比重/API；
- 硫含量；
- LCO cloud point / pour point / cetane index；
- gasoline RVP、RON、MON；
- 粘度；
- concarbon；
- basic nitrogen；
- 分子量曲线；
- gasoline PIANO/composition。

这表明 CatSim 输出不只是质量收率，还面向炼厂优化需要的产品规格和性质指标。

### 5.5 插件与附录分析

#### Quench Add-in

Quench Add-in 关注 post-riser/quench 技术对产物分布和反应的影响，包含 quench 相关反应/转化估计公式。它更像是 CatSim 主模型之外的专项扩展。

#### CatCalc Add-in

CatCalc Add-in 关注催化剂 formulation、reformulation、新技术或实验室数据驱动的模拟。它将催化剂性质、实验室或供应商数据与 CatSim 参数相联系，是催化剂方案评估的重要辅助模块。

#### Model Input/Output 与 Molecular Weight Constants

这两个附录对模型迁移和验证非常重要：

- Model Input/Output 可作为接口契约或回归测试字段清单的基础；
- Molecular Weight Constants 可用于统一常数，避免不同实现中分子量不一致导致结果偏差。

## 6. 模型模块架构抽象

可以将 CatSim 抽象为以下数据流：

```text
Feed / Catalyst / Operating Conditions / Design Parameters
        │
        ├─► Heat Balance
        │      ├─ Regenerator calculations
        │      ├─ Reactor calculations
        │      └─ WHSV / preheat / catalyst circulation
        │
        ├─► Standard Yield Prediction
        │      ├─ Calibration factors
        │      └─ Catalyst / feed / severity effects
        │
        ├─► TLP & Fractionation
        │      ├─ TLP curve construction
        │      ├─ Perfect / imperfect fractionation
        │      └─ Plant stream yields
        │
        ├─► Product Quality Prediction
        │      ├─ Standard product properties
        │      └─ Plant product properties
        │
        ├─► Recycle / Catalyst Management
        │
        └─► Material, Sulphur, Hydrogen Balances
               │
               └─► Final yields, qualities, operating outputs, warnings
```

## 7. 适合后续工程化提取的要点

如果仓库后续需要把文档内容转化为可维护代码或结构化知识库，建议按以下优先级推进：

1. **先做文本与公式基线**
   - 保存 `.doc` 原文；
   - 提取纯文本；
   - 将公式按章节编号整理；
   - 对变量、单位、常数建立表格。

2. **建立模块级测试夹具**
   - 热平衡；
   - 标准收率；
   - TLP/分馏；
   - 产品性质；
   - 蒸馏转换；
   - 物性换算。

3. **先迁移确定性强的模块**
   - 分子量常数；
   - 蒸馏曲线转换；
   - 物性换算；
   - 元素衡算。

4. **再迁移耦合强的模块**
   - 热平衡；
   - WHSV/迭代循环；
   - 分馏校准；
   - 催化剂管理；
   - CatCalc / Quench 插件。

5. **保留单位审计机制**
   - 文档大量使用 °F、lb/min、MBTU/min、vol%、wt%、API 等单位；
   - 现代实现应强制单位标注，避免 SI/Imperial 混用。

6. **建立回归测试数据集**
   - 从现有 Excel 或历史案例中抽取 base case 与 predict case；
   - 每个模块至少保留输入、期望输出和容差；
   - 对迭代模块记录收敛条件。

## 8. 质量与风险评估

| 风险 | 影响 | 建议 |
|---|---|---|
| 文档年代久远 | 安装、依赖、组织路径、授权流程可能失效 | 将历史部署说明与现代运行环境分离维护。 |
| `.doc` 嵌入对象未完整解析 | 流程图、图形、Excel 对象和公式对象可能遗漏 | 使用 Word/LibreOffice 导出 PDF 或 DOCX 后再做二次解析。 |
| 单位体系复杂 | 单位误用会造成严重计算偏差 | 建立单位字典和自动单位测试。 |
| 模型强依赖校准因子 | 未校准或校准数据质量差会影响预测可信度 | 明确 calibration data 的数据质量规则。 |
| Excel/宏依赖 | 现代安全策略和版本兼容性可能阻塞运行 | 规划无宏核心计算库与 Excel UI 解耦。 |
| 经验关联式缺少适用域说明 | 超出历史数据范围时外推风险高 | 为每个关联式补充输入范围、适用装置类型和警告条件。 |

## 9. 建议产出物

建议后续在仓库中补充以下文件，以便将两份 `.doc` 的价值转化为可维护资产：

- `docs/catsim-user-manual-outline.md`：用户手册结构化大纲；
- `docs/catsim-technical-formulas.md`：技术手册公式和变量整理；
- `docs/catsim-variable-dictionary.csv`：变量、含义、单位、来源章节；
- `docs/catsim-module-map.md`：模块依赖图与数据流；
- `tests/fixtures/catsim/`：历史 base/predict 案例输入输出；
- `docs/catsim-migration-plan.md`：从 Excel/宏到现代代码的迁移计划。

## 10. 最终判断

- `User manual-EN.doc` 适合作为**用户培训、操作 SOP 和问题排查**的基础。
- `Modelling Technical Manual-EN-Mark.doc` 适合作为**模型实现、验证、重构和迁移**的技术依据。
- 两份文档都应被视为 CatSim v4 的关键知识资产，但当前格式和年代决定了它们不应直接作为唯一运行依据；更合理的做法是将其拆解为结构化模块说明、变量字典、公式库和可执行测试案例。
