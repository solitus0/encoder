import json
import os
from typing import List

from encoder.preset.schemas import Preset


class PresetsCollection:
    def __init__(self):
        self.loader = PresetLoader()

    def get(self, name: str) -> Preset:
        preset = self.loader.get(name)
        return Preset(**preset)

    def all(self) -> List[Preset]:
        return [Preset(**preset) for preset in self.loader.all()]


class PresetLoader:
    def __init__(self):
        self.presets_dir = self._get_presets_path()

    def get(self, name: str):
        all_presets = self._load_all()
        for preset in all_presets:
            if preset.get("PresetName", "") == name:
                return preset
        raise Exception(f"Preset {name} not found")

    def all(self):
        all_presets = self._load_all()
        return all_presets

    def _load_all(self):
        presets = []
        for filename in os.listdir(self.presets_dir):
            with open(os.path.join(self.presets_dir, filename), "r") as f:
                data = json.load(f)
            preset_list = data.get("PresetList", [])
            presets.extend(preset_list)
        return presets

    def _get_presets_path(self) -> str:
        path = os.path.abspath(__file__)
        path = os.path.dirname(path)

        return os.path.join(path, "data/presets")
