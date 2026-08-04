require('dotenv').config();
const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const os = require('os');
const { initializeApp, cert } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');
const { GoogleGenerativeAI } = require('@google/generative-ai');

// Inicializar Gemini
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
let systemPromptCache = '';
try {
    if (fs.existsSync('../MANUAL_WHATSAPP.txt')) {
        systemPromptCache = fs.readFileSync('../MANUAL_WHATSAPP.txt', 'utf8');
    } else if (fs.existsSync('./MANUAL_WHATSAPP.txt')) {
        systemPromptCache = fs.readFileSync('./MANUAL_WHATSAPP.txt', 'utf8');
    } else {
        console.warn("⚠️ Advertencia: No se encontró MANUAL_WHATSAPP.txt ni en './' ni en '../'. ¡La IA necesita este archivo para saber las reglas!");
    }
} catch (e) {
    console.warn("⚠️ Error al leer MANUAL_WHATSAPP.txt:", e.message);
}

// Inicializar Firebase
try {
    const serviceAccount = require('./firebase_key.json');
    initializeApp({
      credential: cert(serviceAccount)
    });
    console.log("✅ Conectado a Firebase Firestore (Nube de Google).");
} catch(e) {
    console.log("⚠️ Advertencia al conectar a Firebase:", e.message);
}

const db = getFirestore();

function getHistorialFile() {
    const fecha = new Date();
    const mes = String(fecha.getMonth() + 1).padStart(2, '0');
    const anio = fecha.getFullYear();
    const fileName = `./historial_agx_${mes}_${anio}.txt`;
    
    if (!fs.existsSync(fileName)) {
        fs.writeFileSync(fileName, "");
    }
    return fileName;
}

// ==========================================
// PREGUNTAS DEL FORMULARIO HÍBRIDO
// ==========================================
const Q_MODELO = '🤖 `¡Hola! Soy tu asistente para crear AGX.`\n\nRecuerda que puedes escribir en cualquier momento:\n`Ayuda` = Obtener ayuda sobre el bot de creación de AGX.\n`Cancelar` = Para cancelar la petición.\n`Regresar` = Para regresar a la pregunta anterior.\n\n¿Qué modelo de terminal usarás?\n\n`1`. 8000\n`2`. 8000v2\n`3`. 8200\n`4`. Todos';
const Q_INVENTARIO = '¿Cuál es el nombre del Inventario? (Ej. `Soriana`, `Walmart`, `Bodega Aurrera`)';
const Q_TIPO = '¿De qué tipo será?\n_Forzado es igual a Abierto._\n\n`1`. Abierto (Forzado).\n`2`. Cerrado.\n`3`. Ambos.';
const Q_FLUJO = '¿Cuál será el Flujo Operativo (Conteo)?\n\n`1`. Pieza x Pieza.\n`2`. Volumen.\n`3`. Ambos.';
const Q_DATOS = `Finalmente, envíame la lista de Datos Requeridos.

_Nota:_ Si \`Cantidad\` no tiene una longitud definida, siempre se asume un rango de 1-10 numérico y por defecto siempre va incluida en los datos del flujo de Volumen. Para forzar un salto de pantalla en tus datos, simplemente deja un renglón en blanco.

*Ejemplo de cómo enviarlos:*
Ubicación 1-12
Caja 1-5

SKU 5-15 catálogo
Lote 5-20
Estado 1-10

Caducidad 8
Caja 1-5`;

// ==========================================
// MÁQUINA DE ESTADOS (Manejo de Sesiones)
// ==========================================
const sessions = {};

function clearUserTimeouts(session) {
    if (!session) return;
    if (session.warningTimeout) clearTimeout(session.warningTimeout);
    if (session.cancelTimeout) clearTimeout(session.cancelTimeout);
}

