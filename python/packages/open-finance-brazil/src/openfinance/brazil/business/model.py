from __future__ import annotations

from enum import Enum
from typing import NamedTuple, Annotated, Optional

from pydantic import BaseModel, Field, StringConstraints


class FieldUri(NamedTuple):
    x: Optional[list[str]] = None
    json: Optional[list[str]] = None
    csv: Optional[list[str]] = None


MoneyString = Annotated[str, StringConstraints(pattern=r"^(\d{1,9}\.\d{2}){1}$")]
CurrencyCode = Annotated[str, StringConstraints(pattern=r"^(\w{3}){1}$")]
RateString = Annotated[str, StringConstraints(pattern=r"^\d{1}\.\d{6}$")]
CnpjString = Annotated[str, StringConstraints(pattern=r"^\d{14}$")]
SizedText = Annotated[str, StringConstraints(pattern=r"^\S(?:.*\S)?$")]
EventQuantity = Annotated[str, StringConstraints(pattern=r"^(\d{1,6}){1}$")]


__doc__ = """
Fonte: /brazil/data-dictionary/contas/getBusinessAccounts_v1.csv
"""


class BusinessAccountType(str, Enum):
    CONTA_DEPOSITO_A_VISTA = "CONTA_DEPOSITO_A_VISTA"
    CONTA_POUPANCA = "CONTA_POUPANCA"
    CONTA_PAGAMENTO_PRE_PAGA = "CONTA_PAGAMENTO_PRE_PAGA"


class PriceInterval(str, Enum):
    FAIXA_1 = "1_FAIXA"
    FAIXA_2 = "2_FAIXA"
    FAIXA_3 = "3_FAIXA"
    FAIXA_4 = "4_FAIXA"


class OpeningClosingChannel(str, Enum):
    DEPENDENCIAS_PROPRIAS = "DEPENDENCIAS_PROPRIAS"
    CORRESPONDENTES_BANCARIOS = "CORRESPONDENTES_BANCARIOS"
    INTERNET_BANKING = "INTERNET_BANKING"
    MOBILE_BANKING = "MOBILE_BANKING"
    CENTRAL_TELEFONICA = "CENTRAL_TELEFONICA"
    CHAT = "CHAT"
    OUTROS = "OUTROS"


class TransactionMethod(str, Enum):
    MOVIMENTACAO_ELETRONICA = "MOVIMENTACAO_ELETRONICA"
    MOVIMENTACAO_CHEQUE = "MOVIMENTACAO_CHEQUE"
    MOVIMENTACAO_CARTAO = "MOVIMENTACAO_CARTAO"
    MOVIMENTACAO_PRESENCIAL = "MOVIMENTACAO_PRESENCIAL"


class Participant(BaseModel):
    brand: SizedText = Field(
        ...,
        uri=FieldUri(
            xpath=["/data/participant/brand"],
            jsonpath=["$data.participant.brand"],
            csv=["./_data/getBusinessAccounts_v1.csv:4"],
        ),
        max_length=80,
        description="Nome da Marca reportada pelo participante do Open Finance. "
                    "O conceito a que se refere a 'marca' é em essência uma promessa da empresa "
                    "em fornecer uma série específica de atributos, benefícios e serviços "
                    "uniformes aos clientes",
    )
    name: SizedText = Field(
        ...,
        json_path=["/data/participant/name"], # CSV L5
        max_length=80,
        description="Nome da Instituição, pertencente à marca, responsável pela modalidade de "
                    "Empréstimos. p.ex.'Empresa da Organização A'",
    )
    cnpjNumber: CnpjString = Field(
        ..., 
        json_path=["/data/participant/cnpjNumber"], # CSV L6
        description="CNPJ",
    )
    urlComplementaryList: Optional[SizedText] = Field(
        json_path=["/data/participant/urlComplementaryList"], # CSV L7
        default=None,
        max_length=1024,
        description="URL do link que conterá a lista complementar com os nomes e CNPJs agrupados sob o mesmo cnpjNumber. Os contidos nessa lista possuem as mesmas características para produtos e serviços. Endereço eletrônico de acesso ao canal. Será obrigatoriamente preenchido se houver lista complementar com os nomes e CNPJs a ser disponibilizada.\nRestrição: Será obrigatorimente preenchido se houver lista complementar com os nomes e CNPJs a ser disponibilizada",
    )


