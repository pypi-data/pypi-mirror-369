

# device tools
# 获取选取设备信息的索引，通过[]之间的字符去解析
# Get the index of the selected device information and parse it through the characters between
def TxtWrapBy(start_str, end, all):
    start = all.find(start_str)
    if start >= 0:
        start += len(start_str)
        end = all.find(end, start)
        if end >= 0:
            return all[start:end].strip()
        
# Convert the returned error code to hexadecimal display
# 将返回的错误码转换为十六进制显示
def ToHexStr(num):
    try:
        chaDic = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}
        hexStr = ""
        if num < 0:
            num = num + 2 ** 32
        while num >= 16:
            digit = num % 16
            hexStr = chaDic.get(digit, str(digit)) + hexStr
            num //= 16
        hexStr = chaDic.get(num, str(num)) + hexStr
        return hexStr
    except Exception as e:
        pass