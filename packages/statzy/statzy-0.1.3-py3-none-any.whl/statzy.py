import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
from io import StringIO
import base64
from IPython.display import display, HTML
import math

################################################
# Utility Methods
################################################    
def get_numeric_cols(df):
    return df.select_dtypes(include=np.number).columns

def get_cat_cols(df):
    return df.select_dtypes(include='object').columns

def format_decimal_if_needed(x, decimals=1):
    if x == int(x):
        return str(int(x))
    else:
        return f"{x:.{decimals}f}"

def toggle_offset(y_text, y_text_offset, toggle):
    if toggle:
        return y_text - y_text_offset
    else:
        return y_text + y_text_offset

def plot_to_base64(fig, width='100%', height='auto'):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    # return f"<img src='data:image/png;base64,{b64}' width='150'>"
    return f"<img src='data:image/png;base64,{b64}' style='width:{width}; height:{height};'>"
    
################################################
# Univariate Analysis
################################################    
def info(df, n=5):
    print("\n")
    print("Basic Information about Data:")
    print("=============================")
    
    print("Shape of the dataset: " + str(df.shape))

    # print only a few wanted lines from df.info()
    buffer = StringIO()
    df.info(buf=buffer)
    lines = buffer.getvalue().splitlines()
    for line in lines:
        if line.strip().startswith("RangeIndex:") or \
           line.strip().startswith("dtypes:") or \
           line.strip().startswith("memory usage:"):
            print(line.strip())

    # calculate metadata about each column
    meta_row = df.dtypes.astype(str).astype(object)  # Convert to object dtype for string ops
    for col in df.columns:
        non_nulls = df[col].notnull().sum()
        nulls = df[col].isnull().sum()
        unique = df[col].nunique(dropna=True)
        dtype = str(df[col].dtype)
        
        meta_str = (f"{non_nulls} non-nulls"
            f"<br><br>{nulls} nulls"
            f"<br><br>{unique} unique"
            f"<br><br>{dtype}")
        meta_row[col] = meta_str
    meta_df = pd.DataFrame([meta_row], index=['Meta'])
    combined = pd.concat([meta_df, df.head(n)], ignore_index=False)
    display(HTML(combined.to_html(escape=False)))
    # display(combined)  # for Jupyter/Colab
    # print(combined)  # Uncomment for non-notebook use
    
    # Missing Data Visualization
    plt.figure(figsize=(8, 4))
    sns.heatmap(df.isnull(), cbar=False, cmap='viridis')
    plt.title("Missing Values Heatmap")
    plt.show()
    
def describe(df):    
    numeric_cols = get_numeric_cols(df)
    cat_cols = get_cat_cols(df)

    print("\n")
    print("Summary Stats and Univariate Analysis:")
    print("======================================")
    
    print("\nNUMERIC COLUMNS SUMMARY:")
    print("------------------------")
    numeric_data = prepare_table_data_for_numeric_columns(df, numeric_cols)
    numeric_html = render_html_table(numeric_data, numeric_cols)
    display(HTML(numeric_html))

    print("\nCATEGORICAL COLUMNS SUMMARY:")
    print("----------------------------")
    if not cat_cols.empty:
        cat_data = prepare_table_data_for_categorical_columns(df, cat_cols)
        cat_html = render_html_table(cat_data, cat_cols)
        display(HTML(cat_html))
    
    tidy_describe(df)

def prepare_table_data_for_numeric_columns(df, numeric_cols):
    """Prepare all data for the summary table for numeric columns"""
    data = {}
    
    desc = df[numeric_cols].describe().round(2)
    
    # Add summary statistics
    for idx in desc.index:
        data[idx] = {col: desc.loc[idx, col] for col in numeric_cols}
    
    # Add visualizations
    data['Box Plot'] = {col: get_boxplot(df, col) for col in numeric_cols}
    data['Histogram'] = {col: get_histogram(df, col) for col in numeric_cols}
    
    plt.close('all')
    return data
    
