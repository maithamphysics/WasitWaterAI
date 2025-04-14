# app.py - Enhanced Wasit Water Management AI with PyDeck Maps
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from scipy.optimize import minimize
import math
import random
import requests
from PIL import Image
from sklearn.ensemble import RandomForestRegressor
import time
from tenacity import retry, stop_after_attempt, wait_exponential
import pydeck as pdk  # Added PyDeck import

# ================
# CONFIGURATION
# ================
st.set_page_config(
    page_title="نظام ذكي لإدارة المياه - واسط",
    page_icon="💧",
    layout="wide"
)

# Enhanced Arabic font and styles
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Tajawal', sans-serif;
    direction: rtl;
    text-align: right;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display:none;}
.stMap {border-radius: 10px;}
.mapboxgl-canvas {border-radius: 10px;}
.stCameraInput {direction: ltr;}  /* Camera input works better LTR */
.loading-spinner {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100px;
    flex-direction: column;
}
</style>
""", unsafe_allow_html=True)

# ================
# CORE FUNCTIONS (Enhanced with Error Handling)
# ================
class WaterAI:
    # ... [Keep all existing WaterAI methods unchanged] ...

# ================
# STREAMLIT UI (Enhanced with PyDeck Maps)
# ================
def show_loading_spinner():
    """عرض مؤشر التحميل"""
    st.markdown("""
    <div class="loading-spinner">
        <div style="font-size: 20px; margin-bottom: 10px;">جاري تحميل البيانات...</div>
        <div class="spinner-border text-primary" role="status">
            <span class="sr-only">Loading...</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_arabic_map(locations):
    """إنشاء خريطة تفاعلية بالعربية"""
    locations['coordinates'] = locations.apply(lambda row: [row['lon'], row['lat']], axis=1)
    locations['color'] = locations['score'].apply(
        lambda x: [0, 168, 0] if x > 90 else [255, 170, 0] if x > 80 else [255, 87, 51]
    )
    
    return pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=32.5,
            longitude=45.5,
            zoom=7,
            pitch=40
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=locations,
                get_position="coordinates",
                get_color="color",
                get_radius=10000,
                pickable=True,
                opacity=0.8,
                stroked=True,
                filled=True,
                radius_scale=6,
                radius_min_pixels=10,
                radius_max_pixels=100,
                line_width_min_pixels=1
            ),
            pdk.Layer(
                "TextLayer",
                data=locations,
                get_position="coordinates",
                get_text="index",
                get_color=[0, 0, 0],
                get_size=14,
                get_angle=0,
                get_text_anchor="middle",
                get_alignment_baseline="center"
            )
        ],
        tooltip={
            "html": """
            <div style="direction: rtl; font-family: 'Tajawal'; padding: 10px;">
                <b>الموقع</b>: {index}<br/>
                <b>التقييم</b>: {score}<br/>
                <b>الرطوبة</b>: {humidity}%<br/>
                <b>التوصية</b>: {التوصية}
            </div>
            """,
            "style": {
                "backgroundColor": "white",
                "color": "black",
                "fontFamily": "'Tajawal', sans-serif"
            }
        }
    )

def main():
    # Arabic as default language
    st.sidebar.title("إعدادات النظام")
    show_english = st.sidebar.checkbox("English", False)
    
    if not show_english:
        # Arabic Interface
        st.title("نظام ذكي لإدارة المياه في واسط")
        
        # Added new "الصيانة" tab while keeping original tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "توزيع المياه", 
            "الاستمطار الجوي", 
            "الأسئلة الشائعة",
            "البلاغات",
            "الصيانة"
        ])
        
        # ... [Keep all existing tab1-tab4 code unchanged] ...

        # ===== ENHANCED TAB 5: MAINTENANCE WITH PYDECK =====
        with tab5:
            st.header("الصيانة والمراقبة")
            
            with st.expander("أفضل مواقع لجمع المياه", expanded=True):
                with st.spinner("جاري تحميل بيانات المواقع..."):
                    try:
                        locations = WaterAI.optimal_collector_locations()
                        if not locations.empty:
                            st.write("""
                            **معايير الاختيار**:  
                            - الرطوبة (>65%)  
                            - القرب من مناطق الاستهلاك  
                            - معدل التبخر  
                            """)
                            
                            # Display both dataframe and interactive map
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                st.dataframe(locations)
                            
                            with col2:
                                arabic_map = create_arabic_map(locations)
                                st.pydeck_chart(arabic_map)
                            
                            # Add legend
                            st.markdown("""
                            <div style="text-align: right; margin: 15px 0;">
                                <strong>مفتاح الألوان:</strong><br>
                                <span style='color:#00AA00;font-size:20px'>■</span> ممتاز (تقييم > 90)<br>
                                <span style='color:#FFAA00;font-size:20px'>■</span> جيد (تقييم 80-90)<br>
                                <span style='color:#FF5733;font-size:20px'>■</span> متوسط (تقييم < 80)
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning("تعذر تحميل بيانات المواقع")
                    except Exception as e:
                        st.error("حدث خطأ في تحميل الخريطة التفاعلية")
                        if st.secrets.get("DEBUG", False):
                            st.exception(e)

            # ... [Keep rest of tab5 code unchanged] ...
    
    else:
        # Minimal English version
        st.title("Wasit Water Management AI")
        st.warning("For full features, please use Arabic interface")

if __name__ == "__main__":
    main()