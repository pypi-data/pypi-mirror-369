from typing import Dict, List

from .default_warnings import EDAWarning


class WarningSystem:
    def __init__(self, warnings: Dict[str, EDAWarning]):
        self.warnings = warnings

    def register_warning(self, name: str, warning_obj: EDAWarning):
        """Register a new warning object."""
        self.warnings[name] = warning_obj
        print(f"Registered warning '{name}'")

    def run_warnings(self) -> Dict[str, List[Dict[str, str]]]:
        """Run all registered warning objects and return the results."""
        results = {}
        for name, warning_obj in self.warnings.items():
            results[name] = warning_obj.run()
        return results