def prepare_table_data_for_categorical_columns(df, cat_cols):
    """Prepare all data for the summary table for categorical columns"""
    try:
        data = {}
        desc = df[cat_cols].describe()

        # Add summary statistics for categorical columns
        # for idx in desc.index:
        #     if idx != 'top':  # Skip 'top' row as it's redundant with Top 3 Values
        #         data[idx] = {col: desc.loc[idx, col] for col in cat_cols}
                
        if 'count' in desc.index:
            data['count'] = {col: desc.loc['count', col] for col in cat_cols}
        # data['Missing %'] = {col: f"{(df[col].isnull().sum() / len(df) * 100):.1f}%" for col in cat_cols}
        # if 'freq' in desc.index:
        #     data['freq'] = {col: desc.loc['freq', col] for col in cat_cols}
            
        data['Frequency Chart'] = {col: get_frequency_chart(df, col) for col in cat_cols}
        # if 'unique' in desc.index:
        #     data['unique'] = {col: desc.loc['unique', col] for col in cat_cols}
        data['Top 3 Values'] = {col: f"{df[col].value_counts().head(3).to_dict()}" for col in cat_cols}
        
        return data
    except Exception as e:
        print(f"Error in prepare_table_data_for_categorical_columns: {e}")
        print(f"cat_cols: {cat_cols}")
        print(f"cat_cols type: {type(cat_cols)}")
        return {}
    
def render_html_table(data, columns, table_style="border='1' style='border-collapse: collapse; text-align: center;'"):
    """Convert tabular data to HTML table"""
    # Header
    header = f"<tr><th></th>{''.join(f'<th><b>{col}</b></th>' for col in columns)}</tr>"
    
    # Data rows
    rows = []
    for row_name, row_data in data.items():
        cells = f"<td><b>{row_name}</b></td>{''.join(f'<td>{row_data[col]}</td>' for col in columns)}"
        rows.append(f"<tr>{cells}</tr>")
    
    return f"<table {table_style}>{header}{''.join(rows)}</table>"

def tidy_describe(df):
    desc = df.describe().round(2)

    # For each column, combine all rows into one multi-line string
    combined = desc.apply(
        lambda col: "\n".join(f"{idx}: {val}" for idx, val in col.items())
    )

    # Convert Series to DataFrame for nicer display
    combined_df = pd.DataFrame(combined).T  # single row with columns as columns

    return combined_df.style.background_gradient(cmap='Blues')

################################################
# Correlation Analysis
################################################    
def correlation_analysis(df):
    print("\n")
    print("Bivariate/multivariate analysis (relationships)")
    print("===============================================")
    
    get_pair_plots(df)
    get_correlation_matrix(df)
    get_boxplot_by_category(df)

def get_pair_plots(df):        
    '''Pair plot (comment if too slow)'''
    print("\n")
    print("Pair Plots (Numeric Columns):")
    print("-----------------------------")
    numeric_cols = get_numeric_cols(df)
    sns.pairplot(df[numeric_cols])
    plt.show()

def get_correlation_matrix(df):    
    # Correlation Heatmap
    print("\nCorrelation Heatmap (Numeric Columns):")
    print("--------------------------------------")
    plt.figure(figsize=(8, 6))
    numeric_cols = get_numeric_cols(df)
    sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm')
    plt.title("Correlation Heatmap")
    plt.show()
    
def get_boxplot_by_category(df):
    # Box plots: numeric columns grouped by each categorical column
    print("\nBOX PLOTS: Numeric Columns grouped by Categorical Columns")
    print("---------------------------------------------------------")
    numeric_cols = get_numeric_cols(df)
    cat_cols = get_cat_cols(df)
    for cat_col in cat_cols:
        n = len(numeric_cols)
        cols = min(n, 3)  # max 3 plots per row
        rows = math.ceil(n / cols)

        fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 5 * rows))
        fig.suptitle(f"Box Plots Grouped by '{cat_col}'", fontsize=16)
        
        # Flatten axes for consistent indexing
        axes = np.array(axes).reshape(-1)

        for i, num_col in enumerate(numeric_cols):
            sns.boxplot(x=cat_col, y=num_col, data=df, ax=axes[i])
            axes[i].set_title(f"{num_col} by {cat_col}")
            axes[i].tick_params(axis='x', rotation=45)

        # Turn off any unused subplots
        for j in range(i + 1, len(axes)):
            axes[j].axis('off')

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()
    
