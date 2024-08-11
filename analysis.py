# -*- coding: utf-8 -*-
import os
from pathlib import Path
import toml

from config import config

def get_analysis():
    directories = [d for d in Path(config.ANALYSIS_DIR).iterdir() if d.is_dir() and not d.name.startswith('.')]

    analysis: list[Analysis] = []

    for dir in directories:
        analysis_toml = os.path.join(dir, "analysis.toml")
        if os.path.exists(analysis_toml):
            analysis.append(Analysis(file=analysis_toml))

    return analysis


class Analysis:  # pylint: disable=too-few-public-methods

    def __init__(self, file):
        self.path = os.path.abspath(os.path.dirname(file))
        self.dirname = os.path.split(self.path)[1]

        self.analysis = toml.load(file)