function resetUserTimeout(user_id) {
    const session = sessions[user_id];
    if (!session) return;
    
    clearUserTimeouts(session);
    
    // Warning at 4 minutes 25 seconds (265,000 ms)
    session.warningTimeout = setTimeout(async () => {
        if (sessions[user_id] && !sessions[user_id].isPaused) {
            await client.sendMessage(user_id, '🤖 `¿Hola, sigues ahí?`\n\n\n\n_La sesión se cerrará en 30 segundos_');
        }
    }, 265000);
    
    // Cancel at 5 minutes (300,000 ms)
    session.cancelTimeout = setTimeout(async () => {
        if (sessions[user_id] && !sessions[user_id].isPaused) {
            clearUserTimeouts(sessions[user_id]);
            delete sessions[user_id];
            await client.sendMessage(user_id, '```🛑 Se ha cancelado tu sesión por inactividad. Si deseas volver a empezar, envía: ``` `\'Solicitar AGX\'.`');
        }
    }, 300000);
}

// ==========================================
// WHATSAPP CLIENT
// ==========================================

const puppeteerOptions = {
    protocolTimeout: 300000,
    timeout: 300000,
    args: [
        '--no-sandbox', 
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--no-first-run',
        '--disable-gpu',
        '--disable-gpu-compositing',
        '--disable-software-rasterizer',
        '--mute-audio'
    ]
};

// Si estamos probando en Windows, usamos Microsoft Edge nativo
if (os.platform() === 'win32') {
    puppeteerOptions.executablePath = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
} else if (fs.existsSync('/data/data/com.termux/files/usr/bin/chromium-browser')) {
    puppeteerOptions.executablePath = '/data/data/com.termux/files/usr/bin/chromium-browser';
}

const client = new Client({
    authStrategy: new LocalAuth({
        dataPath: (os.platform() === 'linux' || os.platform() === 'android') 
            ? os.homedir() + '/.wwebjs_auth_bot' 
            : './.wwebjs_auth'
    }),
    puppeteer: puppeteerOptions,
    webVersionCache: {
        type: 'remote',
        remotePath: 'https://raw.githubusercontent.com/wppconnect-team/wa-version/main/html/2.2412.54.html',
    }
});

// ==========================================
// HUMANIZACIÓN DE RESPUESTAS Y RASTREO
// ==========================================
const originalSendMessage = client.sendMessage.bind(client);
const botSentTexts = new Set();

