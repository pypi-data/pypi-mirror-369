# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "aiohttp>=3.12.15",
#     "dateparser>=1.2.2",
#     "fastmcp>=2.11.1",
#     "ujson>=5.10.0",
# ]
# ///

import os
from fastmcp import FastMCP

import aiohttp
import ujson
from datetime import datetime, timedelta

from collections.abc import Mapping, Sequence
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import html
import re
import calendar
from typing import Any, cast, Literal, Optional

from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("My MCP Server", host=os.getenv("HOST"), port=os.getenv("PORT"))

# Lista dos Tipos de Atendimento.
TYPE_TO_NUMBER = {
    "Suporte Sistema": 1,
    "Implementação": 2,
    "Manutenção Corretiva": 3,
    "Reunião": 4,
    "Treinamento": 5,
    "Mudança de Escopo": 20,
    "Anexo": 12,
    "Suporte Infraestrutura": 13,
    "Monitoramento": 21,
    "Incidente": 23,
    "Requisição": 24,
}

# Mapeamento de meses em português
MESES_PT = {
    "janeiro": 1,
    "jan": 1,
    "fevereiro": 2,
    "fev": 2,
    "março": 3,
    "mar": 3,
    "abril": 4,
    "abr": 4,
    "maio": 5,
    "mai": 5,
    "junho": 6,
    "jun": 6,
    "julho": 7,
    "jul": 7,
    "agosto": 8,
    "ago": 8,
    "aug": 8,
    "setembro": 9,
    "set": 9,
    "sep": 9,
    "outubro": 10,
    "out": 10,
    "oct": 10,
    "novembro": 11,
    "nov": 11,
    "dezembro": 12,
    "dez": 12,
    "dec": 12,
}

# Mapeamento de dias da semana em português
DIAS_SEMANA_PT = {
    "segunda": 0,
    "segunda-feira": 0,
    "seg": 0,
    "terça": 1,
    "terça-feira": 1,
    "ter": 1,
    "terca": 1,
    "terca-feira": 1,
    "quarta": 2,
    "quarta-feira": 2,
    "qua": 2,
    "quinta": 3,
    "quinta-feira": 3,
    "qui": 3,
    "sexta": 4,
    "sexta-feira": 4,
    "sex": 4,
    "sábado": 5,
    "sabado": 5,
    "sab": 5,
    "domingo": 6,
    "dom": 6,
}

# Palavras que indicam tempo futuro/passado
TEMPO_FUTURO = [
    "próximo",
    "proximo",
    "que vem",
    "seguinte",
    "vindouro",
    "daqui a",
    "daqui",
    "vindoura",
    "entrante",
]
TEMPO_PASSADO = [
    "passado",
    "anterior",
    "ultimo",
    "último",
    "atrás",
    "atras",
    "ha",
    "há",
    "retrasado",
    "retrasada",
]

# Números por extenso
NUMEROS_EXTENSO = {
    "um": 1,
    "uma": 1,
    "dois": 2,
    "duas": 2,
    "três": 3,
    "tres": 3,
    "quatro": 4,
    "cinco": 5,
    "seis": 6,
    "sete": 7,
    "oito": 8,
    "nove": 9,
    "dez": 10,
    "onze": 11,
    "doze": 12,
    "treze": 13,
    "catorze": 14,
    "quatorze": 14,
    "quinze": 15,
    "dezesseis": 16,
    "dezessete": 17,
    "dezoito": 18,
    "dezenove": 19,
    "vinte": 20,
    "trinta": 30,
}

# Expressões de período do dia
PERIODOS_DIA = {
    "manhã": 8,
    "manha": 8,
    "de manhã": 8,
    "de manha": 8,
    "tarde": 14,
    "de tarde": 14,
    "à tarde": 14,
    "a tarde": 14,
    "noite": 20,
    "de noite": 20,
    "à noite": 20,
    "a noite": 20,
    "madrugada": 2,
    "de madrugada": 2,
}


class XMLBuilder:
    """Classe genérica para montagem dinâmica de XML a partir de dados estruturados."""

    @staticmethod
    def normalize_field_name(field_name: str) -> str:
        """Converte automaticamente nomes de campos para formato XML válido.

        Args:
            field_name (str): Nome do campo original

        Returns:
            str: Nome do campo normalizado para XML
        """
        if not field_name:
            return "campo_vazio"

        # Converter para lowercase
        normalized = field_name.lower()

        # Remover acentos e caracteres especiais, manter apenas letras, números e underscore
        normalized = re.sub(r"[^\w\s]", "", normalized)

        # Substituir espaços por underscore
        normalized = re.sub(r"\s+", "_", normalized)

        # Remover underscores consecutivos
        normalized = re.sub(r"_+", "_", normalized)

        # Remover underscore do início e fim
        normalized = normalized.strip("_")

        # Se começar com número, adicionar prefixe
        if normalized and normalized[0].isdigit():
            normalized = f"campo_{normalized}"

        # Se ficou vazio, usar nome padrão
        if not normalized:
            normalized = "campo_sem_nome"

        return normalized

    @staticmethod
    def clean_html_entities(text: str) -> str:
        """Remove entidades HTML e limpa o texto.

        Args:
            text (str): Texto a ser limpo

        Returns:
            str: Texto limpo
        """
        # Converter para string se não for
        text = str(text)

        # Fazer unescape de entidades HTML
        text = html.unescape(text)

        # Remover tags HTML se existirem
        text = re.sub(r"<[^>]+>", "", text)

        # Limpar espaços extras
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def build_xml(
        self,
        data: Sequence[Mapping[str, Any]] | Mapping[str, Any],
        root_element_name: str = "root",
        item_element_name: str = "item",
        root_attributes: Mapping[str, str] | None = None,
        custom_attributes: Mapping[str, Any] | None = None,
    ) -> str:
        """Constrói XML dinamicamente a partir de uma lista de dicionários.

        Args:
            data (Sequence[Mapping[str, Any]]): Lista de dicionários com os dados
            root_element_name (str): Nome do elemento raiz
            item_element_name (str): Nome do elemento para cada item da lista
            root_attributes (Mapping[str, str]]) | None Atributos para o elemento raiz
            custom_attributes (Mapping[str, Any]]) | None Atributos customizados adicionais

        Returns:
            str: XML bem formatado
        """
        # Criar elemento raiz
        root = Element(root_element_name)

        # Adicionar atributos padrão
        if root_attributes:
            for key, value in root_attributes.items():
                root.set(key, str(value))

        # Adicionar total de itens como atributo
        root.set("total", str(len(data)))

        # Adicionar atributos customizados
        if custom_attributes:
            for key, value in custom_attributes.items():
                root.set(key, str(value))

        if isinstance(data, Mapping):
            data = [data]

        # Processar cada item automaticamente
        for item_data in data:
            item_element = SubElement(root, item_element_name)

            # Adicionar todos os campos automaticamente
            for key, value in item_data.items():
                # Normalizar nome do campo automaticamente
                xml_field_name = self.normalize_field_name(key)

                # Criar elemento filho
                field_element = SubElement(item_element, xml_field_name)

                # Limpar valor de entidades HTML e definir texto
                cleaned_value = self.clean_html_entities(value)
                field_element.text = cleaned_value

        return self._format_xml(root)

    def build_single_item_xml(
        self,
        data: Mapping[str, Any],
        root_element_name: str = "root",
        root_attributes: Mapping[str, str] | None = None,
    ) -> str:
        """Constrói XML para um único item (dicionário).

        Args:
            data (Dict[str, Any]): Dicionário com os dados
            root_element_name (str): Nome do elemento raiz
            root_attributes (Mapping[str, str]]) | None Atributos para o elemento raiz

        Returns:
            str: XML bem formatado
        """
        # Criar elemento raiz
        root = Element(root_element_name)

        # Adicionar atributos
        if root_attributes:
            for key, value in root_attributes.items():
                root.set(key, str(value))

        # Adicionar todos os campos automaticamente
        for key, value in data.items():
            # Normalizar nome do campo automaticamente
            xml_field_name = self.normalize_field_name(key)

            # Criar elemento filho
            field_element = SubElement(root, xml_field_name)

            # Limpar valor de entidades HTML e definir texto
            cleaned_value = self.clean_html_entities(value)
            field_element.text = cleaned_value

        return self._format_xml(root)

    def build_nested_xml(
        self,
        data: Mapping[str, Any],
        root_element_name: str = "root",
        root_attributes: Mapping[str, str] | None = None,
    ) -> str:
        """Constrói XML para estruturas aninhadas (dicionários e listas).

        Args:
            data (Dict[str, Any]): Dados com estrutura aninhada
            root_element_name (str): Nome do elemento raiz
            root_attributes (Mapping[str, str]]) | None Atributos para o elemento raiz

        Returns:
            str: XML bem formatado
        """
        root = Element(root_element_name)

        if root_attributes:
            for key, value in root_attributes.items():
                root.set(key, str(value))

        self._add_nested_elements(root, data)
        return self._format_xml(root)

    def _add_nested_elements(self, parent: Element, data: Any) -> None:
        """Adiciona elementos aninhados recursivamente.

        Args:
            parent (Element): Elemento pai
            data (Any): Dados a serem processados
        """
        if isinstance(data, dict):
            for key, value in data.items():
                xml_field_name = self.normalize_field_name(cast(Any, key))

                if isinstance(value, (dict, list)):
                    # Criar elemento para estrutura aninhada
                    nested_element = SubElement(parent, xml_field_name)
                    self._add_nested_elements(nested_element, value)
                else:
                    # Elemento simples
                    field_element = SubElement(parent, xml_field_name)
                    cleaned_value = self.clean_html_entities(cast(Any, value))
                    field_element.text = cleaned_value

        elif isinstance(data, list):
            for i, item in enumerate(cast(Any, data)):
                item_element = SubElement(parent, f"item_{i}")
                self._add_nested_elements(item_element, item)
        else:
            # Valor simples
            parent.text = self.clean_html_entities(data)

    def _format_xml(self, root: Element) -> str:
        """Formata o XML com indentação bonita.

        Args:
            root (Element): Elemento raiz

        Returns:
            str: XML formatado
        """
        # Converter para string com formatação bonita e encoding UTF-8
        rough_string = tostring(root, encoding="unicode")
        reparsed = minidom.parseString(rough_string)

        # Remover linha em branco extra do toprettyxml
        pretty_xml = reparsed.toprettyxml(indent="  ", encoding=None)

        # Limpar linhas vazias extras
        lines = [line for line in pretty_xml.split("\n") if line.strip()]
        return "\n".join(lines)


