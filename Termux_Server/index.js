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
const HISTORIAL_FILE = './historial_agx.txt';

// Inicializar queue.json si no existe
if (!fs.existsSync(QUEUE_FILE)) {
    fs.writeFileSync(QUEUE_FILE, JSON.stringify([]));
}
// Crear historial si no existe
if (!fs.existsSync(HISTORIAL_FILE)) {
    fs.writeFileSync(HISTORIAL_FILE, "");
}

// ==========================================
// PREGUNTAS DEL FORMULARIO
// ==========================================
const PREGUNTAS = [
    {
        key: '¿QUÉ MODELO DE AGX NECESITAS?',
        msg: '*¿QUÉ MODELO DE AGX NECESITAS?*\n\n1. Modelo 8000\n2. Modelo 8200\n\n_-Responde 1 o 2-_'
    },
    {
        key: 'INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:',
        msg: '*INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:*\n_(Ejemplo: ANFORA, BAJAJ, BIOGRUP, etc.)_'
    },
    {
        key: '¿DE QUÉ TIPO SERÁ?',
        msg: '*¿DE QUÉ TIPO SERÁ?*\n_(Abierto es lo mismo que Forzado)_\n\n1. Abierto\n2. Cerrado\n3. Ambos\n\n_-Responde 1, 2 o 3-_'
    },
    {
        key: 'FLUJO OPERATIVO:',
        msg: '*FLUJO OPERATIVO:*\n_(Tipo de Conteo. En caso de ser Gramaje seleccione Pieza x Pieza)_\n\n1. Pieza x Pieza\n2. Volúmen\n3. Ambos\n\n_-Responde 1, 2 o 3-_'
    },
    {
        key: 'MARBETE Y UBICACIÓN',
        msg: '*MARBETE Y UBICACIÓN*\n\n1. Solo Marbete\n2. Solo Ubicación\n3. Ambos\n\n_-Responde 1, 2 o 3-_'
    },
    {
        key: '¿QUÉ NIVEL DE PRIORIDAD DAREMOS?',
        msg: '*¿QUÉ NIVEL DE PRIORIDAD DAREMOS?*\n_Si los Marbetes tienen muchas Ubicaciones elige "a"._\n_Si las Ubicaciones tienen muchos Marbetes elige "b"._\n_La opción "c" te da la facilidad de registrar ambos en la misma pantalla._\n\na. Primero registrar Marbete y en la pantalla siguiente Ubicación.\n\nb. Primero registrar Ubicación y en la pantalla siguiente Marbetes.\n\nc. Registrar ambos en la misma pantalla.\n\n_-Responde "a", "b" o "c"-_'
    },
    {
        key: 'DATOS REQUERIDOS',
        msg: '*DATOS REQUERIDOS*\n_Ejemplo de Solicitud:_\n\n_Marbete: 5 num_\n_Ubicacion: 3-12_\n_SK: 5-15 alfanum Catálogo_\n_EAN: 3-15 Catálogo_\n_Kilos: 1-6 decimal_\n_Lote: 0-11 alfanum_\n_Cantidad: 1-10_'
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
    args: [
        '--no-sandbox', 
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--no-first-run',
        '--no-zygote',
        '--single-process',
        '--disable-gpu'
    ]
};

// Si estamos probando en Windows, usamos Microsoft Edge nativo
if (os.platform() === 'win32') {
    puppeteerOptions.executablePath = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
} else if (os.platform() === 'linux' || os.platform() === 'android') {
    // Cuando lo pases a Termux, asegúrate de instalar chromium con: pkg install chromium
    puppeteerOptions.executablePath = '/data/data/com.termux/files/usr/bin/chromium-browser';
}

const client = new Client({
    authStrategy: new LocalAuth({
        dataPath: (os.platform() === 'linux' || os.platform() === 'android') 
            ? os.homedir() + '/.wwebjs_auth_bot' 
            : './.wwebjs_auth'
    }),
    puppeteer: puppeteerOptions
});

// ==========================================
// HUMANIZACIÓN DE RESPUESTAS (Anti-Ban Meta)
// ==========================================
const originalSendMessage = client.sendMessage.bind(client);

client.sendMessage = async function(chatId, content, options = {}) {
    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
    const randomDelay = Math.floor(Math.random() * (3000 - 1500 + 1)) + 1500; // Entre 1.5 y 3.0 segundos
    
    try {
        const chat = await this.getChatById(chatId);
        if (chat && chat.sendStateTyping) {
            await chat.sendStateTyping();
        }
    } catch (e) {
        // Ignorar errores al tratar de obtener chat
    }
    
    await sleep(randomDelay);
    return await originalSendMessage(chatId, content, options);
};

client.on('qr', (qr) => {
    console.log('➤ Escanea este código QR con la app de WhatsApp para vincular el bot de Termux:');
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('✅ Cliente de WhatsApp listo. Escuchando mensajes...');
});

client.on('message', async msg => {
    const chat = await msg.getChat();

    // Evitar respuestas de sí mismo
    if (msg.fromMe) return;

    const body = msg.body.trim();
    const bodyLower = body.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    
    // Si viene de un grupo, msg.author tiene el ID del usuario. Si es privado, msg.from tiene el ID del usuario.
    const user_id = msg.author || msg.from;
    const from_chat = msg.from; // El chat original donde se recibió el mensaje (grupo o privado)

    // Comando de inicio (más flexible)
    const triggerWords = ['solicitud agx', 'solicitud de agx', 'solicitar agx', 'me ayudas con un agx', 'quisiera pedir un agx'];
    if (triggerWords.includes(bodyLower)) {
        if (chat.isGroup) {
            // Etiquetar al usuario en el grupo usando su ID directamente
            await chat.sendMessage(`¡Hola @${user_id.split('@')[0]}! Para no hacer spam en este grupo, te he enviado un mensaje privado para iniciar tu solicitud.`, {
                mentions: [user_id]
            });
        }
        
        // Guardar sesión usando el ID privado del usuario, guardando el origen para la entrega final
        sessions[user_id] = { 
            step: 0, 
            answers: {}, 
            chat_id: from_chat, 
            mention_id: chat.isGroup ? user_id : null 
        };
        
        await client.sendMessage(user_id, '🤖 *¡Hola! Bienvenidx al creador de Solicitudes AGX.*\n\nTe haré unas preguntas rápidas.\n_Escribe *"Regresar"* en cualquier momento para corregir, o *"Cancelar"* para abortar)_');
        await client.sendMessage(user_id, PREGUNTAS[0].msg);
        return;
    }

    // El cuestionario siempre transcurre en el chat privado (donde from_chat === user_id)
    // Si el mensaje viene de un grupo (from_chat != user_id), lo ignoramos para el flujo del formulario
    if (chat.isGroup) return;

    // Si el usuario tiene una sesión activa (está en medio del formulario en su chat privado)
    if (sessions[user_id]) {
        const session = sessions[user_id];
        
        if (bodyLower === 'cancelar') {
            delete sessions[user_id];
            await client.sendMessage(user_id, '🛑 Formulario cancelado.');
            return;
        }
        
        if (bodyLower === 'regresar') {
            if (session.step === 0) {
                await client.sendMessage(user_id, '⚠️ Ya estás en la primera pregunta. Si deseas salir, escribe *Cancelar*.');
                return;
            } else {
                session.step -= 1;
                // Si regresamos a la pregunta de prioridad (paso 5), y esa pregunta se había saltado, regresamos una más (al paso 4)
                if (session.step === 5 && session.answers['MARBETE Y UBICACIÓN'] !== 'Ambos') {
                    session.step -= 1; 
                }
                await client.sendMessage(user_id, '🔙 Regresando...\n\n' + PREGUNTAS[session.step].msg);
                return;
            }
        }
        
        const step = session.step;
        const qKey = step < PREGUNTAS.length ? PREGUNTAS[step].key : 'CONFIRMACION';
        let bodyParsed = body;

        if (qKey === 'CONFIRMACION') {
            if (bodyLower === 'a' || bodyLower === 'a.' || bodyLower === 'enviar') {
                // Finalizó el formulario
                session.answers['ESTATUS:'] = 'PENDIENTE';
                session.answers['id_solicitud'] = Date.now().toString();
                session.answers['chat_id'] = session.chat_id; // Fundamental para envío silencioso posterior
                session.answers['mention_id'] = session.mention_id;

                // Guardar en queue.json
                const queueData = JSON.parse(fs.readFileSync(QUEUE_FILE));
                queueData.push(session.answers);
                fs.writeFileSync(QUEUE_FILE, JSON.stringify(queueData, null, 2));

                // Guardar en historial_agx.txt
                let nextId = 1;
                if (fs.existsSync(HISTORIAL_FILE)) {
                    const data = fs.readFileSync(HISTORIAL_FILE, 'utf8').trim().split('\n');
                    if (data.length > 0 && data[0] !== "") {
                        const lastLine = data[data.length - 1];
                        const parts = lastLine.split('|');
                        if (parts.length > 0) {
                            const lastId = parseInt(parts[0], 10);
                            if (!isNaN(lastId)) {
                                nextId = lastId + 1;
                            }
                        }
                    }
                }
                const paddedId = String(nextId).padStart(5, '0');
                const ans = session.answers;
                const inventario = ans['INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:'] || '';
                const modelo = ans['¿QUÉ MODELO DE AGX NECESITAS?'] || '';
                const tipo = ans['¿DE QUÉ TIPO SERÁ?'] || '';
                const conteo = ans['FLUJO OPERATIVO:'] || '';
                const marbete = ans['MARBETE Y UBICACIÓN'] || '';
                const prioridad = (ans['¿QUÉ NIVEL DE PRIORIDAD DAREMOS?'] || '').replace(/\n/g, ' ');
                const datosReq = (ans['DATOS REQUERIDOS'] || '').replace(/\n/g, ' - ');
                const phone = user_id.split('@')[0];
                const fechaRaw = new Date();
                const fecha = fechaRaw.toLocaleDateString('es-MX');
                const hora = fechaRaw.toLocaleTimeString('es-MX', { hour12: false });
                const logLine = `${paddedId}|${fecha}|${hora}|${inventario}|${modelo}|${tipo}|${conteo}|${marbete}|${prioridad}|${datosReq}|${phone}\n`;
                fs.appendFileSync(HISTORIAL_FILE, logLine);

                // Respuesta final
                await client.sendMessage(user_id, '¡Listo! Tu solicitud se ha enviado. El bot la procesará en cuanto el equipo de Sistemas lo Apruebe.');
                
                const fechaStr = new Date().toLocaleString('es-MX', { hour12: false }).replace(', ', '|');
                console.log(`➤ Nueva solicitud enfilada (Inventario: ${session.answers['INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:']}) [${fechaStr}]`);

                // Limpiar sesión
                delete sessions[user_id];
                return;
            } else if (bodyLower === 'b' || bodyLower === 'b.' || bodyLower === 'corregir') {
                session.step -= 1;
                await client.sendMessage(user_id, '🔙 Regresando...\n\n' + PREGUNTAS[session.step].msg);
                return;
            } else if (bodyLower === 'c' || bodyLower === 'c.' || bodyLower === 'cancelar') {
                delete sessions[user_id];
                await client.sendMessage(user_id, '🛑 Formulario cancelado.');
                return;
            } else {
                await client.sendMessage(user_id, '⚠️ Responde solo con a, b o c.');
                return;
            }
        }

        // Mapeo numérico
        if (qKey === '¿QUÉ MODELO DE AGX NECESITAS?') {
            if (body === '1') bodyParsed = '8000';
            else if (body === '2') bodyParsed = '8200';
            else { await client.sendMessage(user_id, '⚠️ Responde solo con 1 o 2.'); return; }
        }
        else if (qKey === '¿DE QUÉ TIPO SERÁ?') {
            if (body === '1') bodyParsed = 'Abierto';
            else if (body === '2') bodyParsed = 'Cerrado';
            else if (body === '3') bodyParsed = 'Ambos';
            else { await client.sendMessage(user_id, '⚠️ Responde solo con 1, 2 o 3.'); return; }
        }
        else if (qKey === 'FLUJO OPERATIVO:') {
            if (body === '1') bodyParsed = 'Pieza x Pieza';
            else if (body === '2') bodyParsed = 'Volumen'; 
            else if (body === '3') bodyParsed = 'Ambos';
            else { await client.sendMessage(user_id, '⚠️ Responde solo con 1, 2 o 3.'); return; }
        }
        else if (qKey === 'MARBETE Y UBICACIÓN') {
            if (body === '1') bodyParsed = 'Solo Marbete';
            else if (body === '2') bodyParsed = 'Solo Ubicación';
            else if (body === '3') bodyParsed = 'Ambos';
            else { await client.sendMessage(user_id, '⚠️ Responde solo con 1, 2 o 3.'); return; }
        }
        else if (qKey === '¿QUÉ NIVEL DE PRIORIDAD DAREMOS?') {
            const low = body.toLowerCase();
            if (low === 'a') bodyParsed = 'Primero registrar Marbete y en la pantalla siguiente Ubicación.';
            else if (low === 'b') bodyParsed = 'Primero registrar Ubicación y en la pantalla siguiente Marbetes.';
            else if (low === 'c') bodyParsed = 'Registrar ambos en la misma pantalla.';
            else { await client.sendMessage(user_id, '⚠️ Responde solo con a, b o c.'); return; }
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
            await client.sendMessage(user_id, PREGUNTAS[session.step].msg);
        } else if (session.step === PREGUNTAS.length) {
            // Mandar los 3 mensajes de confirmación
            const ans = session.answers;
            
            let marbeteUbicacionStr = '';
            if (ans['MARBETE Y UBICACIÓN'] === 'Solo Marbete') marbeteUbicacionStr = 'solo Marbete';
            else if (ans['MARBETE Y UBICACIÓN'] === 'Solo Ubicación') marbeteUbicacionStr = 'solo Ubicación';
            else {
                const prioridad = ans['¿QUÉ NIVEL DE PRIORIDAD DAREMOS?'] || '';
                if (prioridad.includes('Primero registrar Marbete')) {
                    marbeteUbicacionStr = 'Marbete y Ubicación (Primero Marbete)';
                } else if (prioridad.includes('Primero registrar Ubicación')) {
                    marbeteUbicacionStr = 'Marbete y Ubicación (Primero Ubicación)';
                } else {
                    marbeteUbicacionStr = 'Marbete y Ubicación en una pantalla';
                }
            }

            let tipoVisual = ans['¿DE QUÉ TIPO SERÁ?'];
            if (tipoVisual === 'Ambos') tipoVisual = 'Abierto y Cerrado';
            
            let conteoVisual = ans['FLUJO OPERATIVO:'];
            if (conteoVisual === 'Ambos') conteoVisual = 'Pz x Pz y Volumen';

            const msg1 = `Se ha recibido la siguiente información:\n
-Inventario: ${ans['INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:']}
-Modelo: ${ans['¿QUÉ MODELO DE AGX NECESITAS?']}
-Tipo: ${tipoVisual}
-Conteo: ${conteoVisual}
-Con ${marbeteUbicacionStr}`;

            const msg2 = ans['DATOS REQUERIDOS'];
            
            const msg3 = `Revisa bien la información brindada antes de enviarla.

a. Enviar
b. Corregir (regresa a la última pregunta)
c. Cancelar (cancela la petición)`;

            await client.sendMessage(user_id, msg1);
            await client.sendMessage(user_id, msg2);
            await client.sendMessage(user_id, msg3);
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
    const { id_solicitud, chat_id, mention_id, file_base64, file_name } = req.body;
    let queueData = JSON.parse(fs.readFileSync(QUEUE_FILE));
    
    // Enviar el archivo de vuelta a WhatsApp si viene adjunto
    if (file_base64 && chat_id) {
        try {
            const media = new MessageMedia('application/octet-stream', file_base64, file_name || 'AGX_Generado.agx');
            
            let msgText = '✅ Tu solicitud fue aprobada y generada por Sistemas. Aquí tienes tu archivo:';
            let options = {};
            
            if (mention_id) {
                msgText = `✅ @${mention_id.split('@')[0]}, tu solicitud fue aprobada y generada por Sistemas. Aquí tienes tu archivo:`;
                options.mentions = [mention_id];
            }
            
            await client.sendMessage(chat_id, msgText, options);
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
