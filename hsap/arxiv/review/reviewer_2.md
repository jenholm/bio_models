# Reviewer #2 — Hostile Review

**Summary**: This manuscript presents HSAP, an agent-based model with endocrine feedbacks, and compares it against 11 null models. The null model framework is the paper's strongest contribution, but the mathematical rigor of the model equations, the identifiability of parameters, the strength of the null models, and the statistical methodology all require significant attention before this paper is publishable.

---

## Criticism 1: Mathematical Rigor of Equations

### Where It Happens

**Equation 1 (line 69)**: The male testosterone update is a linear sum of five terms with arbitrary coefficients:

$$T_{male} = T_{base} + 0.3 \cdot rank + 0.4 \cdot mating\_drive - 0.3 \cdot density - 0.4 \cdot (1 - predator\_pressure) - 0.2 \cdot (1 - health)$$

There is no derivation, no justification for linearity, no discussion of whether these terms should interact (e.g., is the effect of rank on testosterone independent of density?). The coefficients sum to potentially large excursions: if rank=1, mating_drive=1, density=0, predator_pressure=0, health=1, then T_male = 1.0 + 0.3 + 0.4 - 0 - 0.4 - 0 = 1.3, which exceeds the clamping range [0, 1]. The clamping at [0, 1] is applied *after* computation (line 40), which means the model frequently operates at boundary conditions — a serious problem for any linear model that can exceed its domain.

**Equation 3 (line 79)**: The cortisol equation:

$$C = 0.5 + 0.1 \cdot density - 0.3 \cdot rank + 0.5 \cdot (1 - health) + 0.2 \cdot predator\_pressure + 0.3 \cdot resource\_scarcity$$

The coefficients sum to a maximum of 0.5 + 0.1 + 0.3 + 0.5 + 0.2 + 0.3 = 1.9 when all stressors are maximized and rank is zero. This is nearly four times the intercept. The model will spend most of its time at the cortisol ceiling (clamped to 1.0), making the equation effectively a threshold function rather than a continuous regulator. This undermines the claim that cortisol provides graded endocrine feedback.

**Equation 4 (line 83)**: Estrogen is defined as:

$$E = 1.0 - 0.3 \cdot C$$

This is the simplest possible linear suppression. It implies that cortisol only ever reduces estrogen, never increases it, and that the relationship is perfectly linear with no threshold, saturation, or individual variation. No biological citation is provided for this functional form.

**Behavioral output (lines 89-93)**: Aggression is defined as "base = T * 0.5 + C * 0.2, with sex-specific additions." The sex-specific additions are described only in words, not equations. This makes the model impossible to reproduce from the paper alone. The fertility modification (line 90) mentions "density-dependent reproductive restraint (activates above density 0.7)" but does not specify the functional form — is it a step function, a sigmoid, a linear ramp?

### Suggested Fixes

- Provide a complete equation table in Supplement C with all coefficients, clamping rules, and interaction terms.
- Derive or justify the linear functional forms. If they are chosen for simplicity, state this explicitly and discuss what nonlinear alternatives might change.
- Specify the fertility density-restraint function mathematically (e.g., "fertility is multiplicatively reduced by `max(0, (density - 0.7) / 0.3)` for densities above 0.7").
- Discuss the clamping problem: how often do agents hit the [0, 1] ceiling? If it is frequent, the linear equations are effectively threshold models and should be analyzed as such.

---

## Criticism 2: Parameter Identifiability

### Where It Happens

**Throughout Section 2**: The model has at least 15 free parameters in the endocrine update equations alone (5 coefficients in Equation 1, 3 in Equation 2, 5 in Equation 3, 1 in Equation 4, plus the intercepts). The behavioral output adds additional free parameters (the 0.5 and 0.2 weights in aggression, the 0.5 and 0.3 weights in mating drive). The sink mechanism adds 3 more (on-threshold 0.75, off-threshold 0.50, recovery duration 100). The mortality model (lines 107-120) adds at least 8 more.

The paper does not address whether these parameters are jointly identifiable. Given the null model result that 7 of 11 null models cannot distinguish HSAP from simpler alternatives on population data, it is unclear whether HSAP's parameters can be identified even with endocrine and behavioral observables. The ablation analysis (Section 4.5) shows which components matter, but not whether the specific coefficient values within each component can be recovered from data.