class Customers(BaseModel):
    rate: RateString = Field(
        ...,
        json_path=[
            "/data/fees/services/prices/customers/rate", # CSV L19
            "/data/serviceBundles/prices/customers/rate", # CSV L38
        ], 
        max_length=8,
        description="Percentual de clientes em cada faixa.",
    )


class PriceDistribution(BaseModel):
    # CSV L15/L34: */prices/interval
    interval: PriceInterval = Field(
        ...,
        json_path=[
            "/data/fees/services/prices/interval", # CSV L15
            "/data/serviceBundles/prices/interval", # CSV L34
        ],
        description="Segundo Normativa nº 32, BCB, de 2020: Distribuição de frequência relativa "
                    "dos valores de tarifas cobradas dos clientes, de que trata o § 2º do art. 3º "
                    "da Circular nº 4.015, de 2020, deve dar-se com base em quatro faixas de igual "
                    "tamanho, com explicitação dos valores sobre a mediana em cada uma dessas "
                    "faixas. Informando: 1ª faixa, 2ª faixa, 3ª faixa e 4ª faixa",
    )
    value: MoneyString = Field(
        ...,
        json_path=[
            "/data/fees/services/prices/value", # CSV L16
            "/data/serviceBundles/prices/value", # CSV L35
        ],
        max_length=12,
        description="Valor da mediana de cada faixa relativa ao serviço ofertado, informado no "
                    "período, conforme Res nº 32 BCB, 2020. "
                    "p.ex. '45.00' \n(representa um valor monetário. "
                    "p.ex: 1547368.92. Este valor, considerando que a moeda seja BRL, "
                    "significa R$ 1.547.368,92. "
                    "\nO único separador presente deve ser o '.' (ponto) para indicar a "
                    "casa decimal. Não deve haver separador de milhar)."
                    "\n\nObservação: Para efeito de comparação de taxas dos produtos, as "
                    "instituições participantes, quando não cobram tarifas, "
                    "\ndevem enviar o valor 0.00 sinalizando que para aquela taxa não há "
                    "cobrança pelo serviço.",
    )
    currency: CurrencyCode = Field(
        ...,
        json_path=[
            "/data/fees/services/prices/currency", # CSV L17
            "/data/serviceBundles/prices/currency", # CSV L36
        ],
        min_length=3,
        max_length=3,
        description="Moeda referente ao valor mínimo da Tarifa, segundo modelo ISO-4217",
    )
    customers: Customers = Field(
        ...,
        json_path=[
            "/data/fees/services/prices/customers", # CSV L18,
            "/data/serviceBundles/prices/customers", # CSV L37
        ],
        description="Informações relevantes para o cliente.",
    )


class MonetaryMinimumAmount(BaseModel):
    value: MoneyString = Field(
        ...,
        json_path=[
            "/data/fees/services/minimum/value", # CSV L21
            "/data/serviceBundles/minimum/value", # CSV L40
            "/data/fees/services/maximum/value", # CSV L50
            "/data/termsConditions/minimumBalance/value", # CSV L60
        ],
        max_length=12,
        description="Valor mínimo apurado para a tarifa de serviços sobre a base de clientes "
                    "no mês de referência."
                    "\n\nObservação: Para efeito de comparação de taxas dos produtos, as "
                    "instituições participantes, quando não cobram tarifas, "
                    "\ndevem enviar o valor 0.00 sinalizando que para aquela taxa não há "
                    "cobrança pelo serviço.",
    )
    currency: CurrencyCode = Field(
        ...,
        json_path=[
            "/data/fees/services/minimum/currency", # CSV L22
            "/data/serviceBundles/minimum/currency", # CSV L41
            "/data/fees/services/maximum/currency", # CSV L51
            "/data/termsConditions/minimumBalance/currency", # CSV L61
        ],
        min_length=3,
        max_length=3,
        description="Moeda referente ao valor mínimo da Tarifa, segundo modelo ISO-4217",
    )