################################################
# Data Visualization Charts
################################################    
def get_histogram(df, numeric_col):
    fig, ax = plt.subplots(figsize=(2, 1.5))
    
    # Histogram (counts, no KDE here)
    hist_data = df[numeric_col].dropna()
    sns.histplot(
        df[numeric_col],
        ax=ax,
        bins=10,
        kde=False,
        edgecolor='black',
        color='skyblue',
        alpha=0.6,
        linewidth=0.5,
    )
    
    # Compute KDE
    from scipy.stats import gaussian_kde
    kde = gaussian_kde(hist_data)
    x_vals = np.linspace(hist_data.min(), hist_data.max(), 200)
    
    # Scale KDE to match histogram counts
    n = len(hist_data)
    bin_width = (hist_data.max() - hist_data.min()) / 10  # same as bins=10
    kde_scaled = kde(x_vals) * n * bin_width
    
    ax.plot(x_vals, kde_scaled, color='crimson', linewidth=1.2)
    
    # Minimalistic style
    ax.set_title(numeric_col, fontsize=10, fontweight='bold', pad=5)
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.tick_params(axis='y', labelsize=6, length=2)
    ax.set_xticks([])  # Remove x-axis ticks entirely
    
    # Remove top/right spines for cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Add count labels above each bar
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(
                f"{int(height)}", 
                (p.get_x() + p.get_width() / 2, height),
                ha='center', va='bottom',
                fontsize=9, color='dimgray', rotation=0, fontweight='bold'
            )
            
    # Reduce y-axis ticks (but keep informative range)
    ax.yaxis.set_major_locator(plt.MaxNLocator(3))
    ax.xaxis.set_major_locator(plt.MaxNLocator(4))
    
    histogram_image = plot_to_base64(fig)
    plt.close(fig)
    return histogram_image
    
