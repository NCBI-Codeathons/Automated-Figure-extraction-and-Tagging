import requests
import string


def openiparser(query: str, output_list: str):
    with open(output_list, 'w') as f:
        f.write('idx\tuid\timg_path\tfig_num\tcaption')

    query_url_start = query.split('m=')[0]
    query_url_end = query.split('n=100')[1]

    start = 1
    end = 100

    r = requests.get(query_url_start+'m='+str(start)+'&'+'n='+str(end)+query_url_end)
    data = r.json()

    total = data['total']

    for result, i in enumerate(data['list']):

        uid = ''.join(x for x in result['uid'] if x in string.printable)
        imgLarge = ''.join(x for x in result['imgLarge'] if x in string.printable)
        fid = ''.join(x for x in result['image']['id'] if x in string.printable)
        capt = ''.join(x for x in result['image']['caption'] if x in string.printable)

        try:
            with open(output_list, 'a') as f:
                f.write('\n'+i+'\t'+uid+'\t'+imgLarge+'\t'+fid+'\t'+capt)
        except Exception:
            print(uid)
            print(imgLarge)
            print(fid)
            print(capt)
            raise

    if total > 100:

        for i in range(0, int((total-100)/100)+1):

            start = 101 + 100*i
            end = 200 + 100*i

            r = requests.get(query_url_start+'m='+str(start)+'&'+'n='+str(end)+query_url_end)
            data = r.json()

            for result, j in enumerate(data['list']):

                uid = ''.join(x for x in result['uid'] if x in string.printable)
                imgLarge = ''.join(x for x in result['imgLarge'] if x in string.printable)
                fid = ''.join(x for x in result['image']['id'] if x in string.printable)
                capt = ''.join(x for x in result['image']['caption'] if x in string.printable)
                idx = 99+100*i+j+1

                try:
                    with open(output_list, 'a') as f:
                        f.write('\n'+idx+'\t'+uid+'\t'+imgLarge+'\t'+fid+'\t'+capt)
                except Exception:
                    print(uid)
                    print(imgLarge)
                    print(fid)
                    print(capt)
                    raise
