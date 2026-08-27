require('dotenv').config();
const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const os = require('os');
const { GoogleGenerativeAI } = require('@google/generative-ai');

// Inicializar Gemini
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

// ==========================================
// INTEGRACIÓN DEL COTIZADOR
// ==========================================
const { handleMessage: handleCotizadorMessage, sessions: cotizadorSessions } = require('./cotizadorFlow');
const { supabase, getCatalog, getQuote, saveQuote } = require('./supabase');
const { generatePDF } = require('./pdfGenerator');

let cotizadorCatalog = {};
getCatalog().then(data => {
    cotizadorCatalog = data;
    console.log("✅ Catálogo del Cotizador cargado desde Supabase.");
}).catch(e => console.error("Error cargando catálogo:", e));

function logWithTime(message) {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('es-MX', { hour12: false });
    console.log(`[${timeStr}] ${message}`);
}

async function processCotizadorAction(client, msg, actionObj) {
    if (actionObj.action === 'REPRINT') {
        try {
            const historicalData = await getQuote(actionObj.folio);
            if (historicalData) {
                const reprintSession = {
                    folio: historicalData.folio,
                    company: historicalData.empresa,
                    name: historicalData.cliente,
                    role: historicalData.role || '', 
                    items: historicalData.productos
                };
                
                let historicalDate = null;
                if (historicalData.fechaCreacion && historicalData.fechaCreacion.toDate) {
                    historicalDate = historicalData.fechaCreacion.toDate();
                }
                
                let priceWarning = false;
                const { getPriceForQuantity } = require('./supabase');
                reprintSession.items.forEach(histItem => {
                    const catItems = cotizadorCatalog[histItem.product];
                    if (catItems) {
                        const currentDim = catItems.find(d => d.dimension === histItem.dimension);
                        if (currentDim) {
                            const currentPrice = getPriceForQuantity(currentDim, histItem.quantity);
                            if (Math.abs(currentPrice - histItem.priceUnit) > 0.01) {
                                priceWarning = true;
                            }
                        }
                    }
                });
                actionObj.priceWarning = priceWarning;
                
                logWithTime(`Generando PDF histórico para ${actionObj.folio}...`);
                const pdfBuffer = await generatePDF(client.pupBrowser, reprintSession, historicalDate);
                
                const base64Pdf = Buffer.isBuffer(pdfBuffer) ? pdfBuffer.toString('base64') : Buffer.from(pdfBuffer).toString('base64');
                const pdfMedia = new MessageMedia('application/pdf', base64Pdf, `Reimpresion_${actionObj.folio}.pdf`);
                
                if (actionObj.priceWarning) {
                    await client.sendMessage(msg.from, `⚠️ *ATENCIÓN:* Los precios de esta cotización están desactualizados respecto al tabulador actual en la base de datos.`);
                }
                
                await client.sendMessage(msg.from, pdfMedia);
                logWithTime(`Reimpresión de ${actionObj.folio} enviada al vendedor.`);
            } else {
                await client.sendMessage(msg.from, `Lo siento, no pude encontrar ninguna cotización con el folio *${actionObj.folio}* en nuestra base de datos.\nEscribe 'Cotizar Placa' para empezar de nuevo.`);
            }
        } catch (err) {
            console.error("Error en la reimpresión:", err);
            await client.sendMessage(msg.from, "Ocurrió un error al buscar la cotización en el servidor. Por favor, intenta de nuevo más tarde.");
        }
    } else if (actionObj.action === 'GENERATE_PDF') {
        const session = actionObj.session;
        const fullDescText = actionObj.descText;
        
        logWithTime("Creando PDF para el vendedor...");
        session.items.forEach(item => item.customDescription = "");
        
        if (fullDescText.toLowerCase() !== 'ninguna' && fullDescText.toLowerCase() !== 'descripción:') {
            const regex = /Descripci[óo]n\s*(\d+)?:/gi;
            let match;
            let lastIndex = -1;
            let lastItemNum = 1;
            const descBlocks = [];
            
            while ((match = regex.exec(fullDescText)) !== null) {
                if (lastIndex !== -1) {
                    descBlocks.push({ itemNum: lastItemNum, text: fullDescText.substring(lastIndex, match.index).trim() });
                }
                lastItemNum = match[1] ? parseInt(match[1]) : 1;
                lastIndex = match.index + match[0].length;
            }
            
            if (lastIndex !== -1) {
                descBlocks.push({ itemNum: lastItemNum, text: fullDescText.substring(lastIndex).trim() });
            } else {
                const simpleText = fullDescText.replace(/^Descripci[óo]n\s*/i, '').trim();
                if (simpleText) descBlocks.push({ itemNum: 1, text: simpleText });
            }
            
            descBlocks.forEach(block => {
                if (block.itemNum >= 1 && block.itemNum <= session.items.length) {
                    session.items[block.itemNum - 1].customDescription = block.text.replace(/\n/g, '<br/>');
                }
            });
        }

        try {
            const pdfBuffer = await generatePDF(client.pupBrowser, session);
            const base64Pdf = Buffer.isBuffer(pdfBuffer) ? pdfBuffer.toString('base64') : Buffer.from(pdfBuffer).toString('base64');
            const pdfMedia = new MessageMedia('application/pdf', base64Pdf, `Cotizacion_${session.company.replace(/[^a-zA-Z0-9]/g, '_')}.pdf`);
            
            await client.sendMessage(msg.from, pdfMedia);
            logWithTime(`PDF enviado exitosamente (Folio: ${session.folio}).`);
            
            await client.sendMessage(msg.from, "Una vez tengas el pdf correcto escribe 'Terminar' para finalizar esta conversación o sigue enviando descripciones para regenerarlo.");
            
            await saveQuote(session, session.company, session.name, session.role, msg.from);
        } catch (err) {
            console.error("Error al generar PDF:", err);
            await client.sendMessage(msg.from, "Hubo un error al generar el PDF.");
        }
    }
}

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

