# app/services/generacion.py

import cohere

# Inicializa el cliente de Cohere
cohere_client = cohere.Client("COHERE_API_KEY")  

def generar_respuesta(fragmentos, pregunta):
    """
    Genera una respuesta usando los fragmentos relevantes y la pregunta.
    Hay que asegurarse de que la respuesta se mantenga dentro del contexto y no se desvíe del tema.
    """
    try:
        # Si los fragmentos están vacíos, evita generar una respuesta incorrecta
        if not fragmentos:
            return "Lo siento, no pude encontrar información relevante para tu pregunta."
        
        # Definir el system prompt con las instrucciones
        system_prompt = """
        Tu tarea es responder preguntas basándote únicamente en la información proporcionada en los textos relevantes.
        Cumple estrictamente con estas reglas:
        1. Responde únicamente en español.
        2. Si no tienes información relevante en los fragmentos proporcionados, responde:
        "Lo siento, no pude encontrar información relevante para tu pregunta."
        3. No inventes información ni respondas sobre temas no relacionados con los textos proporcionados.
        4. Responde exactamente igual ante la misma pregunta. Cada palabra debe ser idéntica.
        5.Usá un lenguaje claro y muy simple para que el usuario pueda entender la informacion de manera sencilla.
        6. Responde lo más breve y preciso posible.
        """

        # Crear el prompt para enviar al LLM
        fragmentos_concatenados = "\n".join(fragmentos)
        prompt = (
            f"{system_prompt}\n\n"
            f"Fragmentos relevantes:\n{fragmentos_concatenados}\n\n"
            f"Pregunta: {pregunta}\n\n"           
            
        )

        # Generar la respuesta con Cohere
        response = cohere_client.generate(
            model="command-r-08-2024", 
            prompt=prompt,
            max_tokens=170,  # Limitar la longitud de la respuesta
            temperature=0.1,  # Respuestas más precisas
        )

        # Procesar y limpiar la respuesta
        respuesta = response.generations[0].text.strip()
        return " ".join(respuesta.split())  # Eliminar saltos de línea y espacios extra
    
    except Exception as e:
        print(f"Error al generar la respuesta: {e}")
        return "Hubo un problema generando la respuesta."
