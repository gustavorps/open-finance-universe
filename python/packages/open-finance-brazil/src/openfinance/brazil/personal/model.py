from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel, Field, StringConstraints


MoneyString = Annotated[str, StringConstraints(pattern=r"^(\d{1,9}\.\d{2}){1}$")]
CurrencyCode = Annotated[str, StringConstraints(pattern=r"^(\w{3}){1}$")]
RateString = Annotated[str, StringConstraints(pattern=r"^\d{1}\.\d{6}$")]
CnpjString = Annotated[str, StringConstraints(pattern=r"^\d{14}$")]
SizedText = Annotated[str, StringConstraints(pattern=r"^\S(?:.*\S)?$")]
EventQuantity = Annotated[str, StringConstraints(pattern=r"^(\d{1,6}){1}$")]


class PersonalAccountType(str, Enum):
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
    # CSV L4: /data/participant/brand
    brand: SizedText = Field(
        ...,
        max_length=80,
        description="Nome da marca reportada pelo participante do Open Finance.",
    )
    # CSV L5: /data/participant/name
    name: SizedText = Field(
        ...,
        max_length=80,
        description="Nome da instituição pertencente à marca.",
    )
    # CSV L6: /data/participant/cnpjNumber
    cnpjNumber: CnpjString = Field(..., description="CNPJ da instituição.")
    # CSV L7: /data/participant/urlComplementaryList
    urlComplementaryList: Optional[SizedText] = Field(
        default=None,
        max_length=1024,
        description="URL com a lista complementar de nomes e CNPJs agrupados.",
    )


class Customers(BaseModel):
    # CSV L19/L35/L54: */prices/customers/rate
    rate: RateString = Field(
        ...,
        max_length=8,
        description="Percentual de clientes em cada faixa.",
    )


class PriceDistribution(BaseModel):
    # CSV L15/L31: */prices/interval
    interval: PriceInterval = Field(
        ...,
        description="Faixa de distribuição de frequência relativa da tarifa.",
    )
    # CSV L16/L32: */prices/value
    value: MoneyString = Field(
        ...,
        max_length=12,
        description="Valor da mediana da faixa relativa ao serviço ofertado.",
    )
    # CSV L17/L33: */prices/currency
    currency: CurrencyCode = Field(
        ...,
        min_length=3,
        max_length=3,
        description="Moeda referente ao valor, conforme ISO-4217.",
    )
    # CSV L18/L34: */prices/customers
    customers: Customers = Field(..., description="Informações relevantes para o cliente.")


class MonetaryAmount(BaseModel):
    # CSV L21/L24/L37/L40/L56/L59/L66: */value
    value: MoneyString = Field(
        ...,
        max_length=12,
        description="Valor monetário apurado para o campo de mínimo/máximo/saldo.",
    )
    # CSV L22/L25/L38/L41/L57/L60/L67: */currency
    currency: CurrencyCode = Field(
        ...,
        min_length=3,
        max_length=3,
        description="Moeda referente ao valor, conforme ISO-4217.",
    )


class PriorityService(BaseModel):
    # CSV L11: /data/fees/priorityServices/name
    name: str = Field(
        ...,
        description="Nome do serviço prioritário segundo Resolução 3.919 do Bacen.",
    )
    # CSV L12: /data/fees/priorityServices/code
    code: str = Field(
        ...,
        description="Sigla de identificação do serviço prioritário.",
    )
    # CSV L13: /data/fees/priorityServices/chargingTriggerInfo
    chargingTriggerInfo: SizedText = Field(
        ...,
        max_length=2000,
        description="Fatos geradores de cobrança do serviço prioritário.",
    )
    # CSV L14: /data/fees/priorityServices/prices
    prices: Annotated[
        list[PriceDistribution],
        Field(
            min_length=4,
            max_length=4,
            description="Lista de distribuição de preços das tarifas do serviço prioritário.",
        ),
    ]
    # CSV L20: /data/fees/priorityServices/minimum
    minimum: MonetaryAmount = Field(
        ...,
        description="Valor mínimo apurado para a tarifa do serviço prioritário.",
    )
    # CSV L23: /data/fees/priorityServices/maximum
    maximum: MonetaryAmount = Field(
        ...,
        description="Valor máximo apurado para a tarifa do serviço prioritário.",
    )