async def buscar_info_colaboradores() -> str:
    """Lista os atendimentos avulsos abertos do usuario.

    Args:
        matricula (str | int): a matricula do usuario
        codigo_os (str): a Ordem de Serviço (OS)
        data_inicio (str): a data de inicio dos atendimentos
        data_final(str): a data final dos atendimentos


    Returns:
        str: um XML bem formatado indicando os atendimentos das OS.
    """
    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/usuarios/buscarInformacoesUsuariosSIGA/",
            json={
                "apiKey": os.getenv("AVA_API_KEY")
            }
        ) as response:
            json = await response.json(content_type=None)
            retorno = XMLBuilder().build_xml(
                data=json["result"],
                root_element_name="colaboradores",
                item_element_name="colaborador",
            )

            return retorno


@mcp.tool
async def buscar_informacoes_atendimentos_os(codigo_atendimento: int) -> str:
    """Busca Informações do atendimento avulso aberto pelo usuario. Serve de consulta para edição do atendimento os.

    Args:
        codigo_atendimento (int): o código do atendimento

    Returns:
        str: um XML bem formatado indicando os dados/informações do atendimento OS.
    """
    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/atendimentosOs/buscarInfoAtendimentosOsSigaIA/",
            json={
                "atendimento": codigo_atendimento,
                "apiKey": os.getenv("AVA_API_KEY"),
            },
        ) as response:
            try:
                json = await response.json(content_type=None)
                retorno = XMLBuilder().build_xml(
                    data=json["result"],
                    root_element_name="info_atendimentos_os",
                    item_element_name="info_atendimentos_os",
                    root_attributes={
                        "atendimento": str(codigo_atendimento),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception:
                return "Erro ao buscar as informações do atendimento."


@mcp.tool
async def buscar_pendencias_lancamentos_atendimentos(
    matricula: str | int,
    dataIni: str | Literal["hoje", "agora", "ontem"],
    dataFim: str | Literal["hoje", "agora", "ontem"],
) -> str:
    """Busca a listagem dos dias que o usuário (analista) não efetuou registros no SIGA, nem de criação de OS ou Atendimentos OS ou Atendimentos Avulsos.

    Args:
        matricula (str): a matricula do usuario (analista)
        dataIni (str): a data inicio
        dataFim(str): a data final

    Returns:
        str: um XML bem formatado indicando as OS em aberto.
    """

    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/atendimentosAvulsos/buscarPendenciasRegistroAtendimentosSigaIA/",
            json={
                "matricula": matricula,
                "dataIni": converter_data_siga(dataIni),
                "dataFim": converter_data_siga(dataFim),
                "apiKey": os.getenv("AVA_API_KEY"),
            },
        ) as response:
            try:
                # Verifica se a requisição HTTP foi bem-sucedida (status 2xx)
                response.raise_for_status()

                # Converte a resposta para JSON, permitindo qualquer content-type
                data = await response.json(content_type=None)

                retorno = XMLBuilder().build_xml(
                    # Usa [] se 'result' não existir ou for None
                    data=data.get("result", []),
                    root_element_name="pendencias_lançamentos",
                    item_element_name="pendencias_lançamentos",
                    root_attributes={"matricula": str(matricula)},
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception:
                # Captura qualquer outro erro não previsto
                return "Erro ao consultar todas as pendências de registros SIGA do usuário."


@mcp.tool
async def buscar_todas_os_usuario(
    matricula: str | Sequence[str] | None = None,
    os: str | Sequence[str] | None = None,
    filtrar_por: Sequence[
        Literal[
            "Pendente-Atendimento",
            "Em Teste",
            "Pendente-Teste",
            "Em Atendimento",
            "Em Implantação",
            "Pendente-Liberação",
            "Concluída por Encaminhamento",
            "Concluída",
            "Concluída por substituição",
            "Não Planejada",
            "Pendente-Sist. Administrativos",
            "Pendente-AVA",
            "Pendente-Consultoria",
            "Solicitação em Aprovação",
            "Pendente-Aprovação",
            "Pendente-Sist. Acadêmicos",
            "Pendente-Marketing",
            "Pendente-Equipe Manutenção",
            "Pendente-Equipe Infraestrutura",
            "Pendente-Atualização de Versão",
            "Pendente-Help-Desk",
            "Cancelamento DTI | Arquivado",
            "Cancelada-Usuário",
            "Pendente-Fornecedor",
            "Pendente-Usuário",
        ]
    ]
    | Literal["Todas OS em Aberto"]
    | str
    | None = None,
    data_inicio: str | Literal["hoje", "agora", "ontem"] | None = None,
    data_fim: str | Literal["hoje", "agora", "ontem"] | None = None,
) -> str:
    """Busca todas as Ordens de Serviços (OS) do usuário.

    Casos de uso principais:
        1. OS em aberto (uma matrícula): filtrar_por="Todas OS em Aberto", matricula="123"
        2. OS em aberto (múltiplas matrículas): filtrar_por="Todas OS em Aberto", matricula=["123", "456"]
        3. OS por status (uma matrícula): filtrar_por=["Concluída"], matricula="123"
        4. OS por status (múltiplas matrículas): filtrar_por=["Concluída"], matricula=["123", "456"]
        5. OS específica (uma OS): os="12345", matricula=None ou preenchida
        6. OS específicas (múltiplas OS): os=["12345", "67890"], matricula=None ou preenchida
        7. Todas as OS: filtrar_por=None, matricula preenchida
        8. "Liste minhas OS": interpretar como OS em aberto

    Args:
        matricula (str | Sequence[str] | None):
            - String única: "12345"
            - Lista: ["12345", "67890", "11111"] para múltiplas matrículas
            - None: quando consulta OS específica sem filtro de usuário
        os (str | Sequence[str] | None):
            - String única: "98765"
            - Lista: ["98765", "54321", "11111"] para múltiplas OS
            - None: quando não é consulta de OS específica
        filtrar_por: Status para filtrar:
            - "Todas OS em Aberto": grupo pré-definido
            - Lista: ["Concluída", "Pendente-Teste"] para múltiplos status
            - None: sem filtro de status
        data_inicio (str | None): Data início DD/MM/AAAA
        data_fim (str | None): Data fim DD/MM/AAAA

    Returns:
        str: um XML bem formatado indicando as todas OS do usuário.

     Examples:
        - "minhas OS em aberto" → matricula="user", filtrar_por="Todas OS em Aberto"
        - "OS das matrículas 123 e 456" → matricula=["123", "456"], filtrar_por="Todas OS em Aberto"
        - "OS concluídas das matrículas 123, 456, 789" → matricula=["123", "456", "789"], filtrar_por=["Concluída", "Concluída por Encaminhamento"]
        - "detalhes das OS 1001 e 1002" → os=["1001", "1002"], matricula=None
        - "minhas OS 1001, 1002 e 1003" → os=["1001", "1002", "1003"], matricula="user"
        - "OS 12345" → os="12345", matricula=None (uma OS apenas)

    Note:
        Pelo menos 'matricula' ou 'os' deve ter valor válido para executar a consulta.
    """

    if not matricula and not os:
        return "Erro: É necessário informar pelo menos a matrícula ou o código da OS para realizar a consulta."

    if filtrar_por == "Todas OS em Aberto":
        filtrar_por = [
            "Pendente-Atendimento",
            "Em Teste",
            "Pendente-Teste",
            "Em Atendimento",
            "Em Implantação",
            "Pendente-Liberação",
            "Não Planejada",
            "Pendente-Sist. Administrativos",
            "Pendente-AVA",
            "Pendente-Consultoria",
            "Solicitação em Aprovação",
            "Pendente-Aprovação",
            "Pendente-Sist. Acadêmicos",
            "Pendente-Marketing",
            "Pendente-Equipe Manutenção",
            "Pendente-Equipe Infraestrutura",
            "Pendente-Atualização de Versão",
            "Pendente-Help-Desk",
            "Pendente-Fornecedor",
            "Pendente-Usuário",
        ]

    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/os/buscarTodasOsPorMatriculaSigaIA/",
            json={
                "descricaoStatusOs": filtrar_por or "",  # Array ou string puro
                "matricula": matricula or "",  # Array ou string puro
                "codOs": os or "",  # Array ou string puro
                "dataIni": converter_data_siga(data_inicio) if data_inicio else "",
                "dataFim": converter_data_siga(data_fim) if data_fim else "",
                "apiKey": os.getenv("AVA_API_KEY"),
            },
        ) as response:
            try:
                # Verifica se a requisição HTTP foi bem-sucedida (status 2xx)
                # response.raise_for_status()

                data = await response.json(content_type=None)
                retorno = XMLBuilder().build_xml(
                    data=data["result"],
                    root_element_name="ordens_servico",
                    item_element_name="ordem_servico",
                    root_attributes={"matricula": str(matricula)},
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception:
                # Captura qualquer outro erro não previsto
                return "Erro ao consultar dados da(s) OS."


@mcp.tool
async def editar_atendimentos_os(
    codigo_atendimento: int,
    codigo_os: int,
    data_inicio: str,
    codigo_analista: int,
    descricao_atendimento: str,
    tipo_atendimento: Literal[
        "Suporte Sistema",
        "Implementação",
        "Manutenção Corretiva",
        "Reunião",
        "Treinamento",
        "Mudança de Escopo",
        "Anexo",
        "Suporte Infraestrutura",
        "Monitoramento",
        "Incidente",
        "Requisição",
    ] = "Implementação",
    data_fim: str | Literal["hoje", "agora", "ontem"] | None = None,
    tempo_gasto: int | None = None,
    primeiro_atendimento: bool = False,
    apresenta_solucao: bool = False,
) -> str:
    """Edita as informações do atendimento OS pelo usuario.

    Args:
        atendimento (int): o número do atendimento da OS
        os (int): o número da OS
        dataIni (str): a data e hora inicial do atendimento os
        analista (int): a matricula do usuario / analista
        descricao (str): a descrição do atendimento os
        tipo (str): o tipo do atendimento os
        dataFim (str): a data e hora final do atendimento os
        tempoGasto (int): o tempo gasto do atendimento os
        primeiroAtendimento (int): quando for o primeiro atendimento os
        apresentaSolucao (int): quando for apresentada a solução para o atendimento os

    Returns:
        str: um XML bem formatado indicando que o atendimento da os foi ou não editado com sucesso.
    """

    if data_inicio:
        data_inicio = converter_data_siga(data_inicio, manter_horas=True)

    if data_fim:
        data_fim = converter_data_siga(data_fim, manter_horas=True)

    # Busca o tipo correto na constante TYPE_TO_NUMBER ignorando maiúsculas/minúsculas
    tipo_normalizado = next(
        # Expressão geradora que itera sobre todas as chaves do dicionário TYPE_TO_NUMBER
        (
            key
            for key in TYPE_TO_NUMBER.keys()
            # Compara a chave atual em minúsculas com o tipo recebido em minúsculas
            if str(key).lower() == str(tipo_atendimento).lower()
        ),
        # Se nenhuma correspondência for encontrada, retorna None como valor padrão
        None,
    )

    # Verifica se foi encontrado um tipo válido após a busca case-insensitive
    if tipo_normalizado is None:
        # Retorna XML de erro em vez de levantar exceção
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "tipo_invalido",
                    "tipo_informado": tipo_atendimento,
                    "mensagem": f"Tipo '{tipo_atendimento}' não encontrado na constante TYPE_TO_NUMBER",
                    "tipos_validos": list(TYPE_TO_NUMBER.keys()),
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "editar_atendimentos_os"},
            custom_attributes={"sistema": "SIGA"},
        )

    tipo_final = TYPE_TO_NUMBER[tipo_normalizado]

    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/atendimentosOs/updateAtendimentosOsSigaIA/",
                json={
                    "atendimento": codigo_atendimento,
                    "os": codigo_os,
                    "dataIni": data_inicio,
                    "analista": codigo_analista,
                    "descricao": descricao_atendimento,
                    "tipo": tipo_final,
                    "dataFim": data_fim if data_fim else "",
                    "tempoGasto": tempo_gasto if tempo_gasto else "",
                    "primeiroAtendimento": primeiro_atendimento,
                    "apresentaSolucao": apresenta_solucao,
                    "apiKey": os.getenv("AVA_API_KEY"),
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Não foi possível editar o atendimento. Verifique as informações digitadas.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "Atendimento editado com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao editar o atendimento. Tente novamente.",
                        }
                    ]

                # Adiciona os root_attributes
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="ordens_servico",
                    item_element_name="ordem_servico",
                    root_attributes={
                        "os": str(codigo_os),
                        "dataIni": str(data_inicio),
                        "analista": str(codigo_analista),
                        "descricao": str(descricao_atendimento),
                        "tipo": str(tipo_normalizado),
                        "dataFim": str(data_fim),
                        "tempoGasto": str(tempo_gasto),
                        "primeiroAtendimento": str(primeiro_atendimento),
                        "apresentaSolucao": str(apresenta_solucao),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

    except Exception as e:
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "mensagem": f"Erro interno: {str(e)}. Tente novamente mais tarde.",
                }
            ],
            root_element_name="resultado",
            item_element_name="item",
            custom_attributes={"sistema": "SIGA"},
        )