**Section 4.6 (lines 273-275)**: The factorial sensitivity analysis identifies space constraint as the dominant regulator but does not perform formal sensitivity analysis (e.g., Sobol indices, Morris screening). Figure 6 caption (line 353) mentions "Sobol sensitivity analysis tornado plot" but the main text does not describe the Sobol analysis methodology, sample size, or convergence criteria.

### Suggested Fixes

- Add a parameter identifiability analysis: given observed population trajectories AND endocrine observables, which parameters can be recovered? Use profile likelihood or Fisher information matrix analysis.
- Report the Sobol analysis in the main text, not just the figure caption. Specify the number of model evaluations, the sampling strategy, and the confidence intervals on the sensitivity indices.
- Discuss the practical identifiability problem: even if all 15+ endocrine parameters are theoretically identifiable, are they practically identifiable given realistic data availability?

---

## Criticism 3: Null Model Strength

### Where It Happens

**Section 3.3 (lines 181-197)**: The 11 null models are described only by name and mechanism, with no equations or parameter specifications. How were they fit to HSAP's population trajectory? Were they fit jointly or individually? What optimization algorithm was used? Were the same initial conditions used?

**Section 4.4 (lines 255-259)**: The criterion for "indistinguishable" is an A/B MSE ratio < 1.5. This is an arbitrary threshold with no statistical justification. Why not 1.2? Why not 2.0? The paper does not report whether the MSE differences are statistically significant — it reports raw MSE values (e.g., "MSEs 25,000-86,000 compared to HSAP ablation MSEs of 70-2,458") without confidence intervals or significance tests.

**Critical gap**: The null models are fit to *population trajectories alone*. But the paper's own argument is that population trajectories are insufficient. This means the null model comparison is testing a straw man — of course simpler models fit population trajectories well; that is the point. The real test should be: can null models fit the joint (population, endocrine, behavior) trajectory? If they can, HSAP is not distinguishable even with the richer data the paper advocates for.

**N5_random_hormone (line 191)**: This null model has "random hormone levels (no environmental coupling)." This is not a realistic alternative — no real organism has environmentally uncoupled hormones. Including it inflates the count of "indistinguishable" models with a weak competitor.

**N8_random_behavior (line 193)**: Similarly, "random behavioral decisions" is not a plausible null for any real organism. Including it is a straw man.

### Suggested Fixes

- Report full equations and fitting procedures for all 11 null models in a supplement.
- Justify the MSE ratio threshold of 1.5 with a statistical argument (e.g., power analysis, likelihood ratio test equivalent).
- Report confidence intervals on MSE estimates and whether the indistinguishability holds under bootstrap resampling.
- **Critically**: Apply the null model comparison to the joint (population + endocrine + behavior) trajectory, not just population alone. If null models still cannot distinguish HSAP in the joint space, the paper's argument is strengthened. If they can, the paper's main result is weakened.
- Remove or demote N5 (random hormone) and N8 (random behavior) from the primary comparison, as they are not biologically plausible alternatives. Report them as upper-bound nulls in a supplement.

---

## Criticism 4: Sensitivity Analysis Methodology

### Where It Happens

**Section 4.6 (lines 273-275)**: The factorial analysis is presented as the sensitivity analysis, but a full factorial design with 3×3×3×2 = 54 scenarios is not a sensitivity analysis — it is a parameter sweep. True sensitivity analysis quantifies how much each parameter contributes to output variance, including interactions.

**Figure 6 (line 353)**: The caption references "Sobol sensitivity analysis tornado plot showing total-order indices (ST)" but the main text never describes the Sobol analysis. How were the Sobol indices computed? What was the base sample size? Were first-order and total-order indices both computed? Were interaction effects significant?

**Section 4.6 (line 273)**: "space constraint is the dominant population regulator" — this conclusion comes from the factorial sweep, not from formal sensitivity analysis. The factorial sweep shows that populations are lower under high space constraint, but it does not quantify what fraction of output variance is explained by space constraint versus its interactions with other parameters.

### Suggested Fixes

- Move the Sobol analysis from the figure caption to the main text. Report:
  - Sample size (number of model evaluations)
  - First-order indices (S1) and total-order indices (ST) for all parameters
  - Confidence intervals on indices
  - Which interactions are significant (S2 or higher)
- Distinguish between the factorial parameter sweep (which shows *direction* of effects) and the Sobol analysis (which shows *variance contribution*). These are different questions.
- If the Sobol analysis was not actually performed, remove the figure caption reference and perform it.

