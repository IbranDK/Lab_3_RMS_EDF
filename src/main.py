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

def edf_schedulable(tasks: Sequence[Task]) -> bool:
    """EDF при неявных дедлайнах (D = T): необходимо и достаточно U <= 1.

    Если есть D < T, применяется достаточное условие по плотности:
    sum(C / min(D, T)) <= 1.
    """
    if all(t.D >= t.T for t in tasks):
        return utilization(tasks) <= 1.0
    return sum(t.C / min(t.D, t.T) for t in tasks) <= 1.0

def response_time(task: Task, higher: Sequence[Task]) -> int | None:
    """Анализ времени отклика: R(k+1) = C + sum(ceil(R(k) / Tj) * Cj), R(0) = C.

    Итерация останавливается при R(k+1) = R(k) либо при R > D
    (задача не укладывается в дедлайн -> None).
    """
    r = task.C
    while True:
        r_next = task.C + sum(math.ceil(r / h.T) * h.C for h in higher)
        if r_next == r:
            return r
        if r_next > task.D:
            return None
        r = r_next

def hyperperiod(tasks: Iterable[Task]) -> int:
    """Гиперпериод — наименьшее общее кратное периодов."""
    return math.lcm(*(t.T for t in tasks))


def simulate_rms(tasks: Sequence[Task], interval: int) -> list[str | None]:
    """Вытесняющая симуляция RMS с шагом 1 мс.

    Возвращает имя выполняющейся задачи на каждом такте (None — простой).
    """
    ordered = by_priority(tasks)
    remaining = {t.name: 0 for t in ordered}
    timeline: list[str | None] = []
    for now in range(interval):
        for t in ordered:
            if now % t.T == 0:
                remaining[t.name] += t.C
        running = next((t.name for t in ordered if remaining[t.name] > 0), None)
        if running is not None:
            remaining[running] -= 1
        timeline.append(running)
    return timeline


def gantt(tasks: Sequence[Task], interval: int) -> str:
    """Текстовая диаграмма выполнения по RMS на интервале [0, interval]."""
    timeline = simulate_rms(tasks, interval)
    ordered = by_priority(tasks)
    width = max(len(t.name) for t in ordered)
    pad = " " * (width + 3)
    tens = "".join(str(i // 10 % 10) if i % 10 == 0 else " " for i in range(interval))
    ones = "".join(str(i % 10) for i in range(interval))
    lines = [pad + tens, pad + ones]
    for t in ordered:
        row = "".join(
            "█" if name == t.name else ("|" if i % t.T == 0 else "·")
            for i, name in enumerate(timeline)
        )
        lines.append(f"{t.name.ljust(width)} | {row}")
    idle = "".join("█" if name is None else "·" for name in timeline)
    lines.append(f"{'Простой'.ljust(width)} | {idle}")
    return "\n".join(lines)

