import json
import os
from datetime import datetime

import mysql.connector

import whatsappchamadosprotheus

# confirmacao de teste para o git
# Configurações do banco de dados

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_arquivo_json = os.path.join(diretorio_atual, 'config', 'glpi', 'data', 'bancoglpiprod.json')
with open(caminho_arquivo_json, 'r') as arquivo:
    db_config = json.load(arquivo)


def verifirareleasedia():
    global release, consultarelease
    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y")
    release = 'Release ' + date_time
    release = release.replace('/', '.')

    consultarelease = f"SELECT * FROM glpi.glpi_plugin_tag_tags tags where tags.name like '%{release}%'"

    cursor.execute(consultarelease)
    results = cursor.fetchall()
    return results


def etiquetadianoschamados(idrelease):
    # Etapa 4: Adicionar a etiqueta da release do dia
    add_new_tag_query = "INSERT INTO glpi_plugin_tag_tagitems (items_id, plugin_tag_tags_id,itemtype)"
    add_new_tag_query += f" SELECT tagi.items_id, {idrelease}, 'Ticket' FROM glpi.glpi_plugin_tag_tagitems tagi"
    add_new_tag_query += " INNER JOIN glpi.glpi_plugin_tag_tags tag ON tag.id = tagi.plugin_tag_tags_id"
    add_new_tag_query += " INNER JOIN glpi.glpi_tickets tic ON tic.id = tagi.items_id"
    add_new_tag_query += " LEFT JOIN glpi.glpi_plugin_tag_tagitems itens on tagi.items_id = itens.items_id"
    add_new_tag_query += f" AND itens.plugin_tag_tags_id = {idrelease} AND itens.itemtype = 'Ticket'"
    add_new_tag_query += " WHERE tag.id = 586"
    add_new_tag_query += " and itens.id is null"

    cursor.execute(add_new_tag_query)
    connection.commit()
    print("Etapa 4 concluída: Nova tag adicionada aos chamados correspondentes.")


def etiquetafeedbackchamados():
    # Etapa 5: Adicionar a tag 214 aos mesmos chamados, se necessário
    add_tag_214_query = " INSERT INTO glpi_plugin_tag_tagitems (items_id, plugin_tag_tags_id,itemtype)"
    add_tag_214_query += " SELECT tagi.items_id, 214, 'Ticket' FROM glpi.glpi_plugin_tag_tagitems tagi"
    add_tag_214_query += " INNER JOIN glpi.glpi_plugin_tag_tags tag ON tag.id = tagi.plugin_tag_tags_id"
    add_tag_214_query += " INNER JOIN glpi.glpi_tickets tic ON tic.id = tagi.items_id"
    add_tag_214_query += " LEFT JOIN glpi.glpi_plugin_tag_tagitems itens on tagi.items_id = itens.items_id"
    add_tag_214_query += " AND itens.plugin_tag_tags_id = 214 AND itens.itemtype = 'Ticket'"
    add_tag_214_query += " WHERE tag.id = 586"
    add_tag_214_query += " and itens.id is null"

    cursor.execute(add_tag_214_query)
    connection.commit()
    print("Etapa 5 concluída: Tag 214 adicionada aos chamados, se necessário.")


def deletadeployproducao():
    # Etapa 6: retira a etiqueta de deploy de producao
    wait_query = " DELETE FROM glpi_plugin_tag_tagitems"
    wait_query += " WHERE plugin_tag_tags_id = 586"

    cursor.execute(wait_query)
    connection.commit()
    print("Etapa 6 concluída: Aguardo de 5 segundos.")


try:
    # Envia o comunicado da janela via whatsapp para todos os grupos
    whatsappchamadosprotheus.preparamensagem()
    # Conectando ao banco de dados
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    print("Conexão ao banco de dados estabelecida.")

    results = verifirareleasedia()
    if not results:
        insert_release = " INSERT INTO glpi_plugin_tag_tags (entities_id, is_recursive, name, comment, color)"
        insert_release += f" VALUES (15, 1, '{release}', '{release}', '#aeff00')"
        cursor.execute(insert_release)
        connection.commit()

        # Etapa 3: Pegar o ID da nova tag
    cursor.execute(consultarelease)
    results = cursor.fetchall()
    for idnovarelease in results:
        etiquetadianoschamados(
            str(idnovarelease[0]))  # Adiciona a etique do dia nos chamados que estão com deploy em produção

        etiquetafeedbackchamados()  # Adiciona a eituqe de aguardando feedback do usuários para os chamados que estão com deploy em produção

        deletadeployproducao()  # Retira a etiqueta de deploy em produção do chamados que subiram

except mysql.connector.Error as err:
    print("Erro ao executar o script:", err)

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Conexão ao banco de dados encerrada.")
