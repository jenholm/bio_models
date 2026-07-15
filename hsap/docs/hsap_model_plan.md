# HSAP Model Plan

## Architecture

Four-layer simulation:

1. **Environment** — resource abundance, predation, disease, space, seasonality
2. **Agents** — individual mammals with sex, age, energy, rank, endocrine proxies
3. **Behavior** — probabilistic action selection influenced by endocrine state
4. **Population** — emergent birth/death rates, age structure, aggression rates

## Development milestones

- **M0**: Project skeleton (complete)
- **M1**: Deterministic population baseline (null models)
- **M2**: Agent-based mammal population (no hormones)
- **M3**: Endocrine proxy layer
- **M4**: Behavioral coupling
- **M5**: Scenario grid
- **M6**: Genetic algorithm search
- **M7**: Sensitivity and robustness
- **M8**: Literature/data matrix
- **M9**: Final verdict report

## Key design principles

1. **Endocrine proxies are outputs and mediators, not magic causes.**
2. **Resource abundance and crowding are separate axes.**
3. **Start simple, add complexity only after baselines work.**
4. **The GA is both microscope and crowbar — search for support AND failure.**
5. **HSAP must beat null models, not just exist.**
