import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import csv
import math
import cv2
import pandas as pd
import datetime
import plotly.figure_factory as ff
import plotly.graph_objects as go

def app():
    st.title('ダストダッシュボード')

    #画像用のfigureインスタンスを作成
    fig = plt.figure()

    #日付を作成
    start_date = datetime.datetime.strptime('2022-01-01', '%Y-%m-%d').strftime('%Y-%m-%d')

    #データ準備
    place = {
        'センサー設置場所': ['搬入', '成形工程', '焼結工程', '加工工程', '製造事務所集中管理室', '金型制作', '搬入製品置場', '研究開発部門', 'エントランス', '食堂'], 
        'sensor_id' : ['sensor1', 'sensor2', 'sensor3', 'sensor4', 'sensor5', 'sensor6', 'sensor7', 'sensor8', 'sensor9', 'sensor10'],
        'x座標' : [225, 223, 251, 649, 475, 463, 649, 873, 926, 924],
        'y座標' : [168, 378, 671, 648, 408, 170, 417, 341, 504, 680]
    }

    df = pd.DataFrame(place)
    df1 = pd.read_csv('./data/dust_dummy.csv')
    df_merge = pd.merge(df1, df)

    #レイアウト
    #sidebar
    st.sidebar.write('フィルター')

    #サイドバーで日付を選択できるようにする
    """
    month_list = list(df_merge['Datetime'].unique())
    selected_month = st.sidebar.multiselect(
        '表示する月を選択：',
        month_list,
        month_list
    )
    """
    #カレンダーから開始日と終了日を選択する
    date_range = st.sidebar.date_input('期間を選択', [datetime.date(2022, 1,1), datetime.date(2022, 4, 21) ])
    start = datetime.datetime.combine(date_range[0], datetime.datetime.min.time())
    end = datetime.datetime.combine(date_range[1], datetime.datetime.min.time())

    #選ばれた月と工場が反映されるようにdf_mergeを更新
    df_merge = df_merge[(pd.to_datetime(df_merge['Datetime']) >= start) & (pd.to_datetime(df_merge['Datetime']) <= end)]
    #df_merge = df_merge[df_merge['Datetime'].isin(selected_month)]

    df_pivot = pd.pivot_table(df_merge, values='concentration (ug/m^3)', index=['Datetime'],columns='センサー設置場所', aggfunc=np.sum)

    #2カラム追加
    column1, column2 = st.columns(2)

    #テーブル
    column1.subheader('粉じん量詳細テーブル')
    df_table = df_merge[['Datetime', 'sensor_id', 'concentration (ug/m^3)', 'センサー設置場所']]
    df_table = df_table.sort_values('Datetime')
    column1.dataframe(df_table.style.highlight_max(axis=0), width=800)

    #マッピング
    column2.subheader('エリア別平均粉じん量')
    column2.write('平均粉じん量が1.2ug/m^3未満の場合は緑、1.2以上1.3未満は青、1.3以上は赤で示されます。')

    # 1枚目の画像を読み取り
    img = cv2.imread('./data/diagram.png')

    #センサーごとの埃の量の平均値をマップにplot
    sensors = df_merge['sensor_id'].unique()
    for sensor in sensors:
        param = df_merge[df_merge['sensor_id'] == sensor]
        #print(param['concentration (ug/m^3)'].mean())
        cv2.circle(img,
        center=( param['x座標'].min(), param['y座標'].min()),
        radius=60,
        color=(0, 255, 0) if param['concentration (ug/m^3)'].mean() <= 1.2 else (0, 0, 255) if 1.2 <= param['concentration (ug/m^3)'].mean() > 1.3 else (255, 0, 0),
        
        thickness=-1,
        lineType=cv2.LINE_4,
        shift=0)

    # 結果を表示する
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()

    #streamlitで表示
    column2.pyplot(fig)

    #bar chart
    #積み上げ棒グラフ
    st.subheader('エリア別粉じん量推移')
    fig_bar = go.Figure()
    for col in df_pivot.columns:
        fig_bar = fig_bar.add_trace(go.Bar(
        x=df_pivot.index,
        y=df_pivot[col].values,
        name = col
    ))
    fig_bar.update_layout (
        barmode='stack')

    st.plotly_chart(fig_bar, use_container_width=True)

