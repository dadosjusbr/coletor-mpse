import requests
import pathlib
import sys
import os
import urllib3

base_url = "https://sistemas.mpse.mp.br/PublicDoc/PublicacaoDocumento/AbrirDocumento.aspx?cd_documento="
cod_meses_2018 = {
    "01": "56421",
    "02": "56423",
    "03": "56425",
    "04": "56894",
    "05": "56897",
    "06": "57398",
    "07": "57910",
    "08": "58383",
    "09": "58865",
    "10": "60307",
    "11": "60308",
    "12": "61432",
}
cod_meses_2019 = {
    "01": "61431",
    "02": "61479",
    "03": "64797",
    "04": "64798",
    "05": "64799",
    "06": "64800",
    "07": "64801",
    "08": "64802",
    "09": "65280",
    "10": "65629",
    "11": "66225",
    "12": "66458",
}
cod_meses_2020 = {
    "01": "67041",
    "02": "67489",
    "03": "67736",
    "04": "67987",
    "05": "68221",
    "06": "68469",
    "07": "68889",
    "08": "69309",
    "09": "69650",
    "10": "70347",
    "11": "70892",
    "12": "71278",
}
cod_meses_2021 = {
    "01": "71898",
    "02": "72385",
    "03": "72635",
    "04": "73091",
    "05": "73484",
    "06": "73802",
    "07": "74255",
    "08": "74625",
    "09": "75036",
    "10": "75445",
    "11": "75950",
    "12": "76218",
}
cod_meses_indenizatorias_2019 = {
    "07": "64806",
    "08": "64807",
    "09": "65281",
    "10": "65628",
    "11": "66226",
    "12": "66459",
}
cod_meses_indenizatorias_2020 = {
    "01": "67042",
    "02": "67576",
    "03": "67737",
    "04": "67988",
    "05": "68220",
    "06": "68471",
    "07": "68894",
    "08": "69314",
    "09": "69656",
    "10": "70352",
    "11": "70936",
    "12": "71287",
}
cod_meses_indenizatorias_2021 = {
    "01": "71905",
    "02": "72390",
    "03": "72640",
    "04": "73097",
    "05": "73490",
    "06": "73811",
    "07": "74257",
    "08": "74630",
    "09": "75050",
    "10": "75474",
    "11": "75957",
    "12": "76223",
}


def links_remuneration(month, year):
    links_type = {}
    link = ""
    if int(year) == 2018:
        for key in cod_meses_2018:
            if key == str(month):
                link = base_url + cod_meses_2018[key]

                links_type["Membros ativos"] = link
    elif int(year) == 2019:
        for key in cod_meses_2019:
            if key == str(month):
                link = base_url + cod_meses_2019[key]

                links_type["Membros ativos"] = link
    elif int(year) == 2020:
        for key in cod_meses_2020:
            if key == str(month):
                link = base_url + cod_meses_2020[key]

                links_type["Membros ativos"] = link
    elif int(year) == 2021:
        for key in cod_meses_2021:
            if key == str(month):
                link = base_url + cod_meses_2021[key]

                links_type["Membros ativos"] = link
    return links_type


def links_perks_temporary_funds(month, year):
    links_type = {}
    link = ""
    if int(year) == 2019:
        for key in cod_meses_indenizatorias_2019:
            if key == str(month):
                link = base_url + cod_meses_indenizatorias_2019[key]

                links_type["Membros ativos"] = link
    elif int(year) == 2020:
        for key in cod_meses_indenizatorias_2020:
            if key == str(month):
                link = base_url + cod_meses_indenizatorias_2020[key]

                links_type["Membros ativos"] = link
    elif int(year) == 2021:
        for key in cod_meses_indenizatorias_2021:
            if key == str(month):
                link = base_url + cod_meses_indenizatorias_2021[key]

                links_type["Membros ativos"] = link
    return links_type


def download(url, file_path):
    # Silence InsecureRequestWarning
    requests.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    try:
        response = requests.get(url, allow_redirects=True, verify=False)
        with open(file_path, "wb") as file:
            file.write(response.content)
        file.close()
    except Exception as excep:
        sys.stderr.write(
            "Não foi possível fazer o download do arquivo: "
            + file_path
            + ". O seguinte erro foi gerado: "
            + excep
        )
        os._exit(1)


def crawl(year, month, output_path):
    urls_remuneration = links_remuneration(month, year)
    files = []

    for element in urls_remuneration:
        pathlib.Path(output_path).mkdir(exist_ok=True)
        file_name = "membros-ativos-contracheque-" + month + "-" + year + ".odt"
        file_path = output_path + "/" + file_name
        download(urls_remuneration[element], file_path)
        files.append(file_path)

    if int(year) == 2018 or (int(year) == 2019 and int(month) < 7):
        # Não existe dados exclusivos de verbas indenizatórias nesse período de tempo.
        pass
    else:
        urls_perks = links_perks_temporary_funds(month, year)
        for element in urls_perks:
            pathlib.Path(output_path).mkdir(exist_ok=True)
            file_name_indemnity = (
                "membros-ativos-verbas-indenizatorias-" + month + "-" + year + ".ods"
            )

            file_path_indemnity = output_path + "/" + file_name_indemnity
            download(urls_perks[element], file_path_indemnity)
            files.append(file_path_indemnity)

    return files
