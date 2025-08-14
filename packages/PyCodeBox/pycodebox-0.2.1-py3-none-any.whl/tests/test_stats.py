import pandas as pd
from pycodebox.stats import fisher_exact_by_strata, linear_reg_by_strata


def test_fisher_exact_by_strata():
  df = pd.DataFrame(
    {
      'var': pd.Categorical(['yes', 'no', 'yes', 'no']),
      'strata': pd.Categorical(['A', 'A', 'B', 'B']),
    }
  )
  result = fisher_exact_by_strata('var', 'strata', df)
  assert isinstance(result, dict)
  assert ('yes', 'A') in result


def test_linear_reg_by_strata():
  df = pd.DataFrame(
    {
      'var': [1.0, 2.0, 3.0, 4.0],
      'strata': pd.Categorical(['A', 'A', 'B', 'B']),
    }
  )
  result = linear_reg_by_strata('var', 'strata', df)
  assert isinstance(result, dict)
  assert 'A' in result
