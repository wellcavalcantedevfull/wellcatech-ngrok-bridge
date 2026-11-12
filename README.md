# 🌉 Ngrok Remote Bridge

Utilitário desktop com interface Dark Mode desenvolvido em Python para automatizar a abertura de túneis TCP/HTTP via Ngrok, agilizando o suporte técnico remoto e o compartilhamento de portas locais.

![Preview da Interface](assets/preview.png)

## 🎯 Problema Resolvido
Durante atendimentos de suporte técnico remoto (como redirecionamento USB/IP, acesso RDP ou testes de servidores locais), configurar túneis via linha de comando e repassar endereços manualmente gera atrito. Este aplicativo centraliza todo o fluxo em um clique: abre o túnel, remove prefixos desnecessários (`tcp://`), copia o endereço automaticamente para a área de transferência e gera o link direto para envio via WhatsApp.

## ✨ Funcionalidades
- **Interface Moderna (Dark UI):** Construída com `CustomTkinter` e indicadores visuais de status em tempo real (`OFFLINE`, `CONECTANDO`, `ONLINE`).
- **Gestão Segura de Credenciais:** Modal dedicado para salvar o `AuthToken` localmente (`config_ngrok.json`) com máscara de segurança, sem expor a chave na tela principal.
- **Formatação Inteligente:** Limpeza automática de prefixos de protocolo para colagem direta em softwares de acesso remoto.
- **Integração com WhatsApp:** Geração automática de mensagem formatada via API oficial (`api.whatsapp.com`), com adição automática de DDI (`55`) para números brasileiros.
- **Arquitetura Modular:** Separação clara entre interface gráfica (`ui.py`), gerenciamento de rede (`tunnel.py`) e configurações (`config.py`).

## 🛠️ Tecnologias Utilizadas
- **Python 3.10+**
- **CustomTkinter** (Interface Gráfica)
- **PyNgrok** (Automação de túneis)
- **Threading** (Execução assíncrona sem travar a interface)
- **PyInstaller** (Empacotamento standalone para Windows)

## 📁 Estrutura do Projeto
```text
wellcatech-ngrok-bridge/
├── assets/
│   ├── icone.ico
│   └── preview.png
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── tunnel.py
│   └── ui.py
├── main.py
├── requirements.txt
└── README.md