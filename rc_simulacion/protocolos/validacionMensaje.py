import hmac, hashlib, json, sys

def firmarMensajeJSON(data: json, secret_key: str) -> dict[str | str]:
  """ 
  Utilizado por EMISOR. Genera un diccionario Python que contiene al string JSON proporcionado y una firma hash de su contenido.

  @param data: Mensaje JSON creado con json.dumps
  @param secret_key: String de llave secreta no hasheada
  @return: Diccionario Python con dos pares clave:valor,
  'data', cuyo valor es el payload/mensaje enviado (sin aplicar encriptación)
  'digest', cuyo valor es un Message Authentication Code (MAC) utilizando cierta función hash (SHA256 por ahora).
  """
  if not (verificarFormatoJSON(data)):
    return
  
  # hmac.new() requiere encoding UTF-8
  data_bytes = data.encode('utf-8')
  secret_key_bytes = secret_key.encode('utf-8')

  mac: hmac = hmac.new(key=secret_key_bytes, 
                        msg=data_bytes, 
                        digestmod=hashlib.sha256)
  
  output = {"data" : data, "digest" : mac.hexdigest()}
  return output

def validarMensaje(data: str, hexdigest: str, secret_key: str) -> bool:
  """
  Utilizado por RECEPTOR, para validar la autenticidad e integridad del mensaje.

  @param data: Mensaje JSON no encriptado recibido
  @param hexdigest: String digest recibida
  @param secret_key: Clave secreta compartida por cliente y servidor
  @return: - True si la MAC calculada por el receptor coincide con la recibida.
  - False en otro caso
  """
  expectedMAC = hmac.new(key=secret_key.encode('utf-8'),
                              msg=data.encode('utf-8'),
                              digestmod=hashlib.sha256)
  
  return hmac.compare_digest(expectedMAC.hexdigest(), hexdigest)

""" Verificar que `msg` está en formato JSON """
def verificarFormatoJSON(msg) -> bool:
  try:
    json.loads(msg)
    return True
  except (ValueError, TypeError, json.JSONDecodeError):
    print(f"Error de firma: Mensaje tiene formato inválido. Mensaje: {msg}", file=sys.stderr)
    return False