## Convert a HAR file to a concatenated sequence of matched packets.

import re, base64, json, argparse

parser = argparse.ArgumentParser(description='Convert a HAR file to the concatenation of the matched packets.')

parser.add_argument('in_filename', nargs='+', default="in.har", metavar='in', type=str, help='input HAR file. default: in.har')
parser.add_argument('out_filename', nargs='?', default="out.ts", metavar='out', type=str, help='output file. The content will be the concatenation of the matched packets. default: out.ts')
parser.add_argument('stream_regex', nargs='?', default=r".+/.+?\.ts", metavar='stream_regex', type=str, help=r'A regular expression to filter packets. default: .+/.+?\.ts')
parser.add_argument('--numsort', default=True, action=argparse.BooleanOptionalAction, help=r'Whether to use numeric sort based on URL.')
parser.add_argument('--numnodup', default=True, action=argparse.BooleanOptionalAction, help=r'Whether to take only one request by each number. Requires numsort is true.')
parser.add_argument('numsort_regex', nargs='?', default=r".+/(.+?)\.ts", metavar='numsort_regex', type=str, help=r'A regular expression to get numeric values to sort packets. default: .+/(.+?)\.ts')

args = parser.parse_args()
in_filename = args.in_filename
out_filename = args.out_filename
stream_regex = args.stream_regex
numsort = args.numsort
numnodup = args.numnodup
numsort_regex = args.numsort_regex

log_entries = []

for fn in in_filename:
    with open(fn) as f:
        data = f.read()
    log_entries += json.loads(data)['log']['entries']

streams = []

entries = list(filter(lambda x: re.match(stream_regex, x['request']['url']) and 'text' in x['response']['content'], log_entries))

if numsort:
    pairs = sorted(
            zip(
                [int(re.match(numsort_regex, x['request']['url'])[1])for x in entries]
                , entries
            )
            , key=lambda x: x[0]
        )
    
    if numnodup:
        pairs_processed = []
        last = None
        for x, y in pairs:
            if last != x:
                print(x)
                pairs_processed.append([x, y])
                last = x
    else:
        pairs_processed = pairs
    
    entries = [x[1] for x in pairs_processed]

for e in entries:
    # print(int(re.match(numsort_regex, e['request']['url'])[1]))
    cont = e['response']['content']
    if 'text' in cont:
        stream = cont['text']
    if 'encoding' in cont and cont['encoding'] == 'base64':
        stream = base64.b64decode(stream)
    streams.append(stream)

concat = b"".join(streams)

with open(out_filename, "wb") as f:
    f.write(concat)