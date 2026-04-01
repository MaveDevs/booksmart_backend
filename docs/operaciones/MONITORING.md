# Estrategia de Monitoreo - Booksmart Backend

Este documento describe la arquitectura y las herramientas de monitoreo implementadas para el proyecto **Booksmart Backend**, el cual opera en una instancia **EC2** con bases de datos y la aplicación desplegadas mediante contenedores Docker.

Para garantizar la fiabilidad del servicio y facilitar el diagnóstico de problemas tanto en el entorno local (desarrollo) como en la nube de AWS (EC2), se han integrado dos herramientas complementarias: **Sentry** y **Dozzle**.

---

## 1. Monitoreo de Errores y APM: Sentry

Sentry es la herramienta principal encargada del registro de excepciones (Error Tracking) y del Monitoreo del Rendimiento de la Aplicación (APM).

### Justificación de Uso en EC2
- **Detección Activa de Fallos:** En un entorno EC2 de producción, los errores no siempre son reportados por los usuarios. Sentry captura automáticamente cualquier excepción no controlada en FastAPI, guardando el "Stack Trace" completo y las variables de contexto, permitiendo identificar el error exacto antes de que los usuarios se quejen.
- **Rendimiento de los Endpoints (APM):** Permite ver en un panel gráfico si algún endpoint está tomando demasiado tiempo en responder a las consultas hacia MySQL, identificando cuellos de botella sin necesidad de instalar agentes pesados en la máquina EC2 que consuman CPU o RAM.
- **Bajo Consumo de Recursos:** Como procesa y envía los reportes a la nube de manera asíncrona mediante un SDK, el impacto en la latencia del backend es casi cero. 

### ¿Cómo configurarlo e implementarlo?
El proyecto FastAPI (`app.core.monitoring`) ya importa e inicializa la librería oficial de Sentry. Solo se requiere proveer el "DSN" (llave única del proyecto).

1. Crea tu cuenta en [Sentry.io](https://sentry.io/).
2. Crea un proyecto del tipo `FastAPI`.
3. Copia el **DSN** que te proporcionan y agrégalo en tu archivo `.env` en tu servidor EC2 o en local:
   ```env
   SENTRY_DSN=https://<tu_codigo>@sentry.io/<tu_proyecto>
   ```
4. Sentry comenzará a registrar excepciones automáticamente. Puedes cambiar el nivel de muestreo (sample rate) para perfiles y trazas gráficas de rendimiento modificando las variables relacionadas como `SENTRY_TRACES_SAMPLE_RATE` en el mismo `.env`.


---

## 2. Visor de Logs de Contenedores en Tiempo Real: Dozzle

Dozzle es una interfaz web ligera diseñada específicamente para leer y visualizar en tiempo real (stream) los logs de los contenedores Docker en ejecución.

### Justificación de Uso en EC2
- **Diagnóstico Ágil sin Terminal:** Ingresar por SSH a la instancia EC2 para ejecutar `docker compose logs -f api` e intentar leer un sin fin de registros crudos en consola resulta ser ineficiente. Con Dozzle dispones de una web interactiva y rápida para todos los contenedores a la vez.
- **Búsqueda (Search & Filter) Inteligente:** Te permite buscar un texto (como un UUID de error o el nombre de un usuario) a través de todos los logs recientes de manera casi instantánea usando el navegador web.
- **Despreciable Consumo de Recursos:** Al estar diseñado en Go, el contenedor de Dozzle consume muy poca RAM y CPU, lo cual es ideal frente al limitado cómputo de las instancias EC2 compartidas. Además, no requiere persistir datos ni usar bases de datos de logs (como ES/Kibana).

### ¿Cómo configurarlo e implementarlo?
Dozzle solo necesita agregarse como un servicio dentro de nuestro `docker-compose.yml`. (Ya ha sido integrado en los archivos `docker-compose.dev.yml` y de `docker-compose.yml`).

```yaml
  dozzle:
    image: amir20/dozzle:latest
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    ports:
      - "8080:8080"
    restart: unless-stopped
```

1. Para levantarlo ejecuta en local o en tu instancia EC2:
   ```bash
   docker compose up -d
   ```
2. Al iniciar, simplemente accede vía el navegador:
   - **Local:** `http://localhost:8080/`
   - **EC2:** `http://<IP_EC2_o_Dominio>:8080/` 
   *(Asegúrate de configurar los **Security Groups** en el panel de AWS EC2 para permitir tráfico de entrada TCP en el puerto 8080).*

---

### Resumen de la Arquitectura
La dupla funciona como un ciclo cerrado:
1. **Sentry** te avisa asíncronamente (vía alerta, Slack o email) de cuándo ocurrió un error "500" y te muestra la línea de código exacta del fallo.
2. Si el fallo tuvo un origen más oscuro, o quieres inspeccionar la transacción paralela del contenedor, abres la interfaz gráfica de **Dozzle**, localizas los registros (logs) en el Timestamp de dicho error y consigues una radiografía exacta del momento de la anomalía sin conectarte a EC2 por terminal técnica.