class MonetaryMaximumAmount(BaseModel):
    # CSV L24/L43/L53: */maximum/value
    value: MoneyString = Field(
        ...,
        max_length=12,
        description="Valor máximo apurado para a tarifa de serviços sobre a base de clientes no mês de referência.\n\nObservação: Para efeito de comparação de taxas dos produtos, as instituições participantes, quando não cobram tarifas, \ndevem enviar o valor 0.00 sinalizando que para aquela taxa não há cobrança pelo serviço.\n",
    )
    # CSV L25/L44/L54: */maximum/currency
    currency: CurrencyCode = Field(
        ...,
        min_length=3,
        max_length=3,
        description="Moeda referente ao valor mínimo da Tarifa, segundo modelo ISO-4217",
    )


class MonetaryMinimumBalanceAmount(BaseModel):
    # CSV L60: /data/termsConditions/minimumBalance/value
    value: MoneyString = Field(
        ...,
        max_length=12,
        description="Saldo mínimo exigido nos Termos e condições contratuais, que regem as contas comercializadas.",
    )
    # CSV L61: /data/termsConditions/minimumBalance/currency
    currency: CurrencyCode = Field(
        ...,
        min_length=3,
        max_length=3,
        description="Moeda referente ao valor mínimo da Tarifa, segundo modelo ISO-4217",
    )


class ServiceFee(BaseModel):
    # CSV L11: /data/fees/services/name
    name: SizedText = Field(
        ...,
        max_length=250,
        description="Nome do Serviço que incide sobre tipo de conta selecionado para pessoa jurídica(Campo Livre)",
    )
    # CSV L12: /data/fees/services/code
    code: SizedText = Field(
        ...,
        max_length=100,
        description="Sigla de identificação de Outros Serviços que incidem sobre os tipos de contas informados.",
    )
    # CSV L13: /data/fees/services/chargingTriggerInfo
    chargingTriggerInfo: SizedText = Field(
        ...,
        max_length=2000,
        description="Fatos geradores de cobrança que incidem sobre serviço que compõe o Pacote de Serviços.",
    )
    # CSV L14: /data/fees/services/prices
    prices: Annotated[
        list[PriceDistribution],
        Field(
            min_length=4,
            max_length=4,
            description="Lista distribuição preços tarifas de serviços",
        ),
    ]
    # CSV L20: /data/fees/services/minimum
    minimum: MonetaryMinimumAmount = Field(
        ...,
        description="Valor mínimo apurado para a tarifa de serviços sobre a base de clientes no mês de referência.\n\nObservação: Para efeito de comparação de taxas dos produtos, as instituições participantes, quando não cobram tarifas, \ndevem enviar o valor 0.00 sinalizando que para aquela taxa não há cobrança pelo serviço.\n",
    )
    # CSV L23: /data/fees/services/maximum
    maximum: MonetaryMaximumAmount = Field(
        ...,
        description="Valor máximo apurado para a tarifa de serviços sobre a base de clientes no mês de referência.\n\nObservação: Para efeito de comparação de taxas dos produtos, as instituições participantes, quando não cobram tarifas, \ndevem enviar o valor 0.00 sinalizando que para aquela taxa não há cobrança pelo serviço.\n",
    )


class Fees(BaseModel):
    # CSV L10: /data/fees/services
    services: Annotated[
        list[ServiceFee],
        Field(
            min_length=1,
            max_length=200,
            description="Lista das Tarifas cobradas sobre Serviços",
        ),
    ]


class ServiceBundleService(BaseModel):
    # CSV L29: /data/serviceBundles/services/code
    code: SizedText = Field(
        ...,
        max_length=100,
        description="Código que identifica o Serviço que compõe o Pacote de Serviços, podendo ser da lista de Serviços Prioritários ou Outros Serviços. p.ex. segundo Resolução 3.919 do Bacen: 'SAQUE_TERMINAL'.\n",
    )
    # CSV L30: /data/serviceBundles/services/chargingTriggerInfo
    chargingTriggerInfo: SizedText = Field(
        ...,
        max_length=2000,
        description="Fatos geradores de cobrança que incidem sobre serviço que compõe o Pacote de Serviços.\n",
    )
    # CSV L31: /data/serviceBundles/services/eventLimitQuantity
    eventLimitQuantity: EventQuantity = Field(
        ...,
        max_length=6,
        description="Segundo Resolução  4196, BCB, de 2013: Quantidade de eventos previstos no Pacote de Serviços (Número de eventos incluídos no mês) p.ex.'2'. No caso de quantidade ilimitada, reportar 999999\n",
    )
    # CSV L32: /data/serviceBundles/services/freeEventQuantity
    freeEventQuantity: EventQuantity = Field(
        ...,
        max_length=6,
        description="Segundo Resolução  4196, BCB, de 2013: Quantidade de eventos previstos no Pacote de Serviços com isenção de Tarifa.p.ex.'1'  No caso de quantidade ilimitada, reportar 999999\n",
    )


