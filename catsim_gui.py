"""CatSim document-driven demonstration interface.

This tkinter application turns the two legacy Word manuals and the Markdown
analysis in this repository into a navigable desktop interface. It is not a
replacement for the original CatSim Excel model; the calculation widgets are
lightweight engineering-style demonstrators that make the documented modules
visible and testable in Python.
"""

from __future__ import annotations

from dataclasses import dataclass
import tkinter as tk
from tkinter import messagebox, ttk


APP_TITLE = "CatSim v4 文档功能展示"
DOC_SOURCES = (
    "User manual-EN.doc",
    "Modelling Technical Manual-EN-Mark.doc",
    "doc-analysis.md",
)


@dataclass(frozen=True)
class ModuleInfo:
    """A CatSim functional module extracted from the documentation analysis."""

    name: str
    purpose: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    source: str
    caution: str = ""


MODULES: tuple[ModuleInfo, ...] = (
    ModuleInfo(
        "校准 / 预测双模式",
        "用装置实测数据建立 Base Case，并在 Predict Case 中评估原料、催化剂、操作条件或设计参数变化。",
        ("测试运行数据", "Feed / catalyst 性质", "FCC 操作变量", "设计参数"),
        ("校准因子", "Base/Predict 对比", "预测工况收率和性质"),
        "User manual: Operational Modes；Technical manual: Base/Predict calculation flow",
        "预测结果依赖校准质量，未校准或输入不完整时不应外推使用。",
    ),
    ModuleInfo(
        "热平衡",
        "闭合反应器与再生器能量约束，支持单级和两级再生器场景。",
        ("空气量", "烟气 CO/CO₂/O₂", "焦炭产率", "反应/再生温度", "蒸汽/提升气", "热损失"),
        ("coke yield", "air rate", "catalyst circulation", "WHSV", "preheat duty"),
        "Technical manual: Heat Balance",
        "文档使用 °F、lb/min、MBTU/min 等英制单位，现代实现必须做单位审计。",
    ),
    ModuleInfo(
        "标准收率预测",
        "将 plant data 标准化为 C5-、gasoline、LCO、DCO、coke 等标准收率，再叠加催化剂/原料/ severity 影响。",
        ("转化率", "feed 性质", "催化剂因子", "unit factors", "severity 指标"),
        ("C5 and lighter", "C5-221°C gasoline", "221-350°C LCO", "350°C+ DCO", "coke"),
        "Technical manual: Prediction of Standard Yields",
        "这里的 Python 演示仅体现模块关系，不复刻专有经验关联式。",
    ),
    ModuleInfo(
        "TLP 与分馏",
        "构造 Total Liquid Product 曲线，并用理想/非理想分馏、effective cut point 和 fractionation indices 得到工厂产品收率。",
        ("标准液体收率", "TLP 曲线", "产品切点", "分馏指数", "校准参数"),
        ("plant gasoline", "LCO", "DCO", "产品蒸馏性质", "切割点偏移"),
        "Technical manual: Fractionation & Prediction of Plant Yields",
        "原始流程图和部分公式为嵌入对象，需由 Word/PDF 视觉解析补全。",
    ),
    ModuleInfo(
        "产品性质预测",
        "预测标准产品和工厂产品的密度、硫、汽油辛烷值、RVP、柴油冷滤点/十六烷指数、粘度等。",
        ("产品收率", "feed 硫/氮", "性质分布", "gasoline composition", "校准因子"),
        ("API/SG", "sulphur", "RON/MON", "RVP", "cetane index", "viscosity"),
        "Technical manual: Product Quality Prediction",
        "性质模型适用范围需从历史案例或原 Excel 模型中验证。",
    ),
    ModuleInfo(
        "循环物流与催化剂管理",
        "处理产品循环、催化剂活性、金属、选择性、平衡/新鲜催化剂以及 CatCalc 插件相关评估。",
        ("recycle rate", "E-cat/F-cat 性质", "metals", "MAT/RMA", "实验室或供应商数据"),
        ("recycle correction", "activity/selectivity impacts", "catalyst scenario comparison"),
        "User manual: Catalyst Management；Technical manual: Product Recycle & CatCalc",
        "催化剂数据质量直接影响长期优化和 reformulation 结论。",
    ),
    ModuleInfo(
        "元素衡算、蒸馏转换与物性换算",
        "用硫/氢衡算、D1160/TBP/D86/Simdis 转换、沸点与碳残炭等换算支撑输入输出一致性。",
        ("feed/product elemental data", "distillation curve", "pressure", "API/SG", "carbon residue"),
        ("sulphur balance", "hydrogen balance", "converted distillation curves", "physical properties"),
        "Technical manual: Elemental Balances; Distillation Conversion; Physical Property Calculations",
        "建议优先工程化这些确定性较强的模块并建立回归测试。",
    ),
)

