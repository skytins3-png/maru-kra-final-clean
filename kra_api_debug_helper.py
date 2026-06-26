import streamlit as st, requests
st.title('🐎 경마 API 점검')
url=st.text_area('URL')
key=st.text_input('KEY',type='password')
if st.button('점검'):
    try:
        r=requests.get(url.replace('{serviceKey}',key).replace('{api_key}',key),timeout=15); st.metric('HTTP',r.status_code); st.text(r.text[:5000])
    except Exception as e: st.error(e)
