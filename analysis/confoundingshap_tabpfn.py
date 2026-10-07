"""TabPFN-2.5 comparison on the frozen 51-node renal simulation.

Uses shapiq 1.7.0's S-learner with an explicitly versioned model factory.
Evaluates its signed global game both in training and held-out populations.
Predictions use all actual training/evaluation rows in fixed order and float32.
This is a documented adaptation, not an unmodified upstream benchmark.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import time

os.environ.setdefault('TABPFN_NO_BROWSER', '1')
os.environ.setdefault('TABPFN_DISABLE_TELEMETRY', '1')

import numpy as np
import pandas as pd
from scipy.special import expit
import torch
from tabpfn import TabPFNRegressor
from tabpfn.constants import ModelVersion
from shapiq_games.benchmark.causal_xai import base as upstream

import confoundingshap_comparison as reference

ROOT = reference.ROOT


@contextmanager
def versioned_factory(seed):
    """Scope the only upstream adaptation; never modify installed files."""
    original = upstream._make_tabpfn

    def factory(device, n_estimators=1):
        return TabPFNRegressor.create_default_for_version(
            ModelVersion.V2_5, device=device, n_estimators=n_estimators,
            n_jobs=1, random_state=seed,
            inference_precision=torch.float32,
            inference_config=upstream._TABPFN_INFERENCE_CONFIG)

    upstream._make_tabpfn = factory
    try:
        yield
    finally:
        upstream._make_tabpfn = original


def state_weights(frame, states):
    index = pd.MultiIndex.from_arrays(states.T, names=reference.FEATURES)
    counts = frame.groupby(reference.FEATURES).size().reindex(index, fill_value=0).to_numpy()
    return counts / counts.sum()


def summarize_predictions(train, evaluation, mu1, mu0, seed, population_filter=None):
    """Same fitted coalition functions, two empirical standardization populations."""
    states = reference.masks(4).astype(int)
    crude = float(train.loc[train.thiazides == 1, 'nephrolithiasis'].mean()
                  - train.loc[train.thiazides == 0, 'nephrolithiasis'].mean())
    contrasts = mu1 - mu0
    contrasts[0] = crude  # Upstream empty coalition is the raw training contrast.
    rows, summaries, games = [], [], []
    for population, frame in [('training', train), ('held_out', evaluation)]:
        if population_filter is not None and population != population_filter:
            continue
        weights = state_weights(frame, states)
        adjusted = float(weights @ contrasts[-1])
        game = adjusted - contrasts @ weights
        phi = reference.package_shapley(game)
        pred_phi = reference.conditional_shap_mean_abs(states, weights, mu0[-1])
        cate_phi = reference.conditional_shap_mean_abs(states, weights, contrasts[-1])
        eta = -2.35 + .60*frame.individual_factors + .60*frame.mineralized_renal_material
        dgp = float((expit(eta-.252*(1-frame.thiazides))
                     - expit(eta+.252*frame.thiazides)).mean())
        summaries.append(dict(seed=seed, population=population, n_train=len(train),
                              n_evaluation=len(frame), crude_train_difference=crude,
                              plugin_full_adjusted_ate=adjusted, dgp_ate=dgp,
                              ate_error=adjusted-dgp, attribution_sum=float(phi.sum()),
                              empty_value=float(game[0]), full_value=float(game[-1]),
                              prediction_min=float(min(mu1.min(), mu0.min())),
                              prediction_max=float(max(mu1.max(), mu0.max()))))
        for j, feature in enumerate(reference.FEATURES):
            rows.append(dict(seed=seed, population=population, feature=feature,
                             confounding_signed=phi[j],
                             control_outcome_conditional_shap_mean_abs=pred_phi[j],
                             cate_conditional_shap_mean_abs=cate_phi[j]))
        for k, subset in enumerate(reference.masks(4)):
            games.append(dict(seed=seed, population=population, mask=k,
                              coalition=';'.join(np.array(reference.FEATURES)[subset]) or 'EMPTY',
                              adjusted_contrast=float(contrasts[k] @ weights), value=float(game[k])))
    return rows, summaries, games


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'analysis/output/confoundingshap_tabpfn')
    parser.add_argument('--seeds', type=int, nargs='+', default=list(range(20260930, 20260935)))
    parser.add_argument('--threads', type=int, default=2)
    parser.add_argument('--device', choices=['cpu', 'cuda'], default='cuda')
    args = parser.parse_args()
    torch.set_num_threads(args.threads)
    if args.device == 'cuda' and not torch.cuda.is_available():
        raise RuntimeError('CUDA unavailable; install GPU-enabled PyTorch or explicitly select --device cpu.')
    reference.validate_renal_design()
    data = pd.read_csv(reference.DATA)
    assert len(data) == 10000
    args.output.mkdir(parents=True, exist_ok=True)
    versions = {p: importlib.metadata.version(p) for p in
                ['shapiq', 'tabpfn', 'torch', 'scikit-learn', 'numpy', 'pandas']}
    assert versions['shapiq'] == '1.7.0' and versions['tabpfn'] == '9.0.0'
    baseline_path = ROOT/'analysis/output/confoundingshap_pilot/renal_attributions.csv'
    provenance = dict(input_sha256=hashlib.sha256(reference.DATA.read_bytes()).hexdigest(),
                      reference_script_sha256=hashlib.sha256(Path(reference.__file__).read_bytes()).hexdigest(),
                      baseline_sha256=hashlib.sha256(baseline_path.read_bytes()).hexdigest(),
                      script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      upstream_source_sha256=hashlib.sha256(Path(upstream.__file__).read_bytes()).hexdigest(),
                      model_version='2.5', n_estimators=1, versions=versions, device=args.device,
                      inference_precision='float32', prediction_query='all actual rows, separate populations and arms',
                      outcome_transform='REGRESSION_Y_PREPROCESS_TRANSFORMS=(None,)')
    manifest = args.output/'metadata.json'
    if manifest.exists():
        old = json.loads(manifest.read_text())
        if old['provenance'] != provenance:
            raise ValueError('Existing checkpoint provenance differs; choose a new output directory.')
    metadata = dict(provenance=provenance, seeds=args.seeds, status='running',
                    source='51-node/75-edge clean NASA-topology simulation; frozen 10,000 rows',
                    treatment='thiazides', outcome='nephrolithiasis', covariates=reference.FEATURES,
                    adaptation='Scoped upstream model factory pins TabPFN 2.5 and random_state. '
                    'Upstream S-learner fits all 6,000 training rows per nonempty coalition. '
                    'Predict all actual training and held-out rows separately, then aggregate within each of 16 binary states. '
                    'Explicit float32 inference; no query compression.',
                    endpoint='Full-set CATE anchor reuses the full S-learner, so full residual is zero by construction; '
                    'upstream can have a nonzero endpoint with an independently estimated CATE anchor.',
                    uncertainty='Five splits of one frozen dataset, not confidence intervals or independent DGP replications.',
                    finite_sample_target='Training crude contrast minus evaluation-standardized adjusted contrast includes '
                    'nuisance error and population-composition variation, not solely true confounding.',
                    limitations=['No renal oracle for confounding allocation; DGP ATE reference only.',
                                 'Conditional mean-absolute prediction/CATE SHAP have different targets from signed bias attribution.',
                                 'No LumaWarp detector or 14-node comparison.',
                                 'No full replication of the paper benchmark; one estimator, version-pinned adaptation.'])
    manifest.write_text(json.dumps(metadata, indent=2)+'\n')
    started = time.perf_counter()
    all_rows, all_summaries, all_games = [], [], []
    states = reference.masks(4).astype(int)
    for seed in args.seeds:
        order = np.random.default_rng(seed).permutation(len(data))
        train, evaluation = data.iloc[order[:6000]], data.iloc[order[6000:]]
        assert len(train.groupby([*reference.FEATURES, 'thiazides'])) == 32
        assert len(evaluation.groupby(reference.FEATURES)) == 16
        X, A, Y = (train[reference.FEATURES].to_numpy(dtype=float),
                   train.thiazides.to_numpy(dtype=float), train.nephrolithiasis.to_numpy(dtype=float))
        population_frames = {'training': train, 'held_out': evaluation}
        arm_predictions = {pop: [np.zeros((16,16)), np.zeros((16,16))] for pop in population_frames}
        for mu1, mu0 in arm_predictions.values():
            mu1[0], mu0[0] = Y[A == 1].mean(), Y[A == 0].mean()
        for k, subset in enumerate(reference.masks(4)):
            if k == 0:
                continue
            checkpoint = args.output/f'predictions_{seed}_{k:02d}.json'
            if checkpoint.exists():
                record = json.loads(checkpoint.read_text())
            else:
                tick = time.perf_counter()
                print(f'Seed {seed}; coalition {k}/15 ({int(subset.sum())} covariates)', flush=True)
                with versioned_factory(seed):
                    predict1, predict0 = upstream._fit_s_learner(X[:, subset], A, Y, device=args.device, n_estimators=1)
                    record = dict(seed=seed, mask=k, populations={})
                    for pop, frame in population_frames.items():
                        query = frame[reference.FEATURES].to_numpy(dtype=float)
                        p1, p0 = predict1(query[:,subset]), predict0(query[:,subset])
                        assert np.isfinite(p1).all() and np.isfinite(p0).all()
                        grouped, spreads = [], []
                        for predictions in [p1,p0]:
                            groups = [predictions[np.all(query == state, axis=1)] for state in states]
                            grouped.append(np.array([g.mean() for g in groups]))
                            spreads.append(max(float(np.ptp(g)) for g in groups))
                            np.testing.assert_allclose(state_weights(frame, states) @ grouped[-1], predictions.mean(), atol=1e-12, rtol=0)
                        record['populations'][pop] = dict(mu1=grouped[0].tolist(), mu0=grouped[1].tolist(),
                            maximum_within_state_spread=max(spreads),
                            actual_query_rows=len(frame), raw_mean1=float(p1.mean()), raw_mean0=float(p0.mean()))
                record['elapsed_seconds'] = time.perf_counter()-tick
                checkpoint.write_text(json.dumps(record, indent=2, allow_nan=False)+'\n')
                print(f'  completed in {record["elapsed_seconds"]:.1f}s', flush=True)
                del predict1, predict0
            assert record['seed'] == seed and record['mask'] == k
            for pop, (mu1,mu0) in arm_predictions.items():
                mu1[k], mu0[k] = record['populations'][pop]['mu1'], record['populations'][pop]['mu0']
                assert np.isfinite(mu1[k]).all() and np.isfinite(mu0[k]).all()
        rows, summaries, games = [], [], []
        for pop, (mu1,mu0) in arm_predictions.items():
            result = summarize_predictions(train, evaluation, mu1, mu0, seed, population_filter=pop)
            rows.extend(result[0]); summaries.extend(result[1]); games.extend(result[2])
        all_rows.extend(rows); all_summaries.extend(summaries); all_games.extend(games)
        for filename, records in [('renal_attributions', all_rows), ('renal_splits', all_summaries), ('renal_coalitions', all_games)]:
            pd.DataFrame(records).to_csv(args.output/f'{filename}.csv', index=False)
        print(pd.DataFrame(summaries).to_string(index=False), flush=True)
    metadata.update(status='complete', elapsed_seconds_this_run=time.perf_counter()-started)
    manifest.write_text(json.dumps(metadata, indent=2)+'\n')
    heldout = pd.DataFrame(all_rows).query('population == "held_out"')
    baseline = pd.read_csv(baseline_path)
    comparison = heldout.merge(baseline, on=['seed', 'feature'], suffixes=('_tabpfn', '_cell'), validate='one_to_one')
    assert len(comparison) == 4*len(args.seeds)
    comparison.to_csv(args.output/'paired_comparison.csv', index=False)
    metrics = [c for c in comparison if c.endswith(('_tabpfn', '_cell'))]
    aggregate = comparison.groupby('feature')[metrics].agg(['mean', 'min', 'max'])
    aggregate.columns = ['_'.join(c) for c in aggregate.columns]
    aggregate.to_csv(args.output/'paired_summary.csv')
    print(aggregate.to_string(), flush=True)


if __name__ == '__main__':
    main()