// Firebase removido en favor de Supabase
console.log("✅ Conectado a Supabase correctamente.");

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
const Q_MODELO = '🤖 `¡Hola! Soy tu asistente para crear AGX.`\n\nRecuerda que puedes escribir en cualquier momento:\n`Ayuda` = Obtener ayuda sobre el bot de creación de AGX.\n`Cancelar` = Para cancelar la petición.\n`Regresar` = Para regresar a la pregunta anterior.\n\n¿Qué modelo de terminal usarás?\n\n`1`. 8000\n`2`. 8200\n`3`. Ambos';
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

function resetUserTimeout(user_id, type = 'agx') {
    const isCot = type === 'cotizador';
    const session = isCot ? cotizadorSessions[user_id] : sessions[user_id];
    if (!session) return;
    
    clearUserTimeouts(session);
    
    // Warning at 9 minutes 30 seconds (570,000 ms)
    session.warningTimeout = setTimeout(async () => {
        const currentSession = isCot ? cotizadorSessions[user_id] : sessions[user_id];
        if (currentSession && !currentSession.isPaused) {
            await client.sendMessage(user_id, '🤖 `¿Hola, sigues ahí?`\n\n\n\n_La sesión se cerrará en 30 segundos_');
        }
    }, 570000);
    
    // Cancel at 10 minutes (600,000 ms)
    session.cancelTimeout = setTimeout(async () => {
        const currentSession = isCot ? cotizadorSessions[user_id] : sessions[user_id];
        if (currentSession && !currentSession.isPaused) {
            clearUserTimeouts(currentSession);
            if (isCot) {
                currentSession.state = 'IDLE';
                await client.sendMessage(user_id, '```🛑 Se ha cancelado tu cotización por inactividad. Si deseas volver a empezar, envía: ``` `\'Cotizar Placa\'.`');
            } else {
                delete sessions[user_id];
                await client.sendMessage(user_id, '```🛑 Se ha cancelado tu sesión por inactividad. Si deseas volver a empezar, envía: ``` `\'Solicitar AGX\'.`');
            }
        }
    }, 600000);
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
        '--mute-audio',
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-renderer-backgrounding'
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
        type: 'none'
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

client.on('loading_screen', (percent, message) => {
    console.log(`⌛ Cargando WhatsApp Web... ${percent}% - ${message}`);
});

client.on('authenticated', () => {
    console.log('🔒 Autenticado correctamente con WhatsApp Web.');
});

client.on('auth_failure', msg => {
    console.error('❌ Falló la autenticación con WhatsApp Web:', msg);
});

client.on('ready', () => {
    console.log('✅ Cliente de WhatsApp listo. Escuchando mensajes...');
});

client.on('disconnected', (reason) => {
    console.log('❌ WhatsApp Web fue desconectado. Razón:', reason);
    console.log('🔄 Reiniciando el cliente automáticamente...');
    client.destroy().then(() => {
        client.initialize();
    }).catch(() => {
        client.initialize();
    });
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
        if (msg.hasMedia) return;
        
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
    
    // ------------------------------------------
    // INTERCEPTOR DEL COTIZADOR
    // ------------------------------------------
    const cotizadorTriggers = ['cotizar placa', 'cotizar placas', 'cotizacion de placas', 'cotizacion de placa', 'cotización de placas', 'cotización de placa'];
    const sessionCot = cotizadorSessions[user_id];
    const isCotizadorActive = sessionCot && sessionCot.state !== 'IDLE' && sessionCot.state !== 'QUOTE_FINISHED';
    
    // El usuario también puede entrar con '3' si está eligiendo una acción del menú del cotizador
    const isChoosingCotizadorAction = sessionCot && sessionCot.state === 'CHOOSE_ACTION' && ['1', '2', '3'].includes(bodyLower);
    
    if (cotizadorTriggers.includes(bodyLower) || isCotizadorActive || isChoosingCotizadorAction) {
        if (sessions[user_id] && !isCotizadorActive && !isChoosingCotizadorAction) {
            await client.sendMessage(user_id, "Tienes una solicitud de AGX en curso. Por favor terminala o cancelala escribiendo 'Cancelar' antes de iniciar una cotización.");
            return;
        }

        try {
            let flowResult = await handleCotizadorMessage(msg, cotizadorCatalog);
            let responseText = null;
            let actionObj = null;

            if (typeof flowResult === 'object' && flowResult !== null) {
                responseText = flowResult.text;
                actionObj = flowResult;
            } else {
                responseText = flowResult;
            }
            
            if (responseText) {
                const delayMs = Math.min(Math.max(responseText.length * 30, 1500), 6000);
                setTimeout(async () => {
                    await client.sendMessage(msg.from, responseText);
                    if (actionObj) {
                        await processCotizadorAction(client, msg, actionObj);
                    }
                }, delayMs);
            }
            if (sessionCot && sessionCot.state !== 'IDLE' && sessionCot.state !== 'QUOTE_FINISHED') {
                resetUserTimeout(user_id, 'cotizador');
            } else if (sessionCot && (sessionCot.state === 'IDLE' || sessionCot.state === 'QUOTE_FINISHED')) {
                clearUserTimeouts(sessionCot);
            }
        } catch (e) {
            console.error("Error en flujo del Cotizador:", e);
        }
        return; // Detenemos la ejecución aquí para que el Bot AGX no procese este mensaje
    }

    // ------------------------------------------
    // FLUJO AGX (Soporte y Creación)
    // ------------------------------------------
    if (bodyLower === 'hablar con un humano' || bodyLower === 'humano' || bodyLower === 'soporte') {
        if (sessions[user_id]) {
             sessions[user_id].isPaused = true;
             await client.sendMessage(user_id, '🤖 `He pausado el bot. En breve un humano te atenderá.`');
        }
        return;
    }

    const triggerWords = ['solicitud agx', 'solicitud de agx', 'solicitar agx', 'me ayudas con un agx', 'quisiera pedir un agx', 'solicitarte un agx', 'quisiera pedirte un agx'];
    if (triggerWords.includes(bodyLower)) {
        if (isCotizadorActive || isChoosingCotizadorAction) {
            await client.sendMessage(user_id, "Tienes una cotización en curso. Por favor terminala o cancelala escribiendo 'Cancelar' antes de solicitar un AGX.");
            return;
        }

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
            else if (bodyLower === '2') { session.datos.Modelo = '8200'; session.step = 1; await client.sendMessage(user_id, Q_INVENTARIO); }
            else if (bodyLower === '3' || bodyLower === 'ambos') { session.datos.Modelo = 'Ambos'; session.step = 1; await client.sendMessage(user_id, Q_INVENTARIO); }
            else if (bodyLower === '4' || bodyLower === 'todos' || bodyLower === '8000v2') { session.datos.Modelo = '8000v2'; session.step = 1; await client.sendMessage(user_id, Q_INVENTARIO); }
            else { await client.sendMessage(user_id, '`⚠️ Opción inválida. Responde 1, 2 o 3.`'); }
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
                if (!bodyLower.includes('catalogo')) {
                    await client.sendMessage(user_id, '`⚠️ Tu solicitud requiere un archivo cerrado, pero no indicaste qué dato se va a validar.`\n\nPara los AGX Cerrados, debes especificar qué campo cruzará contra la base de datos agregando la palabra *"Catálogo"*. \n\n*Ejemplo correcto:*\nSKU 1-13 Catálogo\nCantidad 1-5\n\nPor favor, vuelve a enviar tus datos con esta corrección.');
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
                let correctedAllBlocks = [];
                let locBlocks = [];
                let dataBlocks = [];
                
                // Diccionario Maestro (Clon de DICCIONARIO_NOMBRES_CORTOS de Python y otras comunes)
                const diccMaestro = {
                    "fecha de caducidad": "Caducidad", "fecha caducidad": "Caducidad", "fecha de vencimiento": "Caducidad",
                    "vencimiento": "Caducidad", "caducidad": "Caducidad", "cad": "Caducidad",
                    "numero de serie": "Serie", "numero serial": "Serie", "serial number": "Serie", "serie": "Serie", "serial": "Serie",
                    "registro aduanero": "Pedimento", "mercancia importada": "Pedimento", "importacion": "Pedimento", "pedimento": "Pedimento",
                    "numero de matricula": "LPN", "matricula": "LPN", "lpn": "LPN",
                    "codigo de barras": "C.Barras", "codigo de barra": "C.Barras", "barras": "C.Barras", "ean": "EAN", "upc": "C.Barras",
                    "codigo interno": "C.Interno", "codigo cliente": "C.Cliente", "interno": "C.Interno",
                    "descripcion de articulo": "Descrip.", "descripcion": "Descrip.", "descrip": "Descrip.",
                    "id terminal": "Terminal", "ns del scaner": "Scanner", "scanner": "Scanner", "terminal": "Terminal",
                    "numero de caja": "Caja", "caja": "Caja", "cajas": "Caja",
                    "unidades de medida": "U.Medida", "unidad de medida": "U.Medida", "unidad": "U.Medida", "medida": "U.Medida",
                    "codigo de producto": "C.Producto", "producto": "C.Producto",
                    "departamento": "Depto.", "depto": "Depto.",
                    "ubicacion": "Ubicacion", "marbete": "Marbete", "cantidad": "Cantidad",
                    "sku": "SKU", "sap": "SKU", "articulo": "SKU", "item": "SKU", "cve": "SKU",
                    "estado": "Estado", "condicion": "Estado", "estatus": "Estado",
                    "color": "Color", "talla": "Talla", "modelo": "Modelo", "marca": "Marca", "lote": "Lote"
                };
                const dictKeys = Object.keys(diccMaestro);

                let validationErrorMsg = null;

                rawBlocks.forEach(bloqueStr => {
                    let camposCrudos = bloqueStr.split(/\n/).map(f => f.trim()).filter(f => f !== '');
                    let chunkedCampos = [];
                    for (let i = 0; i < camposCrudos.length; i += 6) {
                        chunkedCampos.push(camposCrudos.slice(i, i + 6));
                    }
                    
                    chunkedCampos.forEach(chunk => {
                        let correctedFields = [];
                        let hasLocalizacion = false;
                        
                        chunk.forEach(field => {
                            // 1. Quitar basura del final y puntuacion (El Embudo)
                            let limpio = field.replace(/\s+(con|de|mínimo|minimo|en|a|al|hasta)$/i, '').trim();
                            limpio = limpio.replace(/[;,.\-:]+$/, '').trim();
                            
                            // 2. Extraer parte literal (Nombre) vs parte matemática/catálogo
                            let matchNombre = limpio.match(/^([^0-9:]+)/);
                            if (!matchNombre) {
                                correctedFields.push(limpio);
                                return;
                            }
                            
                            let nombreParte = matchNombre[1].trim();
                            // Strip keywords that might be caught in nombreParte if there are no numbers
                            let strippedNombre = nombreParte.replace(/(?:\s+(catalogo|lookup|prompt|mensaje|bucle|loop|teclado|keypad|lector|reader))+$/i, '').trim();
                            
                            // Si se borró todo (ej. el field era solo "Catálogo"), restauramos nombreParte original para que pase por isReserved
                            if (strippedNombre.length > 0) {
                                // Mover la keyword removida hacia restoStr
                                let removedKeyword = nombreParte.substring(strippedNombre.length).trim();
                                field = field.replace(nombreParte, strippedNombre + " " + removedKeyword);
                                nombreParte = strippedNombre;
                            }
                            
                            // Quitar acentos y a minúsculas
                            let nombreParteLower = nombreParte.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
                            
                            // 3. Mapeo Inteligente
                            let nombreFinal = nombreParte;
                            let bestMatch = stringSimilarity.findBestMatch(nombreParteLower, dictKeys);
                            
                            if (bestMatch.bestMatch.rating > 0.70) {
                                nombreFinal = diccMaestro[bestMatch.bestMatch.target];
                            } else {
                                // Fallbacks
                                if (nombreParteLower.includes("ean")) nombreFinal = "EAN";
                                else nombreFinal = nombreParte.charAt(0).toUpperCase() + nombreParte.slice(1).toLowerCase();
                            }
                            
                            // Verificar Localización
                            if (nombreFinal === "Ubicacion" || nombreFinal === "Marbete") {
                                hasLocalizacion = true;
                            }
                            
                            // 4. Rango y números (Regla "5" -> "5-5")
                            let restoStr = field.substring(nombreParte.length).toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
                            let rangoFinal = "";
                            let rangoMatch = restoStr.match(/(\d+)\s*(?:-|a|al|maximo|máximo)\s*(\d+)/);
                            if (rangoMatch) {
                                rangoFinal = `${rangoMatch[1]}-${rangoMatch[2]}`;
                            } else {
                                let numMatch = restoStr.match(/\b(\d+)\b/);
                                if (numMatch) rangoFinal = `${numMatch[1]}-${numMatch[1]}`;
                            }
                            
                            // 5. Catálogo
                            let sufijoCat = "";
                            let catMatch = restoStr.match(/\b(catalogo)\b(.*)/);
                            if (catMatch) {
                                let argCat = catMatch[2].replace(/[;,.\-:]+$/, '').trim();
                                sufijoCat = argCat ? ` catálogo ${argCat}` : ' catálogo';
                            }
                            
                            // Bucle
                            let hasBucle = /\b(bucle|loop)\b/i.test(restoStr);
                            let suffixBucle = hasBucle ? " bucle" : "";
                            
                            // Prompt y Lookup (Tipos de datos sin longitud)
                            let isPrompt = /\b(prompt|mensaje)\b/i.test(restoStr);
                            let suffixPrompt = isPrompt ? " prompt" : "";
                            
                            let isLookupType = /\b(lookup)\b/i.test(restoStr);
                            let suffixLookup = isLookupType ? " lookup" : "";
                            
                            // Input Type
                            let suffixInput = "";
                            if (/\b(teclado|keypad)\b/i.test(restoStr)) suffixInput = " teclado";
                            else if (/\b(lector|reader)\b/i.test(restoStr)) suffixInput = " lector";
                            
                            // Validación estricta
                            let isCantidad = nombreFinal.toLowerCase() === 'cantidad';
                            let isReserved = ['catalogo', 'lookup', 'prompt', 'mensaje', 'bucle', 'loop', 'teclado', 'keypad', 'lector', 'reader'].includes(nombreParteLower.trim());
                            
                            if (!rangoFinal && !isPrompt && !isCantidad && !isReserved) {
                                validationErrorMsg = `\`⚠️ Faltan datos en:\` *${field}*\n\nRecuerda que cada dato debe especificar su longitud (ej. *1-5*), o bien, un tipo especial como *Prompt* o *Lookup* si no llevan longitud.\n\nPor favor, corrige ese renglón y vuelve a enviar tus datos requeridos completos.`;
                            } else if (sufijoCat && (isPrompt || isLookupType)) {
                                validationErrorMsg = `\`⚠️ Contradicción en:\` *${field}*\n\nNo es posible usar "Catálogo" y "Prompt/Lookup" al mismo tiempo en un mismo renglón, ya que son excluyentes. Por favor, elige solo uno y vuelve a enviar tus datos.`;
                            } else if (isPrompt && isLookupType) {
                                validationErrorMsg = `\`⚠️ Contradicción en:\` *${field}*\n\nNo es posible usar "Prompt" y "Lookup" al mismo tiempo en un mismo renglón. Por favor, elige solo uno y vuelve a enviar tus datos.`;
                            }
                            
                            let finalField = nombreFinal;
                            if (rangoFinal) finalField += ` ${rangoFinal}`;
                            if (sufijoCat) finalField += sufijoCat;
                            if (hasBucle) finalField += ` bucle`;
                            if (isPrompt) finalField += ` prompt`;
                            if (isLookupType) finalField += ` lookup`;
                            if (suffixInput) finalField += suffixInput;
                            
                            correctedFields.push(finalField.trim());
                        });
                        
                        let bloqueCorregidoStr = correctedFields.join('\n');
                        correctedAllBlocks.push(bloqueCorregidoStr);
                        if (hasLocalizacion) locBlocks.push(bloqueCorregidoStr);
                        else dataBlocks.push(bloqueCorregidoStr);
                    });
                });
                
                if (validationErrorMsg) {
                    await client.sendMessage(user_id, validationErrorMsg);
                    return;
                }
                
                session.datos.Datos = correctedAllBlocks.join('\n\n');
                session.pendingData = session.datos; 
                session.step = 5;
                
                // Mostrar resumen visual en WhatsApp
                let datosDibujados = '';
                locBlocks.forEach((b, i) => {
                    let lines = b.split('\n').map(line => `\`${line}\``).join('\n');
                    datosDibujados += `\n📺 *Pantalla Localización ${i + 1}/${locBlocks.length}*\n${lines}\n`;
                });
                dataBlocks.forEach((b, i) => {
                    let lines = b.split('\n').map(line => `\`${line}\``).join('\n');
                    datosDibujados += `\n📺 *Pantalla Datos ${i + 1}/${dataBlocks.length}*\n${lines}\n`;
                });

                let displayTipo = session.datos.Tipo === 'Ambos' ? 'Abierto y Cerrado' : session.datos.Tipo;
                let displayFlujo = session.datos.Flujo === 'Ambos' ? 'Pz x Pz y Volumen' : session.datos.Flujo;
                let displayModelo = session.datos.Modelo === 'Ambos' ? '8000 y 8200' : (session.datos.Modelo === 'Todos' ? '8000, 8000v2 y 8200' : session.datos.Modelo);

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
    
    const modelosAProcesar = parsed.Modelo === 'Ambos' ? ['8000', '8200'] : (parsed.Modelo === 'Todos' ? ['8000', '8000v2', '8200'] : [parsed.Modelo]);
    const tiposAProcesar = parsed.Tipo === 'Ambos' ? ['Abierto', 'Cerrado'] : [parsed.Tipo];

    let reqIndex = 0;
    let cacheMisses = 0;
    for (let i = 0; i < modelosAProcesar.length; i++) {
        const modeloStr = modelosAProcesar[i];
        
        for (let j = 0; j < tiposAProcesar.length; j++) {
            const tipoStr = tiposAProcesar[j];
            reqIndex++;
            const rand = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
            const userPhone = user_id.split('@')[0];
            const id_solicitud = `${userPhone}_${readableDate}_${rand}_${reqIndex}`;

            if (supabase) {
                try {
                    // 1. Buscar en Caché (Ignorando Nombre_AGX / Inventario)
                    const { data: existing, error: searchError } = await supabase
                        .from('AGX')
                        .select('Archivos_AGX')
                        .eq('Modelo_AGX', modeloStr)
                        .eq('Tipo_AGX', tipoStr)
                        .eq('Flujo_AGX', parsed.Flujo)
                        .contains('Datos_AGX', { Variables_Requeridas: parsed.Datos || "" })
                        .in('Status_AGX', ['Finalizado', 'Entregado', 'Entregado (Caché)'])
                        .not('Archivos_AGX', 'is', null)
                        .limit(1);
                    
                    let isCacheHit = false;
                    let cachedArchivos = null;
                    if (existing && existing.length > 0 && existing[0].Archivos_AGX && existing[0].Archivos_AGX.length > 0) {
                        isCacheHit = true;
                        cachedArchivos = existing[0].Archivos_AGX;
                        console.log(`➤ [CACHÉ HIT] Encontrado AGX idéntico para Modelo: ${modeloStr}, Tipo: ${tipoStr}. Enviando desde caché...`);
                    }

                    // 2. Insertar fila en base de datos
                    const statusToInsert = isCacheHit ? 'Entregado (Caché)' : 'Recibido';
                    if (!isCacheHit) cacheMisses++;
                    
                    const { error } = await supabase.from('AGX').insert({
                        Modelo_AGX: modeloStr || "",
                        Nombre_AGX: parsed.Inventario || "",
                        Tipo_AGX: tipoStr || "",
                        Flujo_AGX: parsed.Flujo || "",
                        Datos_AGX: {
                            Variables_Requeridas: parsed.Datos || ""
                        },
                        Status_AGX: statusToInsert,
                        Archivos_AGX: isCacheHit ? cachedArchivos : null,
                        Chat_id: session.chat_id,
                        Mention_id: session.mention_id || null
                    });
                    
                    if (error) throw error;
                    console.log(`➤ Solicitud Híbrida subida a Supabase exitosamente (Modelo: ${modeloStr}, Tipo: ${tipoStr}, Estatus: ${statusToInsert}).`);

                    // 3. Si fue Caché Hit, enviamos el archivo de inmediato al usuario
                    if (isCacheHit) {
                        let msgText = '```✅ ¡AGX recuperado desde Caché exitosamente!```';
                        if (session.mention_id) {
                            msgText = `\`\`\`✅ ¡AGX recuperado desde Caché exitosamente!\`\`\``;
                        }
                        await client.sendMessage(session.chat_id, msgText);
                        await enviarArchivosHelper(client, session.chat_id, cachedArchivos);
                    }

                } catch(e) {
                    console.log('⚠️ Error al interactuar con Supabase:', e.message);
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
            const logLine = `${paddedId}|${fecha}|${hora}|${parsed.Inventario}|${modeloStr}|${tipoStr}|${parsed.Flujo}|N/A|N/A|${datosReq}|${phone}\n`;
            fs.appendFileSync(currentHistorial, logLine);
            
            const fechaStr = new Date().toLocaleString('es-MX', { hour12: false }).replace(', ', '|');
            console.log(`➤ [${fechaStr}] Nueva solicitud Híbrida: "${parsed.Inventario}" para modelo ${modeloStr} y tipo ${tipoStr}`);
        }
    }

    if (cacheMisses > 0) {
        const msgExtra = cacheMisses > 1 ? `\n(Se procesarán ${cacheMisses} plantillas)` : '';
        await client.sendMessage(user_id, '`¡Listo!` ```Solicitud enviada al generador AGX.```' + msgExtra + '\n\n```Todos tus pedidos quedan en fila y se generarán en breve.```');
        
        try {
            const { data: serverState, error } = await supabase.from('configuracion').select('*').eq('id', 'estado_servidor').single();
            let isOffline = true;
            if (serverState && !error) {
                const ultimo_latido = serverState.ultimo_latido || 0;
                const ahora = Date.now() / 1000;
                if (ahora - ultimo_latido <= 180) {
                    isOffline = false;
                }
            }
            if (isOffline) {
                await new Promise(resolve => setTimeout(resolve, 1000));
                await client.sendMessage(user_id, '```⚠️ Nota: El servidor de Sistemas parece estar fuera de línea, pero no te preocupes, tu solicitud quedó en la "fila virtual" y se procesará automáticamente en cuanto vuelva a estar en línea.```');
            }
        } catch (e) {
            console.error("Error al verificar latido del servidor (Supabase):", e.message);
        }
    }

    clearUserTimeouts(sessions[user_id]);
    delete sessions[user_id];
}

async function enviarArchivosHelper(client, chat_id, archivos_agx) {
    if (!archivos_agx || archivos_agx.length === 0) return;
    
    for (let archivo of archivos_agx) {
        let intentos = 0;
        let enviado = false;
        while (!enviado && intentos < 3) {
            try {
                const response = await fetch(archivo.url);
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                const arrayBuffer = await response.arrayBuffer();
                const base64data = Buffer.from(arrayBuffer).toString('base64');
                const mimetype = response.headers.get('content-type') || 'application/x-zip-compressed';
                
                const media = new MessageMedia(mimetype, base64data, archivo.file_name || 'AGX_Generado.zip');
                if (chat_id) await client.sendMessage(chat_id, media, { sendMediaAsDocument: true });
                enviado = true;
            } catch (err_envio) {
                intentos++;
                console.log(`⚠️ Fallo al enviar archivo (intento ${intentos}):`, err_envio.message);
                if (intentos >= 3) {
                    console.log("Abortando envio del archivo.");
                    break; 
                }
                await new Promise(r => setTimeout(r, 5000));
            }
        }
    }
}

client.initialize();

client.on('ready', async () => {
    if (supabase) {
        // Barrido inicial para recuperar archivos 'Finalizados' que no se enviaron por estar offline
        try {
            console.log("🔍 Buscando archivos 'Finalizados' pendientes de envío...");
            const { data: missedRows, error } = await supabase.from('AGX').select('*').eq('Status_AGX', 'Finalizado');
            if (!error && missedRows && missedRows.length > 0) {
                console.log(`📦 Se encontraron ${missedRows.length} envíos pendientes. Procesando...`);
                for (const data of missedRows) {
                    if (data.Archivos_AGX && data.Archivos_AGX.length > 0) {
                        try {
                            let msgText = '```✅ ¡AGX generado exitosamente!```';
                            if (data.Chat_id) await client.sendMessage(data.Chat_id, msgText);
                            await enviarArchivosHelper(client, data.Chat_id, data.Archivos_AGX);
                            await supabase.from('AGX').update({ Status_AGX: 'Entregado' }).eq('AGX_id', data.AGX_id);
                            console.log(`➤ Recuperado y enviado AGX id: ${data.AGX_id}`);
                        } catch (err) {
                            console.log(`❌ Error al recuperar y enviar AGX:`, err.message);
                        }
                    }
                }
            }
        } catch(e) {
            console.error("Error en barrido inicial:", e.message);
        }

        const agxChannel = supabase.channel('agx_updates')
            .on(
                'postgres_changes',
                { event: 'UPDATE', schema: 'public', table: 'AGX', filter: "Status_AGX=eq.Finalizado" },
                async (payload) => {
                    const data = payload.new;
                    if (data.Archivos_AGX && data.Archivos_AGX.length > 0) {
                        const chat_id = data.Chat_id;
                        const mention_id = data.Mention_id;
                        
                        try {
                            let msgText = '```✅ ¡AGX generado exitosamente!```';
                            if (mention_id) {
                                msgText = `\`\`\`✅ ¡AGX generado exitosamente!\`\`\``;
                            }
                            if (chat_id) await client.sendMessage(chat_id, msgText);

                            await enviarArchivosHelper(client, chat_id, data.Archivos_AGX);
                            
                            let fileNames = data.Archivos_AGX.map(a => a.file_name || 'AGX_Generado.zip').join(', ');
                            console.log(`➤ Se enviaron ${data.Archivos_AGX.length} archivos: ${fileNames}`);
                            
                            await supabase.from('AGX').update({ Status_AGX: 'Entregado' }).eq('AGX_id', data.AGX_id);

                        } catch (err) {
                            console.log(`❌ Error al enviar el archivo de vuelta por WhatsApp:`, err.message);
                        }
                    }
                }
            )
            .subscribe((status) => {
                if(status === 'SUBSCRIBED') {
                    console.log("📡 Escuchando respuestas de la PC a través de Supabase Realtime...");
                }
            });
    }
});
