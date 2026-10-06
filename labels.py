LABELS: dict[str, str] = {
    "Atendimento": (
        "Emails relacionados com pedidos de informação sobre contratos, atendimento "
        "geral, contactos, moradas, horários, balcão ou lojas."
    ),
    "Balção Digital": (
        "Emails relacionados com pedidos de informação ou exposição de "
        "dificuldades/problemas com o balcão digital, a app, passwords, e acessos."
    ),
    "Pagamento": (
        "Emails relacionados com pagamentos, informação sobre valores a pagar ou em " "dívida."
    ),
    "Contratação - Contratos": (
        "Emails relacionados com pedidos de informação sobre contratos existentes ou "
        "novos, ou alteração de dados do contrato ou do cliente (como morada de "
        "residência, nome do titular, NIF, email ou telefone de contacto, email para onde"
        " são enviadas as faturas, ou IBAN/NIB). Pedidos para aderir, alterar ou cancelar"
        " o débito direto não são desta categoria, são 'Pagamento das faturas'."
    ),
    "Contratação - Rescisões": (
        "Emails relacionados com pedidos de cancelamento/rescisão/fecho/baixa do " "contrato."
    ),
    "Faturação - Envio das faturas ": (
        "Emails relacionados com a forma como o cliente quer passar a receber as faturas "
        "daqui para a frente (aderir ou mudar para fatura eletrónica, por email, PDF ou "
        "papel), ou pedidos de informação/esclarecimento sobre o conteúdo ou os valores "
        "de uma fatura. Pedidos para enviar faturas concretas (de um mês, período, número"
        " ou lista) não são desta categoria, são 'Emissão de 2ª vias'."
    ),
    "Faturação - Pagamento  das faturas ": (
        "Emails relacionados com pedidos de esclarecimento relativos aos meios de "
        "pagamento, débito direto, mbway, etc., incluindo pedidos para aderir, alterar ou"
        " cancelar o débito direto. Pedidos para alterar apenas o IBAN/NIB não são desta "
        "categoria, são 'Contratos'."
    ),
    "Faturação - Dados Pagamento ": (
        "Emails relacionados com pedidos de dados para o pagamento, ou emissão de nova "
        "referência de pagamento."
    ),
    "Faturação - Emissão de 2ª vias ": (
        "Emails a pedir que enviem, reenviem ou emitam uma ou mais faturas concretas, "
        "identificadas por mês, período, número, valor, lista ou documento em anexo, "
        "incluindo faturas já emitidas em falta, não recebidas ou já pagas, ou uma 2ª via"
        " de uma determinada fatura. Não inclui o envio de leituras do contador pelo "
        "cliente."
    ),
    "Faturação - Extrato da Conta Corrente ": (
        "Emails relacionados com pedidos de informação sobre o extrato da conta corrente,"
        " ou o saldo atual."
    ),
    "Acordo de Pagamento": (
        "Emails relacionados com negociação de um acordo ou plano de pagamento faseado "
        "(como por parcelas, ou prestações, etc.)."
    ),
    "Tarifa social": (
        "Emails relacionados com apoio social, pedidos de informação sobre tarifa social,"
        " expressão de dificuldades financeiras e económicas, ou "
        "candidatura/aplicabilidade ao regime de tarifa social."
    ),
    "Tarifa familiar": (
        "Emails relacionados com pedidos de informação sobre tarifa familial, ou "
        "candidatura/aplicabilidade ao regime especial para famílias numerosas."
    ),
    "Elogio ": (
        "Email relacionados com expressão de elogio, satisfação, congratulação, "
        "enaltecimento, prestigio, excelencia, simpatia, profissionalismo, ou dedicação "
        "do serviço."
    ),
    "FW E-mail EDOC": (
        "Emails relacionados com pedidos de informação/esclarecimentos gerais, apoio ou "
        "dúvidas. Emails relacionados com reclamações/queixas/exposições/pedidos de "
        "retificação ou análise, expressão de insatisfação, consumos errados. Emails "
        "relacionados com roturas ou fugas, danos, esgotos, referências criminais ou "
        "policiais. Emails relacionados com agendamento ou substituição de equipamento, "
        "construção, incendios, devolução, reembolso ou compensação de valores."
    ),
}