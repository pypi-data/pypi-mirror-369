import re
from datetime import datetime
from typing import List, Optional
from haruka_parser.time_formatter import return_format_datetime


class TimeExtractor:
    def __init__(self):
        # 合并所有meta标签的xpath为一个查询
        self.meta_xpath = (
            '//meta['
            'contains(@name, "og:time") or '
            'contains(@name, "PubDate") or '
            'contains(@name, "pubtime") or '
            'contains(@name, "_pubtime") or '
            'contains(@name, "apub:time") or '
            'contains(@pubdate, "pubdate") or '
            'contains(@name, "publishdate") or '
            'contains(@name, "PublishDate") or '
            'contains(@name, "sailthru.date") or '
            'contains(@itemprop, "dateUpdate") or '
            'contains(@name, "publication_date") or '
            'contains(@itemprop, "datePublished") or '
            'contains(@property, "og:release_date") or '
            'contains(@name, "article_date_original") or '
            'contains(@property, "og:published_time") or '
            'contains(@property, "rnews:datePublished") or '
            'contains(@name, "OriginalPublicationDate") or '
            'contains(@name, "weibo: article:create_at") or '
            'contains(@property, "article:published_time") or '
            '(@name="Keywords" and contains(@content, ":"))'
            ']/@content | //meta[@name="Keywords" and contains(@content, ":")]/@content'
        )
        
        # 合并所有补充标签的xpath为一个查询
        self.supplement_xpath = (
            '//div[@class="time fix"]//text() | '
            '//span[@id="pubtime_baidu"]/text() | '
            '//i[contains(@class, "time")]/text() | '
            '//span[contains(text(), "时间")]/text() | '
            '//div[contains(@class, "time")]//text() | '
            '//span[contains(@class, "date")]/text() | '
            '//div[contains(@class, "info")]//text() | '
            '//span[contains(@class, "time")]/text() | '
            '//div[contains(@class, "_time")]/text() | '
            '//span[contains(@id, "paperdate")]/text() | '
            '//em[contains(@id, "publish_time")]/text() | '
            '//time[@data-testid="timestamp"]/@dateTime | '
            '//span[contains(@id, "articleTime")]/text() | '
            '//span[contains(@class, "pub_time")]/text() | '
            '//span[contains(@class, "item-time")]/text() | '
            '//span[contains(@class, "publishtime")]/text() | '
            '//div[contains(@class, "news_time_source")]/text()'
        )
        
        # 合并所有时间格式的正则表达式为一个
        self.time_regex = re.compile(
            r'('
            r'\d{1,2}月\d{1,2}日|'
            r'\d{2}年\d{1,2}月\d{1,2}日|'
            r'\d{4}年\d{1,2}月\d{1,2}日|'
            r'\d{2}[-|/|.]\d{1,2}[-|/|.]\d{1,2}|'
            r'\d{4}[-|/|.]\d{1,2}[-|/|.]\d{1,2}|'
            r'\d{1,2}月\d{1,2}日\s*?[2][0-3]:[0-5]?[0-9]|'
            r'\d{1,2}月\d{1,2}日\s*?[0-1]?[0-9]:[0-5]?[0-9]|'
            r'\d{2}年\d{1,2}月\d{1,2}日\s*?[2][0-3]:[0-5]?[0-9]|'
            r'\d{4}年\d{1,2}月\d{1,2}日\s*?[2][0-3]:[0-5]?[0-9]|'
            r'\d{2}年\d{1,2}月\d{1,2}日\s*?[0-1]?[0-9]:[0-5]?[0-9]|'
            r'\d{4}年\d{1,2}月\d{1,2}日\s*?[0-1]?[0-9]:[0-5]?[0-9]|'
            r'\d{1,2}月\d{1,2}日\s*?[1-24]\d时[0-60]\d分|'
            r'\d{1,2}月\d{1,2}日\s*?[2][0-3]:[0-5]?[0-9]:[0-5]?[0-9]|'
            r'\d{4}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[2][0-3]:[0-5]?[0-9]|'
            r'\d{1,2}月\d{1,2}日\s*?[0-1]?[0-9]:[0-5]?[0-9]:[0-5]?[0-9]|'
            r'\d{2}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[2][0-3]:[0-5]?[0-9]|'
            r'\d{4}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[0-1]?[0-9]:[0-5]?[0-9]|'
            r'\d{2}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[0-1]?[0-9]:[0-5]?[0-9]|'
            r'\d{2}年\d{1,2}月\d{1,2}日\s*?[1-24]\d时[0-60]\d分|'
            r'\d{4}年\d{1,2}月\d{1,2}日\s*?[1-24]\d时[0-60]\d分|'
            r'\d{2}年\d{1,2}月\d{1,2}日\s*?[2][0-3]:[0-5]?[0-9]:[0-5]?[0-9]|'
            r'\d{4}年\d{1,2}月\d{1,2}日\s*?[2][0-3]:[0-5]?[0-9]:[0-5]?[0-9]|'
            r'\d{2}年\d{1,2}月\d{1,2}日\s*?[0-1]?[0-9]:[0-5]?[0-9]:[0-5]?[0-9]|'
            r'\d{4}年\d{1,2}月\d{1,2}日\s*?[0-1]?[0-9]:[0-5]?[0-9]:[0-5]?[0-9]|'
            r'\d{4}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[1-24]\d时[0-60]\d分|'
            r'\d{2}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[1-24]\d时[0-60]\d分|'
            r'\d{2}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[2][0-3]:[0-5]?[0-9]:[0-5]?[0-9]|'
            r'\d{4}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[2][0-3]:[0-5]?[0-9]:[0-5]?[0-9]|'
            r'\d{4}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[0-1]?[0-9]:[0-5]?[0-9]:[0-5]?[0-9]|'
            r'\d{2}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[0-1]?[0-9]:[0-5]?[0-9]:[0-5]?[0-9]'
            r')', 
            re.IGNORECASE
        )
        
        # 预编译用于清理文本的正则
        self.cleanup_regex = re.compile(r'[^\d年月日时分秒：:\-\/\.\s]', re.IGNORECASE)
    
    def get_best_time(self, time_list: List[str]) -> str:
        """从时间列表中选择最佳时间"""
        if not time_list:
            return ""
        
        # 按长度和完整性评分排序
        scored_times = []
        for time_str in time_list:
            score = len(time_str)
            # 包含年份加分
            if '年' in time_str or len(time_str.split('-')[0]) == 4 or len(time_str.split('/')[0]) == 4:
                score += 10
            # 包含时间加分
            if ':' in time_str or '：' in time_str or '时' in time_str:
                score += 5
            scored_times.append((score, time_str))
        
        # 返回得分最高的时间
        return max(scored_times, key=lambda x: x[0])[1]
    
    def extract_time_from_meta(self, html_tree) -> str:
        """从meta标签提取时间"""
        try:
            results = html_tree.xpath(self.meta_xpath)
            if results:
                return str(results[0]).strip()
        except Exception:
            pass
        return ""
    
    def extract_time_from_tags(self, html_tree) -> str:
        """从其他标签提取时间"""
        try:
            results = html_tree.xpath(self.supplement_xpath)
            if not results:
                return ""
            
            # 合并所有文本内容
            combined_text = ' '.join(str(r).strip() for r in results if r and str(r).strip())
            
            # 使用单个正则表达式提取所有时间
            time_matches = self.time_regex.findall(combined_text)
            
            return self.get_best_time(time_matches)
        except Exception:
            pass
        return ""
    
    def extract_time_from_html(self, content: str) -> str:
        """从HTML内容提取时间"""
        try:
            # 预处理：清理内容，只保留可能包含时间的部分
            cleaned_content = self.cleanup_regex.sub('', content[:50000])  # 限制内容长度
            
            # 使用单个正则表达式提取所有时间
            time_matches = self.time_regex.findall(cleaned_content)
            
            # 限制匹配数量防止过度匹配
            if len(time_matches) > 20:
                time_matches = time_matches[:20]
            
            return self.get_best_time(time_matches)
        except Exception:
            pass
        return ""
    
    def extract_time(self, html_tree) -> str:
        """主提取函数"""
        # 优先级：meta标签 > 特定标签 > HTML内容
        
        # 1. 从meta标签提取
        meta_time = self.extract_time_from_meta(html_tree)
        if meta_time:
            formatted_time = return_format_datetime(meta_time)
            if formatted_time:
                return formatted_time
        
        # 2. 从特定标签提取
        tag_time = self.extract_time_from_tags(html_tree)
        if tag_time:
            formatted_time = return_format_datetime(tag_time)
            if formatted_time:
                return formatted_time
        
        return ""
    
    def extract_time_from_content(self, content: str) -> str:
        # 3. 从HTML内容提取
        html_time = self.extract_time_from_html(content)
        if html_time:
            formatted_time = return_format_datetime(html_time)
            if formatted_time:
                return formatted_time
        return ""