class ServiceBundlePrice(BaseModel):
    # CSV L34: /data/serviceBundles/prices/interval
    interval: PriceInterval = Field(..., description="Segundo Normativa nº 32, BCB, de 2020: Distribuição de frequência relativa dos valores de tarifas cobradas dos clientes, de que trata o § 2º do art. 3º da Circular nº 4.015, de 2020, deve dar-se com base em quatro faixas de igual tamanho, com explicitação dos valores sobre a mediana em cada uma dessas faixas. Informando: 1ª faixa, 2ª faixa, 3ª faixa e 4ª faixa\n")
    # CSV L35: /data/serviceBundles/prices/monthlyFee
    monthlyFee: MoneyString = Field(
        ...,
        max_length=12,
        description="Valor da mediana de cada faixa relativa ao serviço ofertado, informado no período, conforme Res nº 32 BCB, 2020. p.ex. ''45.00''\n(representa um valor monetário. p.ex: 1547368.92. Este valor, considerando que a moeda seja BRL, significa R$ 1.547.368,92. \nO único separador presente deve ser o ''.'' (ponto) para indicar a casa decimal. Não deve haver separador de milhar).\n\nObservação: Para efeito de comparação de taxas dos produtos, as instituições participantes, quando não cobram tarifas, \ndevem enviar o valor 0.00 sinalizando que para aquela taxa não há cobrança pelo serviço.\n",
    )
    # CSV L36: /data/serviceBundles/prices/currency
    currency: CurrencyCode = Field(
        ...,
        min_length=3,
        max_length=3,
        description="Moeda referente ao valor mínimo da Tarifa, segundo modelo ISO-4217",
    )
    # CSV L37: /data/serviceBundles/prices/customers
    customers: Customers = Field(..., description="Informações relevantes para o cliente.")


class ServiceBundle(BaseModel):
    # CSV L27: /data/serviceBundles/name
    name: SizedText = Field(
        ...,
        max_length=250,
        description="Nome do Pacote de Serviços dado pela instituição.",
    )
    # CSV L28: /data/serviceBundles/services
    services: Annotated[
        list[ServiceBundleService],
        Field(
            min_length=1,
            max_length=100,
            description="Lista dos serviços que compõe o pacote de serviços",
        ),
    ]
    # CSV L33: /data/serviceBundles/prices
    prices: Annotated[
        list[ServiceBundlePrice],
        Field(
            min_length=4,
            max_length=4,
            description="Lista distribuição preços tarifas de serviços",
        ),
    ]
    # CSV L39: /data/serviceBundles/minimum
    minimum: Optional[MonetaryMinimumAmount] = None
    # CSV L42: /data/serviceBundles/maximum
    maximum: Optional[MonetaryMaximumAmount] = None


class TermsConditions(BaseModel):
    minimumBalance: MonetaryMinimumBalanceAmount = Field(
        ...,
        json_path = "/data/termsConditions/minimumBalance", # CSV L59
        description="Saldo mínimo exigido nos Termos e condições contratuais, que regem as contas comercializadas.",
    )
    elegibilityCriteriaInfo: SizedText = Field(
        ...,
        json_path = "/data/termsConditions/elegibilityCriteriaInfo", # CSV L62
        max_length=2000,
        description="Critérios de qualificação do cliente com a finalidade de definir sua elegibilidade para a aquisição do tipo de conta. Campo Aberto",
    )
    closingProcessInfo: SizedText = Field(
        ...,
        json_path = "/data/termsConditions/closingProcessInfo", # CSV L63
        max_length=2000,
        description="Procedimentos de encerramento para o tipo de conta tratado. Possibilidade de inscrição da URL. Endereço eletrônico de acesso ao canal. p.ex. 'https://example.com/mobile-banking' ",
    )