client.sendMessage = async function(chatId, content, options = {}) {
    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
    const randomDelay = Math.floor(Math.random() * (3000 - 1500 + 1)) + 1500;
    
    try {
        const chat = await this.getChatById(chatId);
        if (chat && chat.sendStateTyping) {
            await chat.sendStateTyping();
        }
    } catch (e) {}
    
    if (typeof content === 'string') {
        botSentTexts.add(content.trim());
        setTimeout(() => botSentTexts.delete(content.trim()), 30000); 
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

// Usamos message_create para escuchar también nuestros propios mensajes (auto-pausa)
client.on('message_create', async msg => {
    const from_chat = msg.from;
    const to_chat = msg.to;
    const isFromMe = msg.fromMe;
    
    // ------------------------------------------
    // AUTO-PAUSA: Cuando el anfitrión responde manualmente
    // ------------------------------------------
    if (isFromMe) {
        if (typeof msg.body === 'string' && botSentTexts.has(msg.body.trim())) {
            return;
        }

        const target_user_id = to_chat;
        const bodyTrim = (msg.body || '').trim().toLowerCase();
        
        if (sessions[target_user_id]) {
            if (bodyTrim === '/reanudar') {
                sessions[target_user_id].isPaused = false;
                await client.sendMessage(target_user_id, '🤖 `El bot ha reanudado la sesión.`');
            } else if (bodyTrim === '/pausa') {
                sessions[target_user_id].isPaused = true;
            } else if (!sessions[target_user_id].isPaused) {
                sessions[target_user_id].isPaused = true;
                await client.sendMessage(target_user_id, '🤖 `He pausado el bot automáticamente porque un humano está respondiendo.` (Usa /reanudar para volver al bot)');
            }
        }
        return; 
    }

    // ------------------------------------------
    // LÓGICA PRINCIPAL DEL BOT 
    // ------------------------------------------
    const user_id = msg.author || msg.from;
    let chat = null;
    try {
        chat = await msg.getChat();
    } catch (err) {
        console.error("⚠️ Error obteniendo el chat:", err.message);
        // Continuamos sin chat object. Usaremos msg.from para deducir info.
    }
    
    const isGroup = chat ? chat.isGroup : (msg.from && msg.from.includes('@g.us'));
    const body = msg.body.trim();
    const bodyLower = body.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    
    if (bodyLower === 'hablar con un humano' || bodyLower === 'humano' || bodyLower === 'soporte') {
        if (sessions[user_id]) {
             sessions[user_id].isPaused = true;
             await client.sendMessage(user_id, '🤖 `He pausado el bot. En breve un humano te atenderá.`');
        }
        return;
    }

    const triggerWords = ['solicitud agx', 'solicitud de agx', 'solicitar agx', 'me ayudas con un agx', 'quisiera pedir un agx', 'solicitarte un agx', 'quisiera pedirte un agx'];
    if (triggerWords.includes(bodyLower)) {
        if (isGroup) {
            await client.sendMessage(msg.from, `¡Hola @${user_id.split('@')[0]}! Para no hacer spam en este grupo, te he enviado un mensaje privado para iniciar tu solicitud.`);
        }
        
        if (sessions[user_id]) clearUserTimeouts(sessions[user_id]);
        
        sessions[user_id] = { 
            step: 0,
            chat_id: msg.from, 
            mention_id: isGroup ? user_id : null,
            chatHistoryLimpieza: [],
            chatHistoryAyuda: [],
            isPaused: false,
            datos: { Modelo: "", Inventario: "", Tipo: "", Flujo: "", Datos: "" },
            pendingData: null
        };
        
        resetUserTimeout(user_id);
        await client.sendMessage(user_id, Q_MODELO);
        return;
    }

    if (isGroup) return;

    if (sessions[user_id]) {
        if (sessions[user_id].isPaused) return; 
        
        resetUserTimeout(user_id);
        const session = sessions[user_id];
        
        if (msg.hasMedia) {
            await client.sendMessage(user_id, '`⚠️ Por favor, responde solo con texto.`');
            return;
        }

        if (bodyLower === 'cancelar' || bodyLower === 'salir' || bodyLower === 'abortar') {
            clearUserTimeouts(session);
            delete sessions[user_id];
            await client.sendMessage(user_id, '```🛑 Sesión cancelada.```');
            return;
        }

        // ==========================================
        // COMANDO GLOBAL DE AYUDA (IA SOPORTE TÉCNICO)
        // ==========================================
        if (bodyLower.startsWith('ayuda') || bodyLower === 'ayuda') {
            try {
                if (chat && chat.sendStateTyping) await chat.sendStateTyping();
                const modelAyuda = genAI.getGenerativeModel({
                    model: "gemini-2.5-flash",
                    systemInstruction: `Eres soporte técnico para un bot de WhatsApp de creación de AGX.\nUsa este manual para responder la duda del usuario de forma muy breve y concisa (máximo 2 párrafos):\n${systemPromptCache}`
                });
                const chatAyuda = modelAyuda.startChat({
                     history: session.chatHistoryAyuda.map(h => ({role: h.role, parts:[{text: h.text}]}))
                });
                const result = await chatAyuda.sendMessage(body);
                session.chatHistoryAyuda.push({role: 'user', text: body});
                session.chatHistoryAyuda.push({role: 'model', text: result.response.text()});
                
                let resText = `🤖 *Soporte Técnico:*\n${result.response.text().trim()}\n\n_(Volviendo a tu solicitud...)_\n\n`;
                
                if (session.step === 0) resText += Q_MODELO;
                else if (session.step === 1) resText += Q_INVENTARIO;
                else if (session.step === 2) resText += Q_FLUJO;
                else if (session.step === 3) resText += Q_TIPO;
                else if (session.step === 4) resText += Q_DATOS;
                
                await client.sendMessage(user_id, resText);
            } catch (e) {
                console.error(e);
                await client.sendMessage(user_id, '⚠️ `Lo siento, los servidores de Inteligencia Artificial están saturados y no pude cargar la ayuda. Por favor, intenta de nuevo.`');
            }
            return;
        }

        // ==========================================
        // COMANDO GLOBAL DE REGRESAR
        // ==========================================
        if (bodyLower === 'regresar') {
            if (session.step > 0 && session.step < 5) {
                session.step--;
            }
            if (session.step === 0) await client.sendMessage(user_id, Q_MODELO);
            else if (session.step === 1) await client.sendMessage(user_id, Q_INVENTARIO);
            else if (session.step === 2) await client.sendMessage(user_id, Q_FLUJO);
            else if (session.step === 3) await client.sendMessage(user_id, Q_TIPO);
            else if (session.step === 4) await client.sendMessage(user_id, Q_DATOS);
            return;
        }

        // ==========================================
        // MÁQUINA DE ESTADOS (FLUJO PRINCIPAL)
        // ==========================================
        if (session.step === 0) {
            if (bodyLower === '1') { session.datos.Modelo = '8000'; session.step = 1; await client.sendMessage(user_id, Q_INVENTARIO); }
            else if (bodyLower === '2') { session.datos.Modelo = '8000v2'; session.step = 1; await client.sendMessage(user_id, Q_INVENTARIO); }
            else if (bodyLower === '3') { session.datos.Modelo = '8200'; session.step = 1; await client.sendMessage(user_id, Q_INVENTARIO); }
            else if (bodyLower === '4' || bodyLower === 'todos') { session.datos.Modelo = 'Todos'; session.step = 1; await client.sendMessage(user_id, Q_INVENTARIO); }
            else { await client.sendMessage(user_id, '`⚠️ Opción inválida. Responde 1, 2, 3 o 4.`'); }
            return;
        }
        else if (session.step === 1) {
            session.datos.Inventario = msg.body.trim();
            session.step = 2;
            await client.sendMessage(user_id, Q_FLUJO);
            return;
        }
        else if (session.step === 2) {
            if (bodyLower === '1' || bodyLower === 'pieza x pieza' || bodyLower === 'pieza') { session.datos.Flujo = 'Pieza x Pieza'; session.step = 3; await client.sendMessage(user_id, Q_TIPO); }
            else if (bodyLower === '2' || bodyLower === 'volumen') { session.datos.Flujo = 'Volumen'; session.step = 3; await client.sendMessage(user_id, Q_TIPO); }
            else if (bodyLower === '3' || bodyLower === 'ambos') { session.datos.Flujo = 'Ambos'; session.step = 3; await client.sendMessage(user_id, Q_TIPO); }
            else { await client.sendMessage(user_id, '`⚠️ Opción inválida. Responde 1, 2 o 3.`'); }
            return;
        }
        else if (session.step === 3) {
            if (bodyLower === '1' || bodyLower === 'abierto') { session.datos.Tipo = 'Abierto'; session.step = 4; await client.sendMessage(user_id, Q_DATOS); }
            else if (bodyLower === '2' || bodyLower === 'cerrado') { session.datos.Tipo = 'Cerrado'; session.step = 4; await client.sendMessage(user_id, Q_DATOS); }
            else if (bodyLower === '3' || bodyLower === 'ambos') { session.datos.Tipo = 'Ambos'; session.step = 4; await client.sendMessage(user_id, Q_DATOS); }
            else { await client.sendMessage(user_id, '`⚠️ Opción inválida. Responde 1, 2 o 3.`'); }
            return;
        }
        else if (session.step === 4) {
            // ==========================================
            // VALIDACIÓN DE AGX CERRADO
            // ==========================================
            if (session.datos.Tipo === 'Cerrado' || session.datos.Tipo === 'Ambos') {
                if (!bodyLower.includes('lookup') && !bodyLower.includes('catalogo')) {
                    await client.sendMessage(user_id, '`⚠️ Tu solicitud requiere un archivo cerrado, pero no indicaste qué dato se va a validar.`\n\nPara los AGX Cerrados, debes especificar qué campo cruzará contra la base de datos agregando la palabra *"Lookup"* o *"Catálogo"*. \n\n*Ejemplo correcto:*\nUbicación 4-6\nCódigo (Lookup) 1-13\nCantidad 1-5\n\nPor favor, vuelve a enviar tus datos con esta corrección.');
                    return;
                }
            }

            // ==========================================
            // MOTOR NATIVO HÍBRIDO (SIN IA)
            // ==========================================
            try {
                const stringSimilarity = require('string-similarity');
                
                // Separar el texto en Bloques usando doble salto de línea
                let rawBlocks = body.replace(/\r\n/g, '\n').split(/\n\s*\n/).filter(b => b.trim() !== '');
                
                let locBlocks = [];
                let dataBlocks = [];
                let correctedAllBlocks = [];
                
                const palabrasLargas = ['ubicacion', 'marbete', 'cantidad', 'caducidad', 'descripcion', 'pedimento'];
                
                rawBlocks.forEach(bloqueStr => {
                    let camposCrudos = bloqueStr.split(/\n/).map(f => f.trim()).filter(f => f !== '');
                    let chunkedCampos = [];
                    // Dividir arreglos mayores a 6 variables (límite del modelo 8000)
                    for (let i = 0; i < camposCrudos.length; i += 6) {
                        chunkedCampos.push(camposCrudos.slice(i, i + 6));
                    }
                    
                    chunkedCampos.forEach(chunk => {
                        let correctedFields = [];
                        let hasLocalizacion = false;
                        
                        chunk.forEach(field => {
                            let justWords = field.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z\s]/g, "").trim();
                            let words = justWords.split(' ');
                            
                            let correctedWords = words.map(w => {
                                if (w.length >= 6) {
                                    let match = stringSimilarity.findBestMatch(w, palabrasLargas);
                                    if (match.bestMatch.rating > 0.75) return match.bestMatch.target;
                                }
                                return w;
                            });
                            
                            let correctedString = correctedWords.join(' ');
                            let finalField = field;
                            if (correctedString.includes('ubicacion')) finalField = finalField.replace(/[a-zA-ZáéíóúÁÉÍÓÚñÑ]+/, 'Ubicacion');
                            else if (correctedString.includes('marbete')) finalField = finalField.replace(/[a-zA-ZáéíóúÁÉÍÓÚñÑ]+/, 'Marbete');
                            else if (correctedString.includes('caducidad')) finalField = finalField.replace(/[a-zA-ZáéíóúÁÉÍÓÚñÑ]+/, 'Caducidad');
                            else if (correctedString.includes('cantidad')) finalField = finalField.replace(/[a-zA-ZáéíóúÁÉÍÓÚñÑ]+/, 'Cantidad');
                            
                            let matchNum = finalField.match(/^(.+?)\s+(\d+)$/);
                            if (matchNum) {
                                finalField = `${matchNum[1].trim()} ${matchNum[2]}-${matchNum[2]}`;
                            }
                            
                            correctedFields.push(finalField);
                            
                            let checkLower = finalField.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
                            if (checkLower.includes('marbete') || checkLower.includes('ubicacion')) {
                                hasLocalizacion = true;
                            }
                        });
                        
                        let bloqueCorregidoStr = correctedFields.join('\n');
                        correctedAllBlocks.push(bloqueCorregidoStr);
                        
                        if (hasLocalizacion) {
                            locBlocks.push(bloqueCorregidoStr);
                        } else {
                            dataBlocks.push(bloqueCorregidoStr);
                        }
                    });
                });
                
                // Guardar la cadena limpia con dobles saltos de línea para Python
                session.datos.Datos = correctedAllBlocks.join('\n\n');
                session.pendingData = session.datos; 
                session.step = 5;
                
                // Mostrar resumen visual en WhatsApp
                let datosDibujados = '';
                locBlocks.forEach((b, i) => {
                    datosDibujados += `\n📺 *Pantalla Localización ${i + 1}/${locBlocks.length}*\n\`${b}\`\n`;
                });
                dataBlocks.forEach((b, i) => {
                    datosDibujados += `\n📺 *Pantalla Datos ${i + 1}/${dataBlocks.length}*\n\`${b}\`\n`;
                });

                let displayTipo = session.datos.Tipo === 'Ambos' ? 'Abierto y Cerrado' : session.datos.Tipo;
                let displayFlujo = session.datos.Flujo === 'Ambos' ? 'Pz x Pz y Volumen' : session.datos.Flujo;
                let displayModelo = session.datos.Modelo === 'Todos' ? '8000, 8000v2 y 8200' : session.datos.Modelo;

                let screenText = '\`Revisa bien la información recopilada antes de enviarla:\`\n\n';
                screenText += `- \`Inventario:\` ${session.datos.Inventario}\n`;
                screenText += `- \`Modelo:\` ${displayModelo}\n`;
                screenText += `- \`Conteo:\` ${displayFlujo}\n`;
                screenText += `- \`Tipo:\` ${displayTipo}\n`;
                screenText += `- \`Datos Requeridos:\`\n${datosDibujados}\n\n`;
                screenText += `\`a\`. *Enviar*\n\`b\`. *Corregir* _(regresa a los datos requeridos)_\n\`c\`. *Cancelar*`;
                await client.sendMessage(user_id, screenText);
                return;
            } catch(e) {
                console.error("Error en motor nativo híbrido:", e.message);
                await client.sendMessage(user_id, '`⚠️ Ocurrió un error analizando los datos. Asegúrate de enviar la longitud. Ejemplo: Ubicacion 5-10`');
            }

            return;
        }
        else if (session.step === 5) {
            // ==========================================
            // CONFIRMACIÓN FINAL
            // ==========================================
            if (bodyLower === 'a' || bodyLower === 'a.' || bodyLower === 'enviar') {
                await processFinalAGX(user_id, session.pendingData, session);
                return;
            } else if (bodyLower === 'b' || bodyLower === 'b.' || bodyLower === 'corregir') {
                session.step = 4;
                session.chatHistoryLimpieza = []; // Borrar memoria de limpieza al retroceder
                await client.sendMessage(user_id, Q_DATOS);
                return;
            } else if (bodyLower === 'c' || bodyLower === 'c.' || bodyLower === 'cancelar') {
                clearUserTimeouts(session);
                delete sessions[user_id];
                await client.sendMessage(user_id, '```🛑 AGX cancelado.```');
                return;
            } else {
                await client.sendMessage(user_id, '`⚠️ Responde solo con a (Enviar), b (Corregir) o c (Cancelar).`');
                return;
            }
        }
    }
});

