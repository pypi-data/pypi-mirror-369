#!/bin/env python
# -*- coding: utf-8 -*-


# ----------------------------------------------------------------#
# Plotting Utilities                                              #
# ----------------------------------------------------------------#
# These functions help in generating data visualizations.         #
# ----------------------------------------------------------------#


def stratified_barplot(
  data,
  var,
  strata,
  case_id,
  fill_color=None,
  xlab=None,
  alpha=0.05,
):
  """
  Creates a stratified bar plot showing the frequency distribution of a categorical
  variable across different strata, including an 'All cases' comparison group, with
  statistical testing.

  Parameters
  ----------
  data : pandas.DataFrame
      The DataFrame containing the variables of interest.
  var : str
      The name of the categorical variable in `data` to be plotted on the y-axis as
      frequencies.
  strata : str
      The name of the categorical variable in `data` to stratify by, displayed on the
      x-axis.
  case_id : str
      The name of the column in `data` used as the case identifier for counting
      observations.
  fill_color : dict or list, optional
      Color specification for the bars. Can be a dictionary mapping variable categories
      to colors, or a list of colors.
  xlab : str, optional
      The label for the x-axis. If not provided, it defaults to the name of the `strata`
      variable with underscores replaced by spaces.
  alpha : float, optional
      Significance level for statistical tests (default: 0.05).

  Returns
  -------
  fig : matplotlib.figure.Figure
      A matplotlib figure object containing the stratified bar plot.
  ax : matplotlib.axes.Axes
      A matplotlib axes object containing specifications of the stratified bar plot.

  Notes
  -----
  - Missing values in `var` are automatically filtered out before plotting and an error
  arises if no data is left after filtering.
  - Fisher's exact test is performed when `var` contains 2 groups and Chi-squared test
  is performed when `var` has >2 groups.
  - Statistical tests exclude comparisons with the 'All cases' group.
  """
  import pandas as pd
  import numpy as np
  import matplotlib.pyplot as plt
  import matplotlib.colors as mcolors
  import seaborn as sns
  import scipy.stats as stats
  from itertools import combinations

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

  # Filter out missing values for `var`
  data = data[data[var].notna()]
  if data.empty:
    raise ValueError(
      "No data available for `var` and `strata` after filtering out missing \
      values of `var`."
    )

  # Perform pairwise Fisher exact tests
  significant_pairs = []
  pairwise_pvalues = {}

  for cat1, cat2 in combinations(data[strata].cat.categories, 2):
    cat_data = data[(data[strata] == cat1) | (data[strata] == cat2)]

    if len(cat_data) > 0:
      if len(cat_data[var].dropna().unique()) > 2:
        _, pvalue, _, _ = stats.chi2_contingency(
          pd.crosstab(cat_data[var], cat_data[strata])
        )
      else:
        _, pvalue = stats.fisher_exact(
          pd.crosstab(cat_data[var], cat_data[strata]),
          alternative="two-sided",
        )
      pairwise_pvalues[(cat1, cat2)] = pvalue

      if pvalue < alpha:
        # Store position indices for plotting (+1 to avoid plotting in all cases)
        pos1 = list(data[strata].cat.categories).index(cat1) + 1
        pos2 = list(data[strata].cat.categories).index(cat2) + 1
        significant_pairs.append((pos1, pos2, pvalue))

  # Get counts for each combination of `var` and `strata`
  strat_data = data.groupby([strata, var], observed=True)[case_id].count().reset_index()

  # Ensure all combinations of categories are accounted for to avoid errors
  complete_combinations = pd.MultiIndex.from_product(
    [data[strata].cat.categories, data[var].cat.categories],
    names=[strata, var],
  )
  strat_data = (
    strat_data.set_index([strata, var]).reindex(complete_combinations).reset_index()
  )

  # Calculate frequencies
  total_counts = data.groupby(strata, observed=True)[case_id].count().reset_index()
  total_counts = dict(zip(total_counts[strata], total_counts[case_id]))

  strat_data["freq"] = strat_data.apply(
    lambda row: row[case_id] / total_counts[row[strata]]
    if pd.notna(row[case_id])
    else pd.NA,
    axis=1,
  )

  # Aggregate data for all cases
  full_data = data.groupby(var, observed=True)[case_id].count().reset_index()
  full_data[strata] = "All cases"
  full_data["freq"] = full_data[case_id] / len(data)

  # Combine full and stratified data and remove any missing frequencies
  summ_stats = pd.concat([full_data, strat_data], ignore_index=True)
  summ_stats = summ_stats[summ_stats["freq"].notna()]

  # Make labels for counts and frequencies
  summ_stats["count_lab"] = summ_stats[case_id].apply(lambda x: f"N={x}")
  summ_stats["freq_lab"] = summ_stats["freq"].apply(lambda x: f"{round(x * 100, 1)}%")

  # Ensure `strata` categories has initial ordering
  summ_stats[strata] = pd.Categorical(
    summ_stats[strata],
    categories=["All cases"] + list(data[strata].cat.categories),
    ordered=True,
  )

  # Set up colors
  if fill_color is None:
    colors = sns.color_palette("tab10", n_colors=len(data[var].cat.categories))
    fill_color = [mcolors.to_hex(color) for color in colors]

  # Create color mapping
  color_map = dict(zip(data[var].cat.categories, fill_color))

  # Set up x-axis label
  if xlab is None:
    xlab = strata[0].upper() + strata[1:].replace("_", " ")

  ### Begin figure generation ###

  # Create the plot
  plt.ioff()
  fig, ax = plt.subplots(
    figsize=(
      len(data[var].cat.categories) + len(data[strata].cat.categories) + 1,
      5,
    )
  )

  # Set up bar positions
  n_strata = len(summ_stats[strata].cat.categories)
  n_vars = len(data[var].cat.categories)
  bar_width = 0.9 / n_vars

  # Plot bars for each variable category
  for i, var_cat in enumerate(data[var].cat.categories):
    var_data = summ_stats[summ_stats[var] == var_cat]

    # Get frequencies and counts for this variable category
    freqs = []
    counts = []
    freq_labels = []
    count_labels = []

    for strata_cat in summ_stats[strata].cat.categories:
      subset = var_data[var_data[strata] == strata_cat]
      if not subset.empty:
        freqs.append(subset["freq"].iloc[0])
        counts.append(subset[case_id].iloc[0])
        freq_labels.append(subset["freq_lab"].iloc[0])
        count_labels.append(subset["count_lab"].iloc[0])
      else:
        freqs.append(0)
        counts.append(0)
        freq_labels.append("0.0%")
        count_labels.append("N=0")

    # Plot bars
    x_pos = np.arange(n_strata) + (i - n_vars / 2 + 0.5) * bar_width
    bars = ax.bar(
      x=x_pos,
      height=freqs,
      width=bar_width,
      color=color_map.get(var_cat, f"C{i}"),
      edgecolor="black",
      linewidth=1,
      label=var_cat,
      alpha=0.8,
    )

    # Add frequency labels above bars
    for j, (bar, freq_label) in enumerate(zip(bars, freq_labels)):
      if freqs[j] > 0:
        ax.text(
          x=bar.get_x() + bar.get_width() / 2,
          y=bar.get_height() + 0.02,
          s=freq_label,
          ha="center",
          va="bottom",
          fontsize=10,
          rotation=90,
        )

    # Add count labels below x-axis
    for j, (bar, count_label) in enumerate(zip(bars, count_labels)):
      ax.text(
        x=bar.get_x() + bar.get_width() / 2,
        y=-0.01,
        s=count_label,
        ha="center",
        va="top",
        fontsize=9,
      )

  # Get data range for positioning elements
  y_min = min(summ_stats["freq"].dropna())
  y_max = max(summ_stats["freq"].dropna()) + 0.15

  # Add significance lines and p-values
  if significant_pairs:
    # Calculate line heights to avoid overlap
    line_height_increment = (y_max - y_min) * 0.08
    line_base_height = y_max + (y_max - y_min) * 0.05

    # Sort pairs by distance to minimize line crossings
    significant_pairs.sort(key=lambda x: abs(x[1] - x[0]))

    for i, (pos1, pos2, pvalue) in enumerate(significant_pairs):
      line_height = line_base_height + (i * line_height_increment)

      # Draw horizontal line
      ax.plot([pos1, pos2], [line_height, line_height], "black", linewidth=1)

      # Draw vertical connectors
      ax.plot(
        [pos1, pos1],
        [line_height - line_height_increment / 3, line_height],
        "black",
        linewidth=1,
      )
      ax.plot(
        [pos2, pos2],
        [line_height - line_height_increment / 3, line_height],
        "black",
        linewidth=1,
      )

      # Add p-value text
      mid_x = (pos1 + pos2) / 2
      p_text = f"p = {pvalue:.3f}" if pvalue >= 0.001 else "p < 0.001"
      ax.text(
        x=mid_x,
        y=line_height + line_height_increment / 10,
        s=p_text,
        ha="center",
        va="bottom",
        fontsize=9,
      )

  # Customize the plot
  ax.set_xlim(-0.5, n_strata - 0.5)
  if significant_pairs:
    ax.set_ylim(-0.05, (line_height + 0.1) if (line_height + 0.1) > 1 else 1)
  else:
    ax.set_ylim(-0.05, 1)
  ax.set_xlabel(xlab, fontsize=12)
  ax.set_ylabel("Frequency (%)", fontsize=12)
  ax.set_xticks(np.arange(n_strata))
  ax.set_xticklabels(summ_stats[strata].cat.categories, rotation=20, ha="right")

  # Set y-axis to percentage format
  y_ticks = np.linspace(0, 1, 6)
  ax.set_yticks(y_ticks)
  ax.set_yticklabels([f"{int(y * 100)}%" for y in y_ticks])

  # Add legend
  legend_title = var[0].upper() + var[1:].replace("_", " ")
  ax.legend(
    title=legend_title,
    loc="upper center",
    bbox_to_anchor=(0.5, 1.15),
    ncol=n_vars,
    frameon=False,
  )

  # Apply classic theme styling
  ax.spines["top"].set_visible(False)
  ax.spines["right"].set_visible(False)
  ax.grid(visible=False)

  plt.tight_layout()

  return fig, ax


