import re


class NumberUtil:
    _NO_NUM_PATTERN_ = re.compile(r'-')

    @staticmethod
    def is_number(src: str | None) -> bool:
        if not src:
            return False
        return bool(not NumberUtil._NO_NUM_PATTERN_.search(src))

    @staticmethod
    def to_int(src: str | None, fallback: int | None = 0) -> int | None:
        '''문자열에서 정수 변환'''
        if not src:
            return fallback
        target = src.split('-')[-1].strip()
        unit = 10000 if target.endswith('만') else 1
        unit = 10000000 if target.endswith('천만') else 1
        m = re.search(r'(\d+)\s*억', target)
        if m:
            unit = 100_000_000
        find = re.findall(pattern=r'\d+', string=target)
        return int(''.join(find)) * unit if find is not None and len(find) > 0 else fallback

    @staticmethod
    def find_price(src: str | None, fallback: int | None = 0) -> int | None:
        '''문자열에서 돈 찾기'''
        if not src:
            return fallback
        target = src.split('-')[-1].strip().split('원')[0]
        return NumberUtil.to_int(src=target, fallback=fallback)

    @staticmethod
    def find_percent(src: str, fallback: int | None = 0) -> int | None:
        '''문자열에 퍼센트 찾기'''
        find = re.search(r'\d+%', src)
        return int(find.group().replace('%', '')) if find is not None else fallback

    @staticmethod
    def find_area(src: str | None, ndigits: int | None = None, fallback: int | None = None) -> float | None:
        '''문자열에서 면적 찾기'''
        if not src:
            return fallback
        find = re.findall(r'\d+\.?\d*(?=㎡)', src)
        ret = sum(map(lambda x: float(re.sub(r'[^0-9.]', '', x).strip().replace(')', '')), find)) if find else fallback
        return round(ret, ndigits=ndigits) if ret else ret


if __name__ == '__main__':
    TEST = '5천만원'
    print(NumberUtil.find_price(src=TEST))
