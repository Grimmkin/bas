import segno

import streamlit as st
from streamlit import net_util
from streamlit.web.server import server_util

# if __name__ == "__main__":
#     internal_ip = net_util.get_internal_ip()
#     if internal_ip:
#         url = server_util.get_url(internal_ip)

#     segno.make_qr(url).save("./assets/network.png", border=0, scale=3.6)

def generate_qr():
    internal_ip = net_util.get_internal_ip()
    if internal_ip:
        url = server_util.get_url(internal_ip)

    segno.make_qr(url).save("./assets/network.png", border=0, scale=3.6)

def UI_network():
    generate_qr()
    st.image("./assets/network.png")