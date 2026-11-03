"""Сборка СИСТЕМЫ_1 и СИСТЕМЫ_2 варианта в набор приборов модели."""

from __future__ import annotations

from .model import Device
from .variants import SystemSpec, Variant, law_phases, special_device


def devices(spec: SystemSpec, variant: Variant, law_device: int | None = None) -> tuple[Device, ...]:
    probs = variant.device_probs(spec.devices)
    phases = [1] * spec.devices
    if spec.law is not None:
        d = special_device(spec) if law_device is None else law_device
        phases[d] = law_phases(spec.law)
    return tuple(
        Device(f"П{i + 1}", probs[i], spec.buffers[i], phases[i])
        for i in range(spec.devices)
    )