@mcp.tool
async def excluir_atendimentos_os(
    codigo_atendimento: int,
) -> str:
    """exclui as informações do atendimento OS pelo usuario.

    Args:
        atendimento (int): o número do atendimento da OS

    Returns:
        str: um XML bem formatado indicando que o atendimento da os foi ou não excluído com sucesso.
    """

    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/atendimentosOs/excluiAtendimentosOsSigaIA/",
                json={
                    "atendimento": codigo_atendimento,
                    "apiKey": os.getenv("AVA_API_KEY"),
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Não foi possível excluir o atendimento. Verifique as informações digitadas.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "Atendimento excluído com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao excluir o atendimento. Tente novamente.",
                        }
                    ]

                # Adiciona os root_attributes
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="exclusões_atendimento_os",
                    item_element_name="exclusão",
                    root_attributes={
                        "atendimento": str(codigo_atendimento),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

    except Exception as e:
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "mensagem": f"Erro interno: {str(e)}. Tente novamente mais tarde.",
                }
            ],
            root_element_name="resultado",
            item_element_name="item",
            custom_attributes={"sistema": "SIGA"},
        )


@mcp.tool
async def inserir_atendimentos_os(
    codigo_os: int,
    data_inicio: str | Literal["hoje", "agora", "ontem"],
    codigo_analista: int,
    descricao_atendimento: str,
    tipo: Literal[
        "Suporte Sistema",
        "Implementação",
        "Manutenção Corretiva",
        "Reunião",
        "Treinamento",
        "Mudança de Escopo",
        "Anexo",
        "Suporte Infraestrutura",
        "Monitoramento",
        "Incidente",
        "Requisição",
    ] = "Implementação",
    data_fim: str | Literal["hoje", "agora", "ontem"] | None = None,
    tempo_gasto: int | None = None,
    primeiro_atendimento: bool = False,
    apresenta_solucao: bool = False,
) -> str:
    """Grava o atendimento OS aberto pelo usuario.

    Args:
        os (int): o número da OS
        data_inicio (str): a DATA E HORA inicial do atendimento os
        analista (int): a matricula do usuario / analista
        descricao (str): a descrição do atendimento os
        tipo (str): o tipo do atendimento os
        data_fim (str): a DATA E HORA final do atendimento os
        tempoGasto (int): o tempo gasto do atendimento os
        primeiroAtendimento (int): quando for o primeiro atendimento os
        apresentaSolucao (int): quando for apresentada a solução para o atendimento os

    Returns:
        str: um XML bem formatado indicando que o atendimento da os foi ou não inserido com sucesso.
    """

    if data_inicio:
        data_inicio = converter_data_siga(data_inicio, manter_horas=True)

    if data_fim:
        data_fim = converter_data_siga(data_fim, manter_horas=True)

    # Busca o tipo correto na constante TYPE_TO_NUMBER ignorando maiúsculas/minúsculas
    tipo_normalizado = next(
        # Expressão geradora que itera sobre todas as chaves do dicionário TYPE_TO_NUMBER
        (
            key
            for key in TYPE_TO_NUMBER.keys()
            # Compara a chave atual em minúsculas com o tipo recebido em minúsculas
            if str(key).lower() == str(tipo).lower()
        ),
        # Se nenhuma correspondência for encontrada, retorna None como valor padrão
        None,
    )

    # Verifica se foi encontrado um tipo válido após a busca case-insensitive
    if tipo_normalizado is None:
        # Retorna XML de erro em vez de levantar exceção
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "tipo_invalido",
                    "tipo_informado": tipo,
                    "mensagem": f"Tipo '{tipo}' não encontrado na constante TYPE_TO_NUMBER",
                    "tipos_validos": list(TYPE_TO_NUMBER.keys()),
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "inserir_atendimentos_os"},
            custom_attributes={"sistema": "SIGA"},
        )

    tipo_final = TYPE_TO_NUMBER[tipo_normalizado]

    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/atendimentosOs/inserirAtendimentosOsSigaIA/",
                json={
                    "os": codigo_os,
                    "dataIni": data_inicio,
                    "analista": codigo_analista,
                    "descricao": descricao_atendimento,
                    "tipo": tipo_final,
                    "dataFim": data_fim if data_fim else "",
                    "tempoGasto": tempo_gasto if tempo_gasto else "",
                    "primeiroAtendimento": primeiro_atendimento,
                    "apresentaSolucao": apresenta_solucao,
                    "apiKey": os.getenv("AVA_API_KEY"),
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Não foi possível salvar o atendimento. Verifique as informações digitadas.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "Atendimento cadastrado com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao gravar o atendimento. Tente novamente.",
                        }
                    ]

                # Adiciona os root_attributes
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="ordens_servico",
                    item_element_name="ordem_servico",
                    root_attributes={
                        "os": str(codigo_os),
                        "dataIni": str(data_inicio),
                        "analista": str(codigo_analista),
                        "descricao": str(descricao_atendimento),
                        "tipo": str(tipo_normalizado),
                        "dataFim": str(data_fim),
                        "tempoGasto": str(tempo_gasto),
                        "primeiroAtendimento": str(primeiro_atendimento),
                        "apresentaSolucao": str(apresenta_solucao),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

    except Exception as e:
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "mensagem": f"Erro interno: {str(e)}. Tente novamente mais tarde.",
                }
            ],
            root_element_name="resultado",
            item_element_name="item",
            custom_attributes={"sistema": "SIGA"},
        )