def stratified_violin_boxplot(data, var, strata, ylab=None, xlab=None, alpha=0.05):
  """
  Creates a violin box plot showing the distribution of a numerical variable across
  different strata, including an 'All cases' comparison group, with statistical testing.

  Parameters
  ----------
  data : pandas.DataFrame
      The DataFrame containing the variables of interest.
  var : str
      The name of the numerical variable in `data` to be plotted on the y-axis.
  strata : str
      The name of the categorical variable in `data` to stratify by, displayed on the
      x-axis.
  ylab : str, optional
      The title for the y-axis, describing the numerical variable. If not provided,
      it defaults to the name of the `var` variable with underscores replaced by spaces.
  xlab : str, optional
      The title for the x-axis. If not provided, it defaults to the name of the `strata`
      variable with underscores replaced by spaces.
  alpha : float, optional
      Significance level for statistical tests (default: 0.05).

  Returns
  -------
  fig : matplotlib.figure.Figure
      A matplotlib figure object containing the stratified violin box plot with
      statistical comparisons.
  ax : matplotlib.axes.Axes
      A matplotlib axes object containing specifications of the stratified violin box plot.

  Notes
  -----
  - Missing values in `var` are automatically filtered out before plotting and an error
  arises if no data is left after filtering.
  - Statistical tests exclude comparisons with the 'All cases' group.
  """
  import pandas as pd
  import numpy as np
  import matplotlib.pyplot as plt
  import scipy.stats as stats
  from itertools import combinations

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

  # Filter out missing values for `var`
  data = data[data[var].notna()]
  if data.empty:
    raise ValueError(
      "No data available for `var` and `strata` after filtering out missing \
            values of `var`."
    )

  # Perform pairwise Mann-Whitney U tests
  significant_pairs = []
  pairwise_pvalues = {}

  for cat1, cat2 in combinations(data[strata].cat.categories, 2):
    cat1_data = data[data[strata] == cat1][var].dropna()
    cat2_data = data[data[strata] == cat2][var].dropna()

    if len(cat1_data) > 0 and len(cat2_data) > 0:
      _, pvalue = stats.mannwhitneyu(x=cat1_data, y=cat2_data, alternative="two-sided")
      pairwise_pvalues[(cat1, cat2)] = pvalue

      if pvalue < alpha:
        # Store position indices for plotting (+1 to avoid plotting in all cases)
        pos1 = list(data[strata].cat.categories).index(cat1) + 1
        pos2 = list(data[strata].cat.categories).index(cat2) + 1
        significant_pairs.append((pos1, pos2, pvalue))

  # Add data for an all cases group
  data = pd.concat([data, data])
  data[strata] = pd.Categorical(
    data[strata],
    categories=["All cases"] + data[strata].cat.categories.tolist(),
    ordered=True,
  )
  data.loc[
    data.reset_index().index.to_numpy() >= (data.shape[0] // 2),
    strata,
  ] = "All cases"

  # Calculate median for each stratum of `strata`
  summ_stats = data.groupby(strata, observed=True)[var].median().reset_index()
  summ_stats["median_lab"] = summ_stats[var].apply(
    lambda x: f"Median={int(round(x, 0))}"
  )

  # Set up labels
  if ylab is None:
    ylab = var[0].upper() + var[1:].replace("_", " ")
  if xlab is None:
    xlab = strata[0].upper() + strata[1:].replace("_", " ")

  ### Begin plot generation ###

  # Create the plot
  plt.ioff()
  fig, ax = plt.subplots(figsize=(len(data[strata].cat.categories) + 1, 6))

  # Create data for violin and box plots
  plot_data = []
  for cat in data[strata].cat.categories:
    cat_data = data[data[strata] == cat][var].dropna()
    plot_data.append(cat_data)

  # Create violin plots
  violin_plot = ax.violinplot(
    dataset=plot_data,
    positions=np.arange(len(data[strata].cat.categories)),
    widths=0.7,
    showmeans=False,
    showmedians=False,
    showextrema=False,
  )

  # Style violin plots
  for pc in violin_plot["bodies"]:
    pc.set_facecolor("lightgrey")
    pc.set_edgecolor("black")
    pc.set_alpha(0.7)

  # Create box plots
  box_plot = ax.boxplot(
    x=plot_data,
    positions=np.arange(len(data[strata].cat.categories)),
    widths=0.3,
    capwidths=0,
    patch_artist=True,
    showfliers=False,
  )

  # Style box plots
  for patch in box_plot["boxes"]:
    patch.set_facecolor("white")
    patch.set_edgecolor("black")

  for element in ["whiskers", "caps", "medians"]:
    for item in box_plot[element]:
      item.set_color("black")

  # Add jittered points
  np.random.seed(1234)
  for i, cat in enumerate(data[strata].cat.categories):
    cat_data = data[data[strata] == cat][var].dropna()
    if len(cat_data) > 0:
      jitter_x = np.random.uniform(i - 0.2, i + 0.2, size=len(cat_data))
      ax.scatter(x=jitter_x, y=cat_data, color="black", s=50, alpha=0.6)

  # Add mean and 95% CI as red pointrange
  for i, cat in enumerate(data[strata].cat.categories):
    cat_data = data[data[strata] == cat][var].dropna()
    if len(cat_data) > 0:
      mean_val = np.mean(cat_data)
      se = stats.sem(cat_data)
      ci = se * stats.t.ppf((1 + 0.95) / 2, len(cat_data) - 1)

      # Plot mean as red point
      ax.scatter(x=i, y=mean_val, color="red", s=50, zorder=5)

      # Plot 95% CI as red error bars
      ax.errorbar(
        x=i,
        y=mean_val,
        yerr=ci,
        color="red",
        capsize=3,
        capthick=1,
        linewidth=1,
        zorder=5,
      )

  # Get data range for positioning elements
  y_min = min(data[var].dropna())
  y_max = max(data[var].dropna())

  # Add significance lines and p-values
  if significant_pairs:
    # Calculate line heights to avoid overlap
    line_height_increment = (y_max - y_min) * 0.08
    line_base_height = y_max + (y_max - y_min) * 0.05

    # Sort pairs by distance to minimize line crossings
    significant_pairs.sort(key=lambda x: abs(x[1] - x[0]))

    for i, (pos1, pos2, pvalue) in enumerate(significant_pairs):
      line_height = line_base_height + (i * line_height_increment)

      # Draw horizontal line
      ax.plot([pos1, pos2], [line_height, line_height], "black", linewidth=1)

      # Draw vertical connectors
      ax.plot(
        [pos1, pos1],
        [line_height - line_height_increment / 3, line_height],
        "black",
        linewidth=1,
      )
      ax.plot(
        [pos2, pos2],
        [line_height - line_height_increment / 3, line_height],
        "black",
        linewidth=1,
      )

      # Add p-value text
      mid_x = (pos1 + pos2) / 2
      p_text = f"p = {pvalue:.3f}" if pvalue >= 0.001 else "p < 0.001"
      ax.text(
        x=mid_x,
        y=line_height + line_height_increment / 10,
        s=p_text,
        ha="center",
        va="bottom",
        fontsize=9,
      )

  # Set y-axis limits accounting for significance lines
  y_limit_adjustment = (y_max - y_min) * 0.02
  upper_limit = y_max + y_limit_adjustment
  if significant_pairs:
    max_line_height = (
      line_base_height + (len(significant_pairs) - 1) * line_height_increment
    )
    upper_limit = max(upper_limit, max_line_height + line_height_increment)

  # Add median labels
  y_range = upper_limit - y_min
  label_y = y_min - abs(y_range * 0.05)
  for i, (_, row) in enumerate(summ_stats.iterrows()):
    ax.text(x=i, y=label_y, s=row["median_lab"], ha="center", va="center", fontsize=10)

  # Customize the plot
  ax.set_xticks(np.arange(len(data[strata].cat.categories)))
  ax.set_xticklabels(data[strata].cat.categories, rotation=20, ha="right")
  ax.set_xlabel(xlab, fontsize=12)
  ax.set_ylabel(ylab, fontsize=12)

  ax.set_ylim(label_y - (y_range * 0.03), upper_limit)

  # Apply classic theme styling
  ax.spines["top"].set_visible(False)
  ax.spines["right"].set_visible(False)
  ax.grid(visible=False)

  plt.tight_layout()

  return fig, ax


def stratified_coef_w_ci(
  data,
  var,
  strata,
  coef,
  lower,
  upper,
  pvalue=None,
  fill_color=None,
  xlab=None,
):
  """
  Creates a coefficient plot showing the estimated coefficients and confidence
  intervals of a numerical variable across different strata.

  Parameters
  ----------
  data : pandas.DataFrame
      The DataFrame in "long" format that contains columns denoting the names of the
      tested variables (`var`), groups tested (`strata`), coefficients (`coef`), and the
      lower (`lower`) and upper (`upper`) limits of the coefficient confidence interval.
      Optionally, it can also contain p-values (`pvalue`) for each coefficient.
  var : str
      The column in `data` denoting names of tested variables to be plotted on the y-axis.
      The plot will be faceted by this variable.
  strata : str
      The name of the categorical variable in `data` to stratify by, displayed as
      different color points and ranges.
  coef : float
      The column in `data` denoting the estimated coefficients for each stratum of
      `strata` and variable of `var`.
  lower : float
      The column in `data` denoting the lower limit of the confidence interval for each
      coefficient.
  upper : float
      The column in `data` denoting the upper limit of the confidence interval for each
      coefficient
  pvalue : float, optional
      The column in `data` denoting the p-values for each coefficient. If provided,
      p-values will be displayed as text labels on the plot. If not provided, no p-values
      will be displayed.
  fill_color : dict or list, optional
      Color specification for the points and ranges. Can be a dictionary mapping variable
      categories to colors, or a list of colors.
  xlab : str, optional
      The title for the x-axis describing the coefficients being plotted. If not provided,
      it defaults to the name of the `coef` variable with underscores replaced by spaces

  Returns
  -------
  fig : matplotlib.figure.Figure
      A matplotlib figure object containing the coefficient plot.
  ax : matplotlib.axes.Axes
      A matplotlib axes object containing specifications of the coefficient plot.
  """
  import pandas as pd
  import matplotlib.pyplot as plt
  import matplotlib.colors as mcolors
  import seaborn as sns

  # Check `var` is categorical
  if not (data[var].dtype.name == "category"):
    print(
      "The variable supplied to `var` was not a pandas Categorical variable. \
      Converting this variable to pandas Categorical with no specific ordering of \
      categories."
    )
    data[var] = pd.Categorical(data[var])

  # Make sure all categories of `var` are present in data
  var_counts = data[var].value_counts()
  if len(data[var].cat.categories) != sum(var_counts > 0):
    data[var] = pd.Categorical(
      data[var], categories=var_counts[var_counts > 0].index.tolist()
    )

  # Check `strata` is categorical
  if not (data[strata].dtype.name == "category"):
    print(
      "The variable supplied to `strata` was not a pandas Categorical variable. \
      Converting this variable to pandas Categorical with no specific ordering of \
      categories."
    )
    data[strata] = pd.Categorical(data[strata])

  # Check `coef`, `lower`, and `upper` are numerical
  if data[coef].dtype.kind not in ["i", "f"]:
    raise ValueError("The variable supplied to `coef` must be numeric.")
  if data[lower].dtype.kind not in ["i", "f"]:
    raise ValueError("The variable supplied to `lower` must be numeric.")
  if data[upper].dtype.kind not in ["i", "f"]:
    raise ValueError("The variable supplied to `upper` must be numeric.")
  if pvalue and data[pvalue].dtype.kind not in ["i", "f"]:
    raise ValueError("The variable supplied to `pvalue` must be numeric.")

  # If `pvalue` provided, create p-value labels
  if pvalue:
    data["pvalue_labs"] = data[pvalue].apply(
      lambda x: f"P={x:.1e}" if x < 0.005 else f"P={x:.2f}" if x >= 0.005 else ""
    )

  # Set up colors
  if fill_color is None:
    colors = sns.color_palette("tab10", n_colors=len(data[strata].cat.categories))
    fill_color = [mcolors.to_hex(color) for color in colors]

  # Create color mapping
  color_map = dict(zip(data[strata].cat.categories, fill_color))

  # Set x-axis label
  if xlab is None:
    xlab = coef[0].upper() + coef[1:].replace("_", " ")

  ### Begin plot generation ###

  # Create the plot
  fig, ax = plt.subplots(
    nrows=len(data[var].cat.categories),
    ncols=1,
    figsize=(
      (6, len(data[var].cat.categories))
      if len(data[strata].cat.categories) > 1
      else (4, len(data[var].cat.categories))
    ),
    sharex=True,
  )

  # Handle single subplot case
  if len(data[var].cat.categories) == 1:
    ax = [ax]

  # Generate plot for each variable
  for i, cat in enumerate(data[var].cat.categories):
    cat_data = data[data[var] == cat]

    # Add reference line
    ax[i].axvline(
      x=(0 if min(data[coef]) < 0 else 1),
      linestyle="--",
      color="black",
      alpha=0.6,
      linewidth=1,
    )

    # Plot error bars and points for each stratum
    for j, (_, row) in enumerate(cat_data.iterrows()):
      # Error bars
      ax[i].errorbar(
        x=row[coef],
        y=j,
        xerr=[[row[coef] - row[lower]], [row[upper] - row[coef]]],
        fmt="o",
        color=color_map[row[strata]],
        capsize=3,
        capthick=1,
        markersize=8,
        linewidth=2,
        label=row[strata] if i == 0 else "",
      )

      # Add p-value labels if provided
      if pvalue:
        if row["pvalue_labs"]:  # Only add if not empty
          ax[i].text(
            x=max(data[upper]) + (max(data[upper]) * 0.05),
            y=j,
            s=row["pvalue_labs"],
            va="center",
            ha="left",
            fontsize=8 if len(data[strata].cat.categories) > 1 else 10,
          )

    # Remove y-axis ticks and labels
    ax[i].set_yticks([])
    ax[i].set_yticklabels([])
    ax[i].set_ylabel("")

    # Set y-axis limits to give more room around points
    ax[i].set_ylim(-1, len(data[strata].cat.categories) + 0.1)

    # Set subplot title and formatting
    ax[i].set_title(label=cat, fontsize=10, fontweight="bold")
    ax[i].grid(visible=True, alpha=0.3)
    ax[i].set_axisbelow(True)

    # Adjust x-limits if p-values are present
    if len(data[strata].cat.categories) > 1:
      ax[i].set_xlim(
        min(data[lower].dropna()) - abs(min(data[lower].dropna())) * 0.05,
        max(data[upper].dropna()) + abs(min(data[lower].dropna())) * 0.45
        if pvalue
        else max(data[upper].dropna()) + abs(min(data[lower].dropna())) * 0.05,
      )
    else:
      ax[i].set_xlim(
        min(data[lower].dropna()) - abs(min(data[lower].dropna())) * 0.05,
        max(data[upper].dropna()) + abs(min(data[lower].dropna())) * 0.05,
      )

  # Add legend (only show unique labels)
  if len(data[strata].cat.categories) > 1:
    handles, labels = ax[0].get_legend_handles_labels()
    # Remove duplicates while preserving order
    unique_labels = []
    unique_handles = []
    for handle, label in zip(handles, labels):
      if label not in unique_labels:
        unique_labels.append(label)
        unique_handles.append(handle)

    legend_title = strata[0].upper() + strata[1:].replace("_", " ")
    legend_x_pos = 0.95 + max(0, (len(legend_title) - 10) * 0.008)
    fig.legend(
      handles=unique_handles,
      labels=unique_labels,
      title=legend_title,
      loc="center right",
      bbox_to_anchor=(legend_x_pos, 0.5),
      fontsize=10,
      title_fontsize=10,
      frameon=False,
    )

  # Set common x-label
  ax[-1].set_xlabel(xlabel=xlab, fontsize=10)

  plt.tight_layout()
  if len(data[strata].cat.categories) > 1:
    plt.subplots_adjust(right=0.65)

  return fig, ax


def stratified_volcano(
  data,
  var,
  strata,
  coef,
  pvalue,
  pthresh=0.05,
  top_n=None,
  fill_color=None,
  xlab=None,
):
  """
  Creates a stratified volcano plot showing the association results between tested
  numerical variables across different strata. Useful for when there are too many
  variables to plot using the `stratified_coef_w_ci` function.

  Parameters
  ----------
  data : pandas.DataFrame
      The DataFrame in "long" format that contains columns denoting the names of the
      tested variables (`var`), groups tested (`strata`), coefficients (`coef`), and the
      p-values for each coefficient (`pvalue`).
  var : str
      The column in `data` denoting names of tested variables to be plotted. Each variable
      will be an independent point on the plot.
  strata : str
      The name of the categorical variable in `data` to stratify by. The plot will be
      faceted by this variable.
  coef : float
      The column in `data` denoting the estimated coefficients for each stratum of
      `strata` and variable of `var`.
  pvalue : float
      The column in `data` denoting the p-values for each coefficient.
  pthresh : float, optional
      The p-value threshold to use for significance (default: 0.05).
  top_n : float, optional
      The top number of enriched and depleted variables to show labels (default: no
      labels).
  fill_color : dict or list, optional
      Color specification for the points and ranges. Can be a dictionary mapping variable
      categories to colors, or a list of colors.
  xlab : str, optional
      The title for the x-axis describing the coefficients being plotted. If not provided,
      it defaults to the name of the `coef` variable with underscores replaced by spaces

  Returns
  -------
  fig : matplotlib.figure.Figure
      A matplotlib figure object containing the volcano plot.
  ax : matplotlib.axes.Axes
      A matplotlib axes object containing specifications of the volcano plot.
  """
  import numpy as np
  import pandas as pd
  import matplotlib.pyplot as plt
  import matplotlib.colors as mcolors
  import seaborn as sns
  from adjustText import adjust_text

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

  # Check `coef` and `pvalue` are numerical
  if data[coef].dtype.kind not in ["i", "f"]:
    raise ValueError("The variable supplied to `coef` must be numeric.")
  if data[pvalue].dtype.kind not in ["i", "f"]:
    raise ValueError("The variable supplied to `pvalue` must be numeric.")

  # Create enriched vs depleted column
  if min(data[coef]) < 0:
    data["direction"] = pd.Categorical(
      np.where(
        (data[coef] < 0) & (data[pvalue] < pthresh),
        "Depleted",
        np.where(
          (data[coef] > 0) & (data[pvalue] < pthresh),
          "Enriched",
          "Not significant",
        ),
      )
    )
  else:
    data["direction"] = pd.Categorical(
      np.where(
        (data[coef] < 1) & (data[pvalue] < pthresh),
        "Depleted",
        np.where(
          (data[coef] > 1) & (data[pvalue] < pthresh),
          "Enriched",
          "Not significant",
        ),
      )
    )

  # Create column for labels
  if top_n:
    data["var_labs"] = pd.NA
    data_sorted = data.sort_values(pvalue)
    for stratum in data[strata].cat.categories:
      data_subset = data_sorted[data_sorted[strata] == stratum]
      top_enriched = list(
        data_subset[data_subset["direction"] == "Enriched"][var][0:top_n]
      )
      top_depleted = list(
        data_subset[data_subset["direction"] == "Depleted"][var][0:top_n]
      )
      data["var_labs"] = np.where(
        data[var].isin(top_enriched + top_depleted) & (data[strata] == stratum),
        data[var],
        data["var_labs"],
      )

  # Create column for -log10 of the p-value
  data["log10p"] = -np.log10(data[pvalue])

  # Set up colors
  if fill_color is None:
    colors = sns.color_palette("tab10", n_colors=len(data["direction"].cat.categories))
    fill_color = [mcolors.to_hex(color) for color in colors]

  # Create color mapping
  color_map = dict(zip(data["direction"].cat.categories, fill_color))

  # Set up x-axis label
  if xlab is None:
    xlab = coef[0].upper() + coef[1:].replace("_", " ")

  ### Begin figure generation ###

  # Create figure and subplots
  plt.ioff()
  fig, ax = plt.subplots(
    nrows=len(data[strata].cat.categories),
    ncols=1,
    figsize=(5, 4 * len(data[strata].cat.categories)),
    sharex=True,
    sharey=True,
  )

  # Handle single subplot case
  if len(data[strata].cat.categories) == 1:
    ax = [ax]

  # Generate plot for each stratum
  for i, cat in enumerate(data[strata].cat.categories):
    cat_data = data[data[strata] == cat]

    # Plot points for each direction category
    texts = []
    for direction in data["direction"].cat.categories:
      direction_data = cat_data[cat_data["direction"] == direction]
      if not direction_data.empty:
        ax[i].scatter(
          x=direction_data[coef],
          y=direction_data["log10p"],
          label=direction,
          c=color_map[direction],
          alpha=0.6,
          s=50,
        )

        # Add labels for top_n points if specified
        if top_n:
          labeled_data = direction_data[direction_data["var_labs"].notna()]
          for _, row in labeled_data.iterrows():
            text = ax[i].annotate(
              text=row["var_labs"],
              xy=(row[coef], row["log10p"]),
              fontsize=8,
              ha="center",
              va="center",
              bbox=dict(
                boxstyle="round,pad=0.3",
                facecolor="white",
                alpha=0.6,
                edgecolor="black",
              ),
            )
            texts.append(text)

    # Add reference lines
    ax[i].axvline(
      x=(0 if min(data[coef]) < 0 else 1),
      linestyle="--",
      color="black",
      alpha=0.6,
      linewidth=1,
    )
    ax[i].axhline(
      y=-np.log10(pthresh),
      linestyle="--",
      color="black",
      alpha=0.6,
      linewidth=1,
    )

    # Adjust text positions to avoid overlap
    if top_n and texts:
      adjust_text(
        texts=texts,
        ax=ax[i],
        arrowprops=dict(arrowstyle="-", color="black", alpha=0.6),
        force_explode=5,
      )

    # Set subplot title and formatting
    ax[i].set_title(
      label=f"{strata[0].upper() + strata[1:].replace('_', ' ')}: {cat}",
      fontsize=10,
      fontweight="bold",
    )
    ax[i].grid(visible=True, alpha=0.3)
    ax[i].set_ylabel(ylabel="-log10(P-value)", fontsize=10)

    # Only show legend on first subplot
    if i == 0:
      ax[i].legend(fontsize=9, framealpha=1)

  # Set common x-label
  ax[-1].set_xlabel(xlabel=xlab, fontsize=10)

  # Adjust layout
  plt.tight_layout()

  return fig, ax


def pca_kmeans_plot(
  data,
  group_var=None,
  k_range=range(2, 20),
  random_state=0,
  standardize=True,
  group_fill_color=None,
):
  """
  Perform PCA and k-means clustering, plotting the first two PCs colored by clusters.
  Optionally, if a grouping variable is provided, plot two subplots: coloring by group
  and by k-means clusters, and return a contingency table.

  Parameters
  ----------
  data : pandas.DataFrame
      Input dataframe. Must be all numeric except possibly the grouping variable.
  group_var : str or None, optional
      Name of the column with known groupings. If provided, k will be set to the
      number of unique groups.
  k_range : range, optional
      Range of k values to try if group_var is not given.
  random_state : int, optional
      Random state for reproducibility.
  standardize : bool, optional
      Whether to standardize features before PCA (default: True).
  group_fill_color : list, optional
      List of color hex codes to use for filling the groups in the plot. If provided,
      it will override the default color mapping.

  Returns
  -------
  fig : matplotlib.figure.Figure
      A matplotlib figure object containing a PCA plot colored by k-means cluster
      membership and, if `group_var` provided, the known groupings.
  ax : matplotlib.axes.Axes
      A matplotlib axes object containing specifications of the PCA plot(s).
  cluster_labels : numpy.ndarray
      Array of cluster labels assigned by k-means.
  contingency_table : pandas.DataFrame
      A contingency table showing the relationship between the grouping variable and
      the k-means cluster membership. Only returned if `group_var` is provided.
  """
  import pandas as pd
  import numpy as np
  import matplotlib.pyplot as plt
  from sklearn.decomposition import PCA
  from sklearn.cluster import KMeans
  from sklearn.metrics import silhouette_score
  from sklearn.preprocessing import StandardScaler

  # Separate features and group_var
  if group_var is not None:
    # Check `group_var` is in DataFrame
    assert group_var in data.columns, f"{group_var} not found in DataFrame columns"

    # Check `group_var` is categorical
    if not (data[group_var].dtype.name == "category"):
      print(
        "The variable supplied to `group_var` was not a pandas Categorical variable. \
        Converting this variable to pandas Categorical with no specific ordering of \
        categories."
      )
      data[group_var] = pd.Categorical(data[group_var])

    x = data.drop(columns=[group_var])
    k = len(data[group_var].cat.categories)
  else:
    x = data.copy()
    k = None

  # Only keep numeric features
  x = x.select_dtypes(include=[np.number])
  if x.shape[1] < 2:
    raise ValueError("Need at least two numeric columns for PCA.")

  # Standardize to mean of ~0 and variance of 1
  if standardize:
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x)
  else:
    x_scaled = x.values

  # Perform PCA and extract first two components
  pca = PCA(n_components=2, random_state=random_state).fit_transform(x_scaled)
  pc_data = pd.DataFrame(pca, columns=["PC1", "PC2"])

  # Determine optimal k
  if k is None:
    sil_scores = []
    for i in k_range:
      labels = KMeans(
        n_clusters=i,
        n_init=10,
        random_state=random_state,
      ).fit_predict(x_scaled)
      sil_scores.append(silhouette_score(x_scaled, labels))
    k = k_range[np.argmax(sil_scores)]

  # Fit KMeans
  cluster_labels = KMeans(
    n_clusters=k,
    n_init=10,
    random_state=random_state,
  ).fit_predict(x_scaled)
  pc_data["cluster"] = cluster_labels

  ### Begin figure generation ###

  plt.ioff()
  if group_var is None:
    # Initiate a single plot
    fig, ax = plt.subplots(figsize=(6, 5))

    # Plot coloring by estimated cluster
    scatter = ax.scatter(
      pc_data["PC1"],
      pc_data["PC2"],
      c=pc_data["cluster"],
      cmap="tab10",
      s=50,
      alpha=0.8,
      edgecolor="k",
    )

    # Set plot title and formatting
    ax.set_title(f"PCA - Colored by estimated clusters (k={k})", fontsize=12)
    ax.set_xlabel("PC1", fontsize=12)
    ax.set_ylabel("PC2", fontsize=12)
    ax.grid(visible=True, alpha=0.3)

    # Set legend
    handles, labels = scatter.legend_elements(prop="colors")
    ax.legend(handles=handles, labels=labels, title="Cluster")

    return fig, ax, cluster_labels
  else:
    # Initiate a two-panel plot
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(12, 5))

    # Plot coloring by known group
    group_map = {g: i for i, g in enumerate(data[group_var].cat.categories)}
    group_colors = [group_map[grp] for grp in data[group_var].values]
    if group_fill_color is not None:
      color_list = [group_fill_color[group_map[grp]] for grp in data[group_var].values]
      g1 = ax[0].scatter(
        pc_data["PC1"],
        pc_data["PC2"],
        c=color_list,
        s=50,
        alpha=0.8,
        edgecolor="k",
      )
    else:
      g1 = ax[0].scatter(
        pc_data["PC1"],
        pc_data["PC2"],
        c=group_colors,
        cmap="tab10",
        s=50,
        alpha=0.8,
        edgecolor="k",
      )

    # Set plot title and formatting of first subplot
    group_var_format = group_var[0].upper() + group_var[1:].replace("_", " ")
    ax[0].set_title(f"PCA - Colored by {group_var_format}", fontsize=12)
    ax[0].set_xlabel("PC1", fontsize=12)
    ax[0].set_ylabel("PC2", fontsize=12)
    ax[0].grid(visible=True, alpha=0.3)

    # Set legend for known groups
    if group_fill_color is not None:
      # If group_fill_color is provided, use it to create legend handles
      handles = [
        plt.Line2D(
          [0],
          [0],
          marker="o",
          color="w",
          label=grp,
          markerfacecolor=group_fill_color[group_map[grp]],
        )
        for grp in data[group_var].cat.categories
      ]
      labels = data[group_var].cat.categories.tolist()
    else:
      # Otherwise, use the default legend elements
      handles, labels = g1.legend_elements(prop="colors")

    ax[0].legend(handles=handles, labels=labels, title=group_var_format)

    # Plot coloring by estimated cluster
    g2 = ax[1].scatter(
      pc_data["PC1"],
      pc_data["PC2"],
      c=pc_data["cluster"],
      cmap="tab10",
      s=50,
      alpha=0.8,
      edgecolor="k",
    )

    # Set plot title and formatting of second subplot
    ax[1].set_title(f"PCA - Colored by estimated clusters (k={k})", fontsize=12)
    ax[1].set_xlabel("PC1", fontsize=12)
    ax[1].set_ylabel("PC2", fontsize=12)
    ax[1].grid(visible=True, alpha=0.3)

    # Set legend for estimated clusters
    handles, labels = g2.legend_elements(prop="colors")
    ax[1].legend(handles=handles, labels=labels, title="Cluster")

    # Create contingency table of known groups vs estimated clusters
    contingency = pd.crosstab(
      pd.Series(data[group_var].values, name=group_var),
      pd.Series(cluster_labels, name="KMeansCluster"),
    )
    return fig, ax, cluster_labels, contingency
