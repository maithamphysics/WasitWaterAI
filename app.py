# app.py - Professional Arabic-First Water AI
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from scipy.optimize import minimize
import math

# ================
# CONFIGURATION
# ================
st.set_page_config(
    page_title="نظام ذكي لإدارة المياه - واسط",
    page_icon="💧",
    layout="wide"
)

# Hide Streamlit branding
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display:none;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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
            - بدرة: 8-11 صباحاً، 8-10 مساءً""",
            
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
        
        tab1, tab2, tab3 = st.tabs(["توزيع المياه", "الاستمطار الجوي", "الأسئلة الشائعة"])
        
        with tab1:
            st.header("محاكاة توزيع المياه")
            districts = [
                {"name": "الكوت", "demand": 5000, "supply": 3200, "min_required": 2500, "current_alloc": 3000},
                {"name": "الحي", "demand": 4000, "supply": 3500, "min_required": 2000, "current_alloc": 3400},
                {"name": "بدرة", "demand": 3000, "supply": 2500, "min_required": 1500, "current_alloc": 2400}
            ]
            
            optimized = WaterAI.optimize_allocation(districts)
            
            df = pd.DataFrame({
                "المنطقة": [d["name"] for d in districts],
                "الطلب (م³)": [d["demand"] for d in districts],
                "التوزيع الحالي": [d["current_alloc"] for d in districts],
                "التوزيع الأمثل": optimized
            })
            
            fig = px.bar(df, x="المنطقة", y=["التوزيع الحالي", "التوزيع الأمثل"], 
                        title="مقارنة توزيع المياه")
            st.plotly_chart(fig)
            
            st.download_button(
                "تحميل التقرير",
                df.to_csv(index=False).encode('utf-8'),
                file_name="توزيع_المياه.csv",
                mime="text/csv"
            )
        
        with tab2:
            st.header("حساب استخراج المياه الجوية")
            col1, col2 = st.columns(2)
            
            with col1:
                temp = st.slider("درجة الحرارة (°C)", -10, 50, 28)
                humidity = st.slider("الرطوبة النسبية (%)", 5, 100, 45)
                area = st.slider("مساحة الجمع (م²)", 1, 100, 10)
            
            with col2:
                dew_point = WaterAI.calculate_dew_point(temp, humidity)
                st.metric("نقطة الندى", f"{dew_point:.1f} °C")
    
                # Corrected calculation with better formatting
                water_yield = 0.8 * math.exp(0.08 * humidity) * (1 - 0.018 * (temp - 25)**2) * area
                st.metric("الإنتاج المتوقع", f"{water_yield:.2f} لتر/يوم")
    
                if humidity > 70:
                 st.success("✅ ظروف ممتازة للاستمطار")
                else:
                 st.warning("⚠️ يفضل استخدام أنظمة مساعدة")
            
            st.subheader("المناطق الأكثر كفاءة")
            st.image("https://i.imgur.com/J8hQv3a.png", width=600)
        
        with tab3:
            question = st.selectbox("اختر سؤالاً:", [
                "", 
                "كيفية التقديم", 
                "جدول المياه",
                "ترشيد الاستهلاك"
            ])
            
            if question:
                st.markdown(f"### {question}")
                st.markdown(WaterAI.generate_response(question))
                
                if st.button("إرسال استفسار إضافي"):
                    st.text_input("اكتب سؤالك المخصص:")
    
    else:
        # English version (minimal)
        st.title("Wasit Water Management AI")
        st.warning("For full features, please use Arabic interface")

if __name__ == "__main__":
    main()