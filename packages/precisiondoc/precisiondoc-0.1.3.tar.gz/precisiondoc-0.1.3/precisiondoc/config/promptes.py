# document page type classification prompt
page_type_classification_prompt_cn = """
        请根据页面内容判断该页面属于以下哪种类型：
        页面类型枚举：

        COVER: 封面页
        TOC: 目录页
        CONTENT: 正文页
        REFERENCE: 参考文献页
        APPENDIX: 附录页

        判断标准：

        COVER (封面页)

        包含指南标题、编写机构、年份等基本信息
        通常包含"指南"、"Guidelines"等关键词
        包含组织机构名称（如CSCO）
        包含编写组成员、组长等信息


        TOC (目录页)

        包含"目录"、"Contents"等标题
        列出章节标题和对应页码
        使用数字编号的章节结构
        内容为导航性质，不包含实质性医学内容


        CONTENT (正文页)

        包含具体的医学诊疗内容
        包含治疗方案、药物推荐、分期信息等
        包含表格形式的治疗指南
        包含Ⅰ级推荐、Ⅱ级推荐、Ⅲ级推荐等分级
        包含具体的医学术语和治疗方案


        REFERENCE (参考文献页)

        包含"参考文献"、"References"等标题
        内容为文献引用格式
        包含作者姓名、期刊名称、发表年份等
        使用方括号标记的引用编号


        APPENDIX (附录页)

        包含"附录"、"Appendix"等标题
        包含补充性材料，如分期表、分类表等
        通常包含"附录1"、"附录2"等编号



        请输出页面类型的英文枚举值。
"""

page_type_classification_prompt_en = """
        Please classify the page content into one of the following types:
        Page Type Enumeration:

        COVER: Cover page
        TOC: Table of contents page
        CONTENT: Main content page
        REFERENCE: Reference page
        APPENDIX: Appendix page

        Classification Criteria:

        COVER (Cover page)

        Contains guideline title, authoring organization, year
        Usually includes keywords like "指南", "Guidelines"
        Contains organization names (e.g., CSCO)
        Contains editorial board members, chairpersons


        TOC (Table of contents page)

        Contains "目录", "Contents" as title
        Lists chapter titles with corresponding page numbers
        Uses numbered chapter structure
        Navigational content without substantial medical information


        CONTENT (Main content page)

        Contains specific medical diagnostic and treatment content
        Includes treatment protocols, drug recommendations, staging information
        Contains guideline tables
        Includes recommendation levels (Level I, II, III)
        Contains specific medical terminology and treatment protocols


        REFERENCE (Reference page)

        Contains "参考文献", "References" as title
        Content in citation format
        Includes author names, journal names, publication years
        Uses bracketed reference numbers


        APPENDIX (Appendix page)

        Contains "附录", "Appendix" as title
        Contains supplementary materials like staging tables, classification tables
        Usually numbered as "附录1", "附录2", etc.



        Please output the English enumeration value of the page type.
"""