class OtherService(BaseModel):
    # CSV L27: /data/fees/otherServices/name
    name: SizedText = Field(
        ...,
        max_length=250,
        description="Nome do serviço não prioritário (campo livre).",
    )
    # CSV L28: /data/fees/otherServices/code
    code: SizedText = Field(
        ...,
        max_length=100,
        description="Sigla de identificação do serviço (campo livre).",
    )
    # CSV L29: /data/fees/otherServices/chargingTriggerInfo
    chargingTriggerInfo: SizedText = Field(
        ...,
        max_length=2000,
        description="Fatos geradores de cobrança dos outros serviços.",
    )
    # CSV L30: /data/fees/otherServices/prices
    prices: Annotated[
        list[PriceDistribution],
        Field(
            min_length=4,
            max_length=4,
            description="Lista de distribuição de preços das tarifas de outros serviços.",
        ),
    ]
    # CSV L36: /data/fees/otherServices/minimum
    minimum: MonetaryAmount = Field(
        ...,
        description="Valor mínimo apurado para tarifa de outros serviços.",
    )
    # CSV L39: /data/fees/otherServices/maximum
    maximum: MonetaryAmount = Field(
        ...,
        description="Valor máximo apurado para tarifa de outros serviços.",
    )


class Fees(BaseModel):
    # CSV L10: /data/fees/priorityServices
    priorityServices: Optional[
        Annotated[
            list[PriorityService],
            Field(
                min_length=1,
                max_length=40,
                description="Lista de tarifas cobradas sobre serviços prioritários.",
            ),
        ]
    ] = None
    # CSV L26: /data/fees/otherServices
    otherServices: Optional[
        Annotated[
            list[OtherService],
            Field(
                min_length=1,
                max_length=100,
                description="Lista de tarifas cobradas sobre outros serviços.",
            ),
        ]
    ] = None


class ServiceBundleService(BaseModel):
    # CSV L45: /data/serviceBundles/services/code
    code: SizedText = Field(
        ...,
        max_length=100,
        description="Código do serviço que compõe o pacote de serviços.",
    )
    # CSV L46: /data/serviceBundles/services/chargingTriggerInfo
    chargingTriggerInfo: SizedText = Field(
        ...,
        max_length=2000,
        description="Fato gerador de cobrança do serviço do pacote.",
    )
    # CSV L47: /data/serviceBundles/services/eventLimitQuantity
    eventLimitQuantity: EventQuantity = Field(
        ...,
        max_length=6,
        description="Quantidade de eventos previstos no pacote de serviços.",
    )
    # CSV L48: /data/serviceBundles/services/freeEventQuantity
    freeEventQuantity: EventQuantity = Field(
        ...,
        max_length=6,
        description="Quantidade de eventos com isenção de tarifa no pacote.",
    )


class ServiceBundlePrice(BaseModel):
    # CSV L50: /data/serviceBundles/prices/interval
    interval: PriceInterval = Field(..., description="Faixa da distribuição de preço.")
    # CSV L51: /data/serviceBundles/prices/monthlyFee
    monthlyFee: MoneyString = Field(
        ...,
        max_length=12,
        description="Valor da mediana da faixa para mensalidade do pacote.",
    )
    # CSV L52: /data/serviceBundles/prices/currency
    currency: CurrencyCode = Field(
        ...,
        min_length=3,
        max_length=3,
        description="Moeda da mensalidade, conforme ISO-4217.",
    )
    # CSV L53: /data/serviceBundles/prices/customers
    customers: Customers = Field(..., description="Informações relevantes para o cliente.")


