import streamlit as st
import numpy as np
import pandas as pd
import datetime as dt
import plotly.figure_factory as ff
import plotly.graph_objects as go


def app():
    # 今日の日付を取得
    now = dt.datetime.now()
    now_str = 'ページ更新日時 : ' + str(now)
    now_rjust = '{:<30}'.format(now_str)

    #データの準備
    df = pd.read_csv('./data/power_consumption_dunmmy.csv')

    #空白値の削除
    df = df.dropna()
    df = df.sort_values(by='月', ascending=False)
    m_order = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    df['月'] = sorted(df['月'], key=m_order.index)

    #レイアウト
    #sidebar
    st.sidebar.write('フィルター')

    #サイドバーで月を選択できるようにする
    month_list = list(df['月'].unique())
    selected_month = st.sidebar.multiselect(
        '表示する月を選択：',
        month_list,
        month_list
    )

    #サイドバーで工場を選択できるようにする
    line_list = list(df['工場名'].unique())
    selected_line = st.sidebar.multiselect(
        '表示する工場を選択：',
        line_list,
        line_list
    )

    #選ばれた月と工場が反映されるようにdfを更新
    df = df[df['月'].isin(selected_month)&df['工場名'].isin(selected_line)]

    df_pivot = pd.pivot_table(df, values='消費電力', index=['月'],columns='工場名', aggfunc=np.sum)
    df_pivot = df_pivot.reindex(index=['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'])

    #line chart
    #工場名別
    fig = go.Figure()
    for col in df_pivot.columns:
        fig_line = fig.add_trace(go.Scatter(
            x=df_pivot.index,
            y=df_pivot[col].values,
            name = col,
            mode = 'markers+lines',
            line = dict(shape='linear'),
            connectgaps=True
            ))
    fig_line.update_layout (
        title_text="工場別 消費電力量 月別推移")

    #総電力
    df_line = df[['月', '消費電力']].groupby('月', as_index=False).sum()
    df_line['月'] = sorted(df_line['月'], key=m_order.index)
    data_line = go.Scatter(x=df_line['月'], y = df_line['消費電力'].values, marker=dict(color='#2b7bba'))
    fig_line_sum = go.Figure(data=data_line)
    fig_line_sum.update_layout (
        title_text="総消費電力量 月別推移")

    #bar chart
    #積み上げ棒グラフ
    fig = go.Figure()
    for col in df_pivot.columns:
        fig_bar = fig.add_trace(go.Bar(
            x=df_pivot.index,
            y=df_pivot[col].values,
            name = col
            ))
    fig_bar.update_layout (
        title_text="工場別消費電力量推移", barmode='stack')

    # fig_bar = go.Figure(data=data, layout=layout)

    #pie chart
    df_pie = df[['工場名', '消費電力']].groupby('工場名').sum() / df['消費電力'].sum()
    data_pie = go.Pie(labels=df_pie.index,values=df_pie['消費電力'], hole=.3)
    layout_pie = go.Layout(
        title=go.layout.Title(text="消費電力量内訳"),
        margin=go.layout.Margin(l=75, r=75, b=75, t=75))
    fig_pie = go.Figure(data=data_pie, layout=layout_pie)

    #最大、最小、総合計、平均値の取得
    vmax = df['消費電力'].max() * 100
    vmin = df['消費電力'].min() * 100
    vsum = df['消費電力'].sum() * 100
    vmean = df['消費電力'].mean() * 100

    #main画面
    st.title('消費電力ダッシュボード')
    #st.write(now_rjust)

    #card用に4カラム追加
    column1, column2, column3, column4 = st.columns(4)
    # column1.subheader('最大消費電力量')
    column1.metric(label='平均消費量', value=str(round(vmean/1000, 2)) + 'kWh')
    column2.metric(label='最大消費量', value=str(round(vmax/1000, 2)) + 'kWh')
    column3.metric(label='最小消費量', value=str(round(vmin/1000, 2)) + 'kWh')
    column4.metric(label='合計消費量', value=str(round(vsum/1000000, 2)) + 'MWh')

    #chart用に2カラム追加
    column5, column6 = st.columns(2)
    column5.plotly_chart(fig_line_sum, use_container_width=True)
    column5.plotly_chart(fig_bar, use_container_width=True)

    column6.plotly_chart(fig_pie)
    column6.plotly_chart(fig_line, use_container_width=True)

    st.subheader('消費電力詳細テーブル')
    df_table = df
    df_table['消費電力'] = df_table['消費電力'].astype('int') / 10
    df_table.rename(columns={'消費電力': '消費電力量(kWh)'})
    st.dataframe(df_table.style.highlight_max(axis=0), width=800)

