import unicodedata
import random
import time


class StringHelper(object):
    @staticmethod
    def is_number(input_str) -> bool:
        """
        验证字符串为数字。
        @param input_str: 输入字符串或数字
        @return: True or False
        """
        if type(input_str) is int:
            return True

        if type(input_str) is str:
            try:
                unicodedata.digit(input_str)
                return True
            except (TypeError, ValueError):
                pass
        return False

    @staticmethod
    def random_generate_str(int_nu) -> str:
        """
        生成随机指定长度的字符串。
        @param int_nu: 输入字符串
        @return: 返回随机的字符串
        """
        str_template = 'zyxwvutsrqponmlkjihgfedcba'

        while len(str_template) < int_nu:
            str_template += str_template

        return time.strftime('%Y%m%d%H%M%S_', time.localtime()) + "".join([item for item in random.sample(str_template, int_nu)])

    def zh_to_en(input_str: str) -> str:
        """
        将中文字符串符号转换为英文。
        @param input_str: 输入字符串
        @return: 返回转换后的字符串
        """
        punctuation_map = {
            '，': ',',
            '。': '.',
            '？': '?',
            '！': '!',
            '；': ';',
            '：': ':',
            # '《': '"',
            # '》': '"',
            '‘': "'",
            '’': "'",
            '“': '"',
            '”': '"',
            '…': '...',
            '（': '(',
            '）': ')',
            '、': ','
        }
        # 使用字符串的translate方法进行转换
        return input_str.translate(str.maketrans(punctuation_map))

if __name__ == "__main__":
    print(StringHelper.random_generate_str(4))
    print(StringHelper.random_generate_str(30))
    print(time.strftime('%Y%m%d%H%M%S', time.localtime()))