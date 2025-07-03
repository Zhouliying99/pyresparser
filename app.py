import streamlit as st
import os
from pyresparser import ResumeParser
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="简历解析系统", layout="wide")

def save_uploaded_file(uploaded_file):
    # 确保上传目录存在
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    
    # 保存文件
    file_path = os.path.join('uploads', uploaded_file.name)
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def main():
    st.title("简历解析系统")
    
    menu = ["上传简历", "查看历史"]
    choice = st.sidebar.selectbox("选择功能", menu)
    
    if choice == "上传简历":
        st.subheader("上传简历文件")
        uploaded_file = st.file_uploader("选择简历文件", type=['pdf', 'docx', 'doc'])
        
        if uploaded_file is not None:
            if st.button("解析简历"):
                with st.spinner('正在解析中...'):
                    # 保存上传的文件
                    file_path = save_uploaded_file(uploaded_file)
                    
                    try:
                        # 解析简历
                        parser = ResumeParser(file_path)
                        data = parser.get_extracted_data()
                        
                        # 显示解析结果
                        st.success("解析成功！")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("基本信息")
                            st.write(f"姓名：{data.get('name', '未提供')}")
                            st.write(f"邮箱：{data.get('email', '未提供')}")
                            st.write(f"电话：{data.get('mobile_number', '未提供')}")
                            
                            st.subheader("教育背景")
                            st.write(f"学校：{data.get('college_name', '未提供')}")
                            st.write(f"学历：{data.get('degree', '未提供')}")
                        
                        with col2:
                            st.subheader("工作经验")
                            st.write(f"职位：{data.get('designation', '未提供')}")
                            st.write(f"工作年限：{data.get('total_experience', 0)} 年")
                            st.write(f"工作过的公司：{', '.join(data.get('company_names', [])) if data.get('company_names') else '未提供'}")
                            
                            st.subheader("技能")
                            skills = data.get('skills', [])
                            if skills:
                                st.write(", ".join(skills))
                            else:
                                st.write("未提供")
                        
                        # 保存解析结果
                        result = {
                            '时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            '文件名': uploaded_file.name,
                            '姓名': data.get('name', '未提供'),
                            '邮箱': data.get('email', '未提供'),
                            '电话': data.get('mobile_number', '未提供'),
                            '学历': str(data.get('degree', '未提供')),
                            '技能': ', '.join(data.get('skills', [])),
                        }
                        
                        # 确保历史记录文件存在
                        if not os.path.exists('history.csv'):
                            pd.DataFrame([result]).to_csv('history.csv', index=False)
                        else:
                            pd.DataFrame([result]).to_csv('history.csv', mode='a', header=False, index=False)
                        
                    except Exception as e:
                        st.error(f"解析失败：{str(e)}")
                    
                    # 清理上传的文件
                    os.remove(file_path)
    
    else:  # 查看历史
        st.subheader("历史解析记录")
        if os.path.exists('history.csv'):
            df = pd.read_csv('history.csv')
            st.dataframe(df)
        else:
            st.info("还没有解析记录")

if __name__ == '__main__':
    main() 