const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const express = require('express');
const cors = require('cors');
const fs = require('fs');
const os = require('os');

const app = express();
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ limit: '50mb', extended: true }));

const QUEUE_FILE = './queue.json';

// Inicializar queue.json si no existe
if (!fs.existsSync(QUEUE_FILE)) {
    fs.writeFileSync(QUEUE_FILE, JSON.stringify([]));
}

// ==========================================
// PREGUNTAS DEL FORMULARIO
// ==========================================
const PREGUNTAS = [
    {
        key: '¿QUÉ MODELO DE AGX NECESITAS?',
        msg: '*[1/7] ¿QUÉ MODELO DE AGX NECESITAS?*\n1. Modelo 8000\n2. Modelo 8200\n\n_(Responde 1 o 2)_'
    },
    {
        key: 'INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:',
        msg: '*[2/7] INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:*\n_(Ejemplo: ANFORA, BAJAJ, BIOGRUP, etc. Solo ingresa el nombre de uno)_'
    },
    {
        key: '¿DE QUÉ TIPO SERÁ?',
        msg: '*[3/7] ¿DE QUÉ TIPO SERÁ?*\n_(Abierto es lo mismo que Forzado)_\n1. Abierto\n2. Cerrado\n3. Ambos\n\n_(Responde 1, 2 o 3)_'
    },
    {
        key: 'FLUJO OPERATIVO:',
        msg: '*[4/7] FLUJO OPERATIVO:*\n_(Tipo de Conteo. En caso de ser Gramaje seleccione Pieza x Pieza)_\n1. Pieza x Pieza\n2. Volúmen\n3. Ambos\n\n_(Responde 1, 2 o 3)_'
    },
    {
        key: 'MARBETE Y UBICACIÓN',
        msg: '*[5/7] MARBETE Y UBICACIÓN*\n_(Se trabajarán Marbetes y Ubicación o sólo uno de los dos. En caso de ser ambos seleccione "Ambos")_\n1. Solo Marbete\n2. Solo Ubicación\n3. Ambos\n\n_(Responde 1, 2 o 3)_'
    },
    {
        key: '¿QUÉ NIVEL DE PRIORIDAD DAREMOS?',
        msg: '*[6/7] ¿QUÉ NIVEL DE PRIORIDAD DAREMOS?*\n_(Si los Marbetes tienen muchas Ubicaciones elige "a")_\n_(Si las Ubicaciones tienen muchos Marbetes elige "b")_\n_(La opción "c" te da la facilidad de registrar ambos en la misma pantalla.)_\n\na. Primero registrar Marbete y en la pantalla siguiente Ubicación.\nb. Primero registrar Ubicación y en la pantalla siguiente Marbetes.\nc. Registrar ambos en la misma pantalla.\n\n_(Responde a, b o c)_'
    },
    {
        key: 'DATOS REQUERIDOS',
        msg: '*[7/7] DATOS REQUERIDOS*\n_(Ejemplo de Solicitud:_\n_Marbete: 5 num_\n_Ubicacion: 3-12_\n_SK: 5-15 alfanum Catálogo_\n_EAN: 3-15 Catálogo_\n_Kilos: 1-6 decimal_\n_Lote: 0-11 alfanum_\n_Cantidad: 1-10)_'
    }
];

// ==========================================
// MÁQUINA DE ESTADOS (Manejo de Sesiones)
// ==========================================
const sessions = {};

// ==========================================
// WHATSAPP CLIENT
// ==========================================

const puppeteerOptions = {
    args: ['--no-sandbox', '--disable-setuid-sandbox'] // Necesario para Termux/Linux
};

// Si estamos probando en Windows, usamos Microsoft Edge nativo
if (os.platform() === 'win32') {
    puppeteerOptions.executablePath = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
} else if (os.platform() === 'linux' || os.platform() === 'android') {
    // Cuando lo pases a Termux, asegúrate de instalar chromium con: pkg install chromium
    puppeteerOptions.executablePath = '/data/data/com.termux/files/usr/bin/chromium-browser';
}

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: puppeteerOptions
});

