# ── Пулы моделей по роли ─────────────────────────────────────────────────────
MODEL_POOLS: dict[str, list[str]] = {
    "developer":        ["qwen2.5-coder:7b"],
    "reviewer":         ["qwen2.5-coder:7b"],
    "e2e_architect":    ["qwen3:latest"],
    "e2e_qa":           ["qwen3:latest"],
    "qa_runtime":       ["qwen3:latest"],
    "business_analyst": ["qwen3:latest"],
    "system_analyst":   ["qwen2.5-coder:7b"],
    "architect":        ["qwen2.5-coder:7b"],
    "spec_reviewer":    ["qwen3:latest"],
    "test_generator":   ["qwen2.5-coder:7b"],
    "documenter":       ["qwen3:latest"],
    "devops_runtime":   ["qwen3:latest"],
    "arch_validator":   ["qwen2.5-coder:7b"],
    "supervisor":       ["qwen3:latest"],
    "self_reflect":     ["qwen2.5-coder:7b"],
    "contract_analyst": ["qwen2.5-coder:7b"],  # NEW: генерирует A5
    "a5_validator":     ["qwen2.5-coder:7b"],
}