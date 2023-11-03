# def calcularMulta(diasAtraso, imprimir):
#   periodoMax = 21
#   multaDiaria = 1
#   multa = 0
#   if diasAtraso <= periodoMax:
#     multa = diasAtraso * multaDiaria
#   logMulta(multa)
#   if imprimir:
#     print(multa)
#   return multa

def calcularCashback(redeX, valor):
  cashback = valor * 0.02
  if redeX :
    cashback = valor * 0.05
  if cashback > 150:
    cashback = 150
  return cashback

print(calcularCashback(True, 3100))