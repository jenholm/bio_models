# HSAP Model Time Units

## Simulation Step

One simulation step is an abstract time unit. It does not map directly to
days, months, or years. The model is parameterized in step units.

## Age

- `age_increment = 0.1` per step
- An agent at age 0 becomes adult at age 10 (= 100 steps)
- Senior threshold: age 50 (= 500 steps)
- Reproductive age: 10 <= age <= 60

## Gestation

- `gestation_time = 5` steps
- Pregnancy decrements by 1 each step
- Birth occurs when `gestation_remaining` reaches 0

## Weaning

- `weaning_age = 10` age units (= 100 steps)
- After weaning, offspring IDs are removed from mother

## Old-age mortality

- `old_age_mortality_start = 50` age units
- Risk rises linearly after this threshold

## Behavioral sink

- `behavioral_sink_min_duration = 30` steps (minimum time in sink)
- `behavioral_sink_recovery_duration = 100` steps (post-sink recovery)

## Consistency

All parameters that interact with age use age units (age_increment-scaled).
All parameters that interact with simulation steps use step units.
The `age_increment` parameter converts between them: 1 age unit = 1/age_increment steps.
