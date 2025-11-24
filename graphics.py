import pandas as pd

df = pd.read_csv('results_alt.csv', sep=';', index_col=False)

df['config'] = df.apply(
    lambda row: f"{row['constructor']}-{row['strategy']}",
    axis=1
)

df_max = (df[['instance', 'value']]
          .groupby('instance')
          .aggregate({'value': 'min'})
          .reset_index()
          .rename(columns={'value': 'min_value'}))

df = df.merge(df_max, on=['instance'])

intances_count = df['instance'].nunique()

df['tau_value'] = df['value'] / df['min_value']
df['perc'] = 1 / intances_count * 100

#Prepare plotting for value
df = df.sort_values(by=['tau_value'])
df['cum_perc'] = df.groupby('config')['perc'].cumsum()
df = df.groupby(['config', 'tau_value'])[['cum_perc']].max().reset_index()

for config in df['config'].unique():
    config_line = f"{config}:\n"
    df_config = df[df['config'] == config]
    for _, row in df_config.iterrows():
        config_line += f"({row['tau_value']},{row['cum_perc']})"
    config_line += "\n"
    print(config_line)