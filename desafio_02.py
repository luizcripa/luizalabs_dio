from abc import ABC, abstractclassmethod, abstractproperty 
from datetime import datetime
import textwrap


class Conta:
    def __init__(self, numero, cliente):
        self._saldo  = 0
        self._numero = numero  
        self._agencia = "0001"
        self._cliente = cliente 
        self._historico = Historico()

    def nova_conta(cls, cliente, numero):
        return cls( cliente, numero)

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n=== Depósito realizado com sucesso! ===")
            return True           
        else:
            print("\n### Operação Falhou!! ###\n###O valor informado é inválido ###")
        return False

    def sacar(self, valor):
        excedeu_saldo = valor > self._saldo
        if excedeu_saldo:
            print(f"\n### Saldo insulficiente para operação! \n SALDO ATUAL R$ {self._saldo:.2} ###")
        elif valor > 0:
            self._saldo -= valor
            print("\n=== Saque realizado com sucesso! ===")
            return True
        else:
            print("\n### Operação Falhou!! ###\n###O valor informado é inválido ###")
        return False
            
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente    
    
    @property
    def historico(self):
        return self._historico
    
    @property
    def numero(self):
        return self._numero

    def __str__(self):
        return f"Class={__class__.__name__} , { ' , '.join(f'{chave} ={valor}' for chave,valor in self.__dict__.items())}"

class ContaCorrente(Conta):
    def __init__(self, numero , cliente, limite= 500, limite_saques=3 ):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques      

    def sacar(self, valor):
        
        numero_saques = len( [ transacao for transacao in self._historico._transacoes if transacao["tipo"] == Saque.__name__ ])
        excedeu_limite_saques = numero_saques > self.limite_saques
        excedeu_limite = valor > self.limite

        if excedeu_limite or excedeu_limite_saques:
            print(f"Operação bloqueada por {"valor acima do saldo " if excedeu_limite else "Número de saques atingido"} !")
            return False
        else:
            return super().sacar(valor)

    def __str__(self):
        return f"""\
            Agencia: \t{self._agencia}
            C/C: \t\t {self._numero}
            Titular: \t {self.cliente._nome}
        """

class Cliente:
    def __init__(self, endereco):
        self._endereco = endereco 
        self._contas = []

    def realiza_transacao(self, conta, transacao):
        transacao.registrar(conta)
        print("Transação realizada")

    def adicionar_conta(self, conta):
        self._contas.append(conta)

    def __str__(self):
        return f"Class ={__class__.__name__} , {' , '.join( f'{chave} = {valor}' for chave,valor in self.__dict__.items())}"

class PessoaFisica(Cliente):
    def __init__(self, cpf, nome, data_nascimento, endereco):
        self._cpf = cpf
        self._nome = nome
        self._datanascimento = data_nascimento
        super().__init__(endereco= endereco)

class Historico:
    def __init__(self):
        self._transacoes = []

    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        print(self._transacoes)
        print(self._transacoes.__class__)
        print(self._transacoes.__class__.__name__)

        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,    #.name,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )
        # print(self._transacoes)
        # print(self._transacoes.__class__)
        # print(self._transacoes.__class__.__name__)

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self,conta):
        pass
     
class Deposito(Transacao):
    def __init__(self,valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)

class Saque(Transacao):
    def __init__(self,valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)



def criar_cliente(clientes):
    cliente, cpf = pega_cliente(clientes)

    print(cliente, cpf)
    if cliente:
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)
    apresenta_mensagem("=== Cliente criado com sucesso! ===")
    

def criar_conta(numero_conta, clientes, contas):
    cliente, cpf  = pega_cliente(clientes)

    if not cliente:
        print(f"\n@@@ Cliente {cpf} não encontrado, fluxo de criação de conta encerrado! @@@")
        return

    conta = ContaCorrente(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente._contas.append(conta)
    apresenta_mensagem("=== Conta criada com sucesso! ===")

def movimento(clientes,operacao):
    cliente, cpf = pega_cliente(clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input(f"Informe o valor do {operacao}: "))
    transacao = globals()[operacao](valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realiza_transacao(conta, transacao)


def recuperar_conta_cliente(cliente):
    if not cliente._contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return

    numero = 1
    if len(cliente._contas) > 1:
        for conta in cliente._contas:
            print(f"{numero}º opção \n {conta}" )
            numero +=1
        
        while True:
            try:
                numero = int(input("informe posição da conta desejada!"))
                if 1 <= numero <= len(cliente._contas):
                    return cliente._contas[ numero-1 ]        
            except ValueError:    
                print("Por favor, digite um número válido.")

    # FIXME: Única conta encontrada!
    return cliente._contas[0]

def exibir_extrato(clientes):
    cliente, cpf = pega_cliente(clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    transacoes = conta._historico._transacoes   

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")


# funcoes uteis #######
def apresenta_mensagem(texto):
    print(f"\n {texto}")
    input("\n\n\ Precione [Enter] para continuar...")
    
def pega_cliente(clientes):
    cpf = input("Informe o CPF do cliente: ")
    clientes_filtrados = [cliente for cliente in clientes if cliente._cpf == cpf]    
    if not clientes_filtrados:
        return None, cpf
    else:
        return clientes_filtrados[0], cpf
    
def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))

def gera_menu():
    menu = """\n
    ================ MENU ================
    ||     [ 1 ] - \tDepositar          ||
    ||     [ 2 ] - \tSacar              ||
    ||     [ 3 ] - \tExtrato            ||
    ||     [ 4 ] - \tNova conta         ||
    ||     [ 5 ] - \tListar contas      ||
    ||     [ 6 ] - \tNovo usuário       ||
    ||     [ 0 ] - \tSair               ||
    === DIGITE N° REFERENTE A OPERACAO ===
    => """
    return input(menu)

def main():
    clientes = []
    contas = []

    while True:
        opcao = gera_menu()

        if opcao == "1":
            #depositar(clientes)
            movimento(clientes,"Deposito")

        elif opcao == "2":
            #sacar(clientes)
            movimento(clientes,"Saque")

        elif opcao == "3":
            exibir_extrato(clientes)

        elif opcao == "4":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)
        
        elif opcao == "5":
            listar_contas(contas)

        elif opcao == "6":
            criar_cliente(clientes)

        elif opcao == "0":
            break

        else:
            print("\n### Operação inválida, por favor selecione novamente a operação desejada. ###")

main()
