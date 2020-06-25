## Convert a HAR file to a concatenated sequence of matched packets.

import re, base64, json, argparse

parser = argparse.ArgumentParser(description='Convert a HAR file to the concatenation of the matched packets.')

parser.add_argument('in_filename', nargs='?', default="in.har", metavar='in', type=str, help='input HAR file. default: in.har')
parser.add_argument('out_filename', nargs='?', default="out.ts", metavar='out', type=str, help='output file. The content will be the concatenation of the matched packets. default: out.ts')
parser.add_argument('stream_regex', nargs='?', default=r".+/.+?\.ts", metavar='regex', type=str, help=r'Regular expression to filter packets. default: .+/.+?\.ts')

args = parser.parse_args()
in_filename = args.in_filename
out_filename = args.out_filename
stream_regex = args.stream_regex

with open(in_filename) as f:
    data = f.read()

prs = json.loads(data)


streams = []

for e in prs['log']['entries']:
    url = e['request']['url']
    if re.match(stream_regex, url):
        cont = e['response']['content']
        stream = cont['text']
        if cont['encoding'] == 'base64':
            stream = base64.b64decode(stream)
        streams.append(stream)

concat = b"".join(streams)

with open(out_filename, "wb") as f:
    f.write(concat)