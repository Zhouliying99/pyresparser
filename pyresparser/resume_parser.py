# Author: Omkar Pathak

import os
import multiprocessing as mp
import io
import spacy
import re
import pprint
from spacy.matcher import Matcher
from . import utils


def detect_language(text):
    """
    检测文本语言
    简单的实现：如果包含中文字符就认为是中文简历
    """
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    has_chinese = bool(chinese_pattern.search(text))
    return 'zh' if has_chinese else 'en'


class ResumeParser(object):

    def __init__(
        self,
        resume,
        skills_file=None,
        custom_regex=None
    ):
        self.__skills_file = skills_file
        self.__custom_regex = custom_regex
        self.__resume = resume
        if not isinstance(self.__resume, io.BytesIO):
            ext = os.path.splitext(self.__resume)[1].split('.')[1]
        else:
            ext = self.__resume.name.split('.')[1]
        
        self.__text_raw = utils.extract_text(self.__resume, '.' + ext)
        self.__text = ' '.join(self.__text_raw.split())
        
        # 检测语言并加载相应的模型
        self.lang = detect_language(self.__text)
        if self.lang == 'zh':
            try:
                self.nlp = spacy.load('zh_core_web_sm')
            except OSError:
                print("中文模型未安装，正在安装...")
                os.system('python -m spacy download zh_core_web_sm')
                self.nlp = spacy.load('zh_core_web_sm')
        else:
            self.nlp = spacy.load('en_core_web_sm')
        
        self.custom_nlp = self.nlp  # 使用同一个模型
        self.__matcher = Matcher(self.nlp.vocab)
        self.__details = {
            'name': None,
            'email': None,
            'mobile_number': None,
            'skills': None,
            'college_name': None,
            'degree': None,
            'designation': None,
            'experience': None,
            'company_names': None,
            'no_of_pages': None,
            'total_experience': None,
        }
        
        self.__nlp = self.nlp(self.__text)
        self.__custom_nlp = self.custom_nlp(self.__text_raw)
        # 只在英文模式下使用noun_chunks
        self.__noun_chunks = list(self.__nlp.noun_chunks) if self.lang == 'en' else []
        
        self.__get_basic_details()

    def __get_basic_details(self):
        """
        This function will fetch basic details
        """
        try:
            # 基本信息提取
            name = utils.extract_name(self.__nlp, self.__matcher, self.lang)
            email = utils.extract_email(self.__text)
            mobile = utils.extract_mobile_number(self.__text, self.__custom_regex)
            
            # 技能提取
            try:
                skills = utils.extract_skills(
                    self.__nlp,
                    self.__noun_chunks,
                    self.__skills_file,
                    self.lang
                )
            except Exception:
                skills = None
            
            # 教育信息提取
            try:
                edu = utils.extract_education(self.__nlp, self.lang)
            except Exception:
                edu = None
            
            # 实体提取
            try:
                entities = utils.extract_entities_wih_custom_model(
                    self.__custom_nlp,
                    self.lang
                )
            except Exception:
                entities = {}
            
            # 更新结果
            self.__details['name'] = name
            self.__details['email'] = email
            self.__details['mobile_number'] = mobile
            self.__details['skills'] = skills

            # 根据语言选择不同的教育信息提取方式
            if self.lang == 'zh':
                self.__details['degree'] = edu  # 中文简历直接使用学历信息
            else:
                self.__details['college_name'] = entities.get('College Name', None)
                self.__details['degree'] = entities.get('Degree', None)
            
            self.__details['designation'] = entities.get('Designation', None)
            self.__details['experience'] = entities.get('Experience', None)
            self.__details['company_names'] = entities.get('Companies worked at', None)
            
            # 页数提取
            try:
                self.__details['no_of_pages'] = utils.get_number_of_pages(self.__resume)
            except Exception:
                self.__details['no_of_pages'] = None
            
            # 工作经验计算
            try:
                experience = entities.get('Experience', None)
                if experience:
                    self.__details['total_experience'] = round(
                        utils.get_total_experience(experience) / 12,
                        2
                    )
                else:
                    self.__details['total_experience'] = 0
            except Exception:
                self.__details['total_experience'] = 0
                
        except Exception:
            # 确保所有字段都有默认值
            for key in self.__details:
                if self.__details[key] is None:
                    self.__details[key] = [] if key in ['skills', 'experience', 'company_names'] else None

    def get_extracted_data(self):
        return self.__details


def resume_result_wrapper(resume):
    parser = ResumeParser(resume)
    return parser.get_extracted_data()


if __name__ == '__main__':
    pool = mp.Pool(mp.cpu_count())

    resumes = []
    data = []
    for root, directories, filenames in os.walk('resumes/'):
        for filename in filenames:
            file = os.path.join(root, filename)
            resumes.append(file)

    results = pool.map(resume_result_wrapper, resumes)
    pool.close()
    pool.join()

    for result in results:
        data.append(result)
    
    pprint.pprint(data) 