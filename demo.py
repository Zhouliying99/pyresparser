from pyresparser import ResumeParser
import os

# 获取resumes目录下的所有PDF和Word文件
resume_dir = 'resumes'
supported_extensions = ('.pdf', '.docx', '.doc')
resume_files = [f for f in os.listdir(resume_dir) if f.lower().endswith(supported_extensions)]

# 遍历并解析每个简历
for resume_file in resume_files:
    print(f"\n正在解析简历: {resume_file}")
    print("-" * 50)
    resume_path = os.path.join(resume_dir, resume_file)
    try:
        data = ResumeParser(resume_path).get_extracted_data()
        print(data)
    except Exception as e:
        print(f"解析失败: {str(e)}")

# 显示统计信息
print("\n\n解析统计:")
print("-" * 50)
print(f"总共发现简历文件: {len(resume_files)}个")
print(f"支持的文件格式: {', '.join(supported_extensions)}")