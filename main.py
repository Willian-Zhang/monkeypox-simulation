from __future__ import annotations
from typing import List, Tuple, Dict, Set, Optional
from dataclasses import dataclass
import random as ra
from omegaconf import OmegaConf
import wandb


config = OmegaConf.load("config.yaml")

wandb.init(project="monkeypox-simulation", entity="willian")
wandb.config = config

@dataclass
class Person:
    gender: bool
    spouse: Person
    positive: bool = False
    onset: int = 0
    
    def marry(self, other: Person):
        other.spouse = self
        self.spouse = other
        
    def intercourse(self, other: Person):
        ...

@dataclass
class World:
    population: List[Person] = []
    def __init__(self) -> None:
        for _ in range(config.population_size):
            p = Person()
            p.gender = ra.random() < config.gender_ratio


# wandb.log({"loss": loss})
