# Reviewer #1 — Hostile Review

**Summary**: This manuscript presents HSAP, an agent-based model linking endocrine state to population dynamics through behavioral feedbacks. The core claim is that endocrine-linked behavioral feedbacks can generate qualitatively distinct population outcomes under identical resource conditions. While the null model comparison is methodologically interesting, the paper suffers from significant boundary violations, insufficient hedging on species-generalization, and an inconsistent relationship between the paper's own caveats and its stronger claims.

---

## Criticism 1: Causation Claims Where Only Simulation Exists

### Where It Happens

**Abstract (line 12)**: The phrase "endocrine-linked behavioral feedbacks are sufficient to generate qualitatively distinct population dynamics under identical resource conditions" is correctly hedged with "under model assumptions," but the sentence immediately preceding it — "these ecological data are exploratory and non-causal" — is buried at the end of a very long abstract, and the strong causal framing of the earlier sentences (e.g., "populations stabilized at higher densities with lower male testosterone and aggression, consistent with relaxed competitive endocrine signaling") can be read as implying a causal mechanism.

**Section 5.1 (line 281)**: "HSAP shows that endocrine-linked behavioral feedbacks can generate qualitatively distinct population outcomes under identical resource conditions." The word "generate" is ambiguous — does it mean "are sufficient to produce in simulation" or "produce in reality"? This needs to be explicit.

**Section 5.5 (lines 315-323)**: The "Empirical Predictions" are presented as if HSAP has been validated enough to make predictions. But HSAP has never been compared to real data. A simulation model that has not been empirically tested generates *hypotheses*, not *predictions*. The word "prediction" implies the model has earned the right to tell us what to look for.

### Suggested Fixes

- Replace "generate" in 5.1 with "produce in simulation" or "generate under model assumptions."
- Rename Section 5.5 from "Empirical Predictions" to "Testable Hypotheses" or "Simulation-Derived Predictions."
- Add an explicit sentence in the Abstract: "These are simulation results under specified model assumptions, not empirical findings."
- In the Abstract, move the non-causal hedge earlier — it should not be the final clause of a 200-word sentence.

---

## Criticism 2: Endocrine Mechanisms Presented as Established Rather Than Hypothetical

### Where It Happens

**Section 2.3 (lines 69-83)**: The endocrine update equations are presented without any citation to empirical literature supporting the specific functional forms. For example, Equation 1 (line 69) uses fixed linear coefficients (0.3 for rank, 0.4 for mating_drive, -0.4 for predator_pressure) as if these are known relationships. They are not. These are modeler-chosen values. The text says "The term -0.4 * (1 - predator_pressure) is the critical endocrine feedback" (line 71) — this language presents the equation as a discovered mechanism, not a hypothesized one.

**Section 1.1 (line 18)**: "field observations often show complex behavioral and endocrine responses that alter population trajectories" — this implies the endocrine-population link is empirically observed, but no specific field studies are cited for this claim.

**Section 5.3 (lines 295-296)**: "HSAP generates testable predictions in the joint space of population size, endocrine state, and behavior." This again presents the model as having reached the prediction stage, when it has not been empirically tested.

### Suggested Fixes

- In Section 2.3, add a sentence: "The functional forms and coefficients in the endocrine update equations are hypothesized and illustrative; they are not empirically calibrated to any specific species."
- In Section 1.1, either cite specific field studies or weaken the claim to "field observations sometimes suggest..."
- Throughout, replace "HSAP shows" with "HSAP simulates" or "HSAP demonstrates in simulation."

---

## Criticism 3: Species-Generalizations Are Not Justified

### Where It Happens

**Section 5.5 (lines 315-323)**: The predictions are stated in species-agnostic terms ("Male testosterone should decrease following predator removal") without specifying which species, what population, or what ecological context. This is a universal claim about endocrine ecology disguised as a testable prediction.

**Section 1.1 (line 18)**: "When predator populations are removed or suppressed, prey populations initially increase but sometimes stabilize at lower-than-expected densities" — this is stated as a general ecological law, but the phenomenon it describes is specific to certain predator-prey systems (e.g., urchin barrens after sea otter removal). It is not universal.

