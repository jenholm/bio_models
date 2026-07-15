from __future__ import annotations
from collections import Counter
import numpy as np
from tqdm import trange
from .config import HSAPConfig
from .entities import Agent
from .environment import Environment
from .endocrine import EndocrineSystem
from .behavior import BehaviorEngine
from .reproduction import ReproductionEngine
from .mortality import MortalityEngine
from .population import PopulationDynamics
from .metrics import MetricsCollector
from .visual_trace import VisualTrace


INJURY_RECOVERY_RATE = 0.3


class Simulation:
    def __init__(self, config: HSAPConfig):
        self.config = config
        self.rng = np.random.default_rng(config.random_seed)
        self.env = Environment(config, self.rng)
        self.endocrine = EndocrineSystem(config)
        self.behavior = BehaviorEngine(config, self.rng)
        self.reproduction = ReproductionEngine(config, self.rng)
        self.mortality = MortalityEngine(config, self.rng)
        self.pop_dynamics = PopulationDynamics(self.rng)
        self.metrics = MetricsCollector()
        self.visual_trace = VisualTrace()
        self.agents: list[Agent] = []
        self.next_id: int = 0
        self.step_count: int = 0

    def initialize(self):
        for i in range(self.config.initial_population):
            sex = "male" if self.rng.random() < 0.5 else "female"
            agent = Agent(
                agent_id=self.next_id,
                sex=sex,
                age=self.rng.integers(5, 40),
                config=self.config,
                rng=self.rng,
            )
            agent.reset_dynamics(self.config)
            self.agents.append(agent)
            self.next_id += 1
        self.env.sync_population(len(self.agents))
        self._update_all_agents()

    def _update_all_agents(self):
        density = self.env.density
        for agent in self.agents:
            self.endocrine.update(agent, self.env, density)

    def step(self):
        self.step_count += 1
        density = self.env.density
        self.env.step(len(self.agents))

        event_counts = {
            "births": 0,
            "deaths": 0,
            "matings": 0,
            "pregnancies": 0,
            "infanticide": 0,
            "neglect": 0,
            "refugees": 0,
            "actions": Counter(),
        }

        sink = self.env.sink_factor
        recovery = self.env.post_sink_recovery
        ep = self.config.environment

        for agent in self.agents[:]:
            if not agent.alive:
                continue
            agent.step_age(self.config.age_increment)
            agent.stress = agent.cortisol
            self.endocrine.update(agent, self.env, density)

            # Behavioral sink: fertility penalty
            if sink > 0:
                agent.fertility *= (1.0 - sink * ep.behavioral_sink_fertility_penalty)

            # Post-sink recovery: fertility boost
            if recovery:
                agent.fertility *= (1.0 + ep.behavioral_sink_recovery_fertility_boost)

            action = self.behavior.execute(agent, self.env)
            event_counts["actions"][action] += 1

            if agent.injury and agent.injury_timer > 0:
                agent.injury_timer -= 1
                if agent.injury_timer <= 0:
                    if self.rng.random() < INJURY_RECOVERY_RATE:
                        agent.injury = False

            if agent.sex == "male":
                agent.mating_drive = agent.testosterone * 0.5 + 0.3
            else:
                agent.mating_drive = agent.estrogen * 0.4 + 0.2

            # Behavioral sink: mating drive penalty
            if sink > 0:
                agent.mating_drive *= (1.0 - sink * ep.behavioral_sink_mating_penalty)

            # Post-sink recovery: mating drive boost
            if recovery:
                agent.mating_drive *= (1.0 + ep.behavioral_sink_recovery_mating_boost)

        new_offspring: list[Agent] = []
        females = [a for a in self.agents if a.sex == "female" and a.alive]
        males = [a for a in self.agents if a.sex == "male" and a.alive]

        # Pregnancy processing with proper ID assignment
        for female in females:
            offspring = self.reproduction.process_pregnancy(female, self.env)
            for child in offspring:
                if self.mortality.check_death(child, self.env, mortality_multiplier=self.env.mortality_multiplier):
                    continue
                child.agent_id = self.next_id
                self.next_id += 1
                child.reset_dynamics(self.config)
                new_offspring.append(child)
                female.offspring_ids.append(child.agent_id)
                event_counts["births"] += 1

        fertility_gate = ep.behavioral_sink_recovery_female_fertility_gate if recovery else 0.3
        for male in males:
            if self.rng.random() < male.mating_drive * 0.8:
                available = [
                    f
                    for f in females
                    if not f.pregnant and f.fertility > fertility_gate
                ]
                if available:
                    female = self.rng.choice(available)
                    if self.reproduction.mate(male, female, self.env):
                        event_counts["matings"] += 1
                        event_counts["pregnancies"] += 1

        # Infanticide and neglect (sink from line 72 is already in scope)
        for agent in self.agents[:]:
            if not agent.alive:
                continue
            infanticide_triggered = self.reproduction.check_infanticide(agent, self.env)
            if agent.guarding and infanticide_triggered:
                if self.rng.random() < 0.5:
                    infanticide_triggered = False
            if infanticide_triggered:
                if agent.offspring_ids:
                    agent.offspring_ids = []
                    event_counts["infanticide"] += 1
            neglect_prob = 0.3
            if sink > 0:
                neglect_prob += sink * ep.behavioral_sink_neglect_bonus
            if self.reproduction.check_offspring_neglect(agent, self.env):
                if agent.offspring_ids and self.rng.random() < neglect_prob:
                    removed = agent.offspring_ids.pop()
                    self.agents = [a for a in self.agents if a.agent_id != removed]
                    event_counts["neglect"] += 1

        # Mortality
        dead: list[Agent] = []
        mm = self.env.mortality_multiplier
        for agent in self.agents:
            if not agent.alive:
                continue
            if self.mortality.check_death(agent, self.env, mortality_multiplier=mm):
                agent.alive = False
                dead.append(agent)

        for d in dead:
            self.agents.remove(d)
            event_counts["deaths"] += 1

        self.agents.extend(new_offspring)

        # Weaning: clean up dead and weaned offspring IDs
        self.pop_dynamics.update_offspring_links(self.agents, self.config.reproduction.weaning_age)

        # Refuge injection during recovery if population too low
        if recovery and len(self.agents) < ep.behavioral_sink_recovery_min_population:
            needed = min(
                ep.behavioral_sink_recovery_refugee_count,
                ep.behavioral_sink_recovery_min_population - len(self.agents),
            )
            for _ in range(needed):
                sex = "female" if self.rng.random() < 0.5 else "male"
                refugee = Agent(
                    agent_id=self.next_id,
                    sex=sex,
                    age=self.rng.integers(10, 30),
                    config=self.config,
                    rng=self.rng,
                )
                refugee.reset_dynamics(self.config)
                self.agents.append(refugee)
                self.next_id += 1
                event_counts["refugees"] += 1

        # Final end-of-step sync after births, deaths, neglect removals, and refugees.
        self.env.sync_population(len(self.agents))

        self._update_all_agents()

        # Record
        self.metrics.record(self.step_count, self.agents, self.env, self.pop_dynamics, events=event_counts)
        self.visual_trace.record(
            step=self.step_count,
            agents=self.agents,
            env=self.env,
            pop=self.pop_dynamics,
            events=event_counts,
        )

    def run(self, steps: int | None = None) -> MetricsCollector:
        if self.agents:
            raise RuntimeError(
                "Simulation.run() called after agents already initialized. "
                "Remove sim.initialize() before sim.run()."
            )
        max_steps = steps or self.config.max_steps
        self.initialize()
        self.metrics.record(0, self.agents, self.env, self.pop_dynamics)
        self.visual_trace.record(
            step=0,
            agents=self.agents,
            env=self.env,
            pop=self.pop_dynamics,
            events=None,
        )
        for _ in trange(max_steps, desc="Simulation"):
            self.step()
            if len(self.agents) == 0:
                break
        return self.metrics
