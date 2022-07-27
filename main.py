from __future__ import annotations
from typing import List, Tuple, Dict, Set, Optional
from dataclasses import dataclass, field
import random as ra
from omegaconf import OmegaConf
import wandb


config = OmegaConf.load("config.yaml")

# wandb.init(project="monkeypox-simulation", entity="willian")
# wandb.config = config

@dataclass()
class Person:
    id: int
    gender: bool
    affair_rate: float
    spouse: Optional[Person] = None
    
    positive: bool = False
    immued_infection: bool = False
    onset: int = 0
    
    
    def marry(self, other: Person):
        other.spouse = self
        self.spouse = other
        
    def try_infect(self):
        if self.positive:
            onset += 1
            if onset == config.cure_days:
                self.immued_infection = True
                self.positive = False
            return 
        if self.immued_infection:
            return
        
        infection_probability = config.infection_rates.male if self.gender else config.infection_rates.female
        if ra.random() < infection_probability:
            self.positive = True        
        
    def intercourse(self, other: Person):
        if self.positive:
            other.try_infect()

    def __hash__(self): 
        return hash(self.id)


@dataclass
class World:
    population: Set[Person] = field(default_factory=set)
    males: Set[Person] = field(default_factory=set)
    femls: Set[Person] = field(default_factory=set)
    攻め: Set[Person] = field(default_factory=set)
    free: Set[Person] = field(default_factory=set)
    free_males: Set[Person] = field(default_factory=set)
    free_femls: Set[Person] = field(default_factory=set)
    
    def __init__(self) -> None:
        self.males = set()
        self.femls = set()
        self.population = set()
        self.free = set()
        self.攻め = set()
        self.free_males = set()
        self.free_femls = set()
        # fill in world and groups
        print("Initializing world...")
        
        single_males = set()
        single_femls = set()
        for id in range(config.population_size):
            
            p = Person(id=id,
                       gender=ra.random() < config.gender_ratio,
                       affair_rate=config.affair_rate, # TODO: use distribition
                )
            
            if p.gender:
                self.males.add(p)
                single_males.add(p)
            else:
                self.femls.add(p)
                single_femls.add(p)
            self.population.add(p)
        
        print("Marrying the world population")
        for p in self.population:
            if ra.random() > config.single_rate:
                try:
                    if ra.random() < config.homo_rate:
                        gender_group = single_males if p.gender else single_femls
                    else:
                        gender_group = single_femls if p.gender else single_males
                    spouse = gender_group.pop()
                    p.marry(spouse)
                    self.攻め.add(p)
                except KeyError:
                    # No one is single anymore sorry
                    self.free.add(p)
                    free_group = self.free_males if p.gender else self.free_femls
                    free_group.add(p)
            else:
                # I single because I am single
                self.free.add(p)
                free_group = self.free_males if p.gender else self.free_femls
                free_group.add(p)
                
    def statistics(self, day: int = 0) -> Dict[str, float]:
        infected = set(p for p in self.population if p.positive)
        male_len = len(tuple(1 for p in infected if p.gender))
        homo_len = len(tuple(1 for p in infected if p.spouse and p.gender == p.spouse.gender))
        male_homo_len = len(tuple(1 for p in infected if p.spouse and p.gender and p.gender == p.spouse.gender))
        feml_homo_len = len(tuple(1 for p in infected if p.spouse and (not p.gender) and p.gender == p.spouse.gender))
        return {
            "day": day,
            "infected": len(infected),
            "male_infected": male_len,
            "feml_infected": len(infected) - male_len,
            "homo_infected": homo_len
        }
    
    def give_me_someone_random(self, gender: bool, abandened_males: Set[Person], abandened_femls: Set[Person]) -> Optional[Person]:
        if ra.random() < config.homo_rate:
            gender_group = self.free_males & abandened_males if gender else self.free_femls & abandened_femls
        else:
            gender_group = self.free_femls & abandened_femls if gender else self.free_males & abandened_males
        if len(gender_group) > 0:
            temp = list(gender_group)
            return ra.choice(temp)
        else:
            return None
    
    def one_day_past(self):
        abandened_males: Set[Person] = set()
        abandened_femls: Set[Person] = set()
        for 攻 in self.攻め:
            if 攻.spouse:
                p: Person = 攻 if ra.random()> 0.5 else 攻.spouse 
                if ra.random() > p.affair_rate:
                    sexmate: Person = p.spouse
                else:
                    sexmate = self.give_me_someone_random(p.gender, abandened_males, abandened_femls)
                    abandened_group = abandened_males if p.spouse.gender else abandened_femls
                    abandened_group.add(p.spouse)
            else:
                sexmate = self.give_me_someone_random(p.gender, abandened_males, abandened_femls)
            if sexmate:
                p.intercourse(sexmate)
        for p in self.free:
            sexmate = self.give_me_someone_random(p.gender, abandened_males, abandened_femls)
            if sexmate:
                p.intercourse(sexmate)
            
    def run(self, days: int):
        for d in range(days):
            self.one_day_past()
            print(self.statistics(d))
            # wandb.log(self.statistics())
        
def main():
    world = World()
    world.run(config.days)
    
if __name__ == "__main__":
    main()
