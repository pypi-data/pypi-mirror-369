# Biblioteca Robot Framework CNPJGenerator

Biblioteca para geração e validação de CNPJs em testes automatizados com Robot Framework.

## Instalação

```bash
pip install robotframework-cnpjgenerator
```

## Uso Básico

```robotframework
*** Settings ***
Library    cnpjgenerator.CNPJGenerator
...    safe_prefixes=12345678,87654321
...    blocked_prefixes=99999999

*** Test Cases ***
Gerar CNPJ Válido
    ${cnpj} =    Generate Safe CNPJ
    ${valid} =    Validate CNPJ    ${cnpj}
    Should Be True    ${valid}
```

## Documentação Completa

[Ver documentação completa](https://seu-usuario.github.io/robotframework-cnpjgenerator/)