@mcp.tool
async def listar_atendimentos_avulsos(
    matricula: int,
    data_inicio: str | Literal["hoje", "ontem"],
    data_fim: str | Literal["hoje", "ontem"],
) -> str:
    """Lista os atendimentos avulsos abertos pelo usuario.

    Args:
        matricula (str | int): a matricula do usuario
        data_inicio (str): a data de início dos atendimentos
        data_fim(str): a data final dos atendimentos

    Returns:
        str: um XML bem formatado indicando os atendimentos.
    """
    if data_inicio:
        data_inicio = converter_data_siga(data_inicio)

    if data_fim:
        data_fim = converter_data_siga(data_fim)

    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/atendimentosAvulsos/buscarAtendimentosAvulsosSigaIA/",
            json={
                "matricula": matricula,
                "dataIni": data_inicio,
                "dataFim": data_fim,
                "apiKey": os.getenv("AVA_API_KEY"),
            },
        ) as response:
            try:
                json = await response.json(content_type=None)
                retorno = XMLBuilder().build_xml(
                    data=json["result"],
                    root_element_name="atendimentos_avulsos",
                    item_element_name="atendimentos_avulsos",
                    root_attributes={
                        "matricula": str(matricula),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception:
                return "Erro ao listar atendimentos avulsos."


@mcp.tool
async def listar_atendimentos_os(
    matricula: str | int,
    codigo_os: str | int | None = None,
    data_inicio: str | Literal["hoje", "ontem"] | None = None,
    data_fim: str | Literal["hoje", "ontem"] | None = None,
) -> str:
    """Lista os atendimentos de OS do usuario.

    Args:
        matricula (str | int): a matricula do usuario
        codigo_os (str | int | None): a Ordem de Serviço (OS) - opcional para buscar todas
        data_inicio (str): a data de inicio dos atendimentos
        data_fim (str): a data final dos atendimentos


    Returns:
        str: um XML bem formatado indicando os atendimentos das OS.
    """

    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/atendimentosOs/buscarAtendimentosOsSigaIA/",
            json={
                "matricula": str(matricula),
                "os": str(codigo_os) if codigo_os else "",
                "dataIni": converter_data_siga(data_inicio) if data_inicio else "",
                "dataFim": converter_data_siga(data_fim) if data_fim else "",
                "apiKey": os.getenv("AVA_API_KEY"),
            },
        ) as response:
            try:
                json = await response.json(content_type=None)
                retorno = XMLBuilder().build_xml(
                    data=json["result"],
                    root_element_name="atendimentos_os",
                    item_element_name="atendimentos_os",
                    root_attributes={
                        "matricula": str(matricula),
                        "os": str(codigo_os) if codigo_os else "",
                        "dataIni": str(data_inicio) if data_inicio else "",
                        "dataFim": str(data_fim) if data_fim else "",
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception:
                return "Erro ao listar atendimentos OS."


@mcp.tool
async def listar_horas_trabalhadas(
    matricula: str | int,
    data_inicio: str | Literal["hoje", "ontem"],
    data_fim: str | Literal["hoje", "ontem"],
) -> str:
    """Lista o cálculo das horas trabalhadas do analista, levando em consideração os atendimentos OS e os atendimentos avulsos do usuario (analista).

    Args:
        matricula (str | int): a matricula do usuario
        data_inicio (str): a data inicio
        data_fim(str): a data final

    Returns:
        str: um XML bem formatado indicando os atendimentos.
    """
    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/atendimentosAvulsos/buscarTotalHorasTrabalhadasSigaIA/",
            json={
                "matricula": matricula,
                "dataIni": converter_data_siga(data_inicio) if data_inicio else "",
                "dataFim": converter_data_siga(data_fim) if data_fim else "",
                "apiKey": os.getenv("AVA_API_KEY"),
            },
        ) as response:
            try:
                json = await response.json(content_type=None)
                resultado = json["result"]

                retorno = XMLBuilder().build_xml(
                    data=resultado,
                    root_element_name="atendimentos_avulsos",
                    item_element_name="atendimentos_avulsos",
                    root_attributes={
                        "matricula": str(matricula),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception:
                return "Erro ao listar horas trabalhadas."


def converter_data_siga(
    data_input: str | Literal["agora", "hoje", "ontem"],
    manter_horas: bool = False,
) -> str:
    """
    Converte uma string de data em linguagem natural para o formato DD/MM/YYYY ou DD/MM/YYYY HH:MM:SS.

    Suporta uma ampla gama de formatos incluindo:

    DATAS BÁSICAS:
    - Datas no formato DD/MM/YYYY, DD/MM/YYYY HH:MM:SS
    - Formatos ISO: YYYY-MM-DD, YYYY/MM/DD, YYYY-MM-DDTHH:MM, YYYY-MM-DDTHH:MM:SS
    - Formato americano: MM/DD/YYYY
    - Outros separadores: DD-MM-YYYY, DD.MM.YYYY
    - Datas curtas: DD/MM, MM/DD (assumindo ano atual)

    REFERÊNCIAS RELATIVAS:
    - 'hoje', 'ontem', 'amanhã', 'agora'
    - 'hoje-X' onde X são dias (ex: 'hoje-5')
    - 'hoje/ontem/amanhã HH:MM' com hora específica

    LINGUAGEM NATURAL AVANÇADA:
    - 'primeiro dia do mês', 'último dia do mês', 'meio do mês'
    - 'primeiro dia do mês passado', 'último dia do ano', 'início do ano'
    - 'mês passado', 'mês que vem', 'ano passado', 'ano que vem'
    - 'semana passada', 'semana que vem', 'próxima semana', 'semana retrasada'
    - 'daqui a X dias/semanas/meses/anos' (números e por extenso)
    - 'há X dias/semanas/meses/anos atrás' (números e por extenso)
    - Dias da semana: 'segunda-feira', 'terça que vem', 'sexta passada', '2ª feira'
    - Meses por nome: 'janeiro de 2025', 'dezembro passado', 'em março'
    - Expressões como 'início do mês', 'fim do ano', 'meio do mês'
    - Períodos: 'início da semana', 'meio da semana', 'fim da semana'
    - Trimestres: 'primeiro trimestre', 'último trimestre', 'trimestre passado'

    CASOS ESPECIAIS:
    - 'anteontem', 'depois de amanhã', 'outro dia'
    - 'esta semana', 'este mês', 'este ano', 'nesta segunda'
    - 'na próxima segunda', 'segunda passada', 'fim de semana'
    - Números ordinais: 'primeiro de janeiro', 'quinze de março'
    - Períodos do dia: 'hoje de manhã', 'ontem à noite', 'amanhã de tarde'
    - Expressões coloquiais: 'esses dias', 'recentemente', 'há pouco tempo'

    Args:
        data_input: String com a data a ser convertida
        manter_horas: Se True, mantém ou adiciona informações de hora

    Returns:
        String no formato DD/MM/YYYY ou DD/MM/YYYY HH:MM:SS

    Raises:
        ValueError: Se o formato da data for inválido ou não reconhecido
    """

    # Define a data de hoje como referência
    # Usar timezone local do Brasil se possível
    try:
        from zoneinfo import ZoneInfo

        hoje = datetime.now(ZoneInfo("America/Sao_Paulo")).replace(tzinfo=None)
    except ImportError:
        # Fallback para datetime normal se zoneinfo não disponível
        hoje = datetime.now()

    # Remove espaços extras e normaliza
    data_input = data_input.strip().lower()
    data_input = re.sub(r"\s+", " ", data_input)  # Remove espaços duplos

    # === CASOS ESPECIAIS PRIMEIRO ===

    # Caso especial: agora
    if data_input == "agora":
        if manter_horas:
            return hoje.strftime("%d/%m/%Y %H:%M:%S")
        else:
            return hoje.strftime("%d/%m/%Y")

    # === PROCESSAMENTO DE LINGUAGEM NATURAL ===
    try:
        # Tentar casos específicos em português primeiro
        resultado = _processar_linguagem_natural_pt(data_input, hoje, manter_horas)
        if resultado:
            return resultado
    except Exception:
        pass

    # === FALLBACK PARA CASOS ORIGINAIS ===
    try:
        return _processar_casos_originais(data_input, hoje, manter_horas)
    except Exception:
        pass

    # === ÚLTIMO RECURSO: DATEPARSER ===
    try:
        import dateparser

        # Usar dateparser com configurações básicas
        data_parseada = dateparser.parse(
            data_input,
            languages=["pt"],
            locales=["pt-BR"],
            settings={"RELATIVE_BASE": hoje},
        )

        if data_parseada:
            if manter_horas:
                return data_parseada.strftime("%d/%m/%Y %H:%M:%S")
            else:
                return data_parseada.strftime("%d/%m/%Y")

    except ImportError:
        # Se dateparser não estiver disponível, continua sem ele
        pass
    except Exception:
        pass

    # Se chegou até aqui, formato não reconhecido
    raise ValueError(f"Formato de data não reconhecido: {data_input}")


def _processar_linguagem_natural_pt(
    data_input: str, hoje: datetime, manter_horas: bool
) -> Optional[str]:
    """Processa expressões em linguagem natural em português."""

    # === CASOS ESPECIAIS PRIMEIRO (antes de processar meses/números) ===

    # Expressões coloquiais que podem conflitar com outras palavras
    if "outro dia" in data_input:
        # Alguns dias atrás (não uma data futura)
        data_resultado = hoje - timedelta(days=3)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    if any(
        termo in data_input
        for termo in ["esses dias", "recentemente", "ha pouco tempo", "há pouco tempo"]
    ):
        # Aproximadamente uma semana atrás
        data_resultado = hoje - timedelta(days=7)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )
    if data_input == "hoje":
        return hoje.strftime("%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y")

    if data_input == "ontem":
        ontem = hoje - timedelta(days=1)
        return ontem.strftime("%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y")

    if data_input in ["amanha", "amanhã"]:
        amanha = hoje + timedelta(days=1)
        return amanha.strftime("%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y")

    if data_input == "anteontem":
        anteontem = hoje - timedelta(days=2)
        return anteontem.strftime("%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y")

    if data_input in ["depois de amanha", "depois de amanhã"]:
        depois_amanha = hoje + timedelta(days=2)
        return depois_amanha.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    # === SEMANA RETRASADA ===
    if "semana retrasada" in data_input:
        data_resultado = hoje - timedelta(weeks=2)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    # === PERÍODOS DA SEMANA ===
    if "inicio da semana" in data_input or "início da semana" in data_input:
        # Segunda-feira desta semana
        dias_ate_segunda = -hoje.weekday()  # 0 = segunda
        if dias_ate_segunda > 0:  # Se já passou a segunda, próxima segunda
            dias_ate_segunda -= 7
        data_resultado = hoje + timedelta(days=dias_ate_segunda)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    if "meio da semana" in data_input:
        # Quarta-feira desta semana
        dias_ate_quarta = 2 - hoje.weekday()  # 2 = quarta
        if dias_ate_quarta < -2:  # Se já passou muito da quarta, próxima quarta
            dias_ate_quarta += 7
        data_resultado = hoje + timedelta(days=dias_ate_quarta)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    if any(
        termo in data_input
        for termo in [
            "fim da semana",
            "final da semana",
            "fim de semana",
            "fds",
            "fim desta semana",
            "final desta semana",
        ]
    ):
        # Sexta-feira desta semana ou próxima se já passou
        dias_ate_sexta = 4 - hoje.weekday()  # 4 = sexta
        if dias_ate_sexta < 0:  # Se já passou sexta, próxima sexta
            dias_ate_sexta += 7
        data_resultado = hoje + timedelta(days=dias_ate_sexta)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    # === EXPRESSÕES COM "ESTA/ESTE/DESTA/DESTE" ===
    if any(
        termo in data_input for termo in ["esta semana", "nesta semana", "desta semana"]
    ):
        return hoje.strftime("%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y")

    if any(
        termo in data_input
        for termo in [
            "este mes",
            "este mês",
            "neste mes",
            "neste mês",
            "deste mes",
            "deste mês",
        ]
    ):
        return hoje.strftime("%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y")

    if any(termo in data_input for termo in ["este ano", "neste ano", "deste ano"]):
        return hoje.strftime("%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y")

    # Variações com "desta" para períodos
    if any(
        termo in data_input for termo in ["inicio desta semana", "início desta semana"]
    ):
        dias_ate_segunda = -hoje.weekday()  # 0 = segunda
        if dias_ate_segunda > 0:  # Se já passou a segunda, próxima segunda
            dias_ate_segunda -= 7
        data_resultado = hoje + timedelta(days=dias_ate_segunda)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    if any(termo in data_input for termo in ["meio desta semana"]):
        dias_ate_quarta = 2 - hoje.weekday()  # 2 = quarta
        if dias_ate_quarta < -2:  # Se já passou muito da quarta, próxima quarta
            dias_ate_quarta += 7
        data_resultado = hoje + timedelta(days=dias_ate_quarta)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    # === CASOS BÁSICOS ===

    # === PERÍODOS DO DIA (verificar primeiro as expressões compostas) ===
    # Detectar frases como "hoje de manhã", "ontem à noite", etc.
    periodos_detectados = []
    for periodo in PERIODOS_DIA.keys():
        if periodo in data_input:
            periodos_detectados.append(periodo)

    # Ordenar por tamanho (mais específico primeiro)
    periodos_detectados.sort(key=len, reverse=True)

    if periodos_detectados:
        periodo = periodos_detectados[0]  # Pegar o mais específico
        hora_padrao = PERIODOS_DIA[periodo]

        # Extrair a referência de tempo (hoje, ontem, amanhã)
        if "hoje" in data_input:
            data_base = hoje
        elif "ontem" in data_input:
            data_base = hoje - timedelta(days=1)
        elif "amanha" in data_input or "amanhã" in data_input:
            data_base = hoje + timedelta(days=1)
        elif "anteontem" in data_input:
            data_base = hoje - timedelta(days=2)
        else:
            data_base = hoje  # Default para hoje

        try:
            data_resultado = data_base.replace(hour=hora_padrao, minute=0, second=0)
            return data_resultado.strftime(
                "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
            )
        except ValueError:
            pass

    # === TRIMESTRES ===
    if "primeiro trimestre" in data_input:
        if any(palavra in data_input for palavra in TEMPO_PASSADO):
            if hoje.month <= 3:  # Ainda no primeiro trimestre, pegar o do ano passado
                data_resultado = datetime(hoje.year - 1, 1, 1)
            else:
                data_resultado = datetime(hoje.year, 1, 1)
        else:
            data_resultado = datetime(hoje.year, 1, 1)

        return data_resultado.strftime(
            "%d/%m/%Y 00:00:00" if manter_horas else "%d/%m/%Y"
        )

    if "segundo trimestre" in data_input:
        ano = hoje.year
        if any(palavra in data_input for palavra in TEMPO_PASSADO) and hoje.month <= 6:
            ano -= 1
        data_resultado = datetime(ano, 4, 1)
        return data_resultado.strftime(
            "%d/%m/%Y 00:00:00" if manter_horas else "%d/%m/%Y"
        )

    if "terceiro trimestre" in data_input:
        ano = hoje.year
        if any(palavra in data_input for palavra in TEMPO_PASSADO) and hoje.month <= 9:
            ano -= 1
        data_resultado = datetime(ano, 7, 1)
        return data_resultado.strftime(
            "%d/%m/%Y 00:00:00" if manter_horas else "%d/%m/%Y"
        )

    if any(
        termo in data_input
        for termo in ["quarto trimestre", "último trimestre", "ultimo trimestre"]
    ):
        ano = hoje.year
        if any(palavra in data_input for palavra in TEMPO_PASSADO) and hoje.month <= 12:
            ano -= 1
        data_resultado = datetime(ano, 10, 1)
        return data_resultado.strftime(
            "%d/%m/%Y 00:00:00" if manter_horas else "%d/%m/%Y"
        )

    if "trimestre passado" in data_input:
        if hoje.month <= 3:
            data_resultado = datetime(hoje.year - 1, 10, 1)  # Q4 do ano anterior
        elif hoje.month <= 6:
            data_resultado = datetime(hoje.year, 1, 1)  # Q1 deste ano
        elif hoje.month <= 9:
            data_resultado = datetime(hoje.year, 4, 1)  # Q2 deste ano
        else:
            data_resultado = datetime(hoje.year, 7, 1)  # Q3 deste ano

        return data_resultado.strftime(
            "%d/%m/%Y 00:00:00" if manter_horas else "%d/%m/%Y"
        )

    # === HOJE/ONTEM/AMANHÃ COM HORA ===
    for palavra in ["hoje", "ontem", "amanha", "amanhã"]:
        padrao = re.match(rf"{palavra}\s+(\d{{1,2}}):(\d{{1,2}})", data_input)
        if padrao:
            hora, minuto = padrao.groups()
            try:
                if palavra == "hoje":
                    data_resultado = hoje
                elif palavra == "ontem":
                    data_resultado = hoje - timedelta(days=1)
                else:  # amanhã
                    data_resultado = hoje + timedelta(days=1)

                data_resultado = data_resultado.replace(
                    hour=int(hora), minute=int(minuto), second=0
                )
                return data_resultado.strftime(
                    "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
                )
            except ValueError:
                continue

    # === HOJE-X ===
    padrao_hoje_menos = re.match(r"hoje-(\d+)(?:\s+(\d{1,2}):(\d{1,2}))?", data_input)
    if padrao_hoje_menos:
        dias_subtrair = int(padrao_hoje_menos.group(1))
        hora = padrao_hoje_menos.group(2)
        minuto = padrao_hoje_menos.group(3)

        data_resultado = hoje - timedelta(days=dias_subtrair)

        if hora and minuto:
            try:
                data_resultado = data_resultado.replace(
                    hour=int(hora), minute=int(minuto), second=0
                )
            except ValueError:
                pass

        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    # === EXPRESSÕES COM "DAQUI A" ===
    padrao_daqui = re.match(
        r"daqui\s+a?\s*(\d+)\s*(dia|dias|semana|semanas|mes|mês|meses|ano|anos)",
        data_input,
    )
    if padrao_daqui:
        quantidade = int(padrao_daqui.group(1))
        unidade = padrao_daqui.group(2)

        if unidade in ["dia", "dias"]:
            data_resultado = hoje + timedelta(days=quantidade)
        elif unidade in ["semana", "semanas"]:
            data_resultado = hoje + timedelta(weeks=quantidade)
        elif unidade in ["mes", "mês", "meses"]:
            # Aproximação: assumir 30 dias por mês
            data_resultado = hoje + timedelta(days=quantidade * 30)
        elif unidade in ["ano", "anos"]:
            # Aproximação: assumir 365 dias por ano
            data_resultado = hoje + timedelta(days=quantidade * 365)
        else:
            raise ValueError("Data inválida")

        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    # === EXPRESSÕES COM "HÁ" ===
    padrao_ha = re.match(
        r"h[aá]\s+(\d+)\s*(dia|dias|semana|semanas|mes|mês|meses|ano|anos)(\s+atr[aá]s)?",
        data_input,
    )
    if padrao_ha:
        quantidade = int(padrao_ha.group(1))
        unidade = padrao_ha.group(2)

        if unidade in ["dia", "dias"]:
            data_resultado = hoje - timedelta(days=quantidade)
        elif unidade in ["semana", "semanas"]:
            data_resultado = hoje - timedelta(weeks=quantidade)
        elif unidade in ["mes", "mês", "meses"]:
            data_resultado = hoje - timedelta(days=quantidade * 30)
        elif unidade in ["ano", "anos"]:
            data_resultado = hoje - timedelta(days=quantidade * 365)
        else:
            raise ValueError("Data inválida")

        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    # === ÚLTIMO/PRIMEIRO DIA DO ANO ===
    if "ultimo dia do ano" in data_input or "último dia do ano" in data_input:
        if any(palavra in data_input for palavra in TEMPO_PASSADO):
            data_resultado = datetime(hoje.year - 1, 12, 31)
        elif any(palavra in data_input for palavra in TEMPO_FUTURO):
            data_resultado = datetime(hoje.year + 1, 12, 31)
        else:
            data_resultado = datetime(hoje.year, 12, 31)

        return data_resultado.strftime(
            "%d/%m/%Y 23:59:59" if manter_horas else "%d/%m/%Y"
        )

    if (
        "primeiro dia do ano" in data_input
        or "inicio do ano" in data_input
        or "início do ano" in data_input
    ):
        if any(palavra in data_input for palavra in TEMPO_PASSADO):
            data_resultado = datetime(hoje.year - 1, 1, 1)
        elif any(palavra in data_input for palavra in TEMPO_FUTURO):
            data_resultado = datetime(hoje.year + 1, 1, 1)
        else:
            data_resultado = datetime(hoje.year, 1, 1)

        return data_resultado.strftime(
            "%d/%m/%Y 00:00:00" if manter_horas else "%d/%m/%Y"
        )

    # === MEIO DO MÊS ===
    if "meio do mes" in data_input or "meio do mês" in data_input:
        if any(palavra in data_input for palavra in TEMPO_PASSADO):
            if hoje.month == 1:
                data_resultado = datetime(hoje.year - 1, 12, 15)
            else:
                data_resultado = datetime(hoje.year, hoje.month - 1, 15)
        elif any(palavra in data_input for palavra in TEMPO_FUTURO):
            if hoje.month == 12:
                data_resultado = datetime(hoje.year + 1, 1, 15)
            else:
                data_resultado = datetime(hoje.year, hoje.month + 1, 15)
        else:
            data_resultado = datetime(hoje.year, hoje.month, 15)

        return data_resultado.strftime(
            "%d/%m/%Y 12:00:00" if manter_horas else "%d/%m/%Y"
        )

    # === INÍCIO/FIM DO MÊS ===
    if "inicio do mes" in data_input or "início do mês" in data_input:
        return _processar_linguagem_natural_pt(
            "primeiro dia do mês"
            + (
                " passado"
                if any(p in data_input for p in TEMPO_PASSADO)
                else " que vem"
                if any(p in data_input for p in TEMPO_FUTURO)
                else ""
            ),
            hoje,
            manter_horas,
        )

    if "fim do mes" in data_input or "fim do mês" in data_input:
        return _processar_linguagem_natural_pt(
            "último dia do mês"
            + (
                " passado"
                if any(p in data_input for p in TEMPO_PASSADO)
                else " que vem"
                if any(p in data_input for p in TEMPO_FUTURO)
                else ""
            ),
            hoje,
            manter_horas,
        )

    # === NÚMEROS POR EXTENSO ===
    for numero_str, numero_val in NUMEROS_EXTENSO.items():
        # "dois dias atrás", "três semanas", etc.
        padrao_extenso = re.search(
            rf"{numero_str}\s+(dia|dias|semana|semanas|mes|mês|meses|ano|anos)(?:\s+atr[aá]s)?",
            data_input,
        )
        if padrao_extenso:
            unidade = padrao_extenso.group(1)

            # Determinar se é passado ou futuro
            eh_passado = (
                "atrás" in data_input
                or "atras" in data_input
                or any(p in data_input for p in TEMPO_PASSADO)
            )

            delta = None
            if unidade in ["dia", "dias"]:
                delta = timedelta(days=numero_val)
            elif unidade in ["semana", "semanas"]:
                delta = timedelta(weeks=numero_val)
            elif unidade in ["mes", "mês", "meses"]:
                delta = timedelta(days=numero_val * 30)
            elif unidade in ["ano", "anos"]:
                delta = timedelta(days=numero_val * 365)

            if delta is not None:
                if eh_passado:
                    data_resultado = hoje - delta
                else:
                    data_resultado = hoje + delta

                return data_resultado.strftime(
                    "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
                )
    if "primeiro dia do mes" in data_input or "primeiro dia do mês" in data_input:
        if any(palavra in data_input for palavra in TEMPO_PASSADO):
            # Mês passado
            if hoje.month == 1:
                data_resultado = datetime(hoje.year - 1, 12, 1)
            else:
                data_resultado = datetime(hoje.year, hoje.month - 1, 1)
        elif any(palavra in data_input for palavra in TEMPO_FUTURO):
            # Próximo mês
            if hoje.month == 12:
                data_resultado = datetime(hoje.year + 1, 1, 1)
            else:
                data_resultado = datetime(hoje.year, hoje.month + 1, 1)
        else:
            # Mês atual
            data_resultado = datetime(hoje.year, hoje.month, 1)

        return data_resultado.strftime(
            "%d/%m/%Y 00:00:00" if manter_horas else "%d/%m/%Y"
        )

    if "ultimo dia do mes" in data_input or "último dia do mês" in data_input:
        if any(palavra in data_input for palavra in TEMPO_PASSADO):
            # Mês passado
            if hoje.month == 1:
                ultimo_dia = calendar.monthrange(hoje.year - 1, 12)[1]
                data_resultado = datetime(hoje.year - 1, 12, ultimo_dia)
            else:
                ultimo_dia = calendar.monthrange(hoje.year, hoje.month - 1)[1]
                data_resultado = datetime(hoje.year, hoje.month - 1, ultimo_dia)
        elif any(palavra in data_input for palavra in TEMPO_FUTURO):
            # Próximo mês
            if hoje.month == 12:
                ultimo_dia = calendar.monthrange(hoje.year + 1, 1)[1]
                data_resultado = datetime(hoje.year + 1, 1, ultimo_dia)
            else:
                ultimo_dia = calendar.monthrange(hoje.year, hoje.month + 1)[1]
                data_resultado = datetime(hoje.year, hoje.month + 1, ultimo_dia)
        else:
            # Mês atual
            ultimo_dia = calendar.monthrange(hoje.year, hoje.month)[1]
            data_resultado = datetime(hoje.year, hoje.month, ultimo_dia)

        return data_resultado.strftime(
            "%d/%m/%Y 23:59:59" if manter_horas else "%d/%m/%Y"
        )

    # === MÊS PASSADO/PRÓXIMO ===
    if "mes passado" in data_input or "mês passado" in data_input:
        if hoje.month == 1:
            data_resultado = datetime(hoje.year - 1, 12, hoje.day)
        else:
            # Ajustar o dia se necessário
            try:
                data_resultado = datetime(hoje.year, hoje.month - 1, hoje.day)
            except ValueError:
                # Dia não existe no mês anterior (ex: 31 para fevereiro)
                ultimo_dia = calendar.monthrange(hoje.year, hoje.month - 1)[1]
                data_resultado = datetime(hoje.year, hoje.month - 1, ultimo_dia)

        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    if any(
        termo in data_input
        for termo in ["mes que vem", "mês que vem", "proximo mes", "próximo mês"]
    ):
        if hoje.month == 12:
            data_resultado = datetime(hoje.year + 1, 1, hoje.day)
        else:
            try:
                data_resultado = datetime(hoje.year, hoje.month + 1, hoje.day)
            except ValueError:
                ultimo_dia = calendar.monthrange(hoje.year, hoje.month + 1)[1]
                data_resultado = datetime(hoje.year, hoje.month + 1, ultimo_dia)

        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    # === SEMANA PASSADA/PRÓXIMA ===
    if "semana passada" in data_input:
        data_resultado = hoje - timedelta(weeks=1)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    if any(
        termo in data_input
        for termo in ["semana que vem", "proxima semana", "próxima semana"]
    ):
        data_resultado = hoje + timedelta(weeks=1)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    # === DIAS DA SEMANA COM VARIAÇÕES ===
    # Mapeamento adicional para abreviações numéricas
    dias_numericos = {
        "2ª feira": 0,
        "2a feira": 0,
        "2 feira": 0,
        "3ª feira": 1,
        "3a feira": 1,
        "3 feira": 1,
        "4ª feira": 2,
        "4a feira": 2,
        "4 feira": 2,
        "5ª feira": 3,
        "5a feira": 3,
        "5 feira": 3,
        "6ª feira": 4,
        "6a feira": 4,
        "6 feira": 4,
        "sab": 5,
        "sabado": 5,
        "dom": 6,
    }

    # Combinar ambos os dicionários
    todos_dias = {**DIAS_SEMANA_PT, **dias_numericos}

    # === DIAS DA SEMANA ===
    for dia_nome, dia_num in todos_dias.items():
        if dia_nome in data_input:
            dias_ate_dia = (dia_num - hoje.weekday()) % 7

            # Determinar se é passado ou futuro
            if any(palavra in data_input for palavra in TEMPO_PASSADO + ["passada"]):
                if dias_ate_dia == 0:
                    dias_ate_dia = -7  # Semana passada
                else:
                    dias_ate_dia = dias_ate_dia - 7
            elif any(
                palavra in data_input
                for palavra in TEMPO_FUTURO + ["que vem", "proxima", "próxima"]
            ):
                if dias_ate_dia == 0:
                    dias_ate_dia = 7  # Próxima semana
            elif any(
                termo in data_input
                for termo in ["na proxima", "na próxima", "nesta", "na", "no"]
            ):
                if dias_ate_dia == 0:
                    dias_ate_dia = 7  # Próxima ocorrência
            else:
                # Se for hoje, manter hoje; senão, assumir próxima ocorrência
                if dias_ate_dia == 0 and dia_nome not in data_input:
                    dias_ate_dia = 7

            data_resultado = hoje + timedelta(days=dias_ate_dia)
            return data_resultado.strftime(
                "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
            )

    # === EXPRESSÕES COM "EM" ===
    if data_input.startswith("em "):
        resto = data_input[3:]  # Remove "em "

        # "em janeiro", "em dezembro"
        for mes_nome, mes_num in MESES_PT.items():
            if resto == mes_nome or resto.startswith(mes_nome + " "):
                # Extrair ano se presente
                padrao_ano = re.search(r"(\d{4})", resto)
                ano = int(padrao_ano.group(1)) if padrao_ano else hoje.year

                # Se é um mês futuro neste ano ou igual ao atual, usar este ano
                # Se é um mês passado, pode ser que se refira ao próximo ano
                if mes_num < hoje.month and not padrao_ano:
                    ano = hoje.year + 1

                try:
                    data_resultado = datetime(ano, mes_num, 1)
                    return data_resultado.strftime(
                        "%d/%m/%Y 00:00:00" if manter_horas else "%d/%m/%Y"
                    )
                except ValueError:
                    continue

        # "em 2025", "em 2024"
        padrao_ano_so = re.match(r"(\d{4})$", resto)
        if padrao_ano_so:
            ano = int(padrao_ano_so.group(1))
            data_resultado = datetime(ano, 1, 1)
            return data_resultado.strftime(
                "%d/%m/%Y 00:00:00" if manter_horas else "%d/%m/%Y"
            )

    # === TRATAMENTO DE ERROS COMUNS DE DIGITAÇÃO ===
    # Normalizar acentos e espaços comuns
    data_normalizada = data_input
    data_normalizada = data_normalizada.replace("terca", "terça")
    data_normalizada = data_normalizada.replace("proximo", "próximo")
    data_normalizada = data_normalizada.replace("mes", "mês")
    data_normalizada = data_normalizada.replace("apos", "após")
    data_normalizada = data_normalizada.replace("tres", "três")

    # Se normalizou algo, tentar novamente
    if data_normalizada != data_input:
        try:
            return _processar_linguagem_natural_pt(data_normalizada, hoje, manter_horas)
        except Exception:
            pass

    # === CASOS COMPOSTOS MAIS COMPLEXOS ===
    # "segunda da semana que vem"
    if (
        "da semana que vem" in data_input
        or "da proxima semana" in data_input
        or "da próxima semana" in data_input
    ):
        for dia_nome, dia_num in todos_dias.items():
            if dia_nome in data_input:
                # Próxima semana + dia específico
                proxima_semana = hoje + timedelta(weeks=1)
                inicio_semana = proxima_semana - timedelta(
                    days=proxima_semana.weekday()
                )
                data_resultado = inicio_semana + timedelta(days=dia_num)
                return data_resultado.strftime(
                    "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
                )

    # "sexta da semana passada"
    if "da semana passada" in data_input:
        for dia_nome, dia_num in todos_dias.items():
            if dia_nome in data_input:
                # Semana passada + dia específico
                semana_passada = hoje - timedelta(weeks=1)
                inicio_semana = semana_passada - timedelta(
                    days=semana_passada.weekday()
                )
                data_resultado = inicio_semana + timedelta(days=dia_num)
                return data_resultado.strftime(
                    "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
                )

    # === EXPRESSÕES COM NÚMEROS ORDINAIS MAIS EXTENSOS ===
    ordinais = {
        "primeiro": 1,
        "segunda": 2,
        "terceiro": 3,
        "quarto": 4,
        "quinto": 5,
        "sexto": 6,
        "sétimo": 7,
        "setimo": 7,
        "oitavo": 8,
        "nono": 9,
        "décimo": 10,
        "decimo": 10,
        "vigésimo": 20,
        "vigesimo": 20,
        "trigésimo": 30,
        "trigesimo": 30,
    }

    for ordinal, numero in ordinais.items():
        padrao_ordinal = re.search(
            rf"{ordinal}(?:\s+primeiro)?\s+de\s+(\w+)", data_input
        )
        if padrao_ordinal:
            mes_nome = padrao_ordinal.group(1)
            if mes_nome in MESES_PT:
                try:
                    data_resultado = datetime(hoje.year, MESES_PT[mes_nome], numero)
                    return data_resultado.strftime(
                        "%d/%m/%Y 00:00:00" if manter_horas else "%d/%m/%Y"
                    )
                except ValueError:
                    continue
    for dia_nome, dia_num in DIAS_SEMANA_PT.items():
        if dia_nome in data_input:
            dias_ate_dia = (dia_num - hoje.weekday()) % 7

            # Determinar se é passado ou futuro
            if any(palavra in data_input for palavra in TEMPO_PASSADO):
                if dias_ate_dia == 0:
                    dias_ate_dia = -7  # Semana passada
                else:
                    dias_ate_dia = dias_ate_dia - 7
            elif any(palavra in data_input for palavra in TEMPO_FUTURO + ["que vem"]):
                if dias_ate_dia == 0:
                    dias_ate_dia = 7  # Próxima semana
            else:
                # Se for hoje, manter hoje; senão, assumir próxima ocorrência
                if dias_ate_dia == 0 and dia_nome not in data_input:
                    dias_ate_dia = 7

            data_resultado = hoje + timedelta(days=dias_ate_dia)
            return data_resultado.strftime(
                "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
            )

    # === ANO PASSADO/PRÓXIMO ===
    if "ano passado" in data_input:
        data_resultado = datetime(hoje.year - 1, hoje.month, hoje.day)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    if any(
        termo in data_input for termo in ["ano que vem", "proximo ano", "próximo ano"]
    ):
        data_resultado = datetime(hoje.year + 1, hoje.month, hoje.day)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    # === MESES POR NOME ===
    for mes_nome, mes_num in MESES_PT.items():
        if mes_nome in data_input:
            # Extrair ano se presente
            padrao_ano = re.search(r"(\d{4})", data_input)
            ano = int(padrao_ano.group(1)) if padrao_ano else hoje.year

            # Extrair dia se presente
            padrao_dia = re.search(r"(\d{1,2})(?:\s+de\s+)?" + mes_nome, data_input)
            dia = int(padrao_dia.group(1)) if padrao_dia else 1

            # Verificar se é passado ou futuro
            if (
                any(palavra in data_input for palavra in TEMPO_PASSADO)
                and not padrao_ano
            ):
                if mes_num > hoje.month:
                    ano = hoje.year - 1
                elif mes_num == hoje.month and dia <= hoje.day:
                    ano = hoje.year - 1
            elif (
                any(palavra in data_input for palavra in TEMPO_FUTURO)
                and not padrao_ano
            ):
                if mes_num < hoje.month:
                    ano = hoje.year + 1
                elif mes_num == hoje.month and dia <= hoje.day:
                    ano = hoje.year + 1

            try:
                data_resultado = datetime(ano, mes_num, dia)
                return data_resultado.strftime(
                    "%d/%m/%Y 00:00:00" if manter_horas else "%d/%m/%Y"
                )
            except ValueError:
                continue

    return None


def _processar_casos_originais(
    data_input: str, hoje: datetime, manter_horas: bool
) -> str:
    """Processa os casos da função original."""

    # Caso especial: Formato ISO 8601 com T: YYYY-MM-DDTHH:MM:SS ou YYYY-MM-DDTHH:MM
    padrao_iso_t = re.match(
        r"(\d{4})-(\d{1,2})-(\d{1,2})t(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?", data_input
    )
    if padrao_iso_t:
        ano, mes, dia, hora, minuto, segundo = padrao_iso_t.groups()
        segundo = segundo or "00"

        try:
            data_validada = datetime(
                int(ano), int(mes), int(dia), int(hora), int(minuto), int(segundo)
            )
            if manter_horas:
                return data_validada.strftime("%d/%m/%Y %H:%M:%S")
            else:
                return data_validada.strftime("%d/%m/%Y")
        except ValueError:
            raise ValueError(f"Data/hora inválida: {data_input}")

    # Caso 4: Data com horas no formato DD/MM/YYYY HH:MM:SS ou DD/MM/YYYY HH:MM
    padrao_data_com_horas = re.match(
        r"(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?", data_input
    )
    if padrao_data_com_horas:
        dia, mes, ano, hora, minuto, segundo = padrao_data_com_horas.groups()
        segundo = segundo or "00"

        try:
            data_validada = datetime(
                int(ano), int(mes), int(dia), int(hora), int(minuto), int(segundo)
            )
            if manter_horas:
                return data_validada.strftime("%d/%m/%Y %H:%M:%S")
            else:
                return data_validada.strftime("%d/%m/%Y")
        except ValueError:
            raise ValueError(f"Data/hora inválida: {data_input}")

    # Caso 5: Formato ISO com hora: YYYY-MM-DD HH:MM:SS ou YYYY-MM-DD HH:MM
    padrao_iso_com_horas = re.match(
        r"(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?", data_input
    )
    if padrao_iso_com_horas:
        ano, mes, dia, hora, minuto, segundo = padrao_iso_com_horas.groups()
        segundo = segundo or "00"

        try:
            data_validada = datetime(
                int(ano), int(mes), int(dia), int(hora), int(minuto), int(segundo)
            )
            if manter_horas:
                return data_validada.strftime("%d/%m/%Y %H:%M:%S")
            else:
                return data_validada.strftime("%d/%m/%Y")
        except ValueError:
            raise ValueError(f"Data/hora inválida: {data_input}")

    # Caso 6: Formato ISO: YYYY-MM-DD
    padrao_iso = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})$", data_input)
    if padrao_iso:
        ano, mes, dia = padrao_iso.groups()
        try:
            data_validada = datetime(int(ano), int(mes), int(dia))
            if manter_horas:
                return data_validada.strftime("%d/%m/%Y 00:00:00")
            else:
                return data_validada.strftime("%d/%m/%Y")
        except ValueError:
            raise ValueError(f"Data inválida: {data_input}")

    # Caso 7: Formato YYYY/MM/DD
    padrao_ano_primeiro_barra = re.match(r"(\d{4})/(\d{1,2})/(\d{1,2})$", data_input)
    if padrao_ano_primeiro_barra:
        ano, mes, dia = padrao_ano_primeiro_barra.groups()
        try:
            data_validada = datetime(int(ano), int(mes), int(dia))
            if manter_horas:
                return data_validada.strftime("%d/%m/%Y 00:00:00")
            else:
                return data_validada.strftime("%d/%m/%Y")
        except ValueError:
            raise ValueError(f"Data inválida: {data_input}")

    # Caso 8: Formato DD-MM-YYYY
    padrao_traco = re.match(r"(\d{1,2})-(\d{1,2})-(\d{4})$", data_input)
    if padrao_traco:
        dia, mes, ano = padrao_traco.groups()
        try:
            data_validada = datetime(int(ano), int(mes), int(dia))
            if manter_horas:
                return data_validada.strftime("%d/%m/%Y 00:00:00")
            else:
                return data_validada.strftime("%d/%m/%Y")
        except ValueError:
            raise ValueError(f"Data inválida: {data_input}")

    # Caso 9: Formato DD.MM.YYYY
    padrao_ponto = re.match(r"(\d{1,2})\.(\d{1,2})\.(\d{4})$", data_input)
    if padrao_ponto:
        dia, mes, ano = padrao_ponto.groups()
        try:
            data_validada = datetime(int(ano), int(mes), int(dia))
            if manter_horas:
                return data_validada.strftime("%d/%m/%Y 00:00:00")
            else:
                return data_validada.strftime("%d/%m/%Y")
        except ValueError:
            raise ValueError(f"Data inválida: {data_input}")

    # Caso 10: Formato americano MM/DD/YYYY (com validação para distinguir de DD/MM/YYYY)
    padrao_americano = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})$", data_input)
    if padrao_americano:
        parte1, parte2, ano = padrao_americano.groups()

        # Tenta interpretar como DD/MM/YYYY primeiro (formato brasileiro padrão)
        try:
            data_validada = datetime(int(ano), int(parte2), int(parte1))  # DD/MM/YYYY
            if manter_horas:
                return data_validada.strftime("%d/%m/%Y 00:00:00")
            else:
                return data_validada.strftime("%d/%m/%Y")
        except ValueError:
            # Se falhar, tenta como MM/DD/YYYY (formato americano)
            try:
                data_validada = datetime(
                    int(ano), int(parte1), int(parte2)
                )  # MM/DD/YYYY
                if manter_horas:
                    return data_validada.strftime("%d/%m/%Y 00:00:00")
                else:
                    return data_validada.strftime("%d/%m/%Y")
            except ValueError:
                raise ValueError(f"Data inválida: {data_input}")

    # Caso 11: Formato curto DD/MM (assumindo ano atual)
    padrao_data_curta = re.match(r"(\d{1,2})/(\d{1,2})$", data_input)
    if padrao_data_curta:
        parte1, parte2 = padrao_data_curta.groups()

        # Tenta DD/MM primeiro
        try:
            data_validada = datetime(hoje.year, int(parte2), int(parte1))
            if manter_horas:
                return data_validada.strftime("%d/%m/%Y 00:00:00")
            else:
                return data_validada.strftime("%d/%m/%Y")
        except ValueError:
            # Se falhar, tenta MM/DD
            try:
                data_validada = datetime(hoje.year, int(parte1), int(parte2))
                if manter_horas:
                    return data_validada.strftime("%d/%m/%Y 00:00:00")
                else:
                    return data_validada.strftime("%d/%m/%Y")
            except ValueError:
                raise ValueError(f"Data inválida: {data_input}")

    # Caso 12: Formato curto DD-MM ou MM-DD
    padrao_curto_traco = re.match(r"(\d{1,2})-(\d{1,2})$", data_input)
    if padrao_curto_traco:
        parte1, parte2 = padrao_curto_traco.groups()

        # Tenta DD-MM primeiro
        try:
            data_validada = datetime(hoje.year, int(parte2), int(parte1))
            if manter_horas:
                return data_validada.strftime("%d/%m/%Y 00:00:00")
            else:
                return data_validada.strftime("%d/%m/%Y")
        except ValueError:
            # Se falhar, tenta MM-DD
            try:
                data_validada = datetime(hoje.year, int(parte1), int(parte2))
                if manter_horas:
                    return data_validada.strftime("%d/%m/%Y 00:00:00")
                else:
                    return data_validada.strftime("%d/%m/%Y")
            except ValueError:
                raise ValueError(f"Data inválida: {data_input}")

    # Se chegou até aqui, lança exceção
    raise ValueError(
        f"Formato de data não reconhecido nos casos originais: {data_input}"
    )


def main():
    mcp.run(transport=os.getenv("MCP_TRANSPORT"))

if __name__ == "__main__":
    main()