**Section 5.6 (lines 327-329)**: The external proxy section discusses human U.S. data (NHANES, UCR arrest statistics) in the context of a model that is ostensibly about non-human population ecology. This creates a species-generalization problem: the model is parameterized for unnamed species, but the empirical evidence cited is human.

### Suggested Fixes

- In Section 5.5, specify: "For species where testosterone mediates competitive aggression (e.g., many ungulates, primates), HSAP predicts..."
- In Section 1.1, cite specific field examples (e.g., Estes et al. 1998 for sea otter–kelp systems) rather than stating the phenomenon as universal.
- In Section 5.6, explicitly state that the human proxy data are used only to illustrate the *class* of observables needed, not to validate HSAP for humans. The sentence on line 329 does this partially ("their main value is to show how HSAP-like mechanisms could be tested") but the preceding sentences read as if human data are being used as evidence for the model.

---

## Criticism 4: Human Implications Are Not Explicitly Avoided

### Where It Happens

**Line 32**: "HSAP does not model human sexual orientation; non-reproductive sexual or social behavior is treated only as species-specific ethological behavior." This sentence appears in Section 1.4 (Scope and contributions) and Section 5.4 (Limitations), but it is *not* in the Abstract, Introduction, or Conclusion.

**Section 5.6 (lines 327-329)**: The entire subsection discusses human UCR arrest data and NHANES hormone panels as "external proxy evidence." While the text is careful to say these are "ecological and confounded," the very inclusion of human data in a paper about non-human population ecology creates an implicit bridge that the paper's own boundary language tries to prevent.

**Section 3.5 (lines 211-223)**: The external empirical proxy design section discusses FBI UCR data, NIBRS, OJJDP juvenile arrest data, and NCVS victimization data — all human datasets — in the context of a model that claims not to model humans.

### Suggested Fixes

- Add the boundary sentence ("HSAP does not model human sexual orientation") to the Abstract and Conclusion.
- In Section 5.6, begin with: "The following human datasets are used exclusively as illustrations of observable classes, not as evidence for HSAP. HSAP does not model human populations."
- Consider whether Section 3.5 and 5.6 belong in this paper at all, or whether they should be a separate methods paper on observable requirements for endocrine-ecological models.

---

## Criticism 5: The README Boundary Language Does Not Fully Migrate Into the Paper

### Where It Happens

The claim_discipline.md document (line 14) specifies that the paper should use "simulation-consistent" rather than "proves/validates/confirms." Checking the manuscript:

- **Abstract (line 12)**: Uses "consistent with" — acceptable.
- **Section 4.1 (line 233)**: "directionally consistent with relaxed competitive endocrine signaling" — acceptable.
- **Section 5.1 (line 281)**: "simulation-consistent with the hypothesis that endocrine state mediates population regulation" — acceptable.
- **Section 5.3 (line 295)**: "HSAP generates testable predictions" — NOT acceptable. Should be "testable hypotheses."
- **Section 5.5 (lines 315-323)**: Uses "should" throughout ("Male testosterone should decrease") — this is prediction language, not hypothesis language. Should be "would be expected to" or "HSAP hypothesizes that."
- **Section 6 (line 337)**: "HSAP is simulation-consistent, not proven" — acceptable.

The boundary language is mostly enforced in the Results and Discussion sections but breaks down in the empirical predictions section and in the treatment of external proxy data.

### Suggested Fixes

- Systematically replace "prediction" with "hypothesis" in Sections 5.5 and 5.6.
- Replace "should" with "would be expected to under model assumptions" in Section 5.5.
- Add "simulation-consistent" to the Abstract's final sentence.
- Ensure the claim_discipline.md guardrails are applied uniformly, not just in the sections that are most likely to be scrutinized.

---

## Overall Assessment

The paper's null model comparison is genuinely interesting and the honest treatment of non-identifiability is a strength. However, the manuscript oscillates between careful hedging and casual causal language, particularly in the empirical predictions and external proxy sections. The species-generalization problem is serious: a model parameterized for unnamed species should not use human data as its primary external evidence without much stronger disclaimers. The boundary between "illustrative proxy" and "evidence" is being blurred in ways that could mislead readers.

**Recommendation**: Major revision. The core simulation results are sound, but the claim discipline needs to be tightened across the entire manuscript, and the relationship between the model and human data needs explicit resolution.