class IncomeRate(BaseModel):
    savingAccount: Optional[SizedText] = Field(
        json_path = "/data/incomeRate/savingAccount", # CSV L65
        default=None,
        max_length=2000,
        description="Descrição da Remuneração especificamente para Conta de Poupança. Deve ser preenchido com a determinação legal vigente. \n\n[Restrição] Obrigatório quando \"type\" for igual \"CONTA_POUPANCA\".\n",
    )
    prepaidPaymentAccount: Optional[SizedText] = Field(
        json_path = "/data/incomeRate/prepaidPaymentAccount", # CSV L66
        default=None,
        max_length=2000,
        description="Campo Livre. Deve explicitar o Percentual em favor do titular da conta de pagamento pré-paga.",
    )


class BusinessAccountDTO(BaseModel):
    participant: Participant = Field(
        ...,
        json_path = "/data/participant", # CSV L3
        description="Conjunto de informações relativas ao participante do Open Finance que oferta este produto.",
    )
    type: BusinessAccountType = Field(
        ...,
        json_path = "/data/type", # CSV L8
        description="Tipos de contas ofertadas para pessoa natural ou jurídica, "
                    "p.ex. 'CONTA_DEPOSITO_A_VISTA'."
                    "\nConta de depósito à vista ou Conta corrente - é o tipo mais comum. "
                    "Nela, o dinheiro fica à sua disposição para ser sacado a qualquer momento. "
                    "Essa conta não gera rendimentos para o depositante"
                    "\nConta poupança - foi criada para estimular as pessoas a pouparem. "
                    "O dinheiro que ficar na conta por trinta dias passa a gerar rendimentos, "
                    "com isenção de imposto de renda para quem declara. Ou seja, o dinheiro “cresce” (rende) "
                    "enquanto ficar guardado na conta. Cada depósito terá rendimentos de mês em mês, sempre "
                    "no dia do mês em que o dinheiro tiver sido depositado"
                    "\nConta de pagamento pré-paga: segundo CIRCULAR Nº 3.680, BCB de  2013, é a "
                    "'destinada à execução de transações de pagamento em moeda eletrônica realizadas com base "
                    "em fundos denominados em reais previamente aportados'"
    )
    fees: Fees = Field(
        ...,
        json_path = "/data/fees", # CSV L9
        description="Objeto que reúne informações de tarifas de serviços.",
    )
    serviceBundles: Optional[
        Annotated[
            list[ServiceBundle],
            Field(
                json_path = "/data/serviceBundles", # # CSV L26:
                min_length=1,
                max_length=100,
                description="Lista dos pacotes de serviços de contas com serviços essenciais "
                "padronizados e regulados pela Resolução BC 3919, de 25/11/2010"
                "\n\n[Restrição]"
                "\n- Obrigatório quando \"type\" for igual \"CONTA_DEPOSITO_A_VISTA\" "
                "(conta corrente) ou \"CONTA_POUPANCA\", porque existem hoje pacotes passíveis de "
                "cobrança diferentes dos serviços essenciais (que não são cobrados);"
                "\n\n- Opcional quando \"type\" for igual \"CONTA_PAGAMENTO_PRE_PAGA\" ficando "
                "condicionado caso a instituição tenha pacote de serviço atrelado a este tipo de conta.",
            ),
        ]
    ] = None
    openingClosingChannels: Annotated[
        list[OpeningClosingChannel],
        Field(
            json_path = "/data/openingClosingChannels", # CSV L55
            min_length=1,
            max_length=7,
            description="Lista dos canais para aberturas e encerramento",
        ),
    ]
    openingClosingChannelsAdditionalInfo: Optional[SizedText] = Field(
        json_path = "/data/openingClosingChannelsAdditionalInfo", # CSV L56
        default=None,
        max_length=140,
        description="Campo livre para preenchimento das informações adicionais referente ao \"openingClosingChannels\". \n\n[Restrição] Obrigatório quando \"openingClosingChannels\" for igual 'OUTROS'.\n",
    )
    transactionMethods: Annotated[
        list[TransactionMethod],
        Field(
            json_path = "/data/transactionMethods", # CSV L57
            min_length=1,
            max_length=4,
            description="Lista de formas de movimentação",
        ),
    ]
    termsConditions: TermsConditions = Field(
        ...,
        json_path = "/data/termsConditions", # CSV L58
        description="Objeto que reúne informações relativas a Termos e Condições para as modalidades tratadas",
    )
    incomeRate: Optional[IncomeRate] = Field(
        json_path = "/data/incomeRate", # CSV L64
        default=None,
        description="Objeto com informações de remuneração da conta.",
    )