WORKFLOW_STEPS = (
    ("1. 数据准备", "收集 feed properties、catalyst properties、FCC operating variables、设计参数和测试运行数据。"),
    ("2. Base Case 校准", "在 Calibrate 模式下用已知 x/y 数据调整 unit factors、产品切割和性质校准。"),
    ("3. 模块计算", "依次闭合热平衡、标准收率、TLP/分馏、产品性质、循环与元素衡算。"),
    ("4. Predict Case", "改变 feed、催化剂、操作条件或设计参数，沿用校准因子预测新工况。"),
    ("5. 审核与排错", "检查 Base/Predict 一致性、单位、输入完整性、金属/活性数据、Excel/宏兼容性。"),
)


class ScrollableFrame(ttk.Frame):
    """A vertically scrollable frame for long document-driven content."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.content = ttk.Frame(self.canvas)
        self.window_id = self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.content.bind("<Configure>", self._sync_scroll_region)
        self.canvas.bind("<Configure>", self._sync_width)

    def _sync_scroll_region(self, _event: tk.Event) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _sync_width(self, event: tk.Event) -> None:
        self.canvas.itemconfigure(self.window_id, width=event.width)


class CatSimInterface:
    """Main tkinter UI for exploring documented CatSim capabilities."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry("1120x760")
        self.root.minsize(980, 680)
        self._configure_style()
        self._build_layout()

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Arial", 18, "bold"), foreground="#0f172a")
        style.configure("Subtitle.TLabel", font=("Arial", 11), foreground="#475569")
        style.configure("Card.TFrame", background="#f8fafc", relief="solid", borderwidth=1)
        style.configure("CardTitle.TLabel", font=("Arial", 12, "bold"), background="#f8fafc", foreground="#1e3a8a")
        style.configure("CardBody.TLabel", font=("Arial", 10), background="#f8fafc", foreground="#1f2937")
        style.configure("Accent.TButton", font=("Arial", 10, "bold"))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

    def _build_layout(self) -> None:
        header = ttk.Frame(self.root, padding=(18, 14, 18, 8))
        header.pack(fill="x")
        ttk.Label(header, text=APP_TITLE, style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="基于两个旧版 Word 手册与 doc-analysis.md，把 CatSim v4 的操作流程、模型模块、风险和工程化路线做成可浏览界面。",
            style="Subtitle.TLabel",
            wraplength=1050,
        ).pack(anchor="w", pady=(4, 0))

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=18, pady=(4, 18))
        self._build_overview_tab(notebook)
        self._build_modules_tab(notebook)
        self._build_calculator_tab(notebook)
        self._build_risks_tab(notebook)

    def _build_overview_tab(self, notebook: ttk.Notebook) -> None:
        tab = ScrollableFrame(notebook)
        notebook.add(tab, text="总览与流程")
        content = tab.content
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)

        self._add_card(
            content,
            "文档定位",
            "User manual-EN.doc 面向模型使用者，强调安装授权、Excel 导航、校准/预测和故障排查。\n"
            "Modelling Technical Manual-EN-Mark.doc 面向模型维护和验证，强调热平衡、收率、分馏、性质、循环、催化剂、衡算和物性换算。\n"
            "doc-analysis.md 将两份文档整理为模块边界、数据流、风险和迁移建议。",
            0,
            0,
        )
        self._add_card(
            content,
            "核心能力",
            "• 热平衡与再生器/反应器约束\n"
            "• 标准收率、TLP 与工厂产品收率预测\n"
            "• 产品性质、汽油组成、循环物流预测\n"
            "• 催化剂管理、元素衡算、蒸馏与物性换算\n"
            "• Calibrate / Predict 双模式和 Excel 风格工作流",
            0,
            1,
        )

        flow = ttk.LabelFrame(content, text="CatSim 数据流抽象", padding=12)
        flow.grid(row=1, column=0, columnspan=2, sticky="ew", padx=8, pady=8)
        flow.columnconfigure(0, weight=1)
        flow_text = (
            "Feed / Catalyst / Operating Conditions / Design Parameters\n"
            "        │\n"
            "        ├─► Heat Balance ─► WHSV / preheat / catalyst circulation\n"
            "        ├─► Standard Yield Prediction ─► calibration factors / unit factors\n"
            "        ├─► TLP & Fractionation ─► plant stream yields / cut points\n"
            "        ├─► Product Quality Prediction ─► product specifications\n"
            "        ├─► Recycle / Catalyst Management\n"
            "        └─► Material, Sulphur, Hydrogen Balances ─► final outputs and warnings"
        )
        ttk.Label(flow, text=flow_text, font=("Consolas", 10), justify="left").grid(sticky="ew")

        for row, (title, body) in enumerate(WORKFLOW_STEPS, start=2):
            self._add_card(content, title, body, row, 0, columnspan=2)

    def _build_modules_tab(self, notebook: ttk.Notebook) -> None:
        tab = ttk.Frame(notebook, padding=12)
        notebook.add(tab, text="功能模块")
        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=2)
        tab.rowconfigure(0, weight=1)

        self.module_list = tk.Listbox(tab, height=15, exportselection=False, font=("Arial", 11))
        for module in MODULES:
            self.module_list.insert("end", module.name)
        self.module_list.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.module_list.bind("<<ListboxSelect>>", self._show_module_details)

        detail = ttk.LabelFrame(tab, text="模块说明", padding=12)
        detail.grid(row=0, column=1, sticky="nsew")
        detail.columnconfigure(0, weight=1)
        detail.rowconfigure(0, weight=1)
        self.module_text = tk.Text(detail, wrap="word", font=("Arial", 11), padx=12, pady=12)
        detail_scroll = ttk.Scrollbar(detail, orient="vertical", command=self.module_text.yview)
        self.module_text.configure(yscrollcommand=detail_scroll.set)
        self.module_text.grid(row=0, column=0, sticky="nsew")
        detail_scroll.grid(row=0, column=1, sticky="ns")
        self.module_text.tag_configure("title", font=("Arial", 15, "bold"), foreground="#1d4ed8")
        self.module_text.tag_configure("label", font=("Arial", 11, "bold"), foreground="#0f172a")
        self.module_text.tag_configure("warning", foreground="#b45309")
        self.module_list.selection_set(0)
        self._show_module_details()

    def _build_calculator_tab(self, notebook: ttk.Notebook) -> None:
        tab = ttk.Frame(notebook, padding=12)
        notebook.add(tab, text="演示计算台")
        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(0, weight=1)

        input_box = ttk.LabelFrame(tab, text="场景输入（演示值，可编辑）", padding=12)
        input_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        for col in (0, 1):
            input_box.columnconfigure(col, weight=1)
        self.inputs: dict[str, tk.DoubleVar] = {}
        fields = (
            ("feed_rate", "Feed rate / 原料量", 100.0, "kt/a 或任意一致基准"),
            ("conversion", "Conversion / 转化率", 72.0, "wt%"),
            ("gasoline_selectivity", "Gasoline selectivity / 汽油选择性", 58.0, "% of converted"),
            ("coke_selectivity", "Coke selectivity / 焦炭选择性", 6.5, "% of converted"),
            ("lco_cut", "LCO liquid split / LCO 切割比例", 64.0, "% of unconverted liquid"),
            ("feed_sulfur", "Feed sulphur / 原料硫", 1.8, "wt%"),
            ("hydrogen_on_coke", "Hydrogen on coke / 焦炭氢", 7.5, "wt%"),
            ("oxygen_excess", "Excess oxygen / 过量氧", 3.0, "%"),
        )
        for row, (key, label, default, unit) in enumerate(fields):
            ttk.Label(input_box, text=label).grid(row=row, column=0, sticky="w", pady=5)
            var = tk.DoubleVar(value=default)
            self.inputs[key] = var
            ttk.Entry(input_box, textvariable=var, width=14).grid(row=row, column=1, sticky="ew", pady=5)
            ttk.Label(input_box, text=unit, foreground="#64748b").grid(row=row, column=2, sticky="w", padx=(8, 0), pady=5)
        ttk.Button(input_box, text="运行模块演示", style="Accent.TButton", command=self._run_demo_calculation).grid(
            row=len(fields), column=0, columnspan=3, sticky="ew", pady=(14, 4)
        )
        ttk.Button(input_box, text="恢复默认值", command=self._reset_demo_inputs).grid(
            row=len(fields) + 1, column=0, columnspan=3, sticky="ew", pady=4
        )

        output_box = ttk.LabelFrame(tab, text="模块输出（非原 CatSim 公式，仅展示数据流）", padding=12)
        output_box.grid(row=0, column=1, sticky="nsew")
        output_box.columnconfigure(0, weight=1)
        output_box.rowconfigure(0, weight=1)
        self.output_text = tk.Text(output_box, wrap="word", font=("Consolas", 10), padx=12, pady=12)
        out_scroll = ttk.Scrollbar(output_box, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=out_scroll.set)
        self.output_text.grid(row=0, column=0, sticky="nsew")
        out_scroll.grid(row=0, column=1, sticky="ns")
        self.output_text.tag_configure("heading", font=("Consolas", 11, "bold"), foreground="#1d4ed8")
        self.output_text.tag_configure("warn", foreground="#b45309")
        self._run_demo_calculation()

    def _build_risks_tab(self, notebook: ttk.Notebook) -> None:
        tab = ScrollableFrame(notebook)
        notebook.add(tab, text="风险与迁移路线")
        content = tab.content
        content.columnconfigure(0, weight=1)

        risks = (
            ("文档年代久远", "用户手册最后修改日期为 2003-12-10，安装、授权、共享服务器、Help desk 和 Excel/API Databook 依赖需重新验证。"),
            ("嵌入对象未完全解析", "Visio 流程图、Excel 对象、公式对象和图片未做视觉/OCR 解析，迁移前应由 Word/LibreOffice 导出 PDF 或 DOCX 再复核。"),
            ("单位体系复杂", "文档大量使用 °F、lb/min、MBTU/min、vol%、wt%、API 等单位，所有 Python 计算应带单位字典和测试。"),
            ("强依赖校准因子", "CatSim 是机理、经验关联式和装置校准因子的组合，必须保留 base/predict 回归案例。"),
            ("Excel/宏依赖", "原系统通过 Excel workbook 暴露输入、输出、按钮和插件，现代化应拆分为无宏核心计算库 + 可替换 UI。"),
        )
        for row, (title, body) in enumerate(risks):
            self._add_card(content, title, body, row, 0)

        migration = ttk.LabelFrame(content, text="建议工程化优先级", padding=12)
        migration.grid(row=len(risks), column=0, sticky="ew", padx=8, pady=8)
        steps = (
            "1. 保存 .doc 原文，补充纯文本、公式、变量、单位和常数基线。",
            "2. 建立热平衡、标准收率、TLP/分馏、产品性质、蒸馏转换、物性换算测试夹具。",
            "3. 优先迁移分子量常数、蒸馏曲线转换、物性换算、元素衡算。",
            "4. 再迁移热平衡、WHSV/迭代循环、分馏校准、催化剂管理、CatCalc/Quench 插件。",
            "5. 为每个模块保留输入范围、单位审计、收敛条件和 Base/Predict 回归数据。",
        )
        ttk.Label(migration, text="\n".join(steps), justify="left", wraplength=1000).pack(anchor="w")

    def _add_card(
        self,
        parent: ttk.Frame,
        title: str,
        body: str,
        row: int,
        column: int,
        columnspan: int = 1,
    ) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=12)
        card.grid(row=row, column=column, columnspan=columnspan, sticky="ew", padx=8, pady=8)
        card.columnconfigure(0, weight=1)
        ttk.Label(card, text=title, style="CardTitle.TLabel").grid(sticky="w")
        ttk.Label(card, text=body, style="CardBody.TLabel", wraplength=980, justify="left").grid(sticky="ew", pady=(6, 0))

    def _show_module_details(self, _event: tk.Event | None = None) -> None:
        selection = self.module_list.curselection()
        index = selection[0] if selection else 0
        module = MODULES[index]
        self.module_text.configure(state="normal")
        self.module_text.delete("1.0", "end")
        self.module_text.insert("end", f"{module.name}\n\n", "title")
        self.module_text.insert("end", "目的\n", "label")
        self.module_text.insert("end", f"{module.purpose}\n\n")
        self.module_text.insert("end", "主要输入\n", "label")
        self.module_text.insert("end", "\n".join(f"• {item}" for item in module.inputs) + "\n\n")
        self.module_text.insert("end", "主要输出\n", "label")
        self.module_text.insert("end", "\n".join(f"• {item}" for item in module.outputs) + "\n\n")
        self.module_text.insert("end", "文档来源\n", "label")
        self.module_text.insert("end", f"{module.source}\n\n")
        if module.caution:
            self.module_text.insert("end", "注意\n", "label")
            self.module_text.insert("end", module.caution, "warning")
        self.module_text.configure(state="disabled")

    def _run_demo_calculation(self) -> None:
        values = {name: var.get() for name, var in self.inputs.items()}
        validation_error = validate_demo_inputs(values)
        if validation_error:
            messagebox.showerror("输入错误", validation_error)
            return
        result = calculate_demo_case(values)
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("end", "⚠ 说明：以下计算用于展示文档描述的模块数据流，不是 CatSim 专有公式复刻。\n\n", "warn")
        self.output_text.insert("end", "1) Standard Yield Prediction / 标准收率\n", "heading")
        self.output_text.insert("end", format_block(result["standard_yields"]))
        self.output_text.insert("end", "\n2) TLP & Fractionation / TLP 与分馏\n", "heading")
        self.output_text.insert("end", format_block(result["fractionation"]))
        self.output_text.insert("end", "\n3) Heat Balance Proxy / 热平衡代理指标\n", "heading")
        self.output_text.insert("end", format_block(result["heat_balance"]))
        self.output_text.insert("end", "\n4) Product Quality Proxy / 产品性质代理指标\n", "heading")
        self.output_text.insert("end", format_block(result["qualities"]))
        self.output_text.insert("end", "\n5) Engineering Checks / 工程检查\n", "heading")
        self.output_text.insert("end", "\n".join(f"• {item}" for item in result["checks"]))
        self.output_text.configure(state="disabled")

    def _reset_demo_inputs(self) -> None:
        defaults = {
            "feed_rate": 100.0,
            "conversion": 72.0,
            "gasoline_selectivity": 58.0,
            "coke_selectivity": 6.5,
            "lco_cut": 64.0,
            "feed_sulfur": 1.8,
            "hydrogen_on_coke": 7.5,
            "oxygen_excess": 3.0,
        }
        for key, value in defaults.items():
            self.inputs[key].set(value)
        self._run_demo_calculation()

    def run(self) -> None:
        self.root.mainloop()


