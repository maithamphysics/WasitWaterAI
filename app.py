# نظام ذكي لإدارة المياه في واسط - النسخة الكاملة مع العزيزية والحفرية
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from scipy.optimize import minimize
import math
import random
import pydeck as pdk
from tenacity import retry, stop_after_attempt, wait_exponential

# ================
# التهيئة والإعداد
# ================
st.set_page_config(
    page_title="نظام ذكي لإدارة المياه - واسط",
    page_icon="💧",
    layout="wide"
)

# تنسيق الصفحة بالعربية
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Tajawal', sans-serif;
    direction: rtl;
    text-align: right;
}
.stMap {border-radius: 10px;}
.mapboxgl-canvas {border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

# ================
# الوظائف الأساسية
# ================
class WaterAI:
    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def calculate_dew_point(temp, humidity):
        """حساب نقطة الندى"""
        A, B = 17.27, 237.7
        alpha = ((A * temp) / (B + temp)) + math.log(humidity/100.0)
        return (B * alpha) / (A - alpha)

    @staticmethod
    def optimize_allocation(districts):
        """توزيع المياه الأمثل بين المناطق"""
        def objective(x):
            return sum((d['demand'] - x[i])**2 for i, d in enumerate(districts))
        
        constraints = (
            {'type': 'ineq', 'fun': lambda x: x - np.array([d['min_required'] for d in districts])},
            {'type': 'ineq', 'fun': lambda x: sum([d['supply'] for d in districts]) - sum(x)}
        )
        
        res = minimize(
            objective,
            x0=[d['current_alloc'] for d in districts],
            bounds=[(d['min_required'], d['demand']) for d in districts],
            constraints=constraints
        )
        return res.x

    @staticmethod
    def calculate_water_yield(temp, humidity, area):
        """حساب كمية المياه المستخرجة من الجو"""
        if not (0 <= humidity <= 100):
            raise ValueError("الرطوبة يجب أن تكون بين 0 و 100%")
        return 0.8 * math.exp(0.08 * humidity) * (1 - 0.018 * (temp - 25)**2) * area

    @staticmethod
    def recommend_system(temp, humidity):
        """توصية بنظام الاستمطار المناسب"""
        dew_point = WaterAI.calculate_dew_point(temp, humidity)
        if temp - dew_point < 2:
            return "🌫️ شبكات الضباب (كفاءة عالية)"
        elif humidity > 70:
            return "⚡ مولدات التبريد الكهروحراري"
        else:
            return "🧂 أنظمة مساعدة بالمجففات"

    @staticmethod
    def generate_response(question):
        """إجابات الأسئلة الشائعة"""
        responses = {
            "كيفية التقديم": """لطلب خدمة المياه:
            1. توجّه إلى أقرب فرع لشركة المياه
            2. أحضر الوثائق المطلوبة
            3. ادفع الرسوم (إن وجدت)
            مدة المعالجة: 3-5 أيام عمل""",
            "جدول المياه": """مواعيد التوزيع:
            - الكوت: 6-9 صباحاً، 5-8 مساءً
            - النعمانية: 7-10 صباحاً، 6-9 مساءً
            - الصويرة: 8-11 صباحاً، 7-10 مساءً
            - العزيزية: 6:30-9:30 صباحاً، 5:30-8:30 مساءً
            - الحفرية: 7-10 صباحاً، 6-9 مساءً""",
            "ترشيد الاستهلاك": """نصائح للترشيد:
            - إصلاح التسريبات فوراً
            - استخدام تقنيات الري الحديثة
            - تجميع مياه الأمطار"""
        }
        return responses.get(question, "اختر سؤالاً من القائمة")

    @staticmethod
    def optimal_collector_locations():
        """أفضل مواقع جمع المياه في واسط"""
        locations = {
            "الكوت": {"lat": 32.51, "lon": 45.82, "score": 88, "humidity": 72},
            "الحي": {"lat": 32.47, "lon": 45.83, "score": 85, "humidity": 68},
            "بدرة": {"lat": 33.12, "lon": 45.93, "score": 82, "humidity": 65},
            "النعمانية": {"lat": 32.57, "lon": 45.30, "score": 92, "humidity": 75},
            "الصويرة": {"lat": 32.92, "lon": 44.47, "score": 95, "humidity": 78},
            "الزبيدية": {"lat": 32.25, "lon": 45.05, "score": 89, "humidity": 70},
            "الجعيفر": {"lat": 32.38, "lon": 45.72, "score": 84, "humidity": 67},
            "الشحيمية": {"lat": 32.65, "lon": 45.15, "score": 87, "humidity": 69},
            "العزيزية": {"lat": 32.90, "lon": 45.05, "score": 83, "humidity": 66},
            "الحفرية": {"lat": 32.30, "lon": 45.25, "score": 86, "humidity": 71}
        }
        df = pd.DataFrame(locations).T
        df["التوصية"] = ["ممتاز" if x > 90 else "جيد" if x > 80 else "متوسط" for x in df["score"]]
        return df.sort_values("score", ascending=False)

# ================
# واجهة المستخدم
# ================
def create_arabic_map(locations):
    """إنشاء خريطة تفاعلية بالعربية"""
    locations['coordinates'] = locations.apply(lambda row: [row['lon'], row['lat']], axis=1)
    locations['color'] = locations['score'].apply(
        lambda x: [0, 168, 0] if x > 90 else [255, 170, 0] if x > 80 else [255, 87, 51]
    )
    
    return pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=32.6,
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
    st.sidebar.title("إعدادات النظام")
    show_english = st.sidebar.checkbox("English", False)
    
    if not show_english:
        st.title("نظام إدارة المياه في محافظة واسط")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "توزيع المياه", 
            "الاستمطار الجوي", 
            "الأسئلة الشائعة",
            "البلاغات",
            "خريطة المحطات"
        ])
        
        # تبويب توزيع المياه
        with tab1:
            st.header("توزيع المياه بين المناطق")
            districts = [
                {"name": "الكوت", "demand": 5000, "supply": 3200, "min_required": 2500, "current_alloc": 3000},
                {"name": "الحي", "demand": 4000, "supply": 3500, "min_required": 2000, "current_alloc": 3400},
                {"name": "بدرة", "demand": 3000, "supply": 2500, "min_required": 1500, "current_alloc": 2400},
                {"name": "النعمانية", "demand": 3800, "supply": 2900, "min_required": 1800, "current_alloc": 2700},
                {"name": "الصويرة", "demand": 4200, "supply": 3100, "min_required": 2100, "current_alloc": 2900},
                {"name": "الزبيدية", "demand": 3500, "supply": 2800, "min_required": 1700, "current_alloc": 2600},
                {"name": "العزيزية", "demand": 3200, "supply": 2400, "min_required": 1600, "current_alloc": 2300},
                {"name": "الحفرية", "demand": 3600, "supply": 2700, "min_required": 1750, "current_alloc": 2500}
            ]
            
            optimized = WaterAI.optimize_allocation(districts)
            
            df = pd.DataFrame({
                "المنطقة": [d["name"] for d in districts],
                "الطلب (م³)": [d["demand"] for d in districts],
                "التوزيع الحالي": [d["current_alloc"] for d in districts],
                "التوزيع الأمثل": optimized,
                "الفرق": optimized - [d["current_alloc"] for d in districts]
            })
            
            fig = px.bar(df, x="المنطقة", y=["التوزيع الحالي", "التوزيع الأمثل"], 
                        title="مقارنة التوزيع الحالي بالأمثل", barmode="group")
            st.plotly_chart(fig, use_container_width=True)
            
            st.download_button(
                "تحميل التقرير",
                df.to_csv(index=False, encoding='utf-8-sig'),
                file_name="توزيع_المياه.csv",
                mime="text/csv"
            )
        
        # تبويب الاستمطار الجوي
        with tab2:
            st.header("حساب إنتاج المياه الجوية")
            col1, col2 = st.columns(2)
            
            with col1:
                temp = st.slider("درجة الحرارة (°C)", -10, 50, 28)
                humidity = st.slider("الرطوبة النسبية (%)", 5, 100, 45)
                area = st.slider("مساحة المجمع (م²)", 1, 100, 10)
                
                if temp > 40:
                    st.error("تحذير: موجة حر! زيادة الاستهلاك المتوقع")
                elif humidity < 30:
                    st.warning("تنبيه: جفاف - تقليل كميات التوزيع")
            
            with col2:
                try:
                    dew_point = WaterAI.calculate_dew_point(temp, humidity)
                    water_yield = WaterAI.calculate_water_yield(temp, humidity, area)
                    system = WaterAI.recommend_system(temp, humidity)
                    
                    st.metric("نقطة الندى", f"{dew_point:.1f} °C")
                    st.metric("الإنتاج اليومي", f"{water_yield:.2f} لتر")
                    st.metric("النظام الموصى به", system)
                    
                    if humidity > 70:
                        st.success("ظروف ممتازة للاستمطار")
                    else:
                        st.warning("ظروف متوسطة - يحتاج أنظمة مساعدة")
                        
                except ValueError as e:
                    st.error(str(e))
        
        # تبويب الأسئلة الشائعة
        with tab3:
            st.header("الأسئلة المتكررة")
            question = st.selectbox("اختر سؤالاً:", ["", "كيفية التقديم", "جدول المياه", "ترشيد الاستهلاك"])
            if question:
                st.markdown(f"### {question}")
                st.markdown(WaterAI.generate_response(question))
        
        # تبويب البلاغات
        with tab4:
            st.header("نظام البلاغات")
            with st.form("report_form"):
                issue_type = st.selectbox("نوع البلاغ", ["", "تسرب مياه", "انقطاع", "تلوث", "أخرى"])
                location = st.selectbox("الموقع", ["", "الكوت", "الحي", "بدرة", "النعمانية", 
                                                  "الصويرة", "الزبيدية", "العزيزية", "الحفرية"])
                details = st.text_area("تفاصيل المشكلة")
                submitted = st.form_submit_button("إرسال البلاغ")
                
                if submitted:
                    if issue_type and location:
                        ref_num = random.randint(1000, 9999)
                        st.success(f"""تم استلام بلاغك (رقم: {ref_num}) وسيتم المعالجة خلال 24 ساعة""")
                    else:
                        st.error("الرجاء إدخال نوع البلاغ والموقع")
        
        # تبويب الخريطة
        with tab5:
            st.header("خريطة محطات المياه")
            with st.expander("أفضل مواقع جمع المياه", expanded=True):
                locations = WaterAI.optimal_collector_locations()
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.dataframe(locations)
                
                with col2:
                    st.pydeck_chart(create_arabic_map(locations))
                
                st.markdown("""
                <div style="text-align: right; margin: 15px 0;">
                    <strong>مفتاح الألوان:</strong><br>
                    <span style='color:#00AA00;font-size:20px'>■</span> ممتاز (تقييم > 90)<br>
                    <span style='color:#FFAA00;font-size:20px'>■</span> جيد (تقييم 80-90)<br>
                    <span style='color:#FF5733;font-size:20px'>■</span> متوسط (تقييم < 80)
                </div>
                """, unsafe_allow_html=True)
    
    else:
        st.title("Wasit Water Management System")
        st.warning("Please switch to Arabic interface for full features")

if __name__ == "__main__":
    main()