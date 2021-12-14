# coding: utf8
import sys
import os
from coleta import coleta_pb2 as Coleta

CONTRACHEQUE_2018 = "contracheque"
CONTRACHEQUE_2019_DEPOIS = "contracheque1"
INDENIZACOES = "indenizações"

HEADERS = {
    CONTRACHEQUE_2018: {
        "Remuneração do Cargo Efetivo": 5,
        "Outras Verbas Remuneratórias, Legais ou Judiciais": 6,
        "Função de Confiança ou Cargo em Comissão": 7,
        "Gratificação Natalina": 8,
        "Férias (1/3 constitucional)": 9,
        "Abono de Permanência": 10,
        "Contribuição Previdenciária": 12,
        "Imposto de Renda": 13,
        "Retenção por Teto Constitucional": 14,
        "Indenizações": 17,
        "Outras Remunerações Retroativas / Temporárias": 18,
    },
    CONTRACHEQUE_2019_DEPOIS: {
        "Remuneração do Cargo Efetivo": 4,
        "Outras Verbas Remuneratórias, Legais ou Judiciais": 5,
        "Função de Confiança ou Cargo em Comissão": 6,
        "Gratificação Natalina": 7,
        "Férias (1/3 constitucional)": 8,
        "Abono de Permanência": 9,
        "Contribuição Previdenciária": 13,
        "Imposto de Renda": 14,
        "Retenção por Teto Constitucional": 15,
    },
    INDENIZACOES: {
        "Auxílio Saúde": 4,
        "Dif. Auxílio-Saúde": 5,
        "Auxílio-Alimentação": 6,
        "Dif. Auxílio-Alimentação": 7,
        "Auxílio-Interiorização": 8,
        "Dif. Auxílio-Interiorização": 9,
        "Dif. Auxílio Lei 8.625/93": 10,
        "Indenizações Férias/Licença-Prêmio": 11,
        "Abono Pecuniário": 12,
        "Dif. Abono Pecuniário": 13,
        "Ressarcimentos": 14,
        "GEO": 16,
        "Dif. GEO": 17,
        "Insalubridade": 18,
        "Dif. Insalubridade": 19,
        "Periculosidade": 20,
        "Dif. Periculosidade": 21,
        "Adicional Trabalho Técnico": 22,
        "Dif. Adicional Trabalho Técnico": 23,
        "Grat. Atividade Ensino": 24,
        "Substituições": 25,
        "Dif. Substituições": 26,
        "Cumulação": 27,
        "Dif. Cumulação": 28,
        "Representação de Direção": 29,
        "Dif. Representação de Direção": 30,
        "Grat. Turma Recursal": 31,
        "Dif. Grat. Turma Recursal": 32,
        "Grat. Difícil Provimento": 33,
        "Dif. Grat. Difícil Provimento": 34,
        "Grat. Assessor": 35,
        "Dif. Grat. Assessor": 36,
        "Representação GAECO": 37,
        "Dif. Representação GAECO": 38,
    },
}


def parse_employees(fn, chave_coleta, ano):
    employees = {}
    counter = 1
    for row in fn:
        if row[0] == "Mês/Ano de Referencia:" or row[0] == "Mes/Ano de Referencia:" or row[0] == "TotalGeral" or row[0] == "Total Geral" or row[0] == "Data da última atualização:":
            continue
        if ano == 2018:
            matricula = str(row[1])
            name = row[2]
            funcao = row[3]
            local_trabalho = row[4]
        else:
            matricula = str(row[0])
            name = row[1]
            funcao = row[2]
            local_trabalho = row[3]
        if not is_nan(name) and name != "0" and matricula != "Matrícula" and matricula != "TotalGeral":
            membro = Coleta.ContraCheque()
            membro.id_contra_cheque = chave_coleta + "/" + str(counter)
            membro.chave_coleta = chave_coleta
            membro.nome = name
            membro.matricula = matricula
            membro.funcao = funcao
            membro.local_trabalho = local_trabalho
            membro.tipo = Coleta.ContraCheque.Tipo.Value("MEMBRO")
            membro.ativo = True
            if int(ano) == 2018:
                membro.remuneracoes.CopyFrom(
                    cria_remuneracao(row, CONTRACHEQUE_2018)
                )
            else:
                membro.remuneracoes.CopyFrom(
                    cria_remuneracao(row, CONTRACHEQUE_2019_DEPOIS)
                )
            employees[name] = membro
            counter += 1
    return employees


def cria_remuneracao(row, categoria):
    remu_array = Coleta.Remuneracoes()
    items = list(HEADERS[categoria].items())
    for i in range(len(items)):
        key, value = items[i][0], items[i][1]
        remuneracao = Coleta.Remuneracao()
        remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("R")
        if categoria == INDENIZACOES:
            remuneracao.categoria = categoria
        else:
            remuneracao.categoria = "contracheque"
        remuneracao.item = key
        remuneracao.valor = format_value(row[value])
        if categoria == CONTRACHEQUE_2018:
            if value == 5:
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("B")
            elif value in [12, 13, 14]:
                remuneracao.valor = remuneracao.valor * (-1)
                remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("D")
            elif value in [6, 7, 8, 9, 10, 17, 18]:
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
        elif categoria == CONTRACHEQUE_2019_DEPOIS:
            if value == 4:
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("B")
            elif value in [13, 14, 15]:
                remuneracao.valor = remuneracao.valor * (-1)
                remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("D")
            elif value in [5, 6, 7, 8, 9]:
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
        else:
            remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")

        remu_array.remuneracao.append(remuneracao)
    return remu_array


def update_employees(fn, employees, categoria):
    for row in fn:
        name = row[1]
        if name in employees.keys():
            emp = employees[name]
            remu = cria_remuneracao(row, categoria)
            emp.remuneracoes.MergeFrom(remu)
            employees[name] = emp
    return employees


def is_nan(string):
    return string != string


def parse(data, chave_coleta, mes, ano):
    employees = {}
    folha = Coleta.FolhaDePagamento()
    if int(ano) == 2018 or (int(ano) == 2019 and int(mes) < 7):
        try:
            employees.update(parse_employees(data.contracheque, chave_coleta, ano))

        except KeyError as e:
            sys.stderr.write(
                "Registro inválido ao processar contracheque: {}".format(e)
            )
            os._exit(1)
    else:
        try:
            employees.update(parse_employees(data.contracheque, chave_coleta, ano))
            update_employees(data.indenizatorias, employees, INDENIZACOES)

        except KeyError as e:
            sys.stderr.write(
                "Registro inválido ao processar contracheque ou indenizações: {}".format(e)
            )
            os._exit(1)
    for i in employees.values():
        folha.contra_cheque.append(i)
    return folha


def format_value(element):
    # A value was found with incorrect formatting. (3,045.99 instead of 3045.99)
    if is_nan(element):
        return 0.0
    if type(element) == str:
        if "." in element and "," in element:
            element = element.replace(".", "").replace(",", ".")
        elif "," in element:
            element = element.replace(",", ".")
        elif "-" in element:
            element = 0.0

    return float(element)
