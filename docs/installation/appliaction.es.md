# Ejecutar como aplicación de escritorio o aplicación móvil

## Plataformas compatibles

| macOS (x86) | macOS (arm) | Windows | Linux (x86?) | iOS | Android |
| ----------- | ----------- | ------- | ------------ | --- | ------- |
| ✅      | ✅       | llamar para probar | llamar para probar | llamar para probar | llamar para probar |

## Descargar desde GHA

Ir a [enlace](https://github.com/SamYuan1990/i18n-agent-action/actions/workflows/release.yml?query=event%3Aschedule)

Encontrar la última compilación
![](../img/install_step1.png)  

Encontrar tu paquete
![](../img/install_step2.png)  

## Uso

> Mi computadora personal es una Mac x86, así que la usaré como referencia.

1. Descargar e instalar el software.  

> Puedes encontrar problemas de confianza con la firma. Intenta algunas veces si es necesario, o si eras desarrollador `
sudo xattr -d com.apple.quarantine ~/i18n-agent-action.app 
codesign --force --deep --sign - --preserve-metadata=entitlements --options runtime ~/i18n-agent-action.app`
puede ayudar.

2. Configurar una clave API de DeepSeek.  
Por favor, consulta https://api-docs.deepseek.com/zh-cn/ o crea una a través de la plataforma web.  
![](../img/step1.png)  


> Por supuesto, todos también son bienvenidos a usar sus modelos de lenguaje grandes existentes en formato OpenAI para ampliar el alcance de las pruebas.  

3. Configurar la información de acceso del modelo de lenguaje grande y guardarla.  
![](../img/step2.png) 

4. Ingresar el contenido a traducir y hacer clic en "Traducir" para esperar el resultado (nota: la salida de voz está habilitada por defecto).  
![](../img/step3.png) 

5. Característica opcional: Palabras reservadas.  
Volver al Paso 1, agregar palabra reservada y reproducir hasta el paso 4.