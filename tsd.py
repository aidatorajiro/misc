## Convert a HAR file to a concatenated sequence of matched packets.

import re, base64, json, argparse

parser = argparse.ArgumentParser(description='Convert a HAR file to the concatenation of the matched packets.')

parser.add_argument('infiles', nargs='+', default="in.har", metavar='infiles', type=str, help='input HAR file. default: in.har')
parser.add_argument('--out', default="out.ts", metavar='out', type=str, help='output file. The content will be the concatenation of the matched packets. default: out.ts')
parser.add_argument('--stream_regex', default=r".+/\d+\.ts", metavar='stream_regex', type=str, help=r'A regular expression to filter packets.')
parser.add_argument('--lensort', default=True, action=argparse.BooleanOptionalAction, help=r'Whether to use length-priority sort based on URL.')
parser.add_argument('--sort_nodup', default=True, action=argparse.BooleanOptionalAction, help=r'Whether to take only one request by each number. Requires lensort is true.')
parser.add_argument('--sort_regex', default=r".+/(\d+)\.ts", metavar='numsort_regex', type=str, help=r'A regular expression to get some part of URL to sort packets.')

args = parser.parse_args()
infiles = args.infiles
out_filename = args.out
stream_regex = args.stream_regex
lensort = args.lensort
sort_nodup = args.sort_nodup
sort_regex = args.sort_regex

log_entries = []

for fn in infiles:
    with open(fn) as f:
        data = f.read()
    log_entries += json.loads(data)['log']['entries']

streams = []

entries = list(filter(lambda x: re.match(stream_regex, x['request']['url']) and 'text' in x['response']['content'], log_entries))

if lensort:
    pairs = sorted(
            zip(
                [re.match(sort_regex, x['request']['url'])[1] for x in entries]
                , entries
            )
            , key=lambda x: [len(x[0]), x[0]]
        )
    
    if sort_nodup:
        pairs_processed = []
        last = None
        for x, y in pairs:
            if last != x:
                print("accepted: " + x)
                pairs_processed.append([x, y])
                last = x
            else:
                print("duplicate omitted: " + x)
    else:
        pairs_processed = pairs
    
    entries = [x[1] for x in pairs_processed]

for e in entries:
    # print(int(re.match(sort_regex, e['request']['url'])[1]))
    cont = e['response']['content']
    stream = cont['text']
    if 'encoding' in cont and cont['encoding'] == 'base64':
        stream = base64.b64decode(stream)
    streams.append(stream)

concat = b"".join(streams)

with open(out_filename, "wb") as f:
    f.write(concat)