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