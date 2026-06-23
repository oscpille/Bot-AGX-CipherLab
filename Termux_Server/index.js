const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const os = require('os');
const { initializeApp, cert } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');

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
// PREGUNTAS DEL FORMULARIO
// ==========================================
const PREGUNTAS = [
    {
        key: '¿QUÉ MODELO DE AGX NECESITAS?',
        msg: '`¿QUÉ MODELO DE AGX NECESITAS?`\n\n1. Modelo 8000\n2. Modelo 8200\n\n_-Responde: `1` o `2`-_'
    },
    {
        key: 'INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:',
        msg: '`INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:`\n\n_(Anfora, BAJAJ, biogrup, etc.)_'
    },
    {
        key: '¿DE QUÉ TIPO SERÁ?',
        msg: '`¿DE QUÉ TIPO SERÁ?`\n\n_(Abierto es lo mismo que Forzado)_\n\n1. Abierto\n2. Cerrado\n3. Ambos\n\n_-Responde: `1`, `2` o `3`-_'
    },
    {
        key: 'FLUJO OPERATIVO:',
        msg: '`FLUJO OPERATIVO:`\n\n_(Tipo de Conteo. En caso de ser Gramaje seleccione Pieza x Pieza)_\n\n1. Pieza x Pieza\n2. Volúmen\n3. Ambos\n\n_-Responde: `1`, `2` o `3`-_'
    },

    {
        key: 'DATOS REQUERIDOS',
        msg: '`DATOS REQUERIDOS`\n\n_Este es un Ejemplo de Solicitud:_\n\n_Ubicación: 3-12_\n_Marbete: 5_\n_Lote: 0-11_\n\n_SKU: 5-15 Catálogo_\n_EAN: 3-15 Catálogo_\n_Kilos: 1-6_\n_Cantidad: 1-10_\n\n_Nota: Puedes separar grupos de pantallas usando un doble salto de línea. Sin embargo ten en cuenta que "Ubicación" y "Marbete" siempre irán cada uno en una pantalla y aparecerá primero el dato que pongas primero._'
    }
];

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
        if (sessions[user_id]) {
            await client.sendMessage(user_id, '🤖 `¿Hola, sigues ahí?`\n\n\n\n_La solicitud se cancelará en 30 segundos_');
        }
    }, 265000);
    
    // Cancel at 5 minutes (300,000 ms)
    session.cancelTimeout = setTimeout(async () => {
        if (sessions[user_id]) {
            clearUserTimeouts(sessions[user_id]);
            delete sessions[user_id];
            await client.sendMessage(user_id, '```🛑 Se ha cancelado tu solicitud por inactividad. Si deseas volver a empezar, envía: ``` `\'Solicitar AGX\'.`');
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
    const triggerWords = ['solicitud agx', 'solicitud de agx', 'solicitar agx', 'me ayudas con un agx', 'quisiera pedir un agx', 'solicitarte un agx', 'quisiera pedirte un agx'];
    if (triggerWords.includes(bodyLower)) {
        if (chat.isGroup) {
            // Etiquetar al usuario en el grupo (solo texto, sin options.mentions) para máxima estabilidad
            await chat.sendMessage(`¡Hola @${user_id.split('@')[0]}! Para no hacer spam en este grupo, te he enviado un mensaje privado para iniciar tu solicitud.`);
        }
        
        if (sessions[user_id]) clearUserTimeouts(sessions[user_id]);
        
        // Guardar sesión usando el ID privado del usuario, guardando el origen para la entrega final
        sessions[user_id] = { 
            step: 0, 
            answers: {}, 
            chat_id: from_chat, 
            mention_id: chat.isGroup ? user_id : null 
        };
        
        resetUserTimeout(user_id);
        
        await client.sendMessage(user_id, '🤖 `Te damos la bienvenida al creador de Solicitudes AGX.`\n\n```Puede escribir en cualquier momento:```\n\n`Cancelar` -> _Para abortar el proceso._\n`Regresar` -> _Para corregir la respuesta anterior._');
        await client.sendMessage(user_id, PREGUNTAS[0].msg);
        return;
    }

    // El cuestionario siempre transcurre en el chat privado (donde from_chat === user_id)
    // Si el mensaje viene de un grupo (from_chat != user_id), lo ignoramos para el flujo del formulario
    if (chat.isGroup) return;

    // Si el usuario tiene una sesión activa (está en medio del formulario en su chat privado)
    if (sessions[user_id]) {
        resetUserTimeout(user_id);
        const session = sessions[user_id];
        
        if (msg.hasMedia) {
            await client.sendMessage(user_id, '`⚠️ Por favor, responde solo con texto.`');
            return;
        }
        
        if (bodyLower === 'cancelar' || bodyLower === 'salir' || bodyLower === 'abortar') {
            clearUserTimeouts(sessions[user_id]);
            delete sessions[user_id];
            await client.sendMessage(user_id, '```🛑 Formulario cancelado.```');
            return;
        }
        
        if (bodyLower === 'regresar') {
            if (session.step === 0) {
                await client.sendMessage(user_id, '```⚠️ Ya estás en la primera pregunta. Si deseas salir, escribe``` `Cancelar`.');
                return;
            } else {
                if (session.awaitingWarning) {
                    session.awaitingWarning = false;
                } else {
                    session.step -= 1;
                }
                await client.sendMessage(user_id, '```🔙 Regresando...```\n\n\n\n' + PREGUNTAS[session.step].msg);
                return;
            }
        }
        
        const step = session.step;
        const qKey = step < PREGUNTAS.length ? PREGUNTAS[step].key : 'CONFIRMACION';
        let bodyParsed = body;

        if (qKey === 'CONFIRMACION') {
            if (bodyLower === 'a' || bodyLower === 'a.' || bodyLower === 'enviar') {
                // Finalizó el formulario
                const ans = session.answers;
                const now = new Date();
                const pad = (n) => n.toString().padStart(2, '0');
                const readableDate = `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())}_${pad(now.getHours())}-${pad(now.getMinutes())}-${pad(now.getSeconds())}`;
                const rand = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
                const id_solicitud = `${readableDate}_${rand}`;

                const documentData = {
                    "1_Estado_de_Orden": {
                        "Estatus": "PENDIENTE",
                        "Fecha_Legible": `${pad(now.getDate())}/${pad(now.getMonth()+1)}/${now.getFullYear()} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`,
                        "Entregado_al_usuario": false
                    },
                    "2_Respuestas_del_Cliente": {
                        "Modelo_AGX": ans['¿QUÉ MODELO DE AGX NECESITAS?'] || "",
                        "Cliente": ans['INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:'] || "",
                        "Tipo": ans['¿DE QUÉ TIPO SERÁ?'] || "",
                        "Flujo_Operativo": ans['FLUJO OPERATIVO:'] || "",
                        "Variables_Requeridas": ans['DATOS REQUERIDOS'] || ""
                    },
                    "3_Metadatos_Internos": {
                        "id_solicitud": id_solicitud,
                        "chat_id": session.chat_id,
                        "mention_id": session.mention_id || null
                    },
                    "ESTATUS": "PENDIENTE"
                };

                // Guardar en Firestore
                if (db) {
                    try {
                        await db.collection('solicitudes').doc(id_solicitud).set(documentData);
                        console.log(`➤ Solicitud ${id_solicitud} subida a Firebase exitosamente.`);
                    } catch(e) {
                        console.log('⚠️ Error al subir a Firebase:', e);
                    }
                }
                
                // Actualizar ans para el historial_agx.txt que lo usa más abajo
                ans['id_solicitud'] = id_solicitud;

                // Guardar en historial rotativo
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
                const inventario = ans['INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:'] || '';
                const modelo = ans['¿QUÉ MODELO DE AGX NECESITAS?'] || '';
                const tipo = ans['¿DE QUÉ TIPO SERÁ?'] || '';
                const conteo = ans['FLUJO OPERATIVO:'] || '';
                const marbete = 'N/A';
                const prioridad = 'N/A';
                const datosReq = (ans['DATOS REQUERIDOS'] || '').replace(/\n/g, ' - ');
                const phone = user_id.split('@')[0];
                const fechaRaw = new Date();
                const fecha = fechaRaw.toLocaleDateString('es-MX');
                const hora = fechaRaw.toLocaleTimeString('es-MX', { hour12: false });
                const logLine = `${paddedId}|${fecha}|${hora}|${inventario}|${modelo}|${tipo}|${conteo}|${marbete}|${prioridad}|${datosReq}|${phone}\n`;
                fs.appendFileSync(currentHistorial, logLine);

                // Respuesta final
                await client.sendMessage(user_id, '`¡Listo!` ```Solicitud enviada.```\n\n```Puedes volver a escribir ``` `Solicitud de AGX` ``` para solicitar un AGX nuevo las veces que quieras. Todos serán agregados a una "fila virtual"```');
                
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
                        await client.sendMessage(user_id, '```⚠️ Nota: El servidor de Sistemas parece estar apagado o fuera de línea. Tu solicitud quedó en la "fila virtual" y se procesará automáticamente en cuanto el sistema regrese.```');
                    }
                } catch (e) {
                    console.error("Error al verificar latido del servidor:", e);
                }
                
                const fechaStr = new Date().toLocaleString('es-MX', { hour12: false }).replace(', ', '|');
                console.log(`➤ [${fechaStr}] Nueva solicitud: "${session.answers['INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:']}"`);

                // Limpiar sesión
                clearUserTimeouts(sessions[user_id]);
                delete sessions[user_id];
                return;
            } else if (bodyLower === 'b' || bodyLower === 'b.' || bodyLower === 'corregir') {
                session.step -= 1;
                await client.sendMessage(user_id, '```🔙 Regresando...```\n\n\n\n' + PREGUNTAS[session.step].msg);
                return;
            } else if (bodyLower === 'c' || bodyLower === 'c.' || bodyLower === 'cancelar') {
                clearUserTimeouts(sessions[user_id]);
                delete sessions[user_id];
                await client.sendMessage(user_id, '```🛑 AGX cancelado.```');
                return;
            } else {
                await client.sendMessage(user_id, '`⚠️ Responde solo con a, b o c.`');
                return;
            }
        }

        // Mapeo numérico
        if (qKey === '¿QUÉ MODELO DE AGX NECESITAS?') {
            if (body === '1') bodyParsed = '8000';
            else if (body === '2') bodyParsed = '8200';
            else { await client.sendMessage(user_id, '`⚠️ Responde solo con 1 o 2.`'); return; }
        }
        else if (qKey === '¿DE QUÉ TIPO SERÁ?') {
            if (body === '1') bodyParsed = 'Abierto';
            else if (body === '2') bodyParsed = 'Cerrado';
            else if (body === '3') bodyParsed = 'Ambos';
            else { await client.sendMessage(user_id, '`⚠️ Responde solo con 1, 2 o 3.`'); return; }
        }
        else if (qKey === 'FLUJO OPERATIVO:') {
            if (body === '1') bodyParsed = 'Pieza x Pieza';
            else if (body === '2') bodyParsed = 'Volumen'; 
            else if (body === '3') bodyParsed = 'Ambos';
            else { await client.sendMessage(user_id, '`⚠️ Responde solo con 1, 2 o 3.`'); return; }
        }
        else if (qKey === 'DATOS REQUERIDOS') {
            if (session.awaitingWarning) {
                if (bodyLower === 'continuar') {
                    bodyParsed = session.tempData;
                    session.awaitingWarning = false;
                } else {
                    const hasLoc = bodyLower.includes('ubicacion') || bodyLower.includes('ubicación') || bodyLower.includes('marbete');
                    if (!hasLoc) {
                        session.tempData = bodyParsed;
                        await client.sendMessage(user_id, '⚠️ Tu AGX sigue sin tener especificada una Ubicación o un Marbete.\n\n¿Deseas *Continuar* así, o enviar los datos corregidos de nuevo? (O escribe *Cancelar*)');
                        return;
                    } else {
                        session.awaitingWarning = false;
                        bodyParsed = body;
                    }
                }
            } else {
                const hasLoc = bodyLower.includes('ubicacion') || bodyLower.includes('ubicación') || bodyLower.includes('marbete');
                if (!hasLoc) {
                    session.awaitingWarning = true;
                    session.tempData = bodyParsed;
                    await client.sendMessage(user_id, '⚠️ Tu AGX no tiene especificada una Ubicación o un Marbete.\n\n¿Deseas *Continuar* así, o prefieres *Regresar* para enviar los datos corregidos?');
                    return;
                }
            }
        }

        // Guardar la respuesta actual
        session.answers[qKey] = bodyParsed;

        // Avanzar al siguiente paso
        session.step += 1;

        if (session.step < PREGUNTAS.length) {
            // Mandar siguiente pregunta
            await client.sendMessage(user_id, PREGUNTAS[session.step].msg);
        } else if (session.step === PREGUNTAS.length) {
            // Mandar los 3 mensajes de confirmación
            const ans = session.answers;
            
            let tipoVisual = ans['¿DE QUÉ TIPO SERÁ?'];
            if (tipoVisual === 'Ambos') tipoVisual = 'Abierto y Cerrado';
            
            let conteoVisual = ans['FLUJO OPERATIVO:'];
            if (conteoVisual === 'Ambos') conteoVisual = 'Pz x Pz y Volumen';

            let reqLines = (ans['DATOS REQUERIDOS'] || '').split('\n');
            let locs = [];
            let dataGroups = [[]];
            
            for (let line of reqLines) {
                let lower = line.trim().toLowerCase();
                if (lower === '') {
                    if (dataGroups[dataGroups.length - 1].length > 0) {
                        dataGroups.push([]);
                    }
                    continue;
                }
                if (lower.includes('ubicacion') || lower.includes('ubicación') || lower.includes('marbete')) {
                    locs.push(line.trim());
                } else {
                    dataGroups[dataGroups.length - 1].push(line.trim());
                }
            }
            if (dataGroups.length > 0 && dataGroups[dataGroups.length - 1].length === 0) {
                dataGroups.pop();
            }
            
            let finalLocs = [];
            let ubic = locs.find(l => l.toLowerCase().includes('ubic'));
            let marb = locs.find(l => l.toLowerCase().includes('marbete'));
            if (ubic) finalLocs.push(ubic);
            if (marb) finalLocs.push(marb);
            if (finalLocs.length === 0) finalLocs = locs; 
            
            let screenText = '`Se ha recibido la siguiente información:`\n\n';
            screenText += `- Inventario: ${ans['INGRESA EL NOMBRE DEL INVENTARIO A TRABAJAR:']}\n`;
            screenText += `- Modelo: ${ans['¿QUÉ MODELO DE AGX NECESITAS?']}\n`;
            screenText += `- Tipo: ${tipoVisual}\n`;
            screenText += `- Conteo: ${conteoVisual}\n`;
            screenText += `- Datos Solicitados x Pantalla:\n`;

            if (finalLocs.length > 0) {
                for (let i = 0; i < finalLocs.length; i++) {
                    screenText += `\`\`\`Pantalla Localización ${i + 1}/${finalLocs.length}:\`\`\`\n- ${finalLocs[i]}`;
                }
            }
            
            let prefix = (ans['FLUJO OPERATIVO:'] === 'Volumen') ? 'Datos Vol' : 'Datos PzxPz';
            if (dataGroups.length > 0) {
                for (let i = 0; i < dataGroups.length; i++) {
                    screenText += `\n\n\`\`\`Pantalla ${prefix} ${i + 1}/${dataGroups.length}:\`\`\`\n`;
                    for (let item of dataGroups[i]) {
                        screenText += `- ${item}\n`;
                    }
                    screenText = screenText.trimEnd();
                }
            }
            
            const msgFinal = `${screenText}\n\n\`Revisa bien la información brindada antes de enviarla:\`\n\n\`a\`. *Enviar*\n\`b\`. *Regresar* _(regresa a la última pregunta)_\n\`c\`. *Cancelar* _(cancela la petición)_`;

            await new Promise(resolve => setTimeout(resolve, 2000));
            await client.sendMessage(user_id, msgFinal);
        }
    }
});