def validate_demo_inputs(values: dict[str, float]) -> str:
    """Return a validation error for impossible demo inputs, or an empty string."""

    if values["feed_rate"] <= 0:
        return "Feed rate 必须大于 0。"
    percent_fields = (
        "conversion",
        "gasoline_selectivity",
        "coke_selectivity",
        "lco_cut",
        "hydrogen_on_coke",
        "oxygen_excess",
    )
    for field in percent_fields:
        if values[field] < 0 or values[field] > 100:
            return f"{field} 必须在 0 到 100 之间。"
    if values["feed_sulfur"] < 0 or values["feed_sulfur"] > 10:
        return "Feed sulphur 建议在 0 到 10 wt% 范围内。"
    if values["gasoline_selectivity"] + values["coke_selectivity"] > 95:
        return "汽油选择性与焦炭选择性之和过高，演示模型无法分配 C5- 收率。"
    return ""


def calculate_demo_case(values: dict[str, float]) -> dict[str, dict[str, float] | list[str]]:
    """Calculate a transparent demonstration case from the documented module flow."""

    feed = values["feed_rate"]
    conversion = values["conversion"] / 100
    converted = feed * conversion
    unconverted = feed - converted
    gasoline = converted * values["gasoline_selectivity"] / 100
    coke = converted * values["coke_selectivity"] / 100
    c5_light = max(converted - gasoline - coke, 0)
    lco = unconverted * values["lco_cut"] / 100
    dco = max(unconverted - lco, 0)
    total = c5_light + gasoline + lco + dco + coke

    hydrogen_coke = coke * values["hydrogen_on_coke"] / 100
    carbon_coke = max(coke - hydrogen_coke, 0)
    oxygen_for_carbon = carbon_coke * 2.667
    oxygen_for_hydrogen = hydrogen_coke * 8.0
    oxygen_required = (oxygen_for_carbon + oxygen_for_hydrogen) * (1 + values["oxygen_excess"] / 100)
    air_required = oxygen_required / 0.232

    feed_sulfur = feed * values["feed_sulfur"] / 100
    liquid_sulfur = feed_sulfur * 0.72
    gas_sulfur = feed_sulfur * 0.18
    coke_sulfur = max(feed_sulfur - liquid_sulfur - gas_sulfur, 0)

    checks = [
        f"物料闭合：输出合计 {total:.2f}，相对原料 {total / feed * 100:.2f}% 。",
        "若 Predict Case 与 Base Case 不一致，应优先检查输入完整性、单位、校准状态和迭代收敛。",
        "实际迁移时需用原 Excel/历史案例替换此演示中的简化选择性和硫分配假设。",
    ]
    if values["conversion"] > 85:
        checks.append("高转化率可能触发经验关联式外推风险，需要适用域检查。")
    if values["feed_sulfur"] > 3:
        checks.append("高硫原料会放大硫衡算和产品硫预测敏感性。")

    return {
        "standard_yields": {
            "C5 and lighter": c5_light,
            "C5-221°C gasoline": gasoline,
            "221-350°C LCO": lco,
            "350°C+ DCO": dco,
            "coke": coke,
        },
        "fractionation": {
            "TLP liquid total": gasoline + lco + dco,
            "gasoline liquid share": gasoline / max(gasoline + lco + dco, 1e-9) * 100,
            "LCO split of unconverted liquid": values["lco_cut"],
            "DCO split of unconverted liquid": 100 - values["lco_cut"],
        },
        "heat_balance": {
            "carbon on coke": carbon_coke,
            "hydrogen on coke": hydrogen_coke,
            "oxygen required proxy": oxygen_required,
            "air required proxy": air_required,
        },
        "qualities": {
            "feed sulphur in": feed_sulfur,
            "liquid sulphur proxy": liquid_sulfur,
            "gas sulphur proxy": gas_sulfur,
            "coke sulphur proxy": coke_sulfur,
            "gasoline RON proxy": 86.0 + conversion * 8.0 - coke / feed,
            "LCO cetane proxy": 38.0 - conversion * 6.0 + dco / max(feed, 1e-9) * 4.0,
        },
        "checks": checks,
    }


def format_block(values: dict[str, float]) -> str:
    """Format a numeric output dictionary for the UI."""

    return "\n".join(f"• {name:<32} {value:10.3f}" for name, value in values.items()) + "\n"


if __name__ == "__main__":
    CatSimInterface().run()
