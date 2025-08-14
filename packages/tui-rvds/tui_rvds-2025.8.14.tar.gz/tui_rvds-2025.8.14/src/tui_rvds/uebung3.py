import numpy as np
import pandas as pd
from checkmarkandcross import image


# TODO prüfen, ob Spalten überhaupt im df sind, um Exceptions zu vermeiden


def aufgabe1_1(df_raw: pd.DataFrame):
    if len(df_raw) != 2076 or len(df_raw.columns) != 196:
        return image(False)

    for col in df_raw.columns:
        if col not in ('lfdn', 'duration') and not col.startswith('v_'):
            return image(False)

    return image(True)


def aufgabe1_2(df: pd.DataFrame):
    if len(df) != 2076 or len(df.columns) != 196:
        return image(False)

    for col in df.columns:
        if col.startswith('v_'):
            return image(False)

    for required in ('int_techdevre1', 'meus_government1', 'act_contactpoliticans1'):
        if required not in df.columns:
            return image(False)

    return image(True)


def aufgabe2_1(df: pd.DataFrame):
    if len(df.columns) != 11:
        return image(False)

    for col in [
        'lfdn1',
        'duration1',
        'age1',
        'sex1',
        'edu1',
        'federalstate1',
        'int_pol1',
        'int_enccpol1',
        'int_ccresearch1',
        'int_techdevre1',
        'int_techdevhyd1',
    ]:
        if col not in df.columns:
            return image(False)

    return image(True)


def aufgabe2_2(df: pd.DataFrame):
    for col in [
        'lfdn1',
        'duration1',
        'age1',
        'sex1',
        'edu1',
        'federalstate1',
        'int_pol1',
        'int_enccpol1',
        'int_ccresearch1',
        'int_techdevre1',
        'int_techdevhyd1',
    ]:
        if df[col].dtype != np.int64:
            return image(False)

    return image(True)


def aufgabe3_1(df: pd.DataFrame):
    if len(df['sex1'].unique()) != 3:
        return image(False)

    for val in [None, 1, 2]:
        if val not in df['sex1'].unique():
            return image(False)

    return image(True)


def aufgabe3_2(df: pd.DataFrame):
    if len(df['region1'].unique()) != 5:
        return image(False)

    if ((df['federalstate1'] == 5) & (df['region1'] != 'Nord')).any():
        return image(False)
    if ((df['federalstate1'] == 8) & (df['region1'] != 'Ost')).any():
        return image(False)

    return image(True)


def aufgabe3_3(df: pd.DataFrame):
    return image(len(df['age1_grp'].unique()) == 4 and None not in df['age1_grp'].unique())


def aufgabe3_4(df: pd.DataFrame):
    if len(df['edu1_grp'].unique()) != 3:
        return image(False)

    for x, y in [
        (1, 3),
        (1, 4),
        (1, 5),
        (2, 3),
        (2, 4),
        (2, 5),
        (3, 4),
        (3, 5),
    ]:
        if len(df[(df['edu1'] == x) | (df['edu1'] == y)]['edu1_grp'].unique()) != 2:
            return image(False)

    for x, y in [
        (1, 2),
        (4, 4),
    ]:
        if len(df[(df['edu1'] == x) | (df['edu1'] == y)]['edu1_grp'].unique()) != 1:
            return image(False)

    return image(True)


def aufgabe3_5(df: pd.DataFrame):
    cols = ['int_pol1', 'int_enccpol1', 'int_ccresearch1', 'int_techdevre1', 'int_techdevhyd1']

    for col in cols:
        if col not in df.columns:
            return image(False)

    for col in cols:
        if len(df[(df[col] == 1) | (df[col] == 2)][f'{col}_grp'].unique()) != 1:
            return image(False)

        if len(df[df[col] == 3][f'{col}_grp'].unique()) != 1:
            return image(False)

        if len(df[(df[col] == 4) | (df[col] == 5)][f'{col}_grp'].unique()) != 1:
            return image(False)

        if len(df[df[col] == 99][f'{col}_grp'].unique()) != 1:
            return image(False)

        if df[f'{col}_grp'].isna().any():
            return image(False)

    return image(True)


def aufgabe4_1(df: pd.DataFrame):
    # cols
    if df.isna().all().any():
        return image(False)

    # rows
    if df.isna().all(axis=1).any():
        return image(False)

    return image(True)


def aufgabe4_2(df: pd.DataFrame):
    if df['duration1'].isna().any():
        return image(False)

    if (df['duration1'] < 360).any():
        return image(False)

    if len(df) != 1907:
        return image(False)

    return image(True)


def aufgabe4_3(df: pd.DataFrame):
    if len(df) != 1862:
        return image(False)

    for col in [
        'int_pol1_grp',
        'int_enccpol1_grp',
        'int_ccresearch1_grp',
        'int_techdevre1_grp',
        'int_techdevhyd1_grp'
    ]:
        if len(df[col].unique()) != 3:
            return image(False)

    return image(True)


def aufgabe6_1(df: pd.DataFrame):
    if len(df) != 1062 or len(df.columns) != 265:
        return image(False)

    for col in [
        'lfdn2',
        'lfdn1',
        'dispcode2',
        'duration2',
        'int_pol2',
        'int_enccpol2',
        'int_ccresearch2',
        'int_techdevre2',
        'int_techdevhyd2',
        'int_energysaving2',
        'v_25',
        'v_26',
        'v_27',
        'v_28',
        'v_29',
        'v_234',
        'exexp_discuss2',
        'exexp_varied2',
        'exexp_events2',
        'quart_part2',
        'quart_havingsay2',
        'quart_fingains2',
        'attenpol_shortflightban2',
        'attenpol_heatpumps2',
        'attenpol_pvbuildings2',
        'date_of_last_access2',
    ]:
        if col not in df.columns:
            return image(False)

    return image(True)


def aufgabe6_2(df: pd.DataFrame):
    required_columns = [
        'lfdn1',
        'lfdn2',
        'duration2',
        'int_pol2',
        'int_enccpol2',
        'int_ccresearch2',
        'int_techdevre2',
        'int_techdevhyd2',
    ]

    if len(df.columns) != len(required_columns):
        return image(False)

    for rc in required_columns:
        if rc not in df.columns:
            return image(False)

    return image(True)


def aufgabe6_3(df: pd.DataFrame):
    if not isinstance(df['int_pol2_grp'].dtype, pd.CategoricalDtype):
        return image(False)

    int_pol2_grp_should = ['großes Interesse', 'mittleres Interesse', 'geringes Interesse']
    int_pol2_grp_is = df['int_pol2_grp'].unique()

    if len(int_pol2_grp_is) != len(int_pol2_grp_should):
        return image(False)

    for c in int_pol2_grp_should:
        if c not in int_pol2_grp_is:
            return image(False)

    return image(True)


def aufgabe6_4(df: pd.DataFrame):
    if len(df) != 990 or len(df.columns) != 27:
        return image(False)

    for col in [
        'lfdn1',
        'int_pol1',
        'int_pol1_grp',
        'int_pol2_grp',
    ]:
        if col not in df.columns:
            return image(False)

    return image(True)