---

## Criticism 5: Statistical Claims (Cohen d, Confidence Intervals)

### Where It Happens

**Abstract (line 12)**: "Cohen d=3.29, non-overlapping 95% CIs" is presented for the A vs. B male testosterone comparison. This is an enormous effect size (Cohen d > 0.8 is "large" by convention). But the comparison is between two simulation scenarios with 50 seeds each, where the means differ by 0.008 (0.994 vs. 0.986) on a [0,1] scale. The large Cohen d reflects the extremely small within-scenario variance (CI widths of ~0.002), which is an artifact of running many seeds of the same deterministic model with random initialization. This is not the same as measuring variance in a real population.

**Section 4.1 (lines 231-237)**: All confidence intervals are reported as "95% CI" without specifying the method. Are these bootstrap CIs? Normal-theory CIs? The figure captions mention "95% bootstrap CIs" (Figure 3, line 345), but the text does not specify. For simulation studies with 50 seeds, bootstrap CIs on the mean are extremely narrow because the seed-to-seed variance is small relative to the number of seeds.

**Section 4.3 (line 251)**: "Extinction occurred in 14% of seeds (95% CI=[6%, 24%])" — this CI is on a binomial proportion (7/50). The method is not specified. Is this Wilson score, Clopper-Pearson, or normal approximation? For n=50, these methods give slightly different intervals.

**Section 4.2 (line 241)**: "space constraint alone, with identical resources, can suppress population to 31% of the resource-matched uncrowded condition" — this is stated as a factual comparison of means, but the two scenarios have different random seeds. The 31% figure is a comparison of scenario means, not a within-seed comparison.

### Suggested Fixes

- Specify the CI method in the text (e.g., "95% bootstrap CIs computed from 10,000 resamples of seed means").
- Acknowledge that the large Cohen d reflects simulation precision, not biological effect size. Add a sentence: "The large Cohen d reflects the small seed-to-seed variance in simulation; in real populations, measurement error and individual variation would substantially increase variance and reduce effect sizes."
- For the binomial extinction CI, specify the method (e.g., "Clopper-Pearson exact CI").
- Consider reporting effect sizes relative to biologically meaningful variance, not just simulation variance. For example: "If real-population testosterone variance is 10× the simulation seed variance, the effective Cohen d would be ~0.33."

---

## Criticism 6: The Ablation Analysis Is Circular

### Where It Happens

**Section 4.5 (lines 263-269)**: The ablation analysis removes one HSAP component at a time and measures the increase in MSE. But the MSE is computed against HSAP's own population trajectory, not against real data. This means the ablation shows which components contribute to HSAP's *internal* dynamics, not which components are empirically necessary. The sentence "Removing the male testosterone downshift channel increased B's population MSE from 73 to 565" (line 265) tells us that the testosterone channel matters *for HSAP's behavior*, not that it matters *in nature*.

**Line 269**: "Removing sink recovery produced MSE=0 across all scenarios, because without the sink mechanism, the behavioral sink never engages and the recovery phase never begins. This is consistent with the internal consistency of the model." The phrase "internal consistency" is doing a lot of work here. A model that is internally consistent is not necessarily externally valid.

### Suggested Fixes

- Rename the section from "Ablation Results" to "Internal Sensitivity Analysis" or "Component Contribution Analysis" to be transparent about what is being measured.
- Add a sentence: "This ablation quantifies each component's contribution to HSAP's internal dynamics; empirical validation requires field data."
- If possible, also report ablation results against a synthetic "ground truth" trajectory generated by a known mechanism, to show whether ablation can distinguish HSAP from known alternatives.

---

## Overall Assessment

The null model framework is the paper's best feature, but it is undermined by insufficient methodological detail (no null model equations, arbitrary MSE threshold, no joint-space comparison) and by statistical claims that overstate simulation precision as biological effect size. The endocrine equations are under-specified and the parameter identifiability problem is unaddressed. The Sobol sensitivity analysis is referenced but not reported in the main text.

**Recommendation**: Major revision. The core idea is sound, but the mathematical and statistical methodology needs substantial strengthening before the results can be trusted. The paper should: (1) provide complete equations for all models; (2) justify the MSE threshold; (3) report the Sobol analysis properly; (4) address parameter identifiability; (5) contextualize effect sizes relative to biological variance.
