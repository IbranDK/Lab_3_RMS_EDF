"""Практическая работа №3: планирование периодических задач (RMS и EDF).
Вариант: «Бортовая система: управление, датчики, связь».
Запуск: python src/main.py -i data/variant.json --png docs/gantt.png
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence
# =========================
# Модель
# =========================
@dataclass(frozen=True)
class Task:
    name: str
    C: int  # время выполнения (WCET), мс
    T: int  # период, мс
    D: int  # относительный дедлайн, мс
# =========================
# Расчётные функции
# =========================
def by_priority(tasks: Iterable[Task]) -> list[Task]:
    """RMS: меньший период -> выше приоритет (первый в списке — старший)."""
    return sorted(tasks, key=lambda t: t.T)


def utilization(tasks: Iterable[Task]) -> float:
    """U = sum(Ci / Ti)."""
    return sum(t.C / t.T for t in tasks)


def liu_layland_bound(n: int) -> float:
    """Граница Liu & Layland: n * (2^(1/n) - 1)."""
    if n <= 0:
        raise ValueError("n должно быть положительным")
    return n * (2 ** (1 / n) - 1)


def rms_schedulable(tasks: Sequence[Task]) -> bool:
    """Достаточный утилизационный тест: U <= n(2^(1/n) - 1)."""
    return utilization(tasks) <= liu_layland_bound(len(tasks))