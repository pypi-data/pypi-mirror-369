from requests import get


def DarkWebSearch(query):
    for i in range(4):
        try:
            re=get(url=f'https://vormweb.de/en/search?q={query}',timeout=6)
            if re.status_code==200:
                c=True
                break
        except:
            c=False
            print('Try internet connection...')
    if c!=True:
        return('Please check your internet connection')
    else:
        data=re.text

        out=[]
        for box in data.split('<div class="query-box">'):
            
            try:
                title=data.split('14px;"><i>')[1].split('</i></li><p')[0]

                url=data.split('sans-serif;">')[1].split('</a>')[0].split('id="urllink" href="')[1].split('" style="font-family')[0]

                out.append({
                    "url":url,
                    "title":title
                })
            except:
                pass
        return(out)