# Student worksheet: what predicts, what changes?

Name: ____________________   Date: ____________________

Assume a fully observed, unconfounded chain X → M → Y. Let M=0.6X+eM and Y=0.6M+eY; X, eM, and eY are mutually independent with mean zero. Our ideal predictor is f(X,M)=0.6M. The displayed individual has x=1, eM=0.2, hence m=0.8.

1. Before opening the lab: once M is known, does X add information about Y? Is X still a cause of Y? Explain both answers.
2. The model-interventional coalition game replaces missing inputs from their marginal background without propagating changes along arrows. Compute v(∅), v({X}), v({M}), v({X,M}). Use φX=½[v(X)−v(∅)]+½[v(X,M)−v(M)]. Compute φM and check efficiency.
3. Now use the structural game, propagating do(X=x) into M. Which coalition value changes? Recompute both Shapley values.
4. Calculate E[Y|do(X=1)]−E[Y|do(X=0)]. Is it the same as φX? Why should these quantities be labeled separately?
5. Set a=0, then a=−0.6. Predict what changes before checking the browser lab. Does a negative coefficient reverse the causal arrow?
6. Replace the chain with the direct mechanism Y=X²+eY. Compare interventions −1→1 and 0→2. What does this say about “direct causes tend to be linear” and the need to specify an intervention range?
7. Two linear-Gaussian models have the same observed covariance: A has X→Y with coefficient 0.6; B has Y→X with coefficient 0.6. Run lab.py and explain why observational agreement does not identify the intervention on X.
8. Along a single path with every coefficient 0.6, compute the depth-1 and depth-5 effects. Can you infer the most important intervention from depth alone in a graph with parallel paths?
9. Paper-reading exit ticket: the renal structural prototype has τ=0.794 in one configuration. Name two additional checks needed before claiming general superiority. Does a scripted reviewer count as human expert validation?

Optional discussion: how would a noisy mediator change the ideal predictor? Why would conditional SHAP be a different game from the two demonstrated here?
