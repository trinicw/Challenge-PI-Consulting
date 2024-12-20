// Configuración del lienzo para el fondo animado
const canvas = document.getElementById('animatedBackground');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const lines = [];
const lineCount = 50;

for (let i = 0; i < lineCount; i++) {
    lines.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        speedX: (Math.random() - 0.5) * 2,
        speedY: (Math.random() - 0.5) * 2,
        length: Math.random() * 100 + 50
    });
}

function drawLines() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = '#ff8c00';
    ctx.lineWidth = 2;

    for (const line of lines) {
        ctx.beginPath();
        ctx.moveTo(line.x, line.y);
        ctx.lineTo(line.x + line.length, line.y + line.length);
        ctx.stroke();

        line.x += line.speedX;
        line.y += line.speedY;

        if (line.x < 0 || line.x > canvas.width) line.speedX *= -1;
        if (line.y < 0 || line.y > canvas.height) line.speedY *= -1;
    }

    requestAnimationFrame(drawLines);
}

drawLines();

// Lógica para enviar consultas a la API FastAPI y mostrar respuestas con efecto de escritura
document.getElementById('queryForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const query = document.getElementById('queryInput').value.trim();
    const responseText = document.getElementById('responseText');

    if (!query) {
        responseText.textContent = 'Por favor, escribe una consulta válida.';
        responseText.style.opacity = '1';
        return;
    }

    responseText.textContent = 'Procesando consulta...';
    responseText.style.opacity = '1';

    try {
        // Realizar la consulta a la API FastAPI
        const response = await fetch('http://127.0.0.1:8000/consulta', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            body: JSON.stringify({ query: query }),
        });

        if (!response.ok) {
            throw new Error(`Error del servidor: ${response.status}`);
        }

        const data = await response.json();
        const respuesta = data.respuesta || 'No se encontró información relevante para tu consulta.';
        mostrarConEfectoEscritura(respuesta);
    } catch (error) {
        responseText.textContent = `Error: ${error.message}`;
        responseText.style.opacity = '1';
    }
});

// Función para mostrar texto con efecto de escritura
function mostrarConEfectoEscritura(texto) {
    const responseText = document.getElementById('responseText');
    responseText.textContent = ''; // Limpia el contenido anterior
    responseText.style.opacity = '1';
    let i = 0;

    function typeEffect() {
        if (i < texto.length) {
            responseText.textContent += texto.charAt(i);
            i++;
            setTimeout(typeEffect, 50); // Controla la velocidad de escritura
        }
    }

    typeEffect();
}