async function processFinalAGX(user_id, parsed, session) {
    const now = new Date();
    const pad = (n) => n.toString().padStart(2, '0');
    const readableDate = `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())}_${pad(now.getHours())}-${pad(now.getMinutes())}-${pad(now.getSeconds())}`;
    
    const modelosAProcesar = parsed.Modelo === 'Todos' ? ['8000', '8000v2', '8200'] : [parsed.Modelo];

    for (let i = 0; i < modelosAProcesar.length; i++) {
        const modeloStr = modelosAProcesar[i];
        const rand = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
        const id_solicitud = `${readableDate}_${rand}_${i}`;

        const documentData = {
            "1_Estado_de_Orden": {
                "Estatus": "PENDIENTE",
                "Fecha_Legible": `${pad(now.getDate())}/${pad(now.getMonth()+1)}/${now.getFullYear()} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`,
                "Entregado_al_usuario": false
            },
            "2_Respuestas_del_Cliente": {
                "Modelo_AGX": modeloStr || "",
                "Cliente": parsed.Inventario || "",
                "Tipo": parsed.Tipo || "",
                "Flujo_Operativo": parsed.Flujo || "",
                "Variables_Requeridas": parsed.Datos || ""
            },
            "3_Metadatos_Internos": {
                "id_solicitud": id_solicitud,
                "chat_id": session.chat_id,
                "mention_id": session.mention_id || null
            },
            "ESTATUS": "PENDIENTE"
        };

        if (db) {
            try {
                await db.collection('solicitudes').doc(id_solicitud).set(documentData);
                console.log(`➤ Solicitud Híbrida ${id_solicitud} subida a Firebase exitosamente (Modelo: ${modeloStr}).`);
            } catch(e) {
                console.log('⚠️ Error al subir a Firebase:', e);
            }
        }
        
        let nextId = 1;
        const currentHistorial = getHistorialFile();
        if (fs.existsSync(currentHistorial)) {
            const data = fs.readFileSync(currentHistorial, 'utf8').trim().split('\n');
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
        const datosReq = (parsed.Datos || '').replace(/\n/g, ' - ');
        const phone = user_id.split('@')[0];
        const fechaRaw = new Date();
        const fecha = fechaRaw.toLocaleDateString('es-MX');
        const hora = fechaRaw.toLocaleTimeString('es-MX', { hour12: false });
        const logLine = `${paddedId}|${fecha}|${hora}|${parsed.Inventario}|${modeloStr}|${parsed.Tipo}|${parsed.Flujo}|N/A|N/A|${datosReq}|${phone}\n`;
        fs.appendFileSync(currentHistorial, logLine);
        
        const fechaStr = new Date().toLocaleString('es-MX', { hour12: false }).replace(', ', '|');
        console.log(`➤ [${fechaStr}] Nueva solicitud Híbrida: "${parsed.Inventario}" para modelo ${modeloStr}`);
    }

    const msgExtra = modelosAProcesar.length > 1 ? `\n(Se procesarán ${modelosAProcesar.length} plantillas: ${modelosAProcesar.join(', ')})` : '';
    await client.sendMessage(user_id, '`¡Listo!` ```Solicitud enviada al generador AGX.```' + msgExtra + '\n\n```Todos tus pedidos quedan en fila y se generarán en breve.```');
    
    try {
        const serverState = await db.collection('configuracion').doc('estado_servidor').get();
        let isOffline = true;
        if (serverState.exists) {
            const data = serverState.data();
            const ultimo_latido = data.ultimo_latido || 0;
            const ahora = Date.now() / 1000;
            if (ahora - ultimo_latido <= 180) {
                isOffline = false;
            }
        }
        if (isOffline) {
            await new Promise(resolve => setTimeout(resolve, 1000));
            await client.sendMessage(user_id, '```⚠️ Nota: El servidor de Sistemas Python parece estar fuera de línea. Tu solicitud quedó en la "fila virtual" y se procesará automáticamente en cuanto regrese.```');
        }
    } catch (e) {
        console.error("Error al verificar latido del servidor:", e);
    }

    clearUserTimeouts(sessions[user_id]);
    delete sessions[user_id];
}

client.initialize();

client.on('ready', () => {
    if (db) {
        db.collection('solicitudes').where('ESTATUS', '==', 'COMPLETADO').onSnapshot((snapshot) => {
            snapshot.docChanges().forEach(async (change) => {
                if (change.type === 'added' || change.type === 'modified') {
                    const data = change.doc.data();
                    if (data.archivos && !data.entregado_al_usuario) {
                        const meta = data['3_Metadatos_Internos'] || data;
                        const chat_id = meta.chat_id;
                        const mention_id = meta.mention_id;
                        
                        try {
                            let msgText = '```✅ ¡AGX generado exitosamente!```';
                            if (mention_id) {
                                msgText = `\`\`\`✅ ¡AGX generado exitosamente!\`\`\``;
                            }
                            await client.sendMessage(chat_id, msgText);

                            for (let archivo of data.archivos) {
                                let intentos = 0;
                                let enviado = false;
                                while (!enviado && intentos < 3) {
                                    try {
                                        const media = new MessageMedia('application/octet-stream', archivo.file_base64, archivo.file_name || 'AGX_Generado.agx');
                                        await client.sendMessage(chat_id, media, { sendMediaAsDocument: true });
                                        enviado = true;
                                    } catch (err_envio) {
                                        intentos++;
                                        console.log(`⚠️ Fallo al enviar archivo (intento ${intentos}):`, err_envio.message);
                                        if (intentos >= 3) {
                                            throw err_envio; 
                                        }
                                        await new Promise(r => setTimeout(r, 5000));
                                    }
                                }
                            }
                            
                            let fileNames = data.archivos.map(a => a.file_name || 'AGX_Generado.agx').join(', ');
                            console.log(`➤ Se enviaron ${data.archivos.length} archivos: ${fileNames}`);
                            await change.doc.ref.update({ entregado_al_usuario: true });

                        } catch (err) {
                            console.log(`❌ Error al enviar el archivo devuelta por WhatsApp:`, err);
                        }
                    }
                }
            });
        });
        console.log("📡 Escuchando respuestas de la PC a través de Firebase...");
    }
});
