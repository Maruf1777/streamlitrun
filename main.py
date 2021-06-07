import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
sns.set_theme()

st.set_option('deprecation.showPyplotGlobalUse', False)
st.set_page_config(
    page_title="Statistics",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded")

ds = pd.read_csv('Test.csv')
ds["date"] = pd.to_datetime(ds["date"])
ds['day'] = ds['date'].dt.day
ds['rpm_min'] = ds['rpm']
ds['rpm_max'] = ds['rpm']
ds['hour'] = ds['date'].dt.hour

add_selectbox = st.sidebar.selectbox(
    'Type of Calculations',
    ('Volume', 'STD'))
st.sidebar.write("**Volume**- Displays All Loads Information\n**STD**- Displays Mean, Max, Min Values")
user_input = st.sidebar.text_input("PLease Enter State")
st.sidebar.write("*Example: 'CA'*")


@st.cache(suppress_st_warning=True)
def avarage_1(state):
    man = ds.loc[ds['st1'] == state]
    aggregation_functions = {'wn': 'first',
                             'cod2': 'first',
                             'st2': 'first',
                             'price': 'mean',
                             'rpm_min': 'min',
                             'rpm': 'mean',
                             'rpm_max': 'max',
                             'miles': 'mean'}
    df_new = man.groupby(ds['wd']).aggregate(aggregation_functions).round(2).sort_values("wn", ascending=True)
    return df_new


avg_df = avarage_1(user_input)


@st.cache(suppress_st_warning=True)
def std(state):
    man = ds.loc[ds['st1'] == state]

    man = man.drop(['zip1', 'zip2', 'id', 'tz', 'st1',
                    'cit2', 'cit1', 'cod1', 'date', 'day'], axis=1)

    man = man.groupby(['st2', 'wn', 'wd', 'hour'], as_index=False).agg(
        dict(cod2="first",
             price="mean",
             miles='mean',
             rpm_min="min",
             rpm="mean",
             rpm_max="max")).round(2)
    return man


@st.cache(suppress_st_warning=True)
def vol(state):
    ca = ds.loc[ds['st1'] == state]

    ca = ca.drop(['zip1', 'zip2', 'id', 'tz', 'st1',
                  'cit2', 'cit1', 'cod1', 'date', 'day'], axis=1)
    return ca


@st.cache(suppress_st_warning=True)
def typ(state):
    if add_selectbox == "Volume":
        return vol(state)
    elif add_selectbox == "STD":
        return std(state)

col1, col2, col3 = st.beta_columns([1, 1, 2])
col1.write("**Main**-Overall Information From Inital State  \n **1-DS**: Specific State Information.")
col2.write("**Main-2**- Overall Information From Arrive State \n **2-DS**: Specific State Information.")
layout_type = st.multiselect('Layout Type',
                             ['Main', '1-DS', 'Main-2', '2-DS'],
                             ['Main'])

df = typ(user_input)
state_list = list(df.st2.unique())


@st.cache(suppress_st_warning=True)
def second_state(state):
    m = df.loc[df['st2'] == state]
    m = m.drop(['st2'], axis=1)
    return m
# print(second_state("GA"))

@st.cache(suppress_st_warning=True)
def mm(state):
    vol_df = vol(user_input)
    man = vol_df.loc[vol_df['st2'] == state]
    aggregation_functions = {'wn': 'first',
                             'cod2': 'first',
                             'price': 'mean',
                             'rpm_min': 'min',
                             'rpm': 'mean',
                             'rpm_max': 'max',
                             'miles': 'mean'}
    df_new = man.groupby(man['wd']).aggregate(aggregation_functions).round(2).sort_values("wn", ascending=True)
    return df_new


try:
    col1, col2 = st.beta_columns([1, 1])

    ds.sort_values(by=['wn'], inplace=True)
    fig = px.scatter_polar(df, r="rpm", theta="wd", color="miles", template="plotly",
                           color_discrete_sequence=px.colors.sequential.Plasma_r,
                           animation_frame="st2",
                           size_max=1, height=750,
                           width=750, hover_name="cod2")

    if user_input == '' or \
            layout_type != ['Main'] and \
            layout_type != ['Main', '1-DS'] and \
            layout_type != ['Main', '1-DS', 'Main-2'] and \
            layout_type != ['Main', '1-DS', 'Main-2', '2-DS']:
        pass
    else:
        col1.write(f"### **Avarage Loads Statistics from {user_input}**")
        col1.table(avg_df.style.format({'rpm': '{:.1f}',
                                        'rpm_min': '{:.1f}',
                                        'rpm_max': '{:.1f}',
                                        'price': '{:.1f}',
                                        'miles': '{:.1f}'}))
        col2.write(f"### **Graph of Loads From {user_input}**")

        col2.plotly_chart(fig)
except Exception as e:
    pass
try:
    name = []
    if '1-DS' in layout_type:
        name.clear()
        ds_1 = st.selectbox("Select State", state_list, 0)
        name.append(ds_1)
        ds2_mean = mm(ds_1)
        df2 = second_state(ds_1)
        df2 = df2.sort_values("wn", ascending=True)


        sw = df2['miles'].sort_values()
        sw_01 = (sw - sw.min()) / (sw.max() - sw.min())
        sw_colors = {n: mpl.colors.rgb2hex(c) for n, c in zip(sw, mpl.cm.viridis(sw_01))}
        rmax = df2['rpm'].nlargest().iloc[0]
        rmin = df2['rpm'].nsmallest().iloc[0]
        # print(rmax)
        col1, col2 = st.beta_columns([2, 2])
        col1.write(f"### **Avarage Loads Statistics from {user_input} to {ds_1}**")
        col1.table(ds2_mean.style.format({'rpm': '{:.1f}',
                                          'rpm_min': '{:.1f}',
                                          'rpm_max': '{:.1f}',
                                          'price': '{:.1f}',
                                          'miles': '{:.1f}'}))
        sns.set_theme()
        miles_max = df2['miles'].nlargest().iloc[-1]
        miles_min = df2['miles'].nsmallest().iloc[-1]

        fig_dims = (10, 5)
        fig, ax = plt.subplots(figsize=fig_dims)
        fig = sns.scatterplot(x="wd", y="rpm",
                              hue="miles",
                              palette="rocket_r",
                              hue_order='wn', size='miles',
                              sizes=(5, 50), linewidth=0.8,
                              data=df2, ax=ax,
                              hue_norm=(miles_min - 200, miles_max + 200))
        col2.write(f"### **Graph from {user_input} to {ds_1}**")
        col2.pyplot()

        print(df2)

        fig_3 = px.strip(df2, x='hour', y='rpm',
                         color='miles', stripmode='group',
                         category_orders={'miles': sw.to_list()[::1]},
                         color_discrete_map=sw_colors,
                         animation_frame="wd",
                         animation_group="cod2",
                         height=600,width=1300,
                         hover_name="cod2")

        fig_3.update_yaxes(range=[1.5, rmax + 0.5],
                           showgrid=True, gridwidth=1, gridcolor='LightPink', nticks=10)

        fig_3.update_xaxes(showgrid=True, gridwidth=1,
                           gridcolor='LightPink', nticks=26, range=[-0.5, 24.5])
        st.plotly_chart(fig_3)
        # print(str(name[0]))
    df3 = typ(str(name[0]))
    state_list2 = list(df3.st2.unique())
    avg2_df = avarage_1(str(name[0]))
    if 'Main-2' in layout_type:
        fig2 = px.scatter_polar(df3, r="rpm", theta="wd",
                                color="miles", template="plotly",
                                color_discrete_sequence=px.colors.sequential.Plasma_r,
                                animation_frame="st2",
                                size_max=1, height=750, width=750, hover_name="cod2")

        col1, col2 = st.beta_columns([1, 1])
        col1.write(f"### **Avarage Loads Statistics from {name[0]}**")
        col2.write(f"### **Graph of Loads From {name[0]}**")
        col2.plotly_chart(fig2)
        col1.table(avg2_df.style.format({'rpm': '{:.1f}',
                                         'rpm_min': '{:.1f}',
                                         'rpm_max': '{:.1f}',
                                         'price': '{:.1f}',
                                         'miles': '{:.1f}'}))
        # ds_2 = st.selectbox("Select 2nd State", state_list2, 0)
    if '2-DS' in layout_type:

        ds_2 = st.selectbox("Select 2nd State", state_list2, 0)
        ds2_mean = mm(ds_2)
        df2 = second_state(ds_2)
        df2 = df2.sort_values("wn", ascending=True)

        sw = df2['miles'].sort_values()
        sw_01 = (sw - sw.min()) / (sw.max() - sw.min())
        sw_colors = {n: mpl.colors.rgb2hex(c) for n, c in zip(sw, mpl.cm.viridis(sw_01))}
        rmax = df2['rpm'].nlargest().iloc[-1]
        rmin = df2['rpm'].nsmallest().iloc[-1]

        col1, col2 = st.beta_columns([2, 2])
        col1.write(f"### **Avarage Loads Statistics from {name[0]} to {ds_2}**")
        col1.table(ds2_mean.style.format({'rpm': '{:.1f}',
                                          'rpm_min': '{:.1f}',
                                          'rpm_max': '{:.1f}',
                                          'price': '{:.1f}',
                                          'miles': '{:.1f}'}))

        miles_max = df2['miles'].nlargest().iloc[-1]
        miles_min = df2['miles'].nsmallest().iloc[-1]

        fig_dims = (10, 5)
        fig, ax = plt.subplots(figsize=fig_dims)
        fig = sns.scatterplot(x="wd", y="rpm",
                              hue="miles", palette="rocket_r",
                              hue_order='wn', size='miles',
                              sizes=(5, 50), linewidth=0.8, data=df2, ax=ax,
                              hue_norm=(miles_min - 200, miles_max + 200))

        col2.write(f"### **Graph from {name[0]} to {ds_2}**")
        col2.pyplot()

        fig_3 = px.strip(df2, x='hour', y='rpm', color='miles', stripmode='overlay',
                         category_orders={'miles': sw.to_list()[::1]},
                         color_discrete_map=sw_colors,
                         animation_frame="wd",
                         animation_group='wd', height=600,
                         width=1300,
                         hover_name="cod2")

        fig_3.update_yaxes(range=[1.5, rmax + 0.5],
                           showgrid=True, gridwidth=1, gridcolor='LightPink', nticks=10)

        fig_3.update_xaxes(showgrid=True,
                           gridwidth=1, gridcolor='LightPink', nticks=26, range=[-0.5, 24.5])
        st.plotly_chart(fig_3)

except Exception as e:
    pass