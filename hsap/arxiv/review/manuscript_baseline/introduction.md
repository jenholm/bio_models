# 1. Introduction

## 1.1 Ecological release and the predator-removal paradox

When predator populations are removed or suppressed, prey populations initially increase but sometimes stabilize at lower-than-expected densities [@getz1974]. Traditional models — logistic growth, Lotka-Volterra predator-prey dynamics, and their extensions — predict simple density-dependent regulation near carrying capacity. However, field observations in post-predator-removal systems frequently show complex behavioral and endocrine responses that alter population trajectories in ways not captured by resource-based models alone. This discrepancy suggests that additional regulatory mechanisms, operating through behavioral and physiological pathways, may contribute to population stabilization.

<!-- TODO: Add specific field examples of predator-removal populations stabilizing below K -->
<!-- TODO: Need citation for ecological release hypothesis beyond Getz 1974 -->

## 1.2 Population regulation: beyond density dependence

Standard density-dependent models assume that population size is regulated primarily through resource competition affecting mortality and fecundity. While these mechanisms are well-established, they do not account for the observation that populations sometimes stabilize at densities well below resource-imposed carrying capacities. This pattern is particularly evident in systems where predator removal has not produced the expected population explosion, or where populations stabilize after an initial irruption phase.

One class of explanations invokes behavioral plasticity: individuals adjust their aggression, reproductive effort, and social organization in response to perceived environmental conditions, creating feedback loops between individual physiology and population dynamics. Endocrine hormones — particularly testosterone, cortisol, and estrogen — are plausible mediators of such adjustments, given their known effects on aggression, reproductive effort, and stress responses across vertebrate taxa [@sapolsky2005; @creel2013; @ellison2003].

<!-- TODO: Need citation for behavioral plasticity in post-predator-removal systems -->

## 1.3 Behavioral sink theory and crowding effects

Calhoun [@calhoun1962] identified "behavioral sink" phenomena in overcrowded populations, where density-dependent behavioral deterioration — including reproductive suppression, aggression, and withdrawal — could trap populations in unsustainable states even after density was reduced. This concept has been influential in conservation biology and urban ecology, but formal mathematical treatments of the behavioral sink remain limited.

Recent theoretical work has proposed that similar mechanisms may operate in human and primate populations. Wrangham [@wrangham2019] proposed self-domestication as a mechanism for reduced reactive aggression, with endocrine mediation playing a central role. Boehm [@boehm1999] documented egalitarian reverse-dominance hierarchies in hunter-gatherer societies, suggesting that social mechanisms can regulate aggression and reproduction independently of resource competition. These perspectives converge on a common hypothesis: that behavioral and endocrine feedbacks can generate population-level regulatory effects.

<!-- TODO: Need citation connecting Calhoun-style behavioral sinks to endocrine mechanisms -->
<!-- TODO: Verify Wrangham self-domestication framing is appropriate for animal model -->

## 1.4 Existing mathematical models

Several modeling frameworks have explored aspects of endocrine-mediated population regulation. Endocrine-based models of stress and dominance [@sapolsky2005] have been applied to primate social dynamics, but typically at the group level rather than as population-level regulators. Agent-based models of behavioral ecology have incorporated hormonal state variables, but usually without formal null model comparisons to test whether endocrine mechanisms add explanatory power beyond simpler alternatives.

The gap in the literature is a model that integrates: (1) individual-level endocrine feedback from environment to behavior; (2) sex-specific behavioral dynamics (male aggression, female competition); (3) a density-driven behavioral sink with recovery; and (4) rigorous null model comparison to test whether population trajectories alone can identify the endocrine mechanism.

<!-- TODO: Need specific citations for existing ABMs with endocrine state variables -->

## 1.5 HSAP contribution

We present HSAP (Hormonal-Social Adaptation Population model) as a falsifiable agent-based model that addresses this gap. HSAP proposes a specific causal chain: low external threat → male testosterone downshift → reduced male aggression, elevated female aggression → reduced fertility → population stabilization. The model is designed to be tested against its own predictions, not merely to demonstrate that endocrine feedbacks can produce interesting dynamics.

Our contributions are: (1) a computational framework linking individual endocrine state to population dynamics through behavioral feedbacks; (2) a demonstration that identical resource conditions produce qualitatively different population outcomes depending on behavioral and endocrine parameters; (3) an honest null model comparison showing that population trajectories alone are insufficient for mechanism identification; and (4) identification of the observable classes required for empirical testing.

**Scope and boundaries.** HSAP is a mammalian population model. It does not model human sexual orientation; non-reproductive sexual or social behavior is treated only as species-specific ethological behavior requiring explicit supporting data. The model is simulation-consistent, not proven; empirical validation requires paired endocrine and behavioral field measurements.

The paper is organized as follows: Section 2 describes the model. Section 3 presents the experimental design. Section 4 reports results. Section 5 discusses implications and limitations. Section 6 concludes.
