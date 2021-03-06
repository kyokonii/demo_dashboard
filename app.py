import streamlit as st
from multiapp import MultiApp
from apps import qcd, power, dust # import your app modules here

app = MultiApp()

# Add all your application here
# app.add_app("Home", home.app)
# app.add_app("Data Stats", data_stats.app)
app.add_app ('消費電力ダッシュボード', power.app)
app.add_app ('QCDダッシュボード', qcd.app)
app.add_app ('ダストダッシュボード', dust.app)

# The main app
app.run()