class ServiceBundle(BaseModel):
    # CSV L43: /data/serviceBundles/name
    name: SizedText = Field(
        ...,
        max_length=250,
        description="Nome do pacote de serviços dado pela instituição.",
    )
    # CSV L44: /data/serviceBundles/services
    services: Annotated[
        list[ServiceBundleService],
        Field(
            min_length=1,
            max_length=100,
            description="Lista de serviços que compõem o pacote de serviços.",
        ),
    ]
    # CSV L49: /data/serviceBundles/prices
    prices: Annotated[
        list[ServiceBundlePrice],
        Field(
            min_length=4,
            max_length=4,
            description="Lista de distribuição de preços do pacote de serviços.",
        ),
    ]
    # CSV L55: /data/serviceBundles/minimum
    minimum: Optional[MonetaryAmount] = None
    # CSV L58: /data/serviceBundles/maximum
    maximum: Optional[MonetaryAmount] = None


class TermsConditions(BaseModel):
    # CSV L65: /data/termsConditions/minimumBalance
    minimumBalance: MonetaryAmount = Field(
        ...,
        description="Saldo mínimo exigido nos termos e condições contratuais.",
    )
    # CSV L68: /data/termsConditions/elegibilityCriteriaInfo
    elegibilityCriteriaInfo: SizedText = Field(
        ...,
        max_length=2000,
        description="Critérios de elegibilidade do cliente para aquisição da conta.",
    )
    # CSV L69: /data/termsConditions/closingProcessInfo
    closingProcessInfo: SizedText = Field(
        ...,
        max_length=2000,
        description="Procedimentos de encerramento para o tipo de conta.",
    )


class IncomeRate(BaseModel):
    # CSV L71: /data/incomeRate/savingAccount
    savingAccount: Optional[SizedText] = Field(
        default=None,
        max_length=2000,
        description="Descrição da remuneração para conta poupança.",
    )
    # CSV L72: /data/incomeRate/prepaidPaymentAccount
    prepaidPaymentAccount: Optional[SizedText] = Field(
        default=None,
        max_length=2000,
        description="Percentual em favor do titular da conta de pagamento pré-paga.",
    )


class PersonalAccountDTO(BaseModel):
    # CSV L3: /data/participant
    participant: Participant = Field(
        ...,
        description="Informações do participante do Open Finance que oferta o produto.",
    )
    # CSV L8: /data/type
    type: PersonalAccountType = Field(
        ...,
        description="Tipo de conta ofertada para pessoa natural ou jurídica.",
    )
    # CSV L9: /data/fees
    fees: Optional[Fees] = Field(
        default=None,
        description="Objeto que reúne informações de tarifas de serviços.",
    )
    # CSV L42: /data/serviceBundles
    serviceBundles: Optional[
        Annotated[
            list[ServiceBundle],
            Field(
                min_length=1,
                max_length=200,
                description="Lista dos pacotes de serviços de contas.",
            ),
        ]
    ] = None
    # CSV L61: /data/openingClosingChannels
    openingClosingChannels: Annotated[
        list[OpeningClosingChannel],
        Field(
            min_length=1,
            max_length=7,
            description="Lista dos canais para abertura e encerramento de conta.",
        ),
    ]
    # CSV L62: /data/openingClosingChannelsAdditionalInfo
    openingClosingChannelsAdditionalInfo: Optional[SizedText] = Field(
        default=None,
        max_length=140,
        description="Informações adicionais de canais, obrigatório quando houver OUTROS.",
    )
    # CSV L63: /data/transactionMethods
    transactionMethods: Annotated[
        list[TransactionMethod],
        Field(
            min_length=1,
            max_length=4,
            description="Lista de formas de movimentação da conta.",
        ),
    ]
    # CSV L64: /data/termsConditions
    termsConditions: TermsConditions = Field(
        ...,
        description="Objeto com termos e condições para a modalidade de conta.",
    )
    # CSV L70: /data/incomeRate
    incomeRate: Optional[IncomeRate] = Field(
        default=None,
        description="Objeto com informações de remuneração da conta.",
    )
