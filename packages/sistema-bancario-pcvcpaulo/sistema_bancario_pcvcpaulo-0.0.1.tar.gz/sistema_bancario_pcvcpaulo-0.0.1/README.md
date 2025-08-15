## Desafio_Criacao_Pacotes_em_Python
Exercício prático - Criar um pacote usando a estrutura simples de um módulo.

📚 Descrição

    O sistema bancário executa as seguintes operações: depósito, saque e visualiza o extrato.

🤌 Operação de depósito

    O sistema deve ser possível de realizar depósitos de valores positivos na conta corrente do usuário.Nesta primeira versão teremos
    apenas um usuário, dessa forma não será necessário identificar o número da conta e agência bancária. Todos os depósitos deverão 
    ser armazenados em uma variável e exibidos na operação extrato.

    Por exemplo, na opção de depósito o sistema tem que perguntar ao usuário qual o valor que ele deseja depositar. Esse valor tem 
    que ser um valor inteiro e positivo, ou seja, não podemos depositar “R$ - 100,00”. O sistema não poderá permitir que o usuário
    informe um valor negativo.

    Estas operações de depósito deverão ficar armazenadas para que, nas operações de extrato elas estejam acessíveis. Se foram 
    feitos 10 depósitos, estes 10 depósitos devem constar no extrato.

💰Operação de saque

    Outro requisito do sistema é que serão permitidos apenas 3 saques diários com limite máximo de R$ 500,00 por saque. Caso o 
    usuário não tenha saldo em conta, o sistema deve exibir uma mensagem informando que não será possível efetuar o saque por 
    saldo insuficiente. Todos os saques devem ser armazenados em uma variável e exibidos na operação de extrato.

📋Operação de extrato

    O extrato deverá listar todos os depósitos e saques realizados na conta. No final da listagem deve ser exibido o saldo 
    atual da conta. Os valores devem ser exibidos utilizando o formato R$ 000.00, ou seja, 1500.45 = R$ 1500.45.



## Instalação
Use o gerenciador de pacotes [pip](https://pip.pypa.io/en/stable/) para instalar o package sistema_bancario_pcvcpaulo

``` bash
pip install -m sistema-bancario-pcvcpaulo==0.0.1
```

## Uso

``` python
from sistema_bancario_pcvcpaulo import sistema_bancario

```

## Autor
PAULO CÉSAR

## Licença
[MIT](https://choosealicense.com/licenses/mit/)

