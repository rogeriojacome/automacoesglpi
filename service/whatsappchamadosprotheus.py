import requests
import json
import datetime
import mysql.connector
import os

token = "seutoken"

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_arquivo_json = os.path.join(diretorio_atual, 'config','glpi','data', 'bancoglpiprod.json')
with open(caminho_arquivo_json, 'r') as arquivo:
    db_config = json.load(arquivo)

def listachamados():

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    consultarelease = """SELECT tagi.items_id, loc.name,solicitante.name as solicitante FROM glpi.glpi_plugin_tag_tagitems tagi
    INNER JOIN glpi.glpi_plugin_tag_tags tag ON tag.id = tagi.plugin_tag_tags_id
    INNER JOIN glpi.glpi_tickets tic ON tic.id = tagi.items_id
    LEFT JOIN glpi.glpi_tickets_users tus_ ON tus_.tickets_id = tic.id
    AND tus_.type = 1
    LEFT JOIN glpi.glpi_users solicitante ON solicitante.id = tus_.users_id
    LEFT JOIN glpi.glpi_locations loc ON solicitante.locations_id = loc.id
    WHERE tag.id = 586
    GROUP BY tagi.items_id, loc.name,solicitante
    """

    cursor.execute(consultarelease)
    results = cursor.fetchall()
    return results


def mensagemtexto():
    data_atual = datetime.date.today()
    data_atual_formatada = data_atual.strftime("%d/%m/%Y")
    listadechamados = listachamados()
    mensagem =  "\ud83d\udea8  *Atenção* \ud83d\udea8 \n \n"
    mensagem += "\ud83d\udce2 \ud83d\udce2 _Protheus informa_ \ud83d\udce2 \ud83d\udce2 \n \n"
    mensagem += "\ud83d\udccd Será realizada uma ATUALIZAÇÃO em ambiente de PRODUÇÃO\n \n"
    mensagem += "\ud83d\udcc5 *Início: " + data_atual_formatada + " às 22:00hs* \n"
    mensagem += " *Término: " + data_atual_formatada + " às 23:00hs* \n \n"
    mensagem += "\ud83d\udd14 _* Por favor sair do sistema, pois haverá indisponibilidade durante essa atualização *_ \n \n \n"
    #mensagem += "\ud83d\udc68\u200d\ud83d\udcbb _~*Chamados da Release: *~_ \n \n"
    #for lista in listadechamados:
     #   mensagem += "*Chamado:* " + str(lista[0]) + "\n"
     #   mensagem += "*Setor:* " + lista[1] + "\n"
     #   mensagem += "*Solicitante:* " + lista[2] + "\n \n"
    mensagem += "\n \n \n"
    mensagem += "\ud83d\udcde _Segue o telefone do nosso plantão: (85) 99983-0557 | Whatsapp: (85) 4005-1948_"

    return mensagem


def enviamensagem(id,mensagem):
    urlenvio = "https://api.connectzap.com.br/sistema/sendTextGrupo"
    dataenvio = {
        "SessionName": token,
        "groupId": id,
        "msg": mensagem
    }
    repostaenvio = requests.post(urlenvio, json=dataenvio)
    if repostaenvio.status_code == 200:
        print("Mensagem enviada com sucesso")

    return

def preparamensagem():
# URL da API
    url = "https://api.connectzap.com.br/sistema/getAllGroups"

    # Dados JSON para o corpo da solicitação
    data = {
        "SessionName": token
    }
    # Enviar a solicitação POST com os dados JSON
    response = requests.post(url, json=data)

    # Verificar se a solicitação foi bem-sucedida (código de status 200)
    if response.status_code == 200:
        # Converter a resposta JSON em um dicionário Python
        msgqueseraenviada = mensagemtexto()
        result = response.json()
        getAllGroups = result["Status"]["getAllGroups"]

    # Agora você pode iterar sobre os elementos do array ou acessar os valores individualmente
    for group in getAllGroups:
        #group_id = '120363158789566980'  # group["user"]
        group_id = group["user"]
        print(group['name'])
        enviamensagem(group_id,msgqueseraenviada)
    else:
        print("Erro na solicitação. Código de status:", response.status_code)

if __name__ == "__main__":
    preparamensagem()

