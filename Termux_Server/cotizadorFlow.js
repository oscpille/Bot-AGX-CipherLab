const { getPriceForQuantity } = require('./supabase');
const fs = require('fs');
const path = require('path');

const clientesPath = path.join(__dirname, 'clientes.json');

function loadClients() {
    try {
        if (fs.existsSync(clientesPath)) {
            return JSON.parse(fs.readFileSync(clientesPath, 'utf8'));
        }
    } catch (e) {
        console.error("Error loading clientes.json", e);
    }
    return {};
}

function saveClient(from, company, name, role) {
    const clients = loadClients();
    clients[from] = { company, name, role };
    try {
        fs.writeFileSync(clientesPath, JSON.stringify(clients, null, 2));
    } catch (e) {
        console.error("Error saving clientes.json", e);
    }
}

const sessions = {};

// Constantes de estados
const STATES = {
    IDLE: 'IDLE',
    CHOOSE_ACTION: 'CHOOSE_ACTION',
    ASK_REPRINT_FOLIO: 'ASK_REPRINT_FOLIO',
    ASK_REPRINT_METHOD: 'ASK_REPRINT_METHOD',
    ASK_COMPANY_SEARCH: 'ASK_COMPANY_SEARCH',
    SELECT_REPRINT_OPTION: 'SELECT_REPRINT_OPTION',
    CONFIRM_SAVED_DATA: 'CONFIRM_SAVED_DATA',
    ENTER_CLIENT_DATA: 'ENTER_CLIENT_DATA',
    SELECT_PRODUCT: 'SELECT_PRODUCT',
    SELECT_DIMENSION: 'SELECT_DIMENSION',
    ENTER_QUANTITY: 'ENTER_QUANTITY',
    ASK_ADD_ANOTHER: 'ASK_ADD_ANOTHER',
    CONFIRM_CANCEL_ADD: 'CONFIRM_CANCEL_ADD',
    WAITING_FOR_DESCRIPTION: 'WAITING_FOR_DESCRIPTION',
    QUOTE_FINISHED: 'QUOTE_FINISHED',
    ASK_ADMIN_PASSWORD: 'ASK_ADMIN_PASSWORD',
    ADMIN_SELECT_PRODUCT: 'ADMIN_SELECT_PRODUCT',
    ADMIN_SELECT_DIMENSION: 'ADMIN_SELECT_DIMENSION',
    ADMIN_ENTER_PRICE: 'ADMIN_ENTER_PRICE'
};

function getSession(from) {
    if (!sessions[from]) {
        sessions[from] = { state: STATES.IDLE, items: [], product: null, dimension: null, company: null, name: null, role: null, folio: null, timer: null, searchResults: [] };
    }
    return sessions[from];
}

function resetSession(from) {
    if (sessions[from] && sessions[from].timer) {
        clearTimeout(sessions[from].timer);
    }
    sessions[from] = { state: STATES.IDLE, items: [], product: null, dimension: null, company: null, name: null, role: null, folio: null, timer: null };
}