client.initialize();

// ==========================================
// LISTENER EN TIEMPO REAL DE FIREBASE (Reemplaza a Express)
// ==========================================

client.on('ready', () => {
    if (db) {
        db.collection('solicitudes').where('ESTATUS', '==', 'COMPLETADO').onSnapshot((snapshot) => {
            snapshot.docChanges().forEach(async (change) => {
                // Solo actuar si es una solicitud recién terminada por la PC
                if (change.type === 'added' || change.type === 'modified') {
                    const data = change.doc.data();
                    
                    // Si tiene archivos listos y no se han entregado por WhatsApp todavía
                    if (data.archivos && !data.entregado_al_usuario) {
                        const meta = data['3_Metadatos_Internos'] || data;
                    const chat_id = meta.chat_id;
                        const mention_id = meta.mention_id;
                        
                        try {
                            let options = {};
                            let msgText = '```✅ ¡AGX generado exitosamente!```';
                            
                            if (mention_id) {
                                msgText = `\`\`\`✅ ¡AGX generado exitosamente!\`\`\``;
                            }

                            // Enviar el mensaje introductorio usando client.sendMessage (mucho más rápido y no requiere context)
                            await client.sendMessage(chat_id, msgText);

                            // Iterar y enviar cada archivo generado
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
                                            throw err_envio; // Lanza al bloque catch principal
                                        }
                                        await new Promise(r => setTimeout(r, 5000));
                                    }
                                }
                            }
                            
                            let fileNames = data.archivos.map(a => a.file_name || 'AGX_Generado.agx').join(', ');
                            console.log(`➤ Se enviaron ${data.archivos.length} archivos: ${fileNames}`);
                            
                            // Marcar como entregado para que no se reenvíe si se reinicia Termux
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