def get_boxplot(df, col, width='100%', height='auto'):
    #########################################################################################
    # Calculate stats
    #########################################################################################
    series = df[col].dropna()
    
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower_whisker_limit = q1 - 1.5 * iqr
    upper_whisker_limit = q3 + 1.5 * iqr
    # Determine actual whisker ends (largest points within the 1.5*IQR fences)
    whisker_min = series[series >= lower_whisker_limit].min()
    whisker_max = series[series <= upper_whisker_limit].max()
    
    stats = {
        'min': series.min(),
        'whisker_min': whisker_min,
        'p5': series.quantile(0.05),
        'q1': series.quantile(0.25),
        'median': series.median(),
        'q3': series.quantile(0.75),
        'p95': series.quantile(0.95),
        'whisker_max': whisker_max,
        'max': series.max(),
        'mean': series.mean(),
        'std': series.std()
    }

    fig, ax = plt.subplots(figsize=(3, 3))
    ax.set_facecolor('white')  # or 'none' for transparent background
    
    # Draw horizontal boxplot, show mean as red dot, no fliers (outliers)
    sns.boxplot(x=series, 
                ax=ax, 
                showmeans=True,                                             # mean
                meanprops=dict(marker='o', markerfacecolor='red', markeredgecolor='red', markersize=6),
                
                showfliers=True,
                flierprops=dict(marker='o', color='black', markersize=5),   # outliers (dots)
                
                medianprops=dict(color='black'),                            # median line
                
                showcaps=True,
                capprops=dict(linewidth=1),                                 # caps (ends of whiskers)
                boxprops=dict(linewidth=1, facecolor='#f0f4f8'),                                 # box
                whiskerprops=dict(linewidth=1),                             # whiskers (lines)
                
                orient='h',                                                 # horizontal
    )
    
    # Remove y-axis ticks and spines
    ax.set_xticklabels([])
    ax.set_xlabel('')
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
    # Set x-axis limits slightly wider than min/max for padding
    xpad = (stats['max'] - stats['min']) * 0.1
    ax.set_xlim(stats['min'] - xpad, stats['max'] + xpad)
    
    #########################################################################################
    # Annotate min, lower whisker, Q1, median, Q3, upper whisker, max, p5, p95, mean
    #########################################################################################
    y_text = 0.9
    y_text_offset = 0.3
    toggle = True
    label_color = 'black'
    outlier_color = 'red'
    label_font_size = 14
    label_va = 'bottom'
    label_ha = 'center'
    
    # min and Lower whisker
    y_text = toggle_offset(y_text, y_text_offset, toggle); toggle = not toggle
    if stats['min'] < lower_whisker_limit:
        # min (outlier)
        ax.text(stats['min'], y_text, f"min\n(outlier)\n{format_decimal_if_needed(stats['min'])}", ha=label_ha, va=label_va, fontsize=label_font_size, color=outlier_color)
        
        # lower whisker
        y_text = toggle_offset(y_text, y_text_offset, toggle); toggle = not toggle
        ax.text(stats['whisker_min'], y_text, f"{format_decimal_if_needed(stats['whisker_min'])}", ha=label_ha, va=label_va, fontsize=label_font_size, color=label_color)
    else:
        # min
        ax.text(stats['min'], y_text, f"min\n{format_decimal_if_needed(stats['min'])}", ha=label_ha, va=label_va, fontsize=label_font_size, color=label_color)
    
    # Annotate Q1, median, Q3
    for key in ['q1', 'median', 'q3']:
        val = stats[key]
        val_str = format_decimal_if_needed(val)
        # label = f"{key}\n{val_str}"    
        label = f"{val_str}"
        y_text = toggle_offset(y_text, y_text_offset, toggle); toggle = not toggle
        ax.text(val, y_text, label, ha=label_ha, va=label_va, fontsize=label_font_size, color=label_color)

    # Upper whisker and max
    y_text = toggle_offset(y_text, y_text_offset, toggle); toggle = not toggle
    if stats['max'] > upper_whisker_limit:
        # upper whisker
        ax.text(stats['whisker_max'], y_text, f"{format_decimal_if_needed(stats['whisker_max'])}", ha=label_ha, va=label_va, fontsize=label_font_size, color=label_color)
        
        # max (outlier)
        y_text = toggle_offset(y_text, y_text_offset, toggle); toggle = not toggle
        ax.text(stats['max'], y_text, f"max\n(outlier)\n{format_decimal_if_needed(stats['max'])}", ha=label_ha, va=label_va, fontsize=label_font_size, color=outlier_color)
    else:
        # max
        ax.text(stats['max'], y_text, f"max\n{format_decimal_if_needed(stats['max'])}", ha=label_ha, va=label_va, fontsize=label_font_size, color=label_color)    
        
    #########################################################################################
    # Annotate p5, p95, mean
    #########################################################################################
    # Plot dots for p5, p95
    ax.plot(stats['p5'], 0, marker='o', color='purple', markersize=5, zorder=5)
    ax.plot(stats['p95'], 0, marker='o', color='purple', markersize=5, zorder=5)
    
    # Annotate p5, p95, mean
    ax.text(stats['p5'], -0.4, f"p5\n{format_decimal_if_needed(stats['p5'])}", ha=label_ha, va=label_va, fontsize=12, color='purple')
    ax.text(stats['p95'], -0.4, f"p95\n{format_decimal_if_needed(stats['p95'])}", ha=label_ha, va=label_va, fontsize=12, color='purple')
    ax.text(stats['mean'], -0.4, f"mean\n{format_decimal_if_needed(stats['mean'])}", ha=label_ha, va=label_va, fontsize=12, color='red')
    
    #########################################################################################
    # Standard Deviation
    #########################################################################################
    std1_low = stats['mean'] - stats['std']
    std1_high = stats['mean'] + stats['std']
    std2_low = stats['mean'] - 2 * stats['std']
    std2_high = stats['mean'] + 2 * stats['std']

    # ±1 std
    ax.axvspan(std1_low, std1_high, color='blue', alpha=0.1, label=f'±1σ ({format_decimal_if_needed(stats["std"])})\n{format_decimal_if_needed(std1_low)} - {format_decimal_if_needed(std1_high)}') # Shade ±1 std range (light blue)

    # ±2 std
    ax.axvspan(std2_low, std2_high, color='green', alpha=0.05, label=f'±2σ \n{format_decimal_if_needed(std2_low)} - {format_decimal_if_needed(std2_high)}') # Shade ±2 std range (light green)

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.45), ncol=2, frameon=False)

    #########################################################################################
    # Title
    #########################################################################################
    ax.set_title(col, fontsize=18, loc='center', fontweight='bold', color='black', pad=40)

    #########################################################################################
    # Return plot image
    #########################################################################################
    plt.tight_layout()
    plot_image = plot_to_base64(fig, width=width, height=height)
    plt.close(fig)
    return plot_image