async function handleMessage(msg, catalog) {
    const from = msg.from;
    const text = msg.body.trim();
    const lowerText = text.toLowerCase();
    const cleanText = text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
    const triggers = ["cotizar placa", "cotizar placas", "cotizacion de placas", "cotizacion de placa"];
    const session = getSession(from);

    // Cancelar en cualquier momento
    if (lowerText === 'cancelar') {
        if (session.items && session.items.length > 0 && session.state !== STATES.QUOTE_FINISHED) {
            session.state = STATES.CONFIRM_CANCEL_ADD;
            return "¿Deseas cotizar únicamente los productos anteriormente enlistados?\n1. Sí\n2. No";
        }
        resetSession(from);
        return "Operación cancelada. Puedes escribir 'Cotizar Placa' cuando quieras empezar de nuevo.";
    }

    // Terminar cotización cuando se envían descripciones
    if (lowerText === 'terminar') {
        if (session.state === STATES.WAITING_FOR_DESCRIPTION) {
            session.state = STATES.IDLE;
            return "¡Cotización finalizada! Que tengas un excelente día.";
        } else {
            return "No hay ninguna cotización lista para terminar. Usa 'cancelar' si deseas salir.";
        }
    }

    // Regresar al paso anterior
    if (lowerText === 'regresar') {
        switch (session.state) {
            case STATES.IDLE: 
            case STATES.CHOOSE_ACTION:
                return "Ya estás al inicio. Escribe 'Cotizar Placa' para empezar.";
            case STATES.CONFIRM_SAVED_DATA:
            case STATES.ASK_REPRINT_METHOD:
            case STATES.ASK_REPRINT_FOLIO:
            case STATES.ASK_COMPANY_SEARCH:
            case STATES.SELECT_REPRINT_OPTION:
            case STATES.ENTER_CLIENT_DATA:
            case STATES.ASK_ADMIN_PASSWORD:
            case STATES.ADMIN_SELECT_PRODUCT:
            case STATES.ADMIN_SELECT_DIMENSION:
            case STATES.ADMIN_ENTER_PRICE: 
                session.state = STATES.CHOOSE_ACTION;
                return "Regresando...\n¿Qué deseas hacer?\n1. Nueva cotización\n2. Reimprimir cotización";
            case STATES.SELECT_PRODUCT:
                session.state = STATES.ENTER_CLIENT_DATA; 
                return "Regresando... Por favor indícame en **un solo mensaje de 3 líneas**:\n1. Empresa\n2. Nombre\n3. Puesto";
            case STATES.SELECT_DIMENSION: 
                session.state = STATES.SELECT_PRODUCT; 
                const products = Object.keys(catalog);
                let responseProd = "Regresando... ¿Qué producto deseas cotizar?\nResponde con el número de la opción:\n\n";
                products.forEach((prod, index) => { responseProd += `${index + 1}. ${prod}\n`; });
                return responseProd;
            case STATES.ENTER_QUANTITY:
                session.state = STATES.SELECT_DIMENSION;
                const dimensions = catalog[session.product].map(i => i.dimension);
                let responseDim = `Regresando a producto *${session.product}*.\n¿Qué dimensión necesitas? Responde con el número:\n\n`;
                dimensions.forEach((dim, index) => { responseDim += `${index + 1}. ${dim}\n`; });
                return responseDim;
            case STATES.ASK_ADD_ANOTHER:
                session.state = STATES.ENTER_QUANTITY;
                session.items.pop();
                return `Regresando... ¿Cuántas piezas necesitas cotizar para *${session.product}* (${session.dimension})?`;
            case STATES.CONFIRM_CANCEL_ADD:
                session.state = STATES.ASK_ADD_ANOTHER;
                return `¿Deseas agregar otro producto a esta cotización o procedemos a generarla?\n1. Agregar otro producto.\n2. Generar cotización.`;
            default:
                return null;
        }
    }

    switch (session.state) {
        case STATES.IDLE:
        case STATES.QUOTE_FINISHED:
            if (triggers.includes(cleanText)) {
                if (session.timer) clearTimeout(session.timer);
                session.state = STATES.CHOOSE_ACTION;
                session.items = []; // Limpiamos ítems anteriores por si venimos de QUOTE_FINISHED
                return "¡Hola! ¿Qué deseas hacer?\n1. Nueva cotización\n2. Reimprimir cotización";
            }
            break;

        case STATES.CHOOSE_ACTION:
            if (lowerText === '1' || lowerText === '1.' || lowerText === 'nueva') {
                const clients = loadClients();
                const savedData = clients[from];
                if (savedData) {
                    session.company = savedData.company;
                    session.name = savedData.name;
                    session.role = savedData.role;
                    session.state = STATES.CONFIRM_SAVED_DATA;
                    return `¿Seguiremos usando los datos guardados?\n\n* Empresa: ${savedData.company}\n* Nombre: ${savedData.name}\n* Puesto: ${savedData.role}\n\n1. Continuar con estos datos\n2. Editarlos nuevamente`;
                } else {
                    session.state = STATES.ENTER_CLIENT_DATA;
                    return "Para iniciar con tu cotización, por favor indícame en **un solo mensaje de 3 líneas** los siguientes datos (separados por un salto de línea):\n1. Nombre de la empresa\n2. Nombre del cliente\n3. Puesto del comprador";
                }
            } else if (lowerText === '2' || lowerText === '2.' || lowerText === 'reimprimir') {
                session.state = STATES.ASK_REPRINT_METHOD;
                return "¿Cómo deseas buscar la cotización a reimprimir?\n1. Por Folio Exacto (Ej: COT-123456)\n2. Buscar por Nombre de Empresa";
            } else if (lowerText === '3' || lowerText === '3.') {
                session.state = STATES.ASK_ADMIN_PASSWORD;
                return "🔐 Has ingresado al Panel de Administración.\n\nPor favor, ingresa la contraseña de 4 dígitos para continuar, o escribe 'cancelar'.";
            } else {
                return "Por favor responde '1' para Nueva cotización, '2' para Reimprimir cotización, o '3' para el Panel de Administrador.";
            }

        case STATES.ASK_ADMIN_PASSWORD:
            if (text === '2468') {
                session.state = STATES.ADMIN_SELECT_PRODUCT;
                let response = "🔓 Contraseña correcta.\n\n¿A qué producto le deseas cambiar el precio base?\nSelecciona el número correspondiente:\n\n";
                const products = Object.keys(catalog);
                products.forEach((prod, index) => {
                    response += `${index + 1}. ${prod}\n`;
                });
                return response;
            } else {
                return "❌ Contraseña incorrecta. Intenta nuevamente o escribe 'cancelar'.";
            }

        case STATES.ADMIN_SELECT_PRODUCT:
            const adminProductsList = Object.keys(catalog);
            const selectedProdIdx = parseInt(text) - 1;
            if (!isNaN(selectedProdIdx) && selectedProdIdx >= 0 && selectedProdIdx < adminProductsList.length) {
                const selectedProduct = adminProductsList[selectedProdIdx];
                session.adminProduct = selectedProduct; // Guardamos temporalmente
                
                let response = `Has seleccionado *${selectedProduct}*.\n\n¿A qué dimensión le aplicarás el cambio?\n\n`;
                const dimensions = catalog[selectedProduct];
                dimensions.forEach((dimObj, idx) => {
                    response += `${idx + 1}. ${dimObj.dimension} (Actual: $${dimObj.basePrice.toLocaleString('es-MX', {minimumFractionDigits: 2})})\n`;
                });
                session.state = STATES.ADMIN_SELECT_DIMENSION;
                return response;
            } else {
                return "Opción inválida. Selecciona un número de la lista.";
            }

        case STATES.ADMIN_SELECT_DIMENSION:
            const dims = catalog[session.adminProduct];
            const selDimIdx = parseInt(text) - 1;
            if (!isNaN(selDimIdx) && selDimIdx >= 0 && selDimIdx < dims.length) {
                const selectedDim = dims[selDimIdx];
                session.adminDimension = selectedDim.dimension;
                session.adminOldPrice = selectedDim.basePrice;
                
                session.state = STATES.ADMIN_ENTER_PRICE;
                return `El precio base actual de *${session.adminProduct} (${selectedDim.dimension})* es de *$${selectedDim.basePrice.toLocaleString('es-MX', {minimumFractionDigits: 2})}*.\n\nPor favor, ingresa el **NUEVO PRECIO BASE** (sólo números, puedes usar decimales. Ej: 7.50):`;
            } else {
                return "Opción inválida. Selecciona un número de la lista.";
            }

        case STATES.ADMIN_ENTER_PRICE:
            const newPrice = parseFloat(text.replace(/[^0-9.]/g, ''));
            if (!isNaN(newPrice) && newPrice > 0) {
                const { updateBasePrice, getCatalog } = require('./supabase');
                try {
                    // Actualizamos en base de datos
                    await updateBasePrice(session.adminProduct, session.adminDimension, newPrice);
                    // Actualizamos el objeto en memoria actual (aunque el index debería recargarlo para ser perfecto, pero con modificar catalog en memoria basta por ahora)
                    const catalogItem = catalog[session.adminProduct].find(d => d.dimension === session.adminDimension);
                    if(catalogItem) catalogItem.basePrice = newPrice;
                    
                    session.state = STATES.IDLE;
                    return `✅ ¡Éxito! El precio de *${session.adminProduct} (${session.adminDimension})* se actualizó correctamente de $${session.adminOldPrice} a **$${newPrice.toLocaleString('es-MX', {minimumFractionDigits: 2})}**.\n\nLa tabla de tabuladores se ha recalculado automáticamente en la nube.`;
                } catch(e) {
                    console.error("Error al actualizar precio:", e);
                    return "❌ Hubo un error al guardar el precio en la base de datos.";
                }
            } else {
                return "Por favor ingresa un número válido mayor a 0.";
            }

        case STATES.ASK_REPRINT_METHOD:
            if (lowerText === '1' || lowerText === '1.') {
                session.state = STATES.ASK_REPRINT_FOLIO;
                return "Por favor, ingrese los caracteres de su Folio después del guión.\n(Por ejemplo, si su folio era COT-A8F3X1, ingrese solo A8F3X1)";
            } else if (lowerText === '2' || lowerText === '2.') {
                session.state = STATES.ASK_COMPANY_SEARCH;
                return "Por favor, ingresa el nombre (o parte del nombre) de la empresa a buscar:";
            } else {
                return "Responde '1' para buscar por Folio o '2' para buscar por Empresa.";
            }

        case STATES.ASK_COMPANY_SEARCH:
            if (text.length < 2) return "Por favor, ingresa al menos 2 caracteres para buscar.";
            
            // Retornamos un mensaje de espera que será reemplazado cuando la búsqueda termine
            const { searchQuotesByCompany } = require('./firebase');
            try {
                const results = await searchQuotesByCompany(text);
                if (results.length === 0) {
                    return `No encontré cotizaciones recientes para la empresa "${text}". Escribe otro nombre para buscar, o escribe 'cancelar'.`;
                }
                
                session.searchResults = results;
                session.state = STATES.SELECT_REPRINT_OPTION;
                
                let responseList = `Se encontraron las siguientes cotizaciones para "${text}":\n\n`;
                results.forEach((r, idx) => {
                    const dateStr = r.fechaCreacion && r.fechaCreacion.toDate ? r.fechaCreacion.toDate().toLocaleDateString('es-MX') : 'Fecha desconocida';
                    responseList += `${idx + 1}. ${r.folio} - ${r.empresa} (${dateStr})\n`;
                });
                responseList += "\nPor favor, responde con el número de la cotización que deseas reimprimir (Ej: 1).";
                
                return responseList;
            } catch (error) {
                console.error("Error buscando empresa:", error);
                return "Ocurrió un error al buscar en la base de datos. Escribe 'cancelar'.";
            }
            
        case STATES.SELECT_REPRINT_OPTION:
            const selectedIdx = parseInt(text) - 1;
            if (!isNaN(selectedIdx) && selectedIdx >= 0 && selectedIdx < session.searchResults.length) {
                const selectedQuote = session.searchResults[selectedIdx];
                session.state = STATES.IDLE;
                return {
                    text: `Reimprimiendo la cotización ${selectedQuote.folio}, por favor espera un momento...`,
                    action: 'REPRINT',
                    folio: selectedQuote.folio
                };
            } else {
                return "Número inválido. Por favor, selecciona un número de la lista o escribe 'cancelar'.";
            }

        case STATES.ASK_REPRINT_FOLIO:
            const digitsMatch = text.match(/[A-Za-z0-9]+/);
            if (digitsMatch) {
                const digits = digitsMatch[0].toUpperCase();
                const searchFolio = `COT-${digits}`;
                session.state = STATES.IDLE; 
                return {
                    text: `Buscando la cotización ${searchFolio} en la nube, por favor espera un momento...`,
                    action: 'REPRINT',
                    folio: searchFolio
                };
            } else {
                return "Formato inválido. Por favor ingrese solo los caracteres de su folio (ej: A8F3X1) o escriba 'cancelar'.";
            }

        case STATES.CONFIRM_SAVED_DATA:
            if (lowerText === '1' || lowerText === '1.') {
                const products = Object.keys(catalog);
                let response = "¡Perfecto! ¿Qué producto deseas cotizar?\nResponde con el número de la opción:\n\n";
                products.forEach((prod, index) => {
                    response += `${index + 1}. ${prod}\n`;
                });
                session.state = STATES.SELECT_PRODUCT;
                return response;
            } else if (lowerText === '2' || lowerText === '2.') {
                session.company = null;
                session.name = null;
                session.role = null;
                session.state = STATES.ENTER_CLIENT_DATA;
                return "De acuerdo. Por favor indícame en **un solo mensaje de 3 líneas** los siguientes datos (separados por un salto de línea):\n1. Empresa\n2. Nombre\n3. Puesto";
            } else {
                return "Por favor responde '1' para continuar con los datos guardados o '2' para editarlos.";
            }

        case STATES.ENTER_CLIENT_DATA:
            const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0);
            if (lines.length !== 3) {
                return "Formato incorrecto. Deben ser exactamente 3 datos separados por saltos de línea.\n\nEjemplo:\nEmpresa S.A.\nJuan Pérez\nGerente de Compras";
            }
            session.company = lines[0];
            session.name = lines[1];
            session.role = lines[2];
            
            const productsListForRole = Object.keys(catalog);
            let responseRole = "¡Datos guardados! ¿Qué producto deseas cotizar?\nResponde con el número de la opción:\n\n";
            productsListForRole.forEach((prod, index) => {
                responseRole += `${index + 1}. ${prod}\n`;
            });
            session.state = STATES.SELECT_PRODUCT;
            return responseRole;

        case STATES.SELECT_PRODUCT:
            const productsList = Object.keys(catalog);
            const prodIndex = parseInt(text) - 1;
            
            let selectedProduct = null;
            if (!isNaN(prodIndex) && prodIndex >= 0 && prodIndex < productsList.length) {
                selectedProduct = productsList[prodIndex];
            } else {
                const found = productsList.find(p => p.toLowerCase() === lowerText);
                if (found) selectedProduct = found;
            }

            if (selectedProduct) {
                session.product = selectedProduct;
                const dimensions = catalog[selectedProduct].map(i => i.dimension);
                
                let response = `Has seleccionado *${selectedProduct}*.\n¿Qué dimensión necesitas? Responde con el número:\n\n`;
                dimensions.forEach((dim, index) => {
                    response += `${index + 1}. ${dim}\n`;
                });
                
                session.state = STATES.SELECT_DIMENSION;
                return response;
            } else {
                return "Por favor selecciona un número de la lista válida, o escribe 'cancelar'.";
            }

        case STATES.SELECT_DIMENSION:
            if (!session.product) {
                resetSession(from);
                return "Ocurrió un error. Escribe 'Cotizar Placa' para empezar de nuevo.";
            }
            const productItems = catalog[session.product];
            const dimIndex = parseInt(text) - 1;
            
            let selectedItem = null;
            if (!isNaN(dimIndex) && dimIndex >= 0 && dimIndex < productItems.length) {
                selectedItem = productItems[dimIndex];
            } else {
                const foundDim = productItems.find(i => i.dimension.toLowerCase() === lowerText);
                if (foundDim) selectedItem = foundDim;
            }

            if (selectedItem) {
                session.dimension = selectedItem.dimension;
                session.state = STATES.ENTER_QUANTITY;
                return `Dimensión elegida: *${selectedItem.dimension}*.\n\n¿Cuántas piezas necesitas cotizar? (Ingresa solo un número entero, ej: 100)`;
            } else {
                return "Por favor selecciona una dimensión válida de la lista.";
            }

        case STATES.ENTER_QUANTITY:
            const quantity = parseInt(text);
            if (isNaN(quantity) || quantity <= 0) {
                return "Por favor ingresa una cantidad entera válida mayor a 0.";
            }

            const itemInfo = catalog[session.product].find(i => i.dimension === session.dimension);
            if (itemInfo) {
                const priceStr = getPriceForQuantity(itemInfo, quantity);
                if (priceStr === "No disponible") {
                     session.product = null;
                     session.dimension = null;
                     session.state = STATES.SELECT_PRODUCT;
                     const products = Object.keys(catalog);
                     let response = "Lo siento, no hay precio disponible para esa cantidad.\nElige otro producto para continuar:\n\n";
                     products.forEach((prod, index) => { response += `${index + 1}. ${prod}\n`; });
                     return response;
                }
                
                const cleanPrice = typeof priceStr === 'number' ? priceStr : parseFloat(priceStr.replace(/[^0-9.-]+/g,""));
                if (!isNaN(cleanPrice)) {
                    session.items.push({
                        product: session.product,
                        dimension: session.dimension,
                        quantity: quantity,
                        priceUnit: cleanPrice,
                        totalPrice: Number((cleanPrice * quantity).toFixed(2))
                    });
                }

                session.state = STATES.ASK_ADD_ANOTHER;
                return `¿Deseas agregar otro producto a esta cotización o procedemos a generarla?\n1. Agregar otro producto.\n2. Generar cotización.`;
            } else {
                return "Hubo un problema. Por favor escribe 'cancelar'.";
            }
            
        case STATES.ASK_ADD_ANOTHER:
            if (lowerText === '1' || lowerText === '1.' || lowerText === 'si' || lowerText === 'sí') {
                session.product = null;
                session.dimension = null;
                session.state = STATES.SELECT_PRODUCT;
                const products = Object.keys(catalog);
                let response = "¡Perfecto! ¿Qué otro producto deseas agregar?\nResponde con el número de la opción:\n\n";
                products.forEach((prod, index) => {
                    response += `${index + 1}. ${prod}\n`;
                });
                return response;
            } else if (lowerText === '2' || lowerText === '2.' || lowerText === 'no') {
                session.state = STATES.WAITING_FOR_DESCRIPTION;
                
                const { checkFolioExists } = require('./firebase');
                let newFolio;
                let exists = true;
                while(exists) {
                    newFolio = `COT-${Math.random().toString(36).substring(2, 8).toUpperCase()}`;
                    exists = await checkFolioExists(newFolio);
                }
                session.folio = newFolio;
                
                let summary = `¡Carrito completado!\n\n`;
                let grandTotal = 0;
                session.items.forEach((item, idx) => {
                    summary += `*${item.product}* (${item.dimension})\nCantidad: ${item.quantity} piezas - *$${item.totalPrice.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}*\n\n`;
                    grandTotal += item.totalPrice;
                });
                summary += `Total Estimado: *$${grandTotal.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}*\n\n`;
                summary += `Para continuar, comience anotando la descripción de cada artículo en caso de ser necesario.\n\nEjemplo:\nDescripción 1:\n* Material rígido.\n* Envío por FedEx.\nDescripción 2:\n* Esquinas redondeadas.\n\n*(Si no necesitas descripciones, envía la palabra 'Ninguna' o 'Descripción:')*`;
                return summary;
            } else {
                return "Por favor responde '1' para Agregar otro producto, o '2' para Generar cotización.";
            }

        case STATES.CONFIRM_CANCEL_ADD:
            if (lowerText === '1' || lowerText === '1.' || lowerText === 'si' || lowerText === 'sí') {
                session.state = STATES.WAITING_FOR_DESCRIPTION;
                
                const { checkFolioExists } = require('./firebase');
                let newFolio;
                let exists = true;
                while(exists) {
                    newFolio = `COT-${Math.random().toString(36).substring(2, 8).toUpperCase()}`;
                    exists = await checkFolioExists(newFolio);
                }
                session.folio = newFolio;
                
                let summary = `¡Carrito completado!\n\n`;
                let grandTotal = 0;
                session.items.forEach((item, idx) => {
                    summary += `*${item.product}* (${item.dimension})\nCantidad: ${item.quantity} piezas - *$${item.totalPrice.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}*\n\n`;
                    grandTotal += item.totalPrice;
                });
                summary += `Total Estimado: *$${grandTotal.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}*\n\n`;
                summary += `Para continuar, comience anotando la descripción de cada artículo en caso de ser necesario.\n\nEjemplo:\nDescripción 1:\n* Material rígido.\n* Envío por FedEx.\nDescripción 2:\n* Esquinas redondeadas.\n\n*(Si no necesitas descripciones, envía la palabra 'Ninguna' o 'Descripción:')*`;
                return summary;
            } else if (lowerText === '2' || lowerText === '2.' || lowerText === 'no') {
                resetSession(from);
                return "Entendido, hemos cancelado la cotización. Fue un placer atenderte. ¡Saludos de parte de Profesionales en Inventarios!";
            } else {
                return "¿Deseas cotizar únicamente los productos anteriormente enlistados?\n1. Sí\n2. No";
            }
            
        case STATES.WAITING_FOR_DESCRIPTION:
            // Mantenerse en WAITING_FOR_DESCRIPTION para permitir regeneraciones múltiples
            // Guardar cliente de forma permanente
            saveClient(from, session.company, session.name, session.role);
            // Timer ahora se controlará globalmente desde index.js
            
            return {
                text: `Cotización guardada exitosamente. Generando archivo PDF...`,
                action: 'GENERATE_PDF',
                descText: text,
                folio: session.folio,
                session: session
            };
    }
    
    return null;
}

module.exports = {
    handleMessage,
    sessions
};
