import re, base64, json, argparse

parser = argparse.ArgumentParser(description='Check HAR file integrity.')

parser.add_argument('in_filename', nargs='+', default="in.har", metavar='in', type=str, help='input HAR file. default: in.har')
parser.add_argument('num_regex', nargs='?', default=r".+/(\d+)\.ts", metavar='sort_regex', type=str, help=r'A regular expression to get numeric values to sort packets.')

args = parser.parse_args()
in_filename = args.in_filename
num_regex = args.num_regex

log_entries = []

for fn in in_filename:
    with open(fn) as f:
        data = f.read()
    log_entries += json.loads(data)['log']['entries']

streams = []

entries = list(filter(lambda x: x[0] != None and 'text' in x[1]['response']['content'],
    [[re.match(num_regex, x['request']['url']), x] for x in log_entries]))

pairs = sorted([[int(x[0][1]), x[1]] for x in entries], key=lambda x: x[0])

pairs_processed = []
last = None
for x, y in pairs:
    if last != x:
        pairs_processed.append([x, y])
        last = x

print("Start = %s" % pairs_processed[0][0])
print("End = %s" % pairs_processed[-1][0])
print("Len = %s" % len(pairs_processed))

print(len(pairs_processed) == pairs_processed[-1][0] - pairs_processed[0][0] + 1)
