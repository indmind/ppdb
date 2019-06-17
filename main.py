from urllib import request
from bs4 import BeautifulSoup as soup
import json
import sys

header = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'User-Agent' : "Magic Browser"}
school_link = "https://02.ppdbjatim.net/kota/rekap_pendaftaran_sma/sekolah/30502001000"

# fetch from school
def fetch_school(link):
    client = request.urlopen(request.Request(link, headers=header))

    data = soup(client.read(), "html.parser")

    client.close()

    students = []

    for s in data.findAll("tr")[1:]:
        detail = s.findAll("td")

        students.append({
            "urutan": int(detail[0].text),
            "no-ujian": detail[1].text,
            "nama": detail[2].text,
            "sekolah-asal": detail[3].text,
            "nilai": float(detail[4].text),
            "waktu-daftar": detail[5].text,
        })

    return students

def scrape_user(link):
    client = request.urlopen(request.Request(link, headers=header))
    user_soup = soup(client.read(), "html.parser")
    client.close()
    
    sma = link.split("/")[-2] == "sma"
    container = user_soup.select("body > div.container-fluid > div > div > div.row.font > div.col-md-12.col-md-border > div > div.panel-body")[0]
    kelamin = container.div.findAll("div")[8].span.text
    span = container.findAll("div", {"class": "col-md-7"})[0].findAll("span")
    
    if not sma:
        pilihan = [ 
            {
                "Nama Sekolah": span[0].text,
                "Jurusan": span[1].text,
                "Status": span[2].text
            },{
                "Nama Sekolah": span[3].text,
                "Jurusan": span[4].text,
                "Status": span[5].text
            }
        ]
    else:
        pilihan = [ 
            {
                "Nama Sekolah": span[0].text,
                "Status": span[1].text
            },{
                "Nama Sekolah": span[2].text,
                "Status": span[3].text
            }
        ]

    return [kelamin, pilihan, span[4 if sma else 6].text]
    
    
def scrape(link, detail, num=None):
    data = fetch_school(link)

    print("Get {0} data".format(num))

    if not detail:
        return data[:num]

    new_data = []

    for i, d in enumerate(data[:num]):
        print(str(i + 1) + ': ' + d["nama"], end='... ')
        sys.stdout.flush()
        
        detail = scrape_user(d["link"])

        d["kelamin"] = detail[0]
        d["pilihan"] = detail[1]
        d["diterima-sementara"] = detail[2]
        
        new_data.append(d)
        print("done!")
        
    return new_data

if __name__ == '__main__':
    argv = sys.argv

    try:
        if argv[1] == "len":
            print("Jumlah Pendaftar:", len(fetch_school(school_link)))
        else:
            detail = False
            num = int(argv[2])
    
            if argv[3] == "yes":
                detail = True
    
            result = scrape(school_link, detail, num)

            with open(argv[1], 'w') as f:
                json.dump(result, f)
    except IndexError:
        print("Invalid Command! example: ppdb <len|path> <num> <detail?yes/no>")
