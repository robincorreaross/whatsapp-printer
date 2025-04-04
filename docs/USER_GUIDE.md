# Guia do Usuário - WhatsApp Printer

## Requisitos do Sistema

- Windows 10/11
- Python 3.10+
- Conexão com internet

## Instalação

1. Execute o instalador como administrador
2. Configure os dados da API:
   - URL do servidor
   - Nome da instância
   - Chave API
3. A impressora virtual será registrada automaticamente

## Uso Básico

1. Em qualquer aplicativo, selecione "Imprimir"
2. Escolha "WhatsApp Printer" como impressora
3. Preencha o número do destinatário (sem 55)
4. Adicione uma mensagem opcional
5. Clique em "Enviar"

## Solução de Problemas

- Verifique o log em `%appdata%\WhatsApp Printer\logs`
- Certifique-se que:
  - A instância da API está online
  - O número está no formato correto
  - O arquivo não está corrompido
