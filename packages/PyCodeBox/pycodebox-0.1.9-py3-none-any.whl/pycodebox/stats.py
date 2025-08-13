#!/bin/env python
# -*- coding: utf-8 -*-


# ----------------------------------------------------------------#
# Statistical Testing Utilities                                   #
# ----------------------------------------------------------------#
# These functions wrap general statistical tests and compute      #
# additional summary statistics.                                  #
# ----------------------------------------------------------------#


def fisher_exact_by_strata(var, strata, data):
  """
  Performs Fisher's exact test between a binary variable and a categorical strata
  variable, stratifying the analysis by each category of the strata variable. The
  function compares a category against all others for each category in turn.

  Parameters
  ----------
  var : str
      The name of the binary variable in `data` to be tested.
  strata : str
      The name of the categorical variable in `data` to stratify by. Must be a pandas
      Categorical variable that categories can be extracted from.
  data : pandas.DataFrame
      The DataFrame containing the variables of interest.

  Returns
  -------
  dict
      A dictionary with each category as a key and the following values:
      - 'n': Number of observations in category.
      - 'stats': Summary statistics (N, %) for category.
      - 'coef': The estimated odds ratio from statistical testing.
      - 'pvalue': The p-value from statistical testing.

  Notes
  -----
  - If `strata` contains only 2 groups, the resulting odds ratio will be the same for
  each category, just the inverse of the other. The p-values should be exactly the same.
  """
  import numpy as np
  import pandas as pd
  from scipy import stats

  # Check `var` is categorical
  if not (data[var].dtype.name == "category"):
    print(
      "The variable supplied to `var` was not a pandas Categorical variable. \
      Converting this variable to pandas Categorical with no specific ordering of \
      categories."
    )
    data[var] = pd.Categorical(data[var])

  # Check `strata` is categorical
  if not (data[strata].dtype.name == "category"):
    print(
      "The variable supplied to `strata` was not a pandas Categorical variable. \
      Converting this variable to pandas Categorical with no specific ordering of \
      categories."
    )
    data[strata] = pd.Categorical(data[strata])

  # Create empty dictionary to store results
  results = {}

  # Drop rows with NA in `var` or `strata`
  data = data[[var, strata]].dropna()

  # Determine number of categories in `strata` variable
  cat_n = len(data[strata].cat.categories)

  # For each level of `var`, perform testing between `var` and
  # each category of `strata` vs all others
  for group in data[var].cat.categories:
    if cat_n >= 2:
      for cat in data[strata].cat.categories:
        # Create dummy variables for analysis
        var_dummy = np.where(data[var] == group, 1, 0)
        strata_dummy = np.where(data[strata] == cat, 1, 0)

        if sum(var_dummy) > 0:
          # Create a 2x2 contingency table
          table = pd.crosstab(var_dummy, strata_dummy)

          # Calculate N and summary statistics
          n = sum(table.iloc[:, 1])
          summ_stats = (
            table.iloc[:, 1].astype(str)
            + " ("
            + round(table.iloc[:, 1] / n * 100, 1).astype(str)
            + "%)"
          )

          # Perform statistical testing
          statistic, pvalue = stats.fisher_exact(table, alternative="two-sided")

          # Calculate confidence interval and add to statistic
          ci = stats.contingency.odds_ratio(table).confidence_interval(
            confidence_level=0.95
          )
          statistic = (
            str(round(statistic, 2))
            + " ["
            + str(round(ci.low, 2))
            + "; "
            + str(round(ci.high, 2))
            + "]"
          )

          # Get results
          results[group, cat] = {
            "n": n,
            "stats": summ_stats,
            "coef": statistic,
            "pvalue": pvalue,
          }
    else:
      raise ValueError("Given strata variable has < 2 categories.")

  # Return results
  return results


def linear_reg_by_strata(var, strata, data):
  """
  Performs linear regression for a numerical variable and a categorical strata variable,
  stratifying the analysis by each category of the strata variable. The function tests
  a category against all others for each category in turn.

  Parameters
  ----------
  var : str
      The name of the numerical variable in `data` to be tested.
  strata : str
      The name of the categorical variable in `data` to stratify by. Must be a pandas
      Categorical variable that categories can be extracted from.
  data : pandas.DataFrame
      The DataFrame containing the variables of interest.

  Returns
  -------
  dict
      A dictionary with each category as a key and the following values:
      - 'n': Number of observations in category.
      - 'stats': Summary statistics (mean ± standard deviation) for category.
      - 'coef': The estimated beta coefficient from statistical testing.
      - 'pvalue': The p-value from statistical testing.

  Notes:
  ------
  - If `strata` contains only 2 groups, the resulting coefficient will be the same for
  each category, just the inverse of the other. The p-values should be exactly the same.
  """
  import numpy as np
  import pandas as pd
  from scipy import stats

  # Check `var` is numerical
  if data[var].dtype.kind not in ["i", "f"]:
    raise ValueError("The variable supplied to `var` must be numeric.")

  # Check `strata` is categorical
  if not (data[strata].dtype.name == "category"):
    print(
      "The variable supplied to `strata` was not a pandas Categorical variable. \
      Converting this variable to pandas Categorical with no specific ordering of \
      categories."
    )
    data[strata] = pd.Categorical(data[strata])

  # Create empty dictionary to store results
  results = {}

  # Drop rows with NA in `var` or `strata`
  data = data[[var, strata]].dropna()

  # Determine number of categories in `strata` variable
  cat_n = len(data[strata].cat.categories)

  # Perform testing between `var` and each category of `strata` vs all others
  if cat_n >= 2:
    for cat in data[strata].cat.categories:
      # Create dummy variable for denoting category vs others
      strata_dummy = np.where(data[strata] == cat, 1, 0)

      # Calculate N and summary statistics
      n = sum(strata_dummy)
      summ_stats = (
        str(round(data.loc[data[strata] == cat, var].mean(), 1))
        + "±"
        + str(round(data.loc[data[strata] == cat, var].std(), 1))
      )

      # Perform statistical testing
      statistic = stats.linregress(strata_dummy, data[var]).slope
      stderr = stats.linregress(strata_dummy, data[var]).stderr
      pvalue = stats.linregress(strata_dummy, data[var]).pvalue

      # Calculate confidence interval and add to statistic
      ci_low = statistic - 1.96 * stderr
      ci_high = statistic + 1.96 * stderr
      statistic = (
        str(round(statistic, 2))
        + " ["
        + str(round(ci_low, 2))
        + "; "
        + str(round(ci_high, 2))
        + "]"
      )

      # Get results
      results[cat] = {
        "n": n,
        "stats": summ_stats,
        "coef": statistic,
        "pvalue": pvalue,
      }

  else:
    raise ValueError("Given strata variable has < 2 categories.")

  # Return results
  return results
