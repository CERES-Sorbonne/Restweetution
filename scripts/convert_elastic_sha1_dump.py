import math

filename = '/Users/david/Restweetution/collectes/export_csv/sha1_format.csv'
dump = '/Users/david/Restweetution/collectes/export_csv/sha1_clean.csv'
result = set()

with open(filename) as file:
    for line in file:
        txt = line.replace('\n', '')
        array = txt.split(',')[2:]
        length = len(array)
        assert length % 2 == 0
        half = math.floor(length / 2)

        for i in range(half):
            sha1 = array[i].replace('"', '')
            sha1 = sha1.replace(' ', '')
            format_ = array[i + half].replace('"', '')
            format_ = format_.replace(' ', '')
            sha1_format = sha1 + '.' + format_
            print(sha1_format)
            result.add(sha1_format)


with open(dump, mode='w') as file:
    for r in result:
        file.write(r + '\n')