def get_frequency_chart(df, col, width='100%', height='auto'):
    """Generate frequency bar chart for categorical column"""
    
    #############################################
    # Using seaborn library's in-built function
    #############################################
    # plt.figure(figsize=(6, 3))
    # sns.countplot(y=df[col], order=df[col].value_counts().index)
    # plt.title(f"Count Plot of {col}")
    # plt.show()
    
    #############################################
    # Custom Plot (without using seaborn library)
    #############################################
    fig, ax = plt.subplots(figsize=(4, 2.5))
    
    value_counts = df[col].value_counts()
    
    # Create bar chart
    bars = ax.bar(range(len(value_counts)), value_counts.values, alpha=0.7)
    ax.set_xticks(range(len(value_counts)))
    ax.set_xticklabels(value_counts.index, rotation=45, ha='right', fontsize=8)
    ax.set_xlabel(f'{col}\n({len(value_counts)} unique)', fontsize=15)
    ax.set_ylabel('Count', fontsize=15)
    ax.set_yticks([])  # Hide y-axis ticks
    ax.set_yticklabels([])  # Hide y-axis labels
    ax.tick_params(axis='y', labelsize=8)
    
    # Add value labels on bars
    for bar, count in zip(bars, value_counts.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(value_counts.values) * 0.01,
                str(count), ha='center', va='bottom', fontsize=12)
    
    #########################################################################################
    # Return plot image
    #########################################################################################
    plt.tight_layout()
    plot_image = plot_to_base64(fig, width=width, height=height)
    plt.close(fig)
    return plot_image

################################################
# Data Cleaning
################################################
def missing_values_print(df):
    # Check missing values - COUNT
    print("Missing values before cleaning: COUNT")
    print(df.isnull().sum())

    # Check missing values - PERCENTAGE
    print("\n")
    print("Missing values before cleaning: PERCENTAGE")
    print((df.isnull().sum() / len(df)) * 100)

def missing_values_impute_categorical_mode(
    df, 
    categorical_cols=None
):
    print('\n')
    print('Imputing each categorical col one-by-one')
    print('----------------------------------------')
    if categorical_cols is None:
        categorical_cols = get_cat_cols(df)
    
    # use mode imputation
    for col in categorical_cols:
        if df[col].isnull().sum() > 0:
            mode_val = df[col].mode()[0]
            df[col].fillna(mode_val, inplace=True)
            print(f"Filled missing {col} values with mode: {mode_val}")
        else:
            print(f'no missing values found for col "{col}"')

def missing_values_impute_numerical_medians(
    df, 
    numerical_cols=None
):
    print('\n')
    print('Imputing each numerical col one-by-one')
    print('---------------------------------------')
    if numerical_cols is None:
        numerical_cols = get_numeric_cols(df)
    
    # use median imputation
    for col in numerical_cols:
        if df[col].isnull().sum() > 0:
            missing_values_impute_numerical_median(df, col)
        else:
            print(f'no missing values found for col "{col}"')
    
def missing_values_impute_numerical_mean(df, numerical_col):
    mean_val = df[numerical_col].mean()
    df[numerical_col] = df[numerical_col].fillna(mean_val, inplace=True)
    print(f"Filled missing {numerical_col} values with mean: {mean_val}")

def missing_values_impute_numerical_median(df, numerical_col):
    median_val = df[numerical_col].median()
    df[numerical_col] = df[numerical_col].fillna(median_val, inplace=True)
    print(f"Filled missing {numerical_col} values with median: {median_val}")
    
def missing_values_impute_numerical_constant(df, numerical_col, constant_val):
    df[numerical_col] = df[numerical_col].fillna(constant_val, inplace=True)
    print(f"Filled missing {numerical_col} values with constant: {constant_val}")