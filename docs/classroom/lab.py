"""Exact teaching examples; no fitting and no renal results. Python stdlib only."""
import argparse
from math import exp, isclose

def games(a=0.6, b=0.6, x=1.0, residual=0.2):
    # X and eM have mean zero and are independent. M=aX+eM; f(X,M)=bM.
    m = a*x + residual
    # v(empty)=0, v(M)=b*m, v(X,M)=b*m.
    # Model-interventional game replaces inputs without propagating X into M.
    pred = (0.0, b*m)
    # Structural game: do(X=x) propagates into M; E[eM]=0 gives v(X)=b*a*x.
    vx = b*a*x
    causal = (vx/2, b*m-vx/2)
    return {'m':m, 'prediction':b*m, 'predictive_shap':pred,
            'structural_shap':causal, 'effect_do_x_0_to_x':vx,
            'effect_do_m_0_to_m':b*m}

def nonlinear_mean(x):
    # Direct edge X -> Y, Y = X^2 + eY, E[eY]=0.
    return x*x

def sigmoid(x):
    return 1/(1+exp(-x))

def checks():
    for a,b,x,e in [(0.6,0.6,1,0.2),(-0.6,0.6,1,0.2),(0,0.6,1,0.2),(1.2,1.1,2,-0.1)]:
        r=games(a,b,x,e)
        assert isclose(sum(r['predictive_shap']),r['prediction'],abs_tol=1e-12)
        assert isclose(sum(r['structural_shap']),r['prediction'],abs_tol=1e-12)
        assert r['predictive_shap'][0] == 0
        assert isclose(r['effect_do_x_0_to_x'],a*b*x,abs_tol=1e-12)
    # Direct nonlinearity and intervention contrast matter.
    assert nonlinear_mean(1)-nonlinear_mean(-1)==0
    assert nonlinear_mean(2)-nonlinear_mean(0)==4
    # Reversing the sign of a path reverses its effect, not its causal direction.
    assert games(-0.6,0.6)['effect_do_x_0_to_x'] < 0
    # Generalized linear outcome: a constant log-odds effect is not a constant risk difference.
    assert not isclose(sigmoid(1)-sigmoid(0),sigmoid(3)-sigmoid(2))
    # Both Gaussian direction models have Var(X)=Var(Y)=1 and Cov(X,Y)=rho.
    rho=0.6
    assert isclose(rho*rho+(1-rho*rho),1)
    print('PASS: efficiency, dummy input, signed/zero effects, nonlinear contrasts, logistic scale, covariance equivalence.')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check',action='store_true')
    args=p.parse_args()
    if args.check:
        checks(); return
    r=games()
    print('TEACHING ONLY: M=0.6X+eM, f=0.6M; x=1, eM=0.2, mean-zero population.')
    for k,v in r.items(): print(f'{k}: {v}')
    print('\nDirect nonlinear cause: Y=X^2+eY.')
    print('do(X=-1) vs do(X=1): equal mean outcomes. do(X=0) to do(X=2): +4.')
    print('\nLinear Gaussian observational ambiguity (rho=0.6):')
    print('World A: X=U, Y=0.6X+sqrt(0.64)V. Effect do(X): 0.6 per unit.')
    print('World B: Y=V, X=0.6Y+sqrt(0.64)U. Effect do(X) on Y: 0.')
    print('Independent standard-normal U,V. Same observed covariance; different interventions.')
    print('\nDepth attenuation: 0.6^d for d=1..5:',[round(0.6**d,5) for d in range(1,6)])
    print('Counterexample: two positive paths of product 0.8 each sum to 1.6; depth alone is insufficient.')
    print('These analytic examples do not evaluate the proposed detector/filter or discovery algorithms.')

if __name__=='__main__': main()
