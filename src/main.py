# coding: utf8
import sys
import os
import crawler
from parser import parse
import metadado
import data
from coleta import coleta_pb2 as Coleta, IDColeta
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf import text_format

if "YEAR" in os.environ:
    year = os.environ["YEAR"]
else:
    sys.stderr.write("Invalid arguments, missing parameter: 'YEAR'.\n")
    os._exit(1)

if "MONTH" in os.environ:
    month = os.environ["MONTH"]
    month = month.zfill(2)
else:
    sys.stderr.write("Invalid arguments, missing parameter: 'MONTH'.\n")
    os._exit(1)

if "OUTPUT_FOLDER" in os.environ:
    output_path = os.environ["OUTPUT_FOLDER"]
else:
    output_path = "/output"

if "GIT_COMMIT" in os.environ:
    crawler_version = os.environ["GIT_COMMIT"]
else:
    crawler_version = "unspecified"


def parse_execution(data, file_names):
    # Cria objeto com dados da coleta.
    coleta = Coleta.Coleta()
    coleta.chave_coleta = IDColeta("mpse", month, year)
    coleta.orgao = "mpse"
    coleta.mes = int(month)
    coleta.ano = int(year)
    coleta.repositorio_coletor = "https://github.com/dadosjusbr/coletor-mpse"
    coleta.versao_coletor = crawler_version
    coleta.arquivos.extend(file_names)
    timestamp = Timestamp()
    timestamp.GetCurrentTime()
    coleta.timestamp_coleta.CopyFrom(timestamp)

    # Consolida folha de pagamento
    folha = Coleta.FolhaDePagamento()
    folha = parse(data, coleta.chave_coleta, int(month), int(year))

    # Monta resultado da coleta.
    rc = Coleta.ResultadoColeta()
    rc.folha.CopyFrom(folha)
    rc.coleta.CopyFrom(coleta)

    metadados = metadado.captura(int(month), int(year))
    rc.metadados.CopyFrom(metadados)

    # Imprime a versão textual na saída padrão.
    print(text_format.MessageToString(rc), flush=True, end="")


# Main execution
def main():
    file_names = crawler.crawl(year, month, output_path)

    dados = data.load(file_names, year, month, output_path)

    # Se não acontecer nada, é porque está tudo ok!
    if int(year) == 2018 or (int(year) == 2019 and int(month) < 7):
        dados.validate_2018(output_path)
    else:
        dados.validate(output_path)

    parse_execution(dados, file_names)


if __name__ == "__main__":
    main()
