# Causal SHAP in the classroom

A 50-minute lesson or 90-minute lab for learners familiar with regression,
conditional expectation and causal graphs.

## Use the lesson

Download and extract the kit, then open `index.html` in a browser. It runs
offline. From a repository download, use `docs/classroom/index.html`.

- [Worksheet](worksheet.md): questions to work through before revealing answers.
- [Educator guide](educator-guide.md): session plan, derivations and answer key.
- [Python lab](lab.py): exact calculations using Python 3.10 or newer, with no additional packages.

```bash
python lab.py
python lab.py --check
```

The lesson distinguishes predictive credit from an intervention contrast,
explores screening-off, and shows why a direct cause need not have a linear
response. Its two-feature model is an exact teaching example, separate from
the renal simulations and their attribution methods.

## Extend the lesson

The [technical note](https://github.com/ahhatype/causal-shap-spaceflight-renal-stones/blob/main/docs/technical/path-length-and-response-shape.md)
develops the path-length equations, detection assumptions and nonlinear
examples, with [BibTeX references](https://github.com/ahhatype/causal-shap-spaceflight-renal-stones/blob/main/docs/references/technical-companion.bib).
The [workflow and evidence map](https://github.com/ahhatype/causal-shap-spaceflight-renal-stones/blob/main/docs/playbook/central-workflow.md)
connects the lesson to the research results.

To build the standalone kit from the repository root:

```bash
python analysis/package_classroom.py
```

This creates `dist/causal-shap-classroom.zip`. The kit is a teaching prototype;
classroom evaluation is pending.
