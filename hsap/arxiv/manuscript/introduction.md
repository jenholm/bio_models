# 1. Introduction

## 1.1 Population regulation through ecological pathways

Population regulation is conventionally modeled through four classes of mechanism: resource competition, predation, disease, and density-dependent effects on fecundity and mortality [@sinclair1989; @hixon2002population]. These frameworks—logistic growth, Lotka-Volterra predator-prey dynamics, SIR disease models, and their extensions—share a common assumption: population size is determined by external conditions acting on individuals through resource limitation and mortality risk. While these mechanisms are well-established and empirically supported, they do not fully account for a recurring pattern in field observations: populations sometimes stabilize at densities well below resource-imposed carrying capacities, particularly following predator removal or during post-irruption phases [@krebs1995impact; @krebs2001].

## 1.2 Behavioral regulation as an alternative pathway

One class of explanations invokes behavioral plasticity. Individuals adjust aggression, reproductive effort, and social organization in response to perceived environmental conditions, creating feedback loops between individual physiology and population dynamics. This behavioral regulation pathway is distinct from resource-based regulation: it operates through individual decision rules rather than external mortality or fecundity limitation.

Endocrine hormones—particularly testosterone, cortisol, and estrogen—are plausible mediators of such adjustments. Testosterone influences aggression and reproductive investment across vertebrate taxa [@wingfield1990; @sapolsky2005]. Cortisol mediates stress responses and can suppress reproductive function [@creel2013]. Estrogen regulates female reproductive effort and social behavior [@ellison2003]. The causal chain from environmental perception through hormonal state to behavioral output is well-documented in individual studies, but has rarely been incorporated into population-level models.

## 1.3 Behavioral sink theory and crowding effects

Calhoun [@calhoun1962] identified "behavioral sink" phenomena in overcrowded populations, where density-dependent behavioral deterioration—including reproductive suppression, aggression, and social withdrawal—could trap populations in unsustainable states even after density was reduced. The behavioral sink concept suggests that populations can enter self-reinforcing states of reproductive failure that persist beyond the ecological conditions that triggered them.

Subsequent work has extended this framework. Christian and Davis [@christian1964endocrines] proposed endocrine-mediated mechanisms linking population density to reproductive suppression through stress hormone pathways. These studies converge on a common hypothesis: that behavioral and endocrine feedbacks can generate population-level regulatory effects independent of resource competition.

## 1.4 Existing models and the integration gap

Several modeling frameworks have explored aspects of endocrine-mediated population regulation. Endocrine-based models of stress and dominance have been applied to primate social dynamics [@sapolsky2005], but typically at the group level rather than as population-level regulators. Agent-based models of behavioral ecology have incorporated hormonal state variables [@higham2013endocrinology], but usually without formal null model comparisons to test whether endocrine mechanisms add explanatory power beyond simpler alternatives.

The gap in the literature is a model that integrates: (1) individual-level endocrine feedback from environment to behavior; (2) sex-specific behavioral dynamics (male aggression, female competition); (3) a density-driven behavioral sink with recovery; and (4) rigorous null model comparison to test whether population trajectories alone can identify the endocrine mechanism.

## 1.5 HSAP contribution

We present HSAP (Hormonal-Social Adaptation Population model) as a falsifiable agent-based model that addresses this gap. HSAP proposes a specific causal chain: low external threat → male testosterone downshift → reduced male aggression, elevated female aggression → reduced fertility → population stabilization. The model is designed to be tested against its own predictions, not merely to demonstrate that endocrine feedbacks can produce interesting dynamics.

Our contributions are: (1) a computational framework linking individual endocrine state to population dynamics through behavioral feedbacks; (2) a demonstration that identical resource conditions produce qualitatively different population outcomes depending on behavioral and endocrine parameters; (3) an honest null model comparison showing that population trajectories alone are insufficient for mechanism identification; and (4) identification of the observable classes required for empirical testing.

**Scope and boundaries.** HSAP is a mammalian population model. It does not model human sexual orientation; non-reproductive sexual or social behavior is treated only as species-specific ethological behavior requiring explicit supporting data. The model is simulation-consistent, not proven; empirical validation requires paired endocrine and behavioral field measurements.

The paper is organized as follows: Section 2 describes the model. Section 3 presents the experimental design. Section 4 reports results. Section 5 discusses implications and limitations. Section 6 concludes.
