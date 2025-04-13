# app.py - Enhanced Wasit Water Management AI
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from scipy.optimize import minimize
import math
import random
import requests
from PIL import Image

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
</style>
""", unsafe_allow_html=True)

# ================
# CORE FUNCTIONS
# ================
class WaterAI:
    @staticmethod
    def calculate_dew_point(temp, humidity):
        """حساب نقطة الندى"""
        A, B = 17.27, 237.7
        alpha = ((A * temp) / (B + temp)) + math.log(humidity/100.0)
        return (B * alpha) / (A - alpha)

    @staticmethod
    def optimize_allocation(districts):
        """توزيع المياه الأمثل"""
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
        """حساب كمية المياه المستخرجة"""
        if not (0 <= humidity <= 100):
            raise ValueError("الرطوبة يجب أن تكون بين 0 و 100%")
        return 0.8 * math.exp(0.08 * humidity) * (1 - 0.018 * (temp - 25)**2) * area

    @staticmethod
    def recommend_system(temp, humidity):
        """توصية نظام الاستمطار"""
        dew_point = WaterAI.calculate_dew_point(temp, humidity)
        if temp - dew_point < 2:
            return "🌫️ شبكات الضباب (كفاءة عالية)"
        elif humidity > 70:
            return "⚡ مولدات تعمل بالتبريد الكهروحراري"
        else:
            return "🧂 أنظمة مساعدة بالمجففات"

    @staticmethod
    def generate_response(question):
        """الردود الذكية بالعربية"""
        responses = {
            "كيفية التقديم": """لطلب شهادة ميلاد:
            1. احضر إلى مديرية الأحوال المدنية في الكوت
            2. أحضر الهوية الوطنية وسجل العائلة
            3. الدفع: 10,000 دينار
            مدة المعالجة: 3-5 أيام عمل""",
            
            "جدول المياه": """مواعيد توزيع المياه حسب المنطقة:
            - الكوت: 6-9 صباحاً، 6-8 مساءً
            - الحي: 7-10 صباحاً، 7-9 مساءً
            - بدرة: 8-11 صباحاً، 8-10 مساءً
            - النعمانية: 5-8 صباحاً، 5-7 مساءً
            - الصويرة: 6:30-9:30 صباحاً، 6:30-8:30 مساءً""",
            
            "ترشيد الاستهلاك": """نصائح لترشيد المياه:
            - إصلاح التسريبات فوراً
            - استخدام الري بالتنقيط
            - جمع مياه الأمطار
            - تقليل وقت الاستحمام""",
            
            "default": """نظامنا الذكي يمكنه المساعدة في:
            - توزيع المياه العادل
            - استخراج المياه من الجو
            - إرشادات ترشيد الاستهلاك
            الرجاء تحديد سؤال أكثر دقة"""
        }
        return responses.get(question.lower(), responses["default"])

# ================
# STREAMLIT UI
# ================
def main():
    # Arabic as default language
    st.sidebar.title("إعدادات النظام")
    show_english = st.sidebar.checkbox("English", False)
    
    if not show_english:
        # Arabic Interface
        st.title("نظام ذكي لإدارة المياه في واسط")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "توزيع المياه", 
            "الاستمطار الجوي", 
            "الأسئلة الشائعة",
            "البلاغات والاقتراحات"
        ])
        
        # Tab 1: Water Allocation
        with tab1:
            st.header("محاكاة توزيع المياه")
            districts = [
                {"name": "الكوت", "demand": 5000, "supply": 3200, "min_required": 2500, "current_alloc": 3000},
                {"name": "الحي", "demand": 4000, "supply": 3500, "min_required": 2000, "current_alloc": 3400},
                {"name": "بدرة", "demand": 3000, "supply": 2500, "min_required": 1500, "current_alloc": 2400},
                {"name": "النعمانية", "demand": 3800, "supply": 2900, "min_required": 1800, "current_alloc": 2700},
                {"name": "الصويرة", "demand": 4200, "supply": 3100, "min_required": 2100, "current_alloc": 2900}
            ]
            
            optimized = WaterAI.optimize_allocation(districts)
            
            df = pd.DataFrame({
                "المنطقة": [d["name"] for d in districts],
                "الطلب (م³)": [d["demand"] for d in districts],
                "التوزيع الحالي": [d["current_alloc"] for d in districts],
                "التوزيع الأمثل": optimized,
                "التحسين": optimized - [d["current_alloc"] for d in districts]
            })
            
            fig = px.bar(df, x="المنطقة", y=["التوزيع الحالي", "التوزيع الأمثل"], 
                        title="مقارنة توزيع المياه", barmode="group")
            st.plotly_chart(fig, use_container_width=True)
            
            st.download_button(
                "تحميل التقرير",
                df.to_csv(index=False, encoding='utf-8-sig'),
                file_name="توزيع_المياه.csv",
                mime="text/csv"
            )
        
        # Tab 2: Atmospheric Water Harvesting
        with tab2:
            st.header("حساب استخراج المياه الجوية")
            col1, col2 = st.columns(2)
            
            with col1:
                temp = st.slider("درجة الحرارة (°C)", -10, 50, 28)
                humidity = st.slider("الرطوبة النسبية (%)", 5, 100, 45)
                area = st.slider("مساحة الجمع (م²)", 1, 100, 10)
                
                # Emergency alerts
                if temp > 40:
                    st.error("تحذير: موجة حر! تقليل الاستهلاك اليومي 20%")
                elif humidity < 30:
                    st.warning("تحذير: جفاف شديد - تجنب الري نهاراً")
            
            with col2:
                try:
                    dew_point = WaterAI.calculate_dew_point(temp, humidity)
                    water_yield = WaterAI.calculate_water_yield(temp, humidity, area)
                    system = WaterAI.recommend_system(temp, humidity)
                    
                    st.metric("نقطة الندى", f"{dew_point:.1f} °C")
                    st.metric("الإنتاج المتوقع", f"{water_yield:.2f} لتر/يوم")
                    st.metric("النظام الموصى به", system)
                    
                    if humidity > 70:
                        st.success("✅ ظروف ممتازة للاستمطار")
                    else:
                        st.warning("⚠️ يفضل استخدام أنظمة مساعدة")
                        
                except ValueError as e:
                    st.error(str(e))
            
            # Fixed Map Visualization
            st.subheader("أفضل مواقع لمحطات الاستمطار")
            station_data = {
                "الموقع": ["الكوت", "النعمانية", "الصويرة"],
                "خط العرض": [32.51, 32.57, 32.92],
                "خط الطول": [45.82, 45.30, 44.47],
                "النوع": ["صناعي", "زراعي", "سكني"],
                "لون": ["#FF0000", "#00AA00", "#0000FF"]  # Red, Green, Blue
            }
            
            # Display color legend in Arabic
            st.markdown("""
            <div style="text-align: right; margin-bottom: 20px;">
            <strong>مفتاح الألوان:</strong><br>
            <span style='color:#FF0000;font-size:20px'>■</span> صناعي<br>
            <span style='color:#00AA00;font-size:20px'>■</span> زراعي<br>
            <span style='color:#0000FF;font-size:20px'>■</span> سكني
            </div>
            """, unsafe_allow_html=True)
            
            st.map(pd.DataFrame(station_data),
                 latitude='خط العرض',
                 longitude='خط الطول',
                 size=1000,
                 color='لون')
        
        # Tab 3: FAQ
        with tab3:
            st.header("الأسئلة الشائعة")
            question = st.selectbox("اختر سؤالاً:", [
                "", 
                "كيفية التقديم", 
                "جدول المياه",
                "ترشيد الاستهلاك"
            ])
            
            if question:
                st.markdown(f"### {question}")
                st.markdown(WaterAI.generate_response(question))
        
        # Tab 4: Citizen Reporting
        with tab4:
            st.header("البلاغات والاقتراحات")
            
            with st.expander("بلاغ عن مشكلة مياه", expanded=True):
                issue_type = st.selectbox("نوع المشكلة", [
                    "", "تسرب", "انقطاع", "تلوث", "أخرى"
                ])
                location = st.text_input("الموقع الدقيق")
                details = st.text_area("تفاصيل إضافية")
                
                if st.button("إرسال البلاغ"):
                    if issue_type and location:
                        ref_num = random.randint(1000, 9999)
                        st.success(f"""
                        تم استلام بلاغك بنجاح
                        رقم المرجع: #{ref_num}
                        سيتم معالجة الطلب خلال 24 ساعة
                        """)
                    else:
                        st.error("الرجاء إدخال نوع المشكلة والموقع")
            
            with st.expander("اقتراح لتحسين الخدمة"):
                feedback = st.text_area("شاركنا أفكارك")
                if st.button("إرسال الاقتراح"):
                    st.success("شكراً لمساهمتك في تطوير خدماتنا")
    
    else:
        # Minimal English version
        st.title("Wasit Water Management AI")
        st.warning("For full features, please use Arabic interface")

if __name__ == "__main__":
    main()