client.on('qr', (qr) => {
    console.log('➤ Escanea este código QR con la app de WhatsApp para vincular el bot de Termux:');
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('✅ Cliente de WhatsApp listo. Escuchando mensajes...');
});

client.on('message', async msg => {
    const chat = await msg.getChat();
    // Evitar grupos por seguridad
    if (chat.isGroup) return;

    // Evitar respuestas de sí mismo
    if (msg.fromMe) return;

    const body = msg.body.trim();
    const bodyLower = body.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    const from = msg.from;

    // Comando de inicio (más flexible)
    const triggerWords = ['solicitud agx', 'solicitud de agx', 'solicitar agx', 'me ayudas con un agx', 'quisiera pedir un agx'];
    if (triggerWords.includes(bodyLower)) {
        sessions[from] = { step: 0, answers: {} };
        await client.sendMessage(from, '🤖 *¡Hola! Bienvenido al creador de Solicitudes AGX.*\nTe haré unas preguntas rápidas.\n_(Escribe *Regresar* en cualquier momento para corregir, o *Cancelar* para abortar)_');
        await client.sendMessage(from, PREGUNTAS[0].msg);
        return;
    }

    // Si el usuario tiene una sesión activa (está en medio del formulario)
    if (sessions[from]) {
        const session = sessions[from];
        
        if (bodyLower === 'cancelar') {
            delete sessions[from];
            await client.sendMessage(from, '🛑 Formulario cancelado.');
            return;
        }
        
        if (bodyLower === 'regresar') {
            if (session.step === 0) {
                await client.sendMessage(from, '⚠️ Ya estás en la primera pregunta. Si deseas salir, escribe *Cancelar*.');
                return;
            } else {
                session.step -= 1;
                // Si regresamos a la pregunta de prioridad (paso 5), y esa pregunta se había saltado, regresamos una más (al paso 4)
                if (session.step === 5 && session.answers['MARBETE Y UBICACIÓN'] !== 'Ambos') {
                    session.step -= 1; 
                }
                await client.sendMessage(from, '🔙 Regresando...\n\n' + PREGUNTAS[session.step].msg);
                return;
            }
        }
        
        const step = session.step;
        const qKey = PREGUNTAS[step].key;
        let bodyParsed = body;

        // Mapeo numérico
        if (qKey === '¿QUÉ MODELO DE AGX NECESITAS?') {
            if (body === '1') bodyParsed = '8000';
            else if (body === '2') bodyParsed = '8200';
            else { await client.sendMessage(from, '⚠️ Responde solo con 1 o 2.'); return; }
        }
        else if (qKey === '¿DE QUÉ TIPO SERÁ?') {
            if (body === '1') bodyParsed = 'Abierto';
            else if (body === '2') bodyParsed = 'Cerrado';
            else if (body === '3') bodyParsed = 'Ambos';
            else { await client.sendMessage(from, '⚠️ Responde solo con 1, 2 o 3.'); return; }
        }
        else if (qKey === 'FLUJO OPERATIVO:') {
            if (body === '1') bodyParsed = 'Pieza x Pieza';
            else if (body === '2') bodyParsed = 'Volumen'; 
            else if (body === '3') bodyParsed = 'Ambos';
            else { await client.sendMessage(from, '⚠️ Responde solo con 1, 2 o 3.'); return; }
        }
        else if (qKey === 'MARBETE Y UBICACIÓN') {
            if (body === '1') bodyParsed = 'Solo Marbete';
            else if (body === '2') bodyParsed = 'Solo Ubicación';
            else if (body === '3') bodyParsed = 'Ambos';
            else { await client.sendMessage(from, '⚠️ Responde solo con 1, 2 o 3.'); return; }
        }
        else if (qKey === '¿QUÉ NIVEL DE PRIORIDAD DAREMOS?') {
            const low = body.toLowerCase();
            if (low === 'a') bodyParsed = 'Primero registrar Marbete y en la pantalla siguiente Ubicación.';
            else if (low === 'b') bodyParsed = 'Primero registrar Ubicación y en la pantalla siguiente Marbetes.';
            else if (low === 'c') bodyParsed = 'Registrar ambos en la misma pantalla.';
            else { await client.sendMessage(from, '⚠️ Responde solo con a, b o c.'); return; }
        }

        // Guardar la respuesta actual
        session.answers[qKey] = bodyParsed;

        // Avanzar al siguiente paso
        session.step += 1;

        // Salto condicional para PRIORIDAD (si en Q5 no eligieron "Ambos")
        if (session.step === 5) {
            if (session.answers['MARBETE Y UBICACIÓN'] !== 'Ambos') {
                session.step += 1;
                session.answers['¿QUÉ NIVEL DE PRIORIDAD DAREMOS?'] = '';
            }
        }

        if (session.step < PREGUNTAS.length) {
            // Mandar siguiente pregunta
            await client.sendMessage(from, PREGUNTAS[session.step].msg);
        } else {
            // Finalizó el formulario
            session.answers['ESTATUS:'] = 'PENDIENTE';
            session.answers['id_solicitud'] = Date.now().toString();
            session.answers['chat_id'] = from; // Fundamental para envío silencioso posterior

            // Guardar en queue.json
            const queueData = JSON.parse(fs.readFileSync(QUEUE_FILE));
            queueData.push(session.answers);
            fs.writeFileSync(QUEUE_FILE, JSON.stringify(queueData, null, 2));

            // Respuesta final
            await client.sendMessage(from, '¡Listo! Tu solicitud se ha enviado. El bot la procesará en cuanto el equipo de Sistemas lo Apruebe.');
            
            const fechaStr = new Date().toLocaleString('es-MX', { hour12: false }).replace(', ', '|');
            console.log(`➤ Nueva solicitud enfilada (Inventario: ${session.answers['INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:']}) [${fechaStr}]`);

            // Limpiar sesión
            delete sessions[from];
        }
    }
});

client.initialize();

// ==========================================
// SERVIDOR API REST
// ==========================================

// Obtener todas las solicitudes pendientes
app.get('/queue', (req, res) => {
    const queueData = JSON.parse(fs.readFileSync(QUEUE_FILE));
    res.json(queueData);
});

// Borrar una solicitud específica Y enviar el archivo devuelta
const { MessageMedia } = require('whatsapp-web.js');

app.post('/queue/complete', async (req, res) => {
    const { id_solicitud, chat_id, file_base64, file_name } = req.body;
    let queueData = JSON.parse(fs.readFileSync(QUEUE_FILE));
    
    // Enviar el archivo de vuelta a WhatsApp si viene adjunto
    if (file_base64 && chat_id) {
        try {
            const media = new MessageMedia('application/octet-stream', file_base64, file_name || 'AGX_Generado.agx');
            await client.sendMessage(chat_id, '✅ Tu solicitud fue aprobada y generada por Sistemas. Aquí tienes tu archivo:');
            await client.sendMessage(chat_id, media);
            console.log(`📤 Archivo enviado silenciosamente al chat: ${chat_id}`);
        } catch (err) {
            console.log(`❌ Error al enviar el archivo de vuelta: ${err.message}`);
        }
    }

    // Filtrar y eliminar la solicitud procesada
    queueData = queueData.filter(item => item.id_solicitud !== id_solicitud);
    
    fs.writeFileSync(QUEUE_FILE, JSON.stringify(queueData, null, 2));
    console.log(`✅ Solicitud ${id_solicitud} completada y removida de la cola.`);
    
    res.json({ success: true, message: "Removido de la cola y enviado" });
});

const PORT = 3000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`\n🚀 Servidor API escuchando en http://0.0.0.0:${PORT}`);
    console.log(`   Ruta GET:  http://[TU-IP]:${PORT}/queue`);
    console.log(`   Ruta POST: http://[TU-IP]:${PORT}/queue/complete`